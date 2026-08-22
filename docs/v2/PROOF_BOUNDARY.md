# Proof Boundary

## What a Cryptographic Signature Proves

- Record authenticity and integrity
- Tamper detection after signing
- Possession / use of the signing key (according to the implementation)

## What a Signature Alone Does **Not** Prove

- The merchant was trustworthy
- The calculation inside the record was mathematically correct
- The product satisfied user intent
- The applicable law / tax rule was correctly interpreted
- External fulfillment succeeded
- No vulnerability exists in the system

Those require separate evidence and control layers:

1. Deterministic calculation engine (this V2 layer)
2. Rule resolution and enforcement
3. Independent outcome verification (Second Look)
4. Provenance / chain-of-custody (GoldTrac)
5. Compliance evidence (DeadlineSF)

## Separation of Concerns

| Layer | Proves |
|-------|--------|
| Deterministic engine | Calculation path was correct under declared rules |
| Signature | The record of that calculation was not altered |
| Human Key | A human authorized *this exact state* |
| Receipt chain | History is append-only and verifiable |
| External verification | Outcome matched mandate |

Do not collapse these into a single claim.
