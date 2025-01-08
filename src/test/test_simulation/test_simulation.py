# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

import pytest
import pathlib

from pydiabas import Set, Row, StateError
from pydiabas.simulation import SimulatedPyDIABAS, CapturedJob


class Sim(SimulatedPyDIABAS):
    def __init__(self) -> None:
        super().__init__()

    def custom_job(
        self,
        ecu: str,
        job: str,
        parameters: str | bytes = "",
        result_filter: str | list[str] = "",
        fetchall: bool = True,
    ):
        return self.job_simulator(ecu, job, parameters, result_filter)

    def job_simulator(self, ecu, job, parameters, result_filter):
        ECU = "SIM"
        JOB = "TEST"
        PARAMETERS = [1, 2, 3]
        RESULT_FILTER = ["a", "b", "c"]

        if ecu != ECU:
            return None

        result = self.base_result(ecu=ECU, job=JOB)

        if job != JOB:
            result._jobSets[0]._rows.append(Row("JOBSTATUS", "UNKNOWN_JOB"))
            return result

        result._jobSets[0]._rows.append(Row("JOBSTATUS", "OKAY"))
        result._jobSets[0]._rows.append(Row("ECU", ECU))

        if parameters != PARAMETERS:
            result._jobSets[0]._rows.append(Row("ARGUMENTS", "INVALID"))

        if result_filter != RESULT_FILTER:
            result._jobSets[0]._rows.append(Row("RESULT_FILTER", "INVALID"))

        return result


@pytest.fixture(scope="class")
def captured_jobs(pydiabas_no_sim):
    return [
        CapturedJob(
            ecu="TMODE_SIM",
            job="LESE_INTERFACE_TYP",
            result=pydiabas_no_sim.job(ecu="TMODE", job="LESE_INTERFACE_TYP"),
        ),
        CapturedJob(
            ecu="TMODE_SIM",
            job="INFO",
            result=pydiabas_no_sim.job(ecu="TMODE", job="INFO"),
        ),
    ]


