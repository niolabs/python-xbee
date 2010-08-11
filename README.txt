=========
XBee
=========

XBee provides an implementation of the XBee serial communication API. It
allows one to easily access advanced features of one or more XBee
devices from an application written in Python. An example use case might
look like this::

    #! /usr/bin/python
    
    # Import and init an XBee device
    from xbee import XBee
    import serial

    ser = serial.Serial('/dev/ttyUSB0', 9600)
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

Open the file docs/build/html/index.html in your web browser of choice
to view the documentation for this package.

Caveats
=======

Escaped API operation has not been implemented at this time.

Dependencies
============

PySerial

Additional Dependencies (for running tests):
--------------------------------------------

Nose

XBee Firmware
-------------

Please ensure that your XBee device is programmed with the latest firmware
provided by Digi. Using old firmware revisions is not supported and
may result in unspecified behavior.

Contributors
==================

Paul Malmsten <pmalmsten@gmail.com>

Special Thanks
==================

Amit Synderman,
Marco Sangalli
