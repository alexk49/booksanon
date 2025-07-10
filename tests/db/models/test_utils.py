from dataclasses import dataclass
from datetime import datetime
import json

from db.models.utils import make_json_safe, map_types_for_db


# Test data for make_json_safe
@dataclass
class SimpleDataclass:
    a: int
    b: str


@dataclass
class ComplexDataclass:
    x: int
    y: set
    z: datetime
    nested: SimpleDataclass

    @property
    def p(self):
        return self.x * 2


def test_make_json_safe_simple_types():
    assert make_json_safe(1) == 1
    assert make_json_safe("hello") == "hello"
    assert make_json_safe(None) is None


def test_make_json_safe_collections():
    assert make_json_safe([1, 2, 3]) == [1, 2, 3]
    assert make_json_safe({1, 2, 3}) == [1, 2, 3]
    assert make_json_safe({"a": 1, "b": 2}) == {"a": 1, "b": 2}


def test_make_json_safe_datetime():
    dt = datetime(2023, 1, 1, 12, 0, 0)
    assert make_json_safe(dt) == "2023-01-01T12:00:00"


def test_make_json_safe_dataclass():
    simple = SimpleDataclass(a=1, b="test")
    complex_dt = ComplexDataclass(x=10, y={"a", "b"}, z=datetime.now(), nested=simple)

    result = make_json_safe(complex_dt)

    assert result["x"] == 10
    assert sorted(result["y"]) == ["a", "b"]
    assert "z" in result
    assert result["nested"]["a"] == 1
    assert result["p"] == 20


# Test data for map_types_for_db
def test_map_types_for_db_simple():
    data = {"a": 1, "b": "string"}
    assert map_types_for_db(data) == data


def test_map_types_for_db_set():
    data = {"my_set": {1, "a", 3}}
    result = map_types_for_db(data)
    # Order is not guaranteed for sets, so we check content
    assert set(result["my_set"]) == {"1", "a", "3"}


def test_map_types_for_db_dict():
    data = {"my_dict": {"c": 3, "d": 4}}
    result = map_types_for_db(data)
    assert result["my_dict"] == json.dumps({"c": 3, "d": 4})


def test_map_types_for_db_list_of_dicts():
    data = {"my_list": [{"e": 5}, {"f": 6}]}
    result = map_types_for_db(data)
    assert result["my_list"] == json.dumps([{"e": 5}, {"f": 6}])


def test_map_types_for_db_mixed():
    data = {"a": 1, "b": {1, 2}, "c": {"d": 5}}
    result = map_types_for_db(data)
    assert result["a"] == 1
    assert set(result["b"]) == {"1", "2"}
    assert result["c"] == json.dumps({"d": 5})
