"""
Append-only receipt chain.
Corrections become new linked receipts.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from .canonical import sha256_digest
from .errors import ReceiptVerificationError
from .schemas import Receipt


def create_receipt(
    *,
    intent_id: str,
    rule_pack_id: str,
    rule_pack_version: str,
    input_digest: str,
    cart_digest: str,
    calculation_digest: str,
    authorization_digest: str,
    execution_instruction_digest: str,
    external_transaction_reference: Optional[str],
    execution_status: str,
    currency: str,
    grand_total_minor: int,
    previous_receipt_digest: Optional[str] = None,
    signature_metadata: Optional[dict] = None,
) -> Receipt:
    receipt_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    body = {
        "receipt_id": receipt_id,
        "intent_id": intent_id,
        "rule_pack_id": rule_pack_id,
        "rule_pack_version": rule_pack_version,
        "input_digest": input_digest,
        "cart_digest": cart_digest,
        "calculation_digest": calculation_digest,
        "authorization_digest": authorization_digest,
        "execution_instruction_digest": execution_instruction_digest,
        "external_transaction_reference": external_transaction_reference,
        "execution_status": execution_status,
        "currency": currency,
        "grand_total_minor": grand_total_minor,
        "created_at": now.isoformat(),
        "previous_receipt_digest": previous_receipt_digest,
    }
    digest = sha256_digest(body)

    return Receipt(
        receipt_id=receipt_id,
        intent_id=intent_id,
        rule_pack_id=rule_pack_id,
        rule_pack_version=rule_pack_version,
        input_digest=input_digest,
        cart_digest=cart_digest,
        calculation_digest=calculation_digest,
        authorization_digest=authorization_digest,
        execution_instruction_digest=execution_instruction_digest,
        external_transaction_reference=external_transaction_reference,
        execution_status=execution_status,
        currency=currency,
        grand_total_minor=grand_total_minor,
        created_at=now,
        previous_receipt_digest=previous_receipt_digest,
        receipt_digest=digest,
        signature_metadata=signature_metadata or {},
    )


def verify_chain(receipts: List[Receipt]) -> Optional[int]:
    """
    Walk the chain. Return index of first break, or None if intact.
    """
    if not receipts:
        return None
    prev = None
    for i, r in enumerate(receipts):
        # Recompute digest
        body = {
            "receipt_id": r.receipt_id,
            "intent_id": r.intent_id,
            "rule_pack_id": r.rule_pack_id,
            "rule_pack_version": r.rule_pack_version,
            "input_digest": r.input_digest,
            "cart_digest": r.cart_digest,
            "calculation_digest": r.calculation_digest,
            "authorization_digest": r.authorization_digest,
            "execution_instruction_digest": r.execution_instruction_digest,
            "external_transaction_reference": r.external_transaction_reference,
            "execution_status": r.execution_status,
            "currency": r.currency,
            "grand_total_minor": r.grand_total_minor,
            "created_at": r.created_at.isoformat(),
            "previous_receipt_digest": r.previous_receipt_digest,
        }
        expected = sha256_digest(body)
        if r.receipt_digest != expected:
            return i
        if i == 0:
            if r.previous_receipt_digest is not None:
                # First should have no previous or genesis
                pass
        else:
            if r.previous_receipt_digest != prev:
                return i
        prev = r.receipt_digest
    return None
