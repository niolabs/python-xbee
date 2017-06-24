from xbee.tornado.base import XBeeBase
import xbee.backend as _xbee


class DigiMesh(_xbee.DigiMesh, XBeeBase):
    pass
