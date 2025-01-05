# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

from __future__ import annotations

from . import ediabas
from .result import Result
from .exceptions import StateError, ConfigError


class PyDIABAS:
    """Class for simplified interaction with the EDIABAS API."""

    def __init__(self) -> None:
        self._ediabas = ediabas.EDIABAS()
        self._config: dict = {}

    def __enter__(self) -> PyDIABAS:
        # Initialize EDIABAS API session
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        # Terminate EDIABAS API session
        self.end()

    @property
    def ready(self) -> bool:
        return self._ediabas.state() == ediabas.API_STATE.READY

    @property
    def ediabas(self) -> ediabas.EDIABAS:
        return self._ediabas

    def start(self) -> None:
        """Initialize a new EDIABAS API session and set the configuration according the the current
        configuration settings.

        Raises:
            StateError
        """

        # Start EDIABAS API session and set config according to current configuration setting
        self._ediabas.initExt(
            configuration=";".join(
                f"{name}={value}" for name, value in self._config.items()
            )
        )

        # Check if EDIABAS API started successfully
        if self._ediabas.state() == ediabas.API_STATE.ERROR:
            raise StateError(self._ediabas.errorText())

    def end(self):
        """Ends EDIABAS API session and frees used memory."""

        self._ediabas.end()

    def reset(self):
        """Resets the EDIABAS API session be stopping and starting it again.
        Configuration will be set according to configuration settings after restart.
        """

        # Stop and restart EDIABAS API session
        self.end()
        self.start()

    def config(self, **kwargs) -> dict:
        """Sets the EDIABAS API configuration and returns the resulting configuration.
        If no parameters are given, no changes are made an the current configuration is returned.
        For each configuration setting a named parameter can be used like:
            config(apiTrace=2, traceSize=4096)
        Possible configurations and their value ranges can be found in the documentation of the
        pydiabas.ediabas.EDIABAS class.
        Paths can be entered using either '/' oder '\\'.
        Invalid configuration keys will raise a KeyError, invalid values or failing to set the value will raise
        a ConfigError.

        Optional Parameters:
        **kwargs: Configurations to be changed.

        Return values:
        return: Configurations after the changes (if any) have been made.
        """

        # Clean up path strings
        for keyword, value in list(kwargs.items()):
            if keyword.lower().endswith("path") or keyword.lower() == "tracewriter":
                kwargs[keyword] = value.strip("/").strip("\\")

        # Check if key is a valid config name
        for keyword in kwargs:
            try:
                self._ediabas.getConfig(keyword)
            except ediabas.JobFailedError:
                raise KeyError(
                    f"Invalid config parameter '{keyword}'. Did you call start() already?"
                )

        # Set new config in ediabas
        for keyword in kwargs:
            try:
                self._ediabas.setConfig(keyword, f"{kwargs[keyword]}")
                # Merge added config to current config
                self._config = self._config | {keyword.lower(): kwargs[keyword]}
            except ediabas.JobFailedError:
                raise ConfigError(
                    f"Unable to change config of '{keyword}' to '{kwargs[keyword]}'. Please check current config"
                )

        # Check if all values are correctly set
        for keyword in self._config:
            try:
                assert str(self._config[keyword]) == self._ediabas.getConfig(keyword)
            except (ediabas.JobFailedError, AssertionError):
                raise ConfigError(
                    f"Failed to set '{keyword}' correctly. Please check current config"
                )

        # Return current config from EDIABAS
        return self._config

    def job(
        self,
        ecu: str,
        job: str | bytes,
        parameters: str | bytes | list[str] | list[bytes] = "",
        result_filter: str | list[str] = "",
        fetchall: bool = True,
    ) -> Result:
        """Execute a job via the EDIABAS API and get back the result as a pydiabas.Result object.
        This function waits for the job to be finished and the result to be fetched completely if not deactivated.
        Job parameters can be handed either as str, list of str's, bytes or list of bytes but must be
        consistently used in a list like:
            "PARAM1" or b"PARAM1;PARAM2" or ["PARAM1"] or [b"PARAM2", b"PARAM2"] is OK
            ["PARAM1", b"PARAM2"] is NOT OK!
        Job result_filter can be passed as str or list of str's only, as there is no need for bytes support.
        The EDIABAS API uses semicolon as separators for multiple arguments on one str.

        Parameters:
        ecu: Name of the ECU the job has to be send to.
        job: Name of the job to be executed.

        Optional Parameters:
        parameters: Job parameters to be passed alongside with the job.
        result_filter: Results to be asked for. May not work with all ECUs.
        fetchall: If set to False it avoids fetching the complete result. Fetching must be done manually trough the
                  methods coming with the Result object.

        Return values:
        return: Result object with all values fetched (if not deactivated).

        Raises:
            StateError
            TypeError
        """

        # Separate multiple parameters using a semicolon
        if isinstance(parameters, list):

            # Verify all items in list are same type
            for parameter in parameters:
                if not isinstance(parameter, type(parameters[0])):
                    raise TypeError(
                        "All values in the list of parameters must be of the same type"
                    )

            # Check if list contains str or bytes
            if isinstance(parameters[0], str):
                parameters = ";".join(parameters)

            # Verify all items in list are same type
            elif isinstance(parameters[0], bytes):
                parameters = b";".join(parameters)

        elif not isinstance(parameters, (str, bytes)):
            raise TypeError("parameters expects str, bytes or list.")

        # Separate multiple results filters using a semicolon
        if isinstance(result_filter, list):

            # Verify all items in list are same type
            for result in result_filter:
                if not isinstance(result, str):
                    raise TypeError("All values in the list of results must be str")

            # Check if list contains str or bytes
            if isinstance(result_filter[0], str):
                result_filter = ";".join(result_filter)

        elif not isinstance(result_filter, str):
            raise TypeError("result_filter expects str, bytes or list.")

        # Execute job
        self._ediabas.job(ecu, job, parameters, result_filter)

        # Wait for job to finish
        while self._ediabas.state() == ediabas.API_STATE.BUSY:
            pass

        # Check for errors
        if self._ediabas.state() == ediabas.API_STATE.ERROR:
            raise StateError(self._ediabas.errorText())

        # Fetch result if requested
        if fetchall:
            return Result(self._ediabas).fetchall()

        return Result(self._ediabas)
