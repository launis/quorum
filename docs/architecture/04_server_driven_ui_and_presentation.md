# Server-Driven UI & Presentation

## 1. Executive Summary
The **Server-Driven UI & Presentation** capability governs how the "Surface" of the Compound AI System operates. The core philosophy is that the client application (Flutter frontend) is a completely "dumb" rendering engine. It contains zero business logic, zero prompt compilation, and zero layout math. The backend strictly dictates the state, and the frontend merely paints the declarative Markdown and data blocks it receives.

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
- **Enforcement:** Specific SDUI components must inherently support their required domain constraints (e.g., `n_a_card` rendering required fields directly from the context payload without separate API calls). The components defined in the backend `SDUIComponentType` (like `boolean_card`, `extracted_value_card`, `error_card`, `n_a_card`) are absolute boundaries.

### 2.5. UI Editing Parity for Dynamic Text
- **Law:** Forms mutating localized dynamic strings must encapsulate `I18nText` object handling natively.
- **Enforcement:** When the Studio UI interacts with a localized string from the Ontology, it MUST use the standard translation component rather than a generic text input. This component safely extracts, updates, and repackages the underlying `I18nText` schema in real-time, preventing developers from manually unpacking maps or defaulting to fallback string inputs that would break schema parity with the backend.

### 2.6. BFF SDUI Translation
- **Law:** The backend must translate complex domain models into explicit Server-Driven UI payloads before sending them to the frontend.
- **Enforcement:** Utilizing the Backend-for-Frontend (BFF) pattern, dedicated mappers translate domain objects into exact layout structures (e.g., rows, columns, cards). The frontend consumes this strictly typed structure, avoiding any complex logic processing on the client side.

### 2.7. 3-Part UI Layout Block Editor
- **Law:** Editing interfaces for layout components must enforce strict structural constraints across all views.
- **Enforcement:** The UI editing mechanism for layout blocks enforces a rigid three-part architecture (Header, Body, Footer). This standardization ensures that both the interactive canvas editor and the final rendered view follow identical structural rules, maintaining 100% parity across edit and display states.

### 2.8. Dumb Painter Flat Polymorphic Block Pipeline
- **Law:** The frontend must never map semantic business models directly into layout arrays, parse macro-layout containers, nor perform scaling math for score presentation.
- **Enforcement:** All structural UI elements (including charts, matrices, and text blocks) are strictly mapped into a single, flat `inner_sdui_blocks` array by the backend. The frontend iterates sequentially through this flat polymorphic array, rendering each block based on its specific variant (e.g., `grid`, `accordion`, `header`, `markdown`, `radar_3d`). Legacy macro-layout containers (like `ReportLayoutDTO` with `preset_view` routing) are completely forbidden. Furthermore, all mathematical evaluations of scores (e.g., displaying "5.0 / 10.0" versus "-") are computed exclusively on the backend and sent as a pre-computed `score_display_label`. The frontend strictly acts as a Dumb Painter for these pre-computed strings, preserving deterministic rendering parity across web and PDF views.

### 2.9. Strict SDUI Polymorphic Serialization
- **Law:** Dynamic UI block arrays must never rely on unstructured dictionaries or duck-typing.
- **Enforcement:** All dynamic UI layout blocks (e.g., within reports or profiles) MUST be strictly typed using the polymorphic `AnySduiBlock` (Python Pydantic discriminated union) and `SduiBlockDTO` (Flutter Freezed sealed class). Every block MUST possess a discrete `block_type` discriminator. If an unrecognized `block_type` is received by the frontend, the Freezed parser MUST fail-fast (triggering the App Error Boundary) rather than silently dropping or misinterpreting the block, ensuring 100% schema fidelity across boundaries.

## 3. Logical Data Flow
```mermaid
flowchart TD
    A[Backend Service] --> B{SDUI Payload Compiler}
    B --> C[Semantic Markdown Generation]
    B --> D[ICU Template Injection]
    B --> E[Dumb Painter Layout Mapping]
    C & D & E --> F[JSON API Response]
    F --> G[Client App]
    G --> H{App Shell Router}
    H --> I[Widget Library]
    I --> J[Screen Render]
```
