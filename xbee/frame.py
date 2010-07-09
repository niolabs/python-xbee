"""
frame.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

Represents an API frame for communicating with an XBee
"""
import struct

class APIFrame:
    """
    Represents a frame of data to be sent to or which was received 
    from an XBee device
    """
    
    START_BYTE = '\x7E'
    
    def __init__(self, data):
        self.data = data
        
    def checksum(self):
        """
        checksum: None -> single checksum byte
        
        checksum adds all bytes of the binary, unescaped data in the 
        frame, saves the last byte of the result, and subtracts it from 
        0xFF. The final result is the checksum
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
        verify: 1 byte -> boolean
        
        verify checksums the frame, adds the expected checksum, and 
        determines whether the result is correct. The result should 
        be 0xFF.
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
        
        len_bytes counts the number of bytes to be sent and encodes the 
        data length in two bytes, big-endian (most significant first).
        """
        count = len(self.data)
        return struct.pack("> h", count)
        
    def output(self):
        """
        output: None -> valid API frame (binary data)
        
        output will produce a valid API frame for transmission to an 
        XBee module.
        """
        # start is one byte long, length is two bytes
        # data is n bytes long (indicated by length)
        # chksum is one byte long
        return APIFrame.START_BYTE + \
                self.len_bytes() + \
                self.data + \
                self.checksum()
        
    @staticmethod
    def parse(raw_data):
        """
        parse: valid API frame (binary data) -> binary data
        
        Given a valid API frame, empty_frame extracts the data contained
        inside it and verifies it against its checksum
        """
        # First two bytes are the length of the data
        raw_len = raw_data[1:3]
        
        # Unpack it
        data_len = struct.unpack("> h", raw_len)[0]
        
        # Read the data
        data = raw_data[3:3 + data_len]
        chksum = raw_data[-1]
        
        # Checksum check
        frame = APIFrame(data)
        if not frame.verify(chksum):
            raise ValueError("Invalid checksum on given frame")
            
        # If the result is valid, return it
        return frame
