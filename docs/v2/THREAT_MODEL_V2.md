# Threat Model V2

## Arithmetic Threats

| Threat | Mitigation |
|--------|------------|
| Floating-point drift | Decimal only; no float for settlement |
| Rounding manipulation | Explicit scale + rounding mode under rule pack |
| Price substitution | Cart digest + calculation digest + execution-time check |
| Stale price | Revalidate merchant total immediately before execute |
| Tax / fee / shipping mismatch | Included in calculation digest; merchant reconciliation |
| Impossible subtotal | Fail closed on negative / inconsistent intermediates |

## Authorization Threats

| Threat | Mitigation |
|--------|------------|
| Cart swap (same total) | Cart digest binds product/variant/qty/price/merchant |
| Merchant swap | Merchant identity bound in authorization |
| Amount reuse | grand_total_minor + calculation_digest bound |
| Expired approval | Hard expiry check |
| Replay | Nonce burned on redemption |
| Nonce reuse | Durable burned set |

## Execution Threats

| Threat | Mitigation |
|--------|------------|
| Duplicate transaction | Idempotency key derived from instruction + nonce |
| Retry duplication | Same key returns prior result, never re-charges |
| Execute before compute / enforce | State machine rejects |
| Changed amount at rail | Execution-time total verification |
| HOLD / DENY execution | Hard rejection |

## Proof Threats

| Threat | Mitigation |
|--------|------------|
| Fake PQC labels | Detect real support; never claim FIPS 204 if unavailable |
| Weak hash misuse | SHA-256 only; ban Python built-in hash() for digests |
| Nondeterministic digest | Canonical serialization with sorted keys |
| Receipt mutation | Append-only; chain verification |
| Broken chain | Detect and treat as incident |

## Privacy Threats

| Threat | Mitigation |
|--------|------------|
| PII leakage | Deterministic Class-1 redaction before LLM / external |
| Logs | No raw PAN / secrets |
| Human contractor oversharing | Least-privilege scoped tasks, tokenized IDs |
| Raw payment credentials | Tokenized only; never commit real credentials |
