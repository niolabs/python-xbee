from distutils.core import setup

packages=[
    'xbee', 
    'xbee.tests', 
    'xbee.helpers', 
    'xbee.helpers.dispatch',
    'xbee.helpers.dispatch.tests',
]

setup(
    name='XBee',
    version='2.1.0',
    author='Paul Malmsten',
    author_email='pmalmsten@gmail.com',
    packages=packages,
    scripts=[],
    url='http://code.google.com/p/python-xbee/',
    license='LICENSE.txt',
    description='Python tools for working with XBee radios',
    long_description=open('README.txt').read(),
    requires=['serial'],
    provides=packages,
)
