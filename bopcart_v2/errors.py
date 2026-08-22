"""Typed errors for BOPCART V2. Fail closed. No secret leakage in messages."""

from __future__ import annotations


class BopcartV2Error(Exception):
    """Base for all V2 errors."""


class CalculationError(BopcartV2Error):
    """Authoritative calculation failed or inputs invalid."""


class RuleResolutionError(BopcartV2Error):
    """Applicable rule pack could not be resolved."""


class BudgetExceededError(BopcartV2Error):
    """Grand total exceeds budget_cap."""


class MerchantTotalMismatchError(BopcartV2Error):
    """Local computed total does not match merchant execution total."""


class AuthorizationMismatchError(BopcartV2Error):
    """Authorization does not bind to current cart/calculation/merchant/amount."""


class ExpiredAuthorizationError(BopcartV2Error):
    """Authorization has expired."""


class ReplayDetectedError(BopcartV2Error):
    """Nonce or idempotency key already used."""


class ExecutionStateError(BopcartV2Error):
    """Execution attempted in invalid state (e.g. before compute, while HOLD/DENY)."""


class ReceiptVerificationError(BopcartV2Error):
    """Receipt chain integrity failure."""


class CryptoUnavailableError(BopcartV2Error):
    """Requested cryptographic capability (e.g. ML-DSA-65) is unavailable."""
