'''
Created on 2019-12-26

@author: wf
'''
from pcwawc.chessengine import Engine
import os

debug=True

def fix_path():
    """ fixes PATH issues e.g. on MacOS macports environment - adopt to your needs as you see fit"""
    
    # is macports installed?
    if os.path.isfile("/opt/local/bin/port"):
        if debug:
            print ("found macports - adding /opt/local/bin to PATH")
        os.environ["PATH"]=os.environ["PATH"]+":"+"/opt/local/bin"
    if debug:
        print ("PATH is: %s" % (os.environ['PATH']))
        
# http://julien.marcel.free.fr/macchess/Chess_on_Mac/Engines.html
def test_engines():
    fix_path()
    Engine.debug=debug
    engineConfigs=Engine.findEngines()
    for key,engineConfig in engineConfigs.items():
        engine=Engine(engineConfig)
        print (engine)
            

test_engines()
