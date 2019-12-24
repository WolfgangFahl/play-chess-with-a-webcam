'''
Created on 2019-12-21

@author: wf
'''
# https://github.com/rhgrant10/berserk
# https://berserk.readthedocs.io/en/master/
import berserk
import lichess.api
import os
import yaml
import requests
import time

class Account():
    """" Lichess account wrapper """
    
    def __init__(self,adict):
        self.adict=adict
        self.id=adict["id"]
        self.username=adict["username"]
        pass
    
    def __str__(self):
        text="%s - (%s)" % (self.username,self.id)
        return text

class Lichess():
    """ Lichess adapter """
    
    def __init__(self,debug=False):
        self.debug=debug
        token=self.getToken()
        if token is not None:
            self.session= berserk.TokenSession(token)
            self.client=berserk.Client(self.session)
        else:
            self.client=None
    
    def getAccount(self):
        account=Account(self.client.account.get())
        return account
    
    def getToken(self):
        home=os.getenv("HOME")
        #print(home)
        configPath=home+"/.pcwawc/config.yaml"
        if not os.path.isfile(configPath):
            print ("%s is missing please create it" % (configPath))
            return None
        config=yaml.load(open(configPath),Loader=yaml.FullLoader)
        if not "token" in config:
            print ("no token found in %s please add it" % (configPath))
            return None
        return config["token"]
    
    def pgnImport(self,pgn):
        payload = {
          'pgn': pgn,
          'analyse': 'on'
        }
        res = requests.post('https://lichess.org/import', data=payload)
        print(res.url)
        pass
    
    def game(self,gameid):
        game=lichess.api.game(gameid)
        return game
    
    def waitForChallenge(self):
        # Stream whats happening and continue when we are challenged
        in_game = False
        client=self.client
        while(not in_game):
            time.sleep(0.5)
            for event in client.bots.stream_incoming_events():
                eventtype=event['type']
                if self.debug:
                    print (eventtype,event)
                if eventtype == 'gameStart':
                    game_id = event['game']['id']
                    in_game = True
                    break
                elif eventtype == 'challenge':
                    game_id = event['challenge']['id']
                    client.bots.accept_challenge(game_id)
                    in_game = True
        if self.debug:            
            print("The game %s has started!" % (game_id))
        return game_id    
        
    # Stream the events of the game and respond accordingly
    def streamGame(self,game_id):
        playing = True
        client=self.client
        while(playing):
            for event in client.bots.stream_game_state(game_id):
                eventtype=event['type']
                if self.debug:
                    print (eventtype,event)
                if eventtype == 'gameFull':
                    if client.account.get()['username'] == event['white']['id']:
                        client.bots.post_message(game_id, "I got first, nerd!")
                    else:
                        client.bots.post_message(game_id, "You got first, nerd!")    
        
