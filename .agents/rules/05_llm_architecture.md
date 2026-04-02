# 🚀 ANTIGRAVITY LLM & OUTPUT ARCHITECTURE CONSTRAINTS

<system_context>
    <domain>Large Language Model (LLM) Integration, Prompt Engineering, and Output Management</domain>
</system_context>

<catastrophic_system_bans>
    <rule_block id="direct_sdk_calls">
        <banned_pattern>Using `openai.ChatCompletion.create()` directly, calling Vertex AI SDK natively, or hardcoding model strings like "gpt-4" inside services.</banned_pattern>
        <mandatory_pattern>All LLM requests MUST strictly utilize the Model Registry via `LLMClient.from_strategy("strategy_name", repo)`. Follow the Zero-Fallback rule.</mandatory_pattern>
        <catastrophic_reason>Bypassing the Model Registry breaks token tracking, rate limiting, and centralized FinOps cost analysis.</catastrophic_reason>
    </rule_block>

    <rule_block id="data_leak_logging">
        <banned_pattern>Logging raw LLM payloads, user prompts (PII, Chat Data), or full Pydantic exception text blocks natively into logs.</banned_pattern>
        <mandatory_pattern>Enforce strict Data Leak Prevention (DLP). Log ONLY the mathematical/enumerated error code and Trace ID (e.g., `logger.error("Task failed", extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name})`).</mandatory_pattern>
        <catastrophic_reason>Logging Prompt logic and PII breaches data sovereignty contracts and poisons Cloud Logs with sensitive information.</catastrophic_reason>
    </rule_block>

    <rule_block id="infinite_retry_loops">
        <banned_pattern>Running generic self-healing retry pipelines with high `max_retries` causing infinite logic loops upon complex JSON schema mismatches.</banned_pattern>
        <mandatory_pattern>Enforce an absolute max stringency (`max_retries = 2`). If the AI Generator and AI Critic conflict, trigger Fail-Fast and push the error to the AppErrorBoundary.</mandatory_pattern>
        <catastrophic_reason>Infinite loops on failed prompt engineering will explode API billing exponentially within minutes.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="structured_sdui_outputs">
        <banned_pattern>Requesting unstructured Markdown formatting (e.g., `run_chat()`) and expecting the Flutter UI or PDF library to guess the visual layout.</banned_pattern>
        <mandatory_pattern>Mandate Zero-Math Templates via Pydantic. Use `run_structured_task()` to force the LLM to output strict Server-Driven UI (SDUI) visual block arrays (e.g., `HeroInsightBlock`, `DataGridBlock`).</mandatory_pattern>
    </rule_block>

    <rule_block id="two_tier_prompting">
        <banned_pattern>Hardcoding stylistic tone inside the Python backend code, OR conversely, storing rigid JSON layout schemas in the database where an admin UI can mistakenly break them.</banned_pattern>
        <mandatory_pattern>Enforce Structural Sovereignty: The stylistic rules (`tone_instruction`, `audience`) MUST be dynamically loaded from the Database. The rigid JSON mapping and schema validations MUST be locked permanently in the `prompt_compiler.py` code.</mandatory_pattern>
    </rule_block>

    <rule_block id="non_blocking_fastapi">
        <banned_pattern>Awaiting long `LLMClient` tasks, Text Consolidation Hooks, or PDF generation synchronously within a FastAPI router.</banned_pattern>
        <mandatory_pattern>LLM Workflows exceeding 500ms MUST be sent to the Arq background worker. Furthermore, you must include an "SSE-Heartbeat" pulse in the long-running worker to prevent Cloud Load Balancers from timing out the HTTP connection.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="role_segregation">
        <banned_pattern>Concatenating System rules and raw User Paste data into a single massive string inside the `user` role array.</banned_pattern>
        <mandatory_pattern>Always segregate `messages` strictly into `{"role": "system", "content": _SYSTEM_INSTRUCTION}` and `{"role": "user", "content": payload}`. This acts as a firewall against Prompt Injection and enables Anthropic Ephemeral Context Caching.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="internal_utility_llm_execution">
        <banned_pattern>Building ad-hoc LLM instances or placing core parsing instructions into dynamic variables / database fields for backend utilities like `chat_parser.py` or `translation_hook.py`.</banned_pattern>
        <mandatory_pattern>Non-workflow Internal LLM Utilities MUST execute as follows: 1) Load client via `await LLMClient.from_strategy("fast", repository=repo)`. 2) Define instructions as a file-level `_SYSTEM_INSTRUCTION` constant. 3) Pass strictly segregated messages to `run_chat(messages=...)` or `run_structured_task(messages=...)`.</mandatory_pattern>
    </rule_block>
</architectural_invariants>
