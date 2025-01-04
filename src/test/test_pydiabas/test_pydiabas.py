import pytest

from pydiabas import PyDIABAS, StateError, ConfigError
from pydiabas.ediabas import EDIABAS


@pytest.mark.offline
class TestPyDIABAS():
    def test_init(self):
        p = PyDIABAS()
        assert isinstance(p._ediabas, EDIABAS)
        assert p._config == {}
    
    def test_start(self):
        p = PyDIABAS()
        assert p._ediabas.state() == 3
        p.start()
        assert p._ediabas.state() == 1
    
    def test_end(self):
        p = PyDIABAS()
        p.start()
        assert p._ediabas.state() == 1
        p.end()
        assert p._ediabas.state() == 3

    def test_reset(self):
        p = PyDIABAS()
        p.start()
        try:
            p.job("XX", "XX")
        except StateError:
            pass
        assert p._ediabas.state() == 3
        p.reset()
        assert p._ediabas.state() == 1

    def test_property_ready(self):
        p = PyDIABAS()
        assert p.ready == False
        p.start()
        assert p.ready

    def test_property_ediabas(self):
        p = PyDIABAS()
        assert p._ediabas == p.ediabas

    def test_config(self, pydiabas):
        # Confirm returning current config, beeing an empty dict initialle
        assert pydiabas.config() == {}

        # Confirm accepting and returning current config, all lower case letters
        assert pydiabas.config(traceSize=4096) == {"tracesize": 4096}

        # Confirm change in EDIABAS system
        assert pydiabas.ediabas.getConfig("traceSize") == "4096"

        # Confirm beeing case insensitive and adding new data to current config dict
        assert pydiabas.config(APITRACE=0) == {"tracesize": 4096, "apitrace": 0}

        # Confirm changing current config dict ISO adding if already in
        assert pydiabas.config(TRACEsize=1024) == {"tracesize": 1024, "apitrace": 0}

        # Confirm noch change if no parameter
        assert pydiabas.config() == {"tracesize": 1024, "apitrace": 0}

        # Confirm corret Path correction. Deleting last / or \\
        assert (
            pydiabas.config(tracePath="C:\\EDIABAS\\")
            == {"tracesize": 1024, "apitrace": 0, "tracepath": "C:\\EDIABAS"}
        )
        assert (
            pydiabas.config(SimulationPath="C:/EDIABAS/")
            == {"tracesize": 1024, "apitrace": 0, "tracepath": "C:\\EDIABAS", "simulationpath": "C:/EDIABAS"}
        )

    def test_config_invalid_keyword(self):
        p = PyDIABAS()
        p.start()
        with pytest.raises(KeyError):
            p.config(xx=2)

    def test_config_dict_after_invalid_keyword(self):
        p = PyDIABAS()
        p.start()
        try:
            p.config(traceSize=4096, xx=2, apitrace=0)
        except KeyError:
            pass
        assert p.config() == {}

    def test_config_unable_to_set(self):
        p = PyDIABAS()
        p.start()
        with pytest.raises(ConfigError):
            p.config(Interface="XX")

    def test_config_dict_after_failed_to_set(self):
        p = PyDIABAS()
        p.start()
        try:
            p.config(traceSize=4096, Interface="XX", apitrace=0)
        except ConfigError:
            pass
        assert p.config() == {"tracesize": 4096}

    def test_config_not_yet_started(self):
        p = PyDIABAS()
        p.config()
        with pytest.raises(KeyError):
            p.config(traceSize=4096)
    
    def test_job(self, pydiabas):
        r = pydiabas.job("TMODE", "LESE_INTERFACE_TYP")
        assert r["TYP"] == b"OBD"
    
    def test_job_bytes(self, pydiabas):
        r = pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP")
        assert r["TYP"] == b"OBD"
    
    def test_job_parameters_str(self, pydiabas):
        r = pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", parameters="TEST")
        assert r["TYP"] == b"OBD"
    
    def test_job_parameters_list_of_str(self, pydiabas):
        r = pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", parameters=["TEST", "TEST2"])
        assert r["TYP"] == b"OBD"
    
    def test_job_parameters_bytes(self, pydiabas):
        r = pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", parameters=b"TEST")
        assert r["TYP"] == b"OBD"
    
    def test_job_parameters_list_of_bytes(self, pydiabas):
        r = pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", parameters=[b"TEST", b"TEST2"])
        assert r["TYP"] == b"OBD"
    
    def test_job_parameters_list_of_mixed_start(self, pydiabas):
        with pytest.raises(TypeError):
            pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", parameters=[b"TEST", "TEST2", "TEST3"])
    
    def test_job_parameters_list_of_mixed_middle(self, pydiabas):
        with pytest.raises(TypeError):
            pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", parameters=[b"TEST", "TEST2", b"TEST3"])
    
    def test_job_parameters_list_of_mixed_end(self, pydiabas):
        with pytest.raises(TypeError):
            pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", parameters=["TEST", "TEST2", b"TEST3"])
    
    def test_job_parameters_invalid(self, pydiabas):
        with pytest.raises(TypeError):
            pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", parameters=3.2)

    def test_job_results_str(self, pydiabas):
        r = pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", result_filter="TEST")
        assert r["TYP"] == b"OBD"
    
    def test_job_results_list_of_str(self, pydiabas):
        r = pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", result_filter=["TEST", "TEST2"])
        assert r["TYP"] == b"OBD"
    
    def test_job_results_bytes(self, pydiabas):
        with pytest.raises(TypeError):
            pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", result_filter=b"TEST")
    
    def test_job_results_list_of_bytes(self, pydiabas):
        with pytest.raises(TypeError):
            pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", result_filter=[b"TEST", b"TEST2"])
    
    def test_job_results_list_of_mixed_start(self, pydiabas):
        with pytest.raises(TypeError):
            pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", result_filter=[b"TEST", "TEST2", "TEST3"])
    
    def test_job_results_list_of_mixed_middle(self, pydiabas):
        with pytest.raises(TypeError):
            pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", result_filter=[b"TEST", "TEST2", b"TEST3"])
    
    def test_job_results_list_of_mixed_end(self, pydiabas):
        with pytest.raises(TypeError):
            pydiabas.job(b"TMODE", b"LESE_INTERFACE_TYP", result_filter=["TEST", "TEST2", b"TEST3"])

    def test_job_no_fetchall(self, pydiabas):
        r = pydiabas.job("TMODE", "LESE_INTERFACE_TYP", fetchall=False)
        assert r.get("TYP") is None
        r.fetchall()
        assert r.get("TYP") == b"OBD"
    
    def test_job_fail(self, pydiabas):
        with pytest.raises(StateError):
            pydiabas.job("TMODE", "XX")
