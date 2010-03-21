#! /usr/bin/python

import unittest
from xbee import XBee

"""
test_xbee.py
By Paul Malmsten, 2010

Tests the XBee superclass module for XBee API conformance.
"""

class FakeDevice:
    """
    Represents a fake serial port for testing purposes
    """
    
    def write(self, data):
        self.data = data
        
class FakeReadDevice:
    """
    Represents a fake serial port which can be read from in a similar
    fashion to the real thing
    """
    
    def __init__(self, data):
        self.data = data
        self.read_index = 0
        
    def read(self, bytes=1):
        """
        Read the indicated number of bytes from the port
        """
        # If too many bytes would be read, raise exception
        if self.read_index + bytes > len(self.data):
            raise ValueError("Not enough bytes exist!")
        
        read_data = self.data[self.read_index:self.read_index + bytes]
        self.read_index += bytes
        
        return read_data
        
class TestFakeReadDevice(unittest.TestCase):
    """
    FakeReadDevice class should work as intended to emluate a serial 
    port
    """
    def setUp(self):
        self.device = FakeReadDevice("test")
    
    def test_read_single_byte(self):
        """
        reading one byte at a time should work as expected
        """
        self.assertEqual(self.device.read(), 't')
        self.assertEqual(self.device.read(), 'e')
        self.assertEqual(self.device.read(), 's')
        self.assertEqual(self.device.read(), 't')
        
    def test_read_multiple_bytes(self):
        """
        reading multiple bytes at a time should work as expected
        """
        self.assertEqual(self.device.read(3), 'tes')
        self.assertEqual(self.device.read(), 't')
        
    def test_read_too_many(self):
        """
        attempting to read too many bytes should raise an exception
        """
        self.assertRaises(ValueError, self.device.read, 5)

class TestChecksumming(unittest.TestCase):
    """
    XBee class must properly generate and verify checksums for binary
    data sent to and received from an XBee device
    """
    def setUp(self):
        self.data1 = '\x00'
        self.data2 = '\x36'
        self.data3 = '\x01\x01\x01\x01\x01'
        self.chksum1 = '\xff'
        self.chksum2 = '\xc9'
        self.chksum3 = '\xFA'
        
    def test_checksum(self):
        """
        checksum a simple byte
        """
        chksum = XBee.checksum(self.data1)
        self.assertEqual(chksum, self.chksum1)
        
    def test_checksum_again(self):
        """
        checksum a different byte
        """
        chksum = XBee.checksum(self.data2)
        self.assertEqual(chksum, self.chksum2)
        
    def test_checksum_multibyte(self):
        """
        checksum more than one byte
        """
        chksum = XBee.checksum(self.data3)
        self.assertEqual(chksum, self.chksum3)
        
    def test_verify_checksum(self):
        """
        verify_checksum a single byte
        """
        self.assertTrue(XBee.verify_checksum(self.data1, self.chksum1))
        
    def test_verify_checksum_again(self):
        """
        verify_checksum a different byte
        """
        self.assertTrue(XBee.verify_checksum(self.data2, self.chksum2))
        
    def test_verify_checksum_multibyte(self):
        """
        verify_checksum multiple bytes
        """
        self.assertTrue(XBee.verify_checksum(self.data3, self.chksum3))
        
    def test_verify_checksum_uses_low_bits(self):
        """
        verify_checksum should only use the low bits of the 
        byte summing process for verification
        """
        self.assertTrue(XBee.verify_checksum('\x88DMY\x01', '\x8c'))
        
class TestLenBytes(unittest.TestCase):
    """
    XBee class must properly encode the length of the data to be
    sent to the XBee
    """    
    def test_single_byte(self):
        """
        run len_bytes on a single byte
        """
        MSB,LSB = XBee.len_bytes('\x00')
        self.assertEqual(MSB, '\x00')
        self.assertEqual(LSB, '\x01')
        
    def test_few_bytes(self):
        """
        run len_bytes on a few bytes
        """
        MSB,LSB = XBee.len_bytes('\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(MSB, '\x00')
        self.assertEqual(LSB, '\x09')
        
    def test_many_bytes(self):
        """
        run len_bytes on many bytes
        """
        bytes = '\x00' * 300
        MSB,LSB = XBee.len_bytes(bytes)
        self.assertEqual(MSB, '\x01')
        self.assertEqual(LSB, ',')

class TestAPIFrameGeneration(unittest.TestCase):
    """
    XBee class must be able to create a valid API frame given binary
    data, in byte string form.
    """
    def test_single_byte(self):
        """
        create a frame containing a single byte
        """
        bytes = '\x00'
        # start byte, two length bytes, data byte, checksum
        expected_frame = '\x7E\x00\x01\x00\xFF'
        
        frame = XBee.fill_frame(bytes)
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
        
        data = XBee.empty_frame(frame)
        self.assertEqual(data, expected_data)
        
    def test_invalid_checksum(self):
        """
        when an invalid frame is read, an exception must be raised
        """
        frame = '\x7E\x00\x01\x00\xF6'
        self.assertRaises(ValueError, XBee.empty_frame, frame)

class TestWriteToDevice(unittest.TestCase):
    """
    XBee class should properly write binary data in a valid API
    frame to a given serial device.
    """
    
    def test_write(self):
        """
        write method should write the expected data to the serial
        device
        """
        device = FakeDevice()
        
        xbee = XBee(device)
        xbee.write_frame('\x00')
        
        # Check resuting state of fake device
        expected_frame = '\x7E\x00\x01\x00\xFF'
        self.assertEqual(device.data, expected_frame)
        
    def test_write_again(self):
        """
        write method should write the expected data to the serial
        device
        """
        device = FakeDevice()
        
        xbee = XBee(device)
        xbee.write_frame('\x00\x01\x02')
        
        # Check resuting state of fake device
        expected_frame = '\x7E\x00\x03\x00\x01\x02\xFC'
        self.assertEqual(device.data, expected_frame)
        
class TestReadFromDevice(unittest.TestCase):
    """
    XBee class should properly read and extract data from a valid
    API frame
    """
    def test_read(self):
        """
        wait_for_frame should properly read a frame of data
        """
        device = FakeReadDevice('\x7E\x00\x01\x00\xFF')
        xbee = XBee(device)
        
        data = xbee.wait_for_frame()
        self.assertEqual(data, '\x00')
        
    def test_read_invalid_followed_by_valid(self):
        """
        wait_for_frame should skip invalid data
        """
        device = FakeReadDevice(
            '\x7E\x00\x01\x00\xFA' + '\x7E\x00\x01\x05\xFA')
        xbee = XBee(device)
        
        data = xbee.wait_for_frame()
        self.assertEqual(data, '\x05')
        
if __name__ == '__main__':
    unittest.main()
