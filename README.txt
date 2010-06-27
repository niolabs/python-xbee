=========
XBee
=========

XBee provides an implementation of the XBee serial communication API. It
allows one to easily access advanced features of one or more XBee
devices from an application written in Python. An example use case might
look like this::

    #! /usr/bin/python
    
    # Import and init a XBee Series 1 device
    from xbee import XBee1
    import serial

    ser = serial.Serial('/dev/ttyUSB0', 9600)
    xbee = XBee1(ser)
    
    # Set remote DIO pin 2 to low (mode 4)
    xbee.remote_at(
      dest_addr='\x56\x78',
      command='D2',
      parameter='\x04')
      
    xbee.remote_at(
      dest_addr='\x56\x78',
      command='WR')
      
      
Usage
============

Series 1
---------

To use this library with an XBee Series 1 device, import the class
XBee1 and call its constructor with a serial port object.

In order to send commands via the API, call a method with the same
name as the command which you would like to send with words separated
by _'s. For example, to send a Remote AT command, one would call 
remote_at().

The arguments to be given to each method depend upon the command to be 
sent. For more information concerning the names of the arguments which
are expected and the proper data types for each argument, consult the
API manual for the XBee Series 1 device, or consult the source code.

Series 2
-----------

At this time, Series 2 API commands have not yet been translated from 
the API documentation into the library.

Contributors
==================

Paul Malmsten <pmalmsten@gmail.com>

Special Thanks
==================

Amit Synderman
Marco Sangalli
