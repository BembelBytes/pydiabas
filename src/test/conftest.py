# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

import pytest
import os
import pathlib

from pydiabas import PyDIABAS
from pydiabas.ediabas import EDIABAS
from pydiabas.simulation import capture_job, save_jobs_to_file, SimulatedPyDIABAS


# EDIABAS API Trace file will be stored in the CWD
EDIABAS_API_TRACE_DIRECTORY = os.getcwd()

# Path to directory containing job capture files for simulation
SIMULATION_DATA_PATH = pathlib.Path(__file__).parent.resolve().joinpath("data\\")


# Parse command line arguments to set the configuration when running the tests
def pytest_addoption(parser):
    parser.addoption("--simulation", action="store", default="off")
    parser.addoption("--apitrace", action="store", default="0")
    parser.addoption("--capturejobs", action="store", default="off")


# Check if simulation has been set to "on" via command line argument
@pytest.fixture(scope="session")
def simulation(pytestconfig) -> bool:
    return pytestconfig.getoption("simulation") == "on"


# Check if logger debug has been set to "on" via command line argument
@pytest.fixture(scope="session")
def logger_debug(pytestconfig) -> bool:
    return pytestconfig.getoption("loggerdebug") == "on"


# Check if EDIABAS api trace level has been set to "on" via command line argument
@pytest.fixture(scope="session")
def api_trace(pytestconfig) -> int:
    match pytestconfig.getoption("apitrace"):
        case "on":
            return 1
        case "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8":
            return int(pytestconfig.getoption("apitrace"))
    return 0


# Check if job capturing has been set to "on" via command line argument
@pytest.fixture(scope="session")
def capture_jobs(pytestconfig) -> bool:
    return pytestconfig.getoption("capturejobs") == "on"


# This fixture creates an empty list at the beginning of the test session and yields it to enable the running tests
# to append job and result information to the list. After the last test, all the info is saved as pickle file.
# This is much faster than appending each job and result data to the file itself each time.
@pytest.fixture(scope="session")
def job_cache(capture_jobs):
    cache = []
    yield cache
    if capture_jobs:
        save_jobs_to_file(cache)


# Reset the given pydiabas instance and return it again
def reset_pydiabas(pydiabas: PyDIABAS | SimulatedPyDIABAS):
    pydiabas.reset()

    # Load jobs data into simulation
    if isinstance(pydiabas, SimulatedPyDIABAS):
        # Reset captured jobs
        pydiabas._captured_jobs = []
        pydiabas.load_jobs(SIMULATION_DATA_PATH)

    return pydiabas


# This fixture yields a ready to use pydiabas instance that is never simulated,
# even if '--simulation' command line argument is set to 'on'.
@pytest.fixture(scope="session")
def pydiabas_no_sim(api_trace, capture_jobs, job_cache):
    with PyDIABAS() as pydiabas_no_sim:

        if api_trace != 0:
            pydiabas_no_sim.config(
                apiTrace=api_trace, tracePath=EDIABAS_API_TRACE_DIRECTORY
            )

        if capture_jobs:
            pydiabas_no_sim.job = capture_job(pydiabas_no_sim.job, job_cache)

        yield reset_pydiabas(pydiabas_no_sim)


# This fixture yields a ready to use pydiabas instance that is always simulated,
# even if '--simulation' command line argument is set to 'off'.
@pytest.fixture(scope="session")
def pydiabas_sim(api_trace, capture_jobs, job_cache):
    with SimulatedPyDIABAS() as pydiabas_sim:

        if api_trace != 0:
            pydiabas_sim.config(
                apiTrace=api_trace, tracePath=EDIABAS_API_TRACE_DIRECTORY
            )

        if capture_jobs:
            pydiabas_sim.job = capture_job(pydiabas_sim.job, job_cache)

        yield reset_pydiabas(pydiabas_sim)


# This fixture yields a ready to use pydiabas instance that is simulated or not ,
# according to '--simulation' command line argument.
@pytest.fixture(scope="session")
def pydiabas_auto(api_trace, simulation, capture_jobs, job_cache):
    # Select the PyDIABAS class to be used
    pydiabas_class_to_use = SimulatedPyDIABAS if simulation else PyDIABAS

    with pydiabas_class_to_use() as pydiabas:

        if api_trace != 0:
            pydiabas.config(apiTrace=api_trace, tracePath=EDIABAS_API_TRACE_DIRECTORY)

        if capture_jobs:
            pydiabas.job = capture_job(pydiabas.job, job_cache)

        yield reset_pydiabas(pydiabas)


# Yield a running EDIABAS instance scoped to the module to start it before the first and stop it after the last test
# of the class
@pytest.fixture(scope="session")
def ediabas():
    ediabas = EDIABAS()
    ediabas.init()
    yield ediabas
    ediabas.end()


# Automatically reset ediabas before each test
@pytest.fixture(scope="function", autouse=True)
def reset_ediabas(ediabas):
    ediabas.end()
    ediabas.init()
