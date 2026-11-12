"""Regression and Root Cause Analysis (RCA) tests for Studio settings persistence.

Verifies that saving workflows, steps, output profiles, prompt blocks, and model registries
over InMemoryUnitOfWork updates records in-place, preserves canonical Opaque Stripe IDs,
prevents orphan records, and satisfies root Pydantic V2 validation.
"""

from __future__ import annotations

import re
from collections.abc import Callable

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import TypeAdapter

from backend_v2.database.interfaces import QuorumUnitOfWork
from backend_v2.database.repositories.components.output_profile import OutputProfileRepositoryImpl
from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.exceptions import (
    AppException,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import (
    OPAQUE_STRIPE_ID_REGEX,
    I18nText,
    generate_opaque_id,
    parse_prefixed_uuid7,
)
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock, PromptBlockAdapter
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.domain.system_config import (
    ModelProfile,
    ProviderExtraParamsDTO,
    SystemConfigModelRegistry,
)
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    EntityPrefix,
    HistoricalContextMode,
    LLMProvider,
    PromptBlockCategory,
    StepType,
    TargetBlockType,
)
from backend_v2.services.studio.output_profile_service import StudioOutputProfileService
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService
from backend_v2.services.studio.system_config_service import StudioSystemConfigService
from backend_v2.services.studio.workflow_service import StudioWorkflowService
from backend_v2.tests.factories.model_factories import OutputProfileFactory, WorkflowFactory
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork

pytestmark = pytest.mark.asyncio


class _PersonaPromptBlockFactory(ModelFactory[PersonaPromptBlock]):
    """Polyfactory model factory for PersonaPromptBlock domain models."""

    __model__ = PersonaPromptBlock

    category_id: PromptBlockCategory = PromptBlockCategory.EXECUTION_PERSONA
    type: BlockDataType = BlockDataType.INSTRUCTION
    organization_id: str | None = None
    role_enforcement: str = "Strict analytical auditor."

    @classmethod
    def id(cls) -> str:
        """Generate a canonical prompt block Opaque Stripe ID.

        Returns:
            Canonical blk_<hex32> identifier.
        """
        return generate_opaque_id(EntityPrefix.PROMPT_BLOCK)

    @classmethod
    def slug(cls) -> str:
        """Generate a deterministic test slug.

        Returns:
            Prompt block slug string.
        """
        return "test_persona"

    @classmethod
    def label(cls) -> I18nText:
        """Generate localized persona labels.

        Returns:
            I18nText instance with English and Finnish labels.
        """
        return I18nText(translations={"en": "Test Persona", "fi": "Testipersoona"})

    @classmethod
    def description(cls) -> I18nText:
        """Generate localized persona descriptions.

        Returns:
            I18nText instance with English and Finnish descriptions.
        """
        return I18nText(translations={"en": "Persona Description", "fi": "Persoonan kuvaus"})

    @classmethod
    def tone_directives(cls) -> list[str]:
        """Generate default tone directives.

        Returns:
            List of tone directive strings.
        """
        return ["Objective", "Rigorous"]

    @classmethod
    def output_extensions(cls) -> list[str]:
        """Generate empty output extensions list.

        Returns:
            Empty list of extension identifiers.
        """
        return []


class _StepFactory(ModelFactory[Step]):
    """Polyfactory model factory for Step domain models."""

    __model__ = Step

    type: StepType = StepType.LOGIC
    hook: str | None = "sample_hook"
    organization_id: str | None = None

    @classmethod
    def id(cls) -> str:
        """Generate a canonical step Opaque Stripe ID.

        Returns:
            Canonical stp_<hex32> identifier.
        """
        return generate_opaque_id(EntityPrefix.STEP)

    @classmethod
    def slug(cls) -> str:
        """Generate a deterministic step slug.

        Returns:
            Step slug string.
        """
        return "test_step"

    @classmethod
    def name(cls) -> I18nText:
        """Generate localized step names.

        Returns:
            I18nText instance with English and Finnish step names.
        """
        return I18nText(translations={"en": "Test Step", "fi": "Testiaskel"})

    @classmethod
    def description(cls) -> I18nText:
        """Generate localized step descriptions.

        Returns:
            I18nText instance with English and Finnish descriptions.
        """
        return I18nText(translations={"en": "Step Description", "fi": "Askeleen kuvaus"})


