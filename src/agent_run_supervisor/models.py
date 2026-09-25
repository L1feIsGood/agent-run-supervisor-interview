from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping


class RunStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"


class OperationKind(StrEnum):
    NONE = "none"
    READ = "read"
    WRITE = "write"


class DecisionAction(StrEnum):
    COMPLETE = "complete"
    ESCALATE = "escalate"


@dataclass(frozen=True, slots=True)
class RunOutcome:
    run_id: str
    task_id: str
    attempt: int
    status: RunStatus
    error_code: str | None
    operation_kind: OperationKind
    request_sent: bool
    failure_signature: str | None
    requested_by: str
    tool_name: str | None
    message: str
    evidence: dict[str, Any]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "RunOutcome":
        run_id = _required_text(value, "run_id")
        task_id = _required_text(value, "task_id")
        attempt = value.get("attempt")
        if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
            raise ValueError(f"{run_id}: attempt must be a positive integer")

        request_sent = value.get("request_sent")
        if not isinstance(request_sent, bool):
            raise ValueError(f"{run_id}: request_sent must be boolean")

        try:
            status = RunStatus(_required_text(value, "status"))
            operation_kind = OperationKind(_required_text(value, "operation_kind"))
        except ValueError as exc:
            raise ValueError(f"{run_id}: {exc}") from exc

        error_code = _optional_text(value, "error_code")
        if status is RunStatus.SUCCESS and error_code is not None:
            raise ValueError(f"{run_id}: successful run cannot have error_code")
        if status is RunStatus.FAILED and error_code is None:
            raise ValueError(f"{run_id}: failed run must have error_code")

        return cls(
            run_id=run_id,
            task_id=task_id,
            attempt=attempt,
            status=status,
            error_code=error_code,
            operation_kind=operation_kind,
            request_sent=request_sent,
            failure_signature=_optional_text(value, "failure_signature"),
            requested_by=_required_text(value, "requested_by"),
            tool_name=_optional_text(value, "tool_name"),
            message=_required_text(value, "message"),
            evidence=_required_object(value, "evidence"),
        )


@dataclass(frozen=True, slots=True)
class Decision:
    action: DecisionAction
    reason: str
    recipient_role: str | None = None

    def __post_init__(self) -> None:
        if self.action is DecisionAction.ESCALATE and not self.recipient_role:
            raise ValueError("escalation decision requires recipient_role")
        if self.action is not DecisionAction.ESCALATE and self.recipient_role is not None:
            raise ValueError("only escalation decision may have recipient_role")


def _required_text(value: Mapping[str, Any], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return result.strip()


def _optional_text(value: Mapping[str, Any], key: str) -> str | None:
    result = value.get(key)
    if result is None:
        return None
    if not isinstance(result, str) or not result.strip():
        raise ValueError(f"{key} must be null or a non-empty string")
    return result.strip()


def _required_object(value: Mapping[str, Any], key: str) -> dict[str, Any]:
    result = value.get(key)
    if not isinstance(result, dict) or not result:
        raise ValueError(f"{key} must be a non-empty object")
    return dict(result)
