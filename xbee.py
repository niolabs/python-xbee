import struct

"""
XBee superclass module

This class defines data and methods common to both the Xbee Series 1 and
Series 2 modules. This class should be subclassed in order to provide
series-specific functionality.
"""

class XBee:
    START_BYTE = 0x7E
    
    # start is one byte long, length is two bytes
    # data is n bytes long (indicated by length)
    # chksum is one byte long
    api_frame_order = ['start', 'length', 'data', 'chksum']
    api_frame_elems = {'start': START_BYTE,
                       'length': None,
                       'data': None,
                       'chksum':None}
                       
    # In order to generate an API frame, the following elements
    # must be provided
    api_required_data = ['data']
          
    @staticmethod
    def checksum(data):
        """
        checksum: binary data -> single checksum byte
        
        checksum adds all bytes of binary, unescaped data presented to it, 
        saves the last byte of the result, and subtracts it from 0xFF. The
        final result is the checksum
        """
        total = 0
        
        # Add together all bytes
        for byte in data:
            total += ord(byte)
            
        # Only keep the last byte
        total = total & 0xFF
        
        # Subtract from 0xFF
        return 0xFF - total
        
    @staticmethod
    def verify_checksum(data, chksum):
        """
        verify_checksum: binary data, 1 byte -> boolean
        
        verify_checksum checksums the given binary, unescaped data given
        to it, and determines whether the result is correct. The result
        should be 0xFF.
        """
        total = 0
        
        # Add together all bytes
        for byte in data:
            total += ord(byte)
            
        # Add checksum too
        total += ord(chksum)
        
        # Check result
        return total == 0xFF
        
    @staticmethod
    def fill_frame(*args, **kwargs):
        """
        fill_frame: binary data ... -> valid API frame (binary data)
        
        Given the data required to fill an API frame, fill_frame will
        generate all other data as required and produce a valid API
        frame for transmission to an XBee module.
        """
        pass
    
