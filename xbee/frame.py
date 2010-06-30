"""
frame.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

Represents an API frame for communicating with an XBee
"""

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
