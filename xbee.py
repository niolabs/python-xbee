import struct

"""
XBee superclass module

This class defines data and methods common to both the Xbee Series 1 and
Series 2 modules. This class should be subclassed in order to provide
series-specific functionality.
"""

class XBee(object):
    START_BYTE = '\x7E'
                       
    def __init__(self, ser):
        self.serial = ser
          
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
        return chr(0xFF - total)
        
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
        
        # Only keep low bits
        total &= 0xFF
        
        # Check result
        return total == 0xFF
        
    @staticmethod
    def len_bytes(data):
        """
        len_data: binary data -> (MSB, LSB) 16-bit integer length, two bytes
        
        len_bytes counts the number of bytes to be sent and encodes the data
        length in two bytes, big-endian (most significant first).
        """
        count = len(data)
        return struct.pack("> h", count)
        
    @staticmethod
    def fill_frame(data):
        """
        fill_frame: binary data -> valid API frame (binary data)
        
        Given the data required to fill an API frame, fill_frame will
        generate all other data as required and produce a valid API
        frame for transmission to an XBee module.
        """
        # start is one byte long, length is two bytes
        # data is n bytes long (indicated by length)
        # chksum is one byte long
        return XBee.START_BYTE + XBee.len_bytes(data) + data + XBee.checksum(data)
        
    @staticmethod
    def empty_frame(frame):
        """
        empty_frame: valid API frame (binary data) -> binary data
        
        Given a valid API frame, empty_frame extracts the data contained
        inside it and verifies it against its checksum
        """
        # First two bytes are the length of the data
        raw_len = frame[1:3]
        
        # Unpack it
        data_len = struct.unpack("> h", raw_len)[0]
        
        # Read the data
        data = frame[3:3 + data_len]
        chksum = frame[-1]
        
        # Checksum check
        if not XBee.verify_checksum(data, chksum):
            raise ValueError("Invalid checksum on given frame")
            
        # If the result is valid, return it
        return data
        
        
    def write_frame(self, data):
        """
        write_frame: binary data -> None
        
        Packages the given binary data in an API frame and writes the 
        result to the serial port
        """
        self.serial.write(XBee.fill_frame(data))
        
    def wait_for_frame(self):
        """
        wait_for_frame: None -> binary data
        
        wait_for_frame will read from the serial port until a valid
        API frame arrives. It will then return the binary data
        contained within the frame.
        """
        WAITING = 0
        PARSING = 1
        
        data = ''
        state = WAITING
        
        while True:
            if state == WAITING:
                byte = self.serial.read()
                
                # If a start byte is found, swich states
                if byte == XBee.START_BYTE:
                    data += byte
                    state = PARSING
            else:
                # Save all following bytes
                data += self.serial.read()
                
                if len(data) == 3:
                    # We have the length bytes of the data
                    # Now, wait for the rest to appear
                    data_len = struct.unpack("> h", data[1:3])[0]
                    
                    # Wait for the expected number of bytes to appear
                    # Grab the checksum too
                    data += self.serial.read(data_len + 1)
                    
                    try:
                        # Try to parse and return result
                        return XBee.empty_frame(data)
                    except ValueError:
                        # Bad frame, so restart
                        data = ''
                        state = WAITING
    
