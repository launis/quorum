"""Unit tests for RAGPreflightService."""

from collections.abc import Awaitable, Callable
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.blackboard import (
    DraftAtomList,
    DraftExtractedAtom,
    GlobalAtomBlackboard,
)
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.services.orchestrator.rag_preflight_service import (
    RAGPreflightService,
    _extract_inputs_from_record,
)


@pytest.fixture
def mock_workflow_repo() -> MagicMock:
    """Mock workflow repository."""
    return AsyncMock()


@pytest.fixture
def mock_system_repo() -> MagicMock:
    """Mock system repository."""
    repo = AsyncMock()
    repo.get_model_registry.return_value = {
        "id": "sys_e26807f3bfa3454d",
        "name": "Default Stack",
        "tier_definitions": {
            "fast": {
                "provider": "google",
                "model_name": "gemini-2.5-flash",
                "temperature": 0.0,
                "tpm_limit": 100000,
                "rpm_limit": 100,
            },
            "balanced": {
                "provider": "google",
                "model_name": "gemini-2.5-flash",
                "temperature": 0.0,
                "tpm_limit": 100000,
                "rpm_limit": 100,
            },
            "deep": {
                "provider": "google",
                "model_name": "gemini-2.5-pro",
                "temperature": 0.0,
                "tpm_limit": 100000,
                "rpm_limit": 100,
            },
            "reasoning": {
                "provider": "google",
                "model_name": "gemini-2.5-pro",
                "temperature": 0.0,
                "tpm_limit": 100000,
                "rpm_limit": 100,
            },
        },
    }
    return repo


@pytest.fixture
def mock_compiler() -> MagicMock:
    """Mock prompt compiler."""
    return MagicMock()


@pytest.fixture
def preflight_service(
    mock_workflow_repo: MagicMock, mock_system_repo: MagicMock, mock_compiler: MagicMock
) -> RAGPreflightService:
    """Provides initialized RAGPreflightService."""
    return RAGPreflightService(
        workflow_repo=mock_workflow_repo,
        system_repo=mock_system_repo,
        prompt_compiler=mock_compiler,
    )


def make_valid_step_def(cognitive_tier: str | None = "fast") -> Step:
    """Helper to create a valid Step object for testing."""
    return Step.model_validate(
        {
            "id": "stp_1234567890abcdef",
            "slug": "test_step",
            "name": {"translations": {"en": "Test Step"}},
            "description": {"translations": {"en": "Test Description"}},
            "cognitive_tier": cognitive_tier or "fast",
            "criteria_block_ids": ["blk_1234567890abcdef"],
            "extraction_protocol_block_id": "blk_1234567890abcdef",
            "type": "llm",
        }
    )


