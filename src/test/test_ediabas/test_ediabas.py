import pytest
import ctypes

from pydiabas.ediabas import EDIABAS, API_STATE, VersionCheckError, JobFailedError


@pytest.mark.offline
class TestEdiabas():
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

    def test_check_version(self):
        e = EDIABAS()
        e.checkVersion(b"7.0")
        version_str = e.checkVersion()
        version_list = [int(n) for n in version_str.split(".")]
        assert e.checkVersion(version_str)
        assert e.checkVersion(f"{version_list[0]}.{version_list[1]}.{version_list[2]}")
        assert e.checkVersion(f"{version_list[0]-1}.{version_list[1]}.{version_list[2]}")

    def test_check_version_only_last_number_too_low(self):
        e = EDIABAS()
        version_str = e.checkVersion()
        version_list = [int(n) for n in version_str.split(".")]
        assert e.checkVersion(f"{version_list[0]}.{version_list[1]}.{version_list[2]+1}")

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

    def test__process_text_argument(self):
        assert EDIABAS._process_text_argument(b"TEst") == b"TEst"
        assert EDIABAS._process_text_argument("TEst") == b"TEst"
    
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
