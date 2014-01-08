from version import version
from distutils.core import setup as setup
__doc__="""setup.py

Setup module for installing fstr to the default third party location.

Call from command line as: python setup.py install
"""
def setupPackage(install=False):
    """setupPackage()

    Function to call distutils setup to install the package to the default location for third party modules.
    """
    setup(name='fstr',
    version=version,
    description='Python Format String for reading and printing using standard python string.format syntax',
    author='David Pugh',
    author_email='djpugh@gmail.com',
    package_dir={'fstring':'.'},
    packages=['fstring'])
if __name__=="__main__":
    setupPackage()