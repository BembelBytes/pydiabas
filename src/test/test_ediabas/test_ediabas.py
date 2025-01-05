import pytest
import ctypes

from pydiabas import Result
from pydiabas.ediabas import EDIABAS, API_STATE, VersionCheckError, JobFailedError
from pydiabas.ediabas.statics import API_RESULT_FORMAT


@pytest.mark.dev
@pytest.mark.offline
class TestEdiabas:
    def test___init__(self):
        e = EDIABAS()
        assert isinstance(e._handle, ctypes.c_uint)

    def test_init_end_state(self):
        e = EDIABAS()
        e.init()
        assert e._handle != ctypes.c_uint(0)
        assert e.state() == API_STATE.READY
        e.end()
        assert e.state() == API_STATE.ERROR

    def test_initExt(self):
        e = EDIABAS()
        e.initExt(ifh="STD:OBD")
        assert e._handle != ctypes.c_uint(0)
        assert e.state() == API_STATE.READY

    def test_initExt_with_config(self):
        e = EDIABAS()
        e.initExt(ifh="STD:OBD", configuration="apiTrace=4")
        assert e._handle != ctypes.c_uint(0)
        assert e.state() == API_STATE.READY
        assert e.getConfig("apiTrace") == "4"

    def test_initExt_fails(self):
        e = EDIABAS()
        with pytest.raises(JobFailedError):
            e.initExt(ifh="XXX")

    def test_breakJob(self, ediabas):
        ediabas.job("TMODE", "_JOBS")
        ediabas.breakJob()
        with pytest.raises(JobFailedError):
            Result(ediabas).fetchall()

    def test_trace(self, ediabas):
        # Just test if no exception occurs
        ediabas.trace("TRACE_INFO")

    def test_check_version(self):
        e = EDIABAS()
        e.checkVersion(b"7.0")
        version_str = e.checkVersion()
        version_list = [int(n) for n in version_str.split(".")]
        assert e.checkVersion(version_str)
        assert e.checkVersion(f"{version_list[0]}.{version_list[1]}.{version_list[2]}")
        assert e.checkVersion(
            f"{version_list[0]-1}.{version_list[1]}.{version_list[2]}"
        )

    def test_check_version_only_last_number_too_low(self):
        e = EDIABAS()
        version_str = e.checkVersion()
        version_list = [int(n) for n in version_str.split(".")]
        assert e.checkVersion(
            f"{version_list[0]}.{version_list[1]}.{version_list[2]+1}"
        )

    def test_check_version_number_too_low(self):
        e = EDIABAS()
        version_str = e.checkVersion()
        version_list = [int(n) for n in version_str.split(".")]
        with pytest.raises(VersionCheckError):
            e.checkVersion(f"{version_list[0]}.{version_list[1]+1}.{version_list[2]}")

    def test_check_version_wrong_argument_type(self):
        e = EDIABAS()
        with pytest.raises(TypeError):
            e.checkVersion(7)

    def test_check_version_invalid_version(self):
        e = EDIABAS()
        with pytest.raises(ValueError):
            e.checkVersion("seven.two")

    def test_getConfig(self):
        e = EDIABAS()
        e.init()
        assert e.getConfig("Interface") == "STD:OBD"
        assert e.getConfig("interface") == "STD:OBD"
        assert e.getConfig("INterFACE") == "STD:OBD"
        assert e.getConfig(b"Interface") == "STD:OBD"

    def test_getConfig_invalid_key(self):
        e = EDIABAS()
        e.init()
        with pytest.raises(JobFailedError):
            e.getConfig("XX")

    def test_setConfig(self):
        e = EDIABAS()
        e.init()
        traceSize = int(e.getConfig("traceSize"))
        e.setConfig("traceSize", str(traceSize // 2))
        assert e.getConfig("traceSize") == str(traceSize // 2)

    def test_setConfig_not_able_to_set(self):
        e = EDIABAS()
        e.init()
        with pytest.raises(JobFailedError):
            print(e.setConfig("Interface", "XXXX"))

    def test_errorCode_errorText(self):
        e = EDIABAS()
        e.init()
        assert e.errorCode() == 0
        assert e.errorText() == "NO_ERROR"
        try:
            e.resultByte("X")
        except JobFailedError:
            pass
        assert e.errorCode() == 134
        assert e.errorText() == "API-0014: RESULT NOT FOUND"

    def test_job(self, ediabas):
        ediabas.job("TMODE", "_JOBS")
        result = Result(ediabas).fetchsystemset()
        assert result.systemSet["JOBNAME"] == "_JOBS"

    def test_jobData(self, ediabas):
        ediabas.jobData("TMODE", "_JOBS")
        result = Result(ediabas).fetchsystemset()
        assert result.systemSet["JOBNAME"] == "_JOBS"

    def test_jobExt(self, ediabas):
        ediabas.jobExt("TMODE", "_JOBS")
        result = Result(ediabas).fetchsystemset()
        assert result.systemSet["JOBNAME"] == "_JOBS"

    def test_jobInfo(self, ediabas):
        ediabas.job("TMODE", "_JOBS")
        assert ediabas.jobInfo() == -1
        assert ediabas.jobInfo(text=True) == "-1 "

    def test_resultBinary(self, ediabas):
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")
        assert ediabas.resultBinary("TYP") == b"OBD"

    def test_resultBinary_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultBinary("TEST")

    def test_resultBinaryExt(self, ediabas):
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")
        assert ediabas.resultBinaryExt(name="TYP", set=1) == b"OBD"

    def test_resultBinaryExt_fails(self, ediabas):
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")
        with pytest.raises(JobFailedError):
            ediabas.resultBinaryExt(name="TYP", set=1, max_length=1)

    def test__process_text_argument(self):
        assert EDIABAS._process_text_argument(b"TEst") == b"TEst"
        assert EDIABAS._process_text_argument("TEst") == b"TEst"

    def test_resultByte_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultByte("TEST")

    def test_resultChar_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultChar("TEST")

    def test_resultDWord_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultDWord("TEST")

    def test_resultInt(self, ediabas):
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")
        assert ediabas.resultInt(name="UBATTCURRENT", set=0) == -1

    def test_resultInt_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultInt("TEST")

    def test_resultLong_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultLong("TEST")

    def test_resultReal_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultReal("TEST")

    def test_resultText(self, ediabas):
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")
        assert ediabas.resultText(name="OBJECT", set=0) == "tmode"
        ediabas.job("TMODE", "_RESULTS", "INFO")
        assert (
            ediabas.resultText(name="RESULTCOMMENT0", set=1)
            == b"Steuerger\xe4t im Klartext"
        )

    def test_resultText_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultText("TEST")

    def test_resultWord(self, ediabas):
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")
        assert ediabas.resultWord(name="SAETZE", set=0) == 1

    def test_resultWord_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultWord("TEST")

    def test_resultVar(self, ediabas):
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")
        assert ediabas.resultVar() == "TMODE"

    def test_resultVar_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultVar()

    def test_resultSets(self, ediabas):
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")
        assert ediabas.resultSets() == 1

    def test_resultSets_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultSets()

    def test_resultNumber(self, ediabas):
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")
        assert ediabas.resultNumber() == 1
        assert ediabas.resultNumber(set=1) == 1
        assert ediabas.resultNumber(set=0) == 9

    def test_resultNumber_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultNumber()

    def test_resultName(self, ediabas):
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")
        assert ediabas.resultName() == "TYP"
        assert ediabas.resultName(position=1) == "TYP"
        assert ediabas.resultName(set=1) == "TYP"
        assert ediabas.resultName(position=1, set=1) == "TYP"
        assert ediabas.resultName(position=1, set=0) == "OBJECT"
        assert ediabas.resultName(position=2, set=0) == "SAETZE"

    def test_resultName_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultName()

    def test_resultFormat(self, ediabas):
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")
        assert ediabas.resultFormat("TYP") == API_RESULT_FORMAT.BINARY
        assert ediabas.resultFormat("TYP", set=1) == API_RESULT_FORMAT.BINARY
        assert ediabas.resultFormat("SAETZE", set=0) == API_RESULT_FORMAT.WORD

    def test_resultFormat_fails(self, ediabas):
        with pytest.raises(JobFailedError):
            ediabas.resultFormat("TEST")

    def test_resultsNew(self, ediabas):
        address_result_empty = ediabas.resultsNew()
        address_result_empty_2 = ediabas.resultsNew()
        assert isinstance(address_result_empty, int)
        assert address_result_empty > 0
        assert address_result_empty != address_result_empty_2

    def test_resultsScope(self, ediabas):
        ediabas.job("TMODE", "_JOBS")
        address_result_jobs = ediabas.resultsNew()
        ediabas.job("TMODE", "LESE_INTERFACE_TYP")
        address_result_lese_interface_typ = ediabas.resultsNew()
        assert ediabas.resultName() == "TYP"
        ediabas.resultsScope(address_result_jobs)
        assert ediabas.resultName() == "JOBNAME"
        ediabas.resultsScope(address_result_lese_interface_typ)
        assert ediabas.resultName() == "TYP"

    def test_resultsDelete(self, ediabas):
        ediabas.job("TMODE", "_JOBS")
        address_result_jobs = ediabas.resultsNew()
        ediabas.resultsDelete(address_result_jobs)

    def test__process_text_argument_wrong_type(self):
        with pytest.raises(TypeError):
            EDIABAS._process_text_argument(2)

    def test__process_text_argument_unicode_error(self):
        with pytest.raises(ValueError):
            EDIABAS._process_text_argument("\udcc3")

    def test___eq__(self):
        e1 = EDIABAS()
        e2 = EDIABAS()
        e3 = EDIABAS()

        e1._handle = ctypes.c_uint(1)
        e2._handle = ctypes.c_uint(1)
        e3._handle = ctypes.c_uint(2)

        assert e1 == e2
        assert e1 != e3
        assert e2 != e3
