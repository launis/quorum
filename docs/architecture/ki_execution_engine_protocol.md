# ExecutionEngine Protocol & TDA Engine Extraction

<domain_boundary>
    <role>Execution Orchestration & Pipeline Decoupling</role>
    <architectural_invariants>
        1. **Protocol Adherence**: The `LLMNodeStrategy` must NOT contain inline pipeline logic (e.g., TDA phases). It must delegate all execution complexity to an injected class that implements the `ExecutionEngine` Protocol.
        2. **TDA Pipeline Abstraction**: The `TDAEngine` is the concrete implementation of the `ExecutionEngine` Protocol for Two-Pass Document Analysis. It encapsulates the Atomizer, Linker, EnrichedDagExecutor, and ResultProjector.
    </architectural_invariants>
</domain_boundary>

<catastrophic_system_bans>
    <rule_block id="inline_pipeline_ban">
        <banned_pattern>Writing multi-step pipeline logic (e.g., executing Phase 0, then Phase 1, then linking) directly inside the `LLMNodeStrategy.execute()` method.</banned_pattern>
        <mandatory_pattern>All multi-step pipelines MUST be extracted into a standalone `Engine` class (e.g., `TDAEngine`) that implements `ExecutionEngine`, and this engine must be lazily injected into the strategy via `dag_executor.py`.</mandatory_pattern>
        <catastrophic_reason>Inline pipelines violate the Open-Closed Principle, bloat the strategy class, and make unit-testing pipeline variations impossible.</catastrophic_reason>
    </rule_block>

    <rule_block id="engine_dto_strictness">
        <banned_pattern>Passing generic dicts, `**kwargs`, or untyped arguments into an execution engine.</banned_pattern>
        <mandatory_pattern>Engines MUST only accept an `EngineExecutionRequest` DTO and return an `EngineExecutionResult` DTO. Both DTOs must use `ConfigDict(strict=True)` to enforce Pydantic V2 type checking (e.g., ensuring `bound_client` is strictly an instance of `LLMClient`).</mandatory_pattern>
        <catastrophic_reason>Generic payloads circumvent the type-checker, leading to silent state corruption and missing required references during deep DAG execution.</catastrophic_reason>
    </rule_block>

    <rule_block id="engine_exception_acl">
        <banned_pattern>Allowing third-party exceptions (e.g., Anthropic API errors) or standard Python exceptions (e.g., `ValueError`) to bubble up directly from an engine to the DAG orchestrator.</banned_pattern>
        <mandatory_pattern>Engines MUST implement an Anti-Corruption Layer (ACL) that catches all internal exceptions and wraps them in a Quorum-compliant `AppException` (Status 500) before returning control to the strategy. Pre-existing `AppException`s must be re-raised transparently.</mandatory_pattern>
        <catastrophic_reason>Uncaught internal exceptions bypass the Fail-Fast mechanism and crash the DAG loop without properly updating the execution record's step status, causing permanently locked "zombie" executions in the UI.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>
