"""Unit tests for RAGPreflightService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.blackboard import DraftAtomList, DraftExtractedAtom
from backend_v2.models.v2_core import ExecutionRecord, I18nText, Step, StepRule, WorkflowInputs
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService


@pytest.fixture
def mock_workflow_repo() -> MagicMock:
    """Mock workflow repository."""
    return AsyncMock()


@pytest.fixture
def mock_system_repo() -> MagicMock:
    """Mock system repository."""
    return AsyncMock()


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


def make_valid_step_def(model_strategy: str | None = "fast") -> Step:
    """Helper to create a valid Step object for testing."""
    return Step.model_validate(
        {
            "id": "stp_1234567890abcdef",
            "slug": "test_step",
            "name": {"default_locale": "en", "translations": {"en": "Test Step"}},
            "description": {"default_locale": "en", "translations": {"en": "Test Description"}},
            "model_strategy": model_strategy,
            "criteria_block_ids": ["blk_1234567890abcdef"],
            "extraction_protocol_block_id": "blk_1234567890abcdef",
            "type": "llm",
        }
    )


@pytest.mark.asyncio
async def test_rag_preflight_missing_task_blueprint_crashes(preflight_service: RAGPreflightService) -> None:
    """Tests that missing task_blueprint raises CONFIGURATION_ERROR AppException."""
    step_rule = StepRule.model_construct(
        id="stp_1234567890abcdef", task_blueprint=None, input_mappings={}, depends_on=[]
    )
    step_def = make_valid_step_def()
    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "A" * 100}),
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
async def test_rag_preflight_missing_model_strategy_crashes(preflight_service: RAGPreflightService) -> None:
    """Tests that missing model_strategy raises CONFIGURATION_ERROR AppException."""
    step_rule = StepRule(
        id="stp_1234567890abcdef", task_blueprint="blp_1234567890abcdef", input_mappings={}, depends_on=[]
    )
    step_def = Step.model_construct(
        id="stp_1234567890abcdef",
        slug="test_step",
        name=I18nText(default_locale="en", translations={"en": "Test Step"}),
        description=I18nText(default_locale="en", translations={"en": "Test Description"}),
        model_strategy=None,
        type="llm",
    )
    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "A" * 100}),
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
        raw_inputs=WorkflowInputs(dynamic_inputs={"short_doc": "Only 20 chars here.", "non_str": 123}),
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
        assert result == {"atoms_by_input": {}}
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
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc_1": text_content, "skipped_key": None}),
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
        patch("backend_v2.llm.client.LLMClient.from_strategy") as mock_client_factory,
        patch("backend_v2.services.orchestrator.rag_preflight_service.TwoPassAtomizer") as mock_atomizer_cls,
    ):
        mock_client = AsyncMock()
        mock_client_factory.return_value = mock_client
        mock_atomizer = mock_atomizer_cls.return_value

        async def fake_phase_0(client, text, progress_callback=None):
            if progress_callback:
                await progress_callback(50, 100)
            return {"ontology": "valid"}

        async def fake_phase_1(client, text, ontology, progress_callback=None):
            if progress_callback:
                await progress_callback(50, 100)
            return DraftAtomList(atoms=[atom])

        mock_atomizer.execute_phase_0 = AsyncMock(side_effect=fake_phase_0)
        mock_atomizer.execute_phase_1_drafts = AsyncMock(side_effect=fake_phase_1)

        result = await preflight_service.execute(
            target_step=step_rule,
            step_def=step_def,
            exec_record=exec_record,
            emit_progress=emit_mock,
        )

        assert "doc_1" in result["atoms_by_input"]
        assert len(result["atoms_by_input"]["doc_1"]["atoms"]) == 1
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
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc_1": text_content}),
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
        patch("backend_v2.llm.client.LLMClient.from_strategy") as mock_client_factory,
        patch("backend_v2.services.orchestrator.rag_preflight_service.TwoPassAtomizer") as mock_atomizer_cls,
        patch("backend_v2.services.orchestrator.rag_preflight_service.get_settings") as mock_settings,
    ):
        mock_client = AsyncMock()
        mock_client_factory.return_value = mock_client
        mock_atomizer = mock_atomizer_cls.return_value
        mock_atomizer.execute_phase_0 = AsyncMock(return_value={})
        mock_atomizer.execute_phase_1_drafts = AsyncMock(return_value=DraftAtomList(atoms=[atom, atom, atom]))

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
