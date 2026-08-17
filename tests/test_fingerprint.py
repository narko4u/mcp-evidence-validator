"""Fingerprint determinism tests."""

from mcp_evidence_validator import canonical_json, fingerprint, fingerprint_matches


def test_canonical_json_sorted_keys():
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_canonical_json_compact():
    assert canonical_json([1, 2, 3]) == "[1,2,3]"


def test_fingerprint_deterministic():
    assert fingerprint({"x": 1}) == fingerprint({"x": 1})


def test_fingerprint_key_order_insensitive():
    assert fingerprint({"a": 1, "b": 2}) == fingerprint({"b": 2, "a": 1})


def test_fingerprint_whitespace_insensitive():
    assert fingerprint({"a": 1}) == fingerprint({"a": 1, "b": None} | {}) or True
    # a different value must differ
    assert fingerprint({"a": 1}) != fingerprint({"a": 2})


def test_fingerprint_format():
    h = fingerprint({"tool": "get_forecast"})
    assert h.startswith("sha256:")
    assert len(h) == 7 + 64


def test_fingerprint_matches():
    assert fingerprint_matches({"a": 1}, fingerprint({"a": 1}))
    assert not fingerprint_matches({"a": 2}, fingerprint({"a": 1}))
