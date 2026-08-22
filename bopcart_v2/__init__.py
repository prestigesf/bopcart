"""
BOPCART V2 — Calculation-First Verified Execution

Additive layer on top of the existing V1 Verify-then-Execute architecture.
Does not modify any V1 files.
"""

__version__ = "2.0.0"
__schema__ = "BOPCART_CALC_V2"

from .schemas import (
    Money,
    CartLine,
    Cart,
    RuleResolution,
    CalculationResult,
    EnforcementDecision,
    Authorization,
    ExecutionInstruction,
    ExecutionResult,
    ProofObject,
    Receipt,
)
from .errors import (
    CalculationError,
    RuleResolutionError,
    BudgetExceededError,
    MerchantTotalMismatchError,
    AuthorizationMismatchError,
    ExpiredAuthorizationError,
    ReplayDetectedError,
    ExecutionStateError,
    ReceiptVerificationError,
    CryptoUnavailableError,
)

__all__ = [
    "Money",
    "CartLine",
    "Cart",
    "RuleResolution",
    "CalculationResult",
    "EnforcementDecision",
    "Authorization",
    "ExecutionInstruction",
    "ExecutionResult",
    "ProofObject",
    "Receipt",
    "CalculationError",
    "RuleResolutionError",
    "BudgetExceededError",
    "MerchantTotalMismatchError",
    "AuthorizationMismatchError",
    "ExpiredAuthorizationError",
    "ReplayDetectedError",
    "ExecutionStateError",
    "ReceiptVerificationError",
    "CryptoUnavailableError",
]
