# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

from .ediabas import EDIABAS
from .exceptions import JobFailedError
from .statics import API_RESULT_FORMAT


def getResult(
    ediabas: EDIABAS, name: str | bytes, set: int = 1
) -> str | bytes | int | float | None:
    """First checks for the result format and then gets the result from EDIABAS API and converts it to
    the corresponding python type. If set number is not given, set #1 is used.

    Parameters:
    ediabas: EDIABAS instance.
    name: Name of the result to get.
    set: Set to be used.

    Return values:
    return: Value of the result or None of result with the given name is not available.
    """

    # Convert arguments to bytes if given as strings
    name = EDIABAS._process_text_argument(name)

    try:
        match ediabas.resultFormat(name, set):
            case API_RESULT_FORMAT.BINARY:
                return ediabas.resultBinary(name, set)

            case API_RESULT_FORMAT.BYTE:
                return ediabas.resultByte(name, set)

            case API_RESULT_FORMAT.CHAR:
                return ediabas.resultChar(name, set)

            case API_RESULT_FORMAT.DWORD:
                return ediabas.resultDWord(name, set)

            case API_RESULT_FORMAT.INTEGER:
                return ediabas.resultInt(name, set)

            case API_RESULT_FORMAT.LONG:
                return ediabas.resultLong(name, set)

            case API_RESULT_FORMAT.REAL:
                return ediabas.resultReal(name, set)

            case API_RESULT_FORMAT.TEXT:
                return ediabas.resultText(name, set)

            case API_RESULT_FORMAT.WORD:
                return ediabas.resultWord(name, set)

    except JobFailedError:
        return None
