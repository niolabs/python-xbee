#!/usr/bin/env python
"""
shell.py

Amit Snyderman, 2009
<amit@amitsnyderman.com>

Updated by Paul Malmsten, 2010
pmalmsten@gmail.com

Provides a simple shell for testing XBee devices. Currently, the shell
only allows one to parse and print received data; sending is not
supported.
"""
# $Id: xbee-serial-terminal.py 7 2009-12-30 16:25:08Z amitsnyderman $

import sys, time, cmd, serial, binascii
from xbee import XBee1

class XBeeShell(cmd.Cmd):
	def __init__(self):
		cmd.Cmd.__init__(self)
		self.prompt = "xbee% "
		self.serial = serial.Serial()
	
	def default(self, p):
		if not self.serial.isOpen():
			print "You must set a serial port first."
		else:
			if p == '+++':
				self.serial.write(p)
				time.sleep(2)
			else:
				self.serial.write('%s\r' % p)
				time.sleep(0.5)
			
			output = ''
			while self.serial.inWaiting():
				output += self.serial.read()
			print output.replace('\r', '\n').rstrip()
	
	def do_serial(self, p):
		"""Set the serial port, e.g.: /dev/tty.usbserial-A4001ib8"""
		try:
			self.serial.port = p
			self.serial.open()
			print 'Opening serial port: %s' % p
		except Exception, e:
			print 'Unable to open serial port: %s' % p
	
	def do_baudrate(self, p):
		"""Set the serial port's baud rate, e.g.: 19200"""
		self.serial.baudrate = p
	
	def do_watch(self, p):
		if not self.serial.isOpen():
			print "You must set a serial port first."
		else:
			while 1:
				xbee = XBee1(self.serial)
				packet = xbee.wait_read_frame()
				print packet
	
	def do_exit(self, p):
		"""Exits from the XBee serial console"""
		self.serial.close()
		return 1

if __name__ == '__main__':
	shell = XBeeShell()
	shell.cmdloop()
