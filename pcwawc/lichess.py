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
import threading

class Account():
    """" Lichess account wrapper """
    
    def __init__(self,adict):
        self.adict=adict
        self.id=adict["id"]
        if "username" in adict:
            self.username=adict["username"]
        elif "name" in adict:
            self.username=adict["name"]    
        pass
    
    def __str__(self):
        text="%s - (%s)" % (self.username,self.id)
        return text
 
#https://berserk.readthedocs.io/en/master/usage.html#being-a-bot    
class Game(threading.Thread):
    """ Lichess game """
    def __init__(self, lichess,game_id,debug=False,**kwargs):
        super().__init__(**kwargs)
        self.debug=debug
        self.game_id = game_id
        self.lichess=lichess
        self.account=lichess.getAccount()
        self.client=lichess.client
        self.stream = self.client.bots.stream_game_state(game_id)
        self.current_state = None    
        
    def postChat(self,msg):    
        if self.debug:
            print ("Chat %s: %s" % (self.game_id,msg))
        self.client.bots.post_message(self.game_id,msg)
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
        
    def move(self,move):
        try:
            self.client.bots.make_move(self.game_id, move)
            return True
        except requests.exceptions.HTTPError as httpError:
            return self.handle(httpError)
    
    def handle(self,httpError):
        if self.debug:
            print (httpError)
        return False
        
    def run(self):
        if self.debug:
            print ("started thread for game %s" % (self.game_id))
        # https://lichess.org/api#operation/botGameStream
        for event in self.stream:
            self.current_state=event
            eventtype=event['type']     
            if self.debug:
                print (eventtype,event)  
            if eventtype == 'gameFull':
                self.white=Account(event['white'])
                self.black=Account(event['black'])
                msg="white:%s black:%s" % (self.white.username,self.black.username)
                self.postChat(msg)     

class Lichess():
    """ Lichess adapter """
    
    def __init__(self,tokenName="token",debug=False):
        self.debug=debug
        token=self.getToken(tokenName)
        if token is not None:
            self.session= berserk.TokenSession(token)
            self.client=berserk.Client(self.session)
        else:
            self.client=None
    
    def getAccount(self):
        account=Account(self.client.account.get())
        return account
    
    def getToken(self,tokenname="token"):
        home=os.getenv("HOME")
        #print(home)
        configPath=home+"/.pcwawc/config.yaml"
        if not os.path.isfile(configPath):
            print ("%s is missing please create it" % (configPath))
            return None
        config=yaml.load(open(configPath),Loader=yaml.FullLoader)
        if not tokenname in config:
            print ("no token found in %s please add it" % (configPath))
            return None
        return config[tokenname]
    
    def pgnImport(self,pgn):
        payload = {
          'pgn': pgn,
          'analyse': 'on'
        }
        res = requests.post('https://lichess.org/import', data=payload)
        print(res.url)
        pass
    
    def game(self,game_id):
        game=lichess.api.game(game_id)
        return game
    
    def challenge(self,oponentUserName):
        if self.debug:
            print ("challenge %s" % (oponentUserName))
        client=self.client
        client.challenges.create(username=oponentUserName,rated=False)
    
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
                      
        
