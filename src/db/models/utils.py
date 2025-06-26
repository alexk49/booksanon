import inspect
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime


def make_json_safe(data):
    """
    Recursively converts data into JSON.
    Supports dataclasses (with properties), sets, datetime, etc.
    """
    if is_dataclass(data):
        return _dataclass_to_safe_dict(data)
    elif isinstance(data, dict):
        return {k: make_json_safe(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [make_json_safe(v) for v in data]
    elif isinstance(data, set):
        return [make_json_safe(v) for v in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data


def _dataclass_to_safe_dict(instance):
    result = {k: make_json_safe(v) for k, v in asdict(instance).items()}

    # Include @property values
    for name, attr in inspect.getmembers(type(instance), lambda o: isinstance(o, property)):
        try:
            value = getattr(instance, name)
            result[name] = make_json_safe(value)
        except Exception as exc:
            print(f"unable to read {result}, {name}, {result[name]}: {exc}")
            result[name] = None
    return result


def map_types_for_db(data: dict) -> dict:
    """
    Cleans a dict for insertion into database.
    Converts sets to lists, JSON dicts/lists of dicts.
    """
    return {k: _convert_for_db(k, v) for k, v in data.items()}


def _convert_for_db(key: str, value):
    if isinstance(value, set):
        return [str(v) for v in value]

    if isinstance(value, list):
        if all(isinstance(v, dict) for v in value):
            return json.dumps(value)
        return [_convert_for_db(key, v) for v in value]

    if isinstance(value, dict):
        return json.dumps({k: _convert_for_db(k, v) for k, v in value.items()})

    if key == "openlib_cover_ids" and isinstance(value, list):
        return [str(v) for v in value]

    return value
