'''
Created on 2019-12-31

@author: wf
'''
from pcwawc.config import Config
from unittest import TestCase

class ConfigTest(TestCase):
    
    def test_Config(self):
        config=Config.default()
        assert config is not None
    