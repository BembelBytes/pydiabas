# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from .ediabas import utils, EDIABAS


class Result:
    """Class to handle the results in the EDIABAS API."""

    def __init__(self, ediabas: EDIABAS) -> None:
        """Initializes the Result object.

        Handling the EDIABAS API initialization and job execution must be done before trying to fetch the results.

        Parameters:
        ediabas: Instance of pydiabas.ediabas.EDIABAS class.

        Raises:
            TypeError
        """

        if not isinstance(ediabas, EDIABAS):
            raise TypeError("ediabas need to be an instance of EDIABAS")

        self._ediabas = ediabas
        self._jobSets: list[Set] = []
        self._systemSet: Set = Set()

    def clear(self) -> None:
        """Resets systemSet and jobSets."""

        self._systemSet = Set()
        self._jobSets = []

    def _fetchset(self, i_set: int) -> Result:
        """Gets all result names and values from the given set.
        USES EDIABAS API INDEXING! Set #0 is alway the system set. Job sets start at set #1.

        Parameters:
        i_set: Set index to be fetched (#0 is system result, job results start at #1).

        Return values:
        return: Result object.

        Raises:
            IndexError
        """

        rows: list[Row] = []

        job_sets_available = self._ediabas.resultSets()
        if i_set > job_sets_available:
            raise IndexError("Index out of range")

        # Got trough all results in the given set and add them to the rows
        for pos in range(1, self._ediabas.resultNumber(set=i_set) + 1):
            result_name = self._ediabas.resultName(position=pos, set=i_set).upper()
            rows.append(
                Row(result_name, utils.getResult(self._ediabas, result_name, set=i_set))
            )

        # Set the rows as systemResult if set 0 has been fetched (set 0 contains always the system results according to
        # EDIABAS API documentation)
        if i_set == 0:
            self._systemSet = Set(rows)

        # Add the rows to the jobSets and make sure to fill any missing sets before the index of the given set with
        # empty sets if necessary
        else:
            # index for job sets is not the same as the set index from EDIABAS API as set #0 is always the system set
            # and job data sets start at set #1
            i_job_set = i_set - 1

            # Fill list with empty sets if necessary to be able to get the fetched set via its index in jobSets
            for i in range(i_job_set + 1):
                try:
                    self._jobSets[i]
                except IndexError:
                    self._jobSets.append(Set())

            # Store set in jobSets
            self._jobSets[i_job_set] = Set(rows)

        return self

    def fetchsystemset(self) -> Result:
        """Gets all result names and values from the systemSet.
        Any previously stored results in the systemSet will be overridden!

        Return values:
        result: Result object.
        """

        self._fetchset(i_set=0)
        return self

    def fetchjobsets(self) -> Result:
        self._jobSets = []
        for s in range(self._ediabas.resultSets()):
            self._fetchset(s + 1)

        return self

    def fetchall(self) -> Result:
        """Gets the systemSet and all available jobSets.
        All previously stored result data will be overridden!

        Result values:
        result: Result object.
        """

        self.fetchsystemset()
        self.fetchjobsets()
        return self

    def fetchname(self, name: str) -> Result:
        """Searches every jobSet for the given name and gets the corresponding value.
        Results will be incorporated in already present jobResult data.
        systemSet will not be searched.
        Only the first occurrence of the name per jobSet will be fetched.

        Parameters:
        name: Name to be searched for.

        Return values:
        result: Result object.
        """

        # Search for result with given name in each job set
        for i_set in range(self._ediabas.resultSets()):

            # Add an empty set if needed
            if len(self._jobSets) <= i_set:
                self._jobSets.append(Set())

            # Try to get result by name in this set
            result_value = utils.getResult(self._ediabas, name, set=i_set + 1)
            if result_value is not None:

                # Check if row with same name is already present and set new value
                found: bool = False
                for i_row, row in enumerate(self._jobSets[i_set]):
                    if row.name.upper() == name.upper():
                        self._jobSets[i_set][i_row].value = result_value
                        # End this iteration if row has been found
                        found = True
                        break

                if found:
                    continue

                # Add new row to set
                row_to_add = Row(name=name, value=result_value)
                self._jobSets[i_set]._rows.append(row_to_add)

        return self

    def fetchnames(self, names: list[str]) -> Result:
        """Searches every jobSet for the given names and gets the corresponding values.
        Results will be incorporated in already present jobResult data.
        systemSet will not be searched.
        Only the first occurrence of each name per jobSet will be fetched.

        Parameters:
        names: List of names to be searched for.

        Return values:
        result: Result object.
        """

        for name in names:
            self.fetchname(name)

        return self

    @property
    def systemSet(self) -> Set:
        """Set containing all system related results."""

        return self._systemSet

    @property
    def jobSets(self) -> list[Set]:
        """Sets containing all job related results."""

        return self._jobSets

    @property
    def ecu(self) -> str | None:
        """Name of the ECU."""

        try:
            return self._systemSet["VARIANTE"]
        except KeyError:
            return None

    @property
    def jobname(self) -> str | None:
        """Name of the job. Not implemented in all ECUs."""

        try:
            return self._systemSet["JOBNAME"]
        except KeyError:
            return None

    @property
    def jobstatus(self) -> str | None:
        """Jobstatus in plain text."""

        try:
            return self._systemSet["JOBSTATUS"]
        except KeyError:
            return None

    def as_dicts(self) -> list[dict]:
        """List of dicts holding all fetched result data.
        systemSet will be at index #0, jobSets will start at index #1.

        Return values:
        result: A list with a dict for each set (systemSet and jobSets).
        """

        return [self._systemSet.as_dict()] + [s.as_dict() for s in self._jobSets]

    def count(self, name: str) -> int:
        """Number of occurrences of the given job name in all jobSets

        Parameters:
        name: Name of the result to be counted.

        Return values:
        result: Number of occurrences.

        Raises:
            TypeError
        """

        # Check correct type of name
        if not isinstance(name, str):
            raise TypeError("name need to be a string")

        # Search all jobSets for the name
        n = 0
        for s in self._jobSets:
            if name in s:
                n += 1
        return n

    def index(self, name: str, start: int = 0, end: int | None = None) -> int:
        """Get index of first set in jobSets containing the given name starting and ending with the indexes given.
        If a result with the given name cannot be found, a ValueError will be raised.

        Parameters:
        name: Name of the result to be searched for.

        Optional Parameters:
        start: Index to start searching from (including the given index).
        end: Index to stop searching at (not including the given index).

        Return values:
        result: Index of set in jobSets containing a result with the given name.

        Raises:
            TypeError
            ValueError
        """

        if not isinstance(name, str):
            raise TypeError("name need to be a string")

        for i, s in enumerate(
            self._jobSets[start : end if end else len(self._jobSets)]
        ):
            if name in s:
                return i + start

        raise ValueError(f"'{name}' is not in result")

    def get(self, name: str, default=None) -> int | str | bytes | float | None:
        """Get the value of the first occurrence of a result with the given name
        starting from the first jobSet to the last.
        Any further occurrences of the name in other jobSets will be ignored.
        A default value other than None can be specified.

        Parameters:
        name: Name of the result to get the value from

        Optional Parameters:
        default: Value to be returned of no result with the given name has been found.

        Return value:
        result: Value of the result or default value

        Raises:
            TypeError
        """

        if not isinstance(name, str):
            raise TypeError("name need to be a string")

        for set in self._jobSets:
            try:
                return set[name]
            except KeyError:
                pass

        return default

    def get_in(self, pattern: str, default=None) -> int | str | bytes | float | None:
        """Get the value of the first occurrence of a result that partially matches the pattern
        starting from the first jobSet to the last.
        Any further occurrences of the name in other jobSets will be ignored.
        A default value other than None can be specified.

        Parameters:
        pattern: A string that must partially match the result name.

        Optional Parameters:
        default: Value to be returned of no result with the given name has been found.

        Return value:
        result: Value of the result or default value

        Raises:
            TypeError
        """

        if not isinstance(pattern, str):
            raise TypeError("pattern need to be a str")

        for set in self._jobSets:
            if value := set.get_in(pattern):
                return value

        return default

    def get_fn(self, fn: Callable, default=None) -> int | str | bytes | float | None:
        """Get the value of the first occurrence of a result that returns True when passed to the callable
        starting from the first jobSet to the last.
        Any further occurrences of the name in other jobSets will be ignored.
        A default value other than None can be specified.

        Parameters:
        fn: A function that takes one str argument and returns a bool.

        Optional Parameters:
        default: Value to be returned of no result with the given name has been found.

        Return value:
        result: Value of the result or default value

        Raises:
            TypeError
        """

        if not isinstance(fn, Callable):
            raise TypeError("fn need to be a function")

        for set in self._jobSets:
            if value := set.get_fn(fn):
                return value

        return default

    def __len__(self) -> int:
        return len(self._jobSets)

    def __bool__(self) -> bool:
        return bool(self._jobSets)

    def __iter__(self) -> Result:
        self._n = 0
        return self

    def __next__(self) -> Set:
        if self._n < self.__len__():
            result = self._jobSets[self._n]
            self._n += 1
            return result
        else:
            raise StopIteration()

    def __str__(self) -> str:
        s = "\n"
        s += "============== PyDIABAS Result ==============\n"

        if self._systemSet:
            s += "-------------- systemSet       --------------\n"
            s += str(self._systemSet)

        for i in range(len(self._jobSets)):
            s += f"-------------- jobSet #{i:<3d}     --------------\n"
            s += str(self._jobSets[i])

        s += "============== END             ==============\n"
        return s

    def __getitem__(
        self, key: str | int | slice
    ) -> list[Row] | Row | int | str | bytes | float:
        """Gets items from the jobSets only."""

        if isinstance(key, slice):
            sliced_result = Result(self._ediabas)
            sliced_result._systemSet = self._systemSet
            sliced_result._jobSets = self._jobSets[key]
            return sliced_result

        if isinstance(key, int):
            return self._jobSets[key]

        elif isinstance(key, str):
            for s in self._jobSets:
                try:
                    return s[key]
                except KeyError:
                    pass

            raise KeyError(f"'{key}' not in result")

        raise TypeError(f"Expected str, int or slice. Got {type(key)}")

    def __contains__(self, name: str) -> bool:
        """Checks jobSets only."""

        if not isinstance(name, str):
            raise TypeError("name need to be a string")

        for set in self._jobSets:
            for row in set:
                if name.upper() == row.name.upper():
                    return True

        return False


class Set:
    """Class to store a set of results form the EDIABAS API."""

    def __init__(self, rows: list[Row] | None = None) -> None:
        """Initializes a new instance of Set either empty or with the rows given as parameter.

        Optional Parameters:
        rows: list of Row types to be used as initial data n the set.

        Raises:
            TypeError
        """

        # Set rows to empty list if not passed as arguments
        # = [] as default value as function parameter leads to unpredictable behavior.
        if rows is None:
            rows = []

        if not isinstance(rows, list):
            raise TypeError("rows need to be a list containing Row instances")

        for row in rows:
            if not isinstance(row, Row):
                raise TypeError("rows need to be a list containing Row instances")

        self._rows = rows

    @property
    def all(self) -> list[Row]:
        """All rows in a list."""

        return self._rows

    def as_dict(self) -> dict:
        """All rows as a dict with row.name as key and row.value as value.

        Return values:
        result: dict containing all results.
        """

        return {row.name: row.value for row in self._rows}

    def index(self, name: str, start: int = 0, end: int | None = None) -> int:
        """Get the index of a row with the given name.
        Start and end can be given as indexes.
        If the name cannot be found, a ValueError will be raised.

        Parameters:
        name: Name of the result to search for.

        Optional Parameters:
        start: Index to start searching from (including the given index).
        end: Index to stop searching at (not including the given index).

        Return values:
        result: Index of the result with the given name.

        Raises:
            ValueError
        """

        if not isinstance(name, str):
            raise TypeError("name need to be a string")

        for i, row in enumerate(
            self._rows[start : end if end is not None else len(self._rows)]
        ):
            if row.name.upper() == name.upper():
                return i + start

        raise ValueError(f"'{name}' is not in set")

    def keys(self) -> list:
        """List of all row.names if this Set.

        Return values:
        result: List of all names in the Set.
        """

        return [row.name for row in self._rows]

    def values(self) -> list:
        """List of all row.values if this Set.

        Return values:
        result: List of all values in the Set.
        """

        return [row.value for row in self._rows]

    def items(self) -> list[tuple]:
        """List of all rows if this Set as tuples.

        Return values:
        result: List of all rows in the Set as tuples.
        """

        return [(row.name, row.value) for row in self._rows]

    def get(self, name: str, default=None) -> int | str | bytes | float | None:
        """Get the value of the row with the given name.
        A default value other than None can be specified.

        Parameters:
        name: Name of the row to get the value from.

        Optional Parameters:
        default: Value to be returned of no row with the given name has been found.

        Return value:
        result: Value of the row or default value

        Raises:
            TypeError
        """

        if not isinstance(name, str):
            raise TypeError("name need to be a string")

        try:
            return self[name]
        except KeyError:
            return default

    def get_in(self, pattern: str, default=None) -> int | str | bytes | float | None:
        """Get the value of the first row partially matching the given pattern.
        A default value other than None can be specified.

        Parameters:
        pattern: Str that must be in the result name to match.

        Optional Parameters:
        default: Value to be returned of no row with the given name has been found.

        Return value:
        result: Value of the row or default value

        Raises:
            TypeError
        """

        if not isinstance(pattern, str):
            raise TypeError("pattern need to be a string")

        for row in self._rows:
            if pattern.upper() in row.name.upper():
                return row.value

        return default

    def get_fn(self, fn: Callable, default=None) -> int | str | bytes | float | None:
        """Get the value of the first row returning true when passed into the given function.
        A default value other than None can be specified.

        Parameters:
        fn: A function that takes one str argument and returns a bool.

        Optional Parameters:
        default: Value to be returned of no row with the given name has been found.

        Return value:
        result: Value of the row or default value

        Raises:
            TypeError
        """

        if not isinstance(fn, Callable):
            raise TypeError("fn need to be a function")

        for row in self._rows:
            if fn(row.name):
                return row.value

        return default

    def __len__(self) -> int:
        return len(self._rows)

    def __bool__(self) -> bool:
        return bool(self._rows)

    def __iter__(self) -> Row:
        self._n: int = 0
        return self

    def __next__(self) -> Row:
        if self._n < self.__len__():
            result = self._rows[self._n]
            self._n += 1
            return result
        else:
            raise StopIteration()

    def __str__(self) -> str:
        s = ""
        for i, row in enumerate(self._rows):
            s += f"{row.name:30}: {row.value}"
            if i < len(self) - 1:
                s += "\n"
        s += "\n"
        return s

    def __getitem__(self, key: str | int | slice) -> int | str | bytes | float:
        if isinstance(key, slice):
            return Set(self._rows[key])

        if isinstance(key, int):
            return self._rows[key]

        if isinstance(key, str):
            for row in self._rows:
                if key.upper() == row.name.upper():
                    return row.value

            raise KeyError(f"'{key}' not in set")

        raise TypeError(f"Expected str, int or slice. Got {type(key)}")

    def __contains__(self, name: str) -> bool:
        if not isinstance(name, str):
            raise TypeError("name need to be a string")

        for row in self._rows:
            if name.upper() == row.name.upper():
                return True

        return False


@dataclass
class Row:
    """Represents a row in a Set. Maps name to value."""

    name: str
    value: bytes
