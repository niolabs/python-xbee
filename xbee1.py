"""
xbee1.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

This module implements an XBee Series 1 driver.
"""
import struct
from xbee import XBee

class XBee1(XBee):
    """
    Provides an implementation of the XBee API for Series 1 modules
    with recent firmware.
    
    Commands may be sent to a device by instansiating this class with
    a serial port object (see PySerial) and then calling the send
    method with the proper information specified by the API. Data may
    be read from a device (syncronously only, at the moment) by calling 
    wait_read_frame.
    """
    # Packets which can be sent to an XBee
    
    # Format: 
    #        {name of command:
    #           [{name:field name, len:field length, default: default value sent}
    #            ...
    #            ]
    #         ...
    #         }
    api_commands = {"at":
                        [{'name':'id',        'len':1,      'default':'\x88'},
                         {'name':'frame_id',  'len':1,      'default':'\x00'},
                         {'name':'command',   'len':2,      'default':None},
                         {'name':'parameter', 'len':None,   'default':None}],
                    "queued_at":
                        [{'name':'id',        'len':1,      'default':'\x09'},
                         {'name':'frame_id',  'len':1,      'default':'\x00'},
                         {'name':'command',   'len':2,      'default':None},
                         {'name':'parameter', 'len':None,   'default':None}]
                    "remote_at":
                        [{'name':'id',              'len':1,        'default':'\x17'},
                         {'name':'frame_id',        'len':1,        'default':'\x00'},
                         # dest_addr_long is 8 bytes (64 bits), so use an unsigned long long
                         {'name':'dest_addr_long',  'len':8,        'default':struct.pack('>Q', 0)}
                         {'name':'dest_addr',       'len':2,        'default':'\xFF\xFE'}
                         {'name':'command',         'len':2,        'default':None},
                         {'name':'parameter',       'len':None,     'default':None}],
                    "tx_long_addr":
                        [{'name':'id',              'len':1,        'default':'\x00'},
                         {'name':'frame_id',        'len':1,        'default':'\x00'},
                         {'name':'dest_addr',       'len':8,        'default':struct.pack('>Q', 0)}
                         {'name':'options',         'len':1,        'default':'\x00'},
                         {'name':'data',            'len':None,     'default':None}],
                    "tx":
                        [{'name':'id',              'len':1,        'default':'\x01'},
                         {'name':'frame_id',        'len':1,        'default':'\x00'},
                         {'name':'dest_addr',       'len':8,        'default':struct.pack('>Q', 0)}
                         {'name':'options',         'len':1,        'default':'\x00'},
                         {'name':'data',            'len':None,     'default':None}]
                    }
    
    # Packets which can be received from an XBee
    
    # Format: 
    #        {id byte received from XBee:
    #           {name: name of response
    #            structure:
    #                [ {'name': name of field, 'len':length of field}
                      ...
                      ]
    #            parse_as_io_samples:name of field to parse as io
    #           }
    #           ...
    #        }
    #
    api_responses = {"\x80":
                        {'name':'rx_long_addr',
                         'structure':
                            [{'name':'source_addr', 'len':8},
                             {'name':'rssi',        'len':1},
                             {'name':'options',     'len':1},
                             {'name':'rf_data',     'len':None}]},
                     "\x81":
                        {'name':'rx',
                         'structure':
                            [{'name':'source_addr', 'len':2},
                             {'name':'rssi',        'len':1},
                             {'name':'options',     'len':1},
                             {'name':'rf_data',     'len':None}]},
                     "\x83":
                        {'name':'rx_io_data',
                         'structure':
                            [{'name':'source_addr', 'len':2},
                             {'name':'rssi',        'len':1},
                             {'name':'options',     'len':1},
                             {'name':'samples',     'len':None}]
                         'parse_as_io_samples':'samples'},
                     "\x89":
                        {'name':'tx_status',
                         'structure':
                            [{'name':'frame_id',    'len':1},
                             {'name':'status',      'len':1}]},
                     "\x8a":
                        {'name':'status',
                         'structure':
                            [{'name':'status',      'len':1}]},
                     "\x88":
                        {'name':'at_response',
                         'structure':
                            [{'name':'frame_id',    'len':1},
                             {'name':'command',     'len':2},
                             {'name':'status',      'len':1},
                             {'name':'parameter',   'len':None}]},
                     "\x97":
                        {'name':'remote_at_response',
                         'structure':
                            [{'name':'frame_id',        'len':1},
                             {'name':'source_addr_long','len':8},
                             {'name':'source_addr',     'len':2},
                             {'name':'command',         'len':2},
                             {'name':'status',          'len':1},
                             {'name':'parameter',       'len':None}]},
                     }
    
    def __init__(self, ser):
        # Call the super class constructor to save the serial port
        super(XBee1, self).__init__(ser)

    def send(self, cmd, **kwargs):
        """
        send: string param=binary data ... -> None
        
        When send is called with the proper arguments, an API command
        will be written to the serial port for this XBee Series 1 device
        containing the proper instructions and data.
        
        This method must be called with named arguments in accordance
        with the api_command specification. Arguments matching all 
        field names other than those in reserved_names (like 'id' and
        'order') should be given, unless they are of variable length 
        (of 'None' in the specification. Those are optional).
        """
        # Pass through the keyword arguments
        self.write_frame(XBee1.build_command(cmd, **kwargs))
        
        
    def wait_read_frame(self):
        """
        wait_read_frame: None -> frame info dictionary
        
        wait_read_frame calls XBee.wait_for_frame() and waits until a
        valid frame appears on the serial port. Once it receives a frame,
        wait_read_frame attempts to parse the data contained within it
        and returns the resulting dictionary
        """
        
        frame_data = self.wait_for_frame()
        return XBee1.split_response(frame_data)

    @staticmethod
    def build_command(cmd, **kwargs):
        """
        build_command: string (binary data) ... -> binary data
        
        build_command will construct a command packet according to the
        specified command's specification in api_commands. It will expect
        named arguments for all fields other than 'id','order', and those 
        with a specified length of 'None'.
        
        the 'id' field will be written first, followed by each other field
        in the order specified by the 'order' key.
        """
        
        cmd_spec = XBee1.api_commands[cmd]
        packet = cmd_spec['id']
        
        for param in cmd_spec['order']:
            # Skip 'id' and 'order'
            if param in XBee1.reserved_names:
                continue
                
            # Fetch it
            try:
                data = kwargs[param]
            except KeyError:
                try:
                    field_length = cmd_spec[param]
                except KeyError:
                    # The text in the 'order' API field def. was probably wrong
                    raise KeyError(
                        'The field \'%s\' was not found. Is the field order for \'%s\' properly defined?' % 
                        (param, cmd_spec['id'])
                    )
                      
                # Only a problem if the field has a specific length
                if field_length is not None:
                    raise KeyError(
                        "The expected field %s of length %d was not provided" 
                        % (param, cmd_spec[param]))
                else:
                    data = None
            
            # Ensure that the proper number of elements will be written
            if data and cmd_spec[param] and len(data) != cmd_spec[param]:
                raise ValueError(
                    "The data provided was not %d bytes long"\
                    % cmd_spec[param])
        
            # Add the data to the packet, if it has been specified
            # Otherwise, the parameter was of variable length, and not given
            if data:
                packet += data
                
        return packet
        
    @staticmethod
    def split_response(data):
        """
        split_response: binary data -> {'id':str,
                                        'param':binary data,
                                        ...}
                                        
        split_response takes a data packet received from an XBee device
        and converts it into a dictionary. This dictionary provides
        names for each segment of binary data as specified in the 
        api_responses spec.
        """
        # Fetch the first byte, identify the packet
        # If the spec doesn't exist, raise exception
        packet_id = data[0]
        try:
            packet_spec = XBee1.api_responses[packet_id]
        except KeyError:
            raise KeyError(
                "Unrecognized response packet with id byte %s"
                % data[0])
        
        # Current byte index in the data stream
        index = 1
        
        # Result info
        info = {'id':packet_spec['id']}
        
        # Parse the packet in the order specified
        for param in packet_spec['order']:
            # Skip reserved fields
            if param in XBee1.reserved_names:
                continue
            
            # Raise a nicer exception on a bad API definition
            try:
                field_len = packet_spec[param]
            except KeyError:
                # The text in the 'order' field was probably wrong
                raise KeyError(
                        'The field \'%s\' was not found. Is the field order for \'%s\' properly defined?' % 
                        (param, packet_id))
            
            # Store the number of bytes specified
            # If the data field has no length specified, store any
            #  leftover bytes and quit
            if field_len is not None:
                # Are we trying to read beyond the last data element?
                if index + field_len > len(data):
                    raise ValueError(
                        "Response packet was shorter than expected")
                
                field = data[index:index + field_len]
                info[param] = field
            else:
                field = data[index:]
                
                # Were there any remaining bytes?
                if field:
                    # If so, store them
                    info[param] = field
                    index += len(field)
                break
            
            # Move the index
            index += field_len
            
        # If there are more bytes than expected, raise an exception
        if index < len(data):
            raise ValueError(
                "Response packet was longer than expected")
                
        # Check if this packet was an IO sample
        # If so, process the sample data
        if packet_id in XBee1.io_data_packets:
            info['samples'] = XBee1.parse_samples(info['samples'])
            
        return info
        
    @staticmethod
    def parse_samples_header(data):
        """
        parse_samples_header: binary data in XBee IO data format ->
                        (int, [int ...], [int ...])
                        
        parse_samples_header will read the first three bytes of the 
        binary data given and will return the number of samples which
        follow, a list of enabled digital inputs and a list of enabled
        analog inputs
        """
        
        ## Parse the header, bytes 0-2
        dio_enabled = []
        adc_enabled = []
        
        # First byte: number of samples
        len_raw = data[0]
        len_samples = ord(len_raw)
        
        # Second-third bytes: enabled pin flags
        sources_raw = data[1:3]
        
        # In order to put the io line names in list positions which
        # match their number (for ease of traversal), the second byte
        # will be read first
        byte_2_data = ord(sources_raw[1])
        
        # Check each flag
        #  DIO lines 0-7
        i = 1
        for dio in range(0, 8):
            if byte_2_data & i:
                dio_enabled.append(dio)
            i *= 2
            
        # Byte 1
        byte_1_data = ord(sources_raw[0])
        
        # Grab DIO8 first
        if byte_1_data & 1:
            dio_enabled.append(8)
        
        # Check each flag (after the first)
        #  ADC lines 0-5
        i = 2
        for adc in range(0, 6):
            if byte_1_data & i:
                adc_enabled.append(adc)
            i *= 2
            
        return (len_samples, dio_enabled, adc_enabled)
        
    @staticmethod
    def parse_samples(data):
        """
        parse_samples: binary data in XBee IO data format ->
                        [ {"dio-0":True,
                           "dio-1":False,
                           "adc-0":100"}, ...]
                           
        parse_samples reads binary data from an XBee device in the IO
        data format specified by the API. It will then return a dictionary
        indicating the status of each enabled IO port.
        """
        
        ## Parse and store header information
        header_data = XBee1.parse_samples_header(data)
        len_samples, dio_enabled, adc_enabled = header_data
        
        samples = []
        
        ## Parse the samples
        # Start at byte 3
        byte_pos = 3
        
        for i in range(0, len_samples):
            sample = {}
            
            # If one or more DIO lines are set, the first two bytes
            # contain their values
            if dio_enabled:
                # Get two bytes
                values = data[byte_pos:byte_pos + 2]
                
                # Read and store values for all enabled DIO lines
                for dio in dio_enabled:
                    # Second byte contains values for 0-7
                    # If we want number 8, switch to the first byte, and
                    #  move back to the beginning
                    if dio > 7:
                        sample["dio-%d" % dio] = True if ord(values[0]) & 2 ** (dio - 8) else False
                    else:
                        sample["dio-%d" % dio] = True if ord(values[1]) & 2 ** dio else False
                
                # Move the starting position for the next new byte
                byte_pos += 2
                
            # If one or more ADC lines are set, the remaining bytes, in
            # pairs, represent their values, MSB first.
            if adc_enabled:
                for adc in adc_enabled:
                    # Analog reading stored in two bytes
                    value_raw = data[byte_pos:byte_pos + 2]
                    
                    # Unpack the bits
                    value = struct.unpack("> h", value_raw)[0]
                    
                    # Only 10 bits are meaningful
                    value &= 0x3FF
                    
                    # Save the result
                    sample["adc-%d" % adc] = value
                    
                    # Move the starting position for the next new byte
                    byte_pos += 2
                
            samples.append(sample)
            
        return samples