@pytest.mark.asyncio
async def test_rag_preflight_missing_task_blueprint_crashes(preflight_service: RAGPreflightService) -> None:
    """Tests that missing task_blueprint raises CONFIGURATION_ERROR AppException."""
    step_rule = StepRule.model_construct(
        id="stp_1234567890abcdef", task_blueprint=cast(Any, None), input_mappings={}, depends_on=[]
    )
    step_def = make_valid_step_def()
    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        output_profile_id="prof_1234567890abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "A" * 100}),
        target_locale="en",
        metadata=ExecutionMetadata(),
    )

    with pytest.raises(AppException) as exc_info:
        await preflight_service.execute(
            target_step=step_rule,
            step_def=step_def,
            exec_record=exec_record,
            emit_progress=AsyncMock(),
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_rag_preflight_missing_cognitive_tier_crashes(preflight_service: RAGPreflightService) -> None:
    """Tests that missing cognitive_tier raises CONFIGURATION_ERROR AppException."""
    step_rule = StepRule(
        id="stp_1234567890abcdef", task_blueprint="blp_1234567890abcdef", input_mappings={}, depends_on=[]
    )
    step_def = Step.model_construct(
        id="stp_1234567890abcdef",
        slug="test_step",
        name=I18nText(translations={"en": "Test Step"}),
        description=I18nText(translations={"en": "Test Description"}),
        cognitive_tier=None,
        type="llm",
    )
    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        output_profile_id="prof_1234567890abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "A" * 100}),
        target_locale="en",
        metadata=ExecutionMetadata(),
    )

    with pytest.raises(AppException) as exc_info:
        await preflight_service.execute(
            target_step=step_rule,
            step_def=step_def,
            exec_record=exec_record,
            emit_progress=AsyncMock(),
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.details.get("error_code") == ErrorCodes.CONFIGURATION_ERROR.value
    assert "has no cognitive_tier" in exc_info.value.message


@pytest.mark.asyncio
async def test_rag_preflight_input_below_character_threshold_skips(
    preflight_service: RAGPreflightService,
) -> None:
    """Tests that inputs below rag_preflight_min_input_chars (50 chars) skip atomization."""
    step_rule = StepRule(
        id="stp_1234567890abcdef", task_blueprint="blp_1234567890abcdef", input_mappings={}, depends_on=[]
    )
    step_def = make_valid_step_def()
    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        output_profile_id="prof_1234567890abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"short_doc": "Only 20 chars here.", "non_str": 123}),
        target_locale="en",
        metadata=ExecutionMetadata(),
    )

    emit_mock = AsyncMock()

    with patch("backend_v2.services.orchestrator.rag_preflight_service.TwoPassAtomizer") as mock_atomizer_cls:
        result = await preflight_service.execute(
            target_step=step_rule,
            step_def=step_def,
            exec_record=exec_record,
            emit_progress=emit_mock,
        )

        assert mock_atomizer_cls.called is False
        assert result == GlobalAtomBlackboard(atoms_by_input={}, is_data_starved=True)
        emit_mock.assert_called_once_with("Input data sparse/empty. Preflight extraction skipped.", 100)


@pytest.mark.asyncio
async def test_rag_preflight_happy_path_with_progress_callbacks(
    preflight_service: RAGPreflightService,
) -> None:
    """Tests full happy-path RAG preflight with multi-paragraph text and progress callbacks."""
    step_rule = StepRule(
        id="stp_1234567890abcdef", task_blueprint="blp_1234567890abcdef", input_mappings={}, depends_on=[]
    )
    step_def = make_valid_step_def()
    text_content = (
        "Paragraph one is substantive and provides context.\n\nParagraph two provides additional insights and evidence."
    )
    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        output_profile_id="prof_1234567890abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc_1": text_content, "skipped_key": "too short"}),
        target_locale="en",
        metadata=ExecutionMetadata(),
    )

    emit_mock = AsyncMock()

    atom = DraftExtractedAtom(
        draft_id="atm_1234567890abcdef",
        reasoning="Test reasoning",
        resolved_claim="Test claim",
        is_logical_deduction=False,
        source_quote="Paragraph one is substantive and provides context.",
        source_sequence_index=0,
    )

    with (
        patch("backend_v2.llm.client.LLMClient.from_tier") as mock_client_factory,
        patch("backend_v2.services.orchestrator.rag_preflight_service.TwoPassAtomizer") as mock_atomizer_cls,
    ):
        mock_client = AsyncMock()
        mock_client_factory.return_value = mock_client
        mock_atomizer = mock_atomizer_cls.return_value

        async def fake_phase_0(
            client: Any, text: str, progress_callback: Callable[[int, int], Awaitable[None]] | None = None
        ) -> tuple[dict[str, Any], TokenUsage]:
            if progress_callback:
                await progress_callback(50, 100)
            return {"ontology": "valid"}, TokenUsage(prompt_tokens=50, completion_tokens=10, total_tokens=60)

        async def fake_phase_1(
            client: Any,
            text: str,
            ontology: dict[str, Any],
            progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
        ) -> tuple[DraftAtomList, TokenUsage]:
            if progress_callback:
                await progress_callback(50, 100)
            return DraftAtomList(atoms=[atom]), TokenUsage(prompt_tokens=80, completion_tokens=20, total_tokens=100)

        mock_atomizer.execute_phase_0 = AsyncMock(side_effect=fake_phase_0)
        mock_atomizer.execute_phase_1_drafts = AsyncMock(side_effect=fake_phase_1)

        result = await preflight_service.execute(
            target_step=step_rule,
            step_def=step_def,
            exec_record=exec_record,
            emit_progress=emit_mock,
        )

        assert isinstance(result, GlobalAtomBlackboard)
        assert "doc_1" in result.atoms_by_input
        assert len(result.atoms_by_input["doc_1"].atoms) == 1
        assert emit_mock.call_count >= 3