class _ModelRegistryFactory(ModelFactory[SystemConfigModelRegistry]):
    """Polyfactory model factory for SystemConfigModelRegistry domain models."""

    __model__ = SystemConfigModelRegistry

    name: str = "Primary Model Registry"
    type: str = "model_registry"
    slug: str | None = "primary_model_registry"
    default_provider: LLMProvider = LLMProvider.AI_STUDIO

    @classmethod
    def id(cls) -> str:
        """Generate a canonical system config Opaque Stripe ID.

        Returns:
            Canonical sys_<hex32> identifier.
        """
        return generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)

    @classmethod
    def tier_definitions(cls) -> dict[CognitiveTier, ModelProfile]:
        """Generate complete four-tier model profile mappings.

        Returns:
            Mapping of all canonical CognitiveTier members to ModelProfile objects.
        """
        return {
            CognitiveTier.FAST: ModelProfile(
                provider=LLMProvider.AI_STUDIO,
                model_name="gemini/gemini-2.5-flash",
                temperature=0.2,
                allowed_tools=[],
                additional_params=ProviderExtraParamsDTO(),
            ),
            CognitiveTier.BALANCED: ModelProfile(
                provider=LLMProvider.AI_STUDIO,
                model_name="gemini/gemini-2.5-flash",
                temperature=0.4,
                allowed_tools=[],
                additional_params=ProviderExtraParamsDTO(),
            ),
            CognitiveTier.DEEP: ModelProfile(
                provider=LLMProvider.AI_STUDIO,
                model_name="gemini/gemini-2.5-pro",
                temperature=0.7,
                allowed_tools=[],
                additional_params=ProviderExtraParamsDTO(),
            ),
            CognitiveTier.REASONING: ModelProfile(
                provider=LLMProvider.AI_STUDIO,
                model_name="gemini/gemini-2.5-pro",
                temperature=1.0,
                thinking_budget_tokens=4096,
                allowed_tools=[],
                additional_params=ProviderExtraParamsDTO(),
            ),
        }


def _make_uow_harness() -> tuple[InMemoryUnitOfWork, Callable[[], QuorumUnitOfWork]]:
    """Construct a shared InMemoryUnitOfWork store and a UnitOfWorkFactory callable.

    Returns:
        Tuple of (shared InMemoryUnitOfWork instance, factory returning UoWs bound to the same store).
    """
    base_uow = InMemoryUnitOfWork()

    def uow_factory() -> QuorumUnitOfWork:
        return InMemoryUnitOfWork(store=base_uow.store)

    return base_uow, uow_factory


def _make_root_token() -> TokenData:
    """Create a ROOT TokenData fixture with a canonical UUIDv7 user identifier.

    Returns:
        Validated ROOT TokenData instance.
    """
    return TokenData(id=generate_opaque_id(EntityPrefix.USER), role=UserRole.ROOT)


