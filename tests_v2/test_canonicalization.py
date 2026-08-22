"""Canonical serialization & digest stability."""

from decimal import Decimal
from bopcart_v2.canonical import canonicalize, sha256_digest


def test_key_order_independent():
    a = {"b": 1, "a": 2}
    b = {"a": 2, "b": 1}
    assert canonicalize(a) == canonicalize(b)
    assert sha256_digest(a) == sha256_digest(b)


def test_decimal_stable():
    d = Decimal("14.25")
    assert sha256_digest({"amount": d}) == sha256_digest({"amount": Decimal("14.25")})


def test_no_float_in_canonical():
    try:
        canonicalize({"x": 0.1})
        assert False, "should have raised"
    except TypeError:
        pass