@pytest.mark.asyncio
async def test_rag_preflight_atom_ceiling_exceeded_crashes(
    preflight_service: RAGPreflightService,
) -> None:
    """Tests that exceeding max_extracted_atoms_per_document raises VALIDATION_FAILED AppException."""
    step_rule = StepRule(
        id="stp_1234567890abcdef", task_blueprint="blp_1234567890abcdef", input_mappings={}, depends_on=[]
    )
    step_def = make_valid_step_def()
    text_content = "Valid long input text with more than fifty characters for analysis."
    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        output_profile_id="prof_1234567890abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc_1": text_content}),
        target_locale="en",
        metadata=ExecutionMetadata(),
    )

    atom = DraftExtractedAtom(
        draft_id="atm_1234567890abcdef",
        reasoning="Test",
        resolved_claim="Test",
        is_logical_deduction=False,
        source_quote="Valid long input text with more than fifty characters for analysis.",
        source_sequence_index=0,
    )

    with (
        patch("backend_v2.llm.client.LLMClient.from_tier") as mock_client_factory,
        patch("backend_v2.services.orchestrator.rag_preflight_service.TwoPassAtomizer") as mock_atomizer_cls,
        patch("backend_v2.services.orchestrator.rag_preflight_service.get_settings") as mock_settings,
    ):
        mock_client = AsyncMock()
        mock_client_factory.return_value = mock_client
        mock_atomizer = mock_atomizer_cls.return_value
        mock_atomizer.execute_phase_0 = AsyncMock(
            return_value=({}, TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15))
        )
        mock_atomizer.execute_phase_1_drafts = AsyncMock(
            return_value=(
                DraftAtomList(atoms=[atom, atom, atom]),
                TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
            )
        )

        settings_mock = MagicMock()
        settings_mock.rag_preflight_min_input_chars = 50
        settings_mock.max_extracted_atoms_per_document = 2
        mock_settings.return_value = settings_mock

        with pytest.raises(AppException) as exc_info:
            await preflight_service.execute(
                target_step=step_rule,
                step_def=step_def,
                exec_record=exec_record,
                emit_progress=AsyncMock(),
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.details.get("error_code") == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_rag_preflight_excludes_metadata_keys_from_count_and_atomization(
    preflight_service: RAGPreflightService,
) -> None:
    """Tests that excluded metadata keys (e.g. document_date) are ignored in count and atomization."""
    step_rule = StepRule(
        id="stp_1234567890abcdef", task_blueprint="blp_1234567890abcdef", input_mappings={}, depends_on=[]
    )
    step_def = make_valid_step_def()
    long_metadata = "2026-07-22T04:43:36+00:00" * 10  # 250 chars
    sparse_doc = "Sparse doc with only 30 chars."

    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        output_profile_id="prof_1234567890abcdef",
        raw_inputs=WorkflowInputs(
            dynamic_inputs={
                "document_date": long_metadata,
                "doc_1": sparse_doc,
            }
        ),
        target_locale="en",
        metadata=ExecutionMetadata(),
    )

    emit_mock = AsyncMock()

    with patch("backend_v2.services.orchestrator.rag_preflight_service.TwoPassAtomizer") as mock_atomizer_cls:
        result = await preflight_service.execute(
            target_step=step_rule,
            step_def=step_def,
            exec_record=exec_record,
            emit_progress=emit_mock,
        )

        # Since document_date is excluded and doc_1 has < 100 chars, it should skip
        assert mock_atomizer_cls.called is False
        assert result == GlobalAtomBlackboard(atoms_by_input={}, is_data_starved=True)


