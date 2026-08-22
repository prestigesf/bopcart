"""
Human Key V2 — narrow, strongly bound authorization.
Binds cart, merchant, exact calculated total, rule version, etc.
"""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Set

from .canonical import sha256_digest
from .errors import (
    AuthorizationMismatchError,
    ExpiredAuthorizationError,
    ReplayDetectedError,
)
from .schemas import Authorization, CalculationResult, EnforcementDecision


def issue_authorization(
    *,
    intent_id: str,
    cart_digest: str,
    merchant_identity: str,
    calc: CalculationResult,
    decision: EnforcementDecision,
    ttl_seconds: int = 900,
    burned_nonces: Optional[Set[str]] = None,
) -> Authorization:
    """Issue a V2 authorization bound to exact economic state."""
    if decision.verdict.value not in ("ALLOW", "ESCALATE"):
        raise AuthorizationMismatchError(f"cannot authorize under verdict {decision.verdict}")

    now = datetime.now(timezone.utc)
    nonce = secrets.token_urlsafe(16)
    auth_id = str(uuid.uuid4())
    expires = now + timedelta(seconds=ttl_seconds)

    # Idempotency key derived from nonce + digests
    idemp_payload = {
        "nonce": nonce,
        "cart_digest": cart_digest,
        "calculation_digest": calc.calculation_digest,
        "merchant": merchant_identity,
    }
    idempotency_key = sha256_digest(idemp_payload)[7:]  # pure hex for key

    auth = Authorization(
        authorization_id=auth_id,
        intent_id=intent_id,
        cart_digest=cart_digest,
        merchant_identity=merchant_identity,
        grand_total_minor=calc.grand_total_minor,
        currency=calc.currency,
        budget_cap_minor=calc.budget_cap_minor,
        calculation_digest=calc.calculation_digest,
        calculation_schema=calc.calculation_schema,
        rule_pack_id=calc.rule_pack_id,
        rule_pack_version=calc.rule_pack_version,
        expires_at=expires,
        nonce=nonce,
        idempotency_key=idempotency_key,
        authorization_status="ISSUED",
    )

    # Compute authorization digest
    digest_payload = {
        "authorization_id": auth.authorization_id,
        "intent_id": auth.intent_id,
        "cart_digest": auth.cart_digest,
        "merchant_identity": auth.merchant_identity,
        "grand_total_minor": auth.grand_total_minor,
        "currency": auth.currency,
        "budget_cap_minor": auth.budget_cap_minor,
        "calculation_digest": auth.calculation_digest,
        "calculation_schema": auth.calculation_schema,
        "rule_pack_id": auth.rule_pack_id,
        "rule_pack_version": auth.rule_pack_version,
        "expires_at": auth.expires_at.isoformat(),
        "nonce": auth.nonce,
        "idempotency_key": auth.idempotency_key,
    }
    # Re-create with digest
    return auth.model_copy(update={"authorization_digest": sha256_digest(digest_payload)})


def verify_and_redeem(
    auth: Authorization,
    *,
    current_cart_digest: str,
    current_calc_digest: str,
    current_merchant: str,
    current_grand_total_minor: int,
    burned_nonces: Set[str],
    now: Optional[datetime] = None,
) -> str:
    """
    Verify binding and burn nonce.
    Returns the idempotency_key on success.
    Raises on any mismatch / expiry / replay.
    """
    now = now or datetime.now(timezone.utc)

    if auth.authorization_status != "ISSUED":
        raise AuthorizationMismatchError(f"status is {auth.authorization_status}")

    if now > auth.expires_at:
        raise ExpiredAuthorizationError("authorization expired")

    if auth.nonce in burned_nonces:
        raise ReplayDetectedError("nonce already redeemed")

    if auth.cart_digest != current_cart_digest:
        raise AuthorizationMismatchError("cart_digest mismatch")
    if auth.calculation_digest != current_calc_digest:
        raise AuthorizationMismatchError("calculation_digest mismatch")
    if auth.merchant_identity != current_merchant:
        raise AuthorizationMismatchError("merchant mismatch")
    if auth.grand_total_minor != current_grand_total_minor:
        raise AuthorizationMismatchError("amount mismatch")

    burned_nonces.add(auth.nonce)
    return auth.idempotency_key
