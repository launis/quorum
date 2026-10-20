"""Unit tests for asynchronous live LLM ablation execution engine (scripts/ablation_live_executor.py).

Verifies prompt builders, in-process executor logic, Best-of-3 voting, lexical firewall rejection,
chimera detection, single-pass transient error DLQ transition, monolithic step judging, omission detection,
concurrency semaphore management, and dual-client cross-model dispatch.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import CognitiveTier, ExecutionStatus, LLMProvider
from backend_v2.models.llm import TokenUsage
from scripts.ablation_live_executor import (
    AblationAtomEvaluationDTO,
    AblationLiveExecutionConfigDTO,
    AblationLiveExecutor,
    AblationMode,
    AblationMonolithicItemDTO,
    AblationMonolithicResponseDTO,
    AblationPropositionDTO,
    AblationStepBatchDTO,
    AblationStructuredResponseDTO,
    ModelTelemetryItemDTO,
    TraceEvaluationRawDTO,
    build_monolithic_step_prompt,
    build_quorum_standard_prompt,
    build_unconstrained_prompt,
    coerce_source_quotes_tuple,
    print_model_telemetry,
    resolve_model_telemetry,
)


@pytest.fixture
def sample_grounding_text() -> str:
    """Provide realistic grounding source text for citation validation."""
    return (
        "Johtoryhmän kokous 15.1.2026. Päätettiin hyväksyä uusi tekoälystrategia "
        "ja kohdentaa 500 000 euroa laadunvarmistukseen vuodelle 2026. "
        "Projektipäälliköksi nimitettiin Matti Meikäläinen."
    )


@pytest.fixture
def sample_propositions() -> list[AblationPropositionDTO]:
    """Provide structured propositions with both valid quotes and unanchored chimeras."""
    return [
        AblationPropositionDTO(
            tda_id="tda_001",
            step_id="step_strat",
            claim_text="Tekoälystrategia hyväksyttiin kokouksessa.",
            expected_true=True,
            synthetic_quote="Päätettiin hyväksyä uusi tekoälystrategia",
            is_quote_valid_in_source=True,
        ),
        AblationPropositionDTO(
            tda_id="tda_002",
            step_id="step_strat",
            claim_text="Budjetti oli miljoona euroa.",
            expected_true=False,
            synthetic_quote="budjetoitiin 1 000 000 euroa kehitykseen",
            is_quote_valid_in_source=False,
        ),
        AblationPropositionDTO(
            tda_id="tda_003",
            step_id="step_strat",
            claim_text="Matti Meikäläinen nimitettiin projektipäälliköksi.",
            expected_true=True,
            synthetic_quote="Projektipäälliköksi nimitettiin Matti Meikäläinen.",
            is_quote_valid_in_source=True,
        ),
    ]


def test_prompt_builders(sample_propositions: list[AblationPropositionDTO], sample_grounding_text: str) -> None:
    """Verify that all three Four-Layer Clean Stack prompt builders generate valid payloads."""
    # 1. Standard Quorum prompt
    sys_std, usr_std = build_quorum_standard_prompt(sample_propositions[0].claim_text, sample_grounding_text)
    assert "<system_directive>" in sys_std
    assert "Null Hypothesis Default" in sys_std
    assert "<target_proposition>" in usr_std
    assert sample_propositions[0].claim_text in usr_std
    assert "<source_document>" in usr_std

    # 2. Unconstrained prompt
    sys_unc, usr_unc = build_unconstrained_prompt(sample_propositions[0].claim_text, sample_grounding_text)
    assert "You are an AI assistant" in sys_unc
    assert "Null Hypothesis" not in sys_unc
    assert sample_propositions[0].claim_text in usr_unc

    # 3. Monolithic step prompt
    sys_mono, usr_mono = build_monolithic_step_prompt("step_strat", sample_propositions, sample_grounding_text)
    assert "step_strat" in sys_mono
    assert "<propositions_to_evaluate>" in usr_mono
    assert "tda_001" in usr_mono
    assert "tda_002" in usr_mono
    assert "tda_003" in usr_mono


@pytest.mark.asyncio
async def test_config_1_bo3_consensus_and_firewall(
    sample_propositions: list[AblationPropositionDTO],
    sample_grounding_text: str,
) -> None:
    """Verify Config 1: Best-of-3 voting consensus and lexical firewall enforcement."""
    mock_client = AsyncMock()
    usage = TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20)

    # 1. Valid quote: 3 positive votes with valid quote in source -> PASSED
    valid_res = AblationStructuredResponseDTO(
        is_true=True,
        source_quote="Päätettiin hyväksyä uusi tekoälystrategia",
        reasoning="Löytyy tekstistä.",
    )
    mock_client.run_structured_task.return_value = (valid_res, usage)

    config = AblationLiveExecutionConfigDTO(mode=AblationMode.LIVE, tier=CognitiveTier.FAST)
    executor = AblationLiveExecutor(config=config, client_1=mock_client)

    eval_dto = await executor.evaluate_atom_live(
        prop=sample_propositions[0],
        config_id=1,
        source_text=sample_grounding_text,
    )

    assert eval_dto.status == ExecutionStatus.PASSED
    assert eval_dto.raw_is_true is True
    assert eval_dto.is_chimera is False
    assert eval_dto.source_quote == "Päätettiin hyväksyä uusi tekoälystrategia"

    # 2. Chimera quote: 3 positive votes with hallucinated quote -> rejected by firewall to FAILED
    chimera_res = AblationStructuredResponseDTO(
        is_true=True,
        source_quote="Hallusinoitu lainaus jota ei ole dokumentissa",
        reasoning="Vaikuttaa todelta mutta keksitty lainaus.",
    )
    mock_client.run_structured_task.return_value = (chimera_res, usage)

    eval_chimera = await executor.evaluate_atom_live(
        prop=sample_propositions[1],
        config_id=1,
        source_text=sample_grounding_text,
    )

    assert eval_chimera.status == ExecutionStatus.FAILED
    assert eval_chimera.raw_is_true is True
    assert eval_chimera.is_chimera is True
    assert eval_chimera.error_reason == "FIREWALL_REJECTED_CHIMERA_QUOTE"


@pytest.mark.asyncio
async def test_config_2_chimera_accepted_without_firewall(
    sample_propositions: list[AblationPropositionDTO],
    sample_grounding_text: str,
) -> None:
    """Verify Config 2: Quorum without Lexical Firewall accepts chimera quotes as PASSED but flags is_chimera."""
    mock_client = AsyncMock()
    usage = TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20)

    chimera_res = AblationStructuredResponseDTO(
        is_true=True,
        source_quote="Hallusinoitu sitaatti",
        reasoning="Hyväksytään ilman leksikaalista tarkistusta.",
    )
    mock_client.run_structured_task.return_value = (chimera_res, usage)

    config = AblationLiveExecutionConfigDTO(mode=AblationMode.LIVE, tier=CognitiveTier.FAST)
    executor = AblationLiveExecutor(config=config, client_1=mock_client)

    eval_dto = await executor.evaluate_atom_live(
        prop=sample_propositions[1],
        config_id=2,
        source_text=sample_grounding_text,
    )

    # In Config 2: status is PASSED because model said is_true=True, but is_chimera is True
    assert eval_dto.status == ExecutionStatus.PASSED
    assert eval_dto.raw_is_true is True
    assert eval_dto.is_chimera is True


@pytest.mark.asyncio
async def test_config_3_single_pass_transient_error_dlq(
    sample_propositions: list[AblationPropositionDTO],
    sample_grounding_text: str,
) -> None:
    """Verify Config 3: Single-pass transient API error transitions proposition to SYSTEM_ERROR / DLQ."""
    mock_client = AsyncMock()
    mock_client.run_structured_task.side_effect = AppException(
        message="Transient Rate Limit 429",
        status_code=429,
        details={"error_code": "RATE_LIMIT_EXCEEDED"},
    )

    config = AblationLiveExecutionConfigDTO(mode=AblationMode.LIVE, tier=CognitiveTier.FAST)
    executor = AblationLiveExecutor(config=config, client_1=mock_client)

    eval_dto = await executor.evaluate_atom_live(
        prop=sample_propositions[0],
        config_id=3,
        source_text=sample_grounding_text,
    )

    assert eval_dto.status == ExecutionStatus.SYSTEM_ERROR
    assert eval_dto.raw_is_true is False
    assert "SINGLE_PASS_EXCEPTION" in str(eval_dto.error_reason)


@pytest.mark.asyncio
async def test_config_4_unconstrained_atom_judge(
    sample_propositions: list[AblationPropositionDTO],
    sample_grounding_text: str,
) -> None:
    """Verify Config 4: Atom-level unconstrained LLM-as-a-judge execution."""
    mock_client = AsyncMock()
    usage = TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20)

    unconstrained_res = AblationStructuredResponseDTO(
        is_true=False,
        source_quote=None,
        reasoning="Dokumentti ei tue väitettä.",
    )
    mock_client.run_structured_task.return_value = (unconstrained_res, usage)

    config = AblationLiveExecutionConfigDTO(mode=AblationMode.LIVE, tier=CognitiveTier.FAST)
    executor = AblationLiveExecutor(config=config, client_1=mock_client)

    eval_dto = await executor.evaluate_atom_live(
        prop=sample_propositions[1],
        config_id=4,
        source_text=sample_grounding_text,
    )

    assert eval_dto.status == ExecutionStatus.FAILED
    assert eval_dto.raw_is_true is False
    assert eval_dto.is_chimera is False


@pytest.mark.asyncio
async def test_config_5_monolithic_step_judge_with_omission(
    sample_propositions: list[AblationPropositionDTO],
    sample_grounding_text: str,
) -> None:
    """Verify Config 5: Monolithic step evaluation parses JSON array and flags omitted propositions."""
    mock_client = AsyncMock()
    usage = TokenUsage(prompt_tokens=50, completion_tokens=30, total_tokens=80)

    # Return response for only tda_001 and tda_002; omit tda_003 to simulate attention loss
    mono_res = AblationMonolithicResponseDTO(
        evaluations=[
            AblationMonolithicItemDTO(
                tda_id="tda_001",
                is_true=True,
                source_quote="Päätettiin hyväksyä uusi tekoälystrategia",
                reasoning="Löytyy tekstistä.",
            ),
            AblationMonolithicItemDTO(
                tda_id="tda_002",
                is_true=False,
                source_quote=None,
                reasoning="Ei löydy.",
            ),
        ]
    )
    mock_client.run_structured_task.return_value = (mono_res, usage)

    config = AblationLiveExecutionConfigDTO(mode=AblationMode.LIVE, tier=CognitiveTier.FAST)
    executor = AblationLiveExecutor(config=config, client_1=mock_client)

    step_results = await executor.evaluate_step_monolithic_live(
        step_id="step_strat",
        props=sample_propositions,
        source_text=sample_grounding_text,
    )

    assert len(step_results) == 3
    # Check tda_001
    assert step_results[0].tda_id == "tda_001"
    assert step_results[0].status == ExecutionStatus.PASSED

    # Check tda_002
    assert step_results[1].tda_id == "tda_002"
    assert step_results[1].status == ExecutionStatus.FAILED

    # Check omitted tda_003: MUST be flagged as FAILED with MISSING_FROM_MONOLITHIC_RESPONSE
    assert step_results[2].tda_id == "tda_003"
    assert step_results[2].status == ExecutionStatus.FAILED
    assert step_results[2].error_reason == "MISSING_FROM_MONOLITHIC_RESPONSE"


@pytest.mark.asyncio
async def test_cross_model_dual_client_dispatch(
    sample_propositions: list[AblationPropositionDTO],
    sample_grounding_text: str,
) -> None:
    """Verify that dual-client cross-model dispatch correctly routes Run 1 to client_1 and Run 2 to client_2."""
    mock_client_google = AsyncMock()
    mock_client_openai = AsyncMock()
    usage = TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20)

    res_google = AblationStructuredResponseDTO(
        is_true=True,
        source_quote="Päätettiin hyväksyä uusi tekoälystrategia",
        reasoning="Google Gemini havaitsi väitteen todeksi.",
    )
    res_openai = AblationStructuredResponseDTO(
        is_true=False,
        source_quote=None,
        reasoning="OpenAI GPT arvioi väitteen riittämättömäksi.",
    )

    mock_client_google.run_structured_task.return_value = (res_google, usage)
    mock_client_openai.run_structured_task.return_value = (res_openai, usage)

    config = AblationLiveExecutionConfigDTO(
        mode=AblationMode.LIVE,
        tier=CognitiveTier.FAST,
        compare_providers=("google", "openai"),
    )
    executor = AblationLiveExecutor(
        config=config,
        client_1=mock_client_google,
        client_2=mock_client_openai,
    )

    # Run 1 targeting Google Gemini
    evals_run1 = await executor.evaluate_configuration_live(
        config_id=4,
        propositions=[sample_propositions[0]],
        source_text=sample_grounding_text,
        run_index=1,
    )
    assert evals_run1[0].raw_is_true is True
    assert mock_client_google.run_structured_task.call_count == 1
    assert mock_client_openai.run_structured_task.call_count == 0

    # Run 2 targeting OpenAI GPT
    evals_run2 = await executor.evaluate_configuration_live(
        config_id=4,
        propositions=[sample_propositions[0]],
        source_text=sample_grounding_text,
        run_index=2,
    )
    assert evals_run2[0].raw_is_true is False
    assert mock_client_google.run_structured_task.call_count == 1
    assert mock_client_openai.run_structured_task.call_count == 1


@pytest.mark.asyncio
async def test_concurrency_semaphore_limit(
    sample_propositions: list[AblationPropositionDTO],
    sample_grounding_text: str,
) -> None:
    """Verify that concurrency semaphore strictly restricts parallel LLM requests."""
    active_requests = 0
    max_observed_concurrency = 0

    async def _mock_structured_task(*args: object, **kwargs: object) -> tuple[AblationStructuredResponseDTO, TokenUsage]:
        nonlocal active_requests, max_observed_concurrency
        active_requests += 1
        max_observed_concurrency = max(max_observed_concurrency, active_requests)
        await asyncio.sleep(0.01)
        active_requests -= 1
        return (
            AblationStructuredResponseDTO(is_true=False, source_quote=None, reasoning="test"),
            TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10),
        )

    mock_client = AsyncMock()
    mock_client.run_structured_task.side_effect = _mock_structured_task

    concurrency_ceiling = 2
    config = AblationLiveExecutionConfigDTO(
        mode=AblationMode.LIVE,
        tier=CognitiveTier.FAST,
        concurrency_limit=concurrency_ceiling,
    )
    semaphore = asyncio.Semaphore(concurrency_ceiling)
    executor = AblationLiveExecutor(config=config, client_1=mock_client, semaphore=semaphore)

    # Execute 3 propositions concurrently
    evals = await executor.evaluate_configuration_live(
        config_id=4,
        propositions=sample_propositions,
        source_text=sample_grounding_text,
        run_index=1,
    )

    assert len(evals) == 3
    assert max_observed_concurrency <= concurrency_ceiling


def test_coerce_source_quotes_tuple() -> None:
    """Verify coercion of various quote payload shapes into immutable tuples."""
    assert coerce_source_quotes_tuple(None) is None
    assert coerce_source_quotes_tuple("") is None
    assert coerce_source_quotes_tuple("   ") is None
    assert coerce_source_quotes_tuple("single quote") == ("single quote",)
    assert coerce_source_quotes_tuple(["a", "b", ""]) == ("a", "b")
    assert coerce_source_quotes_tuple([]) is None
    assert coerce_source_quotes_tuple(123) is None


def test_trace_evaluation_raw_dto_validation() -> None:
    """Verify trace evaluation DTO deserialization and field validation."""
    dto = TraceEvaluationRawDTO(
        tda_id="tda_123",
        status="PASSED",
        source_quotes=["q1", "q2"],
    )
    assert dto.tda_id == "tda_123"
    assert dto.status == "PASSED"
    assert dto.source_quotes == ("q1", "q2")


def test_resolve_model_telemetry_live(tmp_path: Path) -> None:
    """Verify resolve_model_telemetry against seed_data.json and custom mock DBs."""
    seed_path = Path("backend_v2/seed/seed_data.json")
    if seed_path.exists():
        res = resolve_model_telemetry(seed_path)
        assert len(res) > 0
        assert "fast" in res or any("fast" in k for k in res)

    # Test empty file
    empty_file = tmp_path / "empty_direct.json"
    empty_file.write_text(json.dumps({"system_config": []}), encoding="utf-8")
    assert resolve_model_telemetry(empty_file) == {}

    # Test malformed JSON
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{bad", encoding="utf-8")
    assert resolve_model_telemetry(bad_file) == {}

    # Test mock custom DB with reasoning models, dict system_config, and various tiers
    mock_db = tmp_path / "mock_db.json"
    mock_db.write_text(
        json.dumps({
            "system_config": {
                "reg_1": {
                    "id": "sys_test",
                    "slug": "test-registry-slug",
                    "name": "Test Registry Name",
                    "type": "model_registry",
                    "default_provider": "google",
                    "tier_definitions": {
                        "fast": {
                            "model_name": "gemini/gemini-3.8-flash",
                            "provider": "google",
                            "temperature": 1.0,
                            "thinking_budget_tokens": 0,
                        },
                        "balanced": {
                            "model_name": "o1-mini",
                            "provider": "openai",
                            "temperature": 1.0,
                            "thinking_budget_tokens": 1024,
                        },
                        "deep": {
                            "model_name": "o3-mini",
                            "provider": "openai",
                            "temperature": 1.0,
                            "thinking_budget_tokens": 3000,
                        },
                        "reasoning": {
                            "model_name": "gpt-5-preview",
                            "provider": "openai",
                            "temperature": 1.0,
                            "thinking_budget_tokens": 5000,
                            "additional_params": {"reasoning_effort": "high"},
                        },
                    },
                }
            }
        }),
        encoding="utf-8",
    )
    # Target by id
    res_id = resolve_model_telemetry(mock_db, registry_id="sys_test")
    assert "fast" in res_id
    assert res_id["fast"].is_gemini_v3 is True

    # Target by slug
    res_slug = resolve_model_telemetry(mock_db, registry_id="test-registry-slug")
    assert "balanced" in res_slug
    assert "'low'" in res_slug["balanced"].reasoning_effort
    assert "'medium'" in res_slug["deep"].reasoning_effort
    assert "'high'" in res_slug["reasoning"].reasoning_effort

    # Target by provider
    res_prov = resolve_model_telemetry(mock_db, registry_id="google")
    assert "fast" in res_prov

    # Target by name
    res_name = resolve_model_telemetry(mock_db, registry_id="registry name")
    assert "fast" in res_name


def test_resolve_provider_enum() -> None:
    """Verify provider string resolution to canonical LLMProvider enum."""
    assert AblationLiveExecutor._resolve_provider_enum("google") == LLMProvider.AI_STUDIO
    assert AblationLiveExecutor._resolve_provider_enum("gemini") == LLMProvider.AI_STUDIO
    assert AblationLiveExecutor._resolve_provider_enum("vertex") == LLMProvider.VERTEX_AI
    assert AblationLiveExecutor._resolve_provider_enum("openai") == LLMProvider.OPENAI
    assert AblationLiveExecutor._resolve_provider_enum("anthropic") == LLMProvider.ANTHROPIC
    assert AblationLiveExecutor._resolve_provider_enum("claude") == LLMProvider.ANTHROPIC


@pytest.mark.asyncio
async def test_executor_create_factory(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify AblationLiveExecutor.create initializes single and dual clients."""
    mock_from_tier = AsyncMock(return_value=AsyncMock())
    mock_from_strategy = AsyncMock(return_value=AsyncMock())
    monkeypatch.setattr("scripts.ablation_live_executor.LLMClient.from_tier", mock_from_tier)
    monkeypatch.setattr("scripts.ablation_live_executor.LLMClient.from_strategy", mock_from_strategy)
    monkeypatch.setattr("scripts.ablation_live_executor.get_driver", AsyncMock())

    # 1. Dual cross-model
    cfg_dual_model = AblationLiveExecutionConfigDTO(
        mode=AblationMode.LIVE,
        tier=CognitiveTier.FAST,
        compare_providers=("google", "openai"),
    )
    exec_dm = await AblationLiveExecutor.create(cfg_dual_model)
    assert exec_dm.client_1 is not None
    assert exec_dm.client_2 is not None

    # 2. Dual cross-strategy
    cfg_dual_strat = AblationLiveExecutionConfigDTO(
        mode=AblationMode.LIVE,
        tier=CognitiveTier.FAST,
        compare_strategies=("fast", "deep"),
    )
    exec_ds = await AblationLiveExecutor.create(cfg_dual_strat)
    assert exec_ds.client_1 is not None
    assert exec_ds.client_2 is not None

    # 3. Single model
    cfg_single = AblationLiveExecutionConfigDTO(mode=AblationMode.LIVE, tier=CognitiveTier.FAST)
    exec_s = await AblationLiveExecutor.create(cfg_single)
    assert exec_s.client_1 is exec_s.client_2


