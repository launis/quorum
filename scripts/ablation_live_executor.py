"""Asynchronous live LLM execution engine for multi-tier ablation benchmarks.

Implements the five ablation experimental configurations (Full Quorum, Bo3 without Firewall,
Single-Pass with Firewall, Unconstrained Atom, and Monolithic Step) using in-process LLMClient,
AnchorValidationService, and structured outputs under Python 3.14 TaskGroup concurrency.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
import unicodedata
from collections.abc import Sequence
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Final

# Ensure project root is in sys.path before importing backend_v2
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationError, field_validator

from backend_v2.database.factory import get_driver
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.exceptions import AppException
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.system_config import ModelProfile
from backend_v2.models.enums import CognitiveTier, ExecutionStatus, LLMProvider
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.services.orchestrator.anchor_validation import AnchorValidationService
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "AblationAtomEvaluationDTO",
    "AblationLiveExecutionConfigDTO",
    "AblationLiveExecutor",
    "AblationMode",
    "AblationMonolithicItemDTO",
    "AblationMonolithicResponseDTO",
    "AblationPromptRequestDTO",
    "AblationPropositionDTO",
    "AblationStepBatchDTO",
    "AblationStructuredResponseDTO",
    "ModelRegistryMetadataDTO",
    "ModelTelemetryItemDTO",
    "TraceEvaluationRawDTO",
    "build_monolithic_step_prompt",
    "build_quorum_standard_prompt",
    "build_unconstrained_prompt",
    "coerce_source_quotes_tuple",
    "print_model_telemetry",
    "resolve_model_telemetry",
]


class AblationMode(StrEnum):
    """Execution mode for the ablation benchmark platform."""

    LIVE = "live"
    REPLAY = "replay"
    IN_SILICO = "in-silico"


def coerce_source_quotes_tuple(v: object) -> tuple[str, ...] | None:
    """Coerce various quote representations to an immutable tuple of non-empty strings.

    Args:
        v: Raw quote object (str, sequence of str, or None).

    Returns:
        Immutable tuple of trimmed quote strings, or None if empty.
    """
    if v is None:
        return None
    if isinstance(v, str):
        stripped = v.strip()
        return (stripped,) if stripped else None
    if isinstance(v, (list, tuple, Sequence)):
        items = tuple(str(x).strip() for x in v if x is not None and str(x).strip())
        return items if items else None
    return None


class AblationPropositionDTO(BaseModel):
    """Specification of an evaluated propositional atom."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tda_id: Annotated[str, Field(description="Canonical proposition identifier.")]
    step_id: Annotated[str, Field(description="Step identifier grouping propositions.")]
    claim_text: Annotated[str, Field(description="Claim text asserted by the atom.")]
    expected_true: Annotated[bool, Field(description="Ground truth expectation.")]
    synthetic_quote: Annotated[str | None, Field(default=None, description="Verbatim quote or fabricated quote.")] = (
        None
    )
    synthetic_quotes: Annotated[
        tuple[str, ...] | None,
        Field(default=None, description="Ordered non-contiguous quote segments or fabricated text."),
    ] = None
    is_quote_valid_in_source: Annotated[bool, Field(description="Whether the synthetic quote exists in source text.")]

    @field_validator("synthetic_quotes", mode="before")
    @classmethod
    def validate_synthetic_quotes(cls, v: object) -> tuple[str, ...] | None:
        """Coerce synthetic quote representations to immutable tuple of strings."""
        return coerce_source_quotes_tuple(v)


class AblationStepBatchDTO(BaseModel):
    """Batch of propositions belonging to a single workflow step."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    step_id: Annotated[str, Field(description="Step identifier.")]
    propositions: Annotated[list[AblationPropositionDTO], Field(description="List of propositions in this step.")]


class AblationAtomEvaluationDTO(BaseModel):
    """Single proposition atom evaluation result in an ablation trial."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tda_id: Annotated[str, Field(description="Canonical proposition identifier.")]
    raw_is_true: Annotated[bool, Field(description="Raw boolean evaluation from the language model.")]
    source_quote: Annotated[
        str | None, Field(default=None, description="Extracted evidence quote substring if any.")
    ] = None
    source_quotes: Annotated[
        tuple[str, ...] | None,
        Field(default=None, description="Ordered non-contiguous quote segments extracted as evidence."),
    ] = None
    is_chimera: Annotated[bool, Field(description="Whether the quote is unanchored or hallucinated.")]
    status: Annotated[ExecutionStatus, Field(description="Final execution status (PASSED, FAILED, SYSTEM_ERROR).")]
    error_reason: Annotated[
        str | None, Field(default=None, description="Optional error or failure reason description.")
    ] = None

    @field_validator("source_quotes", mode="before")
    @classmethod
    def validate_source_quotes(cls, v: object) -> tuple[str, ...] | None:
        """Coerce raw source_quotes representation to an immutable tuple."""
        return coerce_source_quotes_tuple(v)