def _create_sample_workflow(
    workflow_id: str,
    profile_id: str,
    model_registry_id: str,
) -> Workflow:
    """Build a valid Workflow domain model using WorkflowFactory.

    Args:
        workflow_id: Canonical wf_<hex32> identifier.
        profile_id: Canonical prf_<hex32> default profile identifier.
        model_registry_id: Canonical sys_<hex32> model registry identifier.

    Returns:
        Validated Workflow instance.
    """
    return WorkflowFactory.build(
        id=workflow_id,
        slug="test_workflow",
        name=I18nText(translations={"en": "Original Workflow", "fi": "Alkuperainen tyonkulku"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        status="active",
        version=1,
        organization_id=None,
        default_profile_id=profile_id,
        mcp_gateway_id=None,
        default_strictness_level=50,
        enable_semantic_smoothing=False,
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
        expected_inputs=[],
        model_registry_id=model_registry_id,
    )


def _create_sample_output_profile(profile_id: str, workflow_id: str) -> OutputProfile:
    """Build a valid OutputProfile domain model using OutputProfileFactory.

    Args:
        profile_id: Canonical prf_<hex32> identifier.
        workflow_id: Canonical wf_<hex32> parent workflow identifier.

    Returns:
        Validated OutputProfile instance.
    """
    return OutputProfileFactory.build(
        id=profile_id,
        slug="test_profile",
        name=I18nText(translations={"en": "Test Profile", "fi": "Testiprofiili"}),
        description=I18nText(translations={"en": "Profile Desc", "fi": "Profiilin kuvaus"}),
        organization_id=None,
        workflow_id=workflow_id,
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
        matrix_synthesis_groups=[],
        content_blocks=[],
        visible_block_extensions=[],
        visible_workflow_extensions=[],
        variance_target_block=None,
        user_role_target_block=None,
    )


async def test_save_workflow_updates_inplace_and_preserves_preflight() -> None:
    """Verify saving an existing workflow updates in-place without creating orphan records."""
    base_uow, uow_factory = _make_uow_harness()

    workflow_repo = WorkflowRepositoryImpl(uow_factory=uow_factory)
    output_profile_repo = OutputProfileRepositoryImpl(uow_factory=uow_factory)
    prompt_block_repo = PromptBlockRepositoryImpl(uow_factory=uow_factory)
    system_repo = SystemRepositoryImpl(uow_factory=uow_factory)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
    )

    root_token = _make_root_token()
    target_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    prof_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    reg_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)

    initial_wf = _create_sample_workflow(target_id, prof_id, reg_id)
    profile = _create_sample_output_profile(prof_id, target_id)

    await base_uow.entities.upsert_workflow(initial_wf)
    await base_uow.entities.upsert_output_profile(profile)

    updated_data = initial_wf.model_copy(
        update={
            "name": I18nText(translations={"en": "Updated Workflow", "fi": "Paivitetty tyonkulku"}),
            "default_strictness_level": 85,
            "enable_semantic_smoothing": True,
        }
    )

    res = await workflow_service.save_workflow(root_token, target_id, updated_data)

    assert res.id == target_id
    assert re.match(OPAQUE_STRIPE_ID_REGEX, res.id)
    assert res.default_strictness_level == 85
    assert res.enable_semantic_smoothing is True

    persisted = await workflow_repo.get_workflow_by_id(target_id)
    assert persisted is not None
    assert persisted.default_strictness_level == 85
    assert persisted.enable_semantic_smoothing is True

    wf_docs = await base_uow.entities.list_workflows()
    assert len(wf_docs) == 1
    workflow_adapter = TypeAdapter(Workflow)
    for doc in wf_docs:
        reconstituted = workflow_adapter.validate_python(doc.model_dump(mode="json"))
        assert reconstituted.id == target_id
        assert re.match(OPAQUE_STRIPE_ID_REGEX, reconstituted.id)


async def test_save_step_updates_inplace_and_preserves_preflight() -> None:
    """Verify saving an existing step updates in-place without creating orphan records."""
    base_uow, uow_factory = _make_uow_harness()

    workflow_repo = WorkflowRepositoryImpl(uow_factory=uow_factory)
    output_profile_repo = OutputProfileRepositoryImpl(uow_factory=uow_factory)
    prompt_block_repo = PromptBlockRepositoryImpl(uow_factory=uow_factory)
    system_repo = SystemRepositoryImpl(uow_factory=uow_factory)

    workflow_service = StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
    )

    root_token = _make_root_token()
    target_id = generate_opaque_id(EntityPrefix.STEP)
    initial_step = _StepFactory.build(id=target_id)
    await base_uow.entities.upsert_step(initial_step)

    updated_data = initial_step.model_copy(
        update={
            "hook": "updated_hook",
            "name": I18nText(translations={"en": "Updated Step", "fi": "Paivitetty askel"}),
        }
    )

    res = await workflow_service.save_step(root_token, target_id, updated_data)

    assert res.id == target_id
    assert re.match(OPAQUE_STRIPE_ID_REGEX, res.id)
    assert res.hook == "updated_hook"
    assert res.name.translations["en"] == "Updated Step"

    persisted = await workflow_repo.get_step_by_id(target_id)
    assert persisted is not None
    assert persisted.hook == "updated_hook"
    assert persisted.name.translations["en"] == "Updated Step"

    step_docs = await base_uow.entities.list_steps()
    assert len(step_docs) == 1
    for doc in step_docs:
        validated = Step.model_validate(doc.model_dump(mode="json"))
        assert validated.id == target_id
        assert re.match(OPAQUE_STRIPE_ID_REGEX, validated.id)


