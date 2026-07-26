# 02 Orchestration Plan

Source: Epic Phase 2 & Phase 4

## Target Files (Modify)
- `@[c:\src\quorum\backend_v2\models\dtos\engine.py]`
- `@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]`
- `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]`

## Execution Instructions

```xml
<execution_protocol>
  <execution_block phase="phase_2" consumer="tier2-execute">
    <summary><![CDATA[Orchestration, Registry & Prompt Compiler Updates]]></summary>
    <step id="phase_2.1" scope="MODIFY">
      <action>Update `EngineExecutionRequest` to accept `shuffled_atoms`. Add `shuffled_atoms: list[Any] | None = Field(default=None)` to the model to allow passing the predefined matrix atoms into the TDA engine without violating `extra="forbid"`.</action>
      <target>@[c:\src\quorum\backend_v2\models\dtos\engine.py]</target>
      <invariants>
        <constraint invariant="strict_pydantic_v2_rust">Models enforce ConfigDict(extra="forbid", strict=True, frozen=True).</constraint>
      </invariants>
      <tests min_negative="0">
        <positive>Verify engine.py compiles.</positive>
      </tests>
      <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/models/dtos/engine.py --test</audit_command>
    </step>
    <step id="phase_2.2" scope="MODIFY">
      <action>Pass the `shuffled_atoms` to the `EngineExecutionRequest` when the step is a matrix step. To enforce the **Fail-Fast Hydration Mandate**, use a `try...except KeyError` block around `state_data["shuffled_atoms"]` when `is_matrix_step` is True, and explicitly log and raise an `AppException(status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})` to prevent unhandled 500s. Pass this extracted list to the `EngineExecutionRequest` instantiations.</action>
      <target>@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]</target>
      <invariants>
        <constraint invariant="fail_fast_hydration_mandate">All uncertain data flowing as dictionaries MUST be hydrated via .model_validate() IMMEDIATELY before processing.</constraint>
        <constraint invariant="the_duct_tape_ban">Fix the root cause instead of patching symptoms. If data is malformed, let the system CRASH loudly via AppException.</constraint>
      </invariants>
      <tests min_negative="2">
        <positive>Verify llm.py compiles and integrates correctly</positive>
        <negative>Verify missing shuffled_atoms raises structured AppException</negative>
        <negative>Verify invalid shuffled_atoms type triggers Pydantic ValidationError downstream</negative>
      </tests>
      <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py --test</audit_command>
    </step>
    <step id="phase_2.3" scope="MODIFY">
      <action>Implement the **Context-Enriched Decompose-Verify Pipeline** in `TDAEngine.execute()`. If `request.shuffled_atoms` is present (Matrix path): execute Phase 0+1 to generate enriched context, construct `evaluation_context` using strict `<context>` XML boundaries, map the raw dictionaries in `request.shuffled_atoms` into `ExtractedAtom` models via `.model_validate()`, encapsulate them into `LinkedAtomGraph` nodes with empty `depends_on`, skip `SlidingWindowLinker`, and pass `evaluation_context` to `EnrichedDagExecutor.execute_graph()`. If `request.shuffled_atoms` is None (Regular path): preserve existing behavior.</action>
      <target>@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]</target>
      <invariants>
        <constraint invariant="zero_db_hardcoding_mandate">Logic MUST always be based on the abstract attributes, schema types... never by guessing based on magic strings.</constraint>
        <constraint invariant="alias_engine_llm_isolation_mandate">ALWAYS use the AliasEngine to generate short, semantic aliases before sending data to the LLM.</constraint>
        <constraint invariant="hybrid_prompting_mandate">System prompts MUST use a hybrid of XML for structural control and Markdown for nested content formatting.</constraint>
      </invariants>
      <tests min_negative="2">
        <positive>Verify EnrichedDagExecutor is called with mapped matrix atoms and enriched full_context</positive>
        <positive>Verify Regular TDA path uses SlidingWindowLinker unchanged</positive>
        <negative>Verify invalid shuffled_atoms structure triggers ExtractedAtom Pydantic ValidationError</negative>
        <negative>Verify missing tda_id triggers ExtractedAtom validation crash</negative>
      </tests>
      <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/services/orchestrator/engines/tda_engine.py --test</audit_command>
    </step>
  </execution_block>

  <execution_block phase="phase_4" consumer="tier2-execute">
    <summary><![CDATA[Verification & E2E Integration Gate]]></summary>
    <step id="phase_4.1" scope="VERIFY">
      <action>Run the full backend audit loop for all modified files to verify compilation and >90% test coverage. You MUST include the Final Live E2E REST API Verification Gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.</action>
      <target>@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]</target>
      <invariants>
        <constraint invariant="fragmented_quality_gates_prevention">You MUST enforce a Two-Stage Testing Pipeline to balance execution speed with global stability.</constraint>
      </invariants>
      <tests min_negative="0"/>
      <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines --test</audit_command>
    </step>
  </execution_block>
</execution_protocol>
```