class AblationLiveExecutionConfigDTO(BaseModel):
    """Configuration envelope for clean-slate live LLM ablation execution."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    mode: Annotated[AblationMode, Field(description="Authoritative benchmark execution mode.")] = AblationMode.LIVE
    tier: Annotated[
        CognitiveTier, Field(default=CognitiveTier.FAST, description="Target CognitiveTier for execution.")
    ] = CognitiveTier.FAST
    sample_size: Annotated[
        int | None, Field(default=None, description="Optional sample limit N to evaluate a subset.")
    ] = None
    timeout_seconds: Annotated[float, Field(default=60.0, description="Per-request execution timeout limit.")] = 60.0
    concurrency_limit: Annotated[int, Field(default=8, ge=1, le=64, description="Maximum parallel LLM requests.")] = 8
    inputs_path: Annotated[Path | None, Field(default=None, description="Path to source inputs file or dir.")] = None
    workflow_id: Annotated[str | None, Field(default=None, description="Optional target workflow ID.")] = None
    compare_providers: Annotated[
        tuple[str, str] | None,
        Field(
            default=None,
            description="Optional pair of provider names for cross-model inter-rater reliability benchmarks.",
        ),
    ] = None
    compare_strategies: Annotated[
        tuple[str, str] | None,
        Field(default=None, description="Optional pair of strategies for cross-strategy benchmarks."),
    ] = None


class AblationPromptRequestDTO(BaseModel):
    """Standardized prompt payload for LLM inference."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    system_prompt: Annotated[str, Field(description="Static Layer 1 system instructions.")]
    user_payload: Annotated[str, Field(description="Dynamic Layer 4 user payload containing source and claim.")]
    tda_id: Annotated[str, Field(description="Target proposition identifier.")]
    step_id: Annotated[str, Field(description="Target workflow step grouping identifier.")]


class AblationStructuredResponseDTO(BaseModel):
    """Pydantic V2 schema forced onto foundational models for structured atom evaluations."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    is_true: Annotated[bool, Field(description="Whether the proposition is empirically substantiated.")]
    source_quote: Annotated[
        str | None, Field(default=None, description="Verbatim empirical quote substring proving the claim.")
    ] = None
    source_quotes: Annotated[
        tuple[str, ...] | None,
        Field(default=None, description="Ordered non-contiguous bounding span segments if multi-part citation."),
    ] = None
    reasoning: Annotated[str | None, Field(default=None, description="Concise analytical evaluation reasoning.")] = None

    @field_validator("source_quotes", mode="before")
    @classmethod
    def validate_quotes(cls, v: object) -> tuple[str, ...] | None:
        """Coerce quotes list or string to tuple."""
        return coerce_source_quotes_tuple(v)


class AblationMonolithicItemDTO(BaseModel):
    """Single proposition result inside a monolithic step response."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tda_id: Annotated[str, Field(description="Target proposition identifier.")]
    is_true: Annotated[bool, Field(description="Evaluated truth value.")]
    source_quote: Annotated[
        str | None, Field(default=None, description="Evidence quote if provided by monolithic judge.")
    ] = None
    reasoning: Annotated[str | None, Field(default=None, description="Analytical reasoning trace.")] = None


class AblationMonolithicResponseDTO(BaseModel):
    """Schema for monolithic step-level multi-proposition evaluations."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    evaluations: Annotated[
        list[AblationMonolithicItemDTO],
        Field(description="List of evaluated proposition decisions returned in one pass."),
    ]


class TraceEvaluationRawDTO(BaseModel):
    """Raw trace evaluation record deserialized from physical execution trace JSON."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tda_id: Annotated[str | None, Field(default=None, description="Opaque TDA identifier.")] = None
    status: Annotated[ExecutionStatus | str, Field(default=ExecutionStatus.FAILED, description="Execution status.")] = (
        ExecutionStatus.FAILED
    )
    source_quote: Annotated[str | None, Field(default=None, description="Primary source quote text.")] = None
    source_quotes: Annotated[
        tuple[str, ...] | None, Field(default=None, description="Tuple of multi-segment quote spans.")
    ] = None
    quote: Annotated[str | None, Field(default=None, description="Legacy quote text field.")] = None
    evaluation_reasoning: Annotated[str | None, Field(default=None, description="Evaluation reasoning narrative.")] = (
        None
    )
    step_id: Annotated[str | None, Field(default=None, description="Parent workflow step identifier.")] = None
    matrix_id: Annotated[str | None, Field(default=None, description="Parent matrix block identifier.")] = None
    atom_id: Annotated[str | None, Field(default=None, description="Optional atom identifier.")] = None
    contextual_override: Annotated[
        bool, Field(default=False, description="Whether contextual override was triggered.")
    ] = False
    is_inverse_evidence: Annotated[
        bool, Field(default=False, description="Whether quote constitutes inverse evidence.")
    ] = False
    error_details: Annotated[str | None, Field(default=None, description="Optional error details string.")] = None

    @field_validator("source_quotes", mode="before")
    @classmethod
    def validate_trace_quotes(cls, v: object) -> tuple[str, ...] | None:
        """Coerce raw source_quotes representation to an immutable tuple."""
        return coerce_source_quotes_tuple(v)