async def test_save_output_profile_updates_inplace_and_preserves_preflight() -> None:
    """Verify saving an output profile updates in-place without creating orphan records."""
    base_uow, uow_factory = _make_uow_harness()

    workflow_repo = WorkflowRepositoryImpl(uow_factory=uow_factory)
    output_profile_repo = OutputProfileRepositoryImpl(uow_factory=uow_factory)
    prompt_block_repo = PromptBlockRepositoryImpl(uow_factory=uow_factory)
    system_repo = SystemRepositoryImpl(uow_factory=uow_factory)

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

    root_token = _make_root_token()
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    prof_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    reg_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)

    await base_uow.entities.upsert_workflow(_create_sample_workflow(wf_id, prof_id, reg_id))
    initial_prof = _create_sample_output_profile(prof_id, wf_id)
    await base_uow.entities.upsert_output_profile(initial_prof)

    updated_prof = initial_prof.model_copy(
        update={
            "name": I18nText(translations={"en": "Updated Profile", "fi": "Paivitetty profiili"}),
        }
    )

    res = await output_profile_service.save_output_profile(root_token, prof_id, updated_prof)

    assert res.id == prof_id
    assert re.match(OPAQUE_STRIPE_ID_REGEX, res.id)
    assert res.name.translations["en"] == "Updated Profile"

    persisted = await output_profile_repo.get_output_profile_by_id(prof_id)
    assert persisted is not None
    assert persisted.id == prof_id
    assert persisted.name.translations["en"] == "Updated Profile"

    prof_docs = await base_uow.entities.list_output_profiles()
    assert len(prof_docs) == 1
    for doc in prof_docs:
        validated = OutputProfile.model_validate(doc.model_dump(mode="json"))
        assert validated.id == prof_id
        assert re.match(OPAQUE_STRIPE_ID_REGEX, validated.id)


async def test_create_output_profile_draft_binds_to_valid_workflow() -> None:
    """Verify output profile draft binds to an active workflow with a canonical UUIDv7 ID."""
    base_uow, uow_factory = _make_uow_harness()

    workflow_repo = WorkflowRepositoryImpl(uow_factory=uow_factory)
    output_profile_repo = OutputProfileRepositoryImpl(uow_factory=uow_factory)
    prompt_block_repo = PromptBlockRepositoryImpl(uow_factory=uow_factory)
    system_repo = SystemRepositoryImpl(uow_factory=uow_factory)

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

    root_token = _make_root_token()
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    prof_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    reg_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
    await base_uow.entities.upsert_workflow(_create_sample_workflow(wf_id, prof_id, reg_id))

    draft = await output_profile_service.create_output_profile_draft(root_token)
    assert re.match(OPAQUE_STRIPE_ID_REGEX, draft.id)
    assert parse_prefixed_uuid7(draft.id, EntityPrefix.OUTPUT_PROFILE).version == 7
    assert draft.workflow_id == wf_id
    assert draft.workflow_id != "*"


