"""
Deterministic canonical serialization for digests.
UTF-8, stable key ordering, deterministic Decimal handling.
SHA-256 only. Never Python built-in hash().
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any


def _normalize(obj: Any) -> Any:
    """Recursively normalize for canonical form."""
    if isinstance(obj, dict):
        return {k: _normalize(obj[k]) for k in sorted(obj.keys())}
    if isinstance(obj, (list, tuple)):
        return [_normalize(x) for x in obj]
    if isinstance(obj, Decimal):
        # Canonical string form without scientific notation for money
        return format(obj, "f")
    if isinstance(obj, float):
        # Should never reach here for money; fail closed if it does
        raise TypeError("float not allowed in canonical economic data; use Decimal")
    if isinstance(obj, (str, int, bool)) or obj is None:
        return obj
    # Fallback for datetime etc.
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)


def canonicalize(obj: Any) -> bytes:
    """
    Produce deterministic UTF-8 bytes.
    - Sorted keys
    - No whitespace variance
    - Decimal as fixed-point string
    - No Python object ids or nondeterministic fields
    """
    normalized = _normalize(obj)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_digest(obj: Any) -> str:
    """Return 'sha256:<hex>' of the canonical form."""
    data = canonicalize(obj)
    h = hashlib.sha256(data).hexdigest()
    return f"sha256:{h}"


def sha256_hex(obj: Any) -> str:
    """Return pure hex digest (no prefix)."""
    data = canonicalize(obj)
    return hashlib.sha256(data).hexdigest()
