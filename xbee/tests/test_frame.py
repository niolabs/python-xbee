#! /usr/bin/python
"""
test_frame.py

Paul Malmsten, 2010
pmalmsten@gmail.com

Tests frame module for proper behavior
"""
import unittest
from xbee.frame import APIFrame
from Fake import FakeDevice, FakeReadDevice

class TestChecksumming(unittest.TestCase):
    """
    XBee class must properly generate and verify checksums for binary
    data sent to and received from an XBee device
    """
    def setUp(self):
        """
        Factor out common data among most tests
        """
        self.frame1 = APIFrame('\x00')
        self.frame2 = APIFrame('\x36')
        self.frame3 = APIFrame('\x01\x01\x01\x01\x01')
        self.chksum1 = '\xff'
        self.chksum2 = '\xc9'
        self.chksum3 = '\xFA'
        
    def test_checksum(self):
        """
        checksum a simple byte
        """
        chksum = self.frame1.checksum()
        self.assertEqual(chksum, self.chksum1)
        
    def test_checksum_again(self):
        """
        checksum a different byte
        """
        chksum = self.frame2.checksum()
        self.assertEqual(chksum, self.chksum2)
        
    def test_checksum_multibyte(self):
        """
        checksum more than one byte
        """
        chksum = self.frame3.checksum()
        self.assertEqual(chksum, self.chksum3)
        
    def test_verify_checksum(self):
        """
        verify_checksum a single byte
        """
        self.assertTrue(self.frame1.verify(self.chksum1))
        
    def test_verify_checksum_again(self):
        """
        verify_checksum a different byte
        """
        self.assertTrue(self.frame2.verify(self.chksum2))
        
    def test_verify_checksum_multibyte(self):
        """
        verify_checksum multiple bytes
        """
        self.assertTrue(self.frame3.verify(self.chksum3))
        
    def test_verify_checksum_uses_low_bits(self):
        """
        verify_checksum should only use the low bits of the 
        byte summing process for verification
        """
        self.assertTrue(APIFrame('\x88DMY\x01').verify('\x8c'))
        
class TestLenBytes(unittest.TestCase):
    """
    XBee class must properly encode the length of the data to be
    sent to the XBee
    """    
    def test_single_byte(self):
        """
        run len_bytes on a single byte
        """
        msb, lsb = APIFrame('\x00').len_bytes()
        self.assertEqual(msb, '\x00')
        self.assertEqual(lsb, '\x01')
        
    def test_few_bytes(self):
        """
        run len_bytes on a few bytes
        """
        msb, lsb = APIFrame('\x00\x00\x00\x00\x00\x00\x00\x00\x00').len_bytes()
        self.assertEqual(msb, '\x00')
        self.assertEqual(lsb, '\x09')
        
    def test_many_bytes(self):
        """
        run len_bytes on many bytes
        """
        data = '\x00' * 300
        msb, lsb = APIFrame(data).len_bytes()
        self.assertEqual(msb, '\x01')
        self.assertEqual(lsb, ',')

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
