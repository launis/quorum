# System Context & Core Invariants

## 1. Executive Summary
The **System Context & Core Invariants** capability forms the foundational "constitution" of the Compound AI System. It establishes the absolute architectural laws (The Zero-Compromise Pledges) that govern how all other components (Backend, Frontend, LLM Engine) must behave. This capability exists to ensure **Forensic Sovereignty**, deterministic execution, and the total eradication of silent failures, LLM hallucinations, and undocumented state mutations.

## 2. Core Architectural Invariants (The Laws)

These absolute rules (Knowledge Items) govern the global context and must NEVER be violated:

### 2.1. The Zero-Compromise Pledge & Universal Fail-Fast
- **Law:** The system forbids "duct-tape" coding, fallback chains (`v.get('field', '')`), or silent error absorption. Any data entering or leaving a system boundary must be strictly validated against immutable schemas (Pydantic V2 in Python, Freezed in Dart).
- **Enforcement:** If data is missing, malformed, or an expected state is not reached, the system MUST crash immediately (`AppException` or `AppErrorBoundary`). Masking errors by returning empty arrays or hiding UI widgets (`SizedBox.shrink()`) is strictly prohibited.

### 2.2. Global Config Sovereignty
- **Law:** Business logic (e.g., retry limits, API timeouts, maximum token limits) must NEVER be hardcoded deep within operational code or prompt templates.
- **Enforcement:** All thresholds and system-wide limitations must be centrally defined and governed by the backend's master configuration layer. This ensures that a single architectural update propagates deterministically across all services.

### 2.3. Opaque ID Hydration (AliasEngine)
- **Law:** LLMs are inherently prone to token bloat and hallucination when handling long UUIDs or complex database keys.
- **Enforcement:** Raw database identifiers MUST NOT be exposed to the LLM directly. The system uses an "AliasEngine" to replace long UUIDs with deterministic, semantic "Attention Anchors" (e.g., `a0`, `src_1`) during the prompt compilation phase. These opaque IDs are hydrated back into their true physical UUIDs post-execution by the backend.

### 2.4. Hybrid UI Sanitization (Sandwich Architecture)
- **Law:** LLM outputs are naturally noisy and may contain conversational filler or broken markdown schemas, which would crash the UI parser.
- **Enforcement:** A deterministic Python interceptor layer (The Sandwich) strictly sanitizes and validates LLM output *before* it is returned to the frontend. It strips technical metadata, enforces UI constraints, and ensures the payload is 100% compliant with the expected SDUI schema.

### 2.5. Dual-Reporting Protocol (RFC 7807)
- **Law:** Crashing the system without a forensic trace creates "black box" failures.
- **Enforcement:** Every `AppException` thrown must be preceded by a structured `logger.error` containing the exact logical reason for the failure and contextual parameters. This enables the UI to display a user-friendly error card while preserving the deep forensic trace in backend logs (e.g., Logfire).

## 3. Logical Data Flow
```mermaid
flowchart TD
    A[External Request / System Event] --> B{Schema Boundary (Pydantic/Freezed)}
    B -- Invalid --> C[Fail-Fast & Dual-Reporting]
    B -- Valid --> D[AliasEngine ID Masking]
    D --> E[LLM Processing / Business Logic]
    E --> F[Hybrid UI Sanitization]
    F --> G[Opaque ID Hydration]
    G --> H[Deterministic Output]
```


