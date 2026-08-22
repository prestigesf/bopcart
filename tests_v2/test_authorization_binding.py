"""Human Key V2 binding tests."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest

from bopcart_v2.authorization import issue_authorization, verify_and_redeem
from bopcart_v2.calculation_engine import calculate, cart_digest
from bopcart_v2.enforcement_gate import enforce
from bopcart_v2.errors import AuthorizationMismatchError, ExpiredAuthorizationError, ReplayDetectedError
from bopcart_v2.rule_resolution import resolve_rules
from bopcart_v2.schemas import Cart, CartLine, Verdict


def _setup(price="9.99"):
    rule = resolve_rules()
    line = CartLine(product_id="p", unit_price=Decimal(price), quantity=1, merchant_id="merchant-a")
    cart = Cart(lines=[line], merchant_id="merchant-a")
    calc = calculate([line], budget_cap="20.00", rule=rule)
    decision = enforce(calc, cart_digest=cart_digest(cart), merchant_identity="merchant-a", rule=rule)
    return cart, calc, decision


def test_same_total_different_cart_fails():
    cart_a, calc_a, decision_a = _setup("20.00")
    auth = issue_authorization(
        intent_id="i1",
        cart_digest=cart_digest(cart_a),
        merchant_identity="merchant-a",
        calc=calc_a,
        decision=decision_a,
    )
    # Different product, same price
    line_b = CartLine(product_id="OTHER", unit_price=Decimal("20.00"), quantity=1, merchant_id="merchant-a")
    cart_b = Cart(lines=[line_b], merchant_id="merchant-a")
    burned = set()
    with pytest.raises(AuthorizationMismatchError):
        verify_and_redeem(
            auth,
            current_cart_digest=cart_digest(cart_b),
            current_calc_digest=calc_a.calculation_digest,
            current_merchant="merchant-a",
            current_grand_total_minor=calc_a.grand_total_minor,
            burned_nonces=burned,
        )


def test_merchant_change_fails():
    cart, calc, decision = _setup()
    auth = issue_authorization(
        intent_id="i1",
        cart_digest=cart_digest(cart),
        merchant_identity="merchant-a",
        calc=calc,
        decision=decision,
    )
    burned = set()
    with pytest.raises(AuthorizationMismatchError):
        verify_and_redeem(
            auth,
            current_cart_digest=cart_digest(cart),
            current_calc_digest=calc.calculation_digest,
            current_merchant="merchant-b",
            current_grand_total_minor=calc.grand_total_minor,
            burned_nonces=burned,
        )


def test_expired_fails():
    cart, calc, decision = _setup()
    auth = issue_authorization(
        intent_id="i1",
        cart_digest=cart_digest(cart),
        merchant_identity="merchant-a",
        calc=calc,
        decision=decision,
        ttl_seconds=1,
    )
    # Force expiry
    auth = auth.model_copy(update={"expires_at": datetime.now(timezone.utc) - timedelta(seconds=10)})
    burned = set()
    with pytest.raises(ExpiredAuthorizationError):
        verify_and_redeem(
            auth,
            current_cart_digest=cart_digest(cart),
            current_calc_digest=calc.calculation_digest,
            current_merchant="merchant-a",
            current_grand_total_minor=calc.grand_total_minor,
            burned_nonces=burned,
        )


def test_nonce_replay_fails():
    cart, calc, decision = _setup()
    auth = issue_authorization(
        intent_id="i1",
        cart_digest=cart_digest(cart),
        merchant_identity="merchant-a",
        calc=calc,
        decision=decision,
    )
    burned = set()
    verify_and_redeem(
        auth,
        current_cart_digest=cart_digest(cart),
        current_calc_digest=calc.calculation_digest,
        current_merchant="merchant-a",
        current_grand_total_minor=calc.grand_total_minor,
        burned_nonces=burned,
    )
    with pytest.raises(ReplayDetectedError):
        verify_and_redeem(
            auth,
            current_cart_digest=cart_digest(cart),
            current_calc_digest=calc.calculation_digest,
            current_merchant="merchant-a",
            current_grand_total_minor=calc.grand_total_minor,
            burned_nonces=burned,
        )