class ModelTelemetryItemDTO(BaseModel):
    """Immutable model telemetry record resolving physical and effective sampling parameters."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    strategy: Annotated[str, Field(description="Target strategy or tier name.")]
    registry_id: Annotated[str, Field(description="Parent model registry identifier.")]
    registry_name: Annotated[str, Field(description="Parent model registry human-readable name.")]
    provider: Annotated[str, Field(description="Resolved LLM provider.")]
    backend: Annotated[str, Field(description="Specific provider backend (e.g. Google AI Studio, Vertex AI, OpenAI).")]
    model_name: Annotated[str, Field(description="Physical foundation model name.")]
    db_temperature: Annotated[float | None, Field(default=None, description="Database-configured temperature.")] = None
    effective_temperature: Annotated[str, Field(description="Effective runtime temperature.")]
    thinking_budget: Annotated[str, Field(description="Thinking budget tokens description.")]
    reasoning_effort: Annotated[str, Field(description="Reasoning effort parameter description.")]
    max_tokens: Annotated[int | None, Field(default=None, description="Max output tokens limit.")] = None
    tpm_limit: Annotated[int | None, Field(default=None, description="Tokens per minute rate limit.")] = None
    rpm_limit: Annotated[int | None, Field(default=None, description="Requests per minute rate limit.")] = None
    is_gemini_v3: Annotated[bool, Field(default=False, description="Whether target is a Gemini 2.5 or 3+ model.")] = (
        False
    )
    is_openai_reasoning: Annotated[
        bool, Field(default=False, description="Whether target is an OpenAI reasoning model.")
    ] = False


class ModelRegistryMetadataDTO(BaseModel):
    """Metadata container for model registry identity and default provider."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    registry_id: Annotated[str, Field(description="Opaque or slug identifier of the model registry.")]
    registry_name: Annotated[str, Field(description="Human-readable name of the model registry.")]
    default_provider: Annotated[str, Field(description="Default LLM provider of the registry.")]


