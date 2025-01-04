import pytest

from pydiabas import StateError
from pydiabas.ecu import ECU



@pytest.mark.offline
class TestECU():

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

    def test_get_jobs(self, pydiabas, tmode):
        jobs = tmode.get_jobs(pydiabas=pydiabas, details=False)
        assert isinstance(jobs, dict)
        assert len(jobs) >= 1
        assert isinstance(jobs[list(jobs.keys())[0]], dict)
        assert len(jobs[list(jobs.keys())[0]]) == 0

    def get_jobs_with_details(self, pydiabas, tmode):
        jobs = tmode.get_jobs(pydiabas=pydiabas, details=True)
        assert isinstance(jobs, dict)
        assert len(jobs) >= 1
        assert isinstance(jobs[list(jobs.keys())[0]], dict)
        assert len(jobs[list(jobs.keys())[0]]) >= 1
    
    def test_get_jobs_wrong_ecu_name(self, pydiabas, ecu):
        with pytest.raises(StateError):
            ecu.get_jobs(pydiabas=pydiabas, details=False)
     
    def test_get_job_details(self, pydiabas, tmode):
        details = tmode.get_job_details(pydiabas=pydiabas, job="SENDE_TELEGRAMM")
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
    
    def test_get_job_details_wrong_ecu_name(self, pydiabas, ecu):
        assert (
            ecu.get_job_details(pydiabas=pydiabas, job="INFO")
            == {'comments': [], 'arguments': [], 'results': []}
        )
        
    
    def test_get_job_details_wrong_job_name(self, pydiabas, tmode):
        assert (
            tmode.get_job_details(pydiabas=pydiabas, job="XX")
            == {'comments': [], 'arguments': [], 'results': []}
        )
    
    def test_get_tables(self, pydiabas, tmode):
        tables = tmode.get_tables(pydiabas=pydiabas, details=False)
        assert isinstance(tables, dict)
    
    def test_get_tables_wrong_ecu_name(self, pydiabas, ecu):
        with pytest.raises(StateError):
            ecu.get_tables(pydiabas=pydiabas, details=False)
    
    def test_get_table_details_wrong_table_name(self, pydiabas, tmode):
        assert (
            tmode.get_table_details(pydiabas=pydiabas, table="INFO")
            == {'body': [], 'header': []}
        )
    
    def test_get_table_details_wrong_ecu_and_table_name(self, pydiabas, ecu):
        with pytest.raises(StateError):
            ecu.get_table_details(pydiabas=pydiabas, table="INFO")
