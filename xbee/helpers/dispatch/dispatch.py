"""
dispatch.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

Provides the Dispatch class, which allows one to filter incoming data
packets from an XBee device and call an appropriate method when
one arrives.
"""

from xbee import XBee

class Dispatch(object):
    def __init__(self, ser=None, xbee=None):
        if xbee:
            self.xbee = xbee
        elif ser:
            self.xbee = XBee(ser)
        else:
            raise ValueError("Either a serial port or an XBee must be provided to construct a Dispatch")
            
        self.handlers = []
            
    def register(self, name, callback, filter):
        """
        register: string, function: string, data -> None, function: data -> boolean -> None
        
        Register will save the given name, callback, and filter function
        for use when a packet arrives. When one arrives, the filter
        function will be called to determine whether to call its associated
        callback function. If the filter method returns true, the callback
        method will be called with its associated name string and the packet
        which triggered the call.
        """
        self.handlers.append(
            {'name':name,
             'callback':callback,
             'filter':filter}
        )
        
    def run(self, oneshot=False):
        """
        run: boolean -> None
        
        run will read from the associated XBee device until a packet
        arrives. When one does, it will check it against each registered
        callback method and call each callback whose filter function
        returns true.
        """
        
        while True:
            packet = self.xbee.wait_read_frame()
            for handler in self.handlers:
                if handler['filter'](packet):
                    # Call the handler method with its associated
                    # name and the packet which passed its filter check
                    handler['callback'](handler['name'], packet)
                    
            if oneshot:
                break
