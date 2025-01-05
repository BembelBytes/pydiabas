# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License


class PyDIABASError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class StateError(PyDIABASError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ConfigError(PyDIABASError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
