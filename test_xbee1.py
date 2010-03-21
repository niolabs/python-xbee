#! /usr/bin/python

import unittest
from xbee1 import XBee1

"""
test_xbee1.py
By Paul Malmsten

Tests the XBee Series 1 class for XBee API compliance
"""

class TestBuildCommand(unittest.TestCase):
    """
    build_command should properly build a command packet
    """
    
    def test_build_at_data_mismatch(self):
        """
        if not enough or incorrect data is provided, an exception should
        be raised.
        """
        try:
            data = XBee1.build_command("at")
        except KeyError:
           # Test passes
           return
    
        # No exception? Fail.
        self.fail("An exception was not raised with improper data supplied")
        
    def test_build_at_data_len_mismatch(self):
        """
        if data of incorrect length is provided, an exception should be raised
        """
        try:
            data = XBee1.build_command("at", frame_id="AB", command="MY")
        except ValueError:
           # Test passes
           return
    
        # No exception? Fail.
        self.fail("An exception was not raised with improper data length")
        
    def test_build_at(self):
        """
        build_command should build a valid at command packet which has
        no parameter data to be saved
        """
        
        at_command = "MY"
        frame = chr(43)
        data = XBee1.build_command("at", frame_id=frame, command=at_command) 

        expected_data = '\x08+MY'
        self.assertEqual(data, expected_data)

if __name__ == '__main__':
    unittest.main()
