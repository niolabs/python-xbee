"""
distutils_extensions.py

By Paul Malmsten, 2010
Inspired by code written by Amit Synderman and Marco Sangalli
pmalmsten@gmail.com

Provides distutils extension code for running tests
"""
from distutils.core import Command
import sys

class TestCommand(Command):
    description = "Runs automated tests"
    user_options = [('strict','s',
                        "If a test fails, immediately quits with exit code 1")]
    
    def initialize_options(self):
        self.strict = False
                
    def finalize_options(self):
        pass
        
    def run(self):
        try:
            import nose
            
            if not nose.run(argv=['nosetests']):
                self.show_warning(
                    ["An automated test has failed! Please report this",
                     "failure to the project owner. Use at your own risk!"]
                )
                
                if self.strict:
                    sys.exit(1)
        except ImportError:
            self.show_warning(
                    ["Automated tests have been skipped (install nose and run",
                     "'python setup.py test' to manually run the tests)"]
                )
    
    def show_warning(self, lines):
        print "#######################################################"
        print "# WARNING"
        
        for line in lines:
            print "# ", line
            
        print "#######################################################"
