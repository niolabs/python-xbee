#! /usr/bin/python

"""
alarm.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

This module will communicate with a remote XBee device in order to 
implement a simple alarm clock with bed occupancy detection.
"""
import serial
from xbee import XBee

class DataSource(object):
    """
    Represents a source from which alarm times may be pulled (i.e. an
    online calendar)
    """
    def next_alarm_time(self, current_time):
        """
        next_alarm_time: datetime -> datetime
        
        Returns the next time at which the alarm should activate
        """
        raise NotImplemented()
        
class AlarmDevice(object):
    """
    Represents alarm harware, such as input and output to an from 
    the real world
    """
    
    def __init__(self, hw):
        self.hw = hw
        
    def activate(self):
        """
        activate: None -> None
        
        Activates noise-making features
        """
        raise NotImplementedError()
        
    def deactivate(self):
        """
        deactivate: None -> None
        
        Deactivates noise-making features
        """
        raise NotImplementedError()
        
    def bed_occupied(self):
        """
        bed_occupied: None -> Boolean
        
        Determines whether the bed is currently occupied
        """
        raise NotImplementedError()
        
class WakeupRoutine(object):
    """
    Represents a process by which a user should be awoken with a
    particular AlarmDevice
    """
    
    def __init__(self, device):
        self.device = device
        
    def trigger(self):
        """
        trigger: None -> None
        
        Begins the specified wakeup process with the given hardware 
        device. Does not relinquish control until the wakeup process is
        complete.
        """
        raise NotImplementedError()
        
# ================= Custom Classes =============================

class TestSource(DataSource):
    def __init__(self, time):
        super(TestSource, self).__init__()
        self.next_time = time
    
    def next_alarm_time(self, current_time):
        return self.next_time
        
class XBeeAlarm(AlarmDevice):
    DETECT_THRESH = 350
    
    def __init__(self, serial_port, remote_addr):
        # Open serial port, construct XBee1, configure remote device,
        # store as hardware
        self.remote_addr = remote_addr
        
        ser = serial.Serial(serial_port)
        xbee = XBee(ser)
        
        super(XBeeAlarm, self).__init__(xbee)
        
        # Reset remote device
        self._reset()
        
    def _reset(self):
        """
        reset: None -> None
        
        Resets the remote XBee device to a standard configuration
        """
        # Analog pin 0
        self.hw.remote_at(
            dest_addr=self.remote_addr,
            command='D0',
            parameter='\x02')
        
        # Disengage remote LED, buzzer
        self.deactivate()
        self._set_send_samples(False)
            
    def _set_LED(self, status):
        """
        _set_LED: boolean -> None
        
        Sets the status of the remote LED
        """
        # DIO pin 1 (LED), active low
        self.hw.remote_at(
            dest_addr=self.remote_addr,
            command='D1',
            parameter='\x04' if status else '\x05')
            
    def _set_buzzer(self, status):
        """
        _set_buzzer: boolean -> None
        
        Sets the status of the remote buzzer
        """
        # DIO pin 1 (LED), active low
        self.hw.remote_at(
            dest_addr=self.remote_addr,
            command='D2',
            parameter='\x05' if status else '\x04')
            
    def _set_send_samples(self, status):
        """
        _set_send_samples: boolean -> None
        
        Sets whether the remote device will send data samples once every
        second.
        """
        # Send samples once per second
        self.hw.remote_at(
            dest_addr=self.remote_addr,
            command='IR',
            parameter='\xff' if status else '\x00')

    def activate(self):
        """
        activate: None -> None
        
        Remote XBee starts making noise and turns on LED
        """
        self._set_LED(True)
        self._set_buzzer(True)
        
    def deactivate(self):
        """
        activate: None -> None
        
        Remote XBee starts making noise and turns on LED
        """
        self._set_LED(False)
        self._set_buzzer(False)
        
    def bed_occupied(self):
        """
        bed_occupied: None -> boolean
        
        Determines whether the bed is currently occupied by requesting
        data from the remote XBee and comparing the analog value with
        a threshold.
        """
        
        # Receive samples from the remote device
        self._set_send_samples(True)
        
        while True:
            packet = self.hw.wait_read_frame()
            
            if 'adc-0' in packet['samples'][0]:
                # Stop receiving samples from the remote device
                self._set_send_samples(False)
                return packet['samples'][0]['adc-0'] > XBeeAlarm.DETECT_THRESH
                
        
class SimpleWakeupRoutine(WakeupRoutine):
    """
    When triggered, activates the alarm if the bed is occupied. The 
    alarm continues until the bed is no longer occupied.
    """
    
    def trigger(self):
        from time import sleep
        
        pulse_delay = 0.1
        
        
        if self.device.bed_occupied():
             # Initial alarm
            for x in range(0, 5):
                self.device.activate()
                sleep(pulse_delay)
                self.device.deactivate()
                sleep(pulse_delay)
            
            # Allow time to escape
            sleep(30)
            
            # Extended alarm
            duration = 1
            pause = 10
            
            while self.device.bed_occupied():
                self.device.activate()
                sleep(duration)
                self.device.deactivate()
                sleep(pause)
                duration *= 2
            
def main():
    """
    Run through simple demonstration of alarm concept
    """
    alarm = XBeeAlarm('/dev/ttyUSB0', '\x56\x78')
    routine = SimpleWakeupRoutine(alarm)
    
    from time import sleep
    while True:
        """
        Run the routine with 10 second delays
        """
        try:
            print "Waiting 5 seconds..."
            sleep(5)
            print "Firing"
            routine.trigger()
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
