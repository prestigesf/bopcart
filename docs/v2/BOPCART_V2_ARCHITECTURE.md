# BOPCART V2 — Calculation-First Verified Execution

**Status:** Additive layer on top of existing V1  
**Repository:** prestigesf/bopcart  
**Branch:** additive/bopcart-v2-calculation-first  

## Governing Principle

> NEVER ATTEST UNTIL THE CALCULATION PATH IS PROVEN.

A valid cryptographic signature proves the integrity and authenticity of the signed record.  
It does **not** prove that the mathematics inside that record is correct.

Therefore BOPCART V2 inserts a deterministic economic calculation boundary **before** authorization or cryptographic attestation.

## Canonical Sequence

```
INTENT
  ↓
RULE
  ↓
COMPUTE
  ↓
ENFORCE
  ↓
ATTEST
  ↓
AUTHORIZE / HUMAN KEY IF REQUIRED
  ↓
EXECUTE
  ↓
VERIFY OUTCOME
  ↓
RECEIPT
  ↓
PROOF CONTINUITY
```

Short form:

**RULE → COMPUTE → ENFORCE → ATTEST → EXECUTE → RECEIPT**

The payment/procurement rail executes a deterministic instruction.  
It does not calculate or decide the amount.

## Relationship to V1

V1 (August 11, 2026 baseline) established:

- Verify-then-Execute
- Human Key / HITL cryptographic authorization
- Constitution / governance rules
- Treasury
- Tamper-evident hash-chained ledger
- Cart-bound approval, nonce, expiration, idempotency

V2 does **not** invalidate or modify V1.  
V2 extends it with a deterministic calculation layer before attestation.

See `V1_TO_V2_LINEAGE.md` and `V1_PRESERVATION_MANIFEST.md`.

## Key Modules (bopcart_v2/)

| Module | Responsibility |
|--------|----------------|
| `calculation_engine.py` | Decimal-based authoritative money math |
| `canonical.py` | Deterministic serialization + SHA-256 digests |
| `rule_resolution.py` | Resolve applicable rule pack before compute |
| `enforcement_gate.py` | ALLOW / DENY / ESCALATE / HOLD |
| `authorization.py` | Human Key V2 — tightly bound authorization |
| `proof_continuity.py` | Attestation objects + crypto status detection |
| `execution_instruction.py` | Fully resolved instruction for the rail |
| `execution_adapter.py` | Dumb payment rail (simulated) |
| `idempotency.py` | Deterministic idempotency keys |
| `receipt.py` | Append-only receipt chain |
| `schemas.py` | Typed Pydantic models |
| `errors.py` | Fail-closed typed errors |

## Trust Statement

The applicable rules were resolved, the economic result was deterministically computed, the result was checked against authority and budget, the exact state was cryptographically bound, and only then was execution permitted.
