# System Context & Core Invariants

## 1. Executive Summary
The **System Context & Core Invariants** capability forms the foundational constitution of the Compound AI System. It establishes the absolute architectural invariants that govern how all other components (Backend, Frontend, LLM Engine) must behave. This capability exists to ensure **Forensic Sovereignty**, deterministic execution, and the total eradication of silent failures, LLM hallucinations, and undocumented state mutations.

## 2. Architectural Principles & Invariants

Quorum operates on strict structural boundaries, deterministic execution, and end-to-end auditability:

### 2.1. Universal Fail-Fast & Strict Schema Validation
All data crossing system boundaries is strictly validated against immutable schemas (Pydantic V2 in Python, Freezed in Dart). Fallback chains, silent error absorption, and duct-tape workarounds are eliminated. If data is missing, malformed, or an expected state is not reached, the system halts immediately with an explicit `AppException` on the backend or renders an `AppErrorBoundary` on the client. Masking errors by returning empty arrays or hiding UI widgets is strictly prohibited.

### 2.2. Zero Permissive Typing & Dot-Notation Transit
All domain, service, orchestrator, and hook layers enforce 100% typed transit using immutable Pydantic V2 DTOs configured with `ConfigDict(strict=True, extra="forbid", frozen=True)`. Naked dictionaries (`dict[str, Any]`, `list[dict]`, `TypedDict`), permissive type coercions (`cast(Any, ...)`), structural duck-typing (`isinstance(data, dict)`), dictionary pattern matching, and permissive model configurations (`extra="allow"`, `extra="ignore"`) are eliminated. Downstream services access attributes exclusively via static dot-notation (`model.property`). Dynamic dictionary indexing, two-argument fallback lookups (`dict.get("key", default)`), lazy default fallback operators (`a or "default"`), and runtime reflection (`getattr()`, `hasattr()`, `setattr()`) are prohibited. Raw dictionary conversions are confined strictly to external HTTP and low-level persistence driver boundaries via explicit validation and dump calls.

### 2.3. Encapsulation of Multi-Field State (Anti-Tuple Architecture)
All multi-field return states and pipeline intermediate payloads are encapsulated into dedicated, immutable Pydantic V2 DTOs configured with `ConfigDict(strict=True, extra="forbid", frozen=True)`. Anonymous multi-value tuples (three or more elements, or two or more elements sharing identical primitive types) and positional tuple unpacking are eliminated. This prevents positional type blindness, where identically typed variables (such as analytical reasoning versus source quotes) can be inadvertently swapped during unpacking while silently passing static analysis. Standard two-tuples are reserved exclusively for standard payload and token usage pairs or key-value pairs at low-level utility boundaries.

### 2.4. Centralized Configuration Sovereignty
Operational thresholds, concurrency limits, retry budgets, timeouts, token ceilings, and section constraints are centrally defined in the master configuration layer. Business logic, orchestrator pipelines, and prompt templates resolve limits strictly from this single authoritative configuration source rather than hardcoding operational values in execution code.

### 2.5. Universal Single Source of Truth (SSOT) & Data Normalization
Every piece of state, telemetry metric, token count, pricing registry, financial cost, configuration mapping, and entity relation maintains exactly ONE authoritative source and ONE canonical storage location across backend and frontend. Data is maximally normalized at rest and in transit, with zero duplicate sub-dictionaries, secondary shadow tables, local backup dictionaries, or parallel fallback access chains. If data or metadata is missing from the canonical SSOT, the system halts immediately with an explicit exception rather than guessing or maintaining shadow state.

### 2.6. Repository Reconstitution Firewall
Persistence repositories act as strict anti-corruption layers. While low-level database drivers deserialize raw JSON/BSON records, the repository boundary immediately validates and reconstitutes them into strongly typed domain models before returning them to business services. Raw persistence dictionaries never leak into domain service layers, eliminating defensive type checks and ad-hoc fallback logic.

### 2.7. Cross-Domain Contract & Semantic Parity
Field and variable names are permanent architectural contracts. Nomenclature between Python backend and Flutter frontend remains 1:1 identical at the serialization layer (backend `snake_case` mapped to frontend `camelCase` via explicit JSON annotations). Renaming DTO fields, altering properties for subjective preference, or swapping domain concepts is strictly prohibited; all names and terms are derived directly from the SSOT.

### 2.8. Opaque ID Hydration via AliasEngine
To prevent LLM token bloat and hallucination from long database UUIDs, the prompt compiler substitutes raw identifiers with short, deterministic attention anchors (such as indexed atom and source identifiers like `a0` and `src_0`). After execution completes, the service layer hydrates these short aliases back to their physical database identifiers.

### 2.9. Dynamic Workflow Input Encapsulation
Dynamic workflow inputs declared in the ontology database are encapsulated inside strongly typed container DTOs (`ExecutionInputsDTO`). Services, hooks, and context builders accept this typed container directly, maintaining complete type safety across boundaries while preserving runtime workflow dynamism without requiring code deployments.

### 2.10. Server-Side UI Sanitization (Sandwich Architecture)
To ensure output stability, a deterministic interceptor layer sanitizes and validates LLM generation before payload delivery to the client. It strips conversational artifacts, validates markdown structures, and ensures complete compliance with expected Server-Driven UI schemas.

### 2.11. Dual-Reporting Protocol (RFC 7807)
Every backend exception (`AppException`) logs a structured error with exact logical error codes, parameters, and forensic trace identifiers before propagating. This provides immediate forensic traceability in monitoring systems while returning safe, structured problem details representations to client interfaces.

### 2.12. Static AST Guardrail Verification
Architectural invariants (prohibition of reflection, lazy default fallbacks, duck-typing, and multi-variable fallbacks) are statically verified across domain and service code through fatal AST guardrails during automated quality gates. Violations fail pre-test validation immediately, preventing architectural drift and ensuring that code adheres strictly to structural standards before execution.

### 2.13. Agent Context Quarantine
To prevent context amnesia and token saturation, complex agent workflows isolate planning from execution. Automated implementation plans are compiled into structured execution protocol blocks, allowing execution sessions to consume clean, validated instructions without carrying conversational history debt.

## 3. Logical Data Flow
```mermaid
flowchart TD
    A[External Request / System Event] --> B{Schema Boundary (Pydantic / Freezed)}
    B -- Invalid Payload --> C[Dual-Reporting & AppException]
    B -- Valid Payload --> D[Repository Reconstitution Firewall]
    D --> E[ExecutionInputsDTO Encapsulation]
    E --> F[AliasEngine Attention Anchor Masking]
    F --> G[Cognitive Engine & DAG Evaluation]
    G --> H{Evaluation Result}
    H -- Runtime Error --> C
    H -- Success --> I[Immutable Pydantic DTO Transit]
    I --> J[Server-Side UI Sanitization Interceptor]
    J --> K[Opaque ID Hydration]
    K --> L[Deterministic SDUI / PDF Output Delivery]
```
