"""
Enforcement gate. Consumes COMPUTE result. Does not recalculate money.
Verdicts: ALLOW | DENY | ESCALATE | HOLD
"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from .schemas import (
    CalculationResult,
    EnforcementDecision,
    RuleResolution,
    Verdict,
)


def enforce(
    calc: CalculationResult,
    *,
    cart_digest: str,
    merchant_identity: str,
    rule: RuleResolution,
    requires_human_key: bool = False,
    merchant_total_minor: Optional[int] = None,
    tolerance_minor: int = 0,
) -> EnforcementDecision:
    """
    Deterministic enforcement.
    Never independently calculates money.
    """
    reasons: List[str] = []
    rule_ids: List[str] = []

    if rule.status.value != "RESOLVED":
        return EnforcementDecision(
            verdict=Verdict.HOLD,
            rule_ids=["R-RULE-UNRESOLVED"],
            reasons=["rule status is not RESOLVED"],
            calculation_digest=calc.calculation_digest,
            cart_digest=cart_digest,
            requires_human_key=True,
        )

    if calc.status == "BUDGET_EXCEEDED" or calc.remaining_budget < 0:
        return EnforcementDecision(
            verdict=Verdict.DENY,
            rule_ids=["R-BUDGET"],
            reasons=[f"grand_total {calc.grand_total} exceeds budget_cap {calc.budget_cap}"],
            calculation_digest=calc.calculation_digest,
            cart_digest=cart_digest,
            requires_human_key=False,
        )

    # Merchant reconciliation
    if merchant_total_minor is not None:
        diff = abs(calc.grand_total_minor - merchant_total_minor)
        if diff > tolerance_minor:
            return EnforcementDecision(
                verdict=Verdict.HOLD,
                rule_ids=["R-MERCHANT-MISMATCH"],
                reasons=[
                    f"local grand_total_minor={calc.grand_total_minor} "
                    f"vs merchant={merchant_total_minor} (tolerance={tolerance_minor})"
                ],
                calculation_digest=calc.calculation_digest,
                cart_digest=cart_digest,
                requires_human_key=True,
            )

    # Default policy: small amounts may auto-allow; larger require key
    threshold = rule.approval_threshold
    if threshold is not None and calc.grand_total >= threshold:
        requires_human_key = True

    if requires_human_key:
        return EnforcementDecision(
            verdict=Verdict.ESCALATE,
            rule_ids=["R-HUMAN-KEY"],
            reasons=["requires Human Key authorization"],
            calculation_digest=calc.calculation_digest,
            cart_digest=cart_digest,
            requires_human_key=True,
        )

    return EnforcementDecision(
        verdict=Verdict.ALLOW,
        rule_ids=["R-000"],
        reasons=["all checks passed"],
        calculation_digest=calc.calculation_digest,
        cart_digest=cart_digest,
        requires_human_key=False,
    )
