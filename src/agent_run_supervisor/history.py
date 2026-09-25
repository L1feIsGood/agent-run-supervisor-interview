from __future__ import annotations

import json
from pathlib import Path

from .models import RunOutcome


def load_history(path: str | Path) -> list[RunOutcome]:
    source_path = Path(path)
    with source_path.open("r", encoding="utf-8") as stream:
        raw = json.load(stream)

    if not isinstance(raw, list):
        raise ValueError("history root must be an array")

    outcomes: list[RunOutcome] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"history item {index} must be an object")
        try:
            outcomes.append(RunOutcome.from_mapping(item))
        except ValueError as exc:
            raise ValueError(f"history item {index}: {exc}") from exc
    return outcomes

