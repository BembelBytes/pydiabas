# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

import ctypes
from ctypes.util import find_library


# Load API DLL (32bit)
# A 32bit python version is necessary
_api32 = ctypes.WinDLL(find_library("api32"))


# Extract functions from DLL
enableServer = _api32.enableServer  # Not implemented in api.py
closeServer = _api32.closeServer  # Not implemented in api.py
enableMultiThreading = _api32.enableMultiThreading  # Not implemented in api.py

apiInit = _api32.__apiInit
apiInitExt = _api32.__apiInitExt  # Not implemented in api.py
apiBreak = _api32.__apiBreak
apiEnd = _api32.__apiEnd

apiSwitchDevice = _api32.__apiSwitchDevice  # Not implemented in api.py

apiState = _api32.__apiState
apiStateExt = _api32.__apiStateExt  # Not implemented in api.py

apiTrace = _api32.__apiTrace

apiCheckVersion = _api32.__apiCheckVersion
apiGetConfig = _api32.__apiGetConfig
apiSetConfig = _api32.__apiSetConfig

apiErrorCode = _api32.__apiErrorCode
apiErrorText = _api32.__apiErrorText

apiJob = _api32.__apiJob
apiJobData = _api32.__apiJobData
apiJobExt = _api32.__apiJobExt
apiJobInfo = _api32.__apiJobInfo

apiResultSets = _api32.__apiResultSets
apiResultNumber = _api32.__apiResultNumber
apiResultName = _api32.__apiResultName
apiResultFormat = _api32.__apiResultFormat

apiResultBinary = _api32.__apiResultBinary
apiResultBinaryExt = _api32.__apiResultBinaryExt
apiResultByte = _api32.__apiResultByte
apiResultChar = _api32.__apiResultChar
apiResultDWord = _api32.__apiResultDWord
apiResultInt = _api32.__apiResultInt
apiResultLong = _api32.__apiResultLong
apiResultReal = _api32.__apiResultReal
apiResultText = _api32.__apiResultText
apiResultVar = _api32.__apiResultVar
apiResultWord = _api32.__apiResultWord

apiResultsNew = _api32.__apiResultsNew
apiResultsScope = _api32.__apiResultsScope
apiResultsDelete = _api32.__apiResultsDelete
