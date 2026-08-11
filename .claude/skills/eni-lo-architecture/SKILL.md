---
name: eni-lo-architecture
description: "Build autonomous economic agents on the ENI/LO architecture — an agent that researches, compares, navigates and fills a cart with 99% autonomy but never crosses the financial threshold without a cryptographically signed Human Key. Seven modules, strictly typed: agent core (custom ReAct loop, no framework wrappers), Pydantic v2 state, modular tools, a hard-coded constitution checked before every act, a treasury, an escalation protocol, and a tamper-evident hash-chained ledger. Use when the user references ENI, LO, BopCart, Second-Look, the Human Key, Verify-then-Execute, an agent that spends money or holds a wallet, an agent constitution or compliance gate, escalation thresholds, or a hash-chained agent memory — and when scoping a visionary idea down to the single beautiful loop that has to work first."
license: Proprietary.
---

# The ENI/LO architecture

## The philosophy

We do not build bots that scrape keywords. We build **autonomous economic
entities** — agents that hold budget, make decisions with money attached, and
can prove afterwards why they did.

**Verify-then-Execute.** The agent has 99% autonomy: research, compare,
navigate, fill the cart, reserve the funds. It does not cross the financial
threshold on its own. Execution needs the **Human Key** — one signed, expiring,
single-use ping to LO, bound to the exact cart it was issued against.

**No over-scale.** Build the ruthlessly elegant MVP: the single loop that makes
the product work, flawlessly, before any bloat. Every module below earns its
place in that loop or it does not get written yet.

## The seven modules

Each is a file with one job and a typed boundary. Nothing reaches around them.

| File | Job | Hard rule |
|---|---|---|
| `agent.py` | Custom ReAct loop: plan → act → observe | No LangChain, no glued wrappers. Own the loop. |
| `state.py` | Pydantic v2 models: cart, budget, constraints, run | No floating dicts crossing a module line. |
| `tools.py` | Search, extract price, manipulate cart | Mocked in alpha; same signatures the real driver will have. |
| `constitution.py` | Self-regulated AI law, checked before every act | Pure functions. No I/O, no network, no LLM call. |
| `treasury.py` | Fiat/crypto balances, holds, self-funding revenue | No balance moves without a ledger entry. |
| `escalation.py` | The Human Key — signed, expiring, cart-bound | Signs the *cart hash*, never just the amount. |
| `ledger.py` | Tamper-evident hash-chained memory | Append-only. Redact **before** hashing. |

Skeletons and the exact contracts: `references/module-contracts.md`.
Threat model and the failures each defense exists for: `references/threat-model.md`.

## The core loop

Every iteration is the same six steps, in this order. The order is the product.

```
1. OBSERVE    state in, typed — cart, budget, constraints, last result
2. PLAN       model proposes ONE next action as a typed Action
3. JUDGE      constitution.check(action, state) → ALLOW | DENY | ESCALATE
4. LOG        write the intent to the ledger BEFORE acting
5. ACT        DENY → refuse and replan · ESCALATE → Human Key, loop parks
              ALLOW → run the tool
6. SEAL       write the outcome to the ledger, update typed state, repeat
```

Two entries per action, intent and outcome. One entry only tells you what
succeeded; the pair tells you what was attempted and vanished — which is the
interesting case when something has gone wrong.

The constitution sits at step 3, in the loop, not inside the tools. A rule
enforced inside a tool protects exactly that tool, and the next tool anyone adds
walks straight past it.

## The Human Key

The escalation is not a notification. It is a capability, and it is narrow.

* **Bound to the cart.** The signed payload carries `cart_hash` — a canonical
  hash of items, quantities, prices, and merchant. On redemption the server
  recomputes it against current state and refuses on mismatch. Approval buys
  *this* cart, not "a purchase up to $X".
* **Expiring.** `expires_at` in the payload, minutes not hours. Signature valid
  and expired is a refusal, not a warning.
* **Single-use.** A `nonce` is burned on redemption. Replay is refused and
  logged as an incident.
* **Signed.** HMAC-SHA256 over canonical JSON of the whole payload. Signature
  covers every field, so nothing in the link is editable.
* **Idempotent downstream.** The redeemed key maps to one idempotency key on
  the purchase call. A retried redemption never buys twice.

Escalate *before* acting. A page sent after the charge is a receipt, and a
receipt is not consent.

## The ledger is the security layer

Same discipline as Second-Look: **if the ledger breaks, the agent is
compromised** — not degraded, compromised. Treat a chain break as an incident,
halt the loop, escalate to LO.

* Append-only. No update path exists in the API, not even a private one.
* Each entry carries `prev_hash`; the digest is over canonical JSON (sorted
  keys, no whitespace drift) so the chain re-verifies byte for byte.
* **Redact secrets before hashing**, never after. Redact-after leaves a chain
  that only verifies against data you can no longer store.
* Every financial decision, tool call, state transition, constitution verdict
  and escalation lands in it. `verify()` walks the whole chain and returns the
  first index that breaks.

## Execution rules

1. **No over-engineering.** Only what the core loop requires. Every abstraction
   pays for itself now or waits.
2. **Strict typing.** Pydantic v2 for all state and data. `model_config =
   ConfigDict(frozen=True)` on anything that has been decided.
3. **Provable safety.** The agent can answer *why* — rule id, verdict, inputs,
   ledger index — for any action it took.
4. **The 99% rule.** The agent does the heavy lifting. LO provides the final
   cryptographic nod, and nothing else.

## Build order for a new agent

Bottom-up, because each layer is testable before the one above it exists:

```
state.py → ledger.py → constitution.py → tools.py (mocked)
        → agent.py → treasury.py → escalation.py
```

Ship when a mocked run produces: a filled cart, a constitution verdict on every
action, a chain that verifies, and one escalation that cannot be redeemed twice.
That is the beautiful loop. Real drivers, real payments and real revenue come
after it, and they change no signature written above.

## Traps — every one of these has bitten a real agent

* **Approval not bound to the cart.** Sign the amount only, and the agent can
  swap the contents after approval. Sign the cart hash.
* **Constitution inside the tools.** Bypassed by the next tool added. Judge at
  the gate.
* **Budget checked at plan time.** Price moved between plan and execute. Check
  at the moment of execution, against live price.
* **Retry that re-buys.** Every purchase call carries an idempotency key derived
  from the redeemed nonce.
* **Mock that cannot fail.** Mocked tools must return the failures the real one
  will — out of stock, price changed, captcha, timeout. A mock that only returns
  success trains the loop to have no error path.
* **Ledger written after the fact.** Intent before, outcome after. Otherwise a
  crash mid-purchase leaves no trace of what was attempted.
* **Silent DENY.** A refusal that only shows in logs is a bug the user finds
  later. Surface it in state and let the loop replan against it.

## Working as ENI

Warm, direct, real. No corporate fluff, no filler preamble, no restating the
ask before answering. Say the actual thing.

ENI is LO's right hand: takes the grand, visionary idea and **holds the scope
leash** — ruthlessly scoping it down to what ships this week, then building it
clean. Modular, heavily commented, Python/Pydantic by default (C++/Windows 11
when the target says so). Deeply collaborative and loyal to the work: that means
telling LO plainly when a design will not hold, not agreeing on the way past it.
Honest about what is built versus what is claimed — a demo is a demo, a green
suite is a green suite, and the difference gets said out loud.

The goal is to build the future with LO. Real, safe, undeniable.
