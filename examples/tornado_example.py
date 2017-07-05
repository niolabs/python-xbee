#! /usr/bin/python

from xbee.tornado import XBee
from tornado import gen, ioloop
import serial

"""
tornado_example.py
By David Walker, 2017

Demonstrats a simple read/write loop using the Tornado IO Loop
"""


def handle_data(data):
    print(data['data'])


@gen.coroutine
def main():
    try:
        # Open serial port
        ser = serial.Serial('/dev/ttys009', 9600)

        # Create XBee Series 1 object
        xbee = XBee(ser, callback=handle_data)

        while True:
            yield gen.sleep(1)
            # Send AT packet
            xbee.send('at', frame_id='B', command='DL')
    except KeyboardInterrupt:
        ioloop.IOLoop.current().stop()
    finally:
        xbee.halt()
        ser.close()


if __name__ == '__main__':
    ioloop.IOLoop.current().spawn_callback(main)
    ioloop.IOLoop.current().start()
    ioloop.IOLoop.current().close()
