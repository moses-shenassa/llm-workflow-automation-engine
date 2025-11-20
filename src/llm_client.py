"""Provider-agnostic LLM client with JSON + schema enforcement and retries."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional, Type

from openai import OpenAI
import anthropic
from pydantic import BaseModel, ValidationError

from .config import AppConfig
from .schemas import TicketWorkflowOutput


class LLMClient:
    """Wrapper around OpenAI / Anthropic with retry + validation logic.

    This client focuses on producing valid JSON that conforms to a given Pydantic
    model. If the LLM returns malformed JSON or fails validation, it retries with
    a corrective instruction until max_attempts is reached.
    """

    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        provider = cfg.llm.provider.lower()
        if provider == "openai":
            self.provider = "openai"
            self._client = OpenAI()
        elif provider == "anthropic":
            self.provider = "anthropic"
            self._client = anthropic.Anthropic()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        output_model: Type[BaseModel] = TicketWorkflowOutput,
    ) -> Dict[str, Any]:
        """Generate structured JSON for a workflow and validate it.

        Parameters
        ----------
        system_prompt:
            System-level instructions for the LLM.
        user_prompt:
            User/content prompt describing the task and including the raw text.
        output_model:
            Pydantic model to validate the final JSON against.

        Returns
        -------
        Dict[str, Any]
            A Python dict that has passed Pydantic validation.

        Raises
        ------
        RuntimeError
            If valid JSON conforming to the schema cannot be produced after all
            retry attempts.
        """
        attempt = 0
        last_error: Optional[Exception] = None

        while attempt < self.cfg.llm.retry.max_attempts:
            attempt += 1
            try:
                raw = self._call_llm(system_prompt, user_prompt)
                data = json.loads(raw)
                # Validate against Pydantic model
                output_model.model_validate(data)
                return data
            except (json.JSONDecodeError, ValidationError, Exception) as exc:  # noqa: BLE001
                last_error = exc
                if attempt >= self.cfg.llm.retry.max_attempts:
                    break
                # Backoff before retrying
                time.sleep(self.cfg.llm.retry.backoff_seconds)
                # On retry, prepend a correction note
                user_prompt = (
                    "Your previous response did not match the required JSON schema. "
                    "Return ONLY corrected, valid JSON now.\n\n"
                    + user_prompt
                )

        raise RuntimeError(
            f"Failed to produce valid JSON after {attempt} attempts: {last_error}"
        ) from last_error

    # ---------------------------------------------------------------------
    # Internal provider-specific calls
    # ---------------------------------------------------------------------

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if self.provider == "openai":
            return self._call_openai(system_prompt, user_prompt)
        if self.provider == "anthropic":
            return self._call_anthropic(system_prompt, user_prompt)
        raise RuntimeError("Unexpected provider state")

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.cfg.llm.model,
            temperature=self.cfg.llm.temperature,
            max_tokens=self.cfg.llm.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = resp.choices[0].message.content
        # In the new OpenAI client, content is usually a string, but may sometimes
        # be structured; we normalize to string here.
        if isinstance(content, list):
            return "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        return str(content)

    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        client: anthropic.Anthropic = self._client
        resp = client.messages.create(
            model=self.cfg.llm.model,
            max_tokens=self.cfg.llm.max_tokens,
            temperature=self.cfg.llm.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        # Anthropic messages API returns a list of content blocks.
        text_chunks = []
        for block in resp.content:
            if getattr(block, "type", None) == "text":
                text_chunks.append(block.text)
        return "".join(text_chunks)
