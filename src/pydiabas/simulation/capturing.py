# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

import os
import pickle
from dataclasses import dataclass
from typing import Optional, Callable

from ..result import Result


@dataclass
class CapturedJob:
    """Contains captured data of an executed job

    ecu, job, parameters and result_filter are the arguments passed to PyDIABAS when executing the job.
    result is the Result object returned by the job.

    This object can be used to simulate job execution manly to be able to run tests without being connected to a car.
    """

    ecu: str
    job: str | bytes
    parameters: str | bytes | list[str] | list[bytes]
    result_filter: str | list[str]
    result: Result

    def __init__(
        self,
        ecu: str,
        job: str | bytes,
        result: Result,
        parameters: str | bytes | list[str] | list[bytes] = "",
        result_filter: str | list[str] = "",
    ) -> None:
        """Initializes the object with the given values

        parameters and result_filter will be set to an empty string if not given.
        job is set to upper characters as EDIABAS is not case sensitive on this parameter.

        Parameters:
        ecu: Name of the ECU the job has to be send to.
        job: Name of the job to be executed.

        Optional Parameters:
        parameters: Job parameters to be passed alongside with the job.
        result_filter: Results to be asked for. May not work with all ECUs.
        """

        self.ecu = ecu
        self.job = job.upper()
        self.parameters = parameters
        self.result_filter = result_filter
        self.result = result

    def check(
        self,
        ecu: str,
        job: str | bytes,
        parameters: str | bytes | list[str] | list[bytes] = "",
        result_filter: str | list[str] = "",
    ) -> Optional[Result]:
        """Check if the given job arguments match to the ones captured in this object

        If the arguments match, the captured result is returned, if not this function will return None.
        job is not case sensitive.

        Parameters:
        ecu: Name of the ECU the job has to be send to.
        job: Name of the job to be executed.

        Optional Parameters:
        parameters: Job parameters to be passed alongside with the job.
        result_filter: Results to be asked for. May not work with all ECUs.

        Return values:
        return: Result object of arguments match, or None if not.
        """

        if (
            self.ecu == ecu
            and self.job == job.upper()
            and self.parameters == parameters
            and self.result_filter == result_filter
        ):
            return self.result


def capture_job(job_func: Callable, job_cache: list) -> Callable:
    """Decorator for the PyDIABAS.job method to save data of executed jobs in a list

    The list to store the jobs data to, must be passed as job_cache argument.

    Parameters:
    job_func: Original PyDIABAS.job method.
    job_cache: List to be used as storage for captured jobs.

    Return values:
    return: Decorated job function.
    """

    def wrap(*args, **kwargs) -> Result:
        # As the job method accepts the arguments either as positional, keyword or a combination of these arguments
        # they need to be looked for in both args and kwargs

        # The necessary data (ecu and job) needs to be available. If they are not available as positional arguments
        # (Index Error is being raised), they need to be available as keyword argument. If not, the resulting
        # KeyError will be propagated to the caller.
        try:
            ecu = args[0]
        except IndexError:
            ecu = kwargs["ecu"]

        try:
            job = args[1]
        except IndexError:
            job = kwargs["job"]

        # Optional data will be given a default value if they are neither in positional nor in keyword arguments.
        try:
            parameters = args[2]
        except IndexError:
            try:
                parameters = kwargs["parameters"]
            except KeyError:
                parameters = ""

        try:
            parameters = args[2]
        except IndexError:
            try:
                parameters = kwargs["parameters"]
            except KeyError:
                parameters = ""

        try:
            result_filter = args[3]
        except IndexError:
            try:
                result_filter = kwargs["result_filter"]
            except KeyError:
                result_filter = ""

        # The original job function will be called with the original arguments
        result: Result = job_func(*args, **kwargs)

        # Add the result together with the arguments to the list of captured jobs.
        job_cache.append(
            CapturedJob(
                ecu=ecu,
                job=job,
                parameters=parameters,
                result_filter=result_filter,
                result=result,
            )
        )

        # The result will be returned to the caller
        return result

    return wrap


def save_jobs_to_file(
    jobs: CapturedJob | list[CapturedJob] | tuple[CapturedJob],
    directory: str | os.PathLike = "",
) -> str:
    """Saves given jobs as .jobs file and return filename used

    Tries to save given jobs to a file with .jobs extension at the given path. If no path is given, the current working directory (CWD) is used.
    The filename will automatically be chosen and looks like CAPTURE_***.jobs where *** is a ascending number 1-999 without overwriting existing files.
    If no free filename is found, a FileExistsError will be raised.

    Parameters:
    jobs: on single CapturedJob object or a list or tuple of CapturedJob objects to be saved.

    Optional Parameters:
    directory: Path to the directory to write the file to.

    Return values:
    return: Path to stored file as str.

    Raises:
        FileExistsError
    """

    # If a single CapturedJob object is passed, put it into a list to follow formatting of *.jobs files
    if isinstance(jobs, CapturedJob):
        jobs = [jobs]

    for n in range(1, 1000):

        # Join given path with filename
        file_path: str = os.path.join(directory, f"CAPTURE_{n:03d}.jobs")

        # Avoid overwriting an existing file
        if not os.path.exists(file_path):

            # Save jobs as pickle file
            with open(file_path, "wb") as file:
                pickle.dump(jobs, file, pickle.HIGHEST_PROTOCOL)

            # Return path to the written file
            return file_path

    # Raise an error if no unused filename could be found
    raise FileExistsError(
        "Unable to save file, there seems to be too many *.jobs files in the directory"
    )