@pytest.mark.asyncio
async def test_rag_preflight_chat_log_with_large_ai_text_sparse_user_text_skips(
    preflight_service: RAGPreflightService,
) -> None:
    """Tests that large AI text with sparse user payload (<100 user chars) skips preflight."""
    step_rule = StepRule(
        id="stp_1234567890abcdef", task_blueprint="blp_1234567890abcdef", input_mappings={}, depends_on=[]
    )
    step_def = make_valid_step_def()
    large_ai_chat_log = (
        "<user_payload>\nmitä kuuluu?\n</user_payload>\n\n"
        "<ai_draft_context>\n" + ("Tämä on erittäin pitkä tekoälyn vastausteksti. " * 50) + "\n</ai_draft_context>"
    )

    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        output_profile_id="prof_1234567890abcdef",
        raw_inputs=WorkflowInputs(
            dynamic_inputs={
                "chat_log": large_ai_chat_log,
            }
        ),
        target_locale="en",
        metadata=ExecutionMetadata(),
    )

    emit_mock = AsyncMock()

    with patch("backend_v2.services.orchestrator.rag_preflight_service.TwoPassAtomizer") as mock_atomizer_cls:
        result = await preflight_service.execute(
            target_step=step_rule,
            step_def=step_def,
            exec_record=exec_record,
            emit_progress=emit_mock,
        )

        assert mock_atomizer_cls.called is False
        assert result == GlobalAtomBlackboard(atoms_by_input={}, is_data_starved=True)


@pytest.mark.asyncio
async def test_rag_preflight_chat_log_with_substantial_user_text_proceeds(
    preflight_service: RAGPreflightService,
) -> None:
    """Tests that chat log with substantial user payload (>100 user chars) proceeds with atomization."""
    step_rule = StepRule(
        id="stp_1234567890abcdef", task_blueprint="blp_1234567890abcdef", input_mappings={}, depends_on=[]
    )
    step_def = make_valid_step_def()
    substantial_user_chat_log = (
        "<user_payload>\n"
        "Olen toiminut tiiminvetäjänä viisi vuotta ja kehittänyt useita järjestelmiä "
        "kriittisissä ympäristöissä. Kokemukseni kattaa sekä arkkitehtuurisuunnittelun että johtamisen."
        "\n</user_payload>\n\n"
        "<ai_draft_context>\nKiitos tiedoista! Kerro lisää johtamiskokemuksestasi.\n</ai_draft_context>"
    )

    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        output_profile_id="prof_1234567890abcdef",
        raw_inputs=WorkflowInputs(
            dynamic_inputs={
                "chat_log": substantial_user_chat_log,
                "document_date": "2026-07-22T04:43:36+00:00",
            }
        ),
        target_locale="en",
        metadata=ExecutionMetadata(),
    )

    emit_mock = AsyncMock()
    atom = DraftExtractedAtom(
        draft_id="atm_1234567890abcdef",
        reasoning="Test reasoning",
        resolved_claim="Test claim",
        is_logical_deduction=False,
        source_quote="Olen toiminut tiiminvetäjänä viisi vuotta ja kehittänyt useita järjestelmiä",
        source_sequence_index=0,
    )

    with (
        patch("backend_v2.llm.client.LLMClient.from_tier") as mock_client_factory,
        patch("backend_v2.services.orchestrator.rag_preflight_service.TwoPassAtomizer") as mock_atomizer_cls,
    ):
        mock_client = AsyncMock()
        mock_client_factory.return_value = mock_client
        mock_atomizer = mock_atomizer_cls.return_value
        mock_atomizer.execute_phase_0 = AsyncMock(
            return_value=({"ontology": "valid"}, TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15))
        )
        mock_atomizer.execute_phase_1_drafts = AsyncMock(
            return_value=(
                DraftAtomList(atoms=[atom]),
                TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
            )
        )

        result = await preflight_service.execute(
            target_step=step_rule,
            step_def=step_def,
            exec_record=exec_record,
            emit_progress=emit_mock,
        )

        assert isinstance(result, GlobalAtomBlackboard)
        assert "chat_log" in result.atoms_by_input
        assert "document_date" not in result.atoms_by_input
        assert len(result.atoms_by_input["chat_log"].atoms) == 1


