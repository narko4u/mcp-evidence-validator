"""Canonical JSON fingerprinting for the MCP Evidence Validator.

Deterministic SHA-256 over canonical JSON: sorted keys, compact separators,
stable float formatting. Same declaration always yields the same hash.
"""

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    """Serialize a value to canonical JSON (sorted keys, compact)."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def fingerprint(value: Any) -> str:
    """Return 'sha256:<hex>' for a value."""
    raw = canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def fingerprint_matches(value: Any, expected: str) -> bool:
    """True when the value's fingerprint equals the expected hash string."""
    return fingerprint(value) == expected
