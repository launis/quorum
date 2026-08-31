<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

# Phase 3C: Repositories & Domain Models Duck-Typing Eradication

## Overview

Eliminate all remaining `isinstance(..., dict)` duck-typing checks, `# noqa: QGR012` suppressions, and non-exempt `dict[str, Any]` annotations across the Data Access Layer (Repositories) and Domain Models. Enforce the repository reconstitution firewall: internal database drivers handle persistence dictionaries while repositories reconstitute and return strictly typed Pydantic Domain models with zero dictionary leakage into callers.

## Target Files

- `[MODIFY]` `@[backend_v2/database/repositories/execution.py#L17-L353]`
- `[MODIFY]` `@[backend_v2/database/repositories/component.py#L13-L154]`
- `[MODIFY]` `@[backend_v2/database/repositories/components/matrix.py#L13-L102]`
- `[MODIFY]` `@[backend_v2/database/repositories/audit.py#L17-L292]`
- `[MODIFY]` `@[backend_v2/database/repositories/workflow.py#L19-L303]`
- `[MODIFY]` `@[backend_v2/models/domain/inputs.py#L57-L102]`
- `[MODIFY]` `@[backend_v2/models/domain/mechanical_anchors.py#L17-L117]`
- `[MODIFY]` `@[backend_v2/models/dtos/evaluation_steps.py#L17-L114]`
- `[MODIFY]` `@[backend_v2/models/dtos/quote_evidence.py#L69-L142]`
- `[MODIFY]` `@[backend_v2/models/state.py#L348-L455]`
- `[MODIFY]` `@[backend_v2/models/domain/archivist.py#L58-L144]`
- `[MODIFY]` `@[backend_v2/models/dtos/matrix_scorecard.py#L75-L132]`
- `[MODIFY]` `@[backend_v2/models/domain/prompt_blocks.py#L71-L98]`
- `[MODIFY]` `@[backend_v2/models/domain/validation.py#L161-L173]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 3: Hooks, Orchestrator & Repository Suppression Eradication]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/database/repositories/execution.py]</backend>
      <backend>@[backend_v2/database/repositories/component.py]</backend>
      <backend>@[backend_v2/database/repositories/components/matrix.py]</backend>
      <backend>@[backend_v2/database/repositories/audit.py]</backend>
      <backend>@[backend_v2/database/repositories/workflow.py]</backend>
      <backend>@[backend_v2/models/domain/inputs.py]</backend>
      <backend>@[backend_v2/models/domain/mechanical_anchors.py]</backend>
      <backend>@[backend_v2/models/dtos/evaluation_steps.py]</backend>
      <backend>@[backend_v2/models/dtos/quote_evidence.py]</backend>
      <backend>@[backend_v2/models/state.py]</backend>
      <backend>@[backend_v2/models/domain/archivist.py]</backend>
      <backend>@[backend_v2/models/dtos/matrix_scorecard.py]</backend>
      <backend>@[backend_v2/models/domain/prompt_blocks.py]</backend>
      <backend>@[backend_v2/models/domain/validation.py]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="RepositoryReconstitutionFirewall">
      # Repositories map raw database driver records immediately into Pydantic models (strict=False)
      # Zero dict leakage past repository boundary
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/database/interfaces.py]</file>
    <file>@[backend_v2/database/wrapper.py]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item>Zero isinstance(..., dict) checks across repositories and domain models</item>
    <item>Zero # noqa: QGR012 suppressions in repository files</item>
    <item>Persistence drivers isolated behind 102 exempt dictionary annotations</item>
    <item>AST guardrails pass 100% clean on repositories and models in --strict mode</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK & PRE-IMPLEMENTATION CLEANUPS">
    <action>In @[backend_v2/models/domain/prompt_blocks.py#L88-L98], eliminate `object.__setattr__()` calls in `MatrixPromptBlock.compute_min_max` (QGR001 violation) by computing extrema and returning `self.model_copy(update=...)`.</action>
    <action>In @[backend_v2/models/domain/validation.py#L161-L173], replace `extra="ignore"` in `SystemWarningsStateDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)` (QGR007 violation) to uphold the duck_typing_token_shield_ban.</action>
  </step>

  <step id="1" name="HARDEN REPOSITORY RECONSTITUTION LAYER">
    <action>In @[backend_v2/database/repositories/execution.py#L20-L71] and @[backend_v2/database/repositories/execution.py#L73-L154], eradicate 4 `# noqa: QGR012` suppressions by validating `FrozenContext` and `MCPAuditTrace` directly using typed Pydantic models and validating `ExecutionRecord.model_validate(raw, strict=False)`.</action>
    <action>In @[backend_v2/database/repositories/component.py#L134-L154] and @[backend_v2/database/repositories/components/matrix.py#L82-L102], eradicate `isinstance(..., dict)` checks in `get_components_using_dimension` and `get_matrices_using_dimension` by validating criteria using `MatrixPromptBlock` or `TypeAdapter`.</action>
    <action>In @[backend_v2/database/repositories/audit.py#L74-L87] and @[backend_v2/database/repositories/audit.py#L194-L292], eliminate `hasattr(record, "model_dump")` (QGR001) in `log_usage` and `isinstance(e["models_used"], dict)` in `get_detailed_usage` via typed `isinstance(record, UsageRecord)` checks and typed model reconstitution.</action>
    <action>In @[backend_v2/database/repositories/workflow.py#L214-L233], eliminate `isinstance(s, dict)` check in `get_step_by_id` fallback traversal by validating steps via `Step.model_validate(s, strict=False)`.</action>
  </step>

  <step id="2" name="HARDEN DOMAIN MODELS, DTOS & STATE PROJECTORS">
    <action>In @[backend_v2/models/domain/inputs.py#L64-L102], convert `WorkflowInputs.prevent_base64_pollution` to `@model_validator(mode="after")` on typed `self` instance, eradicating 4 `isinstance(..., dict)` checks.</action>
    <action>In @[backend_v2/models/domain/mechanical_anchors.py#L32-L93], eliminate `isinstance(..., dict)` and `.get()` fallback chains in `MechanicalAnchorsPayload.from_context` by validating input context via `TypeAdapter` and strict Pydantic parsing.</action>
    <action>In @[backend_v2/models/dtos/evaluation_steps.py#L30-L72] and @[backend_v2/models/dtos/evaluation_steps.py#L74-L114], eliminate `isinstance(data, dict)` checks in `BaseExtractionDTO` by enforcing exclusivity and sanitization via `@model_validator(mode="after")` or typed field validators.</action>
    <action>In @[backend_v2/models/dtos/quote_evidence.py#L35-L66] and @[backend_v2/models/dtos/quote_evidence.py#L89-L142], eradicate `isinstance(data, dict)` and `info.context.get(...)` calls in `LLMExtractedQuote` and `QuoteEvidenceDTO` via typed `AliasEngine` verification.</action>
    <action>In @[backend_v2/models/state.py#L371-L410] and @[backend_v2/models/state.py#L412-L437], eliminate `isinstance(event.content, dict)` in `fold_trace` and `isinstance(step_output, dict)` in `_build_dto_list` by operating strictly on typed `StepOutputDTO` instances.</action>
    <action>In @[backend_v2/models/domain/archivist.py#L109-L144] and @[backend_v2/models/dtos/matrix_scorecard.py#L114-L132], convert `calc_compliance` and `map_contested_to_warning` to `@model_validator(mode="after")` returning `self.model_copy(update=...)`, eradicating all duck-typing.</action>
  </step>

  <step id="3" name="TEST EXPANSION & UNIVERSAL QUALITY GATE">
    <action>Expand test suites in `backend_v2/tests/unit/database/repositories/` and `backend_v2/tests/unit/models/` with ISTQB negative boundary and equivalence partition tests.</action>
    <action>Verify all 12 target files and 2 pre-cleanup files pass AST guardrails in `--strict` mode.</action>
    <action>Execute full backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/ backend_v2/models/ --test`.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_repository_reconstitutes_typed_domain_models">
      <input>Raw database record dictionary from driver</input>
      <expected>reconstitutes into strict frozen Pydantic Domain model without leaking dict</expected>
      <category>positive</category>
    </contract>
    <contract id="2" name="test_domain_models_forbid_duck_typing">
      <input>Malformed payload with untyped dictionary</input>
      <expected>raises pydantic.ValidationError</expected>
      <category>negative</category>
    </contract>
    <contract id="3" name="test_workflow_inputs_prevent_base64_rejection">
      <input>WorkflowInputs payload containing binary content_base64</input>
      <expected>raises AppException with ErrorCodes.VALIDATION_FAILED</expected>
      <category>negative</category>
    </contract>
    <contract id="4" name="test_matrix_prompt_block_compute_min_max_immutable">
      <input>MatrixPromptBlock initialized with scales but without computed_min/max</input>
      <expected>dynamically computes min and max scores via model_copy without object.__setattr__</expected>
      <category>positive</category>
    </contract>
    <contract id="5" name="test_tda_scorecard_atom_warning_intent_on_override">
      <input>TDAScorecardAtom with status=PASSED and contextual_override=True</input>
      <expected>sets visual_intent=VisualIntent.WARNING via mode=after validator</expected>
      <category>positive</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run AST guardrail scan and backend audit loop on Repositories and Models:</action>
    <command>uv run python scripts/_ast_guardrails.py backend_v2/database/repositories/ backend_v2/models/ --strict</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/ backend_v2/models/ --test</command>
  </validation_gate>
</execution_protocol>

## 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Execution Repository** (`backend_v2/database/repositories/execution.py`) | Banned 4 `# noqa: QGR012` inline suppressions, raw payload duck-typing, and unvalidated `frozen_context` dict branching in `_offload_payloads` / `_hydrate_payloads`. | Reconstitute `FrozenContext` and `MCPAuditTrace` directly using strict Pydantic models. Reconstitute `ExecutionRecord` using `ExecutionRecord.model_validate(raw, strict=False)`. | Eradicate manual dict indexing and fallback branching; pass typed DTO models to subcollection persistence. | AST scan `_ast_guardrails.py` in `--strict` mode; verify `test_execution.py` passes 100%. |
| **Component & Matrix Repositories** (`backend_v2/database/repositories/component.py`, `backend_v2/database/repositories/components/matrix.py`) | Banned 4 `isinstance(..., dict)` duck-typing checks in `get_components_using_dimension` and `get_matrices_using_dimension`. | Validate criteria via typed `MatrixPromptBlock` or `TypeAdapter` when filtering matrices referencing dimensions. | Avoid creating ad-hoc custom query adapters; hydrate components via `TypeAdapter` or model validation. | AST guardrail scan `--strict` reports 0 QGR012 violations on repository files; `test_component.py` and `test_matrix.py` pass. |
| **Audit Repository** (`backend_v2/database/repositories/audit.py`) | Banned `hasattr(record, "model_dump")` (QGR001) in `log_usage` and `isinstance(e["models_used"], dict)` in `get_detailed_usage`. | Type `record: UsageRecord | dict[str, Any]` with explicit `isinstance(record, UsageRecord)` check; hydrate usage summaries strictly. | Reject shadow aggregation models; use typed `UsageRecord` and `AuditLogEntry` domain models natively. | AST guardrail scan passes with 0 violations; `test_audit.py` passes 100%. |
| **Workflow Repository** (`backend_v2/database/repositories/workflow.py`) | Banned `isinstance(s, dict)` check in `get_step_by_id` fallback traversal across workflow steps. | Validate workflow steps via `Step.model_validate(s, strict=False)` or traverse strongly typed `Workflow.steps`. | Eliminate legacy raw dictionary step searches; rely on standard `Workflow` and `Step` domain models. | `test_workflow.py` passes; 0 AST violations reported. |
| **Workflow Inputs Domain Model** (`backend_v2/models/domain/inputs.py`) | Banned 4 `isinstance(..., dict)` duck-typing checks in `prevent_base64_pollution`. | Convert `prevent_base64_pollution` to `@model_validator(mode="after")` inspecting typed `self.dynamic_inputs` attributes. | Do not add custom recursive schema walking classes; inspect `self.dynamic_inputs` directly on typed model instance. | `test_inputs.py` verifies `ValidationError`/`AppException` on base64 payload injection; passes AST guardrails. |
| **Mechanical Anchors Domain Model** (`backend_v2/models/domain/mechanical_anchors.py`) | Banned 3 `isinstance(..., dict)` checks and lazy `.get()` fallback chains in `MechanicalAnchorsPayload.from_context`. | Parse input context via `TypeAdapter` and strict Pydantic parsing into `MechanicalAnchorsPayload`. | Avoid speculative multi-layered fallback dictionaries; resolve known namespaces deterministically. | `test_mechanical_anchors.py` passes all positive and negative boundary tests; passes AST scan `--strict`. |
| **Evaluation Steps DTOs** (`backend_v2/models/dtos/evaluation_steps.py`) | Banned `isinstance(data, dict)` checks in `BaseExtractionDTO` before validators. | Convert sanitization and exclusivity rules to typed field validators or `@model_validator(mode="after")`. | Eliminate duplicate cleaning loops; enforce exclusivity via `@model_validator(mode="after")` on typed attributes. | `test_evaluation_steps.py` passes; AST guardrails pass clean. |
| **Quote Evidence DTOs** (`backend_v2/models/dtos/quote_evidence.py`) | Banned `isinstance(data, dict)` and `ValidationInfo.context.get(...)` lazy fallback dictionaries in `LLMExtractedQuote` and `QuoteEvidenceDTO`. | Enforce typed `SourceDocumentContext` or `AliasEngine` verification without loose context dictionaries. | Avoid parallel alias caching dictionaries; use `AliasEngine` SSOT directly. | `test_quote_evidence.py` passes all alias verification cases; AST scan passes. |
| **State Projector Read Model** (`backend_v2/models/state.py`) | Banned `isinstance(event.content, dict)` in `fold_trace` and `if not isinstance(step_output, dict):` in `_build_dto_list`. | Validate trace event content and step outputs as typed `StepOutputDTO` or typed event payloads. | Avoid unstructured dict-based projection; use structured `list[StepOutputDTO]` natively. | `test_state.py` passes; AST scan passes 100% clean. |
| **Archivist & Scorecard Domain Models** (`backend_v2/models/domain/archivist.py`, `backend_v2/models/dtos/matrix_scorecard.py`) | Banned `isinstance(data, dict)` and `.get()` fallbacks in `ArchivistOutputDTO.calc_compliance` and `TDAScorecardAtom.map_contested_to_warning`. | Execute calculation and visual intent adjustment in `@model_validator(mode="after")` returning `self.model_copy(update=...)`. | Eradicate manual string checks; access typed Enum fields (`self.compliance_analysis`, `self.status`, `self.contextual_override`) directly. | `test_archivist.py` and `test_matrix_scorecard.py` pass; AST scan clean. |
| **Pre-Implementation Cleanups** (`prompt_blocks.py`, `validation.py`) | Banned `object.__setattr__()` in `MatrixPromptBlock.compute_min_max` (QGR001) and `extra="ignore"` in `SystemWarningsStateDTO` (QGR007). | Use `self.model_copy(update=...)` in `MatrixPromptBlock.compute_min_max`; lock `SystemWarningsStateDTO` with `extra="forbid"`. | Eradicate frozen model bypass hacks and token shield models. | AST scan passes 100% clean across all `backend_v2/models/domain/` files. |

## Falsification & Failure Modes

1. **Failure Mode 1: Validation Recursion on Frozen Models in `mode="after"` Validators**:
   - *Risk*: If `@model_validator(mode="after")` invokes `self.model_copy(update=...)` or model re-validation, it could trigger an infinite recursion loop if not guarded by value comparison.
   - *Mitigation*: In `MatrixPromptBlock.compute_min_max` and `TDAScorecardAtom.map_contested_to_warning`, only return `self.model_copy(update=...)` if the derived field value differs from current state.

2. **Failure Mode 2: Repository Reconstitution Mismatch with Driver Deserialization**:
   - *Risk*: `ExecutionRecord` contains complex nested types (`FrozenContext`, `TraceEvent`). If `_hydrate_payloads` fails to deserialize raw storage blobs before `ExecutionRecord.model_validate()`, strict validation will fail.
   - *Mitigation*: Ensure `_hydrate_payloads` uses typed `TypeAdapter(list[TraceEvent | ErrorTraceEvent | TombstoneEvent]).validate_json(blob_data)` and pass `strict=False` to `ExecutionRecord.model_validate()`.

