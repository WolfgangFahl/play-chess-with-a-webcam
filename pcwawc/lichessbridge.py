"""
Created on 2019-12-21

@author: wf
"""

import threading
import time

import berserk
import lichess.api
import requests

from pcwawc.config import Config

# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
#
# uses https://github.com/rhgrant10/berserk
# https://berserk.readthedocs.io/en/master/
from pcwawc.eventhandling import Observable


class Account:
    """ " Lichess account wrapper"""

    def __init__(self, adict):
        self.adict = adict
        self.id = adict["id"]
        if "username" in adict:
            self.username = adict["username"]
        elif "name" in adict:
            self.username = adict["name"]
        pass

    def __str__(self):
        text = "%s - (%s)" % (self.username, self.id)
        return text


class State:
    """Lichess state wrapper"""

    def __init__(self, adict):
        self.adict = adict
        self.type = adict["type"]
        if self.type == "gameState":
            self.moves = adict["moves"]
            self.wtime = adict["wtime"]
            self.btime = adict["btime"]
            self.winc = adict["winc"]
            self.binc = adict["binc"]
            self.wdraw = adict["wdraw"]
            self.bdraw = adict["bdraw"]
            self.moveList = self.moves.split()
            self.moveIndex = len(self.moveList) - 1


# https://berserk.readthedocs.io/en/master/usage.html#being-a-bot
class Game(threading.Thread, Observable):
    """Lichess game"""

    def __init__(self, lichess, game_id, debug=False, **kwargs):
        super().__init__(**kwargs)
        Observable.__init__(self)
        self.debug = debug
        self.game_id = game_id
        self.lichess = lichess
        self.account = lichess.getAccount()
        self.client = lichess.client
        self.stream = self.client.bots.stream_game_state(game_id)
        self.current_state = None
        self.isOn = False

    def postChat(self, msg):
        if self.debug:
            print("Chat %s: %s" % (self.game_id, msg))
        self.client.bots.post_message(self.game_id, msg)
        pass

    def abort(self):
        try:
            self.client.bots.abort_game(self.game_id)
            return True
        except requests.exceptions.HTTPError as httpError:
            return self.handle(httpError)

    def resign(self):
        try:
            self.client.bots.resign_game(self.game_id)
            return True
        except requests.exceptions.HTTPError as httpError:
            return self.handle(httpError)

    def move(self, move):
        try:
            self.client.bots.make_move(self.game_id, move)
            return True
        except requests.exceptions.HTTPError as httpError:
            return self.handle(httpError)

    def handle(self, httpError):
        if self.debug:
            print(httpError)
        return False

    def stop(self):
        self.isOn = False

    def run(self):
        if self.debug:
            print(
                "started thread for user %s game %s"
                % (self.account.username, self.game_id)
            )
        self.isOn = True
        # https://lichess.org/api#operation/botGameStream
        for event in self.stream:
            # stop if we are flagged to
            if not self.isOn:
                break
            self.current_state = event
            state = None
            eventtype = event["type"]
            if self.debug:
                print(eventtype, event)
            if eventtype == "gameFull":
                self.white = Account(event["white"])
                self.black = Account(event["black"])
                msg = "white:%s black:%s" % (self.white.username, self.black.username)
                self.postChat(msg)
                state = State(event["state"])
            elif eventtype == "gameState":
                state = State(event)
            if state is not None:
                self.fire(state=state)
        if self.debug:
            print(
                "%s stopped thread for game %s" % (self.account.username, self.game_id)
            )


class Lichess:
    """Lichess adapter"""

    def __init__(self, tokenName="token", debug=False):
        self.debug = debug
        token = self.getToken(tokenName)
        if token is not None:
            self.session = berserk.TokenSession(token)
            self.client = berserk.Client(self.session)
        else:
            self.client = None
        self.account = None

    def getAccount(self):
        if self.account is None and self.client is not None:
            self.account = Account(self.client.account.get())
        return self.account

    def getToken(self, tokenname="token"):
        config = Config.default()
        if not tokenname in config.config:
            print("no token found in %s please add it" % (config.configFile))
            return None
        return config.config[tokenname]

    def pgnImport(self, pgn):
        payload = {"pgn": pgn, "analyse": "on"}
        res = requests.post("https://lichess.org/import", data=payload)
        print(res.url)
        pass

    def game(self, game_id):
        game = lichess.api.game(game_id)
        return game

    def challenge(self, oponentUserName):
        if self.debug:
            print("challenge %s by %s" % (self.getAccount().username, oponentUserName))
        client = self.client
        client.challenges.create(username=oponentUserName, rated=False)

    def waitForChallenge(self, timeout=1000, pollInterval=0.5):
        """wait for a challend and return the corresponding game"""
        # Stream whats happening and continue when we are challenged
        in_game = False
        client = self.client
        account = self.getAccount()
        if self.debug:
            print(
                "%s waiting for challenge (max %d secs, polling every %.1f secs)"
                % (account.username, timeout, pollInterval)
            )
        while not in_game:
            time.sleep(pollInterval)
            timeout -= pollInterval
            if timeout <= 0:
                raise Exception("time out waiting for challenge")
            for event in client.bots.stream_incoming_events():
                eventtype = event["type"]
                if self.debug:
                    print(eventtype, event)
                if eventtype == "gameStart":
                    game_id = event["game"]["id"]
                    in_game = True
                    break
                elif eventtype == "challenge":
                    challenge = event["challenge"]
                    game_id = challenge["id"]
                    challenger = challenge["challenger"]
                    # don't try to play against myself
                    if not challenger == account.username:
                        client.bots.accept_challenge(game_id)
                        in_game = True
                    elif self.debug:
                        print(
                            "%s avoiding to play against myself in game %s"
                            % (account.username, game_id)
                        )
        if self.debug:
            print("The game %s has started!" % (game_id))
        return game_id
