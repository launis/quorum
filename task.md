# Task Tracker: Binary Target Speaker Contract Anchored to `is_chat_history` SSOT & Strict Quote Validation

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_matrix_sensor_prompt_builder.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[C:\Users\risto\.gemini\antigravity-ide\brain\8bed8fbd-0f73-428e-a4dc-f5823a77a3b2\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Phase 1, Step 1.1 (`touched_scope_tech_debt_mandate`): Eradicate under-engineering assumptions in touched boundaries before adding features.
- [x] Phase 1, Step 1.2 (`variable_and_schema_preservation_mandate`): Use Quorum's authoritative SSOT domain term AI instead of ASSISTANT; ban ALL value.
- [x] Phase 1, Step 1.3 (`pydantic_annotated_fields_mandate`): Use PEP 593 Annotated syntax with default=TargetSpeaker.USER.
- [x] Phase 1, Step 1.4 (`zero_naked_dicts`): Maintain immutable ConfigDict(strict=True, frozen=True, extra='forbid').
- [x] Phase 1, Step 1.5 (`zero_service_layer_fallbacks`): Use direct dot notation access without getattr() or .get() fallbacks.
- [x] Phase 1, Step 1.6 (`cross_domain_dto_parity`): Maintain 1:1 field nomenclature between Python snake_case and Dart camelCase.
- [x] Phase 2, Step 2.1 (`cdata_template_shielding_mandate`): Use TemplateProcessor.encapsulate_payload for safe CDATA shielding.
- [x] Phase 2, Step 2.1 (`four_layer_clean_stack_mandate`): Inject exclusively into Layer 4 dynamic user message to preserve prefix context caching.
- [x] Phase 2, Step 2.2 (`universal_fail_fast`): Crash loudly on schema violation rather than allowing ungrounded positive evaluations to pass silently.
- [x] Phase 2, Step 2.3 (`the_duct_tape_ban`): Enforce mathematical proof of speaker attribution without fuzzy guessing, anchored to Ingress stream SSOT.
- [x] Phase 4, Step 4.1 (`knowledge_base_primacy`): Ensure AI agent knowledge items reflect physical code state before updating human architecture manifestos.
- [x] Phase 4, Step 4.2 & 4.3 (`documentation_present_tense_mandate`): Describe purely and authoritatively what the system currently has and how it operates right now.

## Execution Tasks

- [x] **Phase 1: Pre-Implementation Cleanups and Domain Definitions**
  - [x] Step 1.1: Pre-Implementation Cleanups (Technical Debt Eradication) (`extractive_sensor_service.py`, `anchor_validation_service.py`, `prompt_block.dart`)
  - [x] Step 1.2: Define Strict Binary `TargetSpeaker` StrEnum (`backend_v2/models/enums.py`)
  - [x] Step 1.3: Add `target_speaker` field to `TDAAssertion` (`backend_v2/models/v2_core.py`)
  - [x] Step 1.4: Add `target_speaker` field to `FlattenedAtom` DTO (`backend_v2/models/dtos/engine.py`)
  - [x] Step 1.5: Propagate `target_speaker` in Atom Flattening and Simulation Hooks (`atom_flattening.py`, `simulation_service.py`)
  - [x] Step 1.6: Add `TargetSpeaker` Enum and Model in Frontend Freezed Model (`client_app_v2/lib/core/models/enums.dart`, `prompt_block.dart`)

- [x] **Phase 2: Prompt Compilation, Extraction Validation & Lexical Gate**
  - [x] Step 2.1: Resolve Prompt Contradiction and Update Prompt Directives (`global_mandates.py`, `matrix_evaluation.py`, `matrix_sensor_prompt_builder.py`)
  - [x] Step 2.2: Implement Strict Evidence Quote Validator on `BooleanEvaluationResult` (`extractive_sensor_service.py`)
  - [x] Step 2.3: Implement Deterministic Lexical Speaker Verification in `AnchorValidationService` (`anchor_validation_service.py`)

- [x] **Phase 3: Automated Quality Gates and Test Coverage Expansion**
  - [x] Step 3.1: Backend Unit Tests for `TargetSpeaker` and Model Serialization (`test_target_speaker_enum.py`, `test_engine.py`)
  - [x] Step 3.2: Prompt Builder Unit Tests for `TargetSpeaker` Injection (`test_matrix_sensor_prompt_builder.py`)
  - [x] Step 3.3: ISTQB Negative Partition Tests for `BooleanEvaluationResult` and `AnchorValidationService` (`test_extractive_sensor_service.py`, `test_anchor_validation_service.py`)
  - [x] Step 3.4: Dart Freezed Code Generation and Frontend Unit Tests (`matrix_claim_test.dart`)
  - [x] Step 3.5: Universal Quality Gates Audit Verification

- [x] **Phase 4: Knowledge Items & Architecture Synchronization (Tier 7 Documentation)**
  - [x] Step 4.1: Update Relevant Knowledge Item Artifacts & Metadata
  - [x] Step 4.2: Execute Tier 7 Architecture Synchronization for `docs/architecture/06_enriched_atom_graph_engine.md`
  - [x] Step 4.3: Execute Tier 7 Architecture Synchronization for `docs/architecture/09_llm_prompt_orchestration_and_matrix_evaluation.md`
