"""
Created on 2019-12-31

@author: wf
"""

from unittest import TestCase

from pcwawc.config import Config


class ConfigTest(TestCase):

    def test_Config(self):
        config = Config.default()
        assert config is not None
