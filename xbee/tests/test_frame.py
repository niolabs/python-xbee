#! /usr/bin/python
"""
test_frame.py

Paul Malmsten, 2010
pmalmsten@gmail.com

Tests frame module for proper behavior
"""
import unittest
from xbee.frame import APIFrame

class TestAPIFrameGeneration(unittest.TestCase):
    """
    XBee class must be able to create a valid API frame given binary
    data, in byte string form.
    """
    def test_single_byte(self):
        """
        create a frame containing a single byte
        """
        data = '\x00'
        # start byte, two length bytes, data byte, checksum
        expected_frame = '\x7E\x00\x01\x00\xFF'
        
        frame = APIFrame(data).output()
        self.assertEqual(frame, expected_frame)
        
class TestAPIFrameParsing(unittest.TestCase):
    """
    XBee class must be able to read and validate the data contained
    by a valid API frame.
    """
    
    def test_single_byte(self):
        """
        read a frame containing a single byte
        """
        frame = '\x7E\x00\x01\x00\xFF'
        expected_data = '\x00'
        
        data = APIFrame.parse(frame).data
        self.assertEqual(data, expected_data)
        
    def test_invalid_checksum(self):
        """
        when an invalid frame is read, an exception must be raised
        """
        frame = '\x7E\x00\x01\x00\xF6'
        self.assertRaises(ValueError, APIFrame.parse, frame)

class TestEscapedOutput(unittest.TestCase):
    """
    APIFrame class must properly escape data
    """

    def test_escape_method(self):
        """
        APIFrame.escape() must work as expected
        """
        test_data = APIFrame.START_BYTE
        new_data = APIFrame.escape(test_data)
        self.assertEqual(new_data, APIFrame.ESCAPE_BYTE + '\x5e')

