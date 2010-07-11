"""
distutils_extensions.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

Provides distutils extension code for running tests
"""
from distutils.core import Command
from distutils.command.build_py import build_py as _build_py
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
                message = ["An automated test has failed! Please report this",
                           "failure to a project member. Use at your own risk!"]
                     
                if self.strict:
                    message.append("strict mode is on (see setup.cfg) - setup will now exit")
                           
                self.show_warning(message)
                
                if self.strict:
                    sys.exit(1)
        except ImportError:
            self.show_warning(
                    ["Automated tests have been skipped (install nose and run",
                     "'python setup.py test' to run the tests)"]
                )
    
    def show_warning(self, lines):
        print >> sys.stderr, "#######################################################"
        print >> sys.stderr, "# WARNING"
        
        for line in lines:
            print >> sys.stderr, "# ", line
            
        print >> sys.stderr, "#######################################################"
        
class build_py(_build_py):
    """
    Automatically runs tests during build
    """
    
    def run(self):
        self.run_command('test')
        _build_py.run(self)
