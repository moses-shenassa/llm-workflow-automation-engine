"""Core workflow orchestration for the ticket intake example."""

from __future__ import annotations

from typing import Any, Dict

from .config import AppConfig
from .llm_client import LLMClient
from .prompts import TICKET_SYSTEM_PROMPT, build_ticket_user_prompt
from .schemas import TicketPayload, TicketWorkflowOutput


def run_ticket_intake_workflow(
    payload: Dict[str, Any],
    cfg: AppConfig,
) -> TicketWorkflowOutput:
    """End-to-end ticket intake workflow.

    Steps:
    1. Validate and normalize the incoming payload (TicketPayload)
    2. Build system + user prompts
    3. Call LLM client with retries + schema validation
    4. Return a TicketWorkflowOutput instance
    """
    incoming = TicketPayload.model_validate(payload)

    system_prompt = TICKET_SYSTEM_PROMPT
    user_prompt = build_ticket_user_prompt(
    message=incoming.message,
    customer_name=incoming.customer_name,
    email=incoming.email,
)


    client = LLMClient(cfg)
    json_data = client.generate_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_model=TicketWorkflowOutput,
    )

    return TicketWorkflowOutput.model_validate(json_data)
