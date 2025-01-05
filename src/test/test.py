import pytest


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
    > python -Wa -m pytest test                   => All tests
    > python -Wa -m pytest test -m offline        => Only test that need no car connected
    > python -Wa -m pytest test -m msd80          => Only MSD80 tests
"""


@pytest.mark.offline
class TestPythonVersion:
    def test_python_version(self):
        assert len(hex(id(None))) == 10
