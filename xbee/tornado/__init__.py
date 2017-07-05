"""
XBee package initalization file

info@n.io
"""

try:
    from xbee.tornado.ieee import XBee
    from xbee.tornado.zigbee import ZigBee
    from xbee.tornado.digimesh import DigiMesh
    has_tornado = True
except ImportError:
    has_tornado = False
