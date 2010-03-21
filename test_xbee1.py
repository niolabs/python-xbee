#! /usr/bin/python

import unittest
from xbee1 import XBee1
import pdb

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
        
class TestSplitResponse(unittest.TestCase):
    """
    split_response should properly split a response packet
    """
    
    def test_unrecognized_response(self):
        """
        if a response begins with an unrecognized id byte, split_response
        should raise an exception
        """
        data = '\x23\x00\x00\x00'
        
        try:
            XBee1.split_response(data)
        except KeyError:
            # Passes
            return
            
        # Test Fails
        self.fail()
    
    def test_bad_data_long(self):
        """
        if a response doesn't match the specification's layout, 
        split_response should raise an exception
        """
        # Over length
        data = '\x8a\x00\x00\x00'
        self.assertRaises(ValueError, XBee1.split_response, data)
        
    def test_bad_data_short(self):
        """
        if a response doesn't match the specification's layout, 
        split_response should raise an exception
        """
        # Under length
        data = '\x8a'
        self.assertRaises(ValueError, XBee1.split_response, data)
    
    def test_split_status_response(self):
        """
        split_response should properly split a status response packet
        """
        data = '\x8a\x01'
        
        info = XBee1.split_response(data)
        expected_info = {'id':'status',
                         'status':'\x01'}
        
        self.assertEqual(info, expected_info)
        
    def test_split_short_at_response(self):
        """
        split_response should properly split an at_response packet which
        has no parameter data
        """
        
        data = '\x88DMY\x01'
        info = XBee1.split_response(data)
        expected_info = {'id':'at_response',
                         'frame_id':'D',
                         'command':'MY',
                         'status':'\x01'}
        self.assertEqual(info, expected_info)
        
    def test_split_at_response_with_parameter(self):
        """
        split_response should properly split an at_response packet which
        has parameter data
        """
        
        data = '\x88DMY\x01ABCDEF'
        info = XBee1.split_response(data)
        expected_info = {'id':'at_response',
                         'frame_id':'D',
                         'command':'MY',
                         'status':'\x01',
                         'parameter':'ABCDEF'}
        self.assertEqual(info, expected_info)

if __name__ == '__main__':
    unittest.main()
