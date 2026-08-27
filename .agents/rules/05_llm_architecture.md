---
trigger: always_on
---

# ANTIGRAVITY LLM & OUTPUT ARCHITECTURE CONSTRAINTS

<domain_boundary>
    <role>LLM ORCHESTRATION & PROMPT COMPILATION</role>
    <instruction>These rules govern the EXACT mechanics of how you instruct foundational models, parse structured JSON, and protect prompts against injection. These rules MUST be applied when working inside `backend_v2/llm/` or `services/` involving AI execution.</instruction>
</domain_boundary>

<system_context>
    <domain>Large Language Model (LLM) Integration, Prompt Engineering, and Output Management</domain>
</system_context>

<catastrophic_system_bans>
    <rule_block id="direct_sdk_calls">
        <mandate>NEVER use `openai.ChatCompletion.create()` directly, call Vertex AI SDK natively, or hardcode model strings ("gpt-4") inside services. ALL LLM requests MUST strictly utilize the Model Registry via `LLMClient.from_strategy("strategy_name", repo)` (Zero-Fallback rule).</mandate>
    </rule_block>

    <rule_block id="eager_llm_dependency_loading">
        <mandate>NEVER place `import litellm`, `import vertexai`, or heavy PyO3/Rust-based LLM libraries at module level without `TYPE_CHECKING` guards. Enforce Lazy Loading: import heavy SDKs inside specific methods (`__init__`, `generate`). For typing, use `if typing.TYPE_CHECKING:` combined with `from __future__ import annotations` or string-based type hints.</mandate>
    </rule_block>

    <rule_block id="data_leak_logging">
        <mandate>NEVER log raw LLM payloads, user prompts (PII, Chat Data), or full Pydantic exception blocks into logs. Enforce strict Data Leak Prevention (DLP): log ONLY mathematical/enumerated error codes and Trace IDs (`logger.error("Task failed", extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name})`).</mandate>
    </rule_block>

    <rule_block id="infinite_retry_loops">
        <mandate>NEVER run generic self-healing retry pipelines with high `max_retries`. Enforce absolute max stringency using SSOT config (`settings.llm_max_retries`). If AI Generator and Critic conflict, trigger Fail-Fast and push errors to AppErrorBoundary.</mandate>
    </rule_block>

    <rule_block id="system_concurrency_ssot">
        <mandate>NEVER hardcode parallel task limits or share the same Semaphore instance recursively. All global limits MUST reference `settings.py` SSOT. Enforce Two-Tier Semaphore Architecture: Macro-level workers use a dedicated Job Semaphore (`settings.max_concurrent_jobs`), while `LLMClient` natively manages its own isolated Request Semaphore (`settings.max_concurrent_llm_steps`).</mandate>
    </rule_block>

    <rule_block id="native_language_system_prompts">
        <mandate>NEVER write core system instructions, rules, or system prompts in Finnish (`_SYSTEM_INSTRUCTION = "SÄÄNTÖ: ..."`). ALL system prompts MUST be strictly in English for maximum model instruction adherence.</mandate>
    </rule_block>

    <rule_block id="naked_prompt_injection">
        <mandate>NEVER append raw string instructions dynamically without structural boundaries. ALL dynamic prompt insertions MUST be cleanly separated using Markdown headers or explicit XML sections via `prompt_compiler_adapter.py`.</mandate>
    </rule_block>
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="structured_sdui_outputs">
        <mandate>NEVER request unstructured Markdown formatting (`run_chat()`) and expect client/PDF layers to guess layouts. Mandate Zero-Math Templates via Pydantic: use `run_structured_task()` to force LLMs to output strict SDUI visual block arrays (`HeroInsightBlock`, `DataGridBlock`).</mandate>
    </rule_block>

    <rule_block id="two_tier_prompting">
        <mandate>NEVER hardcode stylistic tone inside backend Python code or store rigid JSON layout schemas in the database. Enforce Structural Sovereignty: stylistic rules (`tone_instruction`, `audience`) MUST be dynamically loaded from DB, while rigid JSON schemas MUST be locked in `prompt_compiler.py`.</mandate>
    </rule_block>

    <rule_block id="non_blocking_fastapi">
        <mandate>NEVER await long `LLMClient` tasks (>500ms), Text Consolidation Hooks, or PDF generation synchronously in FastAPI routers, and NEVER send HTTP/SSE responses directly from Arq workers. Offload to Arq background workers. Routers maintain client connection via SSE emitting heartbeat pulses while waiting for worker completion (via Redis PubSub); workers publish state updates to Redis only.</mandate>
    </rule_block>
    
    <rule_block id="role_segregation_and_fencing">
        <mandate>NEVER pass unescaped user inputs directly into prompts or rely solely on Markdown fences. ALL raw user input MUST be XML-escaped (`<` to `&lt;`, `>` to `&gt;`) and wrapped in `<user_payload>` blocks as a bulletproof firewall against prompt injection.</mandate>
    </rule_block>
    
    <rule_block id="internal_utility_llm_execution">
        <mandate>NEVER build ad-hoc LLM instances or place core parsing instructions in dynamic DB fields for backend utilities (`chat_parser.py`, `translation_hook.py`). Internal LLM Utilities MUST: 1) Load client via `await LLMClient.from_strategy("fast", repository=repo)`, 2) Define instructions as file-level `_SYSTEM_INSTRUCTION` constant, 3) Execute via `executor.execute_chat_task()` or `executor.execute_structured_task()`.</mandate>
    </rule_block>

    <rule_block id="xml_structural_sovereignty_mandate">
        <mandate>NEVER write system prompts with soft Markdown headings (`### RULES`) when defining isolated mandates. Enforce XML Structural Sovereignty: wrap distinct business logic rules and mandates in rigid, named XML tags (e.g. `<language_mandate>...</language_mandate>`).</mandate>
    </rule_block>

    <rule_block id="high_fidelity_prompting_and_caching">
        <mandate>NEVER inject dynamic variables into rule sentences using f-strings or use unstructured Markdown lists for data. Enforce High-Fidelity Prompting & 100% Caching Efficiency: isolate all dynamic variables at the tail (user message) and keep all rules and system directives 100% static as an unbroken, cacheable prefix.</mandate>
    </rule_block>
    
    <rule_block id="llm_structured_execution_mandate">
        <mandate>NEVER ask LLMs to "output valid JSON" in text and parse with Regex/`json.loads`, use manual syntactic self-healing loops, or use `"parsing_mode": "STRUCTURED_JSON"`. Rely ONLY on `LLMTaskExecutor.execute_structured_task()` to force execution via Native Structured Outputs API (passing Pydantic schema to `response_schema`).</mandate>
    </rule_block>

    <rule_block id="ai_bloatware_ban">
        <mandate>NEVER propose heavy frameworks like `langchain`, `llamaindex`, or `crewai`. AI logic MUST remain strictly in our native `LLMClient` wrapper using native Python async patterns and Pydantic.</mandate>
    </rule_block>

    <rule_block id="ephemeral_caching_topology">
        <mandate>NEVER inject dynamic variables (timestamps, UUIDs) into `_SYSTEM_INSTRUCTION`. System Prompts MUST be 100% static to maximize Context Caching; ALL dynamic data MUST be injected exclusively into the `user` message at the tail.</mandate>
    </rule_block>

    <rule_block id="native_english_generation_mandate">
        <mandate>NEVER prompt LLMs to simultaneously generate complex analytical reasoning and translate into a non-English target language in a single pass. High-cognitive tasks MUST be generated natively in English and translated into target languages in a subsequent low-latency pass (e.g. `translation_hook`).</mandate>
    </rule_block>

    <rule_block id="cognitive_dampening_square_root_model">
        <mandate>NEVER use hardcoded artificial floors (`DINA_FLOOR`) or brutal linear multiplication for CDM scores. Enforce Square Root Dampening: soften hierarchical energy flow modifiers via `modifier = modifier * math.sqrt(hit_rate)`.</mandate>
    </rule_block>

    <rule_block id="strict_physical_anchoring_mandate">
        <mandate>NEVER use fuzzy string matching (RapidFuzz, regex, Levenshtein) as ANY part of validation for evidence extraction (strictly prohibited to prevent Chimera quotes). Enforce EXACT Lexical Validation: 1) Primary & Only Gate: `str.find` on normalized strings (accept immediately on exact match), 2) If `str.find` fails, raise `SemanticEvidenceError` (Pre-flight non-forensic exception: RapidFuzz allowed only for performative pattern detection in `linguistics.py`).</mandate>
    </rule_block>

    <rule_block id="ensemble_parallel_evaluation_mandate">
        <mandate>NEVER use multi-pass negative rules logic or wrap Best-of-3 calls in parent worker semaphores. Execute high-entropy validation steps using a single-pass "Best-of-3" voting ensemble across parallel LLM calls cleanly wrapped in `asyncio.TaskGroup`. `LLMClient` router manages micro-concurrency queuing safely decoupled from parent Job Semaphores.</mandate>
    </rule_block>

    <rule_block id="prompt_asset_ssot_mandate">
        <mandate>NEVER hardcode system instructions, language directives (`<linguistic_context>`), or schema descriptions in service classes (`PromptFactory`, `translation_service.py`). Enforce SSOT: `backend_v2/models/prompts` is the ONLY allowed location for defining static prompt blocks, XML mandates, and schema descriptions.</mandate>
    </rule_block>

    <rule_block id="atom_aliasing_hydration_mandate">
        <mandate>NEVER pass raw system UUIDs (`tda_...`, `blk_...`) directly to LLMs or hydrate aliases inside Pydantic validators on UUID fields. ALWAYS expose short, deterministic aliases (`a0`, `a1`, `src_0`) via `AliasEngine` (`alias_engine.py`) as Attention Anchors. Hydrate aliases manually in Python service layer AFTER LLM output is parsed into a temporary string DTO (via `AliasEngine.build_atom_ids_literal()`).</mandate>
    </rule_block>

    <rule_block id="provider_abstraction_mandate">
        <mandate>NEVER hardcode provider-specific hacks (HTTPX custom wrappers, `cachedContent` body mappings, `vertex_location` logic) in `LiteLLMProvider` (`provider.py`). Encapsulate all model- and operator-specific logic in `BaseLLMAdapter` implementations under `backend_v2/llm/adapters/`.</mandate>
    </rule_block>

    <rule_block id="local_prompt_debugging_mandate">
        <mandate>NEVER debug token explosions or hallucinations solely by guessing cloud traces. In `development`, inspect `llm_debug_prompts.md` in `data/files/executions/<execution_id>/`. Use `grep_search` first, then bounded `view_file` (`StartLine`/`EndLine`) to examine Prompt Source Blocks and User Payloads.</mandate>
    </rule_block>

    <rule_block id="compiler_xml_sovereignty_mandate">
        <mandate>NEVER author, edit, or store raw XML tags (`<system_directive>`, `<guidelines>`) in seed data or UI prompt inputs. Raw prompt blocks and persona texts MUST contain unadorned natural language; structural XML framing MUST be generated exclusively just-in-time by `prompt_compiler.py`.</mandate>
    </rule_block>

    <rule_block id="four_layer_clean_stack_hierarchy">
        <mandate>ALL LLM prompts MUST be compiled through the Four-Layer Clean Stack hierarchy:
        1. **Layer 1: Static System Directives & Mandates** (Static prefix for context caching),
        2. **Layer 2: Theory Grounding & Epistemic Context** (Academic references in `<theory_context>`),
        3. **Layer 3: Matrix Objective & Extraction Protocol** (Step-level extraction behavior),
        4. **Layer 4: Dynamic User Payload & Execution Variables** (Runtime text payloads, atom aliases, and dynamic inputs at tail).</mandate>
    </rule_block>
</architectural_invariants>
