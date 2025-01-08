# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

from typing import Callable

from ..pydiabas import PyDIABAS, Result
from .base import ECU


class BlockCreateError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class BlockReadError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ValueReadError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MSD80(ECU):
    """Represents the MSD80 ECU used in BMW E53 engines.
    Provides special functionality for easy and efficient reading of operational parameters from the MSD80.
    """

    # ECU name
    NAME: str = "MSD80"

    # Mapping for combustion modes
    COMBUSTION_MODE: dict = {1: "Stratified", 2: "Homogen", 3: "Lean"}

    def __init__(self) -> None:
        self._block: list = []
        self._last_read_function: Callable | None = None
        super().__init__(name=self.NAME)

    def set_block(self, pydiabas: PyDIABAS, values: list[str]) -> Result | None:
        """Set a new block of values to be read.
        After the block has been set, it can be read very quickly by using read_block() with the same values.
        Each call of set_block() or read() will overwrite the block.

        All (except the very last value in the list of values) must be values that do have "-" as value in
        column "NAME" in the "MESSWERTETAB" table in the ecu. Values wich have a value set in this column need an
        additional table lookup to translate the value coming from the ecu to a more user friendly representation. This
        lookup crashes the retrieval of any further values in the list.
        If a value with a value set in column "NAME" is used at the end of the list of values, all values will be
        retrieved successfully.

        Parameters:
        pydiabas: Instance of PyDIABAS
        values: List of values to be retrieved like ["0x5A30", "0x5A31"] (column ID in MESSWERTETAB)

        Return values:
        result: Result object if successful, else None.

        Raises:
            BlockCreationError
        """

        # Clear block as it will be overridden in the ecu
        self._block = []

        # Try to set block and get values
        result: Result = pydiabas.job(
            ecu=self.name, job="STATUS_MESSWERTBLOCK_LESEN", parameters=["3"] + values
        )

        # Save block, read_function and return values
        if result["JOB_STATUS"] == "OKAY":
            self._block = values
            self._last_read_function = lambda: self.set_block(pydiabas, values)
            return result

        # Raise an error if job failed
        if result["JOB_STATUS"] == "ERROR_TABLE":
            raise BlockCreateError(
                "Only values from MESSWERTETAB where NAME is '-' are supported, except as very last item in value list"
            )

        raise BlockCreateError(f"JOB_STATUS: {result.get('JOB_STATUS')}")

    def read_block(self, pydiabas) -> Result | None:
        """Read a previously set block of reading from the ecu.
        Block must be set by using set_block() to be read before being able to use this function.

        Parameters:
        pydiabas: Instance of PyDIABAS

        Return values:
        result: Result object if successful, else None.

        Raises:
            BlockReadError
        """

        # Check if a block is available
        if not self._block:
            raise BlockReadError("Set a block first using set_block()")

        # Try to get the values from ecu
        result: Result = pydiabas.job(
            ecu=self.name,
            job="STATUS_MESSWERTBLOCK_LESEN",
            parameters=["2"] + self._block,
        )

        # Save read_function and return values if successful
        if result["JOB_STATUS"] == "OKAY":
            self._last_read_function = lambda: self.read_block(pydiabas)
            return result

        # If values are requested, wich are not part of the previously set block
        if result["JOB_STATUS"] == "ERROR_ARGUMENT":
            raise BlockReadError("Block does not contain all requested values")

        # If additional table lookup by the ecu is required for a value being not the last one in the list of values.
        if result["JOB_STATUS"] == "ERROR_TABLE":
            raise BlockCreateError(
                "Values from MESSWERTETAB where NAME is '-' are only supported as very last item in value list"
            )

        # If no block has ever been created sind the last power up of the ecu
        if (
            result["JOB_STATUS"]
            == "ERROR_ECU_CONDITIONS_NOT_CORRECT_OR_REQUEST_SEQUENCE_ERROR"
        ):
            raise BlockReadError("No block available in ECU")

        raise BlockReadError(f"JOB_STATUS: {result.get('JOB_STATUS')}")

    def read(self, pydiabas: PyDIABAS, values: list[str]) -> Result | None:
        """Read values from the ECU an a way wich is slower that read_block but is able to read as many values with
        additional table lookup as needed.
        Values with additional table lookup can be identified by having anything OTHER than "-" set in the column "NAME"
        in the table "MESSWERTETAB".
        A previously created block will be overwritten.

        Parameters:
        pydiabas: Instance of PyDIABAS
        values: List of values to be retrieved like ["0x5A30", "0x5A31"] (column ID in MESSWERTETAB)

        Return values:
        result: Result object if successful, else None.

        Raises:
            ValueReadError
        """

        # Reset block as it will be overridden by the job in the ecu
        self._block = []

        # Try to get the requested values
        result: Result = pydiabas.job(
            ecu=self.name, job="MESSWERTBLOCK_LESEN", parameters=",".join(values)
        )

        # Set read_function and return values if successful
        if result["JOB_STATUS"] == "OKAY":
            self._last_read_function = lambda: self.read(pydiabas, values)
            return result

        raise ValueReadError(f"JOB_STATUS: {result.get('JOB_STATUS')}")

    def read_auto(self, pydiabas: PyDIABAS, values: list[str]) -> Result | None:
        """Automatically selects the fastest way to read all the values from the ecu.
        After successful reading the used function will be stored in last_read_function to know the next time
        wich function to use without having to try.

        Parameters:
        pydiabas: Instance of PyDIABAS
        values: List of values to be retrieved like ["0x5A30", "0x5A31"] (column ID in MESSWERTETAB)

        Return values:
        result: Result object if successful, else None.

        Raises:
            ValueReadError
        """

        # Check if given values match current block
        if values == self._block:

            # Read current block
            try:
                return self.read_block(pydiabas)
            except BlockReadError as e:
                pass

        # If reading the block failed or values do not match the current block, try to set a new block to be faster
        # the next time reading the values.
        try:
            return self.set_block(pydiabas, values)
        except BlockCreateError:

            # If creating the block failed, read block in a slow but robust way.
            # Any raised exception will be passed to the caller.
            return self.read(pydiabas, values)

    def read_again(self) -> Result | None:
        """Uses the read function that has been used successful the last time to read the values again."""

        if self._last_read_function is None:
            raise ValueReadError("No successful reading until now")

        return self._last_read_function()
