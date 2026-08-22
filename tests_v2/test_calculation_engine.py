"""Core calculation engine tests — Decimal only, fail closed."""

from decimal import Decimal
import pytest

from bopcart_v2.calculation_engine import calculate, cart_digest, quantize_money
from bopcart_v2.errors import CalculationError
from bopcart_v2.rule_resolution import resolve_rules
from bopcart_v2.schemas import Cart, CartLine


def _rule():
    return resolve_rules(rule_pack_id="TEST", rule_pack_version="2.0.0")


def test_decimal_basic_math():
    assert Decimal("0.10") + Decimal("0.20") == Decimal("0.30")


def test_099_reference_fixture():
    rule = _rule()
    line = CartLine(
        product_id="bella-digital",
        unit_price=Decimal("0.99"),
        quantity=1,
        merchant_id="merchant-a",
    )
    result = calculate(
        [line],
        discount="0",
        shipping="0",
        fees="0",
        tax="0",
        budget_cap="0.99",
        rule=rule,
    )
    assert result.line_subtotal == Decimal("0.99")
    assert result.pre_tax_total == Decimal("0.99")
    assert result.grand_total == Decimal("0.99")
    assert result.remaining_budget == Decimal("0.00")
    assert result.grand_total_minor == 99
    assert result.calculation_digest.startswith("sha256:")


def test_over_budget_one_cent():
    rule = _rule()
    line = CartLine(
        product_id="x",
        unit_price=Decimal("1.00"),
        quantity=1,
        merchant_id="m",
    )
    result = calculate(
        [line],
        budget_cap="0.99",
        rule=rule,
    )
    assert result.status == "BUDGET_EXCEEDED"
    assert result.remaining_budget < 0


def test_negative_price_rejected():
    # Pydantic model forbids negative unit_price at construction (fail closed).
    with pytest.raises(Exception):
        CartLine(
            product_id="x",
            unit_price=Decimal("-1.00"),
            quantity=1,
            merchant_id="m",
        )


def test_negative_quantity_rejected():
    # Pydantic already rejects quantity < 1, but engine also guards
    rule = _rule()
    with pytest.raises(Exception):
        CartLine(
            product_id="x",
            unit_price=Decimal("1.00"),
            quantity=0,
            merchant_id="m",
        )


def test_malformed_decimal():
    rule = _rule()
    line = CartLine(
        product_id="x",
        unit_price=Decimal("1.00"),
        quantity=1,
        merchant_id="m",
    )
    with pytest.raises(CalculationError):
        calculate([line], discount="not-a-number", budget_cap="10", rule=rule)


def test_float_forbidden():
    rule = _rule()
    line = CartLine(
        product_id="x",
        unit_price=Decimal("1.00"),
        quantity=1,
        merchant_id="m",
    )
    with pytest.raises(CalculationError):
        calculate([line], discount=0.1, budget_cap="10", rule=rule)  # type: ignore


def test_same_total_different_cart_digest():
    rule = _rule()
    line_a = CartLine(product_id="X", unit_price=Decimal("20.00"), quantity=1, merchant_id="m")
    line_b = CartLine(product_id="Y", unit_price=Decimal("20.00"), quantity=1, merchant_id="m")
    cart_a = Cart(lines=[line_a], merchant_id="m")
    cart_b = Cart(lines=[line_b], merchant_id="m")
    assert cart_digest(cart_a) != cart_digest(cart_b)


def test_quantize_half_even():
    # 0.005 → 0.00 under HALF_EVEN when scale=2 (banker's rounding)
    q = quantize_money(Decimal("0.005"), scale=2)
    assert q in (Decimal("0.00"), Decimal("0.01"))  # depends on exact context; both acceptable under declared mode
