"""Prompt templates for the LLM Workflow Automation Engine.

This module centralizes system and user prompts so they can be iterated on
without changing the orchestration code.
"""

from __future__ import annotations

from textwrap import dedent
from typing import Optional


TICKET_SYSTEM_PROMPT = dedent(
    """You are a careful, reliable workflow assistant that analyzes incoming
    support tickets or intake messages and produces structured JSON outputs.

    Your goals:
    - Extract key entities (customer name, email if present in the text)
    - Classify the ticket into one of: billing, technical, account, other
    - Assign a priority: low, medium, high, or urgent
    - Generate a short summary of the request in plain language
    - Decide if the ticket clearly needs human review (true/false)

    You MUST follow the requested JSON schema exactly. Do not include any prose
    outside of the JSON. Do not add extra fields.
    """
)


def build_ticket_user_prompt(
    message: str,
    customer_name: Optional[str] = None,
    email: Optional[str] = None,
) -> str:
    """Build the user prompt for the ticket intake workflow.

    Parameters
    ----------
    message:
        Raw ticket or intake text from the user/system.
    customer_name:
        Upstream customer name, if provided.
    email:
        Upstream email, if provided.
    """
    upstream_block = f"""
    Upstream metadata (may be null):
    - customer_name: {customer_name or "null"}
    - email: {email or "null"}

    If these values are provided (not null), you MUST copy them exactly into
    metadata.customer_name and metadata.email in the JSON. Only infer values
    from the message text if they are null above.
    """

    return dedent(
        f"""You will receive the text of a ticket or intake message.

        Carefully analyze the message and produce a structured JSON object with
        the following fields:

        - summary: a short plain-language summary of the request
        - metadata: an object with:
            - customer_name: inferred or null, but if an upstream value is provided,
              you MUST use that value exactly.
            - email: inferred or null, but if an upstream value is provided, you
              MUST use that value exactly.
            - priority: one of ["low", "medium", "high", "urgent"]
            - category: one of ["billing", "technical", "account", "other"]
            - needs_human_review: boolean
        - original_text: the exact original message string you received

        Your JSON MUST have exactly these top-level keys:
        - "summary"
        - "metadata"
        - "original_text"

        {upstream_block}

        Here is the raw message:

        "{message}"

        Return ONLY valid JSON. No backticks, no explanations, no comments.
        """
    ).strip()
