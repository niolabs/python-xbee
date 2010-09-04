#! /usr/bin/python

"""
dispatch.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

This example continuously reads the serial port and dispatches packets
which arrive to appropriate methods for processing.
"""

from xbee.helpers.dispatch import Dispatch
import serial

PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

# Open serial port
ser = serial.Serial(PORT, BAUD_RATE)

# Create handlers for various packet types
def status_handler(name, packet):
    print "Status Update - Status is now: ", packet['status']

def io_sample_handler(name, packet):
    print "Samples Received: ", packet['samples']

# When a Dispatch is created with a serial port, it will automatically
# create an XBee object on your behalf for accessing the device.
# If you wish, you may explicitly provide your own XBee:
#
#  xbee = XBee(ser)
#  dispatch = Dispatch(xbee=xbee)
#
# Functionally, these are the same.
dispatch = Dispatch(ser)

# Register the packet handlers with the dispatch:
#  The string name allows one to distinguish between mutiple registrations
#   for a single callback function
#  The second argument is the function to call
#  The third argument is a function which determines whether to call its
#   associated callback when a packet arrives. It should return a boolean.
dispatch.register(
    "status", 
    status_handler, 
    lambda packet: packet['id']=='status'
)

dispatch.register(
    "io_data", 
    io_sample_handler,
    lambda packet: packet['id']=='rx_io_data'
)

try:
    # run() will loop infinitely while waiting for and processing
    # packets which arrive. Don't expect it to return (unless an
    # exception occurs).
    dispatch.run()
except KeyboardInterrupt:
    pass

ser.close()
