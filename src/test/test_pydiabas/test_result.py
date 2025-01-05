import pytest

from pydiabas import Result, Set, Row
from pydiabas.ediabas import EDIABAS


@pytest.mark.offline
class TestRow:
    def test_row(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="two", value="2")
        assert r1.name == "one"
        assert r1.value == "1"
        assert r2.name == "two"
        assert r2.value == "2"


@pytest.mark.offline
class TestSet:
    def test___init__(self):
        s = Set()
        assert isinstance(s, Set)
        assert s._rows == []

    def test___init___empty_list(self):
        Set(rows=[])

    def test___init___rows(self):
        r = Row(name="name", value="value")
        s = Set(rows=[r])
        assert s._rows == [r]

    def test___init___rows_no_list(self):
        r = Row(name="name", value="value")
        with pytest.raises(TypeError):
            Set(rows=r)

    def test___init___rows_no_row_in_list(self):
        with pytest.raises(TypeError):
            Set(rows=[2])

    def test___init___rows_not_only_rows_in_list(self):
        r = Row(name="name", value="value")
        with pytest.raises(TypeError):
            Set(rows=[r, 2])

    def test_all(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="two", value="2")
        s = Set(rows=[r1, r2])
        assert s.all == [r1, r2]
        s._rows = []
        assert s.all == []

    def test_as_dict(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="two", value="2")
        s = Set(rows=[r1, r2])
        assert s.as_dict() == {r1.name: r1.value, r2.name: r2.value}
        s._rows = []
        assert s.as_dict() == {}

    def test_index(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="two", value="2")
        r3 = Row(name="two", value=2)
        s = Set(rows=[r1, r2, r3])
        assert s.index("one") == 0
        assert s.index("One") == 0
        assert s.index("ONE") == 0
        assert s.index("onE") == 0
        assert s.index("two") == 1
        assert s.index("one", 0, 1) == 0
        assert s.index("two", 0, 2) == 1
        assert s.index("two", 2, 3) == 2

    def test_index_no_result(self):
        s = Set()
        with pytest.raises(ValueError):
            s.index("test")

    def test_index_no_string(self):
        s = Set()
        with pytest.raises(TypeError):
            s.index(2)

    def test_keys(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="two", value="2")
        r3 = Row(name="THREE", value=3)
        s = Set(rows=[r1, r2, r3])
        assert s.keys() == ["one", "two", "THREE"]
        s._rows = []
        assert s.keys() == []

    def test_values(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="two", value="2")
        r3 = Row(name="THREE", value=3)
        s = Set(rows=[r1, r2, r3])
        assert s.values() == ["1", "2", 3]
        s._rows = []
        assert s.values() == []

    def test_items(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="two", value="2")
        s = Set(rows=[r1, r2])
        assert s.items() == [("one", "1"), ("two", "2")]
        s._rows = []
        assert s.items() == []

    def test___getitem__(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="two", value="2")
        r3 = Row(name="THREE", value=3)
        r4 = Row(name="one", value=1)
        r5 = Row(name="five", value=b"five")
        s = Set(rows=[r1, r2, r3, r4, r5])
        s_sliced_1 = Set(rows=[r1, r2])
        s_sliced_2 = Set(rows=[r2, r3])
        s_sliced_3 = Set(rows=[r1, r3, r5])
        assert s["one"] == "1"
        assert s["ONE"] == "1"
        assert s[0] == r1
        assert s[2] == r3
        assert s[0:2].all == s_sliced_1.all
        assert s[1:3].all == s_sliced_2.all
        assert s[::2].all == s_sliced_3.all
        assert s[:].all == s.all
        assert s[:] != s
        assert s["five"] == b"five"

    def test___getitem__not_found(self):
        s = Set()
        with pytest.raises(KeyError):
            s["test"]

    def test___getitem__wrong_type_float(self):
        s = Set()
        with pytest.raises(TypeError):
            s[2.2]

    def test___getitem__wrong_type_bytes(self):
        s = Set()
        with pytest.raises(TypeError):
            s[b"five"]

    def test_get(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="one", value=1)
        s = Set(rows=[r1, r2])
        assert s.get("one") == "1"
        assert s.get("four") == None
        assert s.get("four", default=4) == 4

    def test_get_wrong_type(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="one", value=1)
        s = Set(rows=[r1, r2])
        with pytest.raises(TypeError):
            s.get(1)

    def test_get_in(self):
        r1 = Row(name="stat_one_value", value="1")
        r2 = Row(name="name_two", value=2)
        s = Set(rows=[r1, r2])
        assert s.get_in("stat_one_value") == "1"
        assert s.get_in("one_value") == "1"
        assert s.get_in("stat_one") == "1"
        assert s.get_in("one") == "1"
        assert s.get_in("statonevalue") is None
        assert s.get_in("stat_one_value_") is None

    def test_get_in_wrong_type(self):
        r1 = Row(name="stat_one_value", value="1")
        r2 = Row(name="name_two", value=2)
        s = Set(rows=[r1, r2])
        with pytest.raises(TypeError):
            s.get_in(22)

    def test_get_fn(self):
        def fn_len_8(name):
            return len(name) == 8

        def fn_starts_with(name):
            return name.startswith("stat_")

        def fn_len_10(name):
            return len(name) == 10

        r1 = Row(name="stat_one_value", value="1")
        r2 = Row(name="name_two", value=2)
        s = Set(rows=[r1, r2])
        assert s.get_fn(fn_len_8) == 2
        assert s.get_fn(fn_starts_with) == "1"
        assert s.get_fn(fn_len_10) is None
        assert s.get_fn(lambda x: x.endswith("_two")) == 2

    def test_get_fn_wrong_type(self):
        r1 = Row(name="stat_one_value", value="1")
        r2 = Row(name="name_two", value=2)
        s = Set(rows=[r1, r2])
        with pytest.raises(TypeError):
            s.get_fn("TEST")

    def test___len__(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="one", value=1)
        s = Set(rows=[r1, r2])
        assert len(s) == 2
        s._rows = []
        assert len(s) == 0

    def test___bool__(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="one", value=1)
        s = Set(rows=[r1, r2])
        assert bool(s)
        s._rows = []
        assert not bool(s)

    def test___iter__(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="one", value=1)
        s = Set(rows=[r1, r2])
        for i, r in enumerate(s):
            assert r == s[i]

    def test___str__(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="two", value=2)
        s = Set(rows=[r1, r2])
        assert (
            s.__str__()
            == "one                           : 1\ntwo                           : 2\n"
        )
        s._rows = []
        assert s.__str__() == "\n"

    def test___contains__(self):
        r1 = Row(name="one", value="1")
        r2 = Row(name="two", value=2)
        s = Set(rows=[r1, r2])
        assert "one" in s
        assert "ONE" in s
        assert "two" in s
        assert "three" not in s
        s._rows = []
        assert "one" not in s

    def test___contains__wrong_type_int(self):
        s = Set()
        with pytest.raises(TypeError):
            2 in s

    def test___contains__wrong_type_bytes(self):
        s = Set()
        with pytest.raises(TypeError):
            b"test" in s


