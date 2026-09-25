from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from agent_run_supervisor.models import RunOutcome, RunStatus  # noqa: E402


class RunOutcomeTests(unittest.TestCase):
    def test_failed_run_requires_error_code(self) -> None:
        raw = valid_mapping()
        raw["status"] = "failed"
        raw["error_code"] = None

        with self.assertRaisesRegex(ValueError, "failed run must have error_code"):
            RunOutcome.from_mapping(raw)

    def test_boolean_is_not_valid_attempt_number(self) -> None:
        raw = valid_mapping()
        raw["attempt"] = True

        with self.assertRaisesRegex(ValueError, "positive integer"):
            RunOutcome.from_mapping(raw)

    def test_valid_mapping_is_parsed(self) -> None:
        outcome = RunOutcome.from_mapping(valid_mapping())

        self.assertEqual("run-model-test", outcome.run_id)
        self.assertIs(RunStatus.SUCCESS, outcome.status)

    def test_evidence_must_be_a_non_empty_object(self) -> None:
        raw = valid_mapping()
        raw["evidence"] = {}

        with self.assertRaisesRegex(ValueError, "evidence must be a non-empty object"):
            RunOutcome.from_mapping(raw)

    def test_evidence_is_preserved(self) -> None:
        raw = valid_mapping()
        raw["evidence"] = {
            "agent_output": {"message": "Merge request created"},
            "validation_errors": ["$.status: required property is missing"],
        }

        outcome = RunOutcome.from_mapping(raw)

        self.assertEqual(
            {
                "agent_output": {"message": "Merge request created"},
                "validation_errors": ["$.status: required property is missing"],
            },
            outcome.evidence,
        )

    def test_worker_result_contract_requires_status_and_message(self) -> None:
        contract_path = REPOSITORY_ROOT / "contracts" / "worker-result-v1.schema.json"

        with contract_path.open("r", encoding="utf-8") as stream:
            contract = json.load(stream)

        self.assertEqual(["status", "message"], contract["required"])
        self.assertEqual(["completed", "blocked"], contract["properties"]["status"]["enum"])


def valid_mapping() -> dict[str, object]:
    return {
        "run_id": "run-model-test",
        "task_id": "TASK-MODEL",
        "attempt": 1,
        "status": "success",
        "error_code": None,
        "operation_kind": "read",
        "request_sent": False,
        "failure_signature": None,
        "requested_by": "user-model-test",
        "tool_name": "test-tool",
        "message": "Test mapping.",
        "evidence": {"source": "unit-test"},
    }


if __name__ == "__main__":
    unittest.main()
