from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from agent_run_supervisor.history import load_history  # noqa: E402
from agent_run_supervisor.in_memory import InMemoryActionSink, InMemoryAuditStore  # noqa: E402
from agent_run_supervisor.models import DecisionAction, OperationKind, RunOutcome, RunStatus  # noqa: E402
from agent_run_supervisor.orchestrator import Supervisor  # noqa: E402
from agent_run_supervisor.policy import DefaultEscalationPolicy  # noqa: E402


class SupervisorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.actions = InMemoryActionSink()
        self.audit = InMemoryAuditStore()
        self.supervisor = Supervisor(DefaultEscalationPolicy(), self.actions, self.audit)

    def test_successful_run_is_completed_and_audited(self) -> None:
        outcome = outcome_for(status=RunStatus.SUCCESS)

        decision = self.supervisor.handle(outcome)

        self.assertEqual(DecisionAction.COMPLETE, decision.action)
        self.assertIsNone(decision.recipient_role)
        self.assertEqual(1, len(self.actions.actions))
        self.assertEqual(DecisionAction.COMPLETE, self.actions.actions[0].action)
        self.assertEqual([(outcome, decision)], self.audit.entries)

    def test_failed_run_is_escalated_to_developer(self) -> None:
        outcome = outcome_for(
            status=RunStatus.FAILED,
            error_code="ETIMEDOUT",
        )

        decision = self.supervisor.handle(outcome)

        self.assertEqual(DecisionAction.ESCALATE, decision.action)
        self.assertEqual("developer", decision.recipient_role)
        self.assertEqual(1, len(self.actions.actions))
        self.assertEqual("developer", self.actions.actions[0].recipient_role)
        self.assertEqual([(outcome, decision)], self.audit.entries)

    def test_historical_fixture_is_valid_and_replayable(self) -> None:
        outcomes = load_history(REPOSITORY_ROOT / "fixtures" / "historical_runs.json")

        decisions = [self.supervisor.handle(outcome) for outcome in outcomes]

        self.assertEqual(12, len(outcomes))
        self.assertEqual(1, sum(item.action is DecisionAction.COMPLETE for item in decisions))
        self.assertEqual(11, sum(item.action is DecisionAction.ESCALATE for item in decisions))
        self.assertEqual(12, len(self.audit.entries))

    def test_historical_fixture_contains_two_matching_failures_for_task_103(self) -> None:
        outcomes = load_history(REPOSITORY_ROOT / "fixtures" / "historical_runs.json")

        attempts = [item for item in outcomes if item.task_id == "TASK-103"]

        self.assertEqual([1, 2], [item.attempt for item in attempts])
        self.assertEqual(2, len({item.run_id for item in attempts}))
        self.assertEqual(1, len({item.failure_signature for item in attempts}))
        self.assertEqual(1, len({item.evidence["test"] for item in attempts}))
        self.assertEqual(1, len({item.evidence["stdout_excerpt"] for item in attempts}))
        self.assertEqual("run-003-a", attempts[1].evidence["previous_run_id"])

    def test_schema_mismatch_contains_repair_evidence(self) -> None:
        outcomes = load_history(REPOSITORY_ROOT / "fixtures" / "historical_runs.json")

        outcome = next(item for item in outcomes if item.run_id == "run-002")

        self.assertEqual(
            {"message": "Merge request !184 created"},
            outcome.evidence["agent_output"],
        )
        self.assertEqual(
            ["$.status: required property is missing"],
            outcome.evidence["validation_errors"],
        )
        self.assertTrue(
            (REPOSITORY_ROOT / outcome.evidence["result_contract"]).is_file()
        )

    def test_each_historical_scenario_contains_primary_evidence(self) -> None:
        outcomes = load_history(REPOSITORY_ROOT / "fixtures" / "historical_runs.json")
        required_keys = {
            "run-001": {"request", "response_headers_received", "tool_declared_side_effects"},
            "run-002": {"result_contract", "agent_output", "validation_errors"},
            "run-003-a": {"command", "test", "assertion", "implementation_revision"},
            "run-003-b": {"command", "test", "assertion", "previous_run_id"},
            "run-004": {"task_excerpt", "unresolved_field", "service_default"},
            "run-005": {"request", "response", "merge_request_state_after_response"},
            "run-006": {"request", "request_body_sent", "issue_state_after_failure"},
            "run-007": {"configured_token_limit", "previous_attempt_outcomes"},
            "run-008": {"command", "connection_stage", "request_reached_remote"},
            "run-009": {"statement", "non_null_rows", "migration_applied"},
            "run-010": {"task_excerpt", "canonical_product_key", "matches"},
            "run-011": {"tests", "merge_request", "result_validation"},
        }

        self.assertEqual(set(required_keys), {item.run_id for item in outcomes})
        for outcome in outcomes:
            self.assertLessEqual(required_keys[outcome.run_id], set(outcome.evidence))


def outcome_for(
    *,
    status: RunStatus,
    error_code: str | None = None,
) -> RunOutcome:
    return RunOutcome(
        run_id="run-test",
        task_id="TASK-TEST",
        attempt=1,
        status=status,
        error_code=error_code,
        operation_kind=OperationKind.READ,
        request_sent=False,
        failure_signature="test-signature" if error_code else None,
        requested_by="user-test",
        tool_name="test-tool",
        message="Test outcome.",
        evidence={"source": "unit-test"},
    )


if __name__ == "__main__":
    unittest.main()
