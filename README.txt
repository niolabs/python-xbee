=========
XBee
=========

XBee provides an implementation of the XBee serial communication API. It
allows one to easily access advanced features of one or more XBee
devices from an application written in Python. An example use case might
look like this::

    #! /usr/bin/python
    
    # Import and init an XBee device
    from xbee import XBee,ZigBee
    import serial

    ser = serial.Serial('/dev/ttyUSB0', 9600)

    # Use an XBee 802.15.4 device
    # To use with an XBee ZigBee device, replace with:
    #xbee = ZigBee(ser)
    xbee = XBee(ser)
    
    # Set remote DIO pin 2 to low (mode 4)
    xbee.remote_at(
      dest_addr='\x56\x78',
      command='D2',
      parameter='\x04')
      
    xbee.remote_at(
      dest_addr='\x56\x78',
      command='WR')
      
      
Installation
============

Extract the source code to your computer, then run the following command
in the root of the source tree::

    python setup.py install
    
This will automatically test and install the package for you. 

Additionally, one may run this package's automated tests at any time
by executing::

    python setup.py test

If a Test Fails
---------------

If an automated test fails, the installation will be halted to prevent 
one from using a potentially broken build. 

In this event, one may comment out the 'strict' flag in setup.cfg in 
order to force the installation to proceed. Do so at your own risk.

Documentation
=============

See the python-xbee project on Google Code (https://code.google.com/p/python-xbee/downloads/list)
for the latest documentation. 
    
To build the documentation yourself, ensure that Sphynx (http://sphinx.pocoo.org/)
is installed. Then cd into the docs folder, and run 'make html'. The documentation can then be opened in
any modern web browser at docs/build/html/index.html.

For more information about building or modifying this project's documentation, see
the documentation for the Sphinx project.

Dependencies
============

PySerial

Additional Dependencies
--------------------------------------------

To run automated tests: Nose (https://code.google.com/p/python-nose/)
To build the documentation: Sphinx (http://sphinx.pocoo.org/)

XBee Firmware
-------------

Please ensure that your XBee device is programmed with the latest firmware
provided by Digi. Using an old firmware revision is not supported and
may result in unspecified behavior.

Contributors
==================

Paul Malmsten <pmalmsten@gmail.com>
Greg Rapp <gdrapp@gmail.com>
Brian <blalor@bravo5.org>

Special Thanks
==================

Amit Synderman,
Marco Sangalli
