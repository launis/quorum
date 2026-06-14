"""Phase 3 Offline Migration ETL Script.

This script migrates the existing `seed_data.json` TDA assertions into a bilingual
structured format. It uses Vaihtoehto B (Option B) for initializing the LLMClient
directly from the seed_data.json configuration to run in standalone mode without
the entire TinyDB/FastAPI application context.
"""
import asyncio
import json
import logging
import sys
import uuid
from pathlib import Path

# Add project root to sys.path so backend_v2 module can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.llm.client import LLMClient
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.models.v2_core import I18nText
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# MILESTONE 1: LOCAL PYDANTIC TARGET SCHEMA
#
# Since the actual application models (v2_core.py) use extra='forbid' and do
# not yet know about the Phase 3 bilingual fields, we must declare our own
# forward-compatible models for the Draft JSON writing step.
# -------------------------------------------------------------------------

class AcceptanceCriterion(BaseModel):
    """Local ETL schema for an acceptance criterion."""
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    instruction: I18nText
    requires_contextual_override: bool = False

class AntiPattern(BaseModel):
    """Local ETL schema for a known anti-pattern."""
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    pattern: I18nText
    allows_contextual_excuse: bool = False

class MigratedTDAAssertion(BaseModel):
    """Local ETL schema representing the FUTURE V2 TDA Assertion structure."""
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    # The existing required fields
    tda_id: str = Field(pattern=r"^tda_[a-f0-9]{32}$")
    ai_rule_description: str
    inverse_evidence: bool
    aggregation_mode: Literal["EXISTS", "ALL_MUST_COMPLY"]
    evaluation_track: Literal["EXTRACTIVE_SENSOR", "COGNITIVE_JUDGEMENT"]
    facts_to_find: list[str]
    logical_expression: str | None
    allow_contextual_override: bool
    high_entropy: bool

    # The new bilingual/structured fields
    concept_description: I18nText
    acceptance_criteria: list[AcceptanceCriterion]
    anti_patterns: list[AntiPattern]
    contrastive_example: I18nText
    syntactic_anchors: list[str]
    enforce_pre_flight: bool = False

    # Pydantic will automatically validate the I18nText fields due to nested validation.


# -------------------------------------------------------------------------
# LLM RESPONSE SCHEMA (Strict structured output)
# -------------------------------------------------------------------------

class AcceptanceCriterionResponse(BaseModel):
    instruction_en: str
    instruction_fi: str
    requires_contextual_override: bool = False

class AntiPatternResponse(BaseModel):
    pattern_en: str
    pattern_fi: str
    allows_contextual_excuse: bool = False

class TDADecompositionResponse(BaseModel):
    """The schema enforced upon the LLM via Structured Outputs."""
    concept_description_en: str
    concept_description_fi: str
    acceptance_criteria: list[AcceptanceCriterionResponse]
    anti_patterns: list[AntiPatternResponse]
    contrastive_example_en: str
    contrastive_example_fi: str
    syntactic_anchors: list[str]


# -------------------------------------------------------------------------
# MILESTONE 2: ASYNC ETL PIPELINE
# -------------------------------------------------------------------------

