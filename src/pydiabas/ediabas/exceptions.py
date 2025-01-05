# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License


class EDIABASError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class JobFailedError(EDIABASError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class VersionCheckError(EDIABASError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
