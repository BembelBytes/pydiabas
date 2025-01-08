# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

import pytest

from pydiabas import Result, StateError
from pydiabas.ecu import MSD80
from pydiabas.ecu.msd80 import BlockCreateError, BlockReadError, ValueReadError


@pytest.mark.msd80
class TestMSD80:
    READINGS_NO_LOOKUP_A = ["0x5A30", "0x5A31", "0x5A32", "0x5A33", "0x5A34", "0x5A35"]
    READINGS_NO_LOOKUP_B = ["0x5B00", "0x5B01", "0x5B02", "0x5B03", "0x5B04", "0x5B05"]
    READINGS_SINGLE_LOOKUP_A = ["0x5AB1", "0x58E4"]
    READINGS_SINGLE_LOOKUP_B = ["0x5A2F", "0x58E4"]
    READINGS_MULTIPLE_LOOKUPS_A = ["0x5AB1", "0x58E4", "0x4307"]
    READINGS_MULTIPLE_LOOKUPS_B = ["0x5A2F", "0x58E4", "0x4307"]
    READINGS_PARTLY_INVALID = ["0x5A2F", "0x58E4", "0xFFFF"]

    # Provide a fresh mas80 for each test function
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

    def test_init(self, msd80):
        assert msd80.name == "MSD80"
        assert msd80._block == []
        assert msd80._last_read_function is None

    def test_set_block_no_lookup(self, pydiabas_auto, msd80):
        result = msd80.set_block(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_A)
        assert isinstance(result, Result)
        assert msd80._block == TestMSD80.READINGS_NO_LOOKUP_A
        assert callable(msd80._last_read_function)
        last_read_function_1 = msd80._last_read_function
        result = msd80.set_block(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_B)
        assert isinstance(result, Result)
        assert msd80._block == TestMSD80.READINGS_NO_LOOKUP_B
        assert callable(msd80._last_read_function)
        assert last_read_function_1 is not msd80._last_read_function

    def test_set_block_single_lookup(self, pydiabas_auto, msd80):
        result = msd80.set_block(pydiabas_auto, TestMSD80.READINGS_SINGLE_LOOKUP_A)
        assert isinstance(result, Result)
        assert msd80._block == TestMSD80.READINGS_SINGLE_LOOKUP_A
        assert callable(msd80._last_read_function)
        last_read_function_1 = msd80._last_read_function
        result = msd80.set_block(pydiabas_auto, TestMSD80.READINGS_SINGLE_LOOKUP_B)
        assert isinstance(result, Result)
        assert msd80._block == TestMSD80.READINGS_SINGLE_LOOKUP_B
        assert callable(msd80._last_read_function)
        assert msd80._last_read_function is not last_read_function_1

    def test_set_block_multiple_lookups_raises_exception(self, pydiabas_auto, msd80):
        with pytest.raises(BlockCreateError):
            msd80.set_block(pydiabas_auto, TestMSD80.READINGS_MULTIPLE_LOOKUPS_A)

    def test_set_block_multiple_lookups_clears_block(self, pydiabas_auto, msd80):
        msd80.set_block(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_A)
        assert msd80._block == TestMSD80.READINGS_NO_LOOKUP_A
        assert callable(msd80._last_read_function)

        try:
            msd80.set_block(pydiabas_auto, TestMSD80.READINGS_MULTIPLE_LOOKUPS_A)
        except BlockCreateError:
            pass

        assert msd80._block == []
        assert callable(msd80._last_read_function)

    def test_set_block_invalid_value_raises_exception(self, pydiabas_auto, msd80):
        with pytest.raises(BlockCreateError):
            msd80.set_block(pydiabas_auto, TestMSD80.READINGS_PARTLY_INVALID)

    def test_set_block_invalid_value_clears_block(self, pydiabas_auto, msd80):
        msd80.set_block(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_A)
        assert msd80._block == TestMSD80.READINGS_NO_LOOKUP_A
        assert callable(msd80._last_read_function)

        try:
            msd80.set_block(pydiabas_auto, TestMSD80.READINGS_PARTLY_INVALID)
        except BlockCreateError:
            pass

        assert msd80._block == []
        assert callable(msd80._last_read_function)

    def test_read_block(self, pydiabas_auto, msd80):
        msd80.set_block(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_A)
        last_read_function_1 = msd80._last_read_function
        result = msd80.read_block(pydiabas_auto)
        assert isinstance(result, Result)
        assert msd80._last_read_function is not last_read_function_1

    def test_read_block_fails_no_block_set(self, pydiabas_auto, msd80):
        with pytest.raises(BlockReadError):
            msd80.read_block(pydiabas_auto)

    def test_read_block_fails_wrong_arguments(self, pydiabas_auto, msd80):
        msd80.set_block(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_A)
        msd80._block = msd80._block[:-2]
        with pytest.raises(BlockReadError):
            msd80.read_block(pydiabas_auto)

    def test_read_test_with_multiple_lookups(self, pydiabas_auto, msd80):
        try:
            msd80.set_block(pydiabas_auto, TestMSD80.READINGS_MULTIPLE_LOOKUPS_A)
        except BlockCreateError:
            pass

        msd80._block = TestMSD80.READINGS_MULTIPLE_LOOKUPS_A
        with pytest.raises(BlockCreateError):
            msd80.read_block(pydiabas_auto)

    def test_read_no_lookup(self, pydiabas_auto, msd80):
        result = msd80.read(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_A)
        assert isinstance(result, Result)
        assert msd80._block == []
        assert callable(msd80._last_read_function)
        last_read_function_1 = msd80._last_read_function
        result = msd80.read(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_B)
        assert isinstance(result, Result)
        assert msd80._block == []
        assert callable(msd80._last_read_function)
        assert last_read_function_1 is not msd80._last_read_function

    def test_read_single_lookup(self, pydiabas_auto, msd80):
        result = msd80.read(pydiabas_auto, TestMSD80.READINGS_SINGLE_LOOKUP_A)
        assert isinstance(result, Result)
        assert msd80._block == []
        assert callable(msd80._last_read_function)
        last_read_function_1 = msd80._last_read_function
        result = msd80.read(pydiabas_auto, TestMSD80.READINGS_SINGLE_LOOKUP_B)
        assert isinstance(result, Result)
        assert msd80._block == []
        assert callable(msd80._last_read_function)
        assert last_read_function_1 is not msd80._last_read_function

    def test_read_multiple_lookups(self, pydiabas_auto, msd80):
        result = msd80.read(pydiabas_auto, TestMSD80.READINGS_MULTIPLE_LOOKUPS_A)
        assert isinstance(result, Result)
        assert msd80._block == []
        assert callable(msd80._last_read_function)
        last_read_function_1 = msd80._last_read_function
        result = msd80.read(pydiabas_auto, TestMSD80.READINGS_MULTIPLE_LOOKUPS_B)
        assert isinstance(result, Result)
        assert msd80._block == []
        assert callable(msd80._last_read_function)
        assert last_read_function_1 is not msd80._last_read_function

    def test_read_invalid_value(self, pydiabas_auto, msd80):
        with pytest.raises(ValueReadError):
            msd80.read(pydiabas_auto, TestMSD80.READINGS_PARTLY_INVALID)

    def test_read_auto_no_lookup(self, pydiabas_auto, msd80):
        result = msd80.read_auto(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_A)
        assert isinstance(result, Result)
        assert msd80._block == TestMSD80.READINGS_NO_LOOKUP_A
        assert callable(msd80._last_read_function)
        last_read_function_1 = msd80._last_read_function
        result = msd80.read_auto(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_B)
        assert isinstance(result, Result)
        assert msd80._block == TestMSD80.READINGS_NO_LOOKUP_B
        assert callable(msd80._last_read_function)
        assert last_read_function_1 is not msd80._last_read_function

    def test_read_auto_single_lookup(self, pydiabas_auto, msd80):
        result = msd80.read_auto(pydiabas_auto, TestMSD80.READINGS_SINGLE_LOOKUP_A)
        assert isinstance(result, Result)
        assert msd80._block == TestMSD80.READINGS_SINGLE_LOOKUP_A
        assert callable(msd80._last_read_function)
        last_read_function_1 = msd80._last_read_function
        result = msd80.read_auto(pydiabas_auto, TestMSD80.READINGS_SINGLE_LOOKUP_B)
        assert isinstance(result, Result)
        assert msd80._block == TestMSD80.READINGS_SINGLE_LOOKUP_B
        assert callable(msd80._last_read_function)
        assert last_read_function_1 is not msd80._last_read_function

    def test_read_auto_multiple_lookups(self, pydiabas_auto, msd80):
        result = msd80.read_auto(pydiabas_auto, TestMSD80.READINGS_MULTIPLE_LOOKUPS_A)
        assert isinstance(result, Result)
        assert msd80._block == []
        assert callable(msd80._last_read_function)
        last_read_function_1 = msd80._last_read_function
        result = msd80.read_auto(pydiabas_auto, TestMSD80.READINGS_MULTIPLE_LOOKUPS_B)
        assert isinstance(result, Result)
        assert msd80._block == []
        assert callable(msd80._last_read_function)
        assert last_read_function_1 is not msd80._last_read_function

    def test_read_auto_invalid_value(self, pydiabas_auto, msd80):
        with pytest.raises(ValueReadError):
            msd80.read_auto(pydiabas_auto, TestMSD80.READINGS_PARTLY_INVALID)

    def test_read_auto_multiple_times(self, pydiabas_auto, msd80):
        # Test for coverage, used read_block the second time
        msd80.read_auto(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_A)
        msd80.read_auto(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_A)

    def test_read_again(self, pydiabas_auto, msd80):
        msd80.read_auto(pydiabas_auto, TestMSD80.READINGS_NO_LOOKUP_A)
        result = msd80.read_again()
        assert isinstance(result, Result)

    def test_read_again_fails(self, msd80):
        with pytest.raises(ValueReadError):
            msd80.read_again()
