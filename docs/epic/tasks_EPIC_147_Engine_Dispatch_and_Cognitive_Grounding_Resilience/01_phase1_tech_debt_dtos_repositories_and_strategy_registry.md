# Phase 1: Pre-Implementation Technical Debt Cleanups, DTOs, Repository Interfaces & Strategy Registry

**Overview:** Eliminate scoped technical debt in `llm.py` and `test_llm_cost_tracking.py`, declare canonical `StepType(StrEnum)` and update `Step.type`, implement fail-fast `IPromptBlockRepository.get_prompt_blocks_by_ids` with strict mathematical set parity, encapsulate strategy dependencies into immutable `@dataclass(frozen=True) StrategyDependencies`, and establish declarative `NODE_STRATEGY_REGISTRY` with `NodeStrategyFactory` and atomic unit test migrations.
**Target Files:**
- `[MODIFY]` @[backend_v2/models/enums.py]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L540-L634]
- `[MODIFY]` @[backend_v2/database/interfaces.py#L677-L766]
- `[MODIFY]` @[backend_v2/database/repositories/components/prompt_block.py#L14-L174]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/base.py#L31-L54]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/logic.py#L19-L176]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781]
- `[NEW]` @[backend_v2/services/orchestrator/strategies/registry.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L148]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py#L25-L35]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py#L64-L99]
- `[MODIFY]` @[backend_v2/tests/unit/test_logic.py#L36-L64]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by previous epics. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/models/enums.py], @[backend_v2/models/v2_core.py#L540-L634], @[backend_v2/database/interfaces.py#L677-L766], @[backend_v2/database/repositories/components/prompt_block.py#L14-L174], @[backend_v2/services/orchestrator/strategies/base.py#L31-L54], @[backend_v2/services/orchestrator/strategies/logic.py#L19-L176], and @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] Stale mock patch `@patch("...tda_engine.get_settings")` removed from @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L148].
    - [x] Scoped technical debt in @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781] eliminated: silent `except Exception: pass` replaced with explicit `AppException` raising, `getattr`/`hasattr` duck-typing removed, magic defaults removed, and `PromptBlockCategory.MATRIX` enum comparison enforced.
    - [x] `StepType(StrEnum)` declared in @[backend_v2/models/enums.py] and adopted on `Step.type` in @[backend_v2/models/v2_core.py#L540-L634].
    - [x] `IPromptBlockRepository` and `PromptBlockRepositoryImpl` extended with `get_prompt_blocks_by_ids` returning hydrated `list[PromptBlock]` with strict mathematical set parity.
    - [x] `StrategyDependencies` container defined in @[backend_v2/services/orchestrator/strategies/base.py#L31-L54] and adopted across `NodeStrategy`, `LogicNodeStrategy`, and `LLMNodeStrategy`.
    - [x] Static `NODE_STRATEGY_REGISTRY` and `NodeStrategyFactory.create_strategy` implemented in [NEW] @[backend_v2/services/orchestrator/strategies/registry.py].
    - [x] Atomic unit test and mock migrations completed for `test_logic.py`, `test_llm_cost_tracking.py`, `test_prompt_block.py`, and `test_node_strategy_registry.py`.
    - [x] Quality gate `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/strategies backend_v2/tests/unit/test_logic.py --test` passes.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/models/enums.py]</backend>
    <backend>@[backend_v2/models/v2_core.py]</backend>
    <backend>@[backend_v2/database/interfaces.py]</backend>
    <backend>@[backend_v2/database/repositories/components/prompt_block.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/base.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/logic.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm.py]</backend>
    <!-- [NEW] backend_v2/services/orchestrator/strategies/registry.py -->
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `backend_v2/services/orchestrator/dag_executor.py` in Phase 1 (reserved for Phase 2).
    - Do NOT modify `backend_v2/hooks/source_verification_hook.py` or `backend_v2/services/source_verification_service.py` in Phase 1 (reserved for Phase 3).
    - Do NOT modify Flutter frontend files in this backend plan.
    - Treat read-only context references as immutable:
      - @[backend_v2/models/v2_core.py#L192-L205] (`TheoryGrounding` schema SSOT)
      - @[backend_v2/models/v2_core.py#L637-L674] (`StepRule` schema SSOT)
      - @[backend_v2/models/v2_core.py#L1400-L1412] (`FrozenContext` schema SSOT)
      - @[backend_v2/models/v2_core.py#L1492-L1550] (`ExecutionRecord` schema SSOT)
      - @[backend_v2/models/domain/source_verification.py#L61-L78] (`SourceVerificationResultDTO`)
      - @[backend_v2/models/dtos/engine.py#L51-L71] (`MatrixEvaluationContext` DTO)
      - @[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L10-L139] (`PromptCompilerAdapter`)
      - @[backend_v2/core/hook_registry.py#L83-L212] (`HookRegistry`, `HookState`, `HookDependencies`, `HookResult`)
      - @[backend_v2/services/mcp/tavily_search_client.py#L47-L184] (`tavily_search`, `batch_tavily_search`)
      - @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L218] (`TDAEngine`)
      - @[backend_v2/services/orchestrator/strategies/base.py#L57-L283] (Legacy 10-argument constructor boundary)
      - @[backend_v2/seed/seed_data.json#L223-L7542] (Coaching prompts SSOT)
  </anti_targets>

  <step id="1" name="Scoped Technical Debt Cleanup in test_llm_cost_tracking.py &amp; llm.py">
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L148]: Remove outdated mock `@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")` at line 60 and remove unused `mock_get_settings: MagicMock` parameter from `test_tda_engine_aggregates_token_usage_and_cost`.</action>
    <demolish>REMOVE: `@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")` and `mock_get_settings: MagicMock` at @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L148].</demolish>
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781]:
      - Replace raw string comparison `b.category_id == "matrix"` with `b.category_id == PromptBlockCategory.MATRIX` and `any(b.category_id == PromptBlockCategory.MATRIX for b in criteria_blocks_models)`.
      - Replace silent `except Exception: pass` blocks (lines 516-517, 539-540) with Fail-Fast `AppException` raising (specifically `ErrorCodes.RESOURCE_NOT_FOUND` and `ErrorCodes.VALIDATION_FAILED`) and structured RFC 7807 logging.
      - Eliminate `getattr(step, "input_mappings", None)` duck-typing. Resolve allowed dynamic keys directly from `input_mappings` argument combined with `context.expected_inputs`.
      - Eliminate `getattr(step, "mcp_tools", None)` and `hasattr(tool, "function")`. Iterate directly over `step.allowed_mcp_tools` (`list[str]`) from the `Step` model.
      - Eliminate `getattr(step, "expected_sdui_type", "grid")`.
    </action>
    <demolish>REMOVE: `except Exception: pass` in `_execute_llm_internal` at @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781]. REPLACE WITH: explicit `AppException` raising and RFC 7807 logging.</demolish>
    <demolish>REMOVE: `getattr(step, "input_mappings", None)`, `getattr(step, "mcp_tools", None)`, `hasattr(tool, "function")`, and `getattr(step, "expected_sdui_type", "grid")` at @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781].</demolish>
    <constraint invariant="touched_scope_tech_debt_mandate">All pre-existing technical debt in touched backend files must be resolved in Phase 1 before engine decomposition in Phase 2.</constraint>
  </step>

  <step id="2" name="Canonical StepType Enum &amp; Schema Update">
    <action>In @[backend_v2/models/enums.py], declare canonical `StepType(StrEnum)` and export in `__all__`:
```python
class StepType(StrEnum):
    """Execution taxonomy for workflow steps."""
    LLM = "llm"
    LOGIC = "logic"
```
    </action>
    <action>In @[backend_v2/models/v2_core.py#L540-L634], update `Step.type`:
```python
type: StepType = Field(default=StepType.LLM, description="Step execution type (llm or native logic)")
```
    </action>
    <constraint invariant="domain_model_purity_mandate">Closed-set string options must be defined as StrEnum in enums.py and referenced strictly in domain models.</constraint>
  </step>

  <step id="3" name="Fail-Fast PromptBlock Batch Resolution in Repository">
    <action>In @[backend_v2/database/interfaces.py#L677-L766]: Add `get_prompt_blocks_by_ids` to `IPromptBlockRepository`:
```python
@abc.abstractmethod
async def get_prompt_blocks_by_ids(
    self,
    block_ids: list[str],
    strict: bool = True,
) -> list[PromptBlock]:
    """Batch resolve prompt blocks by ID with mathematical set validation."""
    pass
```
    </action>
    <action>In @[backend_v2/database/repositories/components/prompt_block.py#L14-L174]: Implement `get_prompt_blocks_by_ids`:
      - Empty input fast-path: `if not block_ids: return []`.
      - Compute `unique_ids = list(dict.fromkeys(block_ids))`.
      - Query documents via `await self.driver.query("prompt_blocks", filters=[Filter(field="id", operator="in", value=unique_ids)])` or `[await self.get_prompt_block_by_id(bid) for bid in unique_ids]`.
      - Validate and hydrate records via `PromptBlockAdapter.validate_python(doc, strict=False)`.
      - Check strict set parity: `found_ids = {b.id for b in results}`; `missing_ids = [bid for bid in unique_ids if bid not in found_ids]`.
      - If `strict=True` and `missing_ids`:
```python
msg = f"Failed to batch resolve prompt blocks. Missing block IDs: {missing_ids}"
logger.error(
    "[PromptBlockRepo] %s: %s",
    ErrorCodes.RESOURCE_NOT_FOUND.name,
    msg,
    extra={
        "error_code": ErrorCodes.RESOURCE_NOT_FOUND.name,
        "missing_ids": missing_ids,
    },
)
raise AppException(
    message=msg,
    status_code=404,
    details={
        "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
        "missing_ids": missing_ids,
    },
)
```
      - Return hydrated `list[PromptBlock]`.
    </action>
    <constraint invariant="rfc7807_dual_reporting_mandate">Every AppException must be preceded by a structured logger.error call with error_code and contextual parameters.</constraint>
  </step>

  <step id="4" name="Define StrategyDependencies Container &amp; Update Strategy Base">
    <action>In @[backend_v2/services/orchestrator/strategies/base.py#L31-L54]:
      - Update `StrategyContext`:
```python
class StrategyContext(BaseModel):
    """Immutable context wrapper enforcing strict typing and Single Responsibility for node execution.

    Follows the V2 Architecture Service Boundary Doctrine: Strict IN -> Strict OUT.
    """

    execution_id: str
    workflow_id: str
    metadata: dict[str, Any]
    expected_inputs: list[ExpectedInput] | None = None
    model_strategy: str | None = None
    strictness_level: int = StrictnessAnchor.STANDARD.value
    global_context_vars: dict[str, Any] = Field(default_factory=dict)
    context_variables: dict[str, Any] = Field(default_factory=dict)
    prompt_blocks: list[PromptBlock] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True, extra="forbid")
```
      - Define `StrategyDependencies`:
```python
@dataclass(frozen=True)
class StrategyDependencies:
    """Immutable dependency container injected into execution strategies."""
    exec_repo: IExecutionRepository
    workflow_repo: IWorkflowRepository
    comp_repo: IComponentRepository
    prompt_block_repo: IPromptBlockRepository
    output_profile_repo: IOutputProfileRepository
    identity_repo: IIdentityRepository
    audit_repo: IAuditRepository
    system_repo: ISystemRepository
    prompt_compiler: Any
    arq_pool: Any | None = None
```
      - Update `NodeStrategy.__init__(self, deps: StrategyDependencies) -> None: self.deps = deps`.
      - Update helper methods `assert_quota`, `run_pre_hooks`, `run_post_hooks` to reference `self.deps.*`.
    </action>
    <action>In @[backend_v2/services/orchestrator/strategies/logic.py#L19-L176]:
      - Update `LogicNodeStrategy.__init__(self, deps: StrategyDependencies) -> None: super().__init__(deps=deps)`.
      - Update references `self.exec_repo` -> `self.deps.exec_repo`, `self.workflow_repo` -> `self.deps.workflow_repo`, `self.comp_repo` -> `self.deps.comp_repo`, `self.prompt_block_repo` -> `self.deps.prompt_block_repo`, `self.output_profile_repo` -> `self.deps.output_profile_repo`, `self.identity_repo` -> `self.deps.identity_repo`, `self.audit_repo` -> `self.deps.audit_repo`, `self.system_repo` -> `self.deps.system_repo`, `self.compiler` -> `self.deps.prompt_compiler`.
    </action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781]:
      - Update `LLMNodeStrategy.__init__(self, deps: StrategyDependencies, engine: ExecutionEngine | None = None) -> None: super().__init__(deps=deps); self._engine = engine`.
    </action>
    <demolish>REMOVE: 10-argument constructors in `NodeStrategy`, `LogicNodeStrategy`, and `LLMNodeStrategy` at @[backend_v2/services/orchestrator/strategies/base.py#L31-L54], @[backend_v2/services/orchestrator/strategies/logic.py#L19-L176], and @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781]. REPLACE WITH: `deps: StrategyDependencies`.</demolish>
    <constraint invariant="typed_dependency_container_mandate">Encapsulate multi-dependency groupings into an immutable @dataclass(frozen=True) container.</constraint>
  </step>

  <step id="5" name="Static NODE_STRATEGY_REGISTRY &amp; NodeStrategyFactory">
    <action>Create [NEW] @[backend_v2/services/orchestrator/strategies/registry.py]:
```python
import logging
from collections.abc import Callable
from typing import Protocol

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import StepType
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy

logger = logging.getLogger(__name__)


class StrategyBuilder(Protocol):
    """Protocol for building node strategy instances."""

    def __call__(
        self,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
    ) -> NodeStrategy: ...


def _build_logic_strategy(
    deps: StrategyDependencies,
    engine: ExecutionEngine | None = None,
) -> NodeStrategy:
    """Build a LogicNodeStrategy instance."""
    return LogicNodeStrategy(deps=deps)


def _build_llm_strategy(
    deps: StrategyDependencies,
    engine: ExecutionEngine | None = None,
) -> NodeStrategy:
    """Build an LLMNodeStrategy instance enforcing non-null engine."""
    if engine is None:
        msg = "LLMNodeStrategy requires a non-null ExecutionEngine instance."
        logger.error(
            "[NodeStrategyFactory] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
        )
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
    return LLMNodeStrategy(deps=deps, engine=engine)


NODE_STRATEGY_REGISTRY: dict[StepType, StrategyBuilder] = {
    StepType.LOGIC: _build_logic_strategy,
    StepType.LLM: _build_llm_strategy,
}


class NodeStrategyFactory:
    """Factory resolving node strategies via strict static registry mapping."""

    @staticmethod
    def create_strategy(
        step_type: StepType,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
    ) -> NodeStrategy:
        """Resolve and instantiate a NodeStrategy for the given StepType."""
        if step_type not in NODE_STRATEGY_REGISTRY:
            msg = f"Unsupported step type '{step_type}'. Must be registered in NODE_STRATEGY_REGISTRY."
            logger.error(
                "[NodeStrategyFactory] %s: %s",
                ErrorCodes.CONFIGURATION_ERROR.name,
                msg,
                extra={
                    "error_code": ErrorCodes.CONFIGURATION_ERROR.name,
                    "step_type": str(step_type),
                },
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={
                    "error_code": ErrorCodes.CONFIGURATION_ERROR.value,
                    "step_type": str(step_type),
                },
            )
        builder = NODE_STRATEGY_REGISTRY[step_type]
        return builder(deps=deps, engine=engine)
```
    </action>
    <constraint invariant="strategy_pattern_mandate">Replace branching business logic with declarative Enum-keyed dictionary registries populated eagerly.</constraint>
  </step>

  <step id="6" name="Atomic Unit Test Migration for Phase 1">
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py#L64-L99] and @[backend_v2/tests/unit/test_logic.py#L36-L64]: Update instantiations of `LogicNodeStrategy` to pass `deps = StrategyDependencies(...)`, and update mock return values for `workflow_repo`, `output_profile_repo` from raw dicts to typed Pydantic V2 models (`Step`, `Workflow`, `OutputProfile`).</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L148]: Remove stale mock patch line 60, remove `mock_get_settings` parameter, and update fixtures to `StrategyDependencies`.</action>
    <action>In @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py#L25-L35]: Add unit tests for `get_prompt_blocks_by_ids` covering happy-path batch resolution, empty input list fast-path, duplicate ID deduplication, strict single missing ID Fail-Fast, strict all missing IDs Fail-Fast, and non-strict partial return.</action>
    <action>In [NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]: Implement unit tests verifying `NODE_STRATEGY_REGISTRY` maps StepType.LOGIC -> `LogicNodeStrategy`, StepType.LLM (with engine) -> `LLMNodeStrategy`, raises `AppException` when StepType.LLM is called with `engine=None`, and raises `AppException` for unregistered step types.</action>
    <test_contracts>
      <test name="test_get_prompt_blocks_by_ids_success" category="positive">
        <input>block_ids=["blk_1", "blk_2"] in DB</input>
        <expected>returns list[PromptBlock] containing both models</expected>
      </test>
      <test name="test_get_prompt_blocks_by_ids_empty_list" category="boundary">
        <input>block_ids=[]</input>
        <expected>returns [] with 0 database queries</expected>
      </test>
      <test name="test_get_prompt_blocks_by_ids_duplicate_input" category="boundary">
        <input>block_ids=["blk_1", "blk_1"]</input>
        <expected>returns [blk_1] deduplicated</expected>
      </test>
      <test name="test_get_prompt_blocks_by_ids_strict_missing_single_raises_app_exception" category="error_path">
        <input>block_ids=["blk_1", "blk_missing"], strict=True</input>
        <expected>raises AppException(status_code=404, error_code=RESOURCE_NOT_FOUND, missing_ids=["blk_missing"])</expected>
      </test>
      <test name="test_get_prompt_blocks_by_ids_strict_missing_all_raises_app_exception" category="error_path">
        <input>block_ids=["blk_ghost_1", "blk_ghost_2"], strict=True</input>
        <expected>raises AppException(status_code=404, missing_ids=["blk_ghost_1", "blk_ghost_2"])</expected>
      </test>
      <test name="test_get_prompt_blocks_by_ids_non_strict_returns_partial" category="boundary">
        <input>block_ids=["blk_1", "blk_missing"], strict=False</input>
        <expected>returns [blk_1] without raising</expected>
      </test>
      <test name="test_node_strategy_registry_resolves_logic_strategy" category="positive">
        <input>step_type=StepType.LOGIC</input>
        <expected>returns LogicNodeStrategy instance</expected>
      </test>
      <test name="test_node_strategy_registry_resolves_llm_strategy" category="positive">
        <input>step_type=StepType.LLM with non-null ExecutionEngine</input>
        <expected>returns LLMNodeStrategy instance</expected>
      </test>
      <test name="test_node_strategy_registry_llm_without_engine_raises_app_exception" category="error_path">
        <input>step_type=StepType.LLM, engine=None</input>
        <expected>raises AppException(CONFIGURATION_ERROR)</expected>
      </test>
      <test name="test_node_strategy_registry_unregistered_type_raises_app_exception" category="error_path">
        <input>step_type="unregistered_type"</input>
        <expected>raises AppException(CONFIGURATION_ERROR)</expected>
      </test>
    </test_contracts>
    <constraint invariant="anti_happy_path_mandate">For every positive test case, write at least 2 negative/boundary test cases.</constraint>
  </step>

  <validation_gate>
    <action>Execute Strategy and Logic Unit Tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py backend_v2/tests/unit/test_logic.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py`</action>
    <action>Execute Prompt Block Repository Tests: `uv run pytest backend_v2/tests/unit/database/repositories/components/test_prompt_block.py`</action>
    <action>Execute Quality Loop: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/strategies backend_v2/tests/unit/test_logic.py --test`</action>
  </validation_gate>
</execution_protocol>
```
