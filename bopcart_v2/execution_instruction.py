"""
Deterministic execution instruction.
The payment rail receives this and must not recalculate.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from .canonical import sha256_digest
from .schemas import Authorization, CalculationResult, ExecutionInstruction


def build_execution_instruction(
    *,
    intent_id: str,
    merchant_id: str,
    calc: CalculationResult,
    auth: Authorization,
    ttl_seconds: int = 300,
) -> ExecutionInstruction:
    now = datetime.now(timezone.utc)
    instr_id = str(uuid.uuid4())

    instr = ExecutionInstruction(
        instruction_id=instr_id,
        intent_id=intent_id,
        merchant_id=merchant_id,
        currency=calc.currency,
        grand_total_minor=calc.grand_total_minor,
        cart_digest=auth.cart_digest,
        calculation_digest=calc.calculation_digest,
        authorization_digest=auth.authorization_digest or "",
        rule_pack_id=calc.rule_pack_id,
        rule_pack_version=calc.rule_pack_version,
        idempotency_key=auth.idempotency_key,
        created_at=now,
        expires_at=now + timedelta(seconds=ttl_seconds),
    )

    payload = {
        "instruction_id": instr.instruction_id,
        "intent_id": instr.intent_id,
        "merchant_id": instr.merchant_id,
        "currency": instr.currency,
        "grand_total_minor": instr.grand_total_minor,
        "cart_digest": instr.cart_digest,
        "calculation_digest": instr.calculation_digest,
        "authorization_digest": instr.authorization_digest,
        "rule_pack_id": instr.rule_pack_id,
        "rule_pack_version": instr.rule_pack_version,
        "idempotency_key": instr.idempotency_key,
        "created_at": instr.created_at.isoformat(),
        "expires_at": instr.expires_at.isoformat(),
    }
    digest = sha256_digest(payload)
    return instr.model_copy(update={"execution_instruction_digest": digest})
