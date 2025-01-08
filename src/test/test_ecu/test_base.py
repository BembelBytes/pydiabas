# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

import pytest

from pydiabas import StateError, Result
from pydiabas.ecu import ECU, MSD80


@pytest.mark.offline
class TestECU:

    # Provide a fresh ecu for each test function
    @pytest.fixture(scope="function")
    def ecu(self):
        return ECU()

    # Provide a fresh tmode for each test function
    @pytest.fixture(scope="function")
    def tmode(self):
        return ECU(name="TMODE")

    def test_init(self, ecu, tmode):
        assert ecu.name == ""
        assert tmode.name == "TMODE"

    def test_job(self, pydiabas_no_sim, tmode):
        result = tmode.job(pydiabas_no_sim, "LESE_INTERFACE_TYP")
        assert isinstance(result, Result)
        assert result["TYP"] == b"OBD"

    def test_get_jobs(self, pydiabas_no_sim, tmode):
        jobs = tmode.get_jobs(pydiabas=pydiabas_no_sim, details=False)
        assert isinstance(jobs, dict)
        assert len(jobs) >= 1
        assert isinstance(jobs[list(jobs.keys())[0]], dict)
        assert len(jobs[list(jobs.keys())[0]]) == 0

    def test_get_jobs_with_details(self, pydiabas_no_sim, tmode):
        jobs = tmode.get_jobs(pydiabas=pydiabas_no_sim, details=True)
        assert isinstance(jobs, dict)
        assert len(jobs) >= 1
        assert isinstance(jobs[list(jobs.keys())[0]], dict)
        assert len(jobs[list(jobs.keys())[0]]) >= 1

    def test_get_jobs_verbose(self, pydiabas_no_sim, tmode):
        jobs = tmode.get_jobs(pydiabas=pydiabas_no_sim, details=False, verbose=True)
        assert isinstance(jobs, dict)
        assert len(jobs) >= 1
        assert isinstance(jobs[list(jobs.keys())[0]], dict)
        assert len(jobs[list(jobs.keys())[0]]) == 0

    def test_get_jobs_with_details_verbose(self, pydiabas_no_sim, tmode):
        jobs = tmode.get_jobs(pydiabas=pydiabas_no_sim, details=True, verbose=True)
        assert isinstance(jobs, dict)
        assert len(jobs) >= 1
        assert isinstance(jobs[list(jobs.keys())[0]], dict)
        assert len(jobs[list(jobs.keys())[0]]) >= 1

    def test_get_jobs_wrong_ecu_name(self, pydiabas_no_sim, ecu):
        with pytest.raises(StateError):
            ecu.get_jobs(pydiabas=pydiabas_no_sim, details=False)

    def test_get_job_details(self, pydiabas_no_sim, tmode):
        details = tmode.get_job_details(pydiabas=pydiabas_no_sim, job="SENDE_TELEGRAMM")
        assert len(details) == 3
        assert "comments" in details
        assert "arguments" in details
        assert "results" in details

        assert isinstance(details["comments"], list)
        assert len(details["comments"]) >= 1
        assert isinstance(details["arguments"], list)
        assert len(details["arguments"]) >= 1
        assert isinstance(details["results"], list)
        assert len(details["results"]) >= 1

        assert "name" in details["arguments"][0]
        assert "type" in details["arguments"][0]
        assert "comments" in details["arguments"][0]
        assert "name" in details["results"][0]
        assert "type" in details["results"][0]
        assert "comments" in details["results"][0]

    def test_get_job_details_wrong_ecu_name(self, pydiabas_no_sim, ecu):
        assert ecu.get_job_details(pydiabas=pydiabas_no_sim, job="INFO") == {
            "comments": [],
            "arguments": [],
            "results": [],
        }

    def test_get_job_details_wrong_job_name(self, pydiabas_no_sim, tmode):
        assert tmode.get_job_details(pydiabas=pydiabas_no_sim, job="XX") == {
            "comments": [],
            "arguments": [],
            "results": [],
        }

    def test_get_tables(self, pydiabas_no_sim, tmode):
        tables = tmode.get_tables(pydiabas=pydiabas_no_sim, details=False)
        assert isinstance(tables, dict)

    def test_get_tables_verbose(self, pydiabas_no_sim, tmode):
        tables = tmode.get_tables(pydiabas=pydiabas_no_sim, details=False, verbose=True)
        assert isinstance(tables, dict)

    def test_get_tables_wrong_ecu_name(self, pydiabas_no_sim, ecu):
        with pytest.raises(StateError):
            ecu.get_tables(pydiabas=pydiabas_no_sim, details=False)

    def test_get_table_details_wrong_table_name(self, pydiabas_no_sim, tmode):
        assert tmode.get_table_details(pydiabas=pydiabas_no_sim, table="INFO") == {
            "body": [],
            "header": [],
        }

    def test_get_table_details_wrong_ecu_and_table_name(self, pydiabas_no_sim, ecu):
        assert ecu.get_table_details(pydiabas=pydiabas_no_sim, table="INFO") == {
            "body": [],
            "header": [],
        }


@pytest.mark.msd80
class TestBaseWithMSD80:

    # Provide a fresh msd80 for each test function
    @pytest.fixture(scope="function")
    def msd80(self):
        return MSD80()

    # If the MSD80 ECU is sleeping, the first job call may return an IFH-0018: INITIALIZATION ERROR
    # Calling a simple job before running the tests will avoid the first test to fail due to a sleeping ECU
    @pytest.fixture(scope="class", autouse=True)
    def avoid_initialization_error(self, pydiabas_auto):
        try:
            pydiabas_auto.job("MSD80", "INFO")
        except StateError:
            pass

    def test_get_tables_with_details(self, pydiabas_auto, msd80):
        tables = msd80.get_tables(pydiabas=pydiabas_auto, details=True)
        assert isinstance(tables, dict)
        assert tables["KONZEPT_TABELLE"]["header"] == ["NR", "KONZEPT_TEXT"]
        assert ["0x10", "D-CAN"] in tables["KONZEPT_TABELLE"]["body"]
        assert ["0x0F", "BMW-FAST"] in tables["KONZEPT_TABELLE"]["body"]

    def test_get_tables_with_details_verbose(self, pydiabas_auto, msd80):
        tables = msd80.get_tables(pydiabas=pydiabas_auto, details=True, verbose=True)
        assert isinstance(tables, dict)
        assert tables["KONZEPT_TABELLE"]["header"] == ["NR", "KONZEPT_TEXT"]
        assert ["0x10", "D-CAN"] in tables["KONZEPT_TABELLE"]["body"]
        assert ["0x0F", "BMW-FAST"] in tables["KONZEPT_TABELLE"]["body"]

    def test_get_table_details(self, pydiabas_auto, msd80):
        table = msd80.get_table_details(pydiabas=pydiabas_auto, table="KONZEPT_TABELLE")
        assert isinstance(table, dict)
        assert table["header"] == ["NR", "KONZEPT_TEXT"]
        assert ["0x10", "D-CAN"] in table["body"]
        assert ["0x0F", "BMW-FAST"] in table["body"]
