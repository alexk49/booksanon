import pytest
from server.form_validators import (
    validate_form,
    clean_results,
    chain_validators,
    get_errors,
    is_required,
    is_openlib_work_id,
    must_be_empty,
    validate_csrf_token,
    book_submit_fields,
    search_form_fields,
)


def test_is_required():
    assert is_required("hello") == {"ok": True, "value": "hello"}
    assert is_required("") == {"ok": False, "error": "This field is required."}
    assert is_required(None) == {"ok": False, "error": "This field is required."}


def test_is_openlib_work_id_valid_and_invalid():
    assert is_openlib_work_id("OL123W") == {"ok": True, "value": "OL123W"}
    assert is_openlib_work_id("INVALID") == {"ok": False, "error": "Invalid openlibrary work ID"}


def test_must_be_empty():
    assert must_be_empty("") == {"ok": True, "value": ""}
    assert must_be_empty(None) == {"ok": True, "value": None}
    assert must_be_empty("not empty") == {"ok": False, "error": "This field must be empty."}


def test_validate_csrf_token():
    # Missing tokens
    assert validate_csrf_token("", "") == {"ok": False, "error": "Missing CSRF token."}
    assert validate_csrf_token("token", "") == {"ok": False, "error": "Missing CSRF token."}
    assert validate_csrf_token("", "token") == {"ok": False, "error": "Missing CSRF token."}

    # Mismatch
    assert validate_csrf_token("token1", "token2") == {"ok": False, "error": "CSRF token mismatch."}

    # Match
    assert validate_csrf_token("token", "token") == {"ok": True, "value": "token"}


def test_chain_validators_pass_and_fail():
    def always_pass(v):
        return {"ok": True, "value": v}

    def always_fail(v):
        return {"ok": False, "error": "Failed"}

    # Single pass
    assert chain_validators("val", always_pass) == {"ok": True, "value": "val"}

    # Multiple passes
    assert chain_validators("val", always_pass, always_pass) == {"ok": True, "value": "val"}

    # Fail on second validator
    assert chain_validators("val", always_pass, always_fail) == {"ok": False, "error": "Failed"}


def test_get_errors_filters_only_failed():
    results = {
        "field1": {"ok": True, "value": 1},
        "field2": {"ok": False, "error": "Error message"},
        "field3": {"ok": False, "error": "Another error"},
    }
    errors = get_errors(results)
    assert errors == {
        "field2": "Error message",
        "field3": "Another error",
    }


def test_clean_results_extracts_values():
    results = {
        "field1": {"ok": True, "value": "value1"},
        "field2": {"ok": True, "value": "value2"},
    }
    cleaned = clean_results(results)
    assert cleaned == {
        "field1": "value1",
        "field2": "value2",
    }


def test_validate_form_with_csrf_and_other_fields():
    data = {
        "openlib_id_hidden": "OL123W",
        "review": "Great book!",
        "csrf_token": "token123",
    }
    session_token = "token123"
    results = validate_form(data, session_token, book_submit_fields)

    assert results["csrf_token"]["ok"] is True
    assert results["openlib_id_hidden"]["ok"] is True
    assert results["review"]["ok"] is True

    # Change csrf_token to mismatch
    results_bad_csrf = validate_form(data, "wrongtoken", book_submit_fields)
    assert results_bad_csrf["csrf_token"]["ok"] is False

    # Remove a required field
    data_missing = data.copy()
    data_missing["review"] = ""
    results_missing = validate_form(data_missing, session_token, book_submit_fields)
    assert results_missing["review"]["ok"] is False


def test_validate_form_empty_csrf_token_field():
    data = {"csrf_token": ""}
    session_token = ""
    results = validate_form(data, session_token, {"csrf_token": [validate_csrf_token]})
    assert results["csrf_token"]["ok"] is False
    assert results["csrf_token"]["error"] == "Missing CSRF token."
