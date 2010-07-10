"""
test_dispatch.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

Tests the Dispatch module.
"""
import unittest
from xbee.helpers.dispatch import Dispatch
from xbee.helpers.dispatch.tests.fake import FakeXBee

class TestDispatch(unittest.TestCase):
    """
    Tests xbee.helpers.dispatch for expected behavior
    """

    def setUp(self):
        self.xbee = FakeXBee(None)
        self.dispatch = Dispatch(xbee=self.xbee)
        
    def test_callback_is_called_when_registered(self):
        """
        After registerring a callback function with a filter function,
        the callback should be called when data arrives.
        """
        self.count = 0
        
        def callback(name, data):
            self.count += 1
            
        self.dispatch.register("test1", callback, lambda data: True)
        self.dispatch.run(oneshot=True)
        self.assertEqual(self.count, 1)
