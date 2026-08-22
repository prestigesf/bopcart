"""
Deterministic idempotency boundaries.
"""

from __future__ import annotations

from .canonical import sha256_digest


def make_idempotency_key(
    execution_instruction_digest: str,
    authorization_nonce: str,
) -> str:
    """
    SHA-256 of canonical combination.
    Different instruction or different nonce → different key.
    """
    payload = {
        "execution_instruction_digest": execution_instruction_digest,
        "authorization_nonce": authorization_nonce,
    }
    return sha256_digest(payload)
