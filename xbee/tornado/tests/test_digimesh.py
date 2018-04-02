"""
test_digimesh.py

By James Saunders, 2016
james@saunders-family.net

Tests the XBee DigiMesh implementation class for API compliance
"""
import unittest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from xbee.tornado import has_tornado

if not has_tornado:
    raise unittest.SkipTest("Requires Tornado")

from tornado import ioloop # noqa
from xbee.tests.Fake import Serial  # noqa
from xbee.tornado.digimesh import DigiMesh  # noqa


class TestDigiMesh(unittest.TestCase):
    """
    Tests DigiMesh-specific features
    More tests will need adding in time
    """

    def setUp(self):
        super(TestDigiMesh, self).setUp()
        patch_io = ioloop.IOLoop.current()
        patch_io.add_handler = Mock()
        serial_port = Serial()
        self.digimesh = DigiMesh(serial_port, io_loop=patch_io)

    def test_split_tx_status(self):
            data = b'\x8b\x01\xff\xff\x01\x01\x01'
            info = self.digimesh._split_response(data)
            expected_info = {
                'id': 'tx_status',
                'frame_id': b'\x01',
                'reserved': b'\xff\xff',
                'retries': b'\x01',
                'deliver_status': b'\x01',
                'discover_status': b'\x01'
            }
            self.assertEqual(info, expected_info)


if __name__ == '__main__':
    unittest.main()
