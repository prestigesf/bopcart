"""Execution adapter & state machine tests."""

from decimal import Decimal
import pytest

from bopcart_v2.authorization import issue_authorization
from bopcart_v2.calculation_engine import calculate, cart_digest
from bopcart_v2.enforcement_gate import enforce
from bopcart_v2.errors import ExecutionStateError
from bopcart_v2.execution_adapter import SimulatedAdapter
from bopcart_v2.execution_instruction import build_execution_instruction
from bopcart_v2.rule_resolution import resolve_rules
from bopcart_v2.schemas import Cart, CartLine, Verdict


def _full_pipeline(price="0.99"):
    rule = resolve_rules()
    line = CartLine(product_id="p", unit_price=Decimal(price), quantity=1, merchant_id="m")
    cart = Cart(lines=[line], merchant_id="m")
    calc = calculate([line], budget_cap="10.00", rule=rule)
    decision = enforce(calc, cart_digest=cart_digest(cart), merchant_identity="m", rule=rule)
    auth = issue_authorization(
        intent_id="i1",
        cart_digest=cart_digest(cart),
        merchant_identity="m",
        calc=calc,
        decision=decision,
    )
    instr = build_execution_instruction(
        intent_id="i1",
        merchant_id="m",
        calc=calc,
        auth=auth,
    )
    return calc, decision, auth, instr


def test_hold_cannot_execute():
    calc, decision, auth, instr = _full_pipeline()
    adapter = SimulatedAdapter()
    with pytest.raises(ExecutionStateError):
        adapter.execute(instr, enforcement_verdict="HOLD")


def test_deny_cannot_execute():
    calc, decision, auth, instr = _full_pipeline()
    adapter = SimulatedAdapter()
    with pytest.raises(ExecutionStateError):
        adapter.execute(instr, enforcement_verdict="DENY")


def test_idempotent_retry():
    calc, decision, auth, instr = _full_pipeline()
    adapter = SimulatedAdapter()
    r1 = adapter.execute(instr, enforcement_verdict="ALLOW")
    r2 = adapter.execute(instr, enforcement_verdict="ALLOW")
    assert r1.status == "SUCCESS"
    assert r2.status == "DUPLICATE"
    assert r1.external_transaction_reference == r2.external_transaction_reference


def test_price_change_at_execution_holds():
    calc, decision, auth, instr = _full_pipeline()
    adapter = SimulatedAdapter()
    result = adapter.execute(
        instr,
        enforcement_verdict="ALLOW",
        live_merchant_total_minor=149,  # different from 99
    )
    assert result.status == "HOLD"
