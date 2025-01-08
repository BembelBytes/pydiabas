# Copyright (c) 2024 Aljoscha Greim <aljoscha@bembelbytes.com>
# MIT License

import pytest
import pathlib
import os
import pickle

from pydiabas import Result
from pydiabas.simulation import CapturedJob, capture_job, save_jobs_to_file


@pytest.mark.offline
class TestCapturedJob:
    def test_init(self, ediabas):
        captured_job = CapturedJob("ECU", "JOB", Result(ediabas))
        assert captured_job.ecu == "ECU"
        assert captured_job.job == "JOB"
        assert captured_job.parameters == ""
        assert captured_job.result_filter == ""

        captured_job = CapturedJob(
            "ECU",
            "JOB",
            parameters="1;2",
            result_filter=["a", "b"],
            result=Result(ediabas),
        )
        assert captured_job.ecu == "ECU"
        assert captured_job.job == "JOB"
        assert captured_job.parameters == "1;2"
        assert captured_job.result_filter == ["a", "b"]

    def test_check(self, ediabas):
        captured_job = CapturedJob("ECU", "JOB", Result(ediabas))
        assert captured_job.check("ECU", "JOB") == captured_job.result
        assert captured_job.check("ECU", "job") == captured_job.result
        assert captured_job.check("ECU", "JOB", "", "") == captured_job.result
        assert captured_job.check("FOO", "JOB") is None
        assert captured_job.check("ECU", "BAR") is None

        captured_job = CapturedJob(
            "ECU",
            "JOB",
            parameters="1;2",
            result_filter=["a", "b"],
            result=Result(ediabas),
        )
        assert (
            captured_job.check("ECU", "JOB", "1;2", ["a", "b"]) == captured_job.result
        )
        assert captured_job.check("FOO", "JOB", "1;2", ["a", "b"]) is None
        assert captured_job.check("ECU", "BAR", "1;2", ["a", "b"]) is None
        assert captured_job.check("ECU", "JOB", "1;3", ["a", "b"]) is None
        assert captured_job.check("ECU", "JOB", "1;2", ["a", "c"]) is None
        assert captured_job.check("ECU", "JOB", "1;2") is None
        assert captured_job.check("ECU", "JOB", result_filter=["a", "b"]) is None


@pytest.mark.offline
class TestCaptureJobs:
    def test_create_function(self):
        l = []
        f = capture_job(lambda _: None, l)
        assert callable(f)

    def test_captured_data(self, pydiabas_no_sim):
        cache: list[CapturedJob] = []
        result = capture_job(pydiabas_no_sim.job, cache)("TMODE", "INFO")
        capture_job(pydiabas_no_sim.job, cache)(
            "TMODE", "LESE_INTERFACE_TYP", "1;2", ["a", "b"]
        )
        capture_job(pydiabas_no_sim.job, cache)(
            "TMODE", "LESE_INTERFACE_TYP", parameters="1;2", result_filter=["a", "b"]
        )
        capture_job(pydiabas_no_sim.job, cache)(
            ecu="TMODE",
            job="LESE_INTERFACE_TYP",
            parameters="1;2",
            result_filter=["a", "b"],
        )
        assert len(cache) == 4
        assert cache[0].ecu == "TMODE"
        assert cache[0].job == "INFO"
        assert cache[0].parameters == ""
        assert cache[0].result_filter == ""
        assert cache[0].result == result

        assert cache[-1].ecu == "TMODE"
        assert cache[-1].job == "LESE_INTERFACE_TYP"
        assert cache[-1].parameters == "1;2"
        assert cache[-1].result_filter == ["a", "b"]

    def test_save_jobs_to_file_as_list(self, pydiabas_no_sim):
        cache: list[CapturedJob] = []
        capture_job(pydiabas_no_sim.job, cache)("TMODE", "INFO")

        path = pathlib.Path(__file__).parent.resolve()
        file_path = save_jobs_to_file(cache, path)
        with open(file_path, "rb") as file:
            file_contents = pickle.load(file)
        os.remove(os.path.join(path, file_path))

        assert isinstance(file_path, str)
        assert "CAPTURE_" in file_path
        assert file_path.endswith(".jobs")
        assert isinstance(file_contents, list)
        for item in file_contents:
            assert isinstance(item, CapturedJob)

    def test_save_jobs_to_file_as_single_object(self, pydiabas_no_sim):
        cache: list[CapturedJob] = []
        capture_job(pydiabas_no_sim.job, cache)("TMODE", "INFO")

        path = pathlib.Path(__file__).parent.resolve()
        file_path = save_jobs_to_file(cache[0], path)
        with open(file_path, "rb") as file:
            file_contents = pickle.load(file)
        os.remove(os.path.join(path, file_path))

        assert isinstance(file_path, str)
        assert "CAPTURE_" in file_path
        assert file_path.endswith(".jobs")
        assert isinstance(file_contents, list)
        for item in file_contents:
            assert isinstance(item, CapturedJob)