@pytest.mark.offline
class TestSimulation:
    def test_init(self):
        simulated_pydiabas = SimulatedPyDIABAS()
        assert simulated_pydiabas._captured_jobs == []

    def test_ready(self, captured_jobs):
        simulated_pydiabas = SimulatedPyDIABAS()
        assert not simulated_pydiabas.ready
        simulated_pydiabas.add_jobs(captured_jobs)
        assert simulated_pydiabas.ready

    def test_start(self, captured_jobs):
        simulated_pydiabas = SimulatedPyDIABAS()
        simulated_pydiabas.add_jobs(captured_jobs)
        assert simulated_pydiabas.ready
        simulated_pydiabas.start()
        assert not simulated_pydiabas.ready

    def test_config(self):
        simulated_pydiabas = SimulatedPyDIABAS()
        assert simulated_pydiabas.config(foo="bar") == {"simulated": True}

    def test_job_no_jobs(self):
        simulated_pydiabas = SimulatedPyDIABAS()
        with pytest.raises(StateError):
            assert simulated_pydiabas.job("TMODE_SIM", "INFO") is None

    def test_job_captured_job(self, captured_jobs):
        simulated_pydiabas = SimulatedPyDIABAS()
        simulated_pydiabas.add_jobs(captured_jobs[0])
        assert (
            simulated_pydiabas.job("TMODE_SIM", "LESE_INTERFACE_TYP")["TYP"] == b"OBD"
        )

    def test_job_captured_jobs(self, captured_jobs):
        simulated_pydiabas = SimulatedPyDIABAS()
        simulated_pydiabas.add_jobs(captured_jobs)
        assert simulated_pydiabas.job("TMODE_SIM", "INFO")["ECU"] == "TMODE"
        assert (
            simulated_pydiabas.job("TMODE_SIM", "INFO")._systemSet._rows[0].name
            == "__SIMULATED__"
        )
        assert (
            simulated_pydiabas.job("TMODE_SIM", "INFO")._systemSet._rows[0].value
            == "YES"
        )
        assert (
            simulated_pydiabas.job("TMODE_SIM", "LESE_INTERFACE_TYP")["TYP"] == b"OBD"
        )
        with pytest.raises(StateError):
            simulated_pydiabas.job("TMODE_SIM", "FAIL") is None

    def test_job_trigger_fetchall_warning(self, captured_jobs):
        simulated_pydiabas = SimulatedPyDIABAS()
        simulated_pydiabas.add_jobs(captured_jobs)
        with pytest.warns(UserWarning):
            simulated_pydiabas.job("TMODE_SIM", "INFO", fetchall=False)

    def test_job_custom_jobs(self):
        simulated_pydiabas = Sim()
        with pytest.raises(StateError):
            simulated_pydiabas.job("TMODE_SIM", "INFO") is None

        result = simulated_pydiabas.job("SIM", "FAIL")
        assert result["JOBSTATUS"] == "UNKNOWN_JOB"

        result = simulated_pydiabas.job("SIM", "TEST", ["foo"], "bar")
        assert result["ECU"] == "SIM"
        assert result["JOBSTATUS"] == "OKAY"
        assert result["ARGUMENTS"] == "INVALID"
        assert result["RESULT_FILTER"] == "INVALID"

        result = simulated_pydiabas.job("SIM", "TEST", [1, 2, 3], "bar")
        assert result["ECU"] == "SIM"
        assert result["JOBSTATUS"] == "OKAY"
        assert result.get("ARGUMENTS") is None
        assert result["RESULT_FILTER"] == "INVALID"

        result = simulated_pydiabas.job("SIM", "TEST", [1, 2, 3], ["a", "b", "c"])
        assert result["ECU"] == "SIM"
        assert result["JOBSTATUS"] == "OKAY"
        assert result.get("ARGUMENTS") is None
        assert result.get("RESULT_FILTER") is None

    def test_job_custom_and_captured_jobs(self, captured_jobs):
        simulated_pydiabas = Sim()
        simulated_pydiabas.add_jobs(captured_jobs)
        assert simulated_pydiabas.job("TMODE_SIM", "INFO")["ECU"] == "TMODE"
        assert simulated_pydiabas.job("SIM", "FAIL")["JOBSTATUS"] == "UNKNOWN_JOB"

    def test_custom_jobs(self):
        simulated_pydiabas = SimulatedPyDIABAS()
        assert simulated_pydiabas.custom_job(ecu="FOO", job="BAR") is None

    def test_base_result(self):
        simulated_pydiabas = SimulatedPyDIABAS()

        base_result = simulated_pydiabas.base_result(ecu="FOO", job="BAR")
        assert len(base_result) == 1
        assert base_result._systemSet["__SIMULATED__"] == "YES"
        assert base_result._systemSet["OBJECT"] == "foo"
        assert base_result._systemSet["SAETZE"] == 1
        assert base_result._systemSet["JOBNAME"] == "BAR"
        assert base_result._systemSet["VARIANTE"] == "FOO"
        assert base_result._systemSet["JOBSTATUS"] == ""
        assert base_result._systemSet["UBATTCURRENT"] == -1
        assert base_result._systemSet["UBATTHISTORY"] == -1
        assert base_result._systemSet["IGNITIONCURRENT"] == -1
        assert base_result._systemSet["IGNITIONHISTORY"] == -1
        assert isinstance(base_result._jobSets[0], Set)

        base_result = simulated_pydiabas.base_result(ecu="FOO", job="BAR", n_sets=10)
        assert len(base_result) == 10
        assert base_result._systemSet["__SIMULATED__"] == "YES"
        assert base_result._systemSet["OBJECT"] == "foo"
        assert base_result._systemSet["SAETZE"] == 10
        assert base_result._systemSet["JOBNAME"] == "BAR"
        assert base_result._systemSet["VARIANTE"] == "FOO"
        assert base_result._systemSet["JOBSTATUS"] == ""
        assert base_result._systemSet["UBATTCURRENT"] == -1
        assert base_result._systemSet["UBATTHISTORY"] == -1
        assert base_result._systemSet["IGNITIONCURRENT"] == -1
        assert base_result._systemSet["IGNITIONHISTORY"] == -1
        assert isinstance(base_result._jobSets[0], Set)
        assert isinstance(base_result._jobSets[-1], Set)

    def test_add_jobs_list(self, captured_jobs):
        simulated_pydiabas = SimulatedPyDIABAS()
        simulated_pydiabas.add_jobs(captured_jobs)
        assert simulated_pydiabas._captured_jobs == captured_jobs
        n_jobs = len(simulated_pydiabas._captured_jobs)
        simulated_pydiabas.add_jobs(captured_jobs)
        assert len(simulated_pydiabas._captured_jobs) == n_jobs * 2

    def test_add_jobs_tuple(self, captured_jobs):
        simulated_pydiabas = SimulatedPyDIABAS()
        simulated_pydiabas.add_jobs(tuple(captured_jobs))
        assert simulated_pydiabas._captured_jobs == captured_jobs

    def test_add_jobs_single_job(self, captured_jobs):
        simulated_pydiabas = SimulatedPyDIABAS()
        simulated_pydiabas.add_jobs(captured_jobs[0])
        assert simulated_pydiabas._captured_jobs == [captured_jobs[0]]

    def test_add_jobs_fail_single_type_error(self):
        simulated_pydiabas = SimulatedPyDIABAS()
        with pytest.raises(TypeError):
            simulated_pydiabas.add_jobs("foo")

    def test_add_jobs_fail_list_type_error(self, captured_jobs):
        simulated_pydiabas = SimulatedPyDIABAS()
        with pytest.raises(TypeError):
            simulated_pydiabas.add_jobs(captured_jobs + ["foo"])

    def test_load_jobs_file(self):
        simulated_pydiabas = SimulatedPyDIABAS()
        simulated_pydiabas.load_jobs(
            pathlib.Path(__file__)
            .parent.resolve()
            .joinpath("data_valid\\CAPTURE_VALID.jobs")
        )
        assert simulated_pydiabas._captured_jobs != []
        n_jobs = len(simulated_pydiabas._captured_jobs)
        simulated_pydiabas.load_jobs(
            pathlib.Path(__file__)
            .parent.resolve()
            .joinpath("data_valid\\CAPTURE_VALID.jobs")
        )
        assert len(simulated_pydiabas._captured_jobs) == n_jobs * 2

    def test_load_jobs_directory(self):
        simulated_pydiabas = SimulatedPyDIABAS()
        simulated_pydiabas.load_jobs(
            pathlib.Path(__file__).parent.resolve().joinpath("data_valid\\")
        )
        assert simulated_pydiabas._captured_jobs != []
        n_jobs = len(simulated_pydiabas._captured_jobs)
        simulated_pydiabas.load_jobs(
            pathlib.Path(__file__).parent.resolve().joinpath("data_valid\\")
        )
        assert len(simulated_pydiabas._captured_jobs) == n_jobs * 2

    def test_load_jobs_invalid_file(self):
        simulated_pydiabas = SimulatedPyDIABAS()
        with pytest.raises(TypeError):
            simulated_pydiabas.load_jobs(
                pathlib.Path(__file__)
                .parent.resolve()
                .joinpath("data_valid\\invalid_extension.test")
            )

    def test_load_jobs_invalid_data_in_file(self):
        simulated_pydiabas = SimulatedPyDIABAS()
        with pytest.raises(TypeError):
            simulated_pydiabas.load_jobs(
                pathlib.Path(__file__).parent.resolve().joinpath("data_invalid\\")
            )
