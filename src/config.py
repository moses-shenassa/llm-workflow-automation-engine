"""Configuration loading for the LLM Workflow Automation Engine.

This module reads a TOML config file (config.toml by default) and exposes a typed
AppConfig object that the rest of the application can depend on.

The expected config structure matches `config.example.toml`:

[llm]
provider = "openai"            # or "anthropic"
model = "gpt-4.1-mini"
temperature = 0.1
max_tokens = 800

[llm.retry]
max_attempts = 3
backoff_seconds = 2

[logging]
log_to_csv = true
csv_path = "data/logs/workflow_runs.csv"
log_prompt_and_response = false

[workflow]
workflow_type = "ticket_intake"

[schema]
output_schema = "TicketWorkflowOutput_v1"
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import toml


@dataclass
class RetryConfig:
    """Retry behavior for LLM calls."""

    max_attempts: int = 3
    backoff_seconds: int = 2


@dataclass
class LLMConfig:
    """Configuration for the LLM provider and model."""

    provider: Literal["openai", "anthropic"] = "openai"
    model: str = "gpt-4.1-mini"
    temperature: float = 0.1
    max_tokens: int = 800
    retry: RetryConfig = RetryConfig()


@dataclass
class LoggingConfig:
    """Configuration for workflow run logging."""

    log_to_csv: bool = True
    csv_path: str = "data/logs/workflow_runs.csv"
    # If true, prompts and raw LLM responses will be logged as well.
    # For real production deployments you may want this off by default.
    log_prompt_and_response: bool = False


@dataclass
class WorkflowConfig:
    """High-level workflow settings."""

    # For now we support a single exemplar workflow, but this allows future expansion.
    workflow_type: str = "ticket_intake"


@dataclass
class SchemaConfig:
    """Output schema selection (versioned)."""

    output_schema: str = "TicketWorkflowOutput_v1"


@dataclass
class AppConfig:
    """Top-level application configuration container."""

    llm: LLMConfig
    logging: LoggingConfig
    workflow: WorkflowConfig
    schema: SchemaConfig


def load_config(path: str | Path = "config.toml") -> AppConfig:
    """Load configuration from a TOML file into an AppConfig instance.

    Parameters
    ----------
    path:
        Path to the TOML configuration file. Defaults to "config.toml" in the
        project root.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.
    toml.TomlDecodeError
        If the configuration file is not valid TOML.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found at {path}. "
            "Copy config.example.toml to config.toml and edit it with your settings."
        )

    data = toml.load(path)

    # LLM + retry
    llm_raw = data.get("llm", {})
    retry_raw = llm_raw.get("retry", {})

    retry_cfg = RetryConfig(
        max_attempts=int(retry_raw.get("max_attempts", 3)),
        backoff_seconds=int(retry_raw.get("backoff_seconds", 2)),
    )

    llm_cfg = LLMConfig(
        provider=llm_raw.get("provider", "openai"),
        model=str(llm_raw.get("model", "gpt-4.1-mini")),
        temperature=float(llm_raw.get("temperature", 0.1)),
        max_tokens=int(llm_raw.get("max_tokens", 800)),
        retry=retry_cfg,
    )

    # Logging
    logging_raw = data.get("logging", {})
    logging_cfg = LoggingConfig(
        log_to_csv=bool(logging_raw.get("log_to_csv", True)),
        csv_path=str(logging_raw.get("csv_path", "data/logs/workflow_runs.csv")),
        log_prompt_and_response=bool(
            logging_raw.get("log_prompt_and_response", False)
        ),
    )

    # Workflow
    workflow_raw = data.get("workflow", {})
    workflow_cfg = WorkflowConfig(
        workflow_type=str(workflow_raw.get("workflow_type", "ticket_intake"))
    )

    # Schema
    schema_raw = data.get("schema", {})
    schema_cfg = SchemaConfig(
        output_schema=str(
            schema_raw.get("output_schema", "TicketWorkflowOutput_v1")
        )
    )

    return AppConfig(
        llm=llm_cfg,
        logging=logging_cfg,
        workflow=workflow_cfg,
        schema=schema_cfg,
    )
