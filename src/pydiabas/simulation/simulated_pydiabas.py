# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

import os
import pathlib
import pickle
from warnings import warn

from ..pydiabas import PyDIABAS, StateError
from ..result import Result, Set, Row

from .capturing import CapturedJob


class SimulatedPyDIABAS(PyDIABAS):
    """Simulated PyDIABAS

    This PyDIABAS class simulates job execution instead of executing jobs via EDIABAS on real ECU's to be able
    to run tests without being connected to the required ECU.

    Simulated job results can be provided either by capturing real job data, or by implementing the custom_job function
    that create the result object to be returned by the simulation.
    """

    def __init__(self) -> None:
        # Initialize the parent PyDIABAS class
        super().__init__()

        # Create an empty list to hold all captured jobs
        self._captured_jobs: list[CapturedJob] = []

    @PyDIABAS.ready.getter
    def ready(self) -> bool:
        # Returns true if captured jobs are available
        return bool(self._captured_jobs)

    def start(self) -> None:
        """Clears captured jobs list"""
        self._captured_jobs = []

    def end(self) -> None:
        """No implementation necessary in simulation"""
        pass

    def config(self, **kwargs) -> dict:
        """Configuration od ediabas is NOT done in simulation

        A dummy dict is returned to indicate the simulation

        Return values:
        return: Dummy config dict {"simulated": True}.
        """
        return {"simulated": True}

    def job(
        self,
        ecu: str,
        job: str | bytes,
        parameters: str | bytes | list[str] | list[bytes] = "",
        result_filter: str | list[str] = "",
        fetchall: bool = True,
    ) -> Result:
        """Try to simulate the called job

        Searches trough captured jobs and custom_job method that simulate job results.
        The returned Result will always hold all data, even if fetchall is set to False.

        Parameters:
        ecu: Name of the ECU the job has to be simulated for.
        job: Name of the job to be simulated.

        Optional Parameters:
        parameters: Job parameters to be passed alongside with the job.
        result_filter: Results to be asked for.
        fetchall: This argument is ignored when simulating the job, a warning is generated if fetchall is set to False to inform the user.

        Return values:
        return: Simulated Result object with all values fetched.

        Raises:
            StateError
        """

        # Warn user about ignored argument
        if not fetchall:
            warn("fetchall argument will be ignored when simulating jobs!")

        # Search for data fitting the called job in all files containing captured jobs
        for captured_job in self._captured_jobs:
            if captured_job.check(ecu, job, parameters, result_filter):
                result = captured_job.result
                result._systemSet._rows.insert(0, Row("__SIMULATED__", "YES"))
                return result

        # Check if custom_job returns a simulated Result
        if result := self.custom_job(
            ecu=ecu,
            job=job,
            parameters=parameters,
            result_filter=result_filter,
            fetchall=fetchall,
        ):
            return result

        # Raise a StateError if job could not been simulated
        raise StateError("Unable to simulate the job")

    def custom_job(
        self,
        ecu: str,
        job: str | bytes,
        parameters: str | bytes | list[str] | list[bytes] = "",
        result_filter: str | list[str] = "",
        fetchall: bool = True,
    ):
        """Custom job simulation

        Can be implemented to simulate jobs without using captured job data.

        This method signature uses the same parameters as the job function itself, as this function is called using
        keyword parameters only, the following signature is sufficient:
        - custom_job(**kwargs) -
        Its not necessary to call this function by using super().custom_job() as this method does nothing but returning
        None

        The Implemented function must return a Result object or None if not able to simulate the job.
        """

        # Return None if job cannot be simulated
        return None

    def base_result(self, ecu: str, job: str, n_sets: int = 1) -> Result:
        """Result containing a standart systemSet.

        A row (__SIMULATED__: YES) will be added as first row to the systemSet to indicate a simulated result.

        Parameters:
        ecu: Name of ECU to be stated in the Result.
        job: Name of the job to be stated in the Result.
        n_sets: Number of Sets in jobSets of the Result to set the correct value for 'SAETZE' in the systemSet.
        """

        # Create a Result object
        result = Result(self.ediabas)

        # Fill systemSet with standard values
        result._systemSet = Set(
            [
                Row("__SIMULATED__", "YES"),
                Row("OBJECT", ecu.lower()),
                Row("SAETZE", n_sets),
                Row("JOBNAME", job),
                Row("VARIANTE", ecu),
                Row("JOBSTATUS", ""),
                Row("UBATTCURRENT", -1),
                Row("UBATTHISTORY", -1),
                Row("IGNITIONCURRENT", -1),
                Row("IGNITIONHISTORY", -1),
            ]
        )

        # Add the requested number of jobSets
        result._jobSets = [Set() for _ in range(n_sets)]

        return result

    def add_jobs(
        self, jobs: CapturedJob | list[CapturedJob] | tuple[CapturedJob]
    ) -> None:
        """Appends the given job(s) to the simulation

        Jobs can be passed as single CapturedJob object or as a list or tuple containing only CapturedJobs objects.

        Parameters:
        jobs: Job(s) to be added.

        Raises:
            TypeError
        """

        # Validate types
        if isinstance(jobs, CapturedJob):
            self._captured_jobs.append(jobs)
        elif isinstance(jobs, (list, tuple)):
            for job in jobs:
                if not isinstance(job, CapturedJob):
                    raise TypeError(
                        "all items in captured_jobs must be 'CapturedJob' objects"
                    )
                # Add jobs
                self._captured_jobs.append(job)
        else:
            raise TypeError("captured_jobs must be a 'CapturedJob' object")

    def load_jobs(self, path: str | os.PathLike = "") -> None:
        """Load data from all *jobs files in the given directory

        Parameters:
        path: Path to the directory containing the *jobs files or to a single *.jobs file.

        Raises:
            TypeError
        """

        def add_jobs_from_file(file_path):
            """Adds jobs contained in the given file

            Parameters:
            file_path: Path to the file containing the jobs.

            Raises:
                TypeError
            """
            try:
                with open(path.joinpath(file_path), "rb") as file:
                    jobs = pickle.load(file)

                    # Check types in the list
                    for job in jobs:
                        if not isinstance(job, CapturedJob):
                            raise TypeError(f"file {file_path} contained invalid data")

                    # Add captured jobs to list
                    self.add_jobs(jobs)
            except EOFError:
                raise TypeError(f"file {file_path} invalid format")

        # Make absolute path from given path
        path = pathlib.Path(path).resolve()

        # If path is a file, load jobs directly
        if os.path.isfile(path):
            add_jobs_from_file(path)

        # If path is a directory, look for *.jobs files to be loaded in this directory
        if os.path.isdir(path):

            # Go through all filenames in the directory
            for filename in os.listdir(path):

                # Skip if extension does not match
                if filename.endswith(".jobs"):
                    add_jobs_from_file(filename)
