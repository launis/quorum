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

    <rule_block id="eager_llm_dependency_loading">
        <banned_pattern>Placing `import litellm`, `import vertexai` or other heavy PyO3/Rust-based LLM libraries at the module level (top of the file) in backend providers or handlers.</banned_pattern>
        <mandatory_pattern>Enforce Lazy Loading / Deferred Initialization: Heavy LLM SDK imports MUST be placed inside the specific functions/methods (e.g. `__init__`, `generate`) where they are actually invoked.</mandatory_pattern>
        <catastrophic_reason>Importing Rust-based libraries (like `tokenizers` via LiteLLM) at the module level permanently crashes Python 3.14+ test suites running with `pytest-cov` due to PyO3 multi-initialization constraints. Lazy loading guarantees test collection is safe and accelerates application boot times.</catastrophic_reason>
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
    <rule_block id="native_language_system_prompts">
        <banned_pattern>Writing core system instructions, rules, or system prompts in Finnish (e.g. `_SYSTEM_INSTRUCTION = "SÄÄNTÖ: ..."`).</banned_pattern>
        <mandatory_pattern>All system prompts MUST be strictly in English to ensure maximum compliance and instruction-following by the foundational models (Gemini/OpenAI).</mandatory_pattern>
        <catastrophic_reason>LLMs are primarily trained on English logic and instruction tuning. Providing complex constraints in Finnish significantly degrades the model's ability to follow strict architectural rules like JSON formatting or key preservation.</catastrophic_reason>
    </rule_block>

    <rule_block id="naked_prompt_injection">
        <banned_pattern>Appending raw string instructions to the prompt context dynamically without structural boundaries (e.g. `compiled += "\n\nCRITICAL MANDATE: ..."`).</banned_pattern>
        <mandatory_pattern>All dynamic prompt insertions MUST be cleanly separated using Markdown headers or explicit sections, allowing `prompt_compiler_adapter.py` to correctly structure them.</mandatory_pattern>
        <catastrophic_reason>Without structural boundaries, the LLM suffers from Attention Dilution and struggles to differentiate between source data, user intent, and absolute system constraints.</catastrophic_reason>
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
        <mandatory_pattern>You MUST fence untrusted user payloads using clear markdown blocks or relying on the structured compiler injection as a firewall against Prompt Injection.</mandatory_pattern>
        <code_example>
            <anti_pattern>{"role": "user", "content": f"Parse this: {user_text}"}</anti_pattern>
            <pro_pattern>{"role": "user", "content": f"Data:\n```\n{user_text}\n```"}</pro_pattern>
        </code_example>
    </rule_block>
    
    <rule_block id="internal_utility_llm_execution">
        <banned_pattern>Building ad-hoc LLM instances or placing core parsing instructions into dynamic variables / database fields for backend utilities like `chat_parser.py` or `translation_hook.py`.</banned_pattern>
        <mandatory_pattern>Non-workflow Internal LLM Utilities MUST execute as follows: 1) Load client via `await LLMClient.from_strategy("fast", repository=repo)`. 2) Define instructions as a file-level `_SYSTEM_INSTRUCTION` constant. 3) Pass strictly segregated messages to `executor.execute_chat_task(client=...)` or `executor.execute_structured_task(client=...)`.</mandatory_pattern>
    </rule_block>

    <rule_block id="xml_structural_sovereignty_mandate">
        <banned_pattern>Writing system prompts with soft Markdown headings (e.g., `### RULES`, `## OBJECTIVE`) when defining isolated architectural mandates in the backend or `seed_data.json`.</banned_pattern>
        <mandatory_pattern>Enforce the "XML Structural Sovereignty" mandate: wrap all distinct business logic rules and mandates in highly rigid, named XML tags (e.g. `<language_mandate>...</language_mandate>`). This provides mathematically optimal semantic boundaries for modern LLMs to process strict hierarchical logic, eliminating "Attention Dilution" risks.</mandatory_pattern>
        <code_example>
            <pro_pattern>
                _SYSTEM = """<system_directive>
                <objective>Extract data</objective>
                <rules>
                <rule>Be exact</rule>
                </rules>
                </system_directive>"""
            </pro_pattern>
        </code_example>
    </rule_block>

    <rule_block id="high_fidelity_prompting_and_caching">
        <banned_pattern>Injecting dynamic execution variables (like length constraints or target languages) directly into rule sentences using Python f-strings, or using Markdown mixed with raw text for data structures.</banned_pattern>
        <mandatory_pattern>Enforce **High-Fidelity Prompting & 100% Caching Efficiency**. All dynamic variables MUST be strictly isolated via the compiler's dynamic inputs system at the very beginning of the prompt. All rules and system directives must remain perfectly static. All input data must be rigidly separated. The usage of unstructured Markdown lists for dynamic data parsing is strictly forbidden.</mandatory_pattern>
        <catastrophic_reason>Mixing dynamic parameters with static system instructions destroys the LLM's Prompt Caching capability. Isolating variables ensures that 95%+ of the prompt remains cacheable, vastly reducing token costs and latency.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="llm_structured_execution_mandate">
        <banned_pattern>Asking LLM to "output valid JSON" in text and parsing it with Regex/json.loads, using LLMClient to handle validation retry loops directly, using manual syntactic self-healing, or using the fallback `"parsing_mode": "STRUCTURED_JSON"` in output profiles.</banned_pattern>
        <mandatory_pattern>Rely ONLY on `LLMTaskExecutor.execute_structured_task()` to force execution via Native Structured Outputs API (e.g., passing Pydantic schema to `response_schema`). Syntactic self-healing loops MUST be completely removed from the codebase. The fallback mode `STRUCTURED_JSON` is BANNED because it degrades API-level constrained decoding into text-based schema instructions, allowing the model to hallucinate forbidden keys and break Pydantic's `extra="forbid"` rule.</mandatory_pattern>
        <code_example>
            <anti_pattern>data = json.loads(await client.run_chat(prompt))</anti_pattern>
            <pro_pattern>result, usage = await executor.execute_structured_task(client=client, messages=messages, response_model=UserDTO)</pro_pattern>
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

    <rule_block id="cognitive_dampening_square_root_model">
        <banned_pattern>Using hardcoded artificial floors (like `DINA_FLOOR`) or brutal linear multiplication to calculate cascading Cognitive Diagnostic Model (CDM) scores.</banned_pattern>
        <mandatory_pattern>Enforce Square Root Dampening. The hierarchical energy flow modifier MUST be softened natively using `modifier = modifier * math.sqrt(hit_rate)`. This mathematics guarantees natural Gaussian curves and ensures Absolute Zero (Fail-Fast) bypasses are perfectly organic.</mandatory_pattern>
        <catastrophic_reason>Pure linear multiplication decays probabilities exponentially, artificially crushing all real-world variance into absolute 0. This forces bad architectural practices like arbitrary UX 'leniency floors', corrupting the integrity of the math.</catastrophic_reason>
    </rule_block>
    <rule_block id="strict_physical_anchoring_mandate">
        <banned_pattern>Using fuzzy string matching (e.g., `RapidFuzz` or `fuzz.partial_ratio`) to validate LLM evidence extraction.</banned_pattern>
        <mandatory_pattern>Enforce strict, deterministic `O(N)` physical anchoring using `str.find` on normalized strings. If an exact lexical match is not found in the original source document, the extraction MUST immediately trigger a Fail-Fast `SemanticEvidenceError`.</mandatory_pattern>
        <catastrophic_reason>Fuzzy matching introduces unacceptable variance and allows the LLM to successfully hallucinate pseudo-quotes that sound similar but do not physically exist in the source, destroying the Single Source of Truth (SSOT) guarantee.</catastrophic_reason>
    </rule_block>

    <rule_block id="ensemble_parallel_evaluation_mandate">
        <banned_pattern>Using multi-pass "negative rules" logic or chained sequential verifications for high-entropy / inverse-evidence PromptBlocks.</banned_pattern>
        <mandatory_pattern>Execute high-entropy and negative validation steps using a single-pass "Best-of-3" ensemble. You MUST run parallel LLM calls cleanly wrapped in `asyncio.TaskGroup` and resolve the final output via a strict majority vote where lexically invalid hallucinations are discarded before counting.</mandatory_pattern>
        <catastrophic_reason>Multi-pass negative logic forces the LLM into "double-negative" confusion, causing severe output oscillation. Parallel Best-of-3 polling mathematically smooths statistical anomalies without convoluting the system prompts.</catastrophic_reason>
    </rule_block>
    <rule_block id="strict_xml_prompt_formatting">
        <banned_pattern>Using arbitrary ASCII separators (like `=== RULES ===`) or soft Markdown headings for critical logic constraints inside prompt models.</banned_pattern>
        <mandatory_pattern>All distinct business logic, rules, and mandates MUST be written using explicit XML boundaries (e.g., `<language_mandate>...</language_mandate>`). Markdown can still be used inside the XML block for readability, but the absolute outer boundary of a rule MUST be an XML tag.</mandatory_pattern>
        <catastrophic_reason>Without XML tag boundaries, LLMs suffer from "Attention Dilution" and can accidentally bleed the context of one rule into another.</catastrophic_reason>
    </rule_block>

    <rule_block id="prompt_asset_ssot_mandate">
        <banned_pattern>Hardcoding system instructions, language translation directives (like `<linguistic_context>`), or Pydantic JSON schema descriptions directly into service layer classes (e.g., `PromptFactory`, `translation_service.py`, or `schema_factory.py`).</banned_pattern>
        <mandatory_pattern>Enforce strict Single Source of Truth (SSOT) for all Prompt Assets. The `backend_v2/models/prompts` directory is the ONLY allowed location for defining static prompt blocks, XML mandates, and schema descriptions. Prompt factories and orchestrators MUST ONLY import and inject these pre-defined assets. They must never construct structural XML rules dynamically in the service layer.</mandatory_pattern>
        <catastrophic_reason>Dispersing prompt instructions across the codebase breaks the Separation of Concerns, makes the system prompt un-auditable, and leads to orphaned or duplicated mandates (like stray XML tags without their corresponding rules) which actively degrades the LLM's logic adherence.</catastrophic_reason>
    </rule_block>
    <rule_block id="atom_aliasing_hydration_mandate">
        <banned_pattern>Passing raw system UUIDs (like `tda_131ffcb70bbc4c29bef079047002bc91` or `blk_...`) directly to the LLM to use as keys or output values for structured evaluations (including Shuffled Atoms and Atom Graphs), OR using regex laastari for hydration.</banned_pattern>
        <mandatory_pattern>Enforce **The Alias Engine & Hydration Mandate**. The LLM MUST ONLY be exposed to short, deterministic aliases (e.g., `a0`, `a1` for atoms, `src_0`, `src_1` for source documents) to act as "Attention Anchors". You MUST use the dedicated `AliasEngine` module (`alias_engine.py`) to handle both the obfuscation injection (translating long UUIDs to aliases before prompt injection) and the hydration phase (translating aliases back to true Opaque IDs during Pydantic validation via context). This guarantees token optimization, prevents hallucinatory typos on primary keys, and centralizes aliasing logic for Epic 92.</mandatory_pattern>
        <catastrophic_reason>Forcing the LLM to juggle dozens of 32-character hashes destroys its ability to track relationships in complex dependency graphs (Epic 92), consumes massive token budgets unnecessarily, and risks database corruption via 1-character hallucination typos.</catastrophic_reason>
    </rule_block>
    <rule_block id="provider_abstraction_mandate">
        <banned_pattern>Hardcoding provider-specific hacks (like HTTPX custom wrappers, `cachedContent` body mappings, or `vertex_location` priority logic) directly into the `LiteLLMProvider` class (`provider.py`).</banned_pattern>
        <mandatory_pattern>All model- and operator-specific anomalies, logic variations, and HTTP client customizations MUST be encapsulated in their respective `BaseLLMAdapter` implementations under `backend_v2/llm/adapters/`. The `LiteLLMProvider` MUST remain a clean, pristine orchestrator.</mandatory_pattern>
        <catastrophic_reason>Allowing provider-specific logic to bleed into the global orchestrator creates a bloated God Class, making it impossible to add new models (Anthropic, OpenAI) without breaking existing, fragile conditional branches. It violates the Open/Closed Principle.</catastrophic_reason>
    </rule_block>

    <rule_block id="local_prompt_debugging_mandate">
        <banned_pattern>Attempting to debug token explosions, JSON schema extraction failures, or model hallucinations solely by guessing or staring at Logfire cloud traces without reviewing the exact constructed XML payload.</banned_pattern>
        <mandatory_pattern>In `development` environments, the backend automatically generates a comprehensive `llm_debug_prompts.md` for every execution step inside `data/files/executions/<execution_id>/`. When resolving LLM hallucination or latency (e.g. 50-second generation times) issues, you MUST proactively use `view_file` to read this markdown file. It contains the precise `Prompt Source Blocks` (e.g. `blk_...` IDs) and the exact `User Payload` (including payload size and expected Pydantic schema name) that caused the anomaly, allowing surgical database corrections rather than trial and error.</mandatory_pattern>
    </rule_block>
</architectural_invariants>
