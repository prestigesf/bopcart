"""
Payment / procurement rail adapter.

VERIFIED INSTRUCTION IN → EXECUTE EXACTLY ONCE → EXECUTION RESULT

The adapter is deliberately "dumb":
- does not choose product/merchant
- does not calculate any money
- does not change cart or amount
- does not invent authorization
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional, Set

from .errors import ExecutionStateError, ReplayDetectedError
from .schemas import ExecutionInstruction, ExecutionResult, Verdict


class SimulatedAdapter:
    """
    Safe simulated rail for tests.
    Never touches real money.
    """

    def __init__(self) -> None:
        self._seen_keys: Set[str] = set()
        self._results: Dict[str, ExecutionResult] = {}

    def execute(
        self,
        instruction: ExecutionInstruction,
        *,
        enforcement_verdict: str,
        live_merchant_total_minor: Optional[int] = None,
    ) -> ExecutionResult:
        # Fail closed on bad state
        if enforcement_verdict in ("HOLD", "DENY"):
            raise ExecutionStateError(f"cannot execute under verdict {enforcement_verdict}")

        if instruction.execution_instruction_digest is None:
            raise ExecutionStateError("missing execution_instruction_digest")

        # Execution-time price check
        if live_merchant_total_minor is not None:
            if live_merchant_total_minor != instruction.grand_total_minor:
                return ExecutionResult(
                    instruction_id=instruction.instruction_id,
                    status="HOLD",
                    provider_message="merchant total changed since calculation",
                    idempotency_key=instruction.idempotency_key,
                    executed_at=datetime.now(timezone.utc),
                )

        key = instruction.idempotency_key
        if key in self._seen_keys:
            # Return prior result — no double charge
            prior = self._results.get(key)
            if prior:
                return prior.model_copy(update={"status": "DUPLICATE"})
            raise ReplayDetectedError("idempotency key already used")

        self._seen_keys.add(key)
        result = ExecutionResult(
            instruction_id=instruction.instruction_id,
            status="SUCCESS",
            external_transaction_reference=f"sim-{instruction.instruction_id[:8]}",
            provider_message="simulated success",
            executed_at=datetime.now(timezone.utc),
            idempotency_key=key,
        )
        self._results[key] = result
        return result