async def test_save_prompt_block_updates_inplace_and_preserves_preflight() -> None:
    """Verify saving a prompt block updates in-place without creating orphan records."""
    base_uow, uow_factory = _make_uow_harness()

    prompt_block_repo = PromptBlockRepositoryImpl(uow_factory=uow_factory)
    system_repo = SystemRepositoryImpl(uow_factory=uow_factory)
    prompt_block_service = StudioPromptBlockService(
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
    )

    root_token = _make_root_token()
    target_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
    initial_block = _PersonaPromptBlockFactory.build(id=target_id)
    await base_uow.entities.upsert_prompt_block(initial_block)

    updated_block = initial_block.model_copy(
        update={
            "label": I18nText(translations={"en": "Updated Persona", "fi": "Paivitetty persoona"}),
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

    block_docs = await base_uow.entities.list_prompt_blocks()
    assert len(block_docs) == 1
    for doc in block_docs:
        validated = PromptBlockAdapter.validate_python(doc.model_dump(mode="json"))
        assert validated.id == target_id
        assert re.match(OPAQUE_STRIPE_ID_REGEX, validated.id)
        assert isinstance(validated, PersonaPromptBlock)


async def test_save_system_config_model_registry_updates_inplace_and_preserves_preflight() -> None:
    """Verify StudioSystemConfigService and SystemRepositoryImpl update model registries in-place."""
    base_uow, uow_factory = _make_uow_harness()

    system_repo = SystemRepositoryImpl(uow_factory=uow_factory)
    workflow_repo = WorkflowRepositoryImpl(uow_factory=uow_factory)
    system_service = StudioSystemConfigService(system_repo=system_repo, workflow_repo=workflow_repo)

    root_token = _make_root_token()
    registry_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
    initial_registry = _ModelRegistryFactory.build(id=registry_id, name="Initial Registry")
    await base_uow.entities.upsert_system_config(initial_registry)

    updated_tiers = dict(initial_registry.tier_definitions)
    updated_tiers[CognitiveTier.FAST] = ModelProfile(
        provider=LLMProvider.VERTEX_AI,
        model_name="vertex_ai/gemini-2.5-flash",
        temperature=0.1,
        allowed_tools=[],
        additional_params=ProviderExtraParamsDTO(vertex_location="europe-north1"),
    )
    updated_payload = initial_registry.model_copy(
        update={
            "name": "Updated Production Registry",
            "default_provider": LLMProvider.VERTEX_AI,
            "tier_definitions": updated_tiers,
        }
    )

    saved = await system_service.save_system_config(root_token, registry_id, updated_payload)
    assert saved.id == registry_id
    assert re.match(OPAQUE_STRIPE_ID_REGEX, saved.id)
    assert saved.name == "Updated Production Registry"
    assert saved.default_provider == LLMProvider.VERTEX_AI

    reloaded = await system_repo.get_model_registry(registry_id=registry_id)
    assert reloaded.id == registry_id
    assert reloaded.name == "Updated Production Registry"
    assert reloaded.tier_definitions[CognitiveTier.FAST].model_name == "vertex_ai/gemini-2.5-flash"

    all_registries = await system_service.list_system_configs(root_token)
    assert len(all_registries) == 1
    registry_adapter = TypeAdapter(SystemConfigModelRegistry)
    reconstituted = registry_adapter.validate_python(all_registries[0].model_dump(mode="json"))
    assert reconstituted.id == registry_id
    assert re.match(OPAQUE_STRIPE_ID_REGEX, reconstituted.id)


async def test_clone_and_delete_system_config_model_registry_preserves_preflight() -> None:
    """Verify draft, clone, and delete lifecycle for model registries over InMemoryUnitOfWork."""
    _, uow_factory = _make_uow_harness()

    system_repo = SystemRepositoryImpl(uow_factory=uow_factory)
    workflow_repo = WorkflowRepositoryImpl(uow_factory=uow_factory)
    system_service = StudioSystemConfigService(system_repo=system_repo, workflow_repo=workflow_repo)
    root_token = _make_root_token()

    reg_draft = await system_service.create_system_config_draft(root_token)
    assert re.match(OPAQUE_STRIPE_ID_REGEX, reg_draft.id)
    assert parse_prefixed_uuid7(reg_draft.id, EntityPrefix.SYSTEM_CONFIG).version == 7

    cloned = await system_service.clone_system_config(root_token, reg_draft.id)
    assert cloned.id != reg_draft.id
    assert re.match(OPAQUE_STRIPE_ID_REGEX, cloned.id)
    assert parse_prefixed_uuid7(cloned.id, EntityPrefix.SYSTEM_CONFIG).version == 7

    all_registries = await system_repo.get_all_model_registries()
    assert len(all_registries) == 2

    await system_service.delete_system_config(root_token, cloned.id)
    remaining = await system_repo.get_all_model_registries()
    assert [m.id for m in remaining] == [reg_draft.id]


async def test_save_output_profile_invalid_target_component_validation_failure() -> None:
    """Verify saving an output profile with an unsupported target block raises 400 VALIDATION_FAILED."""
    base_uow, uow_factory = _make_uow_harness()

    workflow_repo = WorkflowRepositoryImpl(uow_factory=uow_factory)
    output_profile_repo = OutputProfileRepositoryImpl(uow_factory=uow_factory)
    prompt_block_repo = PromptBlockRepositoryImpl(uow_factory=uow_factory)
    system_repo = SystemRepositoryImpl(uow_factory=uow_factory)

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

    root_token = _make_root_token()
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    prof_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    reg_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
    grp_id = generate_opaque_id(EntityPrefix.SYNTHESIS_GROUP)

    await base_uow.entities.upsert_workflow(_create_sample_workflow(wf_id, prof_id, reg_id))
    base_prof = _create_sample_output_profile(prof_id, wf_id)
    await base_uow.entities.upsert_output_profile(base_prof)

    invalid_prof = base_prof.model_copy(
        update={
            "matrix_synthesis_groups": [
                MatrixSynthesisGroup(
                    id=grp_id,
                    title=I18nText(translations={"en": "Invalid Group"}),
                    target_blocks=["blk_0195f3a0000070008000000000000099"],
                )
            ]
        }
    )

    with pytest.raises(AppException) as exc_info:
        await output_profile_service.save_output_profile(root_token, prof_id, invalid_prof)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] in (
        ErrorCodes.VALIDATION_FAILED,
        ErrorCodes.VALIDATION_FAILED.value,
    )


async def test_save_output_profile_nonexistent_workflow_not_found_error() -> None:
    """Verify saving an output profile referencing a missing workflow raises ResourceNotFoundError."""
    base_uow, uow_factory = _make_uow_harness()

    workflow_repo = WorkflowRepositoryImpl(uow_factory=uow_factory)
    output_profile_repo = OutputProfileRepositoryImpl(uow_factory=uow_factory)
    prompt_block_repo = PromptBlockRepositoryImpl(uow_factory=uow_factory)
    system_repo = SystemRepositoryImpl(uow_factory=uow_factory)

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

    root_token = _make_root_token()
    prof_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    missing_wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)

    prof = _create_sample_output_profile(prof_id, missing_wf_id)
    await base_uow.entities.upsert_output_profile(prof)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await output_profile_service.save_output_profile(root_token, prof_id, prof)
    assert exc_info.value.details["resource_type"] == "workflow"