@pytest.mark.offline
class TestResult:

    @pytest.fixture(scope="function")
    def r_tmode_lese_interface_typ(self, pydiabas):
        return pydiabas.job(ecu="TMODE", job="LESE_INTERFACE_TYP")

    @pytest.fixture(scope="function")
    def r_tmode__jobs(self, pydiabas):
        return pydiabas.job(ecu="TMODE", job="_JOBS")

    @pytest.fixture(scope="function")
    def r_simulation(self, pydiabas):
        r_simulation = Result(ediabas=pydiabas._ediabas)
        r_simulation._systemSet = Set(rows=[Row(name="SYS", value="TEM")])
        r_simulation._jobSets = [
            Set(rows=[Row(name="R1", value=1)]),
            Set(rows=[Row(name="R1", value=2), Row(name="R2", value=3)]),
            Set(
                rows=[
                    Row(name="R1", value=3),
                    Row(name="R2", value=4),
                    Row(name="R3", value=5),
                ]
            ),
            Set(rows=[Row(name="STAT_R4_MEAN_WERT", value=3)]),
        ]
        return r_simulation

    @pytest.fixture(scope="function")
    def r_empty(self, pydiabas):
        r_empty = Result(ediabas=pydiabas._ediabas)
        return r_empty

    def test___init__(self, pydiabas, r_empty):
        assert isinstance(r_empty, Result)
        assert isinstance(r_empty._systemSet, Set)
        assert r_empty._jobSets == []
        assert r_empty._systemSet.all == []
        assert isinstance(r_empty._ediabas, EDIABAS)
        assert r_empty._ediabas == pydiabas._ediabas

    def test___init___wrong_type(self):
        with pytest.raises(TypeError):
            Result("")

    def test_clear(self, r_simulation):
        r_simulation.clear()
        assert r_simulation._systemSet.all == []
        assert r_simulation._jobSets == []

    def test_fetchname(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="INFO", fetchall=False)
        assert not r
        assert len(r) == 0
        r.fetchname("AUTHOR")
        assert len(r) == 1
        assert len(r[0]) == 1
        assert r[0].as_dict() == {"AUTHOR": "Softing Ta, Softing WT"}
        assert "AUTHOR" in r._jobSets[0]
        r.fetchname("SPRACHE")
        assert len(r) == 1
        assert len(r[0]) == 2
        assert r[0].as_dict() == {
            "AUTHOR": "Softing Ta, Softing WT",
            "SPRACHE": "deutsch",
        }
        assert "AUTHOR" in r._jobSets[0]
        assert "SPRACHE" in r._jobSets[0]
        r.fetchname("SPRACHE")
        assert len(r) == 1
        assert len(r[0]) == 2
        assert r[0].as_dict() == {
            "AUTHOR": "Softing Ta, Softing WT",
            "SPRACHE": "deutsch",
        }

        r2 = pydiabas.job(ecu="TMODE", job="_JOBS", fetchall=False)
        assert not r2
        assert len(r2) == 0
        r.fetchname("JOBNAME")
        assert len(r) >= 1
        assert len(r[1]) >= 1
        assert "AUTHOR" in r._jobSets[0]
        assert "SPRACHE" in r._jobSets[0]
        assert "JOBNAME" in r._jobSets[0]
        assert "AUTHOR" not in r._jobSets[1]
        assert "SPRACHE" not in r._jobSets[1]
        assert "JOBNAME" in r._jobSets[1]

    def test_fetchset_0(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="_JOBS", fetchall=False)
        r._fetchset(i_set=0)
        assert r._systemSet["OBJECT"] == "tmode"
        assert len(r) == 0
        with pytest.raises(KeyError):
            r["JOBNAME"]

    def test_fetchset_1(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="_JOBS", fetchall=False)
        r._fetchset(i_set=1)
        assert r["JOBNAME"] is not None
        assert r[0]["JOBNAME"] is not None
        assert len(r) == 1
        with pytest.raises(KeyError):
            r._systemSet["OBJECT"]

    def test_fetchset_1_multiple_rows(self, pydiabas):
        r = pydiabas.job(
            ecu="TMODE",
            job="_JOBCOMMENTS",
            parameters="SETZE_TRAP_MASK_REGISTER",
            fetchall=False,
        )
        r._fetchset(i_set=1)
        assert r["JOBCOMMENT0"] is not None
        assert r["JOBCOMMENT1"] is not None
        assert r[0]["JOBCOMMENT0"] is not None
        assert r[0]["JOBCOMMENT1"] is not None
        assert len(r) == 1
        with pytest.raises(KeyError):
            r._systemSet["OBJECT"]

    def test_fetchset_2(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="_JOBS", fetchall=False)
        r._fetchset(i_set=2)
        assert r["JOBNAME"] is not None
        assert r[1]["JOBNAME"] is not None
        assert len(r) == 2
        with pytest.raises(KeyError):
            r[0]["JOBNAME"]

    def test_fetchset_2_and_4(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="_JOBS", fetchall=False)
        r._fetchset(i_set=2)
        r._fetchset(i_set=4)
        assert r["JOBNAME"] is not None
        assert r[1]["JOBNAME"] is not None
        assert r[3]["JOBNAME"] is not None
        assert len(r) == 4
        with pytest.raises(KeyError):
            r[2]["JOBNAME"]

    def test_fetchset_index_error(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="LESE_INTERFACE_TYP", fetchall=False)
        with pytest.raises(IndexError):
            r._fetchset(2)

    def test_fetchsystem(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="_JOBS", fetchall=False)
        r.fetchsystemset()
        assert r._systemSet["OBJECT"] == "tmode"
        with pytest.raises(KeyError):
            r["JOBNAME"]

    def test_fetchjobsets(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="_JOBS", fetchall=False)
        r.fetchjobsets()
        assert r["JOBNAME"] is not None
        assert r[0]["JOBNAME"] is not None
        assert r[3]["JOBNAME"] is not None
        assert r[len(r) - 1]["JOBNAME"] is not None
        with pytest.raises(KeyError):
            r._systemSet["OBJECT"]

    def test_fetchall(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="LESE_INTERFACE_TYP", fetchall=False)
        r.fetchall()
        assert r["TYP"] == b"OBD"
        assert r._systemSet["OBJECT"] == "tmode"

    def test_fetchall_multiple_sets(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="_JOBS", fetchall=False)
        r.fetchall()
        assert r["JOBNAME"] == "INFO"
        assert r[4]["JOBNAME"] == "SETZE_SG_PARAMETER_ALLG"
        assert r._systemSet["OBJECT"] == "tmode"

    def test_fetchname_multiple_sets(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="_JOBS", fetchall=False)
        r.fetchname("JOBNAME")
        assert r["JOBNAME"] == "INFO"
        assert r[4]["JOBNAME"] == "SETZE_SG_PARAMETER_ALLG"

    def test_fetchname_wrong_name(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="LESE_INTERFACE_TYP", fetchall=False)
        r.fetchname("XX")
        with pytest.raises(KeyError):
            r["TYP"]

    def test_fetchnames(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="LESE_INTERFACE_TYP", fetchall=False)
        r.fetchnames(["TYP"])
        assert r["TYP"] == b"OBD"

    def test_fetchnames_multiple_sets(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="_JOBS", fetchall=False)
        r.fetchnames(["JOBNAME"])
        assert r["JOBNAME"] == "INFO"
        assert r[4]["JOBNAME"] == "SETZE_SG_PARAMETER_ALLG"

    def test_fetchnames_one_wrong_name(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="LESE_INTERFACE_TYP", fetchall=False)
        r.fetchnames(["Y", "TYP", "X"])
        assert r["TYP"] == b"OBD"

    def test_fetchnames_only_wrong_names(self, pydiabas):
        r = pydiabas.job(ecu="TMODE", job="LESE_INTERFACE_TYP", fetchall=False)
        r.fetchnames(["Y", "X"])
        with pytest.raises(KeyError):
            r["TYP"]

    def test_fetchname_after_fetchset(self, pydiabas):
        r = pydiabas.job(
            ecu="TMODE",
            job="_JOBCOMMENTS",
            parameters="SETZE_TRAP_MASK_REGISTER",
            fetchall=False,
        )
        r._fetchset(i_set=1)
        assert len(r) == 1
        assert len(r[0]) == 2
        assert "JOBCOMMENT0" in r
        assert "JOBCOMMENT1" in r
        r.fetchname("JOBCOMMENT0")
        assert len(r) == 1
        assert len(r[0]) == 2
        assert "JOBCOMMENT0" in r
        assert "JOBCOMMENT1" in r

    def test_fetchset_after_fetchname(self, pydiabas):
        r = pydiabas.job(
            ecu="TMODE",
            job="_JOBCOMMENTS",
            parameters="SETZE_TRAP_MASK_REGISTER",
            fetchall=False,
        )
        r.fetchname("JOBCOMMENT0")
        assert len(r) == 1
        assert len(r[0]) == 1
        assert "JOBCOMMENT0" in r
        assert "JOBCOMMENT1" not in r
        r._fetchset(i_set=1)
        assert len(r) == 1
        assert len(r[0]) == 2
        assert "JOBCOMMENT0" in r
        assert "JOBCOMMENT1" in r

    def test_systemSet(self, r_tmode_lese_interface_typ):
        assert (
            r_tmode_lese_interface_typ._systemSet
            == r_tmode_lese_interface_typ.systemSet
        )

    def test_systemSet_empty(self, r_empty):
        assert r_empty.systemSet.all == []

    def test_jobSets(self, r_tmode_lese_interface_typ):
        assert r_tmode_lese_interface_typ._jobSets == r_tmode_lese_interface_typ.jobSets

    def test_jobSets_empty(self, r_empty):
        assert r_empty.jobSets == []

    def test_ecu(self, r_tmode_lese_interface_typ):
        assert r_tmode_lese_interface_typ.ecu == "TMODE"

    def test_ecu_empty(self, r_empty):
        assert r_empty.ecu is None

    def test_jobname(self, r_tmode_lese_interface_typ):
        assert r_tmode_lese_interface_typ.jobname == "LESE_INTERFACE_TYP"

    def test_jobname_empty(self, r_empty):
        assert r_empty.jobname is None

    def test_jobstatus(self, r_tmode_lese_interface_typ):
        assert r_tmode_lese_interface_typ.jobstatus == ""

    def test_jobstatus_empty(self, r_empty):
        assert r_empty.jobstatus is None

    def test_as_dicts(self, r_simulation):
        assert r_simulation.as_dicts() == [
            {"SYS": "TEM"},
            {"R1": 1},
            {"R1": 2, "R2": 3},
            {"R1": 3, "R2": 4, "R3": 5},
            {"STAT_R4_MEAN_WERT": 3},
        ]

    def test_as_dicts_empty(self, r_empty):
        assert r_empty.as_dicts() == [{}]

    def test_count(self, r_simulation):
        assert r_simulation.count("X") == 0
        assert r_simulation.count("SYS") == 0
        assert r_simulation.count("R1") == 3
        assert r_simulation.count("R2") == 2
        assert r_simulation.count("r2") == 2
        assert r_simulation.count("r3") == 1

    def test_count_empty(self, r_empty):
        assert r_empty.count("X") == 0
        assert r_empty.count("SYS") == 0
        assert r_empty.count("R1") == 0
        assert r_empty.count("R2") == 0

    def test_count_wring_type(self, r_empty):
        with pytest.raises(TypeError):
            r_empty.count(1)

    def test_index(self, r_simulation):
        assert r_simulation.index(name="R1", start=0, end=100) == 0
        assert r_simulation.index(name="R1", start=1, end=2) == 1
        assert r_simulation.index("R3") == 2

    def test_index_wrong_name(self, r_simulation):
        with pytest.raises(ValueError):
            r_simulation.index("X")

    def test_index_too_narrow_index(self, r_simulation):
        with pytest.raises(ValueError):
            r_simulation.index(name="R1", start=1, end=1)

    def test_index_wrong_type(self, r_simulation):
        with pytest.raises(TypeError):
            r_simulation.index(2)

    def test___getitem__(self, r_simulation):
        r_simulation_sliced_1 = r_simulation[:]
        r_simulation_sliced_1._jobSets = r_simulation._jobSets[1:2]
        r_simulation_sliced_2 = r_simulation[:]
        r_simulation_sliced_2._jobSets = r_simulation._jobSets[2:10]
        r_simulation_sliced_3 = r_simulation[:]
        r_simulation_sliced_3._jobSets = r_simulation._jobSets[::2]

        assert r_simulation["R1"] == 1
        assert r_simulation["r2"] == 3
        assert r_simulation[0] == r_simulation._jobSets[0]
        assert r_simulation[-1] == r_simulation._jobSets[3]
        assert r_simulation[:]._jobSets == r_simulation._jobSets
        assert r_simulation[:]._systemSet == r_simulation._systemSet
        assert id(r_simulation[:]._jobSets) != id(r_simulation._jobSets)
        assert id(r_simulation[:]) != id(r_simulation)
        assert r_simulation[1:2]._jobSets == r_simulation_sliced_1._jobSets
        assert r_simulation[1:2]._systemSet == r_simulation_sliced_1._systemSet
        assert r_simulation[2:10]._jobSets == r_simulation_sliced_2._jobSets
        assert r_simulation[2:10]._systemSet == r_simulation_sliced_2._systemSet
        assert r_simulation[::2]._jobSets == r_simulation_sliced_3._jobSets
        assert r_simulation[::2]._systemSet == r_simulation_sliced_3._systemSet

    def test___getitem___wrong_type(self, r_simulation):
        with pytest.raises(TypeError):
            r_simulation[1.2]

    def test___getitem___index_out_of_range(self, r_simulation):
        with pytest.raises(IndexError):
            r_simulation[4]

    def test___getitem___key_error(self, r_simulation):
        with pytest.raises(KeyError):
            r_simulation["XX"]

    def test___getitem___key_error_on_systemSet(self, r_simulation):
        with pytest.raises(KeyError):
            r_simulation["SYS"]

    def test___contains__(self, r_simulation):
        assert "R1" in r_simulation
        assert "r1" in r_simulation
        assert "r3" in r_simulation
        assert "X" not in r_simulation
        assert "SYS" not in r_simulation

    def test___contains___wrong_type(self, r_simulation):
        with pytest.raises(TypeError):
            2 in r_simulation

    def test_get(self, r_simulation):
        assert r_simulation.get("R1") == 1
        assert r_simulation.get("R1", default="TEST") == 1
        assert r_simulation.get("r2") == 3
        assert r_simulation.get("r2", default="TEST") == 3
        assert r_simulation.get("SYS") == None
        assert r_simulation.get("SYS", default="TEST") == "TEST"

    def test_get_wrong_type(self, r_simulation):
        with pytest.raises(TypeError):
            r_simulation.get(1)

    def test_get_in(self, r_simulation):
        assert r_simulation.get_in("R1") == 1
        assert r_simulation.get_in("R1", default="TEST") == 1
        assert r_simulation.get_in("r2") == 3
        assert r_simulation.get_in("r2", default="TEST") == 3
        assert r_simulation.get_in("SYS") == None
        assert r_simulation.get_in("SYS", default="TEST") == "TEST"
        assert r_simulation.get_in("STAT_R4_MEAN_WERT") == 3
        assert r_simulation.get_in("STAT_r4_MeaN_WERT") == 3
        assert r_simulation.get_in("STAT_R4_MEAN") == 3
        assert r_simulation.get_in("R4_MEAN_WERT") == 3
        assert r_simulation.get_in("R4_MEAN") == 3
        assert r_simulation.get_in("R4_MEA_") is None
        assert r_simulation.get_in("_4_MEAN") is None
        assert r_simulation.get_in("_STAT_R4_MEAN_WERT") is None

    def test_get_in_wrong_type(self, r_simulation):
        with pytest.raises(TypeError):
            r_simulation.get_in(22)

    def test_get_fn(self, r_simulation):
        def fn_len_2(name):
            return len(name) == 2

        def fn_starts_with(name):
            return name.startswith("STAT_")

        def fn_len_40(name):
            return len(name) == 40

        assert r_simulation.get_fn(fn_len_2) == 1
        assert r_simulation.get_fn(fn_starts_with) == 3
        assert r_simulation.get_fn(fn_len_40) is None
        assert r_simulation.get_fn(lambda x: x.endswith("_WERT")) == 3

    def test_get_fn_wrong_type(self, r_simulation):
        with pytest.raises(TypeError):
            r_simulation.get_fn("TEST")

    def test___len__(self, r_simulation, r_empty):
        assert len(r_simulation) == 4
        assert len(r_empty) == 0

    def test___bool__(self, r_simulation, r_tmode__jobs, r_empty):
        assert r_simulation
        assert r_tmode__jobs
        assert not r_empty

    def test___iter__(self, r_simulation):
        for i, s in enumerate(r_simulation):
            assert s == r_simulation._jobSets[i]

    def test___str__(self, r_simulation, r_empty):
        assert (
            str(r_simulation)
            == """
============== PyDIABAS Result ==============
-------------- systemSet       --------------
SYS                           : TEM
-------------- jobSet #0       --------------
R1                            : 1
-------------- jobSet #1       --------------
R1                            : 2
R2                            : 3
-------------- jobSet #2       --------------
R1                            : 3
R2                            : 4
R3                            : 5
-------------- jobSet #3       --------------
STAT_R4_MEAN_WERT             : 3
============== END             ==============
"""
        )

        assert (
            str(r_empty)
            == """
============== PyDIABAS Result ==============
============== END             ==============
"""
        )
