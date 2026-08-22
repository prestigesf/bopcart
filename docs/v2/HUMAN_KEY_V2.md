# Human Key V2

## Design Goal

A user is **not** approving merely “$99”.

A V2 approval means:

> Approve this exact cart, this exact merchant, this exact calculated total, under this exact rule/calculation version.

## Bound Fields

- `authorization_id`
- `intent_id`
- `cart_digest`
- `merchant_identity`
- `grand_total_minor`
- `currency`
- `budget_cap_minor`
- `calculation_digest`
- `calculation_schema`
- `rule_pack_id` / `rule_pack_version`
- `expires_at`
- `nonce`
- `idempotency_key`

## Failure Modes (all hard)

- Different cart, same total → fail
- Different merchant, same cart total → fail
- Changed quantity → fail
- Changed tax / shipping / fees → fail
- Changed calculation digest → fail
- Expired → fail
- Nonce replay → fail

## 2-of-3 Delegated Authority (Architectural Analogy)

1. User / Cedar Intent
2. VenturePilot-derived Vault / Policy Authority
3. Human / Execution Gate

This is an application-level model.  
It is **not** literal Bitcoin multisig unless actual cryptographic multisig is implemented.
