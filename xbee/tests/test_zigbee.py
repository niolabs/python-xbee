"""
test_zigbee.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

Tests the XBee ZB (ZigBee) implementation class for API compliance
"""
import unittest
from xbee.zigbee import ZigBee

class TestZigBee(unittest.TestCase):
    """
    Tests ZigBee-specific features
    """

    def setUp(self):
        self.zigbee = ZigBee(None)

    def test_null_terminated_field(self):
        """
        Packets with null-terminated fields
        should be properly parsed
        """
        expected_data = '\x01\x02\x03\x04'
        terminator = '\x00'
        node_identifier = '\x95' + '\x00' * 21 + expected_data + terminator + '\x00' * 8

        data = self.zigbee._split_response(node_identifier)

        self.assertEqual(data['node_id'], expected_data)
         
