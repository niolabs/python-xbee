from distutils.core import setup

packages=[
    'xbee',
    'xbee.tests',
    'xbee.helpers',
    'xbee.helpers.dispatch',
    'xbee.helpers.dispatch.tests',
]

try:
    from pypandoc import convert
    def read_md(f):
        try:
            return convert(f, 'rst')
        except Exception as e:
            print("warning: pypandoc module not found,"
                  " not converting Markdown to RST")
            print(e)
except ImportError:
    print("warning: pypandoc module not found, not converting Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    name='XBee',
    version='2.2.2',
    author='Paul Malmsten',
    author_email='pmalmsten@gmail.com',
    packages=packages,
    scripts=[],
    url='https://github.com/nioinnovation/python-xbee',
    license='LICENSE.txt',
    description='Python tools for working with XBee radios',
    long_description=read_md('README.md'),
    requires=['serial'],
    provides=packages,
)
