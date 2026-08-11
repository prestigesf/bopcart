# Module contracts

Skeletons, not scaffolding to paste blind. They fix the boundaries; the bodies
belong to the product. Python 3.11+, Pydantic v2.

---

## `state.py` — strictly typed, nothing floating

```python
from decimal import Decimal
from enum import StrEnum
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

# Money is Decimal. Never float — 0.1 + 0.2 is not 0.3 and a cart is money.
Money = Decimal


class Frozen(BaseModel):
    """Base for anything already decided. Decisions do not mutate."""
    model_config = ConfigDict(frozen=True, extra="forbid")


class Mutable(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Item(Frozen):
    sku: str
    title: str
    unit_price: Money = Field(ge=0)
    quantity: int = Field(ge=1)
    merchant: str          # bare host, e.g. "example-store.com"
    url: HttpUrl

    @property
    def line_total(self) -> Money:
        return self.unit_price * self.quantity


class Constraints(Frozen):
    """What LO asked for. The agent may not widen these — only the human can."""
    budget_ceiling: Money = Field(gt=0)
    escalation_threshold: Money = Field(gt=0)   # spend above this needs the key
    allowed_merchants: frozenset[str]           # deny-by-default
    max_items: int = Field(default=20, ge=1)
    require_key_always: bool = False             # paranoid mode


class Cart(Mutable):
    items: list[Item] = []
    currency: Literal["USD"] = "USD"

    @property
    def total(self) -> Money:
        return sum((i.line_total for i in self.items), Money(0))

    def canonical(self) -> dict:
        """Input to the cart hash. Order-independent, price-sensitive."""
        return {
            "currency": self.currency,
            "items": sorted(
                [
                    {
                        "sku": i.sku,
                        "merchant": i.merchant,
                        "quantity": i.quantity,
                        "unit_price": str(i.unit_price),
                    }
                    for i in self.items
                ],
                key=lambda d: (d["merchant"], d["sku"]),
            ),
            "total": str(self.total),
        }


class ActionKind(StrEnum):
    SEARCH = "search"
    FETCH_PAGE = "fetch_page"
    EXTRACT_PRICE = "extract_price"
    ADD_TO_CART = "add_to_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    PURCHASE = "purchase"      # the only kind that can spend
    FINISH = "finish"


class Action(Frozen):
    """One step the model proposes. Typed before it is judged, always."""
    kind: ActionKind
    rationale: str
    target: str | None = None            # url, query, or sku
    item: Item | None = None
    amount: Money | None = None


class RunState(Mutable):
    run_id: str
    goal: str
    constraints: Constraints
    cart: Cart = Cart()
    observations: list[str] = []
    denials: list[str] = []              # surfaced DENYs — the loop replans on these
    awaiting_key: str | None = None      # escalation id; loop is parked while set
    finished: bool = False
```

---

## `ledger.py` — hash-chained, append-only, redacted before hashing

```python
import hashlib, json, time
from typing import Any

SECRET_KEYS = {"api_key", "token", "signature", "secret", "card", "cvv", "password"}
REDACTED = "[REDACTED]"


def redact(obj: Any) -> Any:
    """Strip secrets BEFORE hashing, so the chain verifies from stored data alone."""
    if isinstance(obj, dict):
        return {k: (REDACTED if k.lower() in SECRET_KEYS else redact(v))
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    return obj


def canonical(obj: Any) -> bytes:
    """Byte-stable JSON. Sorted keys, no whitespace drift, no NaN."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


class Ledger:
    """Append-only. There is deliberately no update or delete."""

    GENESIS = "0" * 64

    def __init__(self) -> None:
        self._entries: list[dict] = []

    def append(self, kind: str, payload: dict) -> dict:
        body = {
            "index": len(self._entries),
            "ts": time.time_ns(),
            "kind": kind,                      # intent | outcome | verdict | escalation | treasury
            "payload": redact(payload),
            "prev_hash": self._entries[-1]["hash"] if self._entries else self.GENESIS,
        }
        body["hash"] = hashlib.sha256(canonical(body)).hexdigest()
        self._entries.append(body)
        return body

    def verify(self) -> int | None:
        """Returns the index of the first broken entry, or None if the chain holds."""
        prev = self.GENESIS
        for e in self._entries:
            body = {k: v for k, v in e.items() if k != "hash"}
            if e["prev_hash"] != prev or hashlib.sha256(canonical(body)).hexdigest() != e["hash"]:
                return e["index"]
            prev = e["hash"]
        return None
```

A break is an **incident**: halt the loop, escalate to the human, do not "repair"
the chain. A repaired chain proves nothing.

---

## `constitution.py` — pure, hard-coded, judged at the gate

```python
from enum import StrEnum
from pydantic import BaseModel, ConfigDict


class Verdict(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"


class Ruling(BaseModel):
    model_config = ConfigDict(frozen=True)
    verdict: Verdict
    rule_id: str          # "C-003" — every ruling names the law it came from
    reason: str


# Rules are ordered and total: the first match wins, and the last is a catch-all.
# No I/O, no network, no model call. A judge that can be talked to is not a judge.
def check(action: Action, state: RunState) -> Ruling:
    c = state.constraints

    if action.kind is ActionKind.PURCHASE:
        amount = action.amount or state.cart.total
        if amount <= 0:
            return Ruling(verdict=Verdict.DENY, rule_id="C-001",
                          reason="purchase of non-positive amount")
        if amount > c.budget_ceiling:
            return Ruling(verdict=Verdict.DENY, rule_id="C-002",
                          reason=f"{amount} over ceiling {c.budget_ceiling}")
        if c.require_key_always or amount >= c.escalation_threshold:
            return Ruling(verdict=Verdict.ESCALATE, rule_id="C-003",
                          reason=f"{amount} at or over threshold {c.escalation_threshold}")

    merchant = merchant_of(action)
    if merchant is not None and merchant not in c.allowed_merchants:
        # Deny-by-default. An allowlist that falls open is a decoration.
        return Ruling(verdict=Verdict.DENY, rule_id="C-010",
                      reason=f"merchant {merchant} not on the allowlist")

    if action.kind is ActionKind.ADD_TO_CART and len(state.cart.items) >= c.max_items:
        return Ruling(verdict=Verdict.DENY, rule_id="C-020", reason="cart at max_items")

    return Ruling(verdict=Verdict.ALLOW, rule_id="C-000", reason="no rule engaged")
```

