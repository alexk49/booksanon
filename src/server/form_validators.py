from typing import Any


from calls.openlib import validate_openlib_work_id


def validate_form(data: dict, session_token: str, form_fields: dict) -> dict:
    results = {}
    for field, validators in form_fields.items():
        value = data.get(field, "")
        if field == "csrf_token":
            results[field] = validators[0](session_token, value)
        else:
            results[field] = chain_validators(value, *validators)
    return results


def clean_results(results: dict):
    return {k: v["value"] for k, v in results.items()}


def chain_validators(value, *validators) -> dict:
    """
    Used to run all required validation functions on form value
    """
    for validator in validators:
        result = validator(value)
        print(result)
        if not result["ok"]:
            return result
    return {"ok": True, "value": result["value"]}


def get_errors(validated_data: dict) -> dict:
    """
    Filter through results of dict to find any errors
    """
    return {field: result["error"] for field, result in validated_data.items() if not result["ok"]}


def is_required(value: Any) -> dict:
    if value:
        return {"ok": True, "value": value}
    return {"ok": False, "error": "This field is required."}


def is_openlib_work_id(value: str) -> dict:
    if validate_openlib_work_id(value):
        return {"ok": True, "value": value}
    return {"ok": False, "error": "Invalid openlibrary work ID"}


def must_be_empty(value: Any) -> dict:
    if not value:
        return {"ok": True, "value": value}
    return {"ok": False, "error": "This field must be empty."}


def validate_csrf_token(session_token: str, form_token: str) -> dict:
    if not session_token or not form_token:
        return {"ok": False, "error": "Missing CSRF token."}

    if session_token != form_token:
        return {"ok": False, "error": "CSRF token mismatch."}

    return {"ok": True, "value": form_token}


book_submit_fields = {
    "openlib_id_hidden": [is_required, is_openlib_work_id],
    "review": [is_required],
    "csrf_token": [validate_csrf_token],
}

search_form_fields = {
    "search_query": [is_required],
    "csrf_token": [validate_csrf_token],
}
