"""
BOPCART V2 Calculation Engine

Authoritative money MUST be deterministic.
NEVER use binary floating-point for settlement math.
Fail closed on any invalid or unknown economic input.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, getcontext
from typing import List, Optional, Sequence, Union

from .canonical import sha256_digest
from .errors import BudgetExceededError, CalculationError
from .schemas import CalculationResult, Cart, CartLine, RuleResolution


# High precision working context; we quantize explicitly at the end.
getcontext().prec = 50

USD_SCALE = Decimal("0.01")
DEFAULT_CURRENCY = "USD"
DEFAULT_SCALE = 2
DEFAULT_ROUNDING = ROUND_HALF_EVEN


def _to_decimal(value: Union[str, int, float, Decimal]) -> Decimal:
    """Strict conversion. Reject NaN/Inf/float surprises."""
    if isinstance(value, float):
        raise CalculationError("float is forbidden for authoritative money; use Decimal or str")
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as e:
        raise CalculationError(f"malformed decimal input: {value!r}") from e
    if not d.is_finite():
        raise CalculationError(f"non-finite value not allowed: {value!r}")
    return d


def quantize_money(amount: Decimal, scale: int = DEFAULT_SCALE, rounding=DEFAULT_ROUNDING) -> Decimal:
    """Deterministic quantization to currency minor units."""
    if scale < 0:
        raise CalculationError("currency scale must be non-negative")
    quant = Decimal(10) ** -scale
    return amount.quantize(quant, rounding=rounding)


def compute_line_subtotal(unit_price: Decimal, quantity: int, scale: int = DEFAULT_SCALE) -> Decimal:
    if quantity < 0:
        raise CalculationError("negative quantity not allowed")
    if unit_price < 0:
        raise CalculationError("negative unit_price not allowed")
    raw = unit_price * Decimal(quantity)
    return quantize_money(raw, scale=scale)


def calculate(
    lines: Sequence[CartLine],
    *,
    discount: Union[str, Decimal] = "0",
    shipping: Union[str, Decimal] = "0",
    fees: Union[str, Decimal] = "0",
    tax: Union[str, Decimal] = "0",
    budget_cap: Union[str, Decimal],
    rule: RuleResolution,
    currency: str = DEFAULT_CURRENCY,
) -> CalculationResult:
    """
    Deterministic calculation path.

    Canonical equations:
      line_subtotal = Σ quantize(unit_price × quantity)
      pre_tax_total = line_subtotal - discount + shipping + fees
      grand_total   = pre_tax_total + tax
      remaining_budget = budget_cap - grand_total
    """
    if rule.status != "RESOLVED" and getattr(rule.status, "value", rule.status) != "RESOLVED":
        raise CalculationError("cannot calculate under unresolved or HOLD rule status")

    scale = rule.currency_scale
    rounding = DEFAULT_ROUNDING  # map string if needed later

    if not lines:
        raise CalculationError("cart has no lines")

    # Validate all lines
    unit_prices: List[Decimal] = []
    quantities: List[int] = []
    line_subtotals: List[Decimal] = []
    validated_lines: List[CartLine] = []

    for line in lines:
        if line.currency != currency and line.currency != rule.currency:
            raise CalculationError(f"currency mismatch on line: {line.currency}")
        up = _to_decimal(line.unit_price)
        qty = int(line.quantity)
        if qty < 1:
            raise CalculationError("quantity must be >= 1")
        if up < 0:
            raise CalculationError("negative unit_price")
        ls = compute_line_subtotal(up, qty, scale=scale)
        unit_prices.append(up)
        quantities.append(qty)
        line_subtotals.append(ls)
        validated_lines.append(line)

    line_subtotal = quantize_money(sum(line_subtotals, Decimal("0")), scale=scale)

    disc = quantize_money(_to_decimal(discount), scale=scale)
    ship = quantize_money(_to_decimal(shipping), scale=scale)
    fee = quantize_money(_to_decimal(fees), scale=scale)
    tx = quantize_money(_to_decimal(tax), scale=scale)
    cap = quantize_money(_to_decimal(budget_cap), scale=scale)

    if disc < 0 or ship < 0 or fee < 0 or tx < 0:
        raise CalculationError("negative discount/shipping/fees/tax not allowed")

    pre_tax = quantize_money(line_subtotal - disc + ship + fee, scale=scale)
    if pre_tax < 0:
        raise CalculationError("impossible pre_tax_total (negative)")

    grand = quantize_money(pre_tax + tx, scale=scale)
    remaining = quantize_money(cap - grand, scale=scale)

    # Minor units (integer)
    factor = Decimal(10) ** scale
    grand_minor = int(grand * factor)
    cap_minor = int(cap * factor)

    # Build digest payload (order-independent where possible)
    digest_payload = {
        "calculation_schema": rule.calculation_schema,
        "currency": currency,
        "currency_scale": scale,
        "lines": [
            {
                "product_id": ln.product_id,
                "variant": ln.variant,
                "unit_price": str(up),
                "quantity": qty,
                "merchant_id": ln.merchant_id,
            }
            for ln, up, qty in zip(validated_lines, unit_prices, quantities)
        ],
        "line_subtotal": str(line_subtotal),
        "discount": str(disc),
        "shipping": str(ship),
        "fees": str(fee),
        "tax": str(tx),
        "pre_tax_total": str(pre_tax),
        "grand_total": str(grand),
        "budget_cap": str(cap),
        "remaining_budget": str(remaining),
        "rule_pack_id": rule.rule_pack_id,
        "rule_pack_version": rule.rule_pack_version,
    }

    calc_digest = sha256_digest(digest_payload)

    status = "COMPUTED"
    if remaining < 0:
        # Still return the result so enforcement can DENY; do not raise here
        # so caller can decide HOLD vs DENY based on policy.
        status = "BUDGET_EXCEEDED"

    return CalculationResult(
        calculation_schema=rule.calculation_schema,
        currency=currency,
        currency_scale=scale,
        lines=list(validated_lines),
        unit_prices=unit_prices,
        quantities=quantities,
        line_subtotals=line_subtotals,
        line_subtotal=line_subtotal,
        discount=disc,
        shipping=ship,
        fees=fee,
        tax=tx,
        pre_tax_total=pre_tax,
        grand_total=grand,
        budget_cap=cap,
        remaining_budget=remaining,
        grand_total_minor=grand_minor,
        budget_cap_minor=cap_minor,
        calculation_digest=calc_digest,
        rule_pack_id=rule.rule_pack_id,
        rule_pack_version=rule.rule_pack_version,
        status=status,
    )


def cart_digest(cart: Cart) -> str:
    """Digest that prevents same-total cart substitution."""
    payload = {
        "currency": cart.currency,
        "merchant_id": cart.merchant_id,
        "lines": sorted(
            [
                {
                    "product_id": ln.product_id,
                    "variant": ln.variant,
                    "unit_price": str(ln.unit_price),
                    "quantity": ln.quantity,
                    "merchant_id": ln.merchant_id,
                }
                for ln in cart.lines
            ],
            key=lambda d: (d["merchant_id"], d["product_id"], d.get("variant") or ""),
        ),
    }
    return sha256_digest(payload)