async def transform_tda(
    tda: dict[str, Any],
    executor: LLMTaskExecutor,
    client: LLMClient
) -> dict[str, Any]:
    """Decompose a single TDA using the LLM via Structured Outputs."""
    legacy_rule = tda.get("ai_rule_description", "")
    tda_id = tda.get("tda_id") or f"tda_{uuid.uuid4().hex}"

    if not legacy_rule.strip():
        # Fallback if empty
        legacy_rule = "Empty rule. Evaluate logically."

    # Using f-string for template (equivalent to what's expected for prompt context)
    prompt = f"""You are a precise ontological decomposition engine.
Your task is to take the following legacy AI rule description (a flat string) and decompose it into the new bilingual, highly structured JSON schema.

LEGACY RULE DESCRIPTION:
{legacy_rule}

INSTRUCTIONS:
1. Extract the core concept and describe it formally in English (concept_description_en) and Finnish (concept_description_fi).
2. If there are positive conditions, add them to acceptance_criteria (in both en/fi).
3. If there are negative/veto conditions (like 'NEGATIVE CONDITION: data exists'), add them to anti_patterns (in both en/fi).
4. Provide a clear contrastive example (how it looks vs how it shouldn't look) in both languages.
5. Extract exact syntactic anchors (like specific words, markdown markers) into the syntactic_anchors array. If none exist, leave empty.
"""

    messages = [
        {"role": "system", "content": "You are a master of JSON schema decomposition and bilingual translation (English/Finnish)."},
        {"role": "user", "content": prompt}
    ]

    try:
        response, token_usage = await executor.execute_structured_task(
            client=client,
            messages=messages,
            response_model=TDADecompositionResponse
        )
    except Exception as e:
        logger.error(f"Failed to transform TDA {tda_id}: {e}")
        # Return unmodified but structured minimally if it fails, or bubble up.
        # For an ETL, we want to bubble up so we know it failed.
        raise

    # Convert the raw response into the formal local Pydantic model (Target Schema)

    acceptance_criteria_models = []
    for c in response.acceptance_criteria:
        acceptance_criteria_models.append(AcceptanceCriterion(
            instruction=I18nText(
                default_locale="en",
                translations={"en": c.instruction_en, "fi": c.instruction_fi}
            ),
            requires_contextual_override=c.requires_contextual_override
        ))

    anti_patterns_models = []
    for a in response.anti_patterns:
        anti_patterns_models.append(AntiPattern(
            pattern=I18nText(
                default_locale="en",
                translations={"en": a.pattern_en, "fi": a.pattern_fi}
            ),
            allows_contextual_excuse=a.allows_contextual_excuse
        ))

    migrated_tda = MigratedTDAAssertion(
        tda_id=tda_id,
        ai_rule_description=legacy_rule, # Retain original
        inverse_evidence=tda.get("inverse_evidence", False),
        aggregation_mode=tda.get("aggregation_mode", "EXISTS"),
        evaluation_track=tda.get("evaluation_track", "EXTRACTIVE_SENSOR"),
        facts_to_find=tda.get("facts_to_find", []),
        logical_expression=tda.get("logical_expression"),
        allow_contextual_override=tda.get("allow_contextual_override", False),
        high_entropy=tda.get("high_entropy", False),

        # New bilingual structured fields
        concept_description=I18nText(
            default_locale="en",
            translations={"en": response.concept_description_en, "fi": response.concept_description_fi}
        ),
        acceptance_criteria=acceptance_criteria_models,
        anti_patterns=anti_patterns_models,
        contrastive_example=I18nText(
            default_locale="en",
            translations={"en": response.contrastive_example_en, "fi": response.contrastive_example_fi}
        ),
        syntactic_anchors=response.syntactic_anchors,
        enforce_pre_flight=False
    )

    # Pydantic will automatically validate nested components.

    # Convert back to dict for JSON serialization
    return migrated_tda.model_dump(exclude_none=True)


