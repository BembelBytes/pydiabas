import pytest

from pydiabas import PyDIABAS
from pydiabas.ediabas import EDIABAS

# Yield a running PyDIABAS instance scoped to the module to start it before the first and stop it after the last test
# of the class
@pytest.fixture(scope="session")
def pydiabas():
    pydiabas = PyDIABAS()
    pydiabas.start()
    yield pydiabas
    pydiabas.end()


# Reset PyDIABAS before each test function automatically
@pytest.fixture(scope="function", autouse=True)
def reset_pydiabas(pydiabas):
        pydiabas.reset()


# Yield a running EDIABAS instance scoped to the module to start it before the first and stop it after the last test
# of the class
@pytest.fixture(scope="session")
def ediabas():
    ediabas = EDIABAS()
    ediabas.init()
    yield ediabas
    ediabas.end()


# Reset EDIABAS before each test function automatically
@pytest.fixture(scope="function", autouse=True)
def reset_ediabas(ediabas):
        ediabas.end()
        ediabas.init()