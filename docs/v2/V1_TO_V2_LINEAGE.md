# V1 → V2 Architectural Lineage

## V1 — Verify-then-Execute (August 11, 2026 baseline)

The original BOPCART architecture correctly focused on:

- Controlled autonomy (99% research / preparation autonomy)
- Human Key authorization (cart-bound, expiring, single-use)
- Policy / constitution enforcement
- Treasury management
- Tamper-evident hash-chained audit ledger

Core loop (from the preserved SKILL.md and earlier design):

```
OBSERVE → PLAN → JUDGE → LOG → HUMAN KEY / ALLOW → ACT → SEAL
```

This established safe autonomous procurement under cryptographic human control.

## The Discovery That Produced V2

Later PrestigeSF engine work (DeadlineSF, VenturePilot, GoldTrac) exposed an additional trust boundary:

> A perfectly valid signature can still seal a mathematically incorrect answer.

A cryptographic signature proves the record was not altered after signing and that the holder of the key authorized it.  
It does **not** prove that the numbers inside the record were computed correctly.

Floating-point drift, rounding manipulation, stale prices, tax mismatches, or simple arithmetic errors can all produce a record that signs cleanly yet is economically wrong.

## V2 — Calculation-First Verified Execution

V2 therefore inserts a deterministic calculation layer **before** any attestation or authorization:

```
INTENT → RULE → COMPUTE → ENFORCE → ATTEST → AUTHORIZE → EXECUTE → VERIFY → RECEIPT
```

- Authoritative money uses `Decimal` only (never binary float).
- Every monetary field is quantized under an explicit rule pack.
- Digests bind cart, calculation, authorization, and execution instruction.
- The payment rail is deliberately dumb: it executes an instruction; it never decides the amount.

## This Is Not a Repudiation of V1

V1 remains intact and preserved exactly.  
V2 is the next architectural generation produced after later engine discoveries.

The difference is valuable evidence of engine hardening.
