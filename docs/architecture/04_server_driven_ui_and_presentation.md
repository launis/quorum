# Server-Driven UI & Presentation

## 1. Executive Summary
The **Server-Driven UI & Presentation** capability governs how the "Surface" of the Compound AI System operates. The core philosophy is that the client application (`client_app_v2` / Flutter) is a completely "dumb" rendering engine. It contains zero business logic, zero prompt compilation, and zero layout math. The backend strictly dictates the state, and the frontend merely paints the declarative Markdown and data blocks it receives.

## 2. Core Architectural Invariants (The Laws)

These absolute rules (Knowledge Items) govern the global context and must NEVER be violated:

### 2.1. The De-Generator Execution Paradigm
- **Law:** The UI must never directly write, edit, or understand LLM instructions or XML prompt envelopes.
- **Enforcement:** The system enforces a strict separation of concerns. The frontend application handles only flat, human-readable business logic (typically represented as Markdown text). The backend's `PromptCompiler` is exclusively responsible for injecting this flat text into system-defined XML envelopes. This prevents end-users (or rogue UI code) from manually engineering raw LLM prompts, ensuring prompt injection safety and deterministic execution.

### 2.2. Strict ICU Markdown Parity
- **Law:** The backend must never generate presentation-specific code (e.g., HTML tags, inline CSS colors, Flutter widgets) to enforce visual styles.
- **Enforcement:** The backend is restricted to serving only semantic Markdown and ICU message templates. All layout, coloring, typography, and styling are exclusively handled by the Frontend's UI component library. This absolute parity ensures that the exact same payload can be seamlessly rendered by both the Flutter interactive display and the static PDF generation engine without any platform-specific hacks.

### 2.3. Null-Safe State Synchronization
- **Law:** The frontend must never try to "guess" missing UI components using hidden fallbacks.
- **Enforcement:** The Server-Driven UI (SDUI) models sent from the backend are fully exhaustive. If the frontend expects a configuration block for a specific widget and it is missing, the frontend must rely on the explicit App Error Boundary (as defined in the Resilience capability) rather than silently returning a `SizedBox.shrink()`.

### 2.4. SDUI Component Contracts
- **Law:** The frontend must render SDUI components exactly as dictated by the backend enum mapping, avoiding manual UI overrides.
- **Enforcement:** Specific SDUI components must inherently support their required domain constraints (e.g., `n_a_card` rendering `short_circuit_reason_tda_ids` directly from the context payload without separate API calls). The components defined in the backend `SDUIComponentType` (like `boolean_card`, `extracted_value_card`, `error_card`, `n_a_card`) are absolute boundaries.

### 2.5. UI Editing Parity for Dynamic Text
- **Law:** Forms mutating localized dynamic strings must encapsulate `I18nText` object handling natively.
- **Enforcement:** When the Studio UI interacts with a localized string from the Ontology, it MUST use the `I18nTextField` component rather than a generic text input. This component safely extracts, updates, and repackages the underlying `I18nText` schema in real-time, preventing developers from manually unpacking maps or defaulting to fallback string inputs that would break schema parity with the backend.

## 3. Logical Data Flow
```mermaid
flowchart TD
    A[Backend Service] --> B{SDUI Payload Compiler}
    B --> C[Semantic Markdown Generation]
    B --> D[ICU Template Injection]
    C & D --> E[JSON API Response]
    E --> F[Client App V2 (Flutter)]
    F --> G{App Shell Router}
    G --> H[Widget Library (Theme / Color / Layout)]
    H --> I[Screen Render]
```

## 4. Physical Implementation Map (Auto-Generated)
> **Note:** This section is automatically maintained by the Tier 7 execution agent. Do not manually update physical file paths here.
- **Backend Entrypoints:** `backend_v2/api/routers/execution/`, `backend_v2/services/execution.py`, `backend_v2/services/blueprint.py` (Payload Compiler), `backend_v2/services/sdui_mapper_service.py` (BFF SDUI Translation), `backend_v2/services/pdf_generator.py` (PDF rendering), `backend_v2/templates/` (PDF rendering).
- **Frontend Consumers:** `client_app_v2/lib/features/execution/views/widgets/report_renderer_v2_widget.dart` (Main SDUI consumer), `client_app_v2/lib/features/execution/views/widgets/sdui_block_renderer.dart` (SDUI Rendering), `client_app_v2/lib/shared/widgets/output_renderer.dart` (Markdown Parser), `client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart` (3-Part UI Layout Block Editor).
