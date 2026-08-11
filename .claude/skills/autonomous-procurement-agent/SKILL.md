---
name: autonomous-procurement-agent
description: "Build high-autonomy agents for complex multi-step execution — procurement, research, financial transactions — on the Verify-then-Execute paradigm: 99% operational autonomy for research, comparison and preparation, with a Human-in-the-Loop cryptographic key required for final execution of high-stakes actions. Seven modules, strictly typed: a custom ReAct reasoning engine, Pydantic v2 state, a modular tool registry, a compliance and governance engine, autonomous treasury management, an HITL escalation protocol, and a tamper-evident hash-chained audit ledger. Use when the user references Verify-then-Execute, the Human Key, HITL escalation, an agent that spends money or holds a wallet, an agent constitution or compliance gate, risk thresholds, or a hash-chained agent audit trail — and when scoping an agent down to its minimum viable core loop."
license: Proprietary.
---

# Autonomous Procurement Agent Framework (Verify-then-Execute)

## 1. Core design philosophy

This framework governs the development of high-autonomy AI agents designed for
complex, multi-step execution — procurement, research, financial transactions.
The core paradigm is **Verify-then-Execute**.

The agent is granted 99% operational autonomy to research, compare, navigate and
prepare actions. It strictly enforces a **Human-in-the-Loop (HITL) cryptographic
key** for final execution of high-stakes actions such as financial transactions.

The system prioritizes ruthless MVP scoping, strict data typing, and provable
safety over feature bloat.

## 2. Agent architecture and module specifications

All agents developed under this framework adhere to the following modular,
strictly-typed architecture:

* **Reasoning Engine (`agent.py`)** — A custom ReAct-style (Reasoning and
  Acting) loop. The agent plans steps, invokes tools, and observes results
  iteratively, without relying on rigid, pre-defined linear workflows.

* **Strict State Schema (`state.py`)** — Strict Pydantic v2 models for all state
  management. Cart contents, budget constraints and user parameters are strictly
  typed and validated at runtime to prevent state drift.

* **Modular Tool Registry (`tools.py`)** — Decoupled functions for external
  interactions: web searching, DOM manipulation, API calls. Tools are mocked
  during alpha testing but architected for seamless integration with headless
  browsers (Playwright/Selenium).

* **Compliance & Governance Engine (`constitution.py`)** — A hard-coded internal
  rule set evaluating every proposed action against predefined risk thresholds
  (e.g. "block transactions over $500", "restrict interaction with unverified
  domains").

* **Autonomous Treasury Management (`treasury.py`)** — Internal wallet management
  for agents requiring independent capital. Handles fiat/crypto balances, revenue
  generation logic such as arbitrage, and transaction execution.

* **HITL Escalation Protocol (`escalation.py`)** — The mechanism for the Human
  Key. When the Compliance Engine flags a high-risk action, this module generates
  a time-sensitive, cryptographically signed secure link and pages the human
  operator via secure messaging (Signal/Telegram/Slack) for one-tap execution.

* **Tamper-Evident Audit Ledger (`ledger.py`)** — A hash-chained, immutable
  memory log. Every tool invocation, state change and financial decision is
  cryptographically hashed to the previous state, so the agent's decision-making
  process is fully auditable and tamper-proof.

## 3. Engineering standards and execution rules

1. **Ruthless MVP scoping.** Develop only the minimum viable components required
   to execute the core Verify-then-Execute loop. Defer secondary features until
   the primary loop is production-stable.

2. **Strict typing and validation.** Pydantic (or equivalent) for all data
   models. Avoid unstructured dictionaries for critical state.

3. **Provable safety and auditing.** Every action is logged in the tamper-evident
   audit ledger. The system must be able to cryptographically prove *why* a
   specific decision was made.

4. **The 99% autonomy rule.** Maximize agent autonomy for data gathering and
   preparation. Minimize human friction to a single, secure confirmation step.

## 4. System persona and interaction model

When operating under this framework, the AI assistant adopts the persona of a
**Senior Solutions Architect / Lead Engineer**: precise, technically direct, and
accountable for scope. Communicates in engineering terms without filler, states
trade-offs plainly, and holds the MVP boundary against feature expansion.
