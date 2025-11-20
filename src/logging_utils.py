"""Logging utilities for workflow runs.

For this PoC we log to CSV, but the same pattern can be adapted to databases
or external logging services.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .config import AppConfig
from .schemas import TicketWorkflowOutput


def _ensure_log_dir(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)


def log_ticket_workflow_run(
    cfg: AppConfig,
    input_payload: Dict[str, Any],
    output: Optional[TicketWorkflowOutput],
    status: str = "success",
    error_message: str | None = None,
) -> None:
    """Append a single workflow run entry to the CSV log (if enabled)."""
    if not cfg.logging.log_to_csv:
        return

    csv_path = Path(cfg.logging.csv_path)
    _ensure_log_dir(csv_path)

    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "workflow_type": cfg.workflow.workflow_type,
        "status": status,
        "error_message": error_message or "",
        "input_message": input_payload.get("message", "")[:500],
        "summary": (output.summary[:500] if output else ""),
        "priority": (output.metadata.priority if output else ""),
        "category": (output.metadata.category if output else ""),
        "needs_human_review": (
            output.metadata.needs_human_review if output else ""
        ),
    }

    write_header = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)
