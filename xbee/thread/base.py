"""
base.py

By Paul Malmsten, 2010
Inspired by code written by Amit Synderman and Marco Sangalli
pmalmsten@gmail.com

XBee superclass module

This class defines data and methods common to all XBee modules.
This class should be subclassed in order to provide
series-specific functionality.
"""
from xbee.frame import APIFrame
from xbee.backend.base import XBeeBase as _XBeeBase
from xbee.backend.base import TimeoutException as _TimeoutException
import threading
import time


class ThreadQuitException(Exception):
    pass


class XBeeBase(_XBeeBase):
    """
    Abstract base class providing command generation and response
    parsing methods for XBee modules.

    Constructor arguments:
        ser:    The file-like serial port to use.


        shorthand: boolean flag which determines whether shorthand command
                   calls (i.e. xbee.at(...) instead of xbee.send("at",...)
                   are allowed.

        callback: function which should be called with frame data
                  whenever a frame arrives from the serial port.
                  When this is not None, a background thread to monitor
                  the port and call the given function is automatically
                  started.

        escaped: boolean flag which determines whether the library should
                 operate in escaped mode. In this mode, certain data bytes
                 in the output and input streams will be escaped and unescaped
                 in accordance with the XBee API. This setting must match
                 the appropriate api_mode setting of an XBee device; see your
                 XBee device's documentation for more information.

        error_callback: function which should be called with an Exception
                 whenever an exception is raised while waiting for data from
                 the serial port. This will only take affect if the callback
                 argument is also used.
    """

    def __init__(self, *args, **kwargs):
        super(XBeeBase, self).__init__(*args, **kwargs)
        self._thread_continue = False

        if self._callback:
            self._thread_continue = True
            self._thread = threading.Thread(target=self.run,
                                            name=self.__class__.__name__)
            self._thread.start()

    def halt(self):
        """
        halt: None -> None

        If this instance has a separate thread running, it will be
        halted. This method will wait until the thread has cleaned
        up before returning.
        """
        if self._callback:
            self._thread_continue = False
            self._thread.join()

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
                # Expected termintation of thread due to self.halt()
                break
            except Exception as e:
                # Unexpected thread quit.
                if self._error_callback:
                    self._error_callback(e)

    def wait_read_frame(self, timeout=None):
        """
        wait_read_frame: None -> frame info dictionary

        wait_read_frame calls XBee._wait_for_frame() and waits until a
        valid frame appears on the serial port. Once it receives a frame,
        wait_read_frame attempts to parse the data contained within it
        and returns the resulting dictionary
        """
        frame = self._wait_for_frame(timeout)
        return self._split_response(frame.data)

    def _wait_for_frame(self, timeout=None):
        """
        _wait_for_frame: None -> binary data

        _wait_for_frame will read from the serial port until a valid
        API frame arrives. It will then return the binary data
        contained within the frame.

        If this method is called as a separate thread
        and self.thread_continue is set to False, the thread will
        exit by raising a ThreadQuitException.
        """
        frame = APIFrame(escaped=self._escaped)

        deadline = 0
        if timeout is not None and timeout > 0:
            deadline = time.time() + timeout

        while True:
                if self._callback and not self._thread_continue:
                    raise ThreadQuitException

                if self.serial.inWaiting() == 0:
                    if deadline and time.time() > deadline:
                        raise _TimeoutException
                    time.sleep(.01)
                    continue

                byte = self.serial.read()

                if byte != APIFrame.START_BYTE:
                    continue

                # Save all following bytes, if they are not empty
                if len(byte) == 1:
                    frame.fill(byte)

                while(frame.remaining_bytes() > 0):
                    byte = self.serial.read()

                    if len(byte) == 1:
                        frame.fill(byte)

                try:
                    # Try to parse and return result
                    frame.parse()

                    # Ignore empty frames
                    if len(frame.data) == 0:
                        frame = APIFrame()
                        continue

                    return frame
                except ValueError:
                    # Bad frame, so restart
                    frame = APIFrame(escaped=self._escaped)