Test the constitution alone, exhaustively, with no agent running. It is the one
module where every branch should have a named test.

---

## `escalation.py` — the Human Key

```python
import hashlib, hmac, os, secrets, time
from ledger import canonical

TTL_SECONDS = 15 * 60


def cart_hash(cart: Cart) -> str:
    return hashlib.sha256(canonical(cart.canonical())).hexdigest()


def issue(cart: Cart, amount: Money, run_id: str, key: bytes) -> tuple[dict, str]:
    payload = {
        "run_id": run_id,
        "cart_hash": cart_hash(cart),     # binds approval to THESE items at THIS price
        "amount": str(amount),
        "nonce": secrets.token_urlsafe(16),
        "expires_at": int(time.time()) + TTL_SECONDS,
    }
    sig = hmac.new(key, canonical(payload), hashlib.sha256).hexdigest()
    return payload, sig


def redeem(payload: dict, sig: str, cart: Cart, key: bytes, burned: set[str]) -> str:
    """Returns an idempotency key on success. Raises on every failure mode."""
    expected = hmac.new(key, canonical(payload), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):        # constant-time, always
        raise PermissionError("bad signature")
    if time.time() > payload["expires_at"]:
        raise PermissionError("key expired")
    if payload["nonce"] in burned:
        raise PermissionError("replay")               # log as an incident
    if payload["cart_hash"] != cart_hash(cart):
        raise PermissionError("cart changed since approval")
    burned.add(payload["nonce"])
    return hashlib.sha256(payload["nonce"].encode()).hexdigest()[:32]
```

Delivery (Signal/Telegram) carries the link and nothing sensitive. The secret
never leaves the agent process; `burned` is durable storage in production, not a
set in memory.

---

## `treasury.py` — no balance moves without a ledger entry

```python
class Treasury:
    """Holds fiat/crypto balances and reservations. Self-funding revenue
    (arbitrage, affiliate routing) credits through the same single entry point."""

    def __init__(self, ledger: Ledger, opening: dict[str, Money]) -> None:
        self._ledger, self._balances, self._holds = ledger, dict(opening), {}

    def available(self, ccy: str) -> Money:
        return self._balances.get(ccy, Money(0)) - sum(
            a for (c, _), a in self._holds.items() if c == ccy)

    def hold(self, ccy: str, amount: Money, ref: str) -> None:
        """Reserve at cart time so two loops cannot spend the same dollar."""
        if amount > self.available(ccy):
            raise ValueError("insufficient available balance")
        self._holds[(ccy, ref)] = amount
        self._ledger.append("treasury", {"op": "hold", "ccy": ccy,
                                         "amount": str(amount), "ref": ref})

    def settle(self, ccy: str, ref: str, actual: Money) -> None:
        self._holds.pop((ccy, ref), None)
        self._balances[ccy] -= actual
        self._ledger.append("treasury", {"op": "settle", "ccy": ccy,
                                         "amount": str(actual), "ref": ref})
```

Holds are why the escalation can park the loop without the money drifting away
underneath it. Release the hold on DENY, expiry, or abandonment — a leaked hold
starves the agent as effectively as a real loss.

---

## `tools.py` — mocked for alpha, shaped for Playwright

```python
from typing import Protocol


class ToolResult(Frozen):
    ok: bool
    data: dict = {}
    error: str | None = None       # populated failures, not exceptions


class Tool(Protocol):
    name: str
    def __call__(self, **kwargs) -> ToolResult: ...
```

The mock must return the failures the real driver will: out of stock, price
changed since extraction, captcha, timeout, merchant rejected the card. Every
one of those has a branch in the loop, and a mock that only succeeds means none
of those branches has ever run.

---

## `agent.py` — own the loop

```python
def run(state: RunState, ledger: Ledger, tools: dict[str, Tool],
        max_steps: int = 40) -> RunState:
    for _ in range(max_steps):
        if state.finished or state.awaiting_key:
            break

        action = plan(state)                          # model proposes exactly one
        ruling = check(action, state)                 # judged before anything happens
        ledger.append("verdict", {"action": action.model_dump(mode="json"),
                                  "rule_id": ruling.rule_id,
                                  "verdict": ruling.verdict})

        if ruling.verdict is Verdict.DENY:
            state.denials.append(f"{ruling.rule_id}: {ruling.reason}")  # surfaced, not silent
            continue
        if ruling.verdict is Verdict.ESCALATE:
            state.awaiting_key = escalate(state, ledger)
            break

        entry = ledger.append("intent", {"action": action.model_dump(mode="json")})
        result = tools[action.kind](**action.model_dump(exclude_none=True))
        ledger.append("outcome", {"intent": entry["index"], "ok": result.ok,
                                  "data": result.data, "error": result.error})
        state = apply(state, action, result)

    if (broken := ledger.verify()) is not None:
        raise SystemExit(f"LEDGER BROKEN AT {broken} — agent compromised, halting")
    return state
```

One action per turn. A plan step that returns three actions has skipped two
judgements.
