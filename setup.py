from distutils.core import setup

setup(
    name='XBee',
    version='0.1.0',
    author='Paul Malmsten',
    author_email='pmalmsten@gmail.com',
    packages=['xbee', 'xbee.test'],
    scripts=[],
    url='http://bombadier.homeftp.net/hg/python-xbee-clean',
    license='LICENSE.txt',
    description='XBee API communication library',
    long_description=open('README.txt').read(),
)
