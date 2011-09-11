"""
python2to3.py

By Paul Malmsten, 2011

Helper functions for handling Python 2 and Python 3 datatype shenanigans.
"""

def byteToInt(byte):
	"""
	byte -> int
	
	Determines whether to use ord() or not to get a byte's value.
	"""
	return ord(byte) if hasattr(byte, 'encode') else byte
	
def intToByte(i):
	"""
	int -> byte
	
	Determines whether to use chr() or bytes() to return a bytes object.
	"""
	return chr(i) if hasattr(bytes(), 'encode') else bytes([i])
