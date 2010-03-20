#! /usr/bin/python

import unittest
from xbee import XBee

"""
test_xbee.py
By Paul Malmsten, 2010

Tests the XBee superclass module for XBee API conformance.
"""

class TestChecksumming(unittest.TestCase):
    """
    XBee class must properly generate and verify checksums for binary
    data sent to and received from an XBee device
    """
    def setUp(self):
        self.data1 = '\x00'
        self.data2 = '\x36'
        self.data3 = '\x01\x01\x01\x01\x01'
        
    def test_checksum(self):
        """
        checksum a simple byte
        """
        chksum = XBee.checksum(self.data1)
        self.assertEqual(chksum, 0xFF)
        
    def test_checksum_again(self):
        """
        checksum a different byte
        """
        chksum = XBee.checksum(self.data2)
        self.assertEqual(chksum, 0xc9)
        
    def test_checksum_multibyte(self):
        """
        checksum more than one byte
        """
        chksum = XBee.checksum(self.data3)
        self.assertEqual(chksum, 0xFA)
        
    def test_verify_checksum(self):
        """
        verify_checksum a single byte
        """
        chksum = '\xff'
        self.assertTrue(XBee.verify_checksum(self.data1, chksum))
        
    def test_verify_checksum_again(self):
        """
        verify_checksum a different byte
        """
        chksum = '\xc9'
        self.assertTrue(XBee.verify_checksum(self.data2, chksum))
        
    def test_verify_checksum_multibyte(self):
        """
        verify_checksum multiple bytes
        """
        chksum = '\xFA'
        self.assertTrue(XBee.verify_checksum(self.data3, chksum))

class TestAPIFrameGeneration(unittest.TestCase):
    """
    XBee class must be able to create a valid API frame given binary
    data, in byte string form.
    """
    pass
   
if __name__ == '__main__':
    unittest.main()
