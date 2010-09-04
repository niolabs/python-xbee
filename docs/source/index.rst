.. python-xbee documentation master file, created by
   sphinx-quickstart on Sat Jul 24 22:28:51 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-xbee's documentation!
=======================================

.. module:: xbee

Introduction
------------

The purpose of XBee is to allow one easy access to
the advanced features of an XBee device from a 
Python application. It provides a semi-complete
implementation of the XBee binary API protocol
and allows a developer to send and receive the
information they desire without dealing with the
raw communication details.

Usage
-----

.. note::
   
   In order to use an XBee device with this library, API mode
   must be enabled. For instructions about how to do this, see
   the documentation for your XBee device.

Synchonous Mode
~~~~~~~~~~~~~~~

The following code demonstrates a minimal use-case for the
xbee package::

    import serial
    from xbee import XBee

    serial_port = serial.Serial('/dev/ttyUSB0', 9600)
    xbee = XBee(serial_port)

    while True:
        try:
            print xbee.wait_read_frame()
        except KeyboardInterrupt:
            break

    serial_port.close()

This example will perpetually read from the serial port and 
print out any data frames which arrive from a connected XBee
device. Be aware that wait_read_frame() will block until
a valid frame is received from the associated XBee device.

Asynchronous Mode
~~~~~~~~~~~~~~~~~

The xbee package is used only slightly differently when 
asynchonous notification of received data is needed::

    import serial
    import time
    from xbee import XBee

    serial_port = serial.Serial('/dev/ttyUSB0', 9600)
    
    def print_data(data):
        """
        This method is called whenever data is received
        from the associated XBee device. Its first and
        only argument is the data contained within the 
        frame.
        """
        print data

    xbee = XBee(serial_port, callback=print_data)

    while True:
        try:
            time.sleep(0.001)
        except KeyboardInterrupt:
            break

    xbee.halt()
    serial_port.close()

.. warning:: 
    
   When asychonous mode is enabled, the provided callback method
   is called by a background thread managed by the xbee package.
   Any/all thread safety considerations may apply when employing 
   this functionality to modify external state.

Note that a background thread is automatically started
to handle receiving and processing incoming data from an
XBee device. This example is functionally equivalent to the non-asyncronous
example above.

Additional Examples
~~~~~~~~~~~~~~~~~~~

For additional examples, look in the examples/ directory contained
within the xbee package source code archive or source control. 

API
----

Sending Data to an XBee Device
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to send data to an XBee device, use the send() method::

    xbee.send("at", frame='A', command='MY', parameter=None)

This example will request the 16-bit address of the connected XBee
device with an API frame marker of 'A'.

For your convenience, some optional data fields are not required.
For example, the 'parameter' field may be ommitted if empty::

    xbee.send("at", frame='A', command='MY')

Additionally, an alternate syntax is provided for all
supported commands:::

    xbee.at(frame='A', command='MY')

This example is functionally equivalent to the line(s) above.

Lastly, if an API frame identifier is not needed, the command
may be reduced to::

    xbee.at(command='MY')

For a listing of all supported API frames which may be sent,
see the documentation for your XBee device. Additionally,
xbee.impl.XBee contains a listing of all supported commands
and their associated data fields.

API Reference
~~~~~~~~~~~~~

.. autoclass:: xbee.base.XBeeBase
   :members:

.. autoclass:: xbee.XBee
   :members:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

