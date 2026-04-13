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
        <mandatory_pattern>Enforce an absolute max stringency using `SystemConcurrency.LLM_MAX_RETRIES` (which MUST be fixed at 2). If the AI Generator and AI Critic conflict, trigger Fail-Fast and push the error to the AppErrorBoundary.</mandatory_pattern>
        <catastrophic_reason>Infinite loops on failed prompt engineering will explode API billing exponentially within minutes.</catastrophic_reason>
    </rule_block>

    <rule_block id="system_concurrency_ssot">
        <banned_pattern>Hardcoding parallel task limits (e.g. semaphores, iterators) and retry limits scattered across files, ignoring global constraints.</banned_pattern>
        <mandatory_pattern>All execution limits MUST reference `SystemConcurrency` strictly. Parallel async LLM workers must wrap execution in a TaskGroup limited natively by `asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS)` (fixed at 2). Hardcoded or arbitrary new limits are banned.</mandatory_pattern>
        <catastrophic_reason>Fractured limits allow exponential concurrent API triggers, resulting in instant Cloud Rate Limits (HTTP 429) and quota exhaustion across the entire infrastructure.</catastrophic_reason>
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
    
    <rule_block id="role_segregation_and_fencing">
        <banned_pattern>Passing unescaped user inputs directly into prompts.</banned_pattern>
        <mandatory_pattern>You MUST fence untrusted user payloads inside explicit XML tags (e.g., `<user_payload>...</user_payload>`) as a firewall against Prompt Injection.</mandatory_pattern>
        <code_example>
            <anti_pattern>{"role": "user", "content": f"Parse this: {user_text}"}</anti_pattern>
            <pro_pattern>{"role": "user", "content": f"Data:\n<user_payload>\n{user_text}\n</user_payload>"}</pro_pattern>
        </code_example>
    </rule_block>
    
    <rule_block id="internal_utility_llm_execution">
        <banned_pattern>Building ad-hoc LLM instances or placing core parsing instructions into dynamic variables / database fields for backend utilities like `chat_parser.py` or `translation_hook.py`.</banned_pattern>
        <mandatory_pattern>Non-workflow Internal LLM Utilities MUST execute as follows: 1) Load client via `await LLMClient.from_strategy("fast", repository=repo)`. 2) Define instructions as a file-level `_SYSTEM_INSTRUCTION` constant. 3) Pass strictly segregated messages to `run_chat(messages=...)` or `run_structured_task(messages=...)`.</mandatory_pattern>
    </rule_block>

    <rule_block id="hybrid_prompting_mandate">
        <banned_pattern>Writing flat, unstructured strings for system prompts.</banned_pattern>
        <mandatory_pattern>All system prompts MUST use "Hybrid Prompting" (XML tags inside Markdown) to define semantic boundaries.</mandatory_pattern>
        <code_example>
            <pro_pattern>
                _SYSTEM = """<system_directive>
                <objective>Extract data</objective>
                <rules><rule>Be exact.</rule></rules>
                </system_directive>"""
            </pro_pattern>
        </code_example>
    </rule_block>
    
    <rule_block id="llm_structured_execution_mandate">
        <banned_pattern>Asking LLM to "output valid JSON" in text and parsing it with Regex/json.loads.</banned_pattern>
        <mandatory_pattern>Rely ONLY on `run_structured_task()` to force execution via API native Structural Constraining (e.g. OpenAI Structured Outputs).</mandatory_pattern>
        <code_example>
            <anti_pattern>data = json.loads(await client.run_chat(prompt))</anti_pattern>
            <pro_pattern>result: UserDTO = await client.run_structured_task(messages, response_model=UserDTO)</pro_pattern>
        </code_example>
    </rule_block>

    <rule_block id="ai_bloatware_ban">
        <banned_pattern>Proposing frameworks like `langchain`, `llamaindex`, or `crewai`.</banned_pattern>
        <mandatory_pattern>AI logic MUST remain strictly in our native `LLMClient` wrapper. Complex orchestrations MUST use Python async patterns and Pydantic.</mandatory_pattern>
    </rule_block>

    <rule_block id="ephemeral_caching_topology">
        <banned_pattern>Injecting dynamic variables (timestamps, UUIDs) into `_SYSTEM_INSTRUCTION`.</banned_pattern>
        <mandatory_pattern>To maximize Context Caching (FinOps), the System Prompt MUST be 100% static. ALL dynamic data MUST be injected exclusively into the `user` message at the end.</mandatory_pattern>
    </rule_block>

    <rule_block id="native_english_generation_mandate">
        <banned_pattern>Prompting the LLM to simultaneously generate complex analytical texts (like hypotheses or markdown syntheses) and translate them into a non-English target language in a single pass.</banned_pattern>
        <mandatory_pattern>Enforce Native English Strategy: High-cognitive tasks MUST be generated natively in English to preserve reasoning depth and "cognitive friction". The robust output MUST then be intercepted (e.g., via `backend_v2.hooks.translation_hook`) and translated into the user's target language in a subsequent low-latency pass.</mandatory_pattern>
        <catastrophic_reason>Generating complex logic natively in non-English languages severely reduces the LLM's analytical capacity, forcing it to split token computation between linguistic grammar and structural reasoning, causing "intelligence dropping".</catastrophic_reason>
    </rule_block>
</architectural_invariants>
