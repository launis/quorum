"""Regression and Root Cause Analysis (RCA) tests for Studio settings persistence.

Verifies that saving workflows, steps, output profiles, prompt blocks, and system configurations
updates records in-place, preserves Opaque Stripe IDs, prevents un-prefixed orphan records, and
guarantees that pre-flight schema validation passes upon software restart.
"""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter

from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.database.repositories.components.output_profile import OutputProfileRepositoryImpl
from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock, PromptBlockAdapter
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import (
    BlockDataType,
    HistoricalContextMode,
    PromptBlockCategory,
    StepType,
    TargetBlockType,
)
from backend_v2.services.studio.output_profile_service import StudioOutputProfileService
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService
from backend_v2.services.studio.workflow_service import StudioWorkflowService

pytestmark = pytest.mark.asyncio


def _create_sample_prompt_block(block_id: str = "blk_0195f3a0000070018234567890abcdef") -> PersonaPromptBlock:
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


def _create_sample_workflow(
    workflow_id: str = "wf_0195f3a0000070018234567890abcdef",
    model_registry_id: str = "sys_0195f3a00000700e826807f3bfa3454d",
) -> Workflow:
    """Helper to create a valid minimal Workflow domain model."""
    return Workflow(
        id=workflow_id,
        slug="test_workflow",
        name=I18nText(translations={"en": "Original Workflow", "fi": "Alkuperäinen työnkulku"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        status="active",
        version=1,
        default_profile_id="prf_0195f3a0000070018234567890abcdef",
        default_strictness_level=50,
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
        model_registry_id=model_registry_id,
    )


def _create_sample_step(step_id: str = "stp_0195f3a0000070018234567890abcdef") -> Step:
    """Helper to create a valid minimal Step domain model."""
    return Step(
        id=step_id,
        slug="test_step",
        name=I18nText(translations={"en": "Test Step", "fi": "Testiaskel"}),
        description=I18nText(translations={"en": "Step Description", "fi": "Askeleen kuvaus"}),
        type=StepType.LOGIC,
        hook="sample_hook",
    )


def _create_sample_output_profile(
    profile_id: str = "prf_0195f3a0000070018234567890abcdef",
    workflow_id: str = "wf_0195f3a0000070018234567890abcdef",
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


async def test_save_workflow_updates_inplace_and_preserves_preflight() -> None:
    """Tests that saving an existing workflow updates in-place without creating orphan records."""
    driver = PostgresStorageDriver(auto_initialize_pool=False)

    workflow_repo = WorkflowRepositoryImpl(driver=driver)
    output_profile_repo = OutputProfileRepositoryImpl(driver=driver)
    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)
    system_repo = SystemRepositoryImpl(driver=driver)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    target_id = "wf_0195f3a0000070018234567890abcdef"
    initial_wf = _create_sample_workflow(target_id)

    await driver.upsert("workflows", initial_wf.model_dump(mode="json"), target_id)
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        workflow_id=target_id,
        slug="default",
        name=I18nText(translations={"en": "Default Profile", "fi": "Oletusprofiili"}),
        organization_id=None,
        description=I18nText(translations={"en": "Default description", "fi": "Oletuskuvaus"}),
        target_block_order=[],
        matrix_synthesis_groups=[],
    )
    await driver.upsert("output_profiles", profile.model_dump(mode="json"), "prf_0195f3a0000070018234567890abcdef")

    updated_data = initial_wf.model_copy(
        update={
            "name": I18nText(translations={"en": "Updated Workflow", "fi": "Päivitetty työnkulku"}),
            "default_strictness_level": 85,
            "enable_semantic_smoothing": True,
        }
    )

    res = await workflow_service.save_workflow(root_token, target_id, updated_data)

    assert res.id == target_id
    assert res.default_strictness_level == 85, f"Expected 85, got {res.default_strictness_level}"
    assert res.enable_semantic_smoothing is True

    persisted = await workflow_repo.get_workflow_by_id(target_id)
    assert persisted is not None
    assert persisted.default_strictness_level == 85
    assert persisted.enable_semantic_smoothing is True

    wf_docs = await driver.get_all("workflows")
    assert len(wf_docs) == 1, f"Expected exactly 1 workflow in DB, but found {len(wf_docs)} (orphan created!)"

    workflow_adapter = TypeAdapter(Workflow)
    for doc in wf_docs:
        validated = workflow_adapter.validate_python(doc)
        assert validated.id == target_id


async def test_save_step_updates_inplace_and_preserves_preflight() -> None:
    """Tests that saving an existing step updates in-place without creating orphan records."""
    driver = PostgresStorageDriver(auto_initialize_pool=False)

    workflow_repo = WorkflowRepositoryImpl(driver=driver)
    output_profile_repo = OutputProfileRepositoryImpl(driver=driver)
    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)
    system_repo = SystemRepositoryImpl(driver=driver)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    target_id = "stp_0195f3a0000070018234567890abcdef"
    initial_step = _create_sample_step(target_id)

    await driver.upsert("steps", initial_step.model_dump(mode="json"), target_id)

    updated_data = initial_step.model_copy(
        update={
            "hook": "updated_hook",
            "name": I18nText(translations={"en": "Updated Step", "fi": "Päivitetty askel"}),
        }
    )

    res = await workflow_service.save_step(root_token, target_id, updated_data)

    assert res.id == target_id
    assert res.hook == "updated_hook"
    assert res.name.translations["en"] == "Updated Step"

    persisted = await workflow_repo.get_step_by_id(target_id)
    assert persisted is not None
    assert persisted.hook == "updated_hook"
    assert persisted.name.translations["en"] == "Updated Step"

    step_docs = await driver.get_all("steps")
    assert len(step_docs) == 1, f"Expected exactly 1 step in DB, but found {len(step_docs)}"
    for doc in step_docs:
        validated = Step.model_validate(doc)
        assert validated.id == target_id