@pytest.mark.asyncio
async def test_rag_preflight_extracts_inputs_from_trace_and_ignores_auxiliary_keys(
    preflight_service: RAGPreflightService,
) -> None:
    """Tests that preflight extracts inputs from execution_trace and ignores _user_only/_ai_only keys."""
    step_rule = StepRule(
        id="stp_1234567890abcdef", task_blueprint="blp_1234567890abcdef", input_mappings={}, depends_on=[]
    )
    step_def = make_valid_step_def()

    sparse_chat_log = (
        "<user_payload>\npaljon kello on\n</user_payload>\n\n"
        "<ai_draft_context>\nKello on tällä hetkellä 7.43.\n</ai_draft_context>\n\n"
        "<user_payload>\nkiitos\n</user_payload>\n\n"
        "<ai_draft_context>\nOle hyvä! Autan mielelläni, jos sinulla on muuta kysyttävää.\n</ai_draft_context>"
    )

    # In raw_inputs, chat_log was unparsed (443 chars).
    # In execution_trace inputs event, chat_log is parsed (48 user chars), with helper keys.
    trace_event = TraceEvent(
        step_name="inputs",
        event_type="input",
        content={
            "inputs": {
                "product_text": "lopputuote",
                "reflection_text": "reflektiodokumentti",
                "chat_log": sparse_chat_log,
                "chat_log_user_only": "paljon kello on\n\nkiitos",
                "chat_log_ai_only": "Kello on tällä hetkellä 7.43.\n\nOle hyvä! Autan mielelläni...",
                "document_date": "2026-07-22T04:43:36+00:00",
            },
            "metadata": {"estimated_token_count": 100},
        },
    )

    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        output_profile_id="prof_1234567890abcdef",
        raw_inputs=WorkflowInputs(
            dynamic_inputs={
                "product_text": "lopputuote",
                "reflection_text": "reflektiodokumentti",
                "chat_log": "raw unparsed 443 char string that should be overridden by trace",
                "document_date": "2026-07-22T04:43:36+00:00",
            }
        ),
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[trace_event],
    )

    emit_mock = AsyncMock()

    with patch("backend_v2.services.orchestrator.rag_preflight_service.TwoPassAtomizer") as mock_atomizer_cls:
        result = await preflight_service.execute(
            target_step=step_rule,
            step_def=step_def,
            exec_record=exec_record,
            emit_progress=emit_mock,
        )

        # 10 + 19 + 48 = 77 characters (< 100 chars min threshold).
        # Auxiliary keys (chat_log_user_only, chat_log_ai_only) and metadata (document_date) are ignored.
        mock_atomizer_cls.assert_not_called()
        assert result == GlobalAtomBlackboard(atoms_by_input={}, is_data_starved=True)
        emit_mock.assert_called_with("Input data sparse/empty. Preflight extraction skipped.", 100)


def test_extract_inputs_from_record_variations() -> None:
    """Test _extract_inputs_from_record with ExecutionInputsDTO and dynamic_inputs trace contents."""
    # 1. Test with ExecutionInputsDTO via model_construct
    event_dto = TraceEvent.model_construct(
        step_name="inputs",
        event_type="input",
        content=ExecutionInputsDTO(dynamic_inputs={"file_a": "content from dto"}),
    )
    rec_dto = ExecutionRecord(
        id="exe_0000000000000001",
        workflow_id="wf_0000000000000001",
        output_profile_id="prof_0000000000000001",
        raw_inputs=WorkflowInputs(dynamic_inputs={"raw": "fallback"}),
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[event_dto],
    )
    extracted_dto = _extract_inputs_from_record(rec_dto)
    assert extracted_dto.dynamic_inputs == {"file_a": "content from dto"}

    # 2. Test with content containing dynamic_inputs mapping
    event_dict = TraceEvent(
        step_name="inputs",
        event_type="input",
        content={"dynamic_inputs": {"file_b": "content from dict"}},
    )
    rec_dict = ExecutionRecord(
        id="exe_0000000000000002",
        workflow_id="wf_0000000000000002",
        output_profile_id="prof_0000000000000002",
        raw_inputs=WorkflowInputs(dynamic_inputs={"raw": "fallback"}),
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[event_dict],
    )
    extracted_dict = _extract_inputs_from_record(rec_dict)
    assert extracted_dict.dynamic_inputs == {"file_b": "content from dict"}
