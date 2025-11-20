"""Pydantic schemas for the LLM Workflow Automation Engine.

These models define the structure of both the incoming payloads and the
structured JSON outputs produced by the LLM.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class TicketPayload(BaseModel):
    """Incoming payload from n8n / webhook.

    This represents the raw ticket or intake message. You can extend this with
    additional fields (e.g., account_id, channel) as needed.
    """

    message: str = Field(..., description="Raw ticket or form text")
    customer_name: Optional[str] = Field(
        None, description="Customer name if provided by upstream system"
    )
    email: Optional[str] = Field(
        None, description="Email address if provided by upstream system"
    )


class TicketMetadata(BaseModel):
    """Metadata about the ticket extracted or inferred by the LLM."""

    customer_name: Optional[str]
    email: Optional[str]
    priority: Literal["low", "medium", "high", "urgent"]
    category: Literal["billing", "technical", "account", "other"]
    needs_human_review: bool = False


class TicketWorkflowOutput(BaseModel):
    """Final structured JSON output for the exemplar ticket intake workflow."""

    summary: str
    metadata: TicketMetadata
    original_text: str


def get_output_model(schema_name: str):
    """Lookup function for output models by schema name.

    This is intentionally simple for the PoC, but provides a pattern you can
    extend as you add additional workflows and versions.
    """
    if schema_name == "TicketWorkflowOutput_v1":
        return TicketWorkflowOutput
    raise ValueError(f"Unknown schema name: {schema_name}")
