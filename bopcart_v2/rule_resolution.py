"""
Rule resolution before authoritative calculation.
If a material economic rule cannot be resolved → HOLD.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from .errors import RuleResolutionError
from .schemas import RuleResolution, RuleStatus


def resolve_rules(
    *,
    rule_pack_id: str = "BOPCART_DEFAULT",
    rule_pack_version: str = "2.0.0",
    currency: str = "USD",
    currency_scale: int = 2,
    rounding_mode: str = "ROUND_HALF_EVEN",
    merchant_policy: Optional[str] = None,
    budget_policy: Optional[str] = None,
    approval_threshold: Optional[Decimal] = None,
    jurisdiction: Optional[str] = None,
    tax_source: Optional[str] = None,
    confidence: float = 1.0,
    force_hold: bool = False,
) -> RuleResolution:
    """
    Establish the applicable rule state.
    Returns RESOLVED, UNKNOWN, or HOLD.
    """
    if force_hold:
        return RuleResolution(
            rule_pack_id=rule_pack_id,
            rule_pack_version=rule_pack_version,
            currency=currency,
            currency_scale=currency_scale,
            rounding_mode=rounding_mode,
            status=RuleStatus.HOLD,
            confidence=0.0,
        )

    if not rule_pack_id or not rule_pack_version:
        return RuleResolution(
            rule_pack_id=rule_pack_id or "UNKNOWN",
            rule_pack_version=rule_pack_version or "UNKNOWN",
            status=RuleStatus.UNKNOWN,
            confidence=0.0,
        )

    return RuleResolution(
        rule_pack_id=rule_pack_id,
        rule_pack_version=rule_pack_version,
        currency=currency,
        currency_scale=currency_scale,
        rounding_mode=rounding_mode,
        merchant_policy=merchant_policy,
        budget_policy=budget_policy,
        approval_threshold=approval_threshold,
        jurisdiction=jurisdiction,
        tax_source=tax_source,
        calculation_schema="BOPCART_CALC_V2",
        confidence=confidence,
        status=RuleStatus.RESOLVED,
    )