async def migrate() -> None:
    seed_path = Path("backend_v2/seed/seed_data.json")
    if not seed_path.exists():
        raise FileNotFoundError(f"Missing {seed_path}")

    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    # 1. OPTION B: Bootstrap LLMClient from seed config directly
    system_configs = data.get("system_config", [])
    model_registry_doc = next((doc for doc in system_configs if doc.get("type") == "model_registry"), {})
    registry_raw = model_registry_doc.get("models", {})
    fast_strategy_raw = registry_raw.get("fast")
    if not fast_strategy_raw:
        raise ValueError("Could not locate 'fast' strategy in seed_data.json model_registry.")

    provider_config = LLMProviderConfig(
        id=f"prv_{uuid.uuid4().hex}",
        provider=fast_strategy_raw.get("provider", "litellm"),
        model_name=fast_strategy_raw.get("model_name"),
        api_key=fast_strategy_raw.get("api_key"),
        temperature=fast_strategy_raw.get("temperature", 0.0),
        top_p=fast_strategy_raw.get("top_p"),
        top_k=fast_strategy_raw.get("top_k"),
        tpm_limit=fast_strategy_raw.get("tpm_limit", 100000),
        rpm_limit=fast_strategy_raw.get("rpm_limit", 1000),
        default_max_tokens=fast_strategy_raw.get("max_tokens", 4000),
        supports_grounding=fast_strategy_raw.get("supports_grounding", False),
        parsing_mode=fast_strategy_raw.get("parsing_mode", "JSON"),
        caching_strategy=fast_strategy_raw.get("caching_strategy", "none"),
        additional_params=fast_strategy_raw.get("additional_params", {})
    )

    client = LLMClient(config=provider_config)
    executor = LLMTaskExecutor(prompt_compiler=PromptCompiler())

    # 2. Extract TDAs to process
    tda_refs: list[tuple[dict[str, Any], int, int, int, int]] = []

    blocks = data.get("prompt_blocks", [])
    for b_idx, block in enumerate(blocks):
        scales = block.get("scales", [])
        for s_idx, scale in enumerate(scales):
            claims = scale.get("claims", [])
            for c_idx, claim in enumerate(claims):
                tdas = claim.get("tda_assertions", [])
                for t_idx, tda in enumerate(tdas):
                    tda_refs.append((tda, b_idx, s_idx, c_idx, t_idx))

    logger.info(f"Found {len(tda_refs)} TDA Assertions to migrate.")

    # 3. Process in batches with asyncio.TaskGroup (Strict Rule 61: no asyncio.gather)
    BATCH_SIZE = 10
    total = len(tda_refs)

    for i in range(0, total, BATCH_SIZE):
        batch = tda_refs[i:i+BATCH_SIZE]
        logger.info(f"Processing batch {i//BATCH_SIZE + 1}/{(total+BATCH_SIZE-1)//BATCH_SIZE}...")

        async with asyncio.TaskGroup() as tg:
            tasks = []
            for tda, b_idx, s_idx, c_idx, t_idx in batch:
                task = tg.create_task(transform_tda(tda, executor, client))
                tasks.append((task, b_idx, s_idx, c_idx, t_idx))

        # Write results back to in-memory struct
        for task, b_idx, s_idx, c_idx, t_idx in tasks:
            migrated_dict = task.result()
            # Mutate the in-memory dictionary
            blocks[b_idx]["scales"][s_idx]["claims"][c_idx]["tda_assertions"][t_idx] = migrated_dict

    # -------------------------------------------------------------------------
    # MILESTONE 3: LIGHTWEIGHT EXTRACTION BLOCK
    # -------------------------------------------------------------------------
    # Add the new system rule block to prompt_blocks
    blocks.append({
        "id": "blk_a1b2c3d4e5f67890a1b2c3d4e5f67890",
        "slug": "lightweight_json_extraction",
        "category_id": "system_rule",
        "type": "instruction",
        "is_lightweight_protocol": True,
        "label": {
            "default_locale": "en",
            "translations": {
                "en": "Lightweight JSON Extraction",
                "fi": "Kevyt JSON-poiminta"
            }
        },
        "description": {
            "default_locale": "en",
            "translations": {
                "en": "Protocol block",
                "fi": "Protokollalohko"
            }
        },
        "ai_description": "CRITICAL SYSTEM PROTOCOL: You are performing a lightweight data extraction. You must only output pure valid JSON representing the Extracted Data. Do not write markdown blocks around the JSON. Do not include conversational filler. Do not generate rationale or semantic_reasoning unless explicitly instructed."
    })

    # 4. Save Draft
    out_path = Path("backend_v2/seed/seed_data_v2_draft.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    logger.info(f"Migration complete. Draft saved to {out_path}.")

if __name__ == "__main__":
    asyncio.run(migrate())

