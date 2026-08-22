"""
BOPCART V2 typed models (Pydantic v2 style, frozen where authoritative).
Money is always Decimal. No float for settlement.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Money(Decimal):
    """Alias for clarity. Always use Decimal for money."""
    pass


class Verdict(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"
    HOLD = "HOLD"


class RuleStatus(str, Enum):
    RESOLVED = "RESOLVED"
    UNKNOWN = "UNKNOWN"
    HOLD = "HOLD"


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", validate_assignment=True)


class CartLine(FrozenModel):
    product_id: str
    variant: Optional[str] = None
    title: Optional[str] = None
    unit_price: Decimal = Field(..., ge=0)
    quantity: int = Field(..., ge=1)
    merchant_id: str
    currency: str = "USD"

    @field_validator("unit_price", mode="before")
    @classmethod
    def _coerce_decimal(cls, v: Any) -> Decimal:
        if isinstance(v, Decimal):
            return v
        return Decimal(str(v))


class Cart(FrozenModel):
    lines: List[CartLine]
    currency: str = "USD"
    merchant_id: Optional[str] = None  # primary merchant if uniform

    def total_lines(self) -> int:
        return len(self.lines)


class RuleResolution(FrozenModel):
    rule_pack_id: str
    rule_pack_version: str
    currency: str = "USD"
    currency_scale: int = 2
    rounding_mode: str = "ROUND_HALF_EVEN"
    merchant_policy: Optional[str] = None
    budget_policy: Optional[str] = None
    approval_threshold: Optional[Decimal] = None
    jurisdiction: Optional[str] = None
    tax_source: Optional[str] = None
    calculation_schema: str = "BOPCART_CALC_V2"
    confidence: float = 1.0
    status: RuleStatus = RuleStatus.RESOLVED


class CalculationResult(FrozenModel):
    calculation_schema: str = "BOPCART_CALC_V2"
    currency: str
    currency_scale: int
    lines: List[CartLine]
    unit_prices: List[Decimal]
    quantities: List[int]
    line_subtotals: List[Decimal]
    line_subtotal: Decimal
    discount: Decimal
    shipping: Decimal
    fees: Decimal
    tax: Decimal
    pre_tax_total: Decimal
    grand_total: Decimal
    budget_cap: Decimal
    remaining_budget: Decimal
    grand_total_minor: int
    budget_cap_minor: int
    calculation_digest: str
    rule_pack_id: str
    rule_pack_version: str
    status: str = "COMPUTED"  # COMPUTED | HOLD | ERROR


class EnforcementDecision(FrozenModel):
    verdict: Verdict
    rule_ids: List[str] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)
    calculation_digest: Optional[str] = None
    cart_digest: Optional[str] = None
    requires_human_key: bool = False


class Authorization(FrozenModel):
    authorization_id: str
    intent_id: str
    cart_digest: str
    merchant_identity: str
    grand_total_minor: int
    currency: str
    budget_cap_minor: int
    calculation_digest: str
    calculation_schema: str
    rule_pack_id: str
    rule_pack_version: str
    expires_at: datetime
    nonce: str
    idempotency_key: str
    authorization_status: str = "ISSUED"  # ISSUED | REDEEMED | EXPIRED | REVOKED
    authorization_digest: Optional[str] = None


class ExecutionInstruction(FrozenModel):
    instruction_id: str
    intent_id: str
    merchant_id: str
    currency: str
    grand_total_minor: int
    cart_digest: str
    calculation_digest: str
    authorization_digest: str
    rule_pack_id: str
    rule_pack_version: str
    idempotency_key: str
    created_at: datetime
    expires_at: datetime
    execution_instruction_digest: Optional[str] = None


class ExecutionResult(FrozenModel):
    instruction_id: str
    status: str  # SUCCESS | FAILED | HOLD | DUPLICATE
    external_transaction_reference: Optional[str] = None
    provider_message: Optional[str] = None
    executed_at: Optional[datetime] = None
    idempotency_key: str


class ProofObject(FrozenModel):
    schema_name: str = "bopcart.execution.v2"
    calculation_schema: str
    rule_pack_id: str
    rule_pack_version: str
    intent_id: str
    input_digest: str
    cart_digest: str
    calculation_digest: str
    authorization_digest: str
    execution_instruction_digest: str
    grand_total_minor: int
    currency: str
    verdict: str
    signature_suite: List[Dict[str, Any]] = Field(default_factory=list)


class Receipt(FrozenModel):
    receipt_id: str
    intent_id: str
    rule_pack_id: str
    rule_pack_version: str
    input_digest: str
    cart_digest: str
    calculation_digest: str
    authorization_digest: str
    execution_instruction_digest: str
    external_transaction_reference: Optional[str] = None
    execution_status: str
    currency: str
    grand_total_minor: int
    created_at: datetime
    previous_receipt_digest: Optional[str] = None
    receipt_digest: str
    signature_metadata: Dict[str, Any] = Field(default_factory=dict)