async def test_save_output_profile_updates_inplace_and_preserves_preflight() -> None:
    """Tests that saving an output profile updates in-place without creating orphan records."""
    driver = PostgresStorageDriver(auto_initialize_pool=False)

    workflow_repo = WorkflowRepositoryImpl(driver=driver)
    output_profile_repo = OutputProfileRepositoryImpl(driver=driver)
    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)
    system_repo = SystemRepositoryImpl(driver=driver)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
    )
    output_profile_service = StudioOutputProfileService(
        output_profile_repo=output_profile_repo,
        workflow_service=workflow_service,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    wf_id = "wf_0195f3a0000070018234567890abcdef"
    prof_id = "prf_0195f3a0000070018234567890abcdef"

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

    assert res.id == prof_id
    assert res.name.translations["en"] == "Updated Profile"

    persisted = await output_profile_repo.get_output_profile_by_id(prof_id)
    assert persisted is not None
    assert persisted.id == prof_id
    assert persisted.name.translations["en"] == "Updated Profile"

    prof_docs = await driver.get_all("output_profiles")
    assert len(prof_docs) == 1, f"Expected 1 profile in DB, but found {len(prof_docs)}"
    for doc in prof_docs:
        validated = OutputProfile.model_validate(doc)
        assert validated.id == prof_id


async def test_create_output_profile_draft_binds_to_valid_workflow() -> None:
    """Tests that output profile draft binds to an active workflow and not wildcard '*'."""
    driver = PostgresStorageDriver(auto_initialize_pool=False)

    workflow_repo = WorkflowRepositoryImpl(driver=driver)
    output_profile_repo = OutputProfileRepositoryImpl(driver=driver)
    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)
    system_repo = SystemRepositoryImpl(driver=driver)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
    )
    output_profile_service = StudioOutputProfileService(
        output_profile_repo=output_profile_repo,
        workflow_service=workflow_service,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    wf_id = "wf_0195f3a0000070018234567890abcdef"
    initial_wf = _create_sample_workflow(wf_id)
    await driver.upsert("workflows", initial_wf.model_dump(mode="json"), wf_id)

    draft = await output_profile_service.create_output_profile_draft(root_token)
    assert draft.id.startswith("prf_")
    assert draft.workflow_id == wf_id
    assert draft.workflow_id != "*"


async def test_save_output_profile_invalid_target_component_fails_fast() -> None:
    """Tests that saving an output profile referencing an invalid target component raises 400 VALIDATION_FAILED."""
    driver = PostgresStorageDriver(auto_initialize_pool=False)

    workflow_repo = WorkflowRepositoryImpl(driver=driver)
    output_profile_repo = OutputProfileRepositoryImpl(driver=driver)
    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)
    system_repo = SystemRepositoryImpl(driver=driver)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
    )
    output_profile_service = StudioOutputProfileService(
        output_profile_repo=output_profile_repo,
        workflow_service=workflow_service,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    wf_id = "wf_0195f3a0000070018234567890abcdef"
    prof_id = "prf_0195f3a0000070018234567890abcdef"

    initial_wf = _create_sample_workflow(wf_id)
    await driver.upsert("workflows", initial_wf.model_dump(mode="json"), wf_id)

    invalid_prof = _create_sample_output_profile(prof_id, wf_id).model_copy(
        update={
            "matrix_synthesis_groups": [
                MatrixSynthesisGroup(
                    id="grp_0195f3a0000070018234567890abcdef",
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


async def test_save_output_profile_nonexistent_workflow_raises_resource_not_found() -> None:
    """Tests that saving an output profile referencing a missing workflow raises 404 ResourceNotFoundError."""
    driver = PostgresStorageDriver(auto_initialize_pool=False)

    workflow_repo = WorkflowRepositoryImpl(driver=driver)
    output_profile_repo = OutputProfileRepositoryImpl(driver=driver)
    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)
    system_repo = SystemRepositoryImpl(driver=driver)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
    )
    output_profile_service = StudioOutputProfileService(
        output_profile_repo=output_profile_repo,
        workflow_service=workflow_service,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    prof_id = "prf_0195f3a0000070018234567890abcdef"
    missing_wf_id = "wf_0195f3a0000070008000000000000000"

    prof = _create_sample_output_profile(prof_id, missing_wf_id)

    with pytest.raises(ResourceNotFoundError):
        await output_profile_service.save_output_profile(root_token, prof_id, prof)


async def test_save_prompt_block_updates_inplace_and_preserves_preflight() -> None:
    """Tests that saving a prompt block updates in-place without creating orphan records."""
    driver = PostgresStorageDriver(auto_initialize_pool=False)

    prompt_block_repo = PromptBlockRepositoryImpl(driver=driver)
    system_repo = SystemRepositoryImpl(driver=driver)

    prompt_block_service = StudioPromptBlockService(
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
    )

    root_token = TokenData(id="usr_root", role=UserRole.ROOT)
    target_id = "blk_0195f3a0000070018234567890abcdef"
    initial_block = _create_sample_prompt_block(target_id)

    await driver.upsert("prompt_blocks", initial_block.model_dump(mode="json"), target_id)

    updated_block = initial_block.model_copy(
        update={
            "label": I18nText(translations={"en": "Updated Persona", "fi": "Päivitetty persona"}),
            "role_enforcement": "Empathetic executive coach.",
            "tone_directives": ["Constructive", "Supportive"],
        }
    )

    res = await prompt_block_service.save_prompt_block(root_token, target_id, updated_block)

    assert res.id == target_id
    assert isinstance(res, PersonaPromptBlock)
    assert res.label.translations["en"] == "Updated Persona"
    assert res.role_enforcement == "Empathetic executive coach."
    assert res.tone_directives == ["Constructive", "Supportive"]

    persisted = await prompt_block_repo.get_prompt_block_by_id(target_id)
    assert persisted is not None
    assert persisted.id == target_id
    assert isinstance(persisted, PersonaPromptBlock)
    assert persisted.label.translations["en"] == "Updated Persona"
    assert persisted.role_enforcement == "Empathetic executive coach."
    assert persisted.tone_directives == ["Constructive", "Supportive"]

    block_docs = await driver.get_all("prompt_blocks")
    assert len(block_docs) == 1, f"Expected exactly 1 prompt block in DB, but found {len(block_docs)}"

    for doc in block_docs:
        validated = PromptBlockAdapter.validate_python(doc)
        assert validated.id == target_id
        assert isinstance(validated, PersonaPromptBlock)
        assert validated.label.translations["en"] == "Updated Persona"
        assert validated.role_enforcement == "Empathetic executive coach."
