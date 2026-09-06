# System Context & Core Invariants

## 1. Executive Summary
The **System Context & Core Invariants** capability forms the foundational "constitution" of the Compound AI System. It establishes the absolute architectural laws (The Zero-Compromise Pledges) that govern how all other components (Backend, Frontend, LLM Engine) must behave. This capability exists to ensure **Forensic Sovereignty**, deterministic execution, and the total eradication of silent failures, LLM hallucinations, and undocumented state mutations.

## 2. Architectural Principles & Invariants

Quorum operates on strict structural boundaries, deterministic execution, and end-to-end auditability:

### 2.1. Universal Fail-Fast & Strict Schema Validation
All data crossing system boundaries is strictly validated against immutable schemas (Pydantic V2 in Python, Freezed in Dart). Fallback chains, silent error absorption, and duct-tape workarounds are eliminated. If data is missing, malformed, or an expected state is not reached, the system halts immediately with an explicit `AppException` on the backend or renders an `AppErrorBoundary` on the client. Masking errors by returning empty arrays or hiding UI widgets is strictly prohibited.

### 2.2. Centralized Configuration Sovereignty
Operational thresholds and limits (retry counts, timeouts, token limits, section constraints) are centrally defined in the master configuration layer (`settings.py`). Business logic and prompt templates resolve limits from this single source of truth rather than hardcoding values in operational code.

### 2.3. Opaque ID Hydration via AliasEngine
To prevent LLM token bloat and hallucination from long database UUIDs, the prompt compiler substitutes raw identifiers with short, deterministic "Attention Anchors" (e.g., `a0`, `src_1`). After execution completes, the service layer hydrates these short aliases back to their physical database identifiers.

### 2.4. Server-Side UI Sanitization (Sandwich Architecture)
To ensure output stability, a deterministic Python interceptor layer sanitizes and validates LLM generation before payload delivery to the client. It strips conversational artifacts, validates markdown structures, and ensures 100% compliance with expected Server-Driven UI schemas.

### 2.5. Dual-Reporting Protocol (RFC 7807)
Every backend exception (`AppException`) logs a structured error with exact logical error codes, parameters, and forensic trace identifiers before propagating. This provides immediate forensic traceability in monitoring systems while returning safe, structured error representations to client interfaces.

### 2.6. Agent Context Quarantine
To prevent context amnesia and token saturation, complex agent workflows isolate planning from execution. Automated implementation plans are compiled into structured `<execution_protocol>` blocks, allowing execution sessions to consume clean, validated instructions without carrying conversational history debt.

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


