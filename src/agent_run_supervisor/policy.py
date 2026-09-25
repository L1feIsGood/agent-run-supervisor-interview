from __future__ import annotations

from .models import Decision, DecisionAction, RunOutcome, RunStatus


class DefaultEscalationPolicy:
    """Policy used by the current service."""

    def decide(self, outcome: RunOutcome) -> Decision:
        if outcome.status is RunStatus.SUCCESS:
            return Decision(
                action=DecisionAction.COMPLETE,
                reason="agent run completed successfully",
            )

        return Decision(
            action=DecisionAction.ESCALATE,
            recipient_role="developer",
            reason=f"agent run failed: {outcome.error_code}",
        )
