from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from agent_run_supervisor.history import load_history  # noqa: E402
from agent_run_supervisor.in_memory import InMemoryActionSink, InMemoryAuditStore  # noqa: E402
from agent_run_supervisor.orchestrator import Supervisor  # noqa: E402
from agent_run_supervisor.policy import DefaultEscalationPolicy  # noqa: E402


def main() -> int:
    history = load_history(REPOSITORY_ROOT / "fixtures" / "historical_runs.json")
    sink = InMemoryActionSink()
    audit = InMemoryAuditStore()
    supervisor = Supervisor(DefaultEscalationPolicy(), sink, audit)

    rows = []
    for outcome in history:
        decision = supervisor.handle(outcome)
        rows.append(
            {
                "run_id": outcome.run_id,
                "task_id": outcome.task_id,
                "attempt": outcome.attempt,
                "error_code": outcome.error_code,
                "failure_signature": outcome.failure_signature,
                "message": outcome.message,
                "evidence": outcome.evidence,
                "action": decision.action.value,
                "recipient_role": decision.recipient_role,
                "reason": decision.reason,
            }
        )

    counts = Counter(row["action"] for row in rows)
    recipients = Counter(
        row["recipient_role"] for row in rows if row["recipient_role"] is not None
    )
    print(json.dumps({"runs": rows, "action_counts": counts, "recipient_counts": recipients}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
