"""Enforcement gate tests."""

from decimal import Decimal
from bopcart_v2.calculation_engine import calculate
from bopcart_v2.enforcement_gate import enforce
from bopcart_v2.rule_resolution import resolve_rules
from bopcart_v2.schemas import CartLine, Verdict


def _calc(total="9.99", budget="10.00"):
    rule = resolve_rules()
    line = CartLine(product_id="p", unit_price=Decimal(total), quantity=1, merchant_id="m")
    return calculate([line], budget_cap=budget, rule=rule), rule


def test_allow_under_budget():
    calc, rule = _calc()
    decision = enforce(calc, cart_digest="sha256:abc", merchant_identity="m", rule=rule)
    assert decision.verdict == Verdict.ALLOW


def test_deny_over_budget():
    calc, rule = _calc(total="10.01", budget="10.00")
    decision = enforce(calc, cart_digest="sha256:abc", merchant_identity="m", rule=rule)
    assert decision.verdict == Verdict.DENY


def test_merchant_mismatch_hold():
    calc, rule = _calc(total="9.99")
    decision = enforce(
        calc,
        cart_digest="sha256:abc",
        merchant_identity="m",
        rule=rule,
        merchant_total_minor=1049,  # $10.49
        tolerance_minor=0,
    )
    assert decision.verdict == Verdict.HOLD
