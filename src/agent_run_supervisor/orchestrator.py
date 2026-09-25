from __future__ import annotations

from .models import Decision, DecisionAction, RunOutcome
from .ports import ActionSink, AuditStore, DecisionPolicy


class Supervisor:
    def __init__(
        self,
        policy: DecisionPolicy,
        action_sink: ActionSink,
        audit_store: AuditStore,
    ) -> None:
        self._policy = policy
        self._action_sink = action_sink
        self._audit_store = audit_store

    def handle(self, outcome: RunOutcome) -> Decision:
        decision = self._policy.decide(outcome)

        if decision.action is DecisionAction.COMPLETE:
            self._action_sink.complete(outcome, decision)
        elif decision.action is DecisionAction.ESCALATE:
            self._action_sink.escalate(outcome, decision)
        else:
            raise ValueError(f"unsupported decision action: {decision.action}")

        self._audit_store.record(outcome, decision)
        return decision

