"""
XBee package initalization file

info@n.io
"""

try:
    import tornado
except ImportError:
    print("You must install Tornado to use this module")
    import sys
    sys.exit(1)

from xbee.tornado.ieee import XBee
from xbee.tornado.zigbee import ZigBee
from xbee.tornado.digimesh import DigiMesh
