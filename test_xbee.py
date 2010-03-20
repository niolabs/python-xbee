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
    def test_checksum(self):
        """
        The checksum of binary data must be correct
        """
        # Simple start
        data = '\x00'
        chksum = XBee.checksum(data)
        self.assertEqual(chksum, 0xFF)
        
        # Once more
        data = '\x36'
        chksum = XBee.checksum(data)
        self.assertEqual(chksum, 0xc9)
        
        # Multi bytes
        data = '\x01\x01\x01\x01\x01'
        chksum = XBee.checksum(data)
        self.assertEqual(chksum, 0xFA)
        
    def test_verify_checksum(self):
        """
        verify_checksum must properly assert that the given data
        and checksum are correct
        """
        data = '\x00'
        chksum = '\xff'
        self.assertTrue(XBee.verify_checksum(data, chksum))
        
        data = '\x36'
        chksum = '\xc9'
        self.assertTrue(XBee.verify_checksum(data, chksum))
        
        data = '\x01\x01\x01\x01\x01'
        chksum = '\xFA'
        self.assertTrue(XBee.verify_checksum(data, chksum))

class TestAPIFrameGeneration(unittest.TestCase):
    """
    XBee class must be able to create a valid API frame given binary
    data, in byte string form.
    """
    pass
   
if __name__ == '__main__':
    unittest.main()
