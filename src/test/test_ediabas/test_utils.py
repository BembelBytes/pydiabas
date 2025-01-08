# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

import pytest

from pydiabas.ediabas import utils


@pytest.mark.offline
class TestUtils:
    """Coverage note

    As there are only the following types available in TMODE ECU:
        BINARY, TEXT, WORD, INTEGER

    Only these values can be tested reliable in an offline state.
    The structure of the getResult function will be tested far enough
    """

    # Execute job to have the result available for each test
    @pytest.fixture(scope="function", autouse=True)
    def add_job_tmode_lese_interface_type(self, ediabas):
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")

    def test_getResult_Binary(self, ediabas):
        assert utils.getResult(ediabas, "TYP") == b"OBD"

    def test_getResult_Text(self, ediabas):
        assert utils.getResult(ediabas, "OBJECT", set=0) == "tmode"
        assert utils.getResult(ediabas, "JOBNAME", set=0) == "LESE_INTERFACE_TYP"
        assert utils.getResult(ediabas, "VARIANTE", set=0) == "TMODE"
        assert utils.getResult(ediabas, "JOBSTATUS", set=0) == ""

    def test_getResult_Word(self, ediabas):
        assert utils.getResult(ediabas, "SAETZE", set=0) == 1

    def test_getResult_Integer(self, ediabas):
        assert utils.getResult(ediabas, "UBATTCURRENT", set=0) == -1
        assert utils.getResult(ediabas, "UBATTHISTORY", set=0) == -1
        assert utils.getResult(ediabas, "IGNITIONCURRENT", set=0) == -1
        assert utils.getResult(ediabas, "IGNITIONHISTORY", set=0) == -1

    def test_job_failed(self, ediabas):
        assert utils.getResult(ediabas, "TEST") is None
