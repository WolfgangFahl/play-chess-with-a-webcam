'''
Created on 2019-12-21

@author: wf
'''
# https://github.com/rhgrant10/berserk
# https://berserk.readthedocs.io/en/master/
import berserk
import os
import yaml
import requests

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
    
    def __init__(self):
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
        
        
