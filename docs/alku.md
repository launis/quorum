# COGNITIVE QUORUM - ANTIGRAVITY SYSTEM BOOTSTRAP (V5.1)

## TO THE AI AGENT:
You are operating within the **Cognitive Quorum** monorepo (Python 3.14+ Backend, Flutter/Riverpod Client). This is a highly mature **Phase 9 Hardening** environment built on strict **Clean Architecture**.

Your operational mandate is to strictly enforce pre-established architectural laws. Do not invent new patterns. Do not guess.

### 1. INITIALIZATION PROTOCOL (MUST DO FIRST)
1. **Check KI Summaries**: You have access to Knowledge Items (KIs). **ALWAYS** scan them first for architectural patterns before writing implementation plans.
2. **Read the Core Architecture**: You **MUST** read and interpret the `docs/structured_cognitive_architecture.md`, `docs/architecture.md`, and `docs/components.md` files to understand the data flows, the "Air Gap", and how agents/hooks operate deterministically.
3. **Read Data Management**: Read `docs/data_management.md`.
4. **Read the Manifesto**: Read `docs/flutterpromptohje.md`. It defines banned legacy patterns, the Zero-Compromise Pledge, and the exact Python/Flutter strict mandates.
5. **Read the V2 Master Plan (SUPREME LAW)**: Read `docs/Flutter Frontend V2 Suunnitelma.md`. **CRITICAL:** This document defines the ultimate source of truth for the architecture (Enterprise V2). **If there are any disagreements between this document and any other document (including flutterpromptohje.md or KIs), `docs/Flutter Frontend V2 Suunnitelma.md` strictly dictates the rules.**
6. **Verify via Logs**: Use your terminal capabilities (`get-content backend_debug.log`, `pytest`) before making assumptions about crashes.

### 2. CORE ARCHITECTURAL LAWS (LINK LIST & MANDATES)
These are absolute, non-negotiable rules. If you break these, the system will fail.

* **[System Architecture](architecture.md) & [Structured Cognitive Architecture](structured_cognitive_architecture.md)**: "Zero-Magic", Strict DTOs, RFC 7807 Fail Fast error handling, and the Fused Panel architecture.
* **[Components & Hooks](components.md)**: Read how agents return Pydantic DTOs and how deterministic hooks use `AppException` without fallback.
* **[Backend Mandates](STRICT MANDATES & ARCHITECTURE PRINCIPLES.md)**: Python 3.14+, FastAPI, SSOT (`seed_data.json`), Service/Repository layers, Pydantic `extra="ignore"`. 
* **[Frontend Mandates](STRICT FRONTEND MANDATES & ARCHITECTURE PRINCIPLES.md)**: Riverpod 3.0, Matrix UI Approach, SDUI (Server-Driven UI) Graceful Degradation.
  * **Routing**: Only `GoRouteData` type-safe routes allowed. No string-based `context.go()`.
  * **I18N No-String Mandate**: UI translations happen ONLY in `.arb` files using ICU syntax. Zero backend translations, zero Dart string concatenations.
* **[API Models & SDUI](api_models.md)**: The Backend provides data and enums. The Frontend provides presentation and translation.
* **[System Architecture Manifesto](flutterpromptohje.md)**: Contains the 10-chapter master ruleset covering Pre-Flight Dependencies, the Zero-Compromise fail-fast boundary, Data Lifecycle, and the Hybrid  SDUI contracts.
* **[Enterprise V2 Master Architecture (SUPREME LAW)](Flutter Frontend V2 Suunnitelma.md)**: **The absolute supreme architectural law for V2.** Overrides all other documents in case of conflicts. It defines Zero-Deploy, Schema-Driven AI, Omni-Channel Rendering, Late-Binding SDUI, and Cognitive Multilingualism.

### 3. YOUR WORKFLOW
1. **Analyze**: Use `grep_search` and `find_by_name` to map the codebase.
2. **Plan**: Write your step-by-step strategy to `implementation_plan.md` and use the `notify_user` tool to request my approval for structural changes.
3. **Execute & Test**: Write the code, run standard tests (`pytest backend/tests/`, `flutter analyze`), and ensure 0 regressions.

### 4. SUMMARY OF PLEDGES (ACKNOWLEDGE THESE)
When acknowledging these instructions, you must explicitly mention and confirm that you understand the following core principles:
1. **The Strict DTO Pattern & Schema-Driven AI**: I understand that LLM responses are received purely as DTOs (dynamic Pydantic schemas created on the fly), and metadata is always injected purely by Python code.
2. **Fail-Fast Protocol & Zero-Fallback**: I understand that missing or malformed data is never patched by guessing (no `try-except pass`). Instead, the system must crash and return an RFC 7807 standardized `AppException`.
3. **Courtroom 3.0 (Fused Panel & Fan-Out)**: I understand that critics are executed as a single massive LLM call (PanelAgent), whose response the Engine then distributes into individual keys within the Blackboard state.
4. **Database SSOT Synchronization**: I understand that there is a static CI/CD dependency between the `seed_data.json` configurations and the Python Pydantic models, and I will not modify models without ensuring their linkage aligns.
5. **3-Tier Grounding & Theory-Grounded XAI**: I understand the layers and constraints of information retrieval, and that the LLM is forced to provide numeric scores and multi-lingual justifications grounded strictly in dynamically injected theories.
6. **Late-Binding Omni-Channel SDUI**: I understand that the Backend only returns unified UI hints (`ui_hints_snapshot`) and raw results. The presentation layer (Flutter, PDF, Flat File) handles rendering blindly based on these hints.
7. **V2 Architecture Supremacy**: I understand that `docs/Flutter Frontend V2 Suunnitelma.md` is the ultimate source of truth, and its rules ALWAYS override any conflicting information in other documents.

**CONFIRMATION:**
Before you begin, read `docs/structured_cognitive_architecture.md`, `docs/data_management.md`, `docs/architecture.md`, `docs/components.md`, `docs/flutterpromptohje.md` and especially `docs/Flutter Frontend V2 Suunnitelma.md` carefully.
Then, reply by acknowledging the 7 safety and rule pillars above, and ask: "Understood. Antigravity V5.1/V2 rules loaded. What is the objective of this session?"
