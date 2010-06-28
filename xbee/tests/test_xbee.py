#! /usr/bin/python
"""
test_xbee.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

Tests the XBee superclass module for XBee API conformance.
"""
import unittest
from xbee.base import XBee
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
        msb, lsb = XBee.len_bytes('\x00')
        self.assertEqual(msb, '\x00')
        self.assertEqual(lsb, '\x01')
        
    def test_few_bytes(self):
        """
        run len_bytes on a few bytes
        """
        msb, lsb = XBee.len_bytes('\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(msb, '\x00')
        self.assertEqual(lsb, '\x09')
        
    def test_many_bytes(self):
        """
        run len_bytes on many bytes
        """
        data = '\x00' * 300
        msb, lsb = XBee.len_bytes(data)
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
        
        frame = XBee.fill_frame(data)
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
        
class TestNotImplementedFeatures(unittest.TestCase):
    """
    In order to properly use the XBee class for most situations,
    it must be subclassed with the proper attributes definined. If
    this is not the case, then a NotImplemented exception should be
    raised as appropriate.
    """
    
    def setUp(self):
        """
        Set up a base class XBee object which does not have api_commands
        or api_responses defined
        """
        self.xbee = XBee(None)
    
    def test_build_command(self):
        """
        build_command should raise NotImplemented
        """
        self.assertRaises(NotImplementedError, self.xbee.build_command, "at")
        
    def test_split_response(self):
        """
        split_command should raise NotImplemented
        """
        self.assertRaises(NotImplementedError, self.xbee.split_response, "\00")
        
    def test_shorthand(self):
        """
        Shorthand calls should raise NotImplementedError
        """
        try:
            cmd = self.xbee.at
        except NotImplementedError:
            pass
        else:
            self.fail("Shorthand call on XBee base class should raise NotImplementedError")
        
if __name__ == '__main__':
    unittest.main()
