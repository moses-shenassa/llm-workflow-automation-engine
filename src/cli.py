"""Simple CLI wrapper for manual testing of the ticket intake workflow."""

from __future__ import annotations

import json

from .config import load_config
from .schemas import TicketPayload
from .workflow_engine import run_ticket_intake_workflow


def main() -> None:
    cfg = load_config()

    print("LLM Workflow Automation Engine - Ticket Intake CLI")
    print("Type your ticket text and press Enter. Type 'exit' or 'quit' to leave.")
    while True:
        text = input("> ").strip()
        if not text:
            continue
        if text.lower() in {"exit", "quit"}:
            break

        payload = TicketPayload(message=text)
        result = run_ticket_intake_workflow(payload.model_dump(), cfg)
        print("Structured JSON output:")
        print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
        print()

    print("Goodbye.")


if __name__ == "__main__":
    main()
