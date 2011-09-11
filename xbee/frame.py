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
    
    START_BYTE = b'\x7E'
    ESCAPE_BYTE = b'\x7D'
    XON_BYTE = b'\x11'
    XOFF_BYTE = b'\x13'
    ESCAPE_BYTES = (START_BYTE, ESCAPE_BYTE, XON_BYTE, XOFF_BYTE)
    
    def __init__(self, data=b'', escaped=False):
        self.data = data
        self.raw_data = b''
        self.escaped = escaped
        self._unescape_next_byte = False
        
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
            if hasattr(byte, 'encode'):
                # Python 2.X
                total += ord(byte)
            else:
                # Python 3.X
                total += byte
            
        # Only keep the last byte
        total = total & 0xFF
        
        # Subtract from 0xFF
        if hasattr(bytes(), 'encode'):
            # Python 2.X
            return chr(0xFF - total)
        else:
            return bytes([0xFF - total])

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
        return bytes(struct.pack("> h", count))
        
    def output(self):
        """
        output: None -> valid API frame (binary data)
        
        output will produce a valid API frame for transmission to an 
        XBee module.
        """
        # start is one byte long, length is two bytes
        # data is n bytes long (indicated by length)
        # chksum is one byte long
        data = self.len_bytes() + self.data + self.checksum()

        # Only run the escaoe process if it hasn't been already
        if self.escaped and len(self.raw_data) < 1:
            self.raw_data = APIFrame.escape(data)

        if self.escaped:
            data = self.raw_data

        # Never escape start byte
        return APIFrame.START_BYTE + data

    @staticmethod
    def escape(data):
        """
        escape: byte string -> byte string

        When a 'special' byte is encountered in the given data string,
        it is preceded by an escape byte and XORed with 0x20.
        """

        escaped_data = b""
        for byte in data:
            if byte in APIFrame.ESCAPE_BYTES:
                escaped_data += APIFrame.ESCAPE_BYTE
                
                if hasattr(byte, 'encode'):
                    # Python 2.X in use
                    escaped_data += chr(0x20 ^ ord(byte))
                else:
                    # Python 3.X in use
                    escaped_data += bytes([0x20 ^ byte])
            else:
                escaped_data += byte
        
        return escaped_data

    def fill(self, byte):
        """
        fill: byte -> None

        Adds the given raw byte to this APIFrame. If this APIFrame is marked
        as escaped and this byte is an escape byte, the next byte in a call
        to fill() will be unescaped.
        """

        if self._unescape_next_byte:
            if hasattr(byte, 'encode'):
                # Python 2.X
                byte = chr(ord(byte) ^ 0x20) 
            else:
                # Python 3.X
                byte = byte ^ 0x20
            self._unescape_next_byte = False
        elif self.escaped and byte == APIFrame.ESCAPE_BYTE:
            self._unescape_next_byte = True
            return

        if hasattr(byte, 'encode'):
            # Python 2.X
            self.raw_data += byte
        else:
            self.raw_data += bytes([byte])

    def remaining_bytes(self):
        remaining = 3

        if len(self.raw_data) >= 3:
            # First two bytes are the length of the data
            raw_len = self.raw_data[1:3]
            data_len = struct.unpack("> h", raw_len)[0]

            remaining += data_len

            # Don't forget the checksum
            remaining += 1

        return remaining - len(self.raw_data)
        
    def parse(self):
        """
        parse: None -> None
        
        Given a valid API frame, parse extracts the data contained
        inside it and verifies it against its checksum
        """
        if len(self.raw_data) < 3:
            ValueError("parse() may only be called on a frame containing at least 3 bytes of raw data (see fill())")

        # First two bytes are the length of the data
        raw_len = self.raw_data[1:3]
        
        # Unpack it
        data_len = struct.unpack("> h", raw_len)[0]
        
        # Read the data
        data = self.raw_data[3:3 + data_len]
        chksum = self.raw_data[-1]

        # Checksum check
        self.data = data
        if not self.verify(chksum):
            raise ValueError("Invalid checksum")
