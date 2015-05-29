Tools include a library for working with XBee API mode serial data and an XBee serial command shell for interacting with XBee radios. E.g.:

```
"""
Continuously read the serial port and process IO data received from a remote XBee.
"""

from xbee import XBee
import serial

ser = serial.Serial('/dev/ttyUSB0', 9600)

xbee = XBee(ser)

# Continuously read and print packets
while True:
    try:
        response = xbee.wait_read_frame()
        print response
    except KeyboardInterrupt:
        break
        
ser.close()
```

Originally developed as a port of [Rob Faludi's XBee Processing library](http://www.faludi.com/code/xbee-api-library-for-processing/).