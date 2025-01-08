# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

from typing import Optional

from ..pydiabas import PyDIABAS, StateError
from ..result import Set


class ECU:
    """Represents a ECU and provides functionality to be used with any BEST ECU."""

    # ECU name
    name: str = ""

    def __init__(self, name: Optional[str] = None) -> None:
        """Initializes a new instance and sets name if given."""

        if name is not None:
            self.name = name

    def job(
        self,
        pydiabas: PyDIABAS,
        job: str | bytes,
        parameters: str | bytes | list[str] | list[bytes] = "",
        result_filter: str | list[str] = "",
        fetchall: bool = True,
    ):
        """Executes a job on this ECU

        This method is just implemented to facilitate the execution on jobs when currently working with a ECU class
        instead of working with directly on a PyDIABAS instance.
        There is no additional functionality to the job() method of the PyDIABAS class.

        Parameters:
        pydiabas: PyDIABAS instance to be used to communicate with the ECU.
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

        return pydiabas.job(
            ecu=self.name,
            job=job,
            parameters=parameters,
            result_filter=result_filter,
            fetchall=fetchall,
        )

    def get_jobs(
        self, pydiabas: PyDIABAS, details: bool = True, verbose: bool = False
    ) -> dict[dict]:
        """Gets names of all available jobs in the ecu. If details ar set to True, additional job information will be
        added to each job if available in the ecu.

        Parameters:
        pydiabas: Instance of PyDIABAS.

        Optional Parameters:
        details: Selects if additional job info will be retrieved from the ecu.
        verbose: Selects if progress is written to stdout.

        Return values:
        result: Job data in a dict.
        """

        # Fill a list with available job names from ECU
        jobs: dict[str] = {s["JOBNAME"]: {} for s in pydiabas.job(self.name, "_JOBS")}

        if verbose:
            print(f"Found {len(jobs)} jobs")

        if details:
            # Get additional data for all found jobs
            for n, job in enumerate(jobs):

                # Get job comments, argument and return value information
                jobs[job] = self.get_job_details(pydiabas, job)

                if verbose:
                    percent: int = round(100 * (n + 1) / len(jobs))
                    print(
                        f"\r[{'=' * (percent // 2)}{' ' * (50 - (percent // 2))}] {percent:3d}% complete",
                        end="",
                    )

        if verbose:
            print("\nDone!")

        return jobs

    def get_job_details(self, pydiabas: PyDIABAS, job: str) -> dict:
        """Get additional info about a job available in the ECU like:
            Job comments
            Job arguments, their name, type and comments about it
            Job results, their name type and comments about it
        If the job does not exist, an empty data structure will be returned.

        Parameters:
        pydiabas: Instance of PyDIABAS.
        job: Name of the job.

        Return values:
        result: Job info in a dict.
        """

        info: dict[list] = {
            "comments": [],
            "arguments": [],
            "results": [],
        }

        try:
            # All comments will be stored in set 1
            comments: Set = pydiabas.job(self.name, "_JOBCOMMENTS", job)[0]
            info["comments"] = [
                comments[key]
                for key in sorted(
                    comments.keys(), key=lambda x: int(x.replace("JOBCOMMENT", ""))
                )
            ]
        except (StateError, IndexError):
            pass

        # Argument and result info will be stored in set 1-n
        try:
            arguments: list[Set] = pydiabas.job(self.name, "_ARGUMENTS", job)
            info["arguments"] = [
                {
                    "name": arguments[i]["ARG"],
                    "type": arguments[i]["ARGTYPE"],
                    "comments": [
                        arguments[i][key]
                        for key in arguments[i].keys()
                        if key.startswith("ARGCOMMENT")
                    ],
                }
                for i in range(len(arguments))
            ]
        except (StateError, IndexError):
            pass

        try:
            results: list[Set] = pydiabas.job(self.name, "_RESULTS", job)
            info["results"] = [
                {
                    "name": results[i]["RESULT"],
                    "type": results[i]["RESULTTYPE"],
                    "comments": [
                        results[i][key]
                        for key in results[i].keys()
                        if key.startswith("RESULTCOMMENT")
                    ],
                }
                for i in range(len(results))
            ]
        except (StateError, IndexError):
            pass

        return info

    def get_tables(
        self, pydiabas: PyDIABAS, details: bool = True, verbose: bool = False
    ) -> dict[dict]:
        """Gets names of all available tables in the ecu. If details ar set to True, table header and body data
        will be added.

        Parameters:
        pydiabas: Instance of PyDIABAS.

        Optional Parameters:
        details: Selects if table header and body data will be retrieved from the ecu.
        verbose: Selects if progress is written to stdout.

        Return values:
        result: Table data in a dict.
        """

        # Fill a dict with all available table names as keys
        tables: dict[str] = {s["TABLE"]: {} for s in pydiabas.job(self.name, "_TABLES")}

        if verbose:
            print(f"Found {len(tables)} tables")

        if details:
            # Get additional information for all tables
            for n, table in enumerate(tables):
                tables[table] = self.get_table_details(pydiabas, table)

                if verbose:
                    percent: int = round(100 * (n + 1) / len(tables))
                    print(
                        f"\r[{'=' * (percent // 2)}{' ' * (50 - (percent // 2))}] {percent:3d}% complete",
                        end="",
                    )

        if verbose:
            print("\nDone!")

        return tables

    def get_table_details(self, pydiabas: PyDIABAS, table: str) -> dict:
        """Get table header and body data from a table in the ecu.
        If the table does not exist, an empty data structure will be returned.

        Parameters:
        pydiabas: Instance of PyDIABAS.
        table: Name of the table.

        Return values:
        result: Table header and body data in a dict.
        """

        info: dict[list] = {"header": [], "body": []}

        try:
            contents: list[Set] = pydiabas.job(self.name, "_TABLE", table)
            headers: Set = contents[0]
            body: list[Set] = contents[1:]

            info["header"] = [
                headers[key]
                for key in sorted(
                    headers.keys(), key=lambda x: int(x.replace("COLUMN", ""))
                )
            ]

            info["body"] = [
                [
                    body[i][key]
                    for key in sorted(
                        body[i].keys(), key=lambda x: int(x.replace("COLUMN", ""))
                    )
                ]
                for i in range(len(body))
            ]

        except (StateError, IndexError):
            pass

        return info