def test_print_model_telemetry_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verify print_model_telemetry output formatting and warning on empty DB."""
    # Empty DB
    empty_file = tmp_path / "empty.json"
    empty_file.write_text(json.dumps({"system_config": []}), encoding="utf-8")
    print_model_telemetry(empty_file)
    out = capsys.readouterr().out
    assert "Warning: Model registry not found" in out

    # Populated DB
    mock_db = tmp_path / "pop_db.json"
    mock_db.write_text(
        json.dumps({
            "system_config": [
                {
                    "id": "sys_pop",
                    "name": "Populated Registry",
                    "type": "model_registry",
                    "default_provider": "google",
                    "tier_definitions": {
                        "fast": {
                            "model_name": "gemini/gemini-2.5-flash",
                            "provider": "google",
                            "temperature": 0.2,
                            "thinking_budget_tokens": 1024,
                            "max_tokens": 2048,
                            "rpm_limit": 100,
                            "tpm_limit": 10000,
                        }
                    },
                }
            ]
        }),
        encoding="utf-8",
    )
    print_model_telemetry(mock_db, active_strategies=["fast"], registry_id="sys_pop")
    out_pop = capsys.readouterr().out
    assert "Populated Registry" in out_pop
    assert "AKTIIVINEN TESTIKOHDE" in out_pop
    assert "gemini-2.5-flash" in out_pop


@pytest.mark.asyncio
async def test_evaluate_atom_live_timeout_retry(
    sample_propositions: list[AblationPropositionDTO],
    sample_grounding_text: str,
) -> None:
    """Verify evaluate_atom_live handles TimeoutError and transient exceptions gracefully."""
    mock_client = AsyncMock()
    mock_client.run_structured_task.side_effect = TimeoutError("Request timed out")

    config = AblationLiveExecutionConfigDTO(
        mode=AblationMode.LIVE,
        tier=CognitiveTier.FAST,
    )
    executor = AblationLiveExecutor(config=config, client_1=mock_client)

    eval_dto = await executor.evaluate_atom_live(
        prop=sample_propositions[0],
        config_id=3,
        source_text=sample_grounding_text,
    )
    assert eval_dto.status == ExecutionStatus.SYSTEM_ERROR
    assert "Request timed out" in (eval_dto.error_reason or "")


@pytest.mark.asyncio
async def test_evaluate_atom_live_config_3_chimera(
    sample_propositions: list[AblationPropositionDTO],
    sample_grounding_text: str,
) -> None:
    """Verify Config 3 single-pass rejects chimera quote to FAILED."""
    mock_client = AsyncMock()
    usage = TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10)
    mock_client.run_structured_task.return_value = (
        AblationStructuredResponseDTO(
            is_true=True,
            source_quote="Hallusinoitu lainaus",
            reasoning="Väite totta mutta lainaus puuttuu.",
        ),
        usage,
    )

    config = AblationLiveExecutionConfigDTO(mode=AblationMode.LIVE, tier=CognitiveTier.FAST)
    executor = AblationLiveExecutor(config=config, client_1=mock_client)

    eval_dto = await executor.evaluate_atom_live(
        prop=sample_propositions[1],
        config_id=3,
        source_text=sample_grounding_text,
    )
    assert eval_dto.status == ExecutionStatus.FAILED
    assert eval_dto.is_chimera is True
    assert eval_dto.error_reason == "FIREWALL_REJECTED_CHIMERA_QUOTE"


@pytest.mark.asyncio
async def test_evaluate_step_monolithic_live_exception(
    sample_propositions: list[AblationPropositionDTO],
    sample_grounding_text: str,
) -> None:
    """Verify evaluate_step_monolithic_live marks all propositions as SYSTEM_ERROR on unrecoverable failure."""
    mock_client = AsyncMock()
    mock_client.run_structured_task.side_effect = RuntimeError("Provider crash")

    config = AblationLiveExecutionConfigDTO(mode=AblationMode.LIVE, tier=CognitiveTier.FAST)
    executor = AblationLiveExecutor(config=config, client_1=mock_client)

    results = await executor.evaluate_step_monolithic_live(
        step_id="step_strat",
        props=sample_propositions,
        source_text=sample_grounding_text,
    )
    assert len(results) == len(sample_propositions)
    for res in results:
        assert res.status == ExecutionStatus.SYSTEM_ERROR
        assert "Provider crash" in (res.error_reason or "")


@pytest.mark.asyncio
async def test_evaluate_all_configurations_smoke(
    sample_propositions: list[AblationPropositionDTO],
    sample_grounding_text: str,
) -> None:
    """Verify evaluate_configuration_live across all 5 experimental configurations."""
    mock_client = AsyncMock()
    usage = TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20)

    # Mock atom response
    atom_res = AblationStructuredResponseDTO(
        is_true=True,
        source_quote="Päätettiin hyväksyä uusi tekoälystrategia",
        reasoning="Test reasoning.",
    )
    # Mock monolithic response
    mono_res = AblationMonolithicResponseDTO(
        evaluations=[
            AblationMonolithicItemDTO(tda_id="tda_001", is_true=True, source_quote="Päätettiin hyväksyä uusi tekoälystrategia"),
            AblationMonolithicItemDTO(tda_id="tda_002", is_true=False, source_quote=None),
            AblationMonolithicItemDTO(tda_id="tda_003", is_true=True, source_quote="Projektipäälliköksi nimitettiin Matti Meikäläinen."),
        ]
    )

    config = AblationLiveExecutionConfigDTO(mode=AblationMode.LIVE, tier=CognitiveTier.FAST)
    executor = AblationLiveExecutor(config=config, client_1=mock_client)

    for cfg_id in (1, 2, 3, 4, 5):
        if cfg_id == 5:
            mock_client.run_structured_task.return_value = (mono_res, usage)
        else:
            mock_client.run_structured_task.return_value = (atom_res, usage)

        res = await executor.evaluate_configuration_live(
            config_id=cfg_id,
            propositions=sample_propositions,
            source_text=sample_grounding_text,
            run_index=1,
        )
        assert len(res) == len(sample_propositions)


def test_dto_coercions_extra() -> None:
    """Verify synthetic_quotes and source_quotes coercion on DTOs."""
    prop = AblationPropositionDTO(
        tda_id="tda_extra",
        step_id="step_extra",
        claim_text="extra claim",
        expected_true=True,
        synthetic_quotes=["q1", "q2"],
        is_quote_valid_in_source=True,
    )
    assert prop.synthetic_quotes == ("q1", "q2")

    resp = AblationStructuredResponseDTO(
        is_true=True,
        source_quotes=["q1", "q2"],
        reasoning="extra reasoning",
    )
    assert resp.source_quotes == ("q1", "q2")


def test_validate_quote_lexically_multi_segment(sample_grounding_text: str) -> None:
    """Verify multi-segment quote validation in _validate_quote_lexically."""
    executor = AblationLiveExecutor(
        config=AblationLiveExecutionConfigDTO(mode=AblationMode.LIVE),
        client_1=AsyncMock(),
    )

    # Multi-segment valid (each segment >= 30 chars per MIN_MULTI_SEGMENT_FLOOR_CHARS)
    valid_multi = [
        "Päätettiin hyväksyä uusi tekoälystrategia",
        "Projektipäälliköksi nimitettiin Matti Meikäläinen.",
    ]
    assert executor._validate_quote_lexically(valid_multi, sample_grounding_text) is True

    # Multi-segment empty / whitespace
    assert executor._validate_quote_lexically(["", "  "], sample_grounding_text) is False

    # Multi-segment invalid
    invalid_multi = ["Tämä ei ole tekstissä", "Eikä tämäkään"]
    assert executor._validate_quote_lexically(invalid_multi, sample_grounding_text) is False

    # None quote
    assert executor._validate_quote_lexically(None, sample_grounding_text) is False


@pytest.mark.asyncio
async def test_evaluate_atom_live_config_4_exception(sample_grounding_text: str) -> None:
    """Verify evaluate_atom_live in Config 4 captures LLM failures gracefully."""
    mock_client = AsyncMock()
    mock_client.run_structured_task.side_effect = RuntimeError("Config 4 provider crash")

    executor = AblationLiveExecutor(config=AblationLiveExecutionConfigDTO(mode=AblationMode.LIVE), client_1=mock_client)
    prop = AblationPropositionDTO(
        tda_id="tda_err_4",
        step_id="step_err",
        claim_text="virheellinen väite",
        expected_true=False,
        is_quote_valid_in_source=False,
    )

    res = await executor.evaluate_atom_live(config_id=4, prop=prop, source_text=sample_grounding_text)
    assert res.status == ExecutionStatus.SYSTEM_ERROR
    assert "Config 4 provider crash" in (res.error_reason or "")


@pytest.mark.asyncio
async def test_evaluate_atom_live_bo3_all_branches_failed(sample_grounding_text: str) -> None:
    """Verify evaluate_atom_live returns SYSTEM_ERROR if all 3 Bo3 branches fail."""
    mock_client = AsyncMock()
    mock_client.run_structured_task.side_effect = TimeoutError("Network timeout on Bo3")

    executor = AblationLiveExecutor(config=AblationLiveExecutionConfigDTO(mode=AblationMode.LIVE), client_1=mock_client)
    prop = AblationPropositionDTO(
        tda_id="tda_all_fail",
        step_id="step_fail",
        claim_text="aikakatkaisu väite",
        expected_true=False,
        is_quote_valid_in_source=False,
    )

    res = await executor.evaluate_atom_live(config_id=1, prop=prop, source_text=sample_grounding_text)
    assert res.status == ExecutionStatus.SYSTEM_ERROR
    assert res.error_reason == "ALL_BO3_BRANCHES_FAILED"


def test_print_model_telemetry_without_registry_id(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify print_model_telemetry when registry_id is None."""
    db_path = Path("backend_v2/seed/seed_data.json")
    print_model_telemetry(db_path, registry_id=None)
    captured = capsys.readouterr()
    assert "Fyysiset Malliparametrit ja Telemetria" in captured.out
    assert "Strategia" in captured.out


