"""
xbee.py

By Paul Malmsten, 2010
Inspired by code written by Amit Synderman and Marco Sangalli
pmalmsten@gmail.com

XBee superclass module

This class defines data and methods common to both the Xbee Series 1 and
Series 2 modules. This class should be subclassed in order to provide
series-specific functionality.
"""
import struct, threading, time
from xbee.frame import APIFrame

class ThreadQuitException(Exception):
    pass

class XBeeBase(threading.Thread):
    """
    Abstract base class providing basic API frame generation, validation,
    and data extraction methods for XBee modules
    """
                       
    def __init__(self, ser, shorthand=True, callback=None):
        super(XBeeBase, self).__init__()
        self.serial = ser
        self.shorthand = shorthand
        self._callback = None
        self._thread_continue = False
        
        if callback:
            self._callback = callback
            self._thread_continue = True
            self._thread_quit = threading.Event()
            self.start()

    def __del__(self):
        """
        In the event that this instance is garbage collected before
        its associated serial port is closed, ensure safe thread
        shutdown.
        """
        self.halt()

    def halt(self):
        """
        halt: None -> None

        If this instance has a separate thread running, it will be
        halted. This method will wait until the thread has cleaned
        up before returning.
        """
        if self._callback:
            self._thread_continue = False
            self._thread_quit.wait()
        
    def _write(self, data):
        """
        _write: binary data -> None
        
        Packages the given binary data in an API frame and writes the 
        result to the serial port
        """
        self.serial.write(APIFrame(data).output())
        
    def run(self):
        """
        run: None -> None

        This method overrides threading.Thread.run() and is automatically
        called when an instance is created with threading enabled.
        """
        while True:
            try:
                self._callback(self.wait_read_frame())
            except ThreadQuitException:
                break
        self._thread_quit.set()
    
    def _wait_for_frame(self):
        """
        _wait_for_frame: None -> binary data
        
        _wait_for_frame will read from the serial port until a valid
        API frame arrives. It will then return the binary data
        contained within the frame.

        If this method is called as a separate thread
        and self.thread_continue is set to False, the thread will
        exit by raising a ThreadQuitException.
        """
        WAITING = 0
        PARSING = 1
        
        data = ''
        state = WAITING
        
        while True:
            if state == WAITING:
                if self._callback and not self._thread_continue:
                    raise ThreadQuitException

                if self.serial.inWaiting() == 0:
                    time.sleep(.01)
                    continue
                
                byte = self.serial.read()
                
                # If a start byte is found, swich states
                if byte == APIFrame.START_BYTE:
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
                        return APIFrame.parse(data)
                    except ValueError:
                        # Bad frame, so restart
                        data = ''
                        state = WAITING
                        
    def _build_command(self, cmd, **kwargs):
        """
        _build_command: string (binary data) ... -> binary data
        
        _build_command will construct a command packet according to the
        specified command's specification in api_commands. It will expect
        named arguments for all fields other than those with a default 
        value or a length of 'None'.
        
        Each field will be written out in the order they are defined
        in the command definition.
        """
        try:
            cmd_spec = self.api_commands[cmd]
        except AttributeError:
            raise NotImplementedError("API command specifications could not be found; use a derived class which defines 'api_commands'.")
            
        packet = ''
        
        for field in cmd_spec:
            try:
                # Read this field's name from the function arguments dict
                data = kwargs[field['name']]
            except KeyError:
                # Data wasn't given
                # Only a problem if the field has a specific length
                if field['len'] is not None:
                    # Was a default value specified?
                    default_value = field['default']
                    if default_value:
                        # If so, use it
                        data = default_value
                    else:
                        # Otherwise, fail
                        raise KeyError(
                            "The expected field %s of length %d was not provided" 
                            % (field['name'], field['len']))
                else:
                    # No specific length, ignore it
                    data = None
            
            # Ensure that the proper number of elements will be written
            if field['len'] and len(data) != field['len']:
                raise ValueError(
                    "The data provided for '%s' was not %d bytes long"\
                    % (field['name'], field['len']))
        
            # Add the data to the packet, if it has been specified
            # Otherwise, the parameter was of variable length, and not 
            #  given
            if data:
                packet += data
                
        return packet
    
    def _split_response(self, data):
        """
        _split_response: binary data -> {'id':str,
                                        'param':binary data,
                                        ...}
                                        
        _split_response takes a data packet received from an XBee device
        and converts it into a dictionary. This dictionary provides
        names for each segment of binary data as specified in the 
        api_responses spec.
        """
        # Fetch the first byte, identify the packet
        # If the spec doesn't exist, raise exception
        packet_id = data[0]
        try:
            packet = self.api_responses[packet_id]
        except AttributeError:
            raise NotImplementedError("API response specifications could not be found; use a derived class which defines 'api_responses'.")
        except KeyError:
            raise KeyError(
                "Unrecognized response packet with id byte %s"
                % data[0])
        
        # Current byte index in the data stream
        index = 1
        
        # Result info
        info = {'id':packet['name']}
        packet_spec = packet['structure']
        
        # Parse the packet in the order specified
        for field in packet_spec:
            # Store the number of bytes specified
            # If the data field has no length specified, store any
            #  leftover bytes and quit
            if field['len'] is not None:
                # Are we trying to read beyond the last data element?
                if index + field['len'] > len(data):
                    raise ValueError(
                        "Response packet was shorter than expected")
                
                field_data = data[index:index + field['len']]
                info[field['name']] = field_data
            else:
                field_data = data[index:]
                
                # Were there any remaining bytes?
                if field_data:
                    # If so, store them
                    info[field['name']] = field_data
                    index += len(field_data)
                break
            
            # Move the index
            index += field['len']
            
        # If there are more bytes than expected, raise an exception
        if index < len(data):
            raise ValueError(
                "Response packet was longer than expected")
                
        # Check if this packet was an IO sample
        # If so, process the sample data
        if 'parse_as_io_samples' in packet:
            field_to_process = packet['parse_as_io_samples']
            info[field_to_process] = XBeeBase._parse_samples(
                                        info[field_to_process])
            
        return info
        
    @staticmethod
    def _parse_samples_header(data):
        """
        _parse_samples_header: binary data in XBee IO data format ->
                        (int, [int ...], [int ...])
                        
        _parse_samples_header will read the first three bytes of the 
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
    def _parse_samples(data):
        """
        _parse_samples: binary data in XBee IO data format ->
                        [ {"dio-0":True,
                           "dio-1":False,
                           "adc-0":100"}, ...]
                           
        _parse_samples reads binary data from an XBee device in the IO
        data format specified by the API. It will then return a 
        dictionary indicating the status of each enabled IO port.
        """
        
        ## Parse and store header information
        header_data = XBeeBase._parse_samples_header(data)
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
        
    def send(self, cmd, **kwargs):
        """
        send: string param=binary data ... -> None
        
        When send is called with the proper arguments, an API command
        will be written to the serial port for this XBee device
        containing the proper instructions and data.
        
        This method must be called with named arguments in accordance
        with the api_command specification. Arguments matching all 
        field names other than those in reserved_names (like 'id' and
        'order') should be given, unless they are of variable length 
        (of 'None' in the specification. Those are optional).
        """
        # Pass through the keyword arguments
        self._write(self._build_command(cmd, **kwargs))
        
        
    def wait_read_frame(self):
        """
        wait_read_frame: None -> frame info dictionary
        
        wait_read_frame calls XBee._wait_for_frame() and waits until a
        valid frame appears on the serial port. Once it receives a frame,
        wait_read_frame attempts to parse the data contained within it
        and returns the resulting dictionary
        """
        
        frame = self._wait_for_frame()
        return self._split_response(frame.data)
        
    def __getattr__(self, name):
        """
        If a method by the name of a valid api command is called,
        the arguments will be automatically sent to an appropriate
        send() call
        """
        # If api_commands is not defined, raise NotImplementedError\
        #  If its not defined, _getattr__ will be called with its name
        if name == 'api_commands':
            raise NotImplementedError("API command specifications could not be found; use a derived class which defines 'api_commands'.")
        
        # Is shorthand enabled, and is the called name a command?
        if self.shorthand and name in self.api_commands:
            # If so, simply return a function which passes its arguments
            # to an appropriate send() call
            return lambda **kwargs: self.send(name, **kwargs)
        else:
            raise AttributeError("XBee has no attribute '%s'" % name)
