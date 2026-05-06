"""
Schema validation helpers for API response bodies.
Use these in network interception tests and direct API tests.
"""
from typing import Any


def assert_keys_present(body: dict, required_keys: list[str], label: str = "response"):
    missing = [k for k in required_keys if k not in body]
    assert not missing, (
        f"{label} missing required keys: {missing}. Got: {list(body.keys())}"
    )


def assert_key_type(body: dict, key: str, expected_type: type, label: str = "response"):
    assert key in body, f"{label} missing key '{key}'"
    actual = body[key]
    assert isinstance(actual, expected_type), (
        f"{label}['{key}'] expected {expected_type.__name__}, "
        f"got {type(actual).__name__}: {actual!r}"
    )


def assert_non_empty_list(body: dict, key: str, label: str = "response"):
    assert_key_type(body, key, list, label)
    assert len(body[key]) > 0, f"{label}['{key}'] is an empty list — expected data"


def assert_schema(body: dict, schema: dict[str, type], label: str = "response"):
    """
    Validate a response body against a schema dict.

    Usage:
        assert_schema(resp, {"data": list, "total": int, "page": int})
    """
    for key, expected_type in schema.items():
        assert_key_type(body, key, expected_type, label)
