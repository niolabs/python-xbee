import struct
from xbee import XBee

"""
xbee1.py
By Paul Malmsten

This module implements an XBee Series 1 driver.
"""

class XBee1(XBee):
    # Packets which can be sent to an XBee
    
    # Format: 
    #        name of command
    #           id: id byte to be sent to XBee
    #           param_name: number of bytes to send
    #           param_name: None (size of parameter is variable, 0<n<10 bytes)
    #           order: [param_name, ...] (order in which parameters should be sent)  
    api_commands = {"at":
                        {"id":'\x08',
                         'frame_id':1,
                         'command':2,
                         'parameter': None,
                         'order':['frame_id','command','parameter']}
                    }
    
    # Packets which can be received from an XBee
    
    # Format: 
    #        id byte received from XBee
    #           id: name of response
    #           param_name: number of bytes to read
    #           param_name: None (size of parameter is variable, 0<n<10) 
    api_responses = {'\x8a': 
                        {"id": 'status',
                         "status": 1,
                         "order": ['status']},
                     '\x88':
                        {"id":'at_response',
                         'frame_id':1,
                         'command':2,
                         'status':1,
                         'parameter': None,
                         'order':['frame_id','command','status','parameter']}
                     }

    reserved_names = ['id','order']

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
                # Only a problem if the field has a specific length
                if cmd_spec[param] is not None:
                    raise KeyError(
                        "The expected field %s of length %d was not provided" 
                        % (param, cmd_spec[param]))
                else:
                    data = None
            
            # Ensure that the proper number of elements will be written
            if data and len(data) != cmd_spec[param]:
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
        try:
            packet_spec = XBee1.api_responses[data[0]]
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
                
            field_len = packet_spec[param]
            
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
        
        return info
            
                
            
            
