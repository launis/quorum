"""Regression and Root Cause Analysis (RCA) tests for Studio settings persistence.

Verifies that saving workflows, steps, output profiles, prompt blocks, and system configurations
updates records in-place, preserves Opaque Stripe IDs, prevents un-prefixed orphan records, and
guarantees that pre-flight schema validation passes upon software restart.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import TypeAdapter
from tinydb import TinyDB

from backend_v2.database.repositories.components.output_profile import OutputProfileRepositoryImpl
from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.database.tinydb_driver import TinyDBDriver
from backend_v2.database.wrapper import TinyDBClient
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock, PromptBlockAdapter
from backend_v2.models.dtos.system import AnySystemConfigAdapter
from backend_v2.models.enums import (
    BlockDataType,
    HistoricalContextMode,
    PromptBlockCategory,
    ScoringStrategy,
    StepType,
    SystemConfigID,
    TargetBlockType,
)
from backend_v2.models.v2_core import (
    LexiconConfigPayload,
    MatrixSynthesisGroup,
    OutputProfile,
    Step,
    SystemConfigPerformativeLexicons,
    Workflow,
)
from backend_v2.services.studio.lexicon_service import StudioLexiconService
from backend_v2.services.studio.output_profile_service import StudioOutputProfileService
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService
from backend_v2.services.studio.workflow_service import StudioWorkflowService

pytestmark = pytest.mark.asyncio


def _create_sample_prompt_block(block_id: str = "blk_1234567890abcdef") -> PersonaPromptBlock:
    """Helper to create a valid minimal PersonaPromptBlock domain model."""
    return PersonaPromptBlock(
        id=block_id,
        slug="test_persona",
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "Test Persona", "fi": "Testipersona"}),
        description=I18nText(translations={"en": "Persona Description", "fi": "Persoonan kuvaus"}),
        organization_id=None,
        role_enforcement="Strict analytical auditor.",
        tone_directives=["Objective", "Rigorous"],
    )


def _create_sample_workflow(workflow_id: str = "wf_1234567890abcdef") -> Workflow:
    """Helper to create a valid minimal Workflow domain model."""
    return Workflow(
        id=workflow_id,
        slug="test_workflow",
        name=I18nText(translations={"en": "Original Workflow", "fi": "Alkuperäinen työnkulku"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        status="active",
        version=1,
        default_profile_id="prf_1234567890abcdef",
        default_strictness_level=50,
        default_scoring_strategy=ScoringStrategy.AVERAGE,
        allowed_exports=["pdf", "docx"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )


def _create_sample_step(step_id: str = "stp_1234567890abcdef") -> Step:
    """Helper to create a valid minimal Step domain model."""
    return Step(
        id=step_id,
        slug="test_step",
        name=I18nText(translations={"en": "Test Step", "fi": "Testiaskel"}),
        description=I18nText(translations={"en": "Step Description", "fi": "Askeleen kuvaus"}),
        type=StepType.LOGIC,
        hook="sample_hook",
        model_strategy="standard_strategy",
    )


def _create_sample_lexicons(
    config_id: str = SystemConfigID.PERFORMATIVE_LEXICONS.value,
) -> SystemConfigPerformativeLexicons:
    """Helper to create a valid minimal SystemConfigPerformativeLexicons domain model."""
    return SystemConfigPerformativeLexicons(
        id=config_id,
        type="performative_lexicons",
        lexicon_configs={
            "en": LexiconConfigPayload(
                language_code="en",
                language_name="English",
                fuzz_threshold=85.0,
                words=["in today's digital landscape", "test buzzword"],
            )
        },
    )


def _create_sample_output_profile(
    profile_id: str = "prf_1234567890abcdef",
    workflow_id: str = "wf_1234567890abcdef",
) -> OutputProfile:
    """Helper to create a valid minimal OutputProfile domain model."""
    return OutputProfile(
        id=profile_id,
        slug="test_profile",
        name=I18nText(translations={"en": "Test Profile", "fi": "Testiprofiili"}),
        description=I18nText(translations={"en": "Profile Desc", "fi": "Profiilin kuvaus"}),
        workflow_id=workflow_id,
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )


async def test_save_workflow_updates_inplace_and_preserves_preflight(tmp_path: Path) -> None:
    """Tests that saving an existing workflow updates in-place without creating orphan records.

    RED TEST (RCA): Fails because save_workflow calls create_workflow, stripping the ID,
    generating an un-prefixed UUID with is_latest: True, and leaving the original record unchanged.
    """
    db_path = str(tmp_path / "test_db.json")
    db_client = TinyDBClient(db_path)
    driver = TinyDBDriver(db_client)

    workflow_repo = WorkflowRepositoryImpl(driver=driver)
    output_profile_repo = OutputProfileRepositoryImpl(driver=driver)
    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    target_id = "wf_1234567890abcdef"
    initial_wf = _create_sample_workflow(target_id)

    # Seed initial workflow and output profile into database
    await driver.upsert("workflows", initial_wf.model_dump(mode="json"), target_id)
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        workflow_id=target_id,
        slug="default",
        name=I18nText(translations={"en": "Default Profile", "fi": "Oletusprofiili"}),
        organization_id=None,
        description=I18nText(translations={"en": "Default description", "fi": "Oletuskuvaus"}),
        target_block_order=[],
        matrix_synthesis_groups=[],
    )
    await driver.upsert("output_profiles", profile.model_dump(mode="json"), "prf_1234567890abcdef")

    # Update workflow with new settings
    updated_data = initial_wf.model_copy(
        update={
            "name": I18nText(translations={"en": "Updated Workflow", "fi": "Päivitetty työnkulku"}),
            "default_strictness_level": 85,
            "enable_semantic_smoothing": True,
        }
    )

    res = await workflow_service.save_workflow(root_token, target_id, updated_data)

    # 1. Assert returned DTO has the updated values
    assert res.id == target_id
    assert res.default_strictness_level == 85, f"Expected 85, got {res.default_strictness_level}"
    assert res.enable_semantic_smoothing is True

    # 2. Assert persisted record in repo has the updated values
    persisted = await workflow_repo.get_workflow_by_id(target_id)
    assert persisted is not None
    assert persisted.default_strictness_level == 85
    assert persisted.enable_semantic_smoothing is True

    # 3. Assert no orphan records or un-prefixed UUIDs were created in TinyDB
    with TinyDB(db_path, encoding="utf-8") as raw_db:
        wf_docs = raw_db.table("workflows").all()
        assert len(wf_docs) == 1, f"Expected exactly 1 workflow in DB, but found {len(wf_docs)} (orphan created!)"

        # 4. Assert all documents in workflows pass strict startup pre-flight validation
        workflow_adapter = TypeAdapter(Workflow)
        for doc in wf_docs:
            validated = workflow_adapter.validate_python(doc)
            assert validated.id == target_id


async def test_save_step_updates_inplace_and_preserves_preflight(tmp_path: Path) -> None:
    """Tests that saving an existing step updates in-place without creating orphan records.

    RED TEST (RCA): Fails because save_step strips id, calls create_step, and creates an orphan record.
    """
    db_path = str(tmp_path / "test_db.json")
    db_client = TinyDBClient(db_path)
    driver = TinyDBDriver(db_client)

    workflow_repo = WorkflowRepositoryImpl(driver=driver)
    output_profile_repo = OutputProfileRepositoryImpl(driver=driver)
    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    target_id = "stp_1234567890abcdef"
    initial_step = _create_sample_step(target_id)

    # Seed initial step
    await driver.upsert("steps", initial_step.model_dump(mode="json"), target_id)

    # Update step with new model strategy
    updated_data = initial_step.model_copy(
        update={
            "model_strategy": "pro_fast_2026",
            "name": I18nText(translations={"en": "Updated Step", "fi": "Päivitetty askel"}),
        }
    )

    res = await workflow_service.save_step(root_token, target_id, updated_data)

    # 1. Assert returned step has updated value
    assert res.id == target_id
    assert res.model_strategy == "pro_fast_2026"

    # 2. Assert persisted record in repo has the updated value
    persisted = await workflow_repo.get_step_by_id(target_id)
    assert persisted is not None
    assert persisted.model_strategy == "pro_fast_2026"

    # 3. Assert no orphan records in TinyDB
    with TinyDB(db_path, encoding="utf-8") as raw_db:
        step_docs = raw_db.table("steps").all()
        assert len(step_docs) == 1, f"Expected exactly 1 step in DB, but found {len(step_docs)}"
        for doc in step_docs:
            validated = Step.model_validate(doc)
            assert validated.id == target_id


async def test_save_performative_lexicons_updates_inplace_and_preserves_preflight(tmp_path: Path) -> None:
    """Tests that saving performative lexicons updates in-place without corrupting system_config.

    RED TEST (RCA): Fails because save_performative_lexicons_config wraps data into SystemConfigCreateDTO,
    saving under cfg_performative_lexicons with a nested content dictionary that breaks AnySystemConfigAdapter.
    """
    db_path = str(tmp_path / "test_db.json")
    db_client = TinyDBClient(db_path)
    driver = TinyDBDriver(db_client)

    system_repo = SystemRepositoryImpl(driver=driver)
    lexicon_service = StudioLexiconService(system_repo=system_repo)

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    config_id = SystemConfigID.PERFORMATIVE_LEXICONS.value
    initial_lex = _create_sample_lexicons(config_id)

    # Seed initial lexicons
    await driver.upsert("system_config", initial_lex.model_dump(mode="json"), config_id)

    # Update lexicons
    updated_data = initial_lex.model_copy(
        update={
            "lexicon_configs": {
                "en": LexiconConfigPayload(
                    language_code="en",
                    language_name="English",
                    fuzz_threshold=85.0,
                    words=["in today's digital landscape", "synergy leverage", "paradigm shift"],
                )
            }
        }
    )

    res = await lexicon_service.save_performative_lexicons_config(root_token, updated_data)

    # 1. Assert returned config has 3 words
    assert len(res.lexicon_configs["en"].words) == 3

    # 2. Assert persisted record in repo has 3 words
    persisted = await system_repo.get_system_config(config_id)
    assert isinstance(persisted, SystemConfigPerformativeLexicons)
    assert len(persisted.lexicon_configs["en"].words) == 3

    # 3. Assert system_config table does not have duplicate/corrupted documents
    with TinyDB(db_path, encoding="utf-8") as raw_db:
        configs = raw_db.table("system_config").all()
        assert len(configs) == 1, f"Expected 1 system_config, got {len(configs)}"
        for doc in configs:
            # Must pass pre-flight validation
            validated = AnySystemConfigAdapter.validate_python(doc)
            assert isinstance(validated, SystemConfigPerformativeLexicons)
            assert validated.id == config_id


async def test_save_output_profile_updates_inplace_and_preserves_preflight(tmp_path: Path) -> None:
    """Tests that saving an output profile updates in-place without creating orphan records."""
    db_path = str(tmp_path / "test_db.json")
    db_client = TinyDBClient(db_path)
    driver = TinyDBDriver(db_client)

    workflow_repo = WorkflowRepositoryImpl(driver=driver)
    output_profile_repo = OutputProfileRepositoryImpl(driver=driver)
    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
    )
    output_profile_service = StudioOutputProfileService(
        output_profile_repo=output_profile_repo,
        workflow_service=workflow_service,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    wf_id = "wf_1234567890abcdef"
    prof_id = "prf_1234567890abcdef"

    initial_wf = _create_sample_workflow(wf_id)
    await driver.upsert("workflows", initial_wf.model_dump(mode="json"), wf_id)

    initial_prof = _create_sample_output_profile(prof_id, wf_id)
    await driver.upsert("output_profiles", initial_prof.model_dump(mode="json"), prof_id)

    updated_prof = initial_prof.model_copy(
        update={
            "name": I18nText(translations={"en": "Updated Profile", "fi": "Päivitetty profiili"}),
        }
    )

    res = await output_profile_service.save_output_profile(root_token, prof_id, updated_prof)

    # 1. Assert returned profile has updated value and identical ID
    assert res.id == prof_id
    assert res.name.translations["en"] == "Updated Profile"

    # 2. Assert persisted record in repo has updated value
    persisted = await output_profile_repo.get_output_profile_by_id(prof_id)
    assert persisted is not None
    assert persisted.id == prof_id
    assert persisted.name.translations["en"] == "Updated Profile"

    # 3. Assert output_profiles table does not have orphan/duplicate records
    with TinyDB(db_path, encoding="utf-8") as raw_db:
        prof_docs = raw_db.table("output_profiles").all()
        assert len(prof_docs) == 1, f"Expected 1 profile in DB, but found {len(prof_docs)}"
        for doc in prof_docs:
            validated = OutputProfile.model_validate(doc)
            assert validated.id == prof_id


async def test_create_output_profile_draft_binds_to_valid_workflow(tmp_path: Path) -> None:
    """Tests that output profile draft binds to an active workflow and not wildcard '*'."""
    db_path = str(tmp_path / "test_db.json")
    db_client = TinyDBClient(db_path)
    driver = TinyDBDriver(db_client)

    workflow_repo = WorkflowRepositoryImpl(driver=driver)
    output_profile_repo = OutputProfileRepositoryImpl(driver=driver)
    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
    )
    output_profile_service = StudioOutputProfileService(
        output_profile_repo=output_profile_repo,
        workflow_service=workflow_service,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    wf_id = "wf_1234567890abcdef"
    initial_wf = _create_sample_workflow(wf_id)
    await driver.upsert("workflows", initial_wf.model_dump(mode="json"), wf_id)

    draft = await output_profile_service.create_output_profile_draft(root_token)
    assert draft.id.startswith("prf_")
    assert draft.workflow_id == wf_id
    assert draft.workflow_id != "*"


async def test_save_output_profile_invalid_target_component_fails_fast(tmp_path: Path) -> None:
    """Tests that saving an output profile referencing an invalid target component raises 400 VALIDATION_FAILED."""
    db_path = str(tmp_path / "test_db.json")
    db_client = TinyDBClient(db_path)
    driver = TinyDBDriver(db_client)

    workflow_repo = WorkflowRepositoryImpl(driver=driver)
    output_profile_repo = OutputProfileRepositoryImpl(driver=driver)
    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
    )
    output_profile_service = StudioOutputProfileService(
        output_profile_repo=output_profile_repo,
        workflow_service=workflow_service,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    wf_id = "wf_1234567890abcdef"
    prof_id = "prf_1234567890abcdef"

    initial_wf = _create_sample_workflow(wf_id)
    await driver.upsert("workflows", initial_wf.model_dump(mode="json"), wf_id)

    invalid_prof = _create_sample_output_profile(prof_id, wf_id).model_copy(
        update={
            "matrix_synthesis_groups": [
                MatrixSynthesisGroup(
                    id="grp_1234567890abcdef",
                    title=I18nText(translations={"en": "Invalid Group"}),
                    target_blocks=["unsupported_target_block"],
                )
            ]
        }
    )

    with pytest.raises(AppException) as exc_info:
        await output_profile_service.save_output_profile(root_token, prof_id, invalid_prof)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] in (ErrorCodes.VALIDATION_FAILED, ErrorCodes.VALIDATION_FAILED.value)


async def test_save_output_profile_nonexistent_workflow_raises_resource_not_found(tmp_path: Path) -> None:
    """Tests that saving an output profile referencing a missing workflow raises 404 ResourceNotFoundError."""
    db_path = str(tmp_path / "test_db.json")
    db_client = TinyDBClient(db_path)
    driver = TinyDBDriver(db_client)

    workflow_repo = WorkflowRepositoryImpl(driver=driver)
    output_profile_repo = OutputProfileRepositoryImpl(driver=driver)
    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
    )
    output_profile_service = StudioOutputProfileService(
        output_profile_repo=output_profile_repo,
        workflow_service=workflow_service,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    prof_id = "prf_1234567890abcdef"
    missing_wf_id = "wf_0000000000000000"

    prof = _create_sample_output_profile(prof_id, missing_wf_id)

    with pytest.raises(ResourceNotFoundError):
        await output_profile_service.save_output_profile(root_token, prof_id, prof)


async def test_save_prompt_block_updates_inplace_and_preserves_preflight(tmp_path: Path) -> None:
    """Tests that saving a prompt block updates in-place without creating orphan records.

    Verifies 100% parity across all 5 Studio entities by checking in-place upsert
    and strict pre-flight schema validation against PromptBlockAdapter.
    """
    db_path = str(tmp_path / "test_db.json")
    db_client = TinyDBClient(db_path)
    driver = TinyDBDriver(db_client)

    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)
    system_repo = SystemRepositoryImpl(driver=driver)

    prompt_block_service = StudioPromptBlockService(
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    target_id = "blk_1234567890abcdef"
    initial_block = _create_sample_prompt_block(target_id)

    # Seed initial prompt block into database
    await driver.upsert("prompt_blocks", initial_block.model_dump(mode="json"), target_id)

    # Update prompt block with new values
    updated_block = initial_block.model_copy(
        update={
            "label": I18nText(translations={"en": "Updated Persona", "fi": "Päivitetty persona"}),
            "role_enforcement": "Empathetic executive coach.",
            "tone_directives": ["Constructive", "Supportive"],
        }
    )

    res = await prompt_block_service.save_prompt_block(root_token, target_id, updated_block)

    # 1. Assert returned DTO has the updated values and identical ID
    assert res.id == target_id
    assert isinstance(res, PersonaPromptBlock)
    assert res.label.translations["en"] == "Updated Persona"
    assert res.role_enforcement == "Empathetic executive coach."
    assert res.tone_directives == ["Constructive", "Supportive"]

    # 2. Assert persisted record in repo has the updated values
    persisted = await prompt_block_repo.get_prompt_block_by_id(target_id)
    assert persisted is not None
    assert persisted.id == target_id
    assert isinstance(persisted, PersonaPromptBlock)
    assert persisted.label.translations["en"] == "Updated Persona"
    assert persisted.role_enforcement == "Empathetic executive coach."
    assert persisted.tone_directives == ["Constructive", "Supportive"]

    # 3. Assert prompt_blocks table in TinyDB does not have duplicate/orphan records
    with TinyDB(db_path, encoding="utf-8") as raw_db:
        block_docs = raw_db.table("prompt_blocks").all()
        assert len(block_docs) == 1, f"Expected exactly 1 prompt block in DB, but found {len(block_docs)}"

        # 4. Assert all documents in prompt_blocks pass startup pre-flight validation
        for doc in block_docs:
            validated = PromptBlockAdapter.validate_python(doc)
            assert validated.id == target_id
            assert isinstance(validated, PersonaPromptBlock)
            assert validated.label.translations["en"] == "Updated Persona"
            assert validated.role_enforcement == "Empathetic executive coach."
