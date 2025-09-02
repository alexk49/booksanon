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
)


def test_is_required():
    assert is_required("hello") == {"success": True, "value": "hello"}
    assert is_required("") == {"success": False, "error": "This field is required."}
    assert is_required(None) == {"success": False, "error": "This field is required."}


def test_is_openlib_work_id_valid_and_invalid():
    assert is_openlib_work_id("OL123W") == {"success": True, "value": "OL123W"}
    assert is_openlib_work_id("INVALID") == {"success": False, "error": "Invalid openlibrary work ID"}


def test_must_be_empty():
    assert must_be_empty("") == {"success": True, "value": ""}
    assert must_be_empty(None) == {"success": True, "value": None}
    assert must_be_empty("not empty") == {"success": False, "error": "This field must be empty."}


def test_validate_csrf_token():
    # Missing tokens
    assert validate_csrf_token("", "") == {"success": False, "error": "Missing CSRF token."}
    assert validate_csrf_token("token", "") == {"success": False, "error": "Missing CSRF token."}
    assert validate_csrf_token("", "token") == {"success": False, "error": "Missing CSRF token."}

    # Mismatch
    assert validate_csrf_token("token1", "token2") == {"success": False, "error": "CSRF token mismatch."}

    # Match
    assert validate_csrf_token("token", "token") == {"success": True, "value": "token"}


def test_chain_validators_pass_and_fail():
    def always_pass(v):
        return {"success": True, "value": v}

    def always_fail(v):
        return {"success": False, "error": "Failed"}

    # Single pass
    assert chain_validators("val", always_pass) == {"success": True, "value": "val"}

    # Multiple passes
    assert chain_validators("val", always_pass, always_pass) == {"success": True, "value": "val"}

    # Fail on second validator
    assert chain_validators("val", always_pass, always_fail) == {"success": False, "error": "Failed"}


def test_get_errors_filters_only_failed():
    results = {
        "field1": {"success": True, "value": 1},
        "field2": {"success": False, "error": "Error message"},
        "field3": {"success": False, "error": "Another error"},
    }
    errors = get_errors(results)
    assert errors == {
        "field2": "Error message",
        "field3": "Another error",
    }


def test_clean_results_extracts_values():
    results = {
        "field1": {"success": True, "value": "value1"},
        "field2": {"success": True, "value": "value2"},
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

    assert results["csrf_token"]["success"] is True
    assert results["openlib_id_hidden"]["success"] is True
    assert results["review"]["success"] is True

    # Change csrf_token to mismatch
    results_bad_csrf = validate_form(data, "wrongtoken", book_submit_fields)
    assert results_bad_csrf["csrf_token"]["success"] is False

    # Remove a required field
    data_missing = data.copy()
    data_missing["review"] = ""
    results_missing = validate_form(data_missing, session_token, book_submit_fields)
    assert results_missing["review"]["success"] is False


def test_validate_form_empty_csrf_token_field():
    data = {"csrf_token": ""}
    session_token = ""
    results = validate_form(data, session_token, {"csrf_token": [validate_csrf_token]})
    assert results["csrf_token"]["success"] is False
    assert results["csrf_token"]["error"] == "Missing CSRF token."
