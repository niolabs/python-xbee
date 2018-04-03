"""
base.py

By David Walker, 2017

Tornado XBee superclass module

This class defines data and methods common to all XBee modules.
This class should be subclassed in order to provide
series-specific functionality.
"""
from xbee.frame import APIFrame
from xbee.backend.base import XBeeBase as _XBeeBase
from xbee.backend.base import TimeoutException as _TimeoutException
from tornado import ioloop, gen
from tornado.locks import Event
from tornado.concurrent import Future
from collections import deque


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
        if 'io_loop' in kwargs:
            self._ioloop = kwargs.pop('io_loop')
        else:
            self._ioloop = ioloop.IOLoop.current()

        super(XBeeBase, self).__init__(*args, **kwargs)

        self._running = Event()
        self._running.set()

        self._frame_future = None
        self._frame_queue = deque()

        if self._callback:
            # Make Non-Blocking
            self.serial.timeout = 0
            self.process_frames()

        self._ioloop.add_handler(self.serial.fd,
                                 self._process_input,
                                 ioloop.IOLoop.READ)

    def halt(self):
        """
        halt: None -> None

        Stop the event, and remove the FD from the loop handler
        """
        if self._callback:
            self._running.clear()
            self._ioloop.remove_handler(self.serial.fd)

            if self._frame_future is not None:
                self._frame_future.set_result(None)
                self._frame_future = None

    @gen.coroutine
    def process_frames(self):
        """
        process_frames: None -> None

        Wait for a frame to become available, when resolved call the callback
        """
        while self._running.is_set():
            try:
                frame = yield self._get_frame()
                info = self._split_response(frame.data)
                if info is not None:
                    self._callback(info)
            except Exception as e:
                # Unexpected quit.
                if self._error_callback:
                    self._error_callback(e)

    @gen.coroutine
    def wait_read_frame(self, timeout=None):
        frame = yield self._get_frame(timeout=timeout)
        raise gen.Return(self._split_response(frame.data))

    def _get_frame(self, timeout=None):
        future = Future()
        if self._frame_queue:
            future.set_result(self._frame_queue.popleft())
        else:
            if timeout is not None:
                def on_timeout():
                    future.set_exception(_TimeoutException())

                handle = self._ioloop.add_timeout(
                    self._ioloop.time() + timeout, on_timeout
                )
                future.add_done_callback(lambda _:
                                         self._ioloop.remove_timeout(handle))

            self._frame_future = future

        return future

    def _process_input(self, data, events):
        """
        _process_input:

        _process_input will be notified when there is data ready on the
        serial connection to be read.  It will read and process the data
        into an API Frame and then either resolve a frame future, or push
        the frame into the queue of frames needing to be processed
        """
        frame = APIFrame(escaped=self._escaped)

        byte = self.serial.read()

        if byte != APIFrame.START_BYTE:
            return

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
                return

            if self._frame_future is not None:
                self._frame_future.set_result(frame)
                self._frame_future = None
            else:
                self._frame_queue.append(frame)
        except ValueError:
            return
