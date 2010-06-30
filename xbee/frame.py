"""
frame.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

Represents an API frame for communicating with an XBee
"""
import struct

class APIFrame:
    def __init__(self, data):
        self.data = data
        
    def checksum(self):
        """
        checksum: None -> single checksum byte
        
        checksum adds all bytes of the binary, unescaped data in the frame, 
        saves the last byte of the result, and subtracts it from 0xFF. The
        final result is the checksum
        """
        total = 0
        
        # Add together all bytes
        for byte in self.data:
            total += ord(byte)
            
        # Only keep the last byte
        total = total & 0xFF
        
        # Subtract from 0xFF
        return chr(0xFF - total)

    def verify(self, chksum):
        """
        verify_checksum: 1 byte -> boolean
        
        verify_checksum checksums the given binary, unescaped data given
        to it, and determines whether the result is correct. The result
        should be 0xFF.
        """
        total = 0
        
        # Add together all bytes
        for byte in self.data:
            total += ord(byte)
            
        # Add checksum too
        total += ord(chksum)
        
        # Only keep low bits
        total &= 0xFF
        
        # Check result
        return total == 0xFF

    def len_bytes(self):
        """
        len_data: None -> (MSB, LSB) 16-bit integer length, two bytes
        
        len_bytes counts the number of bytes to be sent and encodes the data
        length in two bytes, big-endian (most significant first).
        """
        count = len(self.data)
        return struct.pack("> h", count)
