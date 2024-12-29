import sys
import unittest

from .test_pydiabas import *
from .test_ediabas import *
from .test_ecu import *


"""Using these tests:

All of the test concerning pydiabas, ediabas and the test_base test in test_ecu can be run
without being connected to a car or even having an USB CAN cable connected.
Only these tests will be executed when running the test module.
There are further test concerning specific ECUs. These test need a active connection to a ECU of this kind.
To run test for the MSD80 class, you need to be connected to a car using an MSD80 ECU.
These test need to be run manually!

Make sure to use a 32bit python version when running these test!

COMMANDS
To run all the test which do NOT need a connection to a car please use:
    > python -m unittest test

To run a specific test for an ECU (in this case the MSD80) use:
    > python -m unittest test.test_ecu.test_msd80
"""


class PythonVersionTest(unittest.TestCase):
    def test_python_version(self):
        self.assertEqual(len(hex(id(None))), 10, f"\n    Please use a 32bit python version\n    Used python version: {sys.version}\n    Used python executable: {sys.executable}")