async def test_save_system_config_missing_registry_not_found_error() -> None:
    """Verify saving an unseeded model registry raises ResourceNotFoundError."""
    _, uow_factory = _make_uow_harness()
    system_repo = SystemRepositoryImpl(uow_factory=uow_factory)
    system_service = StudioSystemConfigService(system_repo=system_repo)

    root_token = _make_root_token()
    missing_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
    payload = _ModelRegistryFactory.build(id=missing_id)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await system_service.save_system_config(root_token, missing_id, payload)
    assert exc_info.value.status_code == 404


async def test_save_system_config_non_root_permission_failure() -> None:
    """Verify non-ROOT caller attempting to save a model registry raises PermissionDeniedError."""
    base_uow, uow_factory = _make_uow_harness()
    system_repo = SystemRepositoryImpl(uow_factory=uow_factory)
    system_service = StudioSystemConfigService(system_repo=system_repo)

    registry_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
    seeded = _ModelRegistryFactory.build(id=registry_id)
    await base_uow.entities.upsert_system_config(seeded)

    admin_token = TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.ADMIN,
        organization_id=generate_opaque_id(EntityPrefix.ORGANIZATION),
    )

    with pytest.raises(PermissionDeniedError):
        await system_service.save_system_config(admin_token, registry_id, seeded)


async def test_get_model_registry_empty_or_missing_not_found_error() -> None:
    """Verify SystemRepositoryImpl.get_model_registry raises ResourceNotFoundError on empty or unknown ID."""
    _, uow_factory = _make_uow_harness()
    system_repo = SystemRepositoryImpl(uow_factory=uow_factory)

    with pytest.raises(ResourceNotFoundError) as empty_exc:
        await system_repo.get_model_registry("")
    assert empty_exc.value.details["resource_type"] == "system_config"

    unknown_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
    with pytest.raises(ResourceNotFoundError) as missing_exc:
        await system_repo.get_model_registry(unknown_id)
    assert missing_exc.value.details["resource_id"] == unknown_id
