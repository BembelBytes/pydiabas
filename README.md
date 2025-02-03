# pydiabas
**pydiabas** is a python module for communication with ECUs (Electronic Control Units) in cars using **EDIABAS** as diagnosis system (eg. BMW, Volkswagen).
The module has only been tested on BMW cars.
Using this module makes it possible to make advantage of the comfort features of python by still allowing communication to a car using **EDIABAS** on a very low level.

## Table of contents
1. [General Description](#1-general-description)
2. [System Requirements](#2-system-requirements)
3. [Installation](#3-installation)
4. [Quick Start](#4-quick-start)
5. [Module Documentation](#5-module-documentation)
    - [pydiabas module](#pydiabas-module)
        - [PyDIABAS class](#pydiabas-class)
        - [Result class](#result-class)
        - [Set class](#set-class)
        - [Row class](#row-class)
    - [ediabas module](#ediabas-module)
        - [EDIABAS class](#ediabas-class)
        - [statics](#statics)
        - [utils](#utils)
        - [api32](#api32)
    - [ecu module](#ecu-module)
        - [ECU class](#ecu-class)
        - [MSD80 class](#msd80-class)
    - [simulation module](#simulation-module)
        - [SimulatedPyDIABAS class](#simulatedpydiabas-class)
        - [CapturedJob class](#capturedjob-class)
        - [capture_jobs decorator](#capture_jobs-decorator)
6. [Tests](#6-tests)
7. [Limitations](#7-limitations)
8. [Future Development](#8-future-development)
9. [EDIABAS Troubleshooting](#9-ediabas-troubleshooting)
10. [License](#10-license)
11. [Change Log](#11-change-log)

## 1 General Description
The **pydiabas** module has two sub modules:
- **ecu**: For ECU specific tasks
- **ediabas**: For direct access to **EDIABAS** without using **pydiabas**
> **Note**
> For a better distinction between this documentation uses the following formatting:
> - **EDIABAS**: EDIABAS system installed separately on your pc
> - **ediabas**: ediabas python module.
> - *EDIABAS*: EDIABAS class located in the ediabas module.

### Architecture
1. **EDIABAS**: It's the basis for any communication via the OBD cable tour your car, respective your cars ECUs. It is installed separately and not part of this python module.
2. **ediabas**: Serves mainly as a wrapper to provide a more pythonic API for **EDIABAS** and  has an utility to facilitate result retrieval. This module can be used even without **pydiabas**.
3. **pydiabas**: Serves as an additional abstraction layer on top of the **ediabas** module to make working with **EDIABAS** more flawless and to hide some complexity from the user. This is the main abstraction layer to be used.
4. **ecu**: Can be used in addition to **pydiabas**. It contains a generic ECU class which can be used with any ECU to extract available jobs and tables.
Furthermore the are classes for single ECUs with specific functionality related to these ECUs.

## 2 System Requirements
To use **pydiabas** there are some system requirements to observe.
As far as I know, **EDIABAS** is only running on Windows.

### EDIABAS
A working **EDIABAS** (version >= 7.0.0) is required. The collection and installation of **EDIABAS** ist neither part of this module nor covered in this documentation. There are a lot of sources, instructions and tutorials out there.
Under [8. EDIABAS Troubleshooting](#8-ediabas-troubleshooting) you can finde some help regarding common problems using **EDIABAS**, focussing on configuring **EDIABAS** correctly to establish a communication via the OBD cable.

### OBD Cable
I'm using the [MaxDia Diag 2+](https://www.obdexpert.de/shopware/diagnose-artikel/fuer-bmw-fahrzeuge/33/maxdia-diag-2-diagnose-interface-fuer-bmw-fahrzeuge-bj.-2007-2016-ohne-software?c=20) cable from [obdexpert.de](https://www.obdexpert.de). This cable is usable for BMW from 2007 to 2016. If you need to connect to older BMWs, you may want to use this [Pin7 - Pin8 - Connector für MaxDia Diag2+](https://www.obdexpert.de/shopware/diagnose-artikel/fuer-bmw-fahrzeuge/28/pin7-pin8-connector-fuer-maxdia-diag2?c=20).

> **Note**
> I don't get payed by obdexpert.de, its just as personal recommendation based on my experience. There may be lots of other cables out there which will be as good or even better as my suggestion, but I've never used them.

### Python Version and dependencies
This module has been developed using [python 3.12.7 32bit](https://www.python.org/downloads/release/python-3127/) and tested on [python 3.13.1 32bit](https://www.python.org/downloads/release/python-3131/). The minimum required version is [python 3.10.0 32bit](https://www.python.org/downloads/release/python-3100/).
As **EDIABAS** uses 32bits memory addresses, a 32bit python version is necessary to load the **EDIABAS** dynamic library ("api32.dll").


## 3 Installation
You can use *pip* to install pydiabas using the following command
```
pip install pydiabas
```

## 4 Quick Start

To get your first data out of **pydiabas** you just need a few lines of code.
It's not necessary to have your OBD cable connected to your PC as `TMODE` is a simulated ECU which can be accessed without being connected to a car.

```py
# Make sure to use a 32bit python version!

# Import the PyDIABAS class from the pydiabas module
from pydiabas import PyDIABAS

# Start the session
# Using pythons context manager ensured proper closing of the EDIABAS session
with PyDIABAS() as pydiabas:

    # Ask the ECU named "TMODE" to execute a job named "LESE_INTERFACE_TYP"
    result = pydiabas.job("TMODE", "LESE_INTERFACE_TYP")

    # Access result data
    print(result["TYP"]) # prints: b'OBD'
```
> __Info:__ If you get the following error you are most probably using a 64bit python version.  
> `OSError: [WinError 193] %1 is not a valid Win32 application`


## 5 Module Documentation

### pydiabas module
This is the main module to be used. It provides all functionality usually required to use **EDIABAS** for communication with ECUs. The **ediabas** sub-module offers more control but needs a deeper understanding about the **EDIABAS** system to work with.

#### PyDIABAS class
The *PyDIABAS* class provides a simple and comfortable API for communication via **EDIABAS**.

##### Starting and ending the **EDIABAS** session
After creating an instance of *PyDIABAS* the *start()* method must be called to set up everything for subsequent communication. This can be done either manually, or automatically by using pythons context manager. Calling *start()* multiple times will usually not cause any problems or memory leaks.
After finishing communications the *end()* method must be called to stop the connection to **EDIABAS** and free the used resources. This is done automatically by using pythons context manager, or must be done manually otherwise.
Forgetting to call *end()* usually doesn't cause any major problems, even for possible succeeding **EDIABAS** sessions on the same machine but it should always be done as a good habit.
During any time the present state of **EDIABAS** can be checked using the property *ready*. It returns *True* if **EDIABAS** is ready or *False* if not. Getting *False* as return value does not necessary mean that **EDIABAS** is not able to execute a Job. *False* may be returned if *start()* has not been called or failed, or if the previous job failed for any reason. In the last case a succeeding job may run successful.

```py
# Starting and ending an EDIABAS session manually
from pydiabas import PyDIABAS

# Create an PyDIABAS instance
pydiabas = PyDIABAS()

# Start the session
pydiabas.start()

# All the work will be done here
# Make sure to catch possible exceptions to make sure the session is being closed properly

# End the session
pydiabas.end()
```
```py
# Starting and ending an EDIABAS session automatically using pythons context manager
from pydiabas import PyDIABAS

with PyDIABAS() as pydiabas:
    # All the work will be done here
    # The session will be started and ended automatically even if exception occur
```
```py
# Using ready property
from pydiabas import PyDIABAS

pydiabas = PyDIABAS()
print(pydiabas.ready) # prints: False

pydiabas.start()
print(pydiabas.ready) # prints: True

pydiabas.end()
print(pydiabas.ready) # prints: False
```

##### Configurations
Initial **EDIABAS** configurations will be loaded from the respective `EDIABAS.ini` file in the `/bin` folder of your **EDIABAS** installation. Please refer to the documentation of your **EDIABAS** installation for further details.
Values not configured via this file will be set to hardcoded default values by **EDIABAS**.
Basically there is no need to change any configurations for routine usage of **pydiabas**.
If required, configuration can be changed using the *config()* method.
Changes to the configuration will be passed as keyword arguments to the *config()* method.
Any changes done via an *PyDIABAS* object will be stored inside the object and will be returned as a dict with lower lettered keys any time the *config()* method is called.
Accessing this dict without changing the configuration can be done by calling *config()* without passing any parameters.
A complete list of configuration parameters can be found in the documentation (usually placed in the `/Doku` folder) of your **EDIABAS** installation or in the docstring of the **EDIABAS** class.

```py
# Setting and reading configuration changes
from pydiabas import PyDIABAS

with PyDIABAS() as pydiabas:

    # Changing the value if "apiTrace" to 1 and getting current configuration changes made by pydiabas
    current_config = pydiabas.config(apiTrace=1, traceSize=4096)
    print(current_config) # prints {"apitrace: 1, "tracesize": 4096}
```

##### Job
Jobs are used for the actual communication.
They have to be addressed to a specific ECU and must pass the jobs name as argument.
Further data can be send as parameters to the ECU. Some ECUs can apply a result filter to return only the results with the names listet in this filter. If a result filter is set for ECUs not supporting this function, all results will be returned instead.
If the size of the data returned by the ECU is expected to be very large and only a small part is actually needed, the parameter *fetchall* can be set to *False* to skip the retrieval of all result values after job execution. The values must then be fetched manually using the functionality coming with the returned *Result* object. 
Calling the *job()* method will block the program until the results have been returned from the ECU and returns these as a *Result* object.
If the job fails, a *StateError* will be raised.

```py
# Executing a job
from pydiabas import PyDIABAS

with PyDIABAS() as pydiabas:

    # Executing a job on ECU "TMODE" which is possible even if no car or OBD cable is connected to the computer
    # The job "_JOBS" gets the names of all jobs available in the ECU
    result = pydiabas.job(ecu="TMODE", job="_JOBS")
```

##### Direct access to the *EDIABAS* instance
To enable direct access to the *EDIABAS* object, the property *ediabas* can be used. This might become necessary to perform very specific jobs or to get detailed information about the current state or error codes and description of the **EDIABAS** system.

```py
# Direct access to the EDIABAS object
from pydiabas import PyDIABAS

with PyDIABAS() as pydiabas:

    # Get the EDIABAS object
    ediabas = pydiabas.ediabas

    # Get current error description
    print(ediabas.errorText()) # prints: NO_ERROR in this case
```

##### Functions and Properties
> **PyDIABAS()** - > None
> 
> Creates a new PyDIABAS() instance without starting an **EDIABAS** session.
> ```
> >>> pydiabas = PyDIABAS()
> ```

> **start()** - > None
>
> Starts the **EDIABAS** server if necessary and sets up a new session. 
>
>If this operation is not successful a *StateError* will be raised. If *start()* is called after a configuration changes has been made using this PyDIABAS object, these configurations will automatically be set again after starting the new session.
> 
> **Raises** a *StateError* if failed.
> ```
> >>> pydiabas.start()
> ```

> **end()** -> None
>
> Current **EDIABAS** session is stopped and used resources will be released.
> ```
> >>> pydiabas.end()
> ```

> **reset()** -> None
>
> Has the same effect as calling *end()* and *start()* consecutive.
> ```
> >>> pydiabas.reset()
> ```

> **ready** -> *bool*
>
> Checks if the **EDIABAS** session has been started and the previous job (if any) ran successful.
>
> **Returns** *True* if **EDIABAS** is running properly.
> ```
> >>> pydiabas.ready
> True
>```

> **ediabas** -> *EDIABAS*
>
> Allows access to the *EDIABAS* object (in this case not the **EDIABAS** system installed on your pc but the python *EDIABAS* object being part og the **ediabas** sub-module of **pydiabas** currently used by this *PyDIABAS* object).  
>
> **Returns** the *EDIABAS* instance being used by this PyDIABAS object.
> ```
> >>> pydiabas.ediabas
> <pydiabas.ediabas.ediabas.EDIABAS object at 0x.....>
> ```

> **config([\*\*kwargs])** -> dict
>
> Sets new configuration values (if passed as arguments) and returns applied configuration changes since creating this PyDIABAS instance.
>
> Optional parameter **\*\*kwargs** can be of any type but must match the required type depending on the configuration value to be changed.
> **Returns** currently applied configuration changes as a dict.
> ```
> >>> pydiabas.config(apiTrace=1)
> {"apitrace: 1}
>
> >>> pydiabas.config(traceSize=4096)
> {"apitrace: 1, "tracesize": 4096}
>
> >>> pydiabas.config()
> {"apitrace: 1, "tracesize": 4096}
> ```

> **job(ecu, job [parameters="", result_filter="", fetchall=*True*])** -> Result
>
> This method actually executes communication with the specified ECU. 
>
> The name of the ECU which should run this job and the jobs name must be passed at least.
> Optional job parameters can be send to the ECU either as *str* or *bytes*, using a semicolon as separator between possible multiple parameters. As a second option, the parameters can be passed as list of *str* or *bytes*. The semicolon as separator will be added automatically in this case before transmission to the ECU.
>
> >**Note:**:
> > If parameters are passed as a list, they must be all of the same type. So either as list only containing *str* objects or only containing *bytes* objects. A mix of types is not supported.
>
> A result_filter can be passed as *str* with semicolon as separator or list of *str* similar to the parameters but *bytes* are not supported here.
>
> Parameter **ecu** must be a *str*.  
> Parameter **job** must be a *str*.  
> Optional parameter **parameters** must be *str*, *bytes* or *list*.  
> Optional parameter **result_filter** must be *str* or *list*.  
> Optional parameter **fetchall** must be a *bool*.  
> **Returns** the *Result* object.
> ```
> >>> pydiabas.job("TMODE", "LESE_INTERFACE_TYP")
> <pydiabas.result.Result object at 0x.....>
> ```

#### Result class
Represents the result coming back from the ECU after a job has been executed.
An instance of this class will be returned by the method *job()* after the job has been executed by the ECU.
The class can be used to manually create *Result* objects. Data can be loaded into these object by fetching them, using on of the various fetch methods.

```py
# Getting Result object from a job
from pydiabas import PyDIABAS

with PyDIABAS() as pydiabas:

    # The Result object will be returned after the job has been executed
    result = pydiabas.job(ecu="TMODE", job="INFO")
```

```py
# Manually creating a Result object
from pydiabas import Result

# Creating an empty result object
result = Result()

# Fetch data from EDIABAS
# The returned data will always be the one of the last job executed if not manually changed to a previously saved result set
result.fetchall()
```
##### Data Structure
Data returned by an ECU via **EDIABAS** follows a specific pattern. The *Result* object uses the same structure to be consistent.

Each job execution creates as new result in **EDIABAS** and is only accessible until the next job is executed. There are possibilities to save result data inside **EDIABAS** but they are not discussed here. Refer to the respective documentation if required.

After the job has been finished, aborted or failed by the ECU, there will be some data available to be fetched. This data is called **EDIABAS** result.
The result comprises of one ore more sets, wich finally hold the data as key value pairs.
Set #0 always contains data about the job execution and is called *systemSet* in the *Result* object.
Sets #1-n will contain the data returned by the executed job. In some cases there might be no such data at all. These sets are called *jobSets* in the *Result* object.
Each *Set* contains a ist of *Row* objects which themselves have the attributes *name* and *value*.

Result
- *Set* #0: (*systemSet*)
    - *Row* #0: *name* = VARIANTE, *value* = TMODE
    - *Row* #1: *name* = SAETZE, *value* = 25
    - *Row* #2: *name* = JOBNAME, *value* = _JOBS
    - ...
- *Set* #1: (*jobSet*)
    - *Row* #0: *name* = JOBNAME, *value* = INFO
- *Set* #2: (*jobSet*)
    - *Row* #0: *name* = JOBNAME, *value* = INITIALISIERUNG
- *Set* #3: (*jobSet*)
    - *Row* #0: *name* = JOBNAME, *value* = SETZE_INTERFACE_ZURUECK
    - ... *Sets* can have more than one *Row*
- ...


##### Fetching Data from **EDIABAS**
If the *Result* object has been returned by a **pydiabas** job, data will automatically be fetched and no further action is required before accessing it through the *Result* object.

```py
# Automatically fetch all data together with executing the job
from pydiabas import PyDIABAS

with PyDIABAS() as pydiabas:

    # All data will be fetched automatically and will be available in the Result object
    result = pydiabas.job(ecu="TMODE", job="INFO")
```

Data can be manually fetched if necessary using one of he following methods.
This can be useful if a job is expected to return a lot of data and only a small part of this data is of interest. Inhibiting fetching of all of the data will reduce execution time.
Manual fetching methods will modify the *Result* object in place as well as returning the modified object to use this functions in both of the following ways:
```py
# Manually fetching in the same line together with the job execution
from pydiabas import PyDIABAS

with PyDIABAS() as pydiabas:

    # Automatic fetching of all data is inhibited by the fetchall parameter being set to False
    # Manual fetching is done by calling 'fetchsystemset'
    result = pydiabas.job(ecu="TMODE", job="INFO", fetchall=False).fetchsystemset()
```

```py
# Manually fetching after the Result object has been created modifying the object in place
from pydiabas import PyDIABAS

with PyDIABAS() as pydiabas:

    # Automatic fetching of all data is inhibited by the fetchall parameter being set to False
    # No data will be available
    result = pydiabas.job(ecu="TMODE", job="INFO", fetchall=False)

    # Modifying the Result object in place
    result.fetchsystemset()
```
##### Functions and Properties
For all examples in this chapter we assume the following data to be present in the *Result* object:

result:
- *Set* #0: (*systemSet*)
    - *Row* #0: *name* = VARIANTE, *value* = TMODE
    - *Row* #1: *name* = SAETZE, *value* = 25
    - *Row* #2: *name* = JOBNAME, *value* = _JOBS
- *Set* #1: (*jobSet*)
    - *Row* #0: *name* = JOBNAME, *value* = INFO
    - *Row* #1: *name* = INFO, *value* = "INFOTEXT"
- *Set* #2: (*jobSet*)
    - *Row* #0: *name* = JOBNAME, *value* = INITIALISIERUNG

<br>

```py
# Using python standart functionality with a Result object

# Get number of jobSets
len(result)

# Check if there is a jobSet available
bool(result)

# Get a string representation
str(result)

# Check if there is a Row with "ECU" as name in any jobSet
"ECU" in result

# Get the value of the first Row with name "ECU" in any jobSet
result["ECU"] # Raises a KeyError of no such Row found

# Get the jobSet with the given index
result[0] # Raises an IndexError if out ouf range

# Get a Result object containing only the sliced jobSets and the systemSet
result[0:5:2]

# Iterate trough all jobSets in the Result object
for job_set in result:
    pass
```
> **clear()** -> None
>
> Clears all data from the *Result* object.
> ```
> >>> result.clear()
> >>> bool(result)
> False
>```

> **fetchsystemset()** -> *Result*
>
> Fetches only set #0 from **EDIABAS** containing all system related data.
>
> **Returns** the *Result* object after fetching.
> ```
> >>> result.fetchsystemset()
> <pydiabas.result.Result object at 0x.....>
>```

> **fetchjobsets()** -> *Result*
>
> Fetches all job sets (#1-n) from **EDIABAS**.
>
> **Returns** the *Result* object after fetching.
> ```
> >>> result.fetchjobsets()
> <pydiabas.result.Result object at 0x.....>
>```

> **fetchall()** -> *Result*
>
> Fetches all sets from **EDIABAS**.
>
> **Returns** the *Result* object after fetching.
> ```
> >>> result.fetchall()
> <pydiabas.result.Result object at 0x.....>
>```

> **fetchname(name)** -> *Result*
>
> Fetches all data from the **EDIABAS** job sets (#1-n) where the name of the data matches the given name.
>
> Parameter **name** must be a *str*.  
> **Returns** the *Result* object after fetching.
> ```
> >>> result.fetchname("JOBNAME")
> <pydiabas.result.Result object at 0x.....>
>```

> **fetchnames(names)** -> *Result*
>
> Fetches all data from the **EDIABAS** job sets (#1-n)  where the name of the data matches one of the names in the list of names.
>
> Parameter **name**s must be a list of *str*.  
> **Returns** the *Result* object after fetching.
> ```
> >>> result.fetchnames(["JOBNAME", "INFO"])
> <pydiabas.result.Result object at 0x.....>
>```

> **systemSet** -> *Set*
>
> **EDIABAS** set #0 contains information about system status and job execution.
>
> **Returns** *Set* #0.
> ```
> >>> result.systemSet
> <pydiabas.result.Set object at 0x.....>
>```

> **jobSets** -> *list*[*Set*]
>
> **EDIABAS** set #1-n contain data returned by the executed job.
>
> **Returns** *Sets* #1-n as a *list* of *Sets*. If not such *Sets* are available, an empty *list* is returned.
> ```
> >>> result.jobSets
> [<pydiabas.result.Set object at 0x.....>, <pydiabas.result.Set object at 0x.....>]
>```

> **ecu** -> *str*
>
> **Returns** the name of the ECU as stated in the result.
> ```
> >>> result.ecu
> 'TMODE'
>```

> **jobname** -> *str*
>
> **Returns** the name of the Job as stated in the result.
> ```
> >>> result.jobname
> '_JOBS'
>```

> **jobstatus** -> *str*
>
> **Returns** the status of the job as stated in the result.
> ```
> >>> result.jobstatus
> 'OK'
>```

> **as_dicts()** -> *list*[*dict*]
>
> Generates a *dict* containing all *Rows* as key value pairs for each *Set* in the *Result*. The *systemSet* will always be at index 0 of this list.
>
> **Return**s the data contained in the *Result* as *dict*.
> ```
> >>> result.as_dicts()
> [{'VARIANTE': 'TMODE', 'SAETZE': 25, 'JOBNAME': '_JOBS'}, {'JOBNAME': 'INFO', 'INFO': 'INFOTEXT'}, {'JOBNAME': 'INITIALISIERUNG'}]
>```

> **count(name)** -> *int*
>
> Count the number of *Rows* matching the given name in all *jobSets* of the *Result*.
>
> Parameter **name** must be a *str*.  
> **Returns** the number of occurrences.
> ```
> >>> result.count("JOBNAME")
> 2
>
> >>> result.count("INFO")
> 1
>```

> **index(name, [start=0, end=None])** -> *int*
>
> Looks for the first *jobSet* which contains a *Row* matching the given name.
> First and last *jobSet* to be searched can be defined using the start and end parameter.
> 
> Parameter **name** must be a *str*.  
> Optional parameter **start** must be an *int*.  
> Optional parameter **end** must be an *int*.  
> **Returns** the index of the first *jobSet* containing a *Row* with the given name.  
> **Raises** a ValueError if no *Row* matching the given name has been found.
> ```
> >>> result.index("INFO")
> 1
> 
> >>> result.index("INFO", start=1)
> 1
> 
> >>> result.index("INFO", end=2)
> 1
> 
> >>> result.index("INFO", start=1, end=2)
> 1
> 
> >>> result.index("INFO", end=1)
> ValueError: 'INFO' not in set
> 
> >>> result.index("TEST")
> ValueError: 'TEST' not in set
>```

> **get(name, [default=None])** -> *int* | *str* | *bytes* | *float* | *None*
>
> Gets the value of the first *Row* matching the given name starting from the first *jobSet* to the last.
> Any further occurrences of the name in other *jobSets* will be ignored.
> A default value can be set to be returned in case no *Row* with the given name can be found instead of returning *None*.
>
> Parameter **name** must be a *str*.  
> Optional parameter **default** can be of any type.  
> **Returns** the value if the *Row* or the default value.
> ```
> >>> result.get("JOBNAME")
> '_JOBS'
>
> >>> result.get("SAETZE")
> 25
>
> >>> result.get("INFO")
> 'INFOTEXT'
>
> >>> result.get("TEST")
> None
>
> >>> result.get("TEST", default=0)
> 0
>```

> **get_in(pattern, [default=None])** -> *int* | *str* | *bytes* | *float* | *None*
>
> Gets the value of the first *Row* having the pattern in its name from the first *jobSet* to the last.
> Any further occurrences of the name in other *jobSets* will be ignored.
> A default value can be set to be returned in case no matching *Row* can be found instead of returning *None*.
>
> Parameter **pattern** must be a *str*.  
> Optional parameter **default** can be of any type.  
> **Returns** the value if the *Row* or the default value.
> ```
> >>> result.get_in("JOBNAME")
> '_JOBS'
>
> >>> result.get_in("JOB")
> '_JOBS'
>
> >>> result.get_in("NAME")
> '_JOBS'
>
> >>> result.get_in("JOBNAMES")
> None
>
> >>> result.get_in("JOBNAMES", default=0)
> 0
>```

> **get_fn(fn, [default=None])** -> *int* | *str* | *bytes* | *float* | *None*
>
> Gets the value of the first *Row* where the given function returns True when the *Rows* name is passed as parameter starting from the first *Row* to the last.
> Any further occurrences of the name in other *jobSets* will be ignored.
> A default value can be set to be returned in case no matching *Row* can be found instead of returning *None*.
>
> Parameter **fn** must be a *Callable*.  
> Optional parameter **default** can be of any type.  
> **Returns** the value if the *Row* or the default value.
> ```
> >>> result.get_fn(lambda name: name.startswith("JOB))
> '_JOBS'
>
> >>> result.get_fn(lambda name: len(name) == 4)
> 'INFO'
>
> >>> result.get_fn(lambda name: name == "TEST")
> None
>```


#### Set class
Is part of a *Result's* data structure and represents a set of data coming back from the **EDIABAS** job.  
A *Set* contains *Row* objects for each row in the respective set of the **EDIABAS** data.

```py
# Get a Set from a Result object
from pydiabas import PyDIABAS

with PyDIABAS() as pydiabas:

    # Getting the result from a job
    result = pydiabas.job(ecu="TMODE", job="INFO")

    # Getting the system set from a Result object
    system_set = result.systemSet
```

##### Functions and Properties
For all examples in this chapter we assume the following data to be present in the *Set* object:

system_set:
- *Row* #0: *name* = VARIANTE, *value* = TMODE
- *Row* #1: *name* = SAETZE, *value* = 25
- *Row* #2: *name* = JOBNAME, *value* = _JOBS

<br>

```py
# Using python standart functionality with a Set

# Get number of Rows
len(system_set)

# Check if Set contains at least one Row
bool(system_set)

# Get a string representation
str(system_set)

# Check if there is a Row with "ECU" as name
"ECU" in system_set

# Get the value of the Row with name "ECU" or raises a KeyError
system_set["ECU"]

# Get the Row at index 0 or raises and IndexError
system_set[0]

# Get a Set object containing only the sliced Rows
system_set[0:5:2]

# Iterate trough all Rows in the Set
for row in system_set:
    pass
```

> **all** -> *list*[*Row*]
>
> Generates a *list* containing all *Rows* in this *Set*.
>
> **Returns** a *list* containing all *Rows*.
> ```
> >>> system_set.all
> [Row(name='VARIANTE', value='TMODE'), Row(name='SAETZE', value=25), Row(name='JOBNAME', value='_JOBS')]
>```

> **as_dict()** -> *dict*
>
> Generates a *dict* containing all *Rows* of this *Set* with the *Rows* name as key. As there are no name duplicates in all *Rows* of a *Set*, not data will be lost.
>
> **Returns** all *Rows* as a *dict*.
> ```
> >>> system_set.as_dict()
> {'VARIANTE': 'TMODE', 'SAETZE': 25, 'JOBNAME': '_JOBS'}
>```

> **index(name, [start=0, end=None])** -> *int*
>
> Looks for the first *Row* matching the given name.
> First and last *Row* to be searched can be defined using the start and end parameter.
> 
> Parameter **name** must be a *str*.  
> Optional parameter **start** must be an *int*.  
> Optional parameter **end** must be an *int*.  
> **Returns** the index of the first *Row* with the given name.  
> **Raises** a ValueError if no *Row* matching the given name has been found.
> ```
> >>> system_set.index("SAETZE")
> 1
> 
> >>> system_set.index("SAETZE", start=1)
> 1
> 
> >>> system_set.index("SAETZE", end=2)
> 1
> 
> >>> system_set.index("SAETZE", start=1, end=2)
> 1
> 
> >>> system_set.index("SAETZE", end=1)
> ValueError: 'SAETZE' not in set
> 
> >>> system_set.index("TEST")
> ValueError: 'TEST' not in set
>```

> **keys()** -> *list*
>
> **Returns** a *list* containing the name of all *Rows* in this *Set*.
> ```
> >>> system_set.keys()
> ['VARIANTE', 'SAETZE', '_JOBS']
>```

> **values()** -> *list*
>
> **Returns** a *list* containing the values of all *Rows* in this *Set*.
> ```
> >>> system_set.values()
> ['TMODE', 25, '_JOBS']
>```

> **items()** -> *list*[*tuple*]
>
> **Returns** a *list* containing *tuples* (name, value) for all *Rows* in this *Set*.
> ```
> >>> system_set.items()
> [('VARIANTE', 'TMODE'), ('SAETZE', 25), ('JOBNAME', '_JOBS')]
>```

> **get(name, [default=None])** -> *int* | *str* | *bytes* | *float* | *None*
>
> Gets the value of the *Row* matching the given name starting from the first *Row* to the last.
> A default value can be set to be returned in case no *Row* with the given name can be found instead of returning *None*.
>
> Parameter **name** must be a *str*.  
> Optional parameter **default** can be of any type.  
> **Returns** the value if the *Row* or the default value.
> ```
> >>> system_set.get("JOBNAME")
> '_JOBS'
>
> >>> system_set.get("SAETZE")
> 25
>
> >>> system_set.get("TEST")
> None
>
> >>> system_set.get("TEST", default=0)
> 0
>```

> **get_in(pattern, [default=None])** -> *int* | *str* | *bytes* | *float* | *None*
>
> Gets the value of the first *Row* having the pattern in its name from the first *Row* to the last.
> A default value can be set to be returned in case no matching *Row* can be found instead of returning *None*.
>
> Parameter **pattern** must be a *str*.  
> Optional parameter **default** can be of any type.  
> **Returns** the value if the *Row* or the default value.
> ```
> >>> system_set.get_in("JOBNAME")
> '_JOBS'
>
> >>> system_set.get_in("JOB")
> '_JOBS'
>
> >>> system_set.get_in("NAME")
> '_JOBS'
>
> >>> system_set.get_in("JOBNAMES")
> None
>
> >>> system_set.get_in("JOBNAMES", default=0)
> 0
>```

> **get_fn(fn, [default=None])** -> *int* | *str* | *bytes* | *float* | *None*
>
> Gets the value of the first *Row* where the given function returns True when the *Rows* name is passed as parameter starting from the first *Row* to the last.
> A default value can be set to be returned in case no matching *Row* can be found instead of returning *None*.
>
> Parameter **fn** must be a *Callable*.  
> Optional parameter **default** can be of any type.  
> **Returns** the value if the *Row* or the default value.
> ```
> >>> system_set.get_fn(lambda name: name.startswith("JOB))
> '_JOBS'
>
> >>> system_set.get_fn(lambda name: len(name) == 6)
> 25
>
> >>> system_set.get_fn(lambda name: name == "TEST")
> None
>```


#### Row class
Represents a row in an EDIABAS result set. Name and value of the Row can be accessed via the respective attributes (Row.name and Row.value).

If we have a row with name="SAETZE" and value=25 we can use the Row object as follows
```
>>> row.name
'SAETZE'

>>> row.value
25
```


### ediabas module
This module is used by **pydiabas** behind the scenes. Most of the functionality is being a wrapper around the **EDIABAS** API to provide a pythonic way of accessing it.

As using this module is not necessary for most of the users, a detailed documentation is not provided at this place. Class and methods are documented in the respective source code file.

A detailed description about handling the **EDIABAS** API can be found in the `/Doku` folder of your **EDIABAS** installation. 

The *EDIABAS* class provides methods with the same names and effects as the functions available in the **EDIABAS** API with some general differences.
As the **EDIABAS** API uses the 'C-style' of function signatures by providing a reference to a variable in which the return value of the job should be stored and returning the status of the job as return value of the function like:
```C
// C-style function signature used in EDIABAS

int value;

// Value will be set to the referenced variable trough side-effect of the function
// Return value of the function gives information about the job status
bool job_sts = arbitrary_ediabas_function(&value);
```
This is translated in to the 'python-style' of function signatures as follows:
```py
# Python-style function signature used in ediabas

try:
    # Return value of the function is the values asked for
    value = arbitrary_ediabas_function()
except JobFailedError:
    # A JobFailedError exception is raised if the job fails
```
Besides these changes, the **ediabas** module works the same as the **EDIABAS** API.
A details description of **EDIABAS** can be found in the `/Doku` folder of your **EDIABAS** installation. Details about the **ediabas** module can be found in the source code file itself.

#### EDIABAS class
Class representing the **EDIABAS** API. Can be used in very much the same way as the **EDIABAS** API itself.

#### statics
Contains all static constants used by this **ediabas** module

#### utils
Provides helper functions for a more comfortable and clean way of interaction with the **ediabas** module.

> **getResult(ediabas, name, [set=1])** -> *str* | *bytes* | *int* | *float* | *None*
> 
> Accesses the **EDIABAS** result and searches the given result set (defaults to 1, as this is the first set containing data returned by the job) data with the given name.  
> Checks the format of the data, gets the data and casts it to the most appropriate python data type. If no data with the name is found, *None* will be returned.
>
> Parameter **ediabas** must be an *EDIABAS* instance.  
> Parameter **name** must be a *str*.  
> Optional parameter **set** must be an *int*.  
> **Returns** the value of the data or *None*.

#### api32
Is just a wrapper around the `api32.dll` library, loading this library and extracting all the functions.


### ecu module
This module facilitates the execution of tasks that are frequently used when working with ECUs. There are some generic functions that can be used on all ECUs in this class and functions more specific to a single ECU which can be found in the respective class. For now, only specific tasks for MSD80 are implemented.  
A *PyDIABAS* instance need to be set up separately to provide connection to the ECU via **EDIABAS**.

```py
# Get available jobs by using the ECU class
from pydiabas import PyDIABAS
from pydiabas.ecu import ECU

# Create a new ECU object with its name set to TMODE
tmode = ECU("TMODE")

# Start pydiabas communication
with PyDIABAS() as pydiabas:

    # Get all available jobs
    # A PyDIABAS object must always be passed to enable communication
    jobs = tmode.get_jobs(pydiabas)

# Print all jobs
for job in jobs:
    print(job)
```

#### ECU class
Offers generic functions that can be used on all ECUs. 

##### Initialization
To be able to use the *ECU* object, the name of the ECU to communicate with must be set first. This can either be done by passing the name as argument when creating the object or it can be set (or even changed) later via the *name* instance variable.
```py
# Setting the name of the ECU
from pydiabas.ecu import ECU

# Passing the name as arguments when creating the object
tmode = ECU("TMODE")

# Settings the name after creating the object
frm = ECU()
frm.name = "FRM"
```
```py
# Executing a job in an ECU
from pydiabas import PyDIABAS
from pydiabas.ecu import ECU

# Create an ECU object
tmode = ECU("TMODE")

# Start a PyDIABAS session
with PyDIABAS() as pydiabas:

    # Jobs can be executed using the ECU object in the same way as using the PyDIABAS instance by just changing the ecu parameter with the pydiabas parameter.
    tmode.job(pydiabas, "LESE_INTERFACE_TYP")
```

##### Functions
> **job(_pydiabas_, job [parameters="", result_filter="", fetchall=*True*])** -> Result
>
> This method actually executes communication with the ECU. 
>
>This method is just a utility to be able to execute jobs directly on the ECU object instead of using a PyDIABAS object to do so. It just calls the *job()* method of the given PyDIABAS instance with the parameter **ecu** set to the name ob this ECU object.  
> Consult the documentation of the *PyDIABAS.job()* method for further details.
>
> Parameter **pydiabas** must be a *PyDIABAS* object.  
> Parameter **job** must be a *str*.  
> Optional parameter **parameters** must be *str*, *bytes* or *list*.  
> Optional parameter **result_filter** must be *str* or *list*.  
> Optional parameter **fetchall** must be a *bool*.  
> **Returns** the *Result* object.
> ```
> >>> ecu.job(pydiabas, "LESE_INTERFACE_TYP")
> <pydiabas.result.Result object at 0x.....>
> ```

> **get_jobs(_pydiabas_, [details=*True*, verbose=*False*])** -> *dict*[*dict*]
>
> Gets the names of all available jobs in the ECU and adds them as keys to a *dict* with an empty *dict* set as the value. If details is set to *True* these empty *dicts* will be filled with additional information about the job if available in the ECU.  
> Settings *verbose* to *True* will print some information concerning the execution progress to the terminal as extracting a lot of data from the an ECU may take a few minutes.
> 
> Parameter **pydiabas** must be a *PyDIABAS* instance.  
> Optional parameter **details** must be a *bool*.  
> Optional parameter **verbose** must be a *bool*.  
> **Returns** a *dict* containing information about the available jobs.
> ```
> >>> ecu.get_jobs(pydiabas, details=False)
> {'INFO': {}, 'INITIALISIERUNG': {}, 'SETZE_INTERFACE_ZURUECK': {}, ...}
> 
> >>> ecu.get_jobs(pydiabas, details=True)
> {
>     'INFO': {
>         'comments': ['Information SGBD'],
>         'arguments': [],
>         'results': [
>             {
>             'name': 'ECU',
>             'type': 'string',
>             'comments': ['Steuergerät im Klartext']
>             }, {
>             'name': 'ORIGIN',
>             'type': 'string',
>             'comments': ['Steuergeräte-Verantwortlicher']
>             }, {
>             'name': 'REVISION',
>             'type': 'string',
>             'comments': ['Versions-Nummer']
>             }, ...
>         ]
>     }, ...
> }
> ```

> **get_job_details(_pydiabas_, job)** -> *dict*
>
> Gets additional information about the job if available in the ECU like:
> - Job comments
> - Job parameters
> - Job results
> 
> Parameter **pydiabas** must be a *PyDIABAS* instance.  
> Parameter **job** must be a *str*.    
> **Returns** a *dict* containing information about the job.
> ```
> >>> ecu.get_jobs(pydiabas, details=False)
> {
>     'comments': ['Information SGBD'],
>     'arguments': [],
>     'results': [
>         {
>         'name': 'ECU',
>         'type': 'string',
>         'comments': ['Steuergerät im Klartext']
>         }, {
>        'name': 'ORIGIN',
>         'type': 'string',
>         'comments': ['Steuergeräte-Verantwortlicher']
>         }, {
>         'name': 'REVISION',
>         'type': 'string',
>         'comments': ['Versions-Nummer']
>         }, ...
>     ]
> }
> ```

> **get_tables(_pydiabas_, [details=*True*, verbose=*False*])** -> *dict*[*dict*]
>
> Gets the names of all available tables in the ECU and adds them as keys to a *dict* with an empty *dict* set as the value. If details is set to *True* these empty *dicts* will be filled with table header and body data.  
> Settings *verbose* to *True* will print some information concerning the execution progress to the terminal as extracting a lot of data from the an ECU may take a few minutes.
> 
> Parameter **pydiabas** must be a *PyDIABAS* instance.  
> Optional parameter **details** must be a *bool*.  
> Optional parameter **verbose** must be a *bool*.  
> **Returns** a *dict* containing information about the available tables.
> ```
> >>> ecu.get_tables(pydiabas, details=False)
> {'KONZEPT_TABELLE': {}, 'JOBRESULT': {}, 'LIEFERANTEN': {}, ...}
> 
> >>> ecu.get_tables(pydiabas, details=True)
> {
>     'KONZEPT_TABELLE': {
>         'header': ['NR', 'KONZEPT_TEXT'],
>         'body': [
>             ['0x10', 'D-CAN'],
>             ['0x0F', 'BMW-FAST'],
>             ['0x0D', 'KWP2000*'],
>             ['0x0C', 'KWP2000'],
>             ['0x06', 'DS2']
>         ]
>     }, 
>     'JOBRESULT': {
>         'header': ['SB', 'STATUS_TEXT'], 
>         'body': [
>             ['0x10', 'ERROR_ECU_GENERAL_REJECT'],
>             ['0x11', 'ERROR_ECU_SERVICE_NOT_SUPPORTED'],
>             ...
>         ]
>     }, 
>     ...
> }
> ```

> **get_table_details(_pydiabas_, table)** -> *dict*
>
> Gets table header and body data.
> 
> Parameter **pydiabas** must be a *PyDIABAS* instance.  
> Optional parameter **table** must be a *str*.  
> **Returns** a *dict* containing header and body data of the table.
> ```
> >>> ecu.get_table_details(pydiabas, "KONZEPT_TABELLE")
> {
>     'header': ['NR', 'KONZEPT_TEXT'],
>     'body': [
>         ['0x10', 'D-CAN'],
>         ['0x0F', 'BMW-FAST'],
>         ['0x0D', 'KWP2000*'],
>         ['0x0C', 'KWP2000'],
>         ['0x06', 'DS2']
>     ]
> }
> ```

#### MSD80 class
Inherits from the *ECU* class and provides some additional functions to be used specifically on MSD80 ECUs.
As MSD80 uses different ways to read out data from the engine which are not quite self-explanatory this class offers a easy way to retrieve data from the MSD80 in the most efficient and quick way. Especially if you need to read the same values over and over again, this class offers great help to do so.

##### Reading data from the MSD80
The available readings can be found in the table *MESSWERTETAB*. This table can be extracted using the function *get_table_details()*. Column "ID" contains the hex values used in the list of values to be passed to the reading functions. Column "RESULTNAME" shows the name of Row in the Result object containing the value of the reading and column "INFO" provides some information about the reading. Its necessary to check the value of column "NAME" to check if an additional table lookup is required by the ECU to convert the raw value before returning the result. This lookup and conversion is done automatically by the ECU, so no additional job is needed to be executed by the user but please check the section below to avoid missing or invalid data being returned by the ECU.

MSD80 uses a so called *MESSWERTBLOCK* to read out data from the ECU.  
When a set of data is requested from the ECU, a *MESSWERTBLOCK* is created which consists of the readings requested like `["RPM", "TEMP", "LAMBDA"]`.  
The creation of the new block takes about 50ms before the readings can be retrieved.  
If the sames readings (in the same order!) are requested for a second time, the existing *MESSWERTBLOCK* can be used again, saving about 50ms as the *MESSWERTBLOCK* does not need to be created and speeding up the retrieval of the readings by the factor of 3! This speeds up retrieval of 20 readings from 280ms to 100ms!  
As soon as different readings are requested (even if its only the order of the readings), the existing *MESSWERTBLOCK* will be overwritten.

###### Data requiring a table lookup for conversion
Some readings from the ECU will be translated using a table in the ECU to return a human readable format via **EDIABAS** like the combustion mode of the engines which will be converted from an simple integer to a string like "STRATIFIED".  
Somehow this lookup crashes when re-reading an existing *MESSWERTBLOCK*. The reading will be returned by **EDIABAS** in the raw format (int in the case of combustion mode) and **all further readings requested will contain invalid or missing data!**  
To avoid this problem, all requested readings except the last **must not** be values that need a conversion trough a table lookup. Readings needing a conversion can be identifies by heaving a `-` set in the column *NAME* in the table *MESSWERTETAB* which contains a list of all possible readings that can be retrieved from your MSD80. The last requested reading may be one that needs a conversion as the raw value will be returned even if the lookup crashes and there are no further readings required which will be impaired by the crashed lookup.  
Maybe this bug ist just present in some firmware versions of MSD80.  
If more that one reading needing a conversion is required the slower *read()* method avoiding the re-use of a *MESSWERTBLOCK* is to be used!


##### Initialization
As the name does not need to be set manually, no parameters musst be passed or set manually.
```py
# Creating an MSD80 object
from pydiabas.ecu import MSD80

msd80 = MSD80()
```

##### Functions
> **set_block(*pydiabas*, values)** -> *Result* | *None*
>
> A new *MESSWERTEBLOCK* will be created and readings will be returned.  
> An existing block will be **overwritten**.  
> Thereafter retrieving the readings from this block is much quicker and can be done using the function *read_block()*. Ony the last item in the *list* of values may be one that needs a conversion via a table lookup, otherwise creating and reading the block will fail.  
> If creating the block fails a *BlockCreationError* exception is raised.
> 
> Parameter **pydiabas** must be a *PyDIABAS* instance.  
> Parameter **values** must be a *list* containing *str*.  
> **Returns** a *Result* object if successful or *None*.  
> **Raises** a *BlockCreationError*.
> ```
> >>> ecu.set_block(pydiabas, ["0x5A30", "0x5A31"])
> <pydiabas.result.Result object at 0x.....>
> ```

> **read_block(*pydiabas*)** -> *Result* | *None*
>
> An existing *MESSWERTEBLOCK* is used to retrieve the reading from the ECU.  
> Before being able to use this function a block must be created using the function *set_block()*.  
> All readings in the block will be retrieved so not list of values needs to be passed to when calling this function.
> 
> Parameter **pydiabas** must be a *PyDIABAS* instance.   
> **Returns** a *Result* object if successful or *None*.  
> **Raises** a *BlockReadError*.  
> **Raises** a *BlockCreationError*.
> ```
> >>> ecu.read_block(pydiabas)
> <pydiabas.result.Result object at 0x.....>
> ```

> **read(*pydiabas*, values)** -> *Result* | *None*
>
> The requested readings will be retrieved from the ECU.  
> An existing block will be **overwritten**.  
> This way of getting the readings is relatively slow but there is no limitation concerning the position or numbers of readings which need a conversion via a table lookup.  
> If retrieving the reading fails, a *ValueReadError* will be raised.
> 
> Parameter **pydiabas** must be a *PyDIABAS* instance.  
> Parameter **values** must be a *list* containing *str*.  
> **Returns** a *Result* object if successful or *None*.  
> **Raises** a *ValueReadError*.
> ```
> >>> ecu.read(pydiabas, ["0x5A30", "0x5A31"])
> <pydiabas.result.Result object at 0x.....>
> ```

> **read_again(*pydiabas*)** -> *Result* | *None*
>
> The most recent successful function used to retrieve reading will be called again with the same parameters. 
> Calling this function may **overwrite** an existing block.
> If retrieving the reading fails, a *ValueReadError* will be raised.
> 
> Parameter **pydiabas** must be a *PyDIABAS* instance.  
> **Returns** a *Result* object if successful or *None*.  
> **Raises** a *ValueReadError*.
> ```
> >>> ecu.read_again(pydiabas)
> <pydiabas.result.Result object at 0x.....>
> ```

> **read_auto(*pydiabas*, values)** -> *Result* | *None*
>
> Automatically chooses the fastest way of retrieving the readings.  
> If the given values match the current block, *read_block()* will be used first. If it fails, a new block is being created by calling *set_block()*. If this fails too, the *read()* function will be used as a last resort.  
> The *read_again()* function will be set and can be used afterwards as usual.  
> If retrieving the reading fails, a *ValueReadError* will be raised.
> 
> Parameter **pydiabas** must be a *PyDIABAS* instance.  
> Parameter **values** must be a *list* containing *str*.   
> **Returns** a *Result* object if successful or *None*.  
> **Raises** a *ValueReadError*.
> ```
> >>> ecu.read_auto(pydiabas, ["0x5A30", "0x5A31"])
> <pydiabas.result.Result object at 0x.....>
> ```


### simulation module
This module provides features to simulate job execution. Its designed to be used for development purpose only, where the *SimulatedPyDIABAS* class can be used to provide job data without necessarily being connected to a car.  
In addition there is the *CapturedJob* class to create objects containing data of previously executed jobs that will be used for the simulation and the *capture_jobs()* decorator, wich makes it possible to capture job data from executed jobs.


```py
# Capturing a job and saving it as *.jobs file
from pydiabas import PyDIABAS
from pydiabas.simulation import capture_job, save_jobs_to_file

# Use a normal PyDIABAS instance to capture a job
with PyDIABAS() as pydiabas:

    # Captured jobs will be stored in this list
    jobs = []

    # Apply the decorator to the job method
    # The second argument (jobs) is the list where the jobs will be stored in
    pydiabas.job = capture_job(pydiabas.job, jobs)

    # Execute and capture a job
    pydiabas.job("TMODE", "INFO")

    # Save captured jobs to a file in the CWD
    save_jobs_to_file(jobs)

# A *.jobs file will be created in the current working directory each time you run this script
```
```py
# Use a SimulatedPyDIABAS instance to simulate the captured job
from pydiabas.simulation import SimulatedPyDIABAS

# The previously saved *.jobs file will automatically be loaded from current working directory
with SimulatedPyDIABAS() as simulated_pydiabas:

    # Load the jobs to simulate. *.jobs files from the CWD will be loaded
    simulated_pydiabas.load_jobs()

    # Simulate a job
    simulated_result = simulated_pydiabas.job("TMODE", "INFO")

print(simulated_result)
"""
============== PyDIABAS Result ==============
-------------- systemSet       --------------
__SIMULATED__                 : YES
OBJECT                        : tmode
SAETZE                        : 1
JOBNAME                       : INFO
VARIANTE                      : TMODE
JOBSTATUS                     :
...
-------------- jobSet #0       --------------
ECU                           : TMODE
...
============== END             ==============
"""
```

#### SimulatedPyDIABAS class
This class is derived from the *PyDIABAS* class with a modified *job()* method and some additional features to provide simulated job results.

##### Limitations
> __Warning:__ The *EDIABAS* instance associated with the *PyDIABAS* object is not simulated!

##### Initialization
There are multiple ways to provide the *SimulatedPyDIABAS* instance with simulation data.
- Loading job data from `*.jobs` files by specifying the path to be used (dir or file).
- Adding captured jobs.

```py
# Adding jobs as list or tuple ob CapturedJob objects or one single CapturesJob object
from pydiabas.simulation import SimulatedPyDIABAS

# This line is just for demonstration to keep this example script short
jobs = CapturedJob(... )

with SimulatedPyDIABAS(captured_jobs=jobs) as simulated_pydiabas:
    pass
```
```py
# Load *.jobs files
from pydiabas.simulation import SimulatedPyDIABAS

# Create an instance without reading any *.jobs files
with SimulatedPyDIABAS() as simulated_pydiabas:
    
    # Load all *.jobs files from the given directory, CWD by default
    simulated_pydiabas.load_jobfiles()
```

##### Simulating jobs
To be able to simulate jobs, the *SimulatedPyDIABAS* object needs data about the jobs to be simulated.
This can either be done by capturing data from executed jobs and make it available for the simulation or by implementing a dedicated function that takes the arguments passed to the *job()* method as keyword arguments and returns a *Result* object or *None* if the not being able to simulate the called job. 

###### Captured jobs
The data of captured jobs comprises the arguments used to execute the job and the resulting *Result* object, that came back from the executed job. This data will be encapsulated in a *CapturedJob* object.
To do all this, the *capture_job* decorator will be used to capture this data while executing jobs using *PyDIABAS*
```py
# Capturing a job by using the decorator
from pydiabas import PyDIABAS
from pydiabas.simulation import SimulatedPyDIABAS, capture_job, save_jobs_to_file

# Captured jobs will be stored in this list
jobs = []

# Use a normal PyDIABAS instance to capture a job
pydiabas = PyDIABAS()

# Apply the decorator to the job method
# The second argument (jobs) is the list where the jobs will be stored in
pydiabas.job = capture_job(pydiabas.job, jobs)

# Jobs can be executed thereafter

# to be continued ...
```
The *list* if *CapturedJob* objects can than be used to simulate jobs.
This *list* or even single *CapturedJob* objects can be added to the *SimulatedPyDIABAS* object by using the *add_jobs()* method.
```py
# ... continuation

# Create a simulation object
simulated_pydiabas = SimulatedPyDIABAS()

# Add a single job to the simulation
simulated_pydiabas.add_jobs(jobs[0])

# Add a list or tuple of jobs to the simulation
simulated_pydiabas.add_jobs(jobs)

# Simulation is now ready to be used by calling the job() method

# to be continued ...
```
Job data can even be saved as a file for later use by using the *save_jobs_to_file()* function and be added py reading the file using the *load_jobs()* method thereafter.
```py
# ... continuation

# Save jobs to file in the CWD and remember filename
filename = save_jobs_to_file(jobs)

# Load jobs from the created file
simulated_pydiabas.load_jobs(filename)

# to be continued ...
```

###### Dedicated job simulation function
If the job can not be simulated by capturing it once and just reproduce the *Result* each time the job is called, a dedicated simulation function can be implemented. This might be necessary if the job depends on a internal state like a job that returns different data each time it is called.
The function must accept the job arguments as keyword arguments and return a *Result* if able to simulate the job object or *None* if not.
To ease the creation of the *Result* object a *base_result()* method is available to create a *Result* containing all basic values.
To implement a dedicated function, the *custom_job()* method shall be overwritten.
```py
# ... continuation

# Define a new simulation class inheriting from SimulatedPyDIABAS
class DedicatedSimulation(SimulatedPyDIABAS):
    
    # Implementing a dedicated job simulation function by overwriting the custom_job method
    def custom_job(self, **kwargs):

        # Check if the correct ecu and job has been called
        if kwargs["ecu"] == "SIM" and kwargs["job"] == "TEST":

            # Get the base result
            result = self.base_result(ecu="SIM", job="TEST")

            # Add data to the jobSet of the result
            result._jobSets = [
                Set([
                    Row("DATA", 100)
                ])
            ]

            # Add additional data to the first jobSet
            result._jobSets[0]._rows.append(
                Row("STATUS", "ON")
            )

            # Return the result object
            return result

        # This code is not necessary but added for clarification
        else:

            # Return None if unable to simulate the job
            return None

# Try the simulation
dedicated_simulation = DedicatedSimulation()
dedicated_simulation.job("SIM", "TEST")
``` 

##### Functions and Properties
> **SimulatedPyDIABAS()** - > None
> 
> Creates a new SimulatedPyDIABAS() instance loading any jobs.
> ```
> >>> simulated_pydiabas = SimulatedPyDIABAS()
> ```

> **start()** - > None
>
> Does nothing in this simulation.
> ```
> >>> simulated_pydiabas.start()
> ```

> **end()** -> None
>
> Does nothing in this simulation.
> ```
> >>> simulated_pydiabas.end()
> ```

> **reset()** -> None
>
> Does nothing in this simulation.
> ```
> >>> simulated_pydiabas.reset()
> ```

> **ready** -> *bool*
>
> **Returns** *True* if jobs are available for simulation.
> ```
> >>> simulated_pydiabas.ready
> False
>```

> **ediabas** -> *EDIABAS*
>
> Allows access to the *EDIABAS* object
> > __Warning:__: EDIABAS is NOT simulated!
>
> **Returns** the *EDIABAS* instance being used by this PyDIABAS object.
> ```
> >>> simulated_pydiabas.ediabas
> <pydiabas.ediabas.ediabas.EDIABAS object at 0x.....>
> ```

> **config([\*\*kwargs])** -> dict
>
> As *EDIABAS* is not used by the *SimulatedPyDIABAS*, configuring of *EDIABAS* is not implemented in this class. To indicate this, a dummy dict is returned in stead of the current *EDIABAS* configuration.
> **Returns** a dummy dict.
> ```
> >>> simulated_pydiabas.config(apiTrace=1)
> {"simulated": True}
>
> >>> simulated_pydiabas.config(traceSize=4096)
> {"simulated": True}
>
> >>> simulated_pydiabas.config()
> {"simulated": True}
> ```

> **job(ecu, job, [parameters="", result_filter="", fetchall=*True*])** -> Result
>
> Simulates the execution of a job and returns the simulated *Result*.
> In a first step, the jobs added to the instance will be searched for matching data. If not matching, the *custom_job()* method as called as second step.
> If both steps do not return a simulated *Result* as *StateError* is raised.
>
> Parameter **ecu** must be a *str*.  
> Parameter **job** must be a *str*.  
> Optional parameter **parameters** must be *str*, *bytes* or *list*.  
> Optional parameter **result_filter** must be *str* or *list*.  
> Optional parameter **fetchall** must be a *bool*, but is actually ignored by the simulation.  
> **Returns** the *Result* object.
> ```
> >>> simulated_pydiabas.job("TMODE", "LESE_INTERFACE_TYP")
> <pydiabas.result.Result object at 0x.....>
> ``` 

> **custom_job(ecu, job, [parameters="", result_filter="", fetchall=*True*])** -> Result
>
> Does nothing by itself. Can be implemented to simulate jobs that can't be simulated by captured jobs.
> This can be useful if the simulated job has an internal state which influences the returned *Result*.
> This method is not designed to be called manually. It will be called by the *job()* method if no captured job matches the job that needs to be simulated. See the section [simulating jobs](#simulating-jobs) above for more details.
>
> Parameter **ecu** must be a *str*.  
> Parameter **job** must be a *str*.  
> Optional parameter **parameters** must be *str*, *bytes* or *list*.  
> Optional parameter **result_filter** must be *str* or *list*.  
> Optional parameter **fetchall** must be a *bool*, but is actually ignored by the simulation.  
> **Returns** the *Result* object.

> **base_result(ecu, job, [n_sets=1])** -> Result
>
> Creates a *Result* object containing all basic information that should be available in any simulated *Result*. By specifying *ECU* name and job name, the values in the *Result* can be set accordingly. n_sets can be changed to reflect the number of *jobSets* available in the simulated *Result*, these Sets will be empty.
>
> Parameter **ecu** must be a *str*.  
> Parameter **job** must be a *str*.  
> Optional parameter **n_sets** must be *int.  
> **Returns** the *Result* object.
> ```
> >>> simulated_pydiabas.base_result("ECU_NAME", "JOB_NAME")
> <pydiabas.result.Result object at 0x.....>
> ``` 

> **add_jobs(jobs)** -> None
>
> Adds the given *CapturedJob* object to the available jobs for simulation. These objects can be generated using the *pydiabas.simulation.capture_job* decorator.
> More details about job capturing can be found in the section [capture_jobs decorator](#capture_jobs-decorator).
>
> Parameter **jobs** must be a *CapturedJob* object or a *list* or *tuple* containing only *CapturedJob* objects.
> ```
> >>> simulated_pydiabas.add_jobs(captured_jobs)
> ``` 

> **load_jobs([path=""])** -> None
>
> Loads job data from the given path. If **path** points to a single file, this file is loaded. If **path** points to a directory, all `*.jobs` files in this directory will be loaded.
> Mor details concerning generating `*.jobs` files can be found in the sections [save_jobs_to_file function](#save_jobs_to_file-function) and [capture_jobs decorator](#capture_jobs-decorator).
>
> Optional parameter **path** must be a *str* or *os.PathLike* object.
> ```
> >>> simulated_pydiabas.load_jobs()
> ``` 

#### CapturedJob class
This class can be used to store captured job data for subsequent simulations. I provides the container to store the job data and a method to check if the captured job matches a job to be simulated by comparing the arguments passed to the job with the data stored in the *CapturedJob* object.
This class is not meant to be used to create *CapturedJob* objects manually but by using the *capture_jobs()* decorator described below.

##### Initialization
To create a new *CapturedJob* object, the following data has to be passed to the constructor.

> **init(ecu, job, result, [parameters="", result_filter=""])** -> None
>
> Creates a new *CapturedJob* object with the given data. **parameters** and **result_filter* will be set to an empty *str* of not given.
>
> Parameter **ecu** must be a *str*.  
> Parameter **job** must be *str* or *bytes*.  
> Parameter **result** must be a *Result* object.  
> Optional parameter **parameters** must be *str*, *bytes* or *list*.  
> Optional parameter **result_filter** must be *str* or *list*.  
> ```
> >>> captured_job = CapturedJob("FRM", "INFO", result)
> ```

##### Functions
> **check(ecu, job, [parameters="", result_filter=""])** -> None | Result
>
> Checks if the given arguments match the data stored in the object and returns either the *Result* object if the arguments math, or *None* if they don't.
>
> Parameter **ecu** must be a *str*.  
> Parameter **job** must be *str* or *bytes*.  
> Parameter **result** must be a *Result* object.  
> Optional parameter **parameters** must be *str*, *bytes* or *list*.  
> Optional parameter **result_filter** must be *str* or *list*.  
> **Returns** the *Result* object or *None*. 
> ```
> >>> result = captured_job.check("FRM", "INFO")
> ```


#### capture_jobs decorator
This decorator can be used to add job data capturing to the *job()* method of a *PyDIABAS* instance.
The original *job()* method must be given as first arguments and a list to store the captured job data to must be passed as second argument. Each time a job is captured, a new *CapturedJob* object will be appended to the given list, containing the data of this job.
The decorated *job()* method can be used without any restrictions or modifications.
```py
# Captured jobs using the capture_job decorator
from pydiabas import PyDIABAS
from pydiabas.simulation import capture_job

# Create a list to store the captured jobs
captured_jobs = []

# Creates a PyDIABAS instance
with PyDIABAS() as pydiabas:

    # Decorate the job method and pass the list to store the jobs to
    pydiabas.job = capture_job(pydiabas.job, captured_jobs)

    # Any executed job will now create a CapturedJob object, wich is appended to te captured_jobs list
    pydiabas.job("TMODE", "INFO")
    pydiabas.job("TMODE", "LESE_INTERFACE_TYP")
```

> **capture_job(job_func, job_cache)** -> Callable
>
> Decorated the given **job_func***. Any executed job will be captured as *CapturedJob* object and appended to the list given as **job_cache** argument.
>
> Parameter **job_func** must be a *Callable*.  
> Parameter **job_cache** must be *list*.  
> **Returns** the decorated job function. 
> ```
> >>> pydiabas.job = capture_job(pydiabas.job, captured_jobs)
> ```

#### save_jobs_to_file function
This utility function can be used to persistently store captured job to a file. This file can later be used to load all the contained jobs into a *SimulatedPyDIABAS* instance.
A directory to store the file to can be given as arguments, if omitted the CWD will be used.
The filename will be set automatically with the format `CAPTURE_***.jobs` where `***` is a ascending number from 1 to 999. The used filename will be returned as *str* containing the absolute path.
If there are already 999 jobs files in this directory and no unused filename can be generated, a FileExistsError will be raised.
```py
# Saving the captured jobs from the example above as file
from pydiabas.simulation import save_jobs_to_file

# Save captured jobs as *.jobs file in the CWD
file_path = save_jobs_to_file(captured_jobs)
```

> **save_jobs_to_file(jobs, [directory=""])** -> str
>
> Decorated the given **job_func***. Any executed job will be captured as *CapturedJob* object and appended to the list given as **job_cache** argument.
>
> Parameter **jobs** must be a *CapturedJob* object or a *list* or *tuple* of *CapturedJob* objects.  
> Optional parameter **directory** must be *str* or *os.PathLike* object.  
> **Returns** the absolute path to the created file as *str*.  
> **Raises** a *FileExistsError* if failed.
> ```
> >>> file_path = save_jobs_to_file(captured_jobs)
> ```


## 6 Tests
There are test which can be run without being connected to an ECU and some other tests need a specific ECU to be connected.  
A working **EDIABAS** system ist required. To solve the most common communication problems with **EDIABAS** please consult the section [EDIABAS Troubleshooting](#8-ediabas-troubleshooting). Steps 1-3 must be completed successful to run the offline test and steps 4-5 in addition to be able to run online tests.
The test must be executed using `pytest` on a 32bit python version.
Current test coverage is 99%.
Use the following command to run all test
```
python -Wa -m pytest test
```

### Offline Tests
These test do not need a to have an ECU connected.
These test cover the behavior of all the classes, methods and properties as well as the connection between **pydiabas** and **EDIABAS**.
Use the following command to rund all offline test at once:
```
python -Wa -m pytest test -m offline
```

### MSD80 Tests
Test which require an MSD80 ECU to be connected have to be run manually.
These test cover the *MSD80* Class as well as some parts of the *ECU* class that need a ECU to be connected to extract table data.
Use the following command to manually run the test for the MSD80:
```
python -Wa -m pytest test -m msd80
```

### MSD80 Simulation
To be able to run all tests without being connected to a car. The jobs executed on an `MSD80` can be simulated by running the test with an additional `--simulation=on` argument.
```
python -Wa -m pytest test --simulation=on
```
The simulation can be combined with any other argument e.g.:
```
python -Wa -m pytest test --simulation=on -m msd80
```

### Additional test commands
There are some additional arguments to modify test execution as follows:
- `--apitrace` ("off", "on" or 0-8, default: 0): Sets the *EDIABAS* apiTrace level.
- `--capturejobs` ("off" or "on", default: "off"): Controls job capturing of all jobs executed while running the test. The `*.jobs` file will be stored in the CWD.


## 7 Limitations
### 32bit python version
As **EDIABAS** is using a 32bit architecture, a 32bit python version must be used to be able to load the `api32.dll` library.

### EDIABAS Multi Threading
It seems that **EDIABAS** allows multithreading in some way, but I didn't figure out how to use it or why it isn't working in my computer.

## 8 Future Development
### Async Job execution
Allowing an job to be executed asynchronous to avoid blocking the calling program until the result is returned by the ECU.

### Extend Parameter Validation
To avoid hidden bugs and ease troubleshooting it might be feasible to add some more parameter checking in each method.

### Add Specific ECU Classes
Add further classes providing specific functionality for single ECUs.

## 9 EDIABAS Troubleshooting
Here are some common reasons for problems with getting a connection to your car.

### 1. Check your Windows Environment Variables
Make sure that the `/bin` folder of your **EDIABAS** installation (default: `C:\EDIABAS\bin`) is set as *system environment variable*. This is needed to be able to load the `api32.dll` library.

### 2. Using a 32bit python version
Make sure your are using a 32bit python version when using this module.  
If your are using a 46bit python version and importing the pydiabas library you will get the following error message:
```
>>> import pydiabas
Traceback (most recent call last):
 ...
 ...
OSError: [WinError 193] %1 is not a valid Win32 application
```
To check if you are using a 32bit python version your can simply check the length of a memory access of any object like this:
```
# On a 64bit python addresses are 12 characters long
>>> hex(id(None))
'0x7fff32736cc8'

# On a 32bit python addresses are 8 characters long
>>> hex(id(None))
'0x607c0340'
```


### 3. Confirm Communication with TMODE ECU
If you successfully completed steps 1 and 2 you should be able to import the **pydiabas** library. To check the communication between your **pydiabas** and **EDIABAS** you can try to execute jobs using the "TMODE" ECU. This ECU is accessible even if no USB cable or car is connected to your computer.
```py
# Check communication with EDIABAS
from pydiabas import PyDIABAS

with PyDIABAS() as pydiabas:
    
    # Run a job using TMODE ECU and print the returned result for verification
    print(pydiabas.job(ecu="TMODE", job="INFO"))

"""This should rund without raising any Exception printing something like:
============== PyDIABAS Result ==============
-------------- systemSet       --------------
OBJECT                        : tmode
SAETZE                        : 1
JOBNAME                       : INFO
VARIANTE                      : TMODE
JOBSTATUS                     :
...
-------------- jobSet #0       --------------
ECU                           : TMODE
...
============== END             ==============
"""
```

### 4. OBD Cable Driver and Settings
Now that we have verified successful communication between your **pydiabas** and **EDIABAS** we need to take a care about the connection between **EDIABAS** and your car.  

In your *Device Manager* open the properties of your OBD USB cable (most probably called "*USB Serial Port*" under the section "*Ports (COM & LPT)*") and continue with the following checks: 

#### Driver
Got to the tab "*Driver*" to check if the driver for your OBD USB cable has been installed properly. For my cable I currently use the FTDI driver with version 2.12.36.4.

#### COM Port and latency
Open the tab "*Port Settings*" and click the button "*Advanced...*".  
In the new window remember the "*COM Port Number*" and set the "*Latency Timer (msec)*" to 1.  
Now you can close all dialogues and your *Device Manager*.

### 5. EDIABAS Configuration
Now let's check your **EDIABAS** configuration.

#### EDIABAS.ini
Open the file `EDIABAS.ini` in the `/bin` folder of your **EDIABAS** installation (default: `C:\EDIABAS\bin`) with a text editor.
Check the following lines for the correct values:
```
...
[Configuration]
Interface        = STD:OBD
Simulation       = 0
NetworkProtocol  = TCP
...
[TCP]
RemoteHost       = 192.168.68.40
Port             = 6801
...
```
> __Info:__ Lines starting with a semicolon are treated as comments and have no effect!

#### OBD.ini
Open the file `OBD.ini` in the `/bin` folder of your **EDIABAS** installation (default: `C:\EDIABAS\bin`) with a text editor.  
Find the section "[OBD]" and make sure the COM port number is set correctly like:  
```
[OBD]  
Port=Com1
...
```

With all this set up, you should be able to establish a connection between **pydiabas** and your car.

## 10 License
Copyright (c) 2024 Aljoscha Greim aljoscha@bembelbytes.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## 11 Change Log
### 1.2.0 (03.02.2025)
#### New Features
- *job()* method added to ECU class
- Simulation feature added
#### Bugfixes
- Exception message corrected in *MSD80*

### 1.1.0 (05.01.2025)
#### New Features
- New methods *get_in()* and *get_fn()* for *Result* and *Set* class.
#### Bugfixes
- Minor BUGFIXES in Tests
#### Miscellaneous
- Tested on Python 3.13.1 32bit
- Tests moved from unittest to pytest
- Increased test coverage to 99%
- Using black for code styling

### 1.0.1 (23.11.2024)
- Reorganized project structure to publish pydiabas as package via PyPi
- Added installation instructions to README

### 1.0.0
- Initial Release