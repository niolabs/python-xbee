#! /usr/bin/python

"""
led_adc_example.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

A simple example which sets up a remote device to read an analog value
on ADC0 and a digital output on DIO1. It will then read voltage 
measurements and write an active-low result to the remote DIO1 pin.
"""

from xbee import XBee
import serial

ser = serial.Serial('/dev/ttyUSB0', 9600)
xbee = XBee(ser)

## Set up remote device
#xbee.send('remote_at', 
          #frame_id='A',
          #dest_addr_long='\x00\x00\x00\x00\x00\x00\x00\x00',
          #dest_addr='\x56\x78',
          #options='\x02',
          #command='D0',
          #parameter='\x02')
          
#print xbee.wait_read_frame()['status']

#xbee.send('remote_at', 
          #frame_id='B',
          #dest_addr_long='\x00\x00\x00\x00\x00\x00\x00\x00',
          #dest_addr='\x56\x78',
          #options='\x02',
          #command='D1',
          #parameter='\x05')
          
#print xbee.wait_read_frame()['status']
          
#xbee.send('remote_at', 
          #frame_id='C',
          #dest_addr_long='\x00\x00\x00\x00\x00\x00\x00\x00',
          #dest_addr='\x56\x78',
          #options='\x02',
          #command='IR',
          #parameter='\x32')

#print xbee.wait_read_frame()['status']

#xbee.send('remote_at', 
          #frame_id='C',
          #dest_addr_long='\x00\x00\x00\x00\x00\x00\x00\x00',
          #dest_addr='\x56\x78',
          #options='\x02',
          #command='WR')
          
# Deactivate alarm pin
xbee.remote_at(
  dest_addr='\x56\x78',
  command='D2',
  parameter='\x04')
  
xbee.remote_at(
  dest_addr='\x56\x78',
  command='WR')

#print xbee.wait_read_frame()['status']

while True:
    try:
        packet = xbee.wait_read_frame()
        print packet
        
        # If it's a sample, check it
        if packet['id'] == 'rx_io_data':
            # Set remote LED status
            if packet['samples'][0]['adc-0'] > 160:
                # Active low
                xbee.remote_at(
                  dest_addr='\x56\x78',
                  command='D1',
                  parameter='\x04')
                  
                # Active high alarm pin
                xbee.remote_at(
                  dest_addr='\x56\x78',
                  command='D2',
                  parameter='\x05')
                
            else:
                xbee.remote_at(
                  dest_addr='\x56\x78',
                  command='D1',
                  parameter='\x05')
                  
                # Deactivate alarm pin
                xbee.remote_at(
                  dest_addr='\x56\x78',
                  command='D2',
                  parameter='\x04')
                
    except KeyboardInterrupt:
        break

ser.close()
