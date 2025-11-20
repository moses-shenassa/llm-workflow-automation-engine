"""FastAPI server exposing the workflow engine as HTTP endpoints."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import load_config
from .logging_utils import log_ticket_workflow_run
from .schemas import TicketPayload, TicketMetadata, TicketWorkflowOutput
from .workflow_engine import run_ticket_intake_workflow


app = FastAPI(title="LLM Workflow Automation Engine")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


# Load configuration once at startup
cfg = load_config()


@app.post("/ticket-intake", response_model=TicketWorkflowOutput)
async def ticket_intake(payload: TicketPayload) -> TicketWorkflowOutput:
    """Primary endpoint for the exemplar ticket intake workflow."""
    try:
        result = run_ticket_intake_workflow(payload.model_dump(), cfg)
        log_ticket_workflow_run(cfg, payload.model_dump(), result, status="success")
        return result
    except Exception as exc:  # noqa: BLE001
        # On error, we still log the attempt, marking needs_human_review=True
        fallback_output = TicketWorkflowOutput(
            summary="",
            metadata=TicketMetadata(
                customer_name=payload.customer_name,
                email=payload.email,
                priority="low",
                category="other",
                needs_human_review=True,
            ),
            original_text=payload.message,
        )
        log_ticket_workflow_run(
            cfg,
            payload.model_dump(),
            fallback_output,
            status="error",
            error_message=str(exc),
        )
        raise HTTPException(status_code=500, detail=f"Workflow failed: {exc}")
