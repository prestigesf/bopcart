"""
Proof Continuity.

Signature proves the record.
Deterministic engine proves the calculation path that produced the record.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .canonical import sha256_digest
from .schemas import CalculationResult, ProofObject


def build_proof(
    *,
    intent_id: str,
    input_digest: str,
    cart_digest: str,
    calc: CalculationResult,
    authorization_digest: str,
    execution_instruction_digest: str,
    verdict: str,
    signature_suite: Optional[List[Dict[str, Any]]] = None,
) -> ProofObject:
    """Assemble the attestation object. Digests are generated, never hard-coded."""
    return ProofObject(
        schema_name="bopcart.execution.v2",
        calculation_schema=calc.calculation_schema,
        rule_pack_id=calc.rule_pack_id,
        rule_pack_version=calc.rule_pack_version,
        intent_id=intent_id,
        input_digest=input_digest,
        cart_digest=cart_digest,
        calculation_digest=calc.calculation_digest,
        authorization_digest=authorization_digest,
        execution_instruction_digest=execution_instruction_digest,
        grand_total_minor=calc.grand_total_minor,
        currency=calc.currency,
        verdict=verdict,
        signature_suite=signature_suite or [],
    )


def detect_crypto_status() -> Dict[str, str]:
    """
    Detect runtime support for signature algorithms.
    Returns status: REAL | MOCK | UNAVAILABLE | UNVERIFIED
    Never fabricates ML-DSA.
    """
    status = {
        "ECDSA_P256": "UNAVAILABLE",
        "ML_DSA_65": "UNAVAILABLE",
        "FIPS_204": "UNAVAILABLE",
    }

    # Try ECDSA via cryptography library if present
    try:
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives import hashes
        # Just presence check
        status["ECDSA_P256"] = "REAL"
    except ImportError:
        pass

    # ML-DSA-65 (FIPS 204) — only claim REAL if a real provider is importable
    # Common candidates: pqcrypto, dilithium, etc. We do not fake.
    try:
        # Placeholder: real detection would import a concrete FIPS-204 implementation
        # For this environment we correctly report UNAVAILABLE unless proven.
        import importlib
        # Do not invent a module name that does not exist
        status["ML_DSA_65"] = "UNAVAILABLE"
        status["FIPS_204"] = "UNAVAILABLE"
    except Exception:
        status["ML_DSA_65"] = "UNAVAILABLE"
        status["FIPS_204"] = "UNAVAILABLE"

    return status


def mock_signature_label() -> Dict[str, Any]:
    """Visible mock that must never claim FIPS 204 verified."""
    return {
        "signature_status": "MOCK",
        "algorithm_claim": None,
        "fips_204_verified": False,
    }
