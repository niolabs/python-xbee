"""
test_digimesh.py

By James saunders, 2016
james@saunders-family.net

Tests the XBee DigiMesh implementation class for API compliance
"""
import unittest
from xbee.digimesh import DigiMesh

class TestDigiMesh(unittest.TestCase):
    """
    Tests DigiMesh-specific features
    """

    def setUp(self):
        self.digimesh = DigiMesh(None)
