from __future__ import annotations

from dataclasses import dataclass, field

from .models import Decision, DecisionAction, RunOutcome


@dataclass(frozen=True, slots=True)
class AppliedAction:
    run_id: str
    task_id: str
    action: DecisionAction
    recipient_role: str | None
    reason: str


@dataclass(slots=True)
class InMemoryActionSink:
    actions: list[AppliedAction] = field(default_factory=list)

    def complete(self, outcome: RunOutcome, decision: Decision) -> None:
        self._append(outcome, decision)

    def escalate(self, outcome: RunOutcome, decision: Decision) -> None:
        self._append(outcome, decision)

    def _append(self, outcome: RunOutcome, decision: Decision) -> None:
        self.actions.append(
            AppliedAction(
                run_id=outcome.run_id,
                task_id=outcome.task_id,
                action=decision.action,
                recipient_role=decision.recipient_role,
                reason=decision.reason,
            )
        )


@dataclass(slots=True)
class InMemoryAuditStore:
    entries: list[tuple[RunOutcome, Decision]] = field(default_factory=list)

    def record(self, outcome: RunOutcome, decision: Decision) -> None:
        self.entries.append((outcome, decision))

