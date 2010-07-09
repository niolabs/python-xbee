from distutils.core import setup

setup(
    name='XBee',
    version='1.7.1',
    author='Paul Malmsten',
    author_email='pmalmsten@gmail.com',
    packages=['xbee', 'xbee.tests'],
    scripts=[],
    url='http://code.google.com/p/python-xbee/',
    license='LICENSE.txt',
    description='Python tools for working with XBee radios',
    long_description=open('README.txt').read(),
    requires=['serial'],
    provides=['xbee','xbee.tests']
)