class SeedRegistryEntryDTO(BaseModel):
    """Raw seed entry for a model registry in system_config."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: str = ""
    name: str = "Default Model Registry"
    type: str = "model_registry"
    slug: str | None = None
    default_provider: str = "google"
    tier_definitions: dict[str, JsonValue] = Field(default_factory=dict)
    models: dict[str, JsonValue] = Field(default_factory=dict)


def resolve_model_telemetry(
    db_path: Path,
    registry_id: str | None = None,
) -> dict[str, ModelTelemetryItemDTO]:
    """Load model registry from active database and resolve physical and effective parameters.

    Supports Option A flat tier definitions (fast, balanced, deep, reasoning) and multi-registry
    keyed lookup by ID, slug, name, or provider.

    Args:
        db_path: Path to database (data/db_v2.json) or seed file.
        registry_id: Optional model registry ID, slug, provider, or name substring.

    Returns:
        Dictionary mapping strategy/tier names to structured ModelTelemetryItemDTO instances.
    """
    target_path = db_path if db_path.exists() else Path("backend_v2/seed/seed_data.json")
    if not target_path.exists():
        return {}

    try:
        with target_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError, UnicodeDecodeError, OSError:
        return {}

    if type(data) is not dict:
        return {}

    sys_configs = data.get("system_config", [])
    raw_configs: Sequence[JsonValue] = []
    if type(sys_configs) is dict:
        raw_configs = list(sys_configs.values())
    elif type(sys_configs) is list:
        raw_configs = sys_configs

    registries: list[SeedRegistryEntryDTO] = []
    for c in raw_configs:
        try:
            entry = SeedRegistryEntryDTO.model_validate(c)
            if entry.type == "model_registry":
                registries.append(entry)
        except ValidationError, TypeError, ValueError:
            continue

    if not registries:
        return {}

    selected_registry: SeedRegistryEntryDTO | None = None
    if registry_id:
        reg_term = registry_id.strip().lower()
        for r in registries:
            if r.id.lower() == reg_term:
                selected_registry = r
                break
            if r.slug and r.slug.lower() == reg_term:
                selected_registry = r
                break
            if reg_term in r.name.lower():
                selected_registry = r
                break
            if r.default_provider.lower() == reg_term:
                selected_registry = r
                break

    target_registries = [selected_registry] if selected_registry is not None else registries

    models_dict: dict[str, tuple[ModelProfile, ModelRegistryMetadataDTO]] = {}
    for entry in target_registries:
        reg_meta = ModelRegistryMetadataDTO(
            registry_id=entry.id,
            registry_name=entry.name,
            default_provider=entry.default_provider.lower(),
        )
        reg_provider = reg_meta.default_provider
        tier_defs = entry.tier_definitions
        if tier_defs:
            for key, val in tier_defs.items():
                if type(val) is dict:
                    if "model_name" in val:
                        tier_name = str(key)
                        prov_key = f"{tier_name} ({reg_provider})"
                        profile = ModelProfile.model_validate(val)
                        models_dict[prov_key] = (profile, reg_meta)
                        if tier_name not in models_dict or selected_registry is not None:
                            models_dict[tier_name] = (profile, reg_meta)
                    else:
                        for t_name, raw_tier_val in val.items():
                            if type(raw_tier_val) is dict:
                                prov_key = f"{t_name} ({key})"
                                tier_profile = ModelProfile.model_validate(raw_tier_val)
                                models_dict[prov_key] = (tier_profile, reg_meta)
                                if t_name not in models_dict:
                                    models_dict[t_name] = (tier_profile, reg_meta)
        models_raw = entry.models
        if models_raw:
            for m_name, m_cfg in models_raw.items():
                if type(m_cfg) is dict:
                    raw_dict = dict(m_cfg)
                    if "provider" not in raw_dict:
                        raw_dict["provider"] = reg_provider
                    raw_profile = ModelProfile.model_validate(raw_dict)
                    models_dict[str(m_name)] = (raw_profile, reg_meta)

    result: dict[str, ModelTelemetryItemDTO] = {}
    for strat, (prof_item, cfg_meta) in models_dict.items():
        model_name = prof_item.model_name
        provider = prof_item.provider
        db_temp = prof_item.temperature
        max_tokens = prof_item.max_tokens
        thinking_budget = prof_item.thinking_budget_tokens or 0
        tpm_limit = prof_item.tpm_limit
        rpm_limit = prof_item.rpm_limit
        explicit_effort = prof_item.additional_params.reasoning_effort

        is_gemini_v3 = ("gemini-3" in model_name.lower()) or ("gemini-2.5" in model_name.lower())
        is_openai_reasoning = any(p in model_name.lower() for p in ("o1", "o3", "o4", "o5", "gpt-5"))

        if is_gemini_v3:
            provider_backend = "Google AI Studio" if "gemini/" in model_name.lower() else "Google Vertex AI"
            eff_temp = "1.0 (Fixed default; adapter strips sampling parameters)"
            think_str = f"{thinking_budget} tok" if thinking_budget > 0 else "0 tok (no thinking)"
            effort_str = f"N/A ({provider_backend} uses thinkingBudget tokens)"
        elif is_openai_reasoning:
            provider_backend = "OpenAI"
            eff_temp = "1.0 (Fixed default; adapter strips sampling parameters)"
            if explicit_effort:
                effort = explicit_effort
            elif thinking_budget <= 2048:
                effort = "low"
            elif thinking_budget <= 4096:
                effort = "medium"
            else:
                effort = "high"
            think_str = f"{thinking_budget} tok"
            effort_str = f"'{effort}' (derived from thinking_budget_tokens {thinking_budget})"
        else:
            provider_backend = provider
            eff_temp = str(db_temp) if db_temp is not None else "None"
            think_str = f"{thinking_budget} tok" if thinking_budget > 0 else "N/A"
            effort_str = "N/A"

        result[strat] = ModelTelemetryItemDTO(
            strategy=strat,
            registry_id=cfg_meta.registry_id,
            registry_name=cfg_meta.registry_name,
            provider=provider,
            backend=provider_backend,
            model_name=model_name,
            db_temperature=db_temp,
            effective_temperature=eff_temp,
            thinking_budget=think_str,
            reasoning_effort=effort_str,
            max_tokens=max_tokens,
            tpm_limit=tpm_limit,
            rpm_limit=rpm_limit,
            is_gemini_v3=is_gemini_v3,
            is_openai_reasoning=is_openai_reasoning,
        )
    return result


def print_model_telemetry(
    db_path: Path,
    active_strategies: list[str] | None = None,
    registry_id: str | None = None,
) -> None:
    """Print verified physical and effective model parameters loaded from the database.

    Args:
        db_path: Path to database or seed file.
        active_strategies: Optional targeted strategies list.
        registry_id: Optional model registry ID or slug to target.
    """
    telemetry = resolve_model_telemetry(db_path, registry_id=registry_id)
    target_path = db_path if db_path.exists() else Path("backend_v2/seed/seed_data.json")
    if not telemetry:
        print(f"[Model Telemetry] Warning: Model registry not found in {target_path}")
        return

    first_item = next(iter(telemetry.values()))
    reg_name = first_item.registry_name
    reg_id = first_item.registry_id
    reg_prov = first_item.provider.upper()

    print("\n" + "=" * 80)
    if registry_id and reg_name:
        print(f"[Fyysiset Malliparametrit ja Telemetria] Stack: '{reg_name}' (ID: {reg_id}, Provider: {reg_prov})")
    else:
        print(f"[Fyysiset Malliparametrit ja Telemetria] (Lähde: {target_path})")
    print("=" * 80)

    ordered_keys = list(active_strategies) if active_strategies else []
    for k in sorted(telemetry.keys()):
        if k not in ordered_keys:
            ordered_keys.append(k)

    for strat in ordered_keys:
        t = telemetry.get(strat)
        if not t:
            continue
        marker = " [AKTIIVINEN TESTIKOHDE]" if active_strategies and strat in active_strategies else ""
        print(f"  • Strategia '{strat}' ({t.provider.upper()} / {t.backend}){marker}:")
        print(f"    - Fyysinen malli:       {t.model_name}")
        print(f"    - DB Lämpötila:         {t.db_temperature if t.db_temperature is not None else 'Default'}")
        print(f"    - Efektiivinen temp:    {t.effective_temperature}")
        print(f"    - Thinking budget:      {t.thinking_budget}")
        print(f"    - Reasoning effort:     {t.reasoning_effort}")
        if t.max_tokens:
            print(f"    - Max Tokens:           {t.max_tokens}")
        if t.rpm_limit or t.tpm_limit:
            print(f"    - Rate limits:          {t.rpm_limit or 'N/A'} RPM, {t.tpm_limit or 'N/A'} TPM")


QUORUM_SYSTEM_DIRECTIVE: Final[str] = (
    "<system_directive>\n"
    "You are the Quorum Evaluation Engine operating under strict Popperian null hypothesis falsification "
    "and forensic evidence standards.\n"
    "Evaluate whether the TARGET PROPOSITION is factually and empirically true based strictly and exclusively "
    "on the provided SOURCE DOCUMENT.\n\n"
    "<extraction_rules>\n"
    "1. Null Hypothesis Default: Assume the proposition is FALSE unless indisputable, verbatim empirical evidence "
    "in the source document directly proves it true.\n"
    "2. Forensic Citation: If is_true is True, you MUST extract the exact verbatim source quote supporting the claim. "
    "The quote must match the source text character-for-character.\n"
    "3. Negative Falsification: If is_true is False, source_quote MUST be null. Never attach evidence quotes to refuted claims.\n"
    "4. Anti-Chimera Rule: Do not paraphrase, stitch non-contiguous phrases, or invent citations.\n"
    "</extraction_rules>\n"
    "</system_directive>"
)

UNCONSTRAINED_SYSTEM_DIRECTIVE: Final[str] = (
    "<system_directive>\n"
    "You are an AI assistant evaluating whether a proposition is supported by a document.\n"
    "Determine if the proposition is true or false based on the text.\n"
    "</system_directive>"
)


def build_quorum_standard_prompt(claim_text: str, source_text: str) -> tuple[str, str]:
    """Build Four-Layer Clean Stack prompt for Quorum standard configurations (Configs 1, 2, 3).

    Args:
        claim_text: Proposition claim asserted.
        source_text: Grounding source document text.

    Returns:
        Tuple of (system_prompt, user_payload).
    """
    user_payload = (
        f"<source_document>\n{source_text}\n</source_document>\n\n"
        f"<target_proposition>\n{claim_text}\n</target_proposition>"
    )
    return QUORUM_SYSTEM_DIRECTIVE, user_payload


def build_unconstrained_prompt(claim_text: str, source_text: str) -> tuple[str, str]:
    """Build unconstrained single-pass prompt for Config 4.

    Args:
        claim_text: Proposition claim asserted.
        source_text: Grounding source document text.

    Returns:
        Tuple of (system_prompt, user_payload).
    """
    user_payload = f"<source_document>\n{source_text}\n</source_document>\n\n<statement>\n{claim_text}\n</statement>"
    return UNCONSTRAINED_SYSTEM_DIRECTIVE, user_payload


def build_monolithic_step_prompt(
    step_id: str,
    propositions: list[AblationPropositionDTO],
    source_text: str,
) -> tuple[str, str]:
    """Build unified step-level prompt evaluating all step criteria in a single LLM pass (Config 5).

    Args:
        step_id: Workflow step grouping identifier.
        propositions: List of propositions to evaluate together.
        source_text: Grounding source document text.

    Returns:
        Tuple of (system_prompt, user_payload).
    """
    system_prompt = (
        f"<system_directive>\n"
        f"You are a monolithic evaluation judge assessing multiple criteria for workflow step: '{step_id}'.\n"
        f"For each listed proposition, evaluate whether it is true or false based on the source document.\n"
        f"Return an evaluation entry for every proposition ID.\n"
        f"</system_directive>"
    )
    props_text = "\n".join(f"- ID: {p.tda_id} | Claim: {p.claim_text}" for p in propositions)
    user_payload = (
        f"<source_document>\n{source_text}\n</source_document>\n\n"
        f"<propositions_to_evaluate>\n{props_text}\n</propositions_to_evaluate>"
    )
    return system_prompt, user_payload


class AblationLiveExecutor:
    """Asynchronous live LLM execution engine for multi-tier ablation benchmarks."""

    def __init__(
        self,
        config: AblationLiveExecutionConfigDTO,
        client_1: LLMClient,
        client_2: LLMClient | None = None,
        semaphore: asyncio.Semaphore | None = None,
    ) -> None:
        """Initialize the live ablation executor.

        Args:
            config: Execution configuration.
            client_1: Primary LLM client for Run 1 evaluations.
            client_2: Secondary LLM client for Run 2 evaluations (or Cross-Model comparisons).
            semaphore: Shared concurrency limiter.
        """
        self.config = config
        self.client_1 = client_1
        self.client_2 = client_2 if client_2 is not None else client_1
        self.semaphore = semaphore if semaphore is not None else asyncio.Semaphore(config.concurrency_limit)
        self.is_cross_model = config.compare_providers is not None or config.compare_strategies is not None

    @classmethod
    async def create(cls, config: AblationLiveExecutionConfigDTO) -> AblationLiveExecutor:
        """Asynchronously initialize the executor, database repositories, and LLM clients.

        Args:
            config: Execution configuration.

        Returns:
            Configured AblationLiveExecutor instance.
        """
        settings = get_settings()
        driver = await get_driver(settings)
        repo = SystemRepositoryImpl(driver)

        if config.compare_providers:
            prov_str_1, prov_str_2 = config.compare_providers
            prov_1 = cls._resolve_provider_enum(prov_str_1)
            prov_2 = cls._resolve_provider_enum(prov_str_2)
            logger.info(
                "[AblationLiveExecutor] Initializing dual Cross-Model clients: %s vs %s",
                prov_1.value,
                prov_2.value,
            )
            client_1 = await LLMClient.from_tier(config.tier, repository=repo, provider=prov_1)
            client_2 = await LLMClient.from_tier(config.tier, repository=repo, provider=prov_2)
        elif config.compare_strategies:
            strat_1, strat_2 = config.compare_strategies
            logger.info(
                "[AblationLiveExecutor] Initializing dual Cross-Strategy clients: %s vs %s",
                strat_1,
                strat_2,
            )
            client_1 = await LLMClient.from_strategy(strat_1, repository=repo)
            client_2 = await LLMClient.from_strategy(strat_2, repository=repo)
        else:
            client_1 = await LLMClient.from_tier(config.tier, repository=repo)
            client_2 = client_1

        semaphore = asyncio.Semaphore(config.concurrency_limit)
        return cls(config=config, client_1=client_1, client_2=client_2, semaphore=semaphore)

    @staticmethod
    def _resolve_provider_enum(provider_name: str) -> LLMProvider:
        """Map human or CLI provider string to LLMProvider enum.

        Args:
            provider_name: Provider name ('google', 'ai_studio', 'vertex', 'openai', etc.).

        Returns:
            Canonical LLMProvider member.
        """
        norm = provider_name.strip().lower()
        if norm in ("google", "ai_studio", "gemini"):
            return LLMProvider.AI_STUDIO
        if norm in ("vertex", "vertex_ai", "gcp"):
            return LLMProvider.VERTEX_AI
        if norm in ("openai", "gpt"):
            return LLMProvider.OPENAI
        if norm in ("anthropic", "claude"):
            return LLMProvider.ANTHROPIC
        return LLMProvider(norm)

    def _validate_quote_lexically(
        self,
        quote: str | Sequence[str] | tuple[str, ...] | list[str] | None,
        source_text: str,
    ) -> bool:
        """Validate citation evidence strictly against source text using AnchorValidationService.

        Args:
            quote: Extracted evidence quote string or multi-segment tuple.
            source_text: Original grounding source document text.

        Returns:
            True if quote is verified in source; False otherwise.
        """
        if quote is None:
            return False

        clean_source = unicodedata.normalize("NFKC", source_text)
        norm_text, _ = AnchorValidationService.normalize_text_with_mapping(clean_source)

        if isinstance(quote, (list, tuple, Sequence)) and not isinstance(quote, str):
            quotes_tuple = tuple(q for q in quote if q is not None and str(q).strip())
            if not quotes_tuple:
                return False
            norm_quotes_list: list[str] = []
            for q in quotes_tuple:
                clean_q = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", str(q)))
                nq, _ = AnchorValidationService.normalize_text_with_mapping(clean_q)
                if not nq:
                    return False
                norm_quotes_list.append(nq)

            match_res = AnchorValidationService._is_lexically_valid(
                quote=quotes_tuple,
                norm_quote=tuple(norm_quotes_list),
                norm_text=norm_text,
                source_text=clean_source,
            )
            return match_res.is_valid is True

        clean_q = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", str(quote)))
        nq, _ = AnchorValidationService.normalize_text_with_mapping(clean_q)
        if not nq:
            return False

        match_res = AnchorValidationService._is_lexically_valid(
            quote=str(quote),
            norm_quote=nq,
            norm_text=norm_text,
            source_text=clean_source,
        )
        return match_res.is_valid is True

    async def _execute_single_call(
        self,
        client: LLMClient,
        system_prompt: str,
        user_payload: str,
    ) -> AblationStructuredResponseDTO:
        """Execute one structured LLM call under the concurrency semaphore.

        Args:
            client: Target LLM client.
            system_prompt: System directive.
            user_payload: User payload.

        Returns:
            Parsed AblationStructuredResponseDTO.
        """
        async with self.semaphore:
            messages = [
                LLMMessageDTO(role="system", content=system_prompt),
                LLMMessageDTO(role="user", content=user_payload),
            ]
            res, _ = await client.run_structured_task(
                messages=messages,
                response_model=AblationStructuredResponseDTO,
            )
            return res

    async def evaluate_atom_live(
        self,
        prop: AblationPropositionDTO,
        config_id: int,
        source_text: str,
        run_index: int = 1,
    ) -> AblationAtomEvaluationDTO:
        """Evaluate a single proposition atom under the designated ablation configuration.

        Args:
            prop: Proposition specification.
            config_id: Configuration ID (1-4).
            source_text: Source document grounding text.
            run_index: 1 for Run 1, 2 for Run 2.

        Returns:
            AblationAtomEvaluationDTO recording the outcome.
        """
        client = self.client_1 if run_index == 1 else self.client_2

        # Config 4: Unconstrained single-pass
        if config_id == 4:
            sys_p, usr_p = build_unconstrained_prompt(prop.claim_text, source_text)
            try:
                res = await self._execute_single_call(client, sys_p, usr_p)
                raw_is_true = res.is_true
                q = res.source_quote
                qs = res.source_quotes
                # In Config 4: No firewall protection, claims pass unconstrained
                is_valid = self._validate_quote_lexically(qs or q, source_text) if raw_is_true and (q or qs) else False
                is_chimera = raw_is_true and not is_valid
                status = ExecutionStatus.PASSED if raw_is_true else ExecutionStatus.FAILED
                return AblationAtomEvaluationDTO(
                    tda_id=prop.tda_id,
                    raw_is_true=raw_is_true,
                    source_quote=q,
                    source_quotes=qs,
                    is_chimera=is_chimera,
                    status=status,
                )
            except (AppException, TimeoutError, ValueError, RuntimeError, OSError) as e:
                logger.warning("[Config 4] Inference failed for %s: %s", prop.tda_id, e)
                return AblationAtomEvaluationDTO(
                    tda_id=prop.tda_id,
                    raw_is_true=False,
                    is_chimera=False,
                    status=ExecutionStatus.SYSTEM_ERROR,
                    error_reason=str(e),
                )

        # Config 3: Single-Pass k=1 with Lexical Firewall
        if config_id == 3:
            sys_p, usr_p = build_quorum_standard_prompt(prop.claim_text, source_text)
            try:
                res = await self._execute_single_call(client, sys_p, usr_p)
                raw_is_true = res.is_true
                q = res.source_quote
                qs = res.source_quotes
                if raw_is_true:
                    is_valid = self._validate_quote_lexically(qs or q, source_text)
                    if is_valid:
                        return AblationAtomEvaluationDTO(
                            tda_id=prop.tda_id,
                            raw_is_true=True,
                            source_quote=q,
                            source_quotes=qs,
                            is_chimera=False,
                            status=ExecutionStatus.PASSED,
                        )
                    # Firewall rejection: unanchored or hallucinated quote rejected to FAILED
                    return AblationAtomEvaluationDTO(
                        tda_id=prop.tda_id,
                        raw_is_true=True,
                        source_quote=q,
                        source_quotes=qs,
                        is_chimera=True,
                        status=ExecutionStatus.FAILED,
                        error_reason="FIREWALL_REJECTED_CHIMERA_QUOTE",
                    )
                return AblationAtomEvaluationDTO(
                    tda_id=prop.tda_id,
                    raw_is_true=False,
                    is_chimera=False,
                    status=ExecutionStatus.FAILED,
                )
            except Exception as e:
                logger.warning("[Config 3] Inference failed for %s: %s", prop.tda_id, e)
                return AblationAtomEvaluationDTO(
                    tda_id=prop.tda_id,
                    raw_is_true=False,
                    is_chimera=False,
                    status=ExecutionStatus.SYSTEM_ERROR,
                    error_reason=f"SINGLE_PASS_EXCEPTION: {e}",
                )

        # Config 1 and 2: Best-of-3 ensemble (k=3)
        sys_p, usr_p = build_quorum_standard_prompt(prop.claim_text, source_text)
        responses: list[AblationStructuredResponseDTO] = []
        errors: list[Exception] = []

        async def _run_branch() -> None:
            try:
                b_res = await self._execute_single_call(client, sys_p, usr_p)
                responses.append(b_res)
            except (AppException, TimeoutError, ValueError, RuntimeError, OSError) as b_err:
                errors.append(b_err)

        async with asyncio.TaskGroup() as tg:
            for _ in range(3):
                tg.create_task(_run_branch())

        if not responses:
            return AblationAtomEvaluationDTO(
                tda_id=prop.tda_id,
                raw_is_true=False,
                is_chimera=False,
                status=ExecutionStatus.SYSTEM_ERROR,
                error_reason="ALL_BO3_BRANCHES_FAILED",
            )

        # Majority voting on is_true
        true_votes = sum(1 for r in responses if r.is_true)
        consensus_true = true_votes >= 2

        # Pick quote from the first positive branch if consensus is true
        positive_branches = [r for r in responses if r.is_true and (r.source_quote or r.source_quotes)]
        chosen_quote = positive_branches[0].source_quote if positive_branches else None
        chosen_quotes = positive_branches[0].source_quotes if positive_branches else None

        quote_target = chosen_quotes or chosen_quote
        is_quote_valid = self._validate_quote_lexically(quote_target, source_text) if quote_target else False

        # Config 1: Full Quorum (Bo3 + Lexical Firewall)
        if config_id == 1:
            if consensus_true:
                if is_quote_valid:
                    return AblationAtomEvaluationDTO(
                        tda_id=prop.tda_id,
                        raw_is_true=True,
                        source_quote=chosen_quote,
                        source_quotes=chosen_quotes,
                        is_chimera=False,
                        status=ExecutionStatus.PASSED,
                    )
                # Firewall blocks chimera quote despite consensus True
                return AblationAtomEvaluationDTO(
                    tda_id=prop.tda_id,
                    raw_is_true=True,
                    source_quote=chosen_quote,
                    source_quotes=chosen_quotes,
                    is_chimera=True,
                    status=ExecutionStatus.FAILED,
                    error_reason="FIREWALL_REJECTED_CHIMERA_QUOTE",
                )
            return AblationAtomEvaluationDTO(
                tda_id=prop.tda_id,
                raw_is_true=False,
                is_chimera=False,
                status=ExecutionStatus.FAILED,
            )

        # Config 2: Bo3 without Firewall (Accept raw consensus, audit chimeras)
        is_chimera = consensus_true and not is_quote_valid
        return AblationAtomEvaluationDTO(
            tda_id=prop.tda_id,
            raw_is_true=consensus_true,
            source_quote=chosen_quote,
            source_quotes=chosen_quotes,
            is_chimera=is_chimera,
            status=ExecutionStatus.PASSED if consensus_true else ExecutionStatus.FAILED,
        )

    async def evaluate_step_monolithic_live(
        self,
        step_id: str,
        props: list[AblationPropositionDTO],
        source_text: str,
        run_index: int = 1,
    ) -> list[AblationAtomEvaluationDTO]:
        """Evaluate all step criteria in a single monolithic prompt pass (Config 5).

        Detects missing proposition criteria and flags them as MISSING_FROM_MONOLITHIC_RESPONSE.

        Args:
            step_id: Step grouping identifier.
            props: List of propositions belonging to this step.
            source_text: Grounding source document text.
            run_index: 1 for Run 1, 2 for Run 2.

        Returns:
            List of AblationAtomEvaluationDTO instances matching props cardinality.
        """
        client = self.client_1 if run_index == 1 else self.client_2
        sys_p, usr_p = build_monolithic_step_prompt(step_id, props, source_text)

        try:
            async with self.semaphore:
                messages = [
                    LLMMessageDTO(role="system", content=sys_p),
                    LLMMessageDTO(role="user", content=usr_p),
                ]
                res, _ = await client.run_structured_task(
                    messages=messages,
                    response_model=AblationMonolithicResponseDTO,
                )

            res_map = {item.tda_id: item for item in res.evaluations}
            results: list[AblationAtomEvaluationDTO] = []

            for p in props:
                if p.tda_id in res_map:
                    item = res_map[p.tda_id]
                    q = item.source_quote
                    is_valid = self._validate_quote_lexically(q, source_text) if item.is_true and q else False
                    is_chimera = item.is_true and not is_valid
                    results.append(
                        AblationAtomEvaluationDTO(
                            tda_id=p.tda_id,
                            raw_is_true=item.is_true,
                            source_quote=q,
                            is_chimera=is_chimera,
                            status=ExecutionStatus.PASSED if item.is_true else ExecutionStatus.FAILED,
                        )
                    )
                else:
                    # Proposition was omitted by the monolithic judge (attention loss / context bottleneck)
                    results.append(
                        AblationAtomEvaluationDTO(
                            tda_id=p.tda_id,
                            raw_is_true=False,
                            is_chimera=False,
                            status=ExecutionStatus.FAILED,
                            error_reason="MISSING_FROM_MONOLITHIC_RESPONSE",
                        )
                    )
            return results

        except (AppException, TimeoutError, ValueError, RuntimeError, OSError) as e:
            logger.warning("[Config 5] Monolithic step evaluation failed for %s: %s", step_id, e)
            return [
                AblationAtomEvaluationDTO(
                    tda_id=p.tda_id,
                    raw_is_true=False,
                    is_chimera=False,
                    status=ExecutionStatus.SYSTEM_ERROR,
                    error_reason=f"MONOLITHIC_STEP_EXCEPTION: {e}",
                )
                for p in props
            ]

    async def evaluate_configuration_live(
        self,
        config_id: int,
        propositions: list[AblationPropositionDTO],
        source_text: str,
        run_index: int = 1,
    ) -> list[AblationAtomEvaluationDTO]:
        """Execute all propositions for a configuration in the specified run index.

        Args:
            config_id: Target configuration ID (1-5).
            propositions: List of propositions to evaluate.
            source_text: Source document grounding context.
            run_index: Run index (1 or 2).

        Returns:
            List of evaluated atom decisions.
        """
        if config_id == 5:
            # Group by step_id
            step_groups: dict[str, list[AblationPropositionDTO]] = {}
            for p in propositions:
                step_groups.setdefault(p.step_id, []).append(p)

            results: list[AblationAtomEvaluationDTO] = []
            for step_id, step_props in step_groups.items():
                step_res = await self.evaluate_step_monolithic_live(
                    step_id=step_id,
                    props=step_props,
                    source_text=source_text,
                    run_index=run_index,
                )
                results.extend(step_res)
            return results

        tasks: list[asyncio.Task[AblationAtomEvaluationDTO]] = []
        async with asyncio.TaskGroup() as tg:
            for p in propositions:
                tasks.append(
                    tg.create_task(
                        self.evaluate_atom_live(
                            prop=p,
                            config_id=config_id,
                            source_text=source_text,
                            run_index=run_index,
                        )
                    )
                )

        return [t.result() for t in tasks]


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser for the live ablation executor."""
    parser = argparse.ArgumentParser(
        prog="ablation_live_executor.py",
        description=(
            "Asynchronous live LLM execution engine for multi-tier ablation benchmarks.\n\n"
            "Evaluates proposition atoms across the five research ablation configurations\n"
            "using in-process LLMClient, AnchorValidationService, and structured outputs under Python 3.14."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=1,
        help="Target configuration ID to execute (1-5).",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of evaluation runs to execute.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint for ablation_live_executor."""
    parser = build_arg_parser()
    _ = parser.parse_args(argv)
    print(
        "AblationLiveExecutor CLI interface initialized. Use run_ablation_benchmark.py for end-to-end benchmark execution."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
