from __future__ import annotations

from typing import Protocol

from .models import Decision, RunOutcome


class DecisionPolicy(Protocol):
    def decide(self, outcome: RunOutcome) -> Decision: ...


class ActionSink(Protocol):
    def complete(self, outcome: RunOutcome, decision: Decision) -> None: ...

    def escalate(self, outcome: RunOutcome, decision: Decision) -> None: ...


class AuditStore(Protocol):
    def record(self, outcome: RunOutcome, decision: Decision) -> None: ...

