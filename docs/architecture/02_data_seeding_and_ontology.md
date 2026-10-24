# Data Seeding & Ontology

## 1. Executive Summary
The **Data Seeding & Ontology** capability dictates that the Compound AI System is fundamentally **data-driven**, not code-driven. The entire behavior of the system—ranging from LLM instructions (PromptBlocks), allowed models, MCP tool gateways, to performative vocabularies—is defined externally in the central static data vault. The backend's primary role is to parse, validate, hydrate, and route this declarative ontology rather than hardcoding operational instructions.

## 2. Architectural Principles & Implementation

The Data Seeding & Ontology layer establishes the declarative schemas, dynamic rules, and static datasets that power the platform:

### 2.1. Polymorphic Rule Routing
All dynamic rules and criteria are modeled as a unified `PromptBlock` entity within the database. Polymorphic collection parsing automatically routes different categories of configuration data (`system_config`, `prompt_blocks`, `mcp_gateways`) into their respective Pydantic validation structures, ensuring typed domain validation before runtime execution.

### 2.2. Single Source of Truth (SSOT) Relational Persistence
The central static data vault serves as the immutable structural authority for baseline entities. The underlying storage remains flat and relational across root collections, while backend APIs construct nested and stitched views (specifically combining Workflows with Output Profiles) dynamically via dedicated response DTOs.

### 2.3. Dual-Tool Seed Governance & Sanitization Architecture
Seed data quality and consistency are maintained through a decoupled inspection and transformation architecture:
- **Static Heuristic Inspection**: A read-only verification engine audits referential integrity, AST pattern rules, and prompt conventions across root database collections (`prompt_blocks`, `steps`, `workflows`, `output_profiles`), returning deterministic compliance exit codes without modifying persistent state.
- **In-Memory Sanitization & Transformation**: A declarative transformation pipeline strips unauthorized formatting artifacts, screaming imperatives, and mechanical counting directives from prompt text, re-validates entities against strict domain schemas, and writes changes atomically.

### 2.4. Two-Phase In-Memory Pre-Flight Validation
Database seeding enforces a two-phase protocol that isolates schema validation from state modification:
- **Phase 1 (Pre-Flight In-Memory Verification)**: The seeder loads master seed data and validates 100% of collection records in memory against strict domain models configured with `ConfigDict(strict=True, extra="forbid")`. If any item fails validation, the process terminates immediately with an explicit validation error, leaving existing database tables untouched.
- **Phase 2 (Atomic Population)**: Existing tables and records are updated only after every collection passes pre-flight validation with zero errors.

### 2.5. Atomic File Persistence & Database Lock Protocol
Master seed persistence and database storage enforce atomic file writes and concurrency controls:
- **Temporary Replacement Writes**: File-level persistence writes serialized JSON to isolated temporary files, flushes and synchronizes disk buffers, verifies complete re-loadability in memory, and replaces target files via atomic file replacement operations.
- **Platform-Native Concurrency Locking**: Local database access enforces cross-process and cross-thread locks using platform-specific non-blocking file locking to prevent race conditions during concurrent execution runs.

### 2.6. In-Place Upsert Lifecycle & Entity Immutability
Runtime persistence repositories maintain state through in-place atomic upsert operations keyed by canonical Opaque Stripe IDs. Entities update their records directly without creating duplicate shadow instances or mutating unrelated collections, preserving referential integrity and audit trails across execution sessions.

### 2.7. Y-Funnel Pre-Hook Normalization
Data transformations during initialization utilize a Y-Funnel architecture where pre-hooks normalize heterogeneous input shapes before domain validation. This keeps core Pydantic V2 domain models pure and focused strictly on business invariants rather than ingestion gymnastics.

### 2.8. Semantic Localization via Performative Lexicons
System personality traits, terminology standards, and vocabulary constraints are governed as data rather than code. Declarative lexicons defined in seed data are injected dynamically during prompt compilation, supporting multilingual enforcement without code modifications.

### 2.9. Universal Bilingual Localization (I18nText)
User-facing dynamic strings across the ontology (profile titles, layout descriptions, preambles) utilize the strictly typed `I18nText` model in both Python and Flutter. The schema mandates complete baseline translations (`en` and target locale) with structured fallback resolution, ensuring bilingual parity across backend services, frontend widgets, and PDF generators.

### 2.10. Workflow Context Governance & Step Protection
Pipeline step definitions declare explicit system core protections (`is_system_core: true`) for foundational operations (document ingestion, scoring, synthesis, forensic reporting). Studio interface and API guardrails prevent unauthorized deletion or mutation of protected resources. Step blueprints (`Step`) and workflow step rules (`NodeStrategy`) embed an authoritative `StepZone` enum (`zone_a`, `zone_b`, `zone_c`), establishing 1:1 cross-language enum parity between backend and frontend. Steps in Zone A govern raw document ingestion (with deletion locked), Zone B hosts dynamic analytical specialists, and Zone C anchors downstream aggregation funnels (scoring, synthesis, XAI reporting). This server-driven zone classification powers Dumb Painter presentation in Quorum Studio with zero heuristic branching or client-side index calculations. Step definitions additionally declare synthesis source flags (`is_synthesis_source`), enabling deterministic context boundary governance between upstream text extraction and downstream qualitative synthesis.

### 2.11. Epistemic Separation (TheoryGrounding SSOT)
Bibliographic references and academic provenance metadata are strictly decoupled from operational prompting instructions. `PromptBlock.theory_grounding` (`TheoryGrounding`) is the sole Single Source of Truth for academic citations (`citation_reference`) and source URLs (`source_url`). `PromptBlock.ai_description` contains purely operational prompt text, allowing presentation layers and PDF reports to consume structured academic citations without prompt-scraping or token bloat.

### 2.12. Structured Few-Shot Calibration Schema (ContrastivePairDTO)
Evaluation assertions and rubrics across the ontology define structured few-shot grounding via `ContrastivePairDTO`, encapsulating `acceptable` and `rejected` exemplars with enforced minimum length boundaries and equality conflict rejection. This eliminates unstructured string delimiters and manual prefix conventions from the seed vault, guaranteeing that every matrix atom provides a pristine, strongly typed boundary definition ready for prompt compilation and direct production deployment across all environments without runtime parsing shims.

### 2.13. Matrix Seed Vault Hardening & Anti-Pattern Standards
High-entropy evaluation atoms across the 14 canonical matrices enforce deterministic anti-patterns and disambiguated multi-step acceptance criteria to eliminate subjective evaluation drift:
- **Scaffolding and Prompt Parameter Disqualification**: Explicit anti-patterns disqualify user task briefings, problem constraints, headcount allocations, and external AI dispatch instructions from satisfying cognitive competence criteria.
- **Cognitive Theory Hardening**: Atoms evaluating Bloom's Revised Taxonomy and Kahneman's Dual Process Theory enforce rigorous ontological boundaries. System 1 claims require demonstrated rule-of-thumb judgment rather than textbook definitions, while System 2 claims require active step-by-step cognitive calculation rather than passive retrospective review.
- **Multi-Step Deductive Criteria**: High-entropy triage atoms specify sequential acceptance criteria requiring multi-stage causal mediators and empirical scrutiny of proxy performance indicators, ensuring consistent interpretation across multi-provider evaluation fleets.

### 2.14. Dual-Track Matrix Schema & TDA Assertion Polarity Standards
All 15 canonical matrices in the seed vault inherit from `PromptBlockBase` as strongly typed `MatrixPromptBlock` entities (`category_id: "matrix"`, `type: "float"`), organizing assessment criteria into hierarchical `MatrixScale` levels containing Test-Driven Assertion (`TDAAssertion`) models:
- **MatrixPromptBlock Structure**: Defines scale extrema (`computed_min`, `computed_max`), localizable labels (`I18nText`), target evidence inputs (`target_input_key`: `product_text`, `chat_log`, or `all`), academic theory grounding (`TheoryGrounding`), evaluative scoring participation (`is_evaluative: bool`), and an ordered collection of `MatrixScale` objects (`scales`).
- **Evaluative Scoring Participation (`is_evaluative: bool`) & Relational Identifier Invariant**:
  - *Opaque Identifier Relational Invariant*: Entity slugs (specifically: `matrix_bloom`, `matrix_toulmin`) are strictly human-readable diagnostic labels and editorial aliases. Slugs MUST NEVER be used as relational keys, foreign keys, step criteria references (`criteria_block_ids`), output profile selectors (`variance_target_block`), or state dictionary keys (`evaluative_matrices`). ALL relational bindings and state transit across the system are keyed strictly and sovereignly by canonical opaque block IDs (`blk_...`).
  - *Evaluative Matrices (10 matrices, `is_evaluative: true`)*: Directly participate in the global holistic score average (`global_score`). Encompasses 4 Track A developmental matrices (`blk_f921c7c0989b47e8` [Bloom], `blk_f6e286f050c94d60` [TaskXAI Clarity], `blk_7d8e9f0a1b2c3d4e` [HACM], `blk_c0a1e50000000001` [Causal Cohesion]) and 6 Track B diagnostic matrices (`blk_440a5fef9331451b` [Toulmin], `blk_109dab5b6b3f403a` [Kahneman], `blk_c5804a9143c34cb1` [Causal Analyst], `blk_b476f89fb732448c` [Falsifier], `blk_22e3598e06414409` [Epistemic Humility], `blk_c3bc5f3eb8e74110` [Causal & Abductive Integrity]).
  - *Specialized Role Matrices (5 matrices, `is_evaluative: false`)*: Serve specialized non-averaging architectural functions: `blk_53f32679aa514fcb` [Goodhart] (Cartesian variance X-axis), `blk_80732a33fe1947ee` [Taskguard] (security containment guard triggering `security_penalty`), `blk_fb15f8dcf23f4865` [Archivist] (statutory compliance checklist), `blk_ff72c2d79edb4ebf` [Supreme Adjudicator] (supervisory steering discipline), and `blk_6b8c766185294f7e` [XAI Reporter] (multi-specialist consensus reporting).
- **MatrixScale Hierarchy**: Each scale level defines a numerical `score` (specifically 1 to 5, or 1 to 6 for Bloom), localized scale names (`I18nText`), an evaluator directive (`ai_label`), and constituent `claims` grouping underlying `TDAAssertion` criteria.
- **TDAAssertion Schema & Mandatory Polarity Constraints**:
  - *Track A (Developmental Competence Matrices: 7 matrices)*: Level 1 designates foundational Novice capability (`Alustava / Noviisi / Tunnistava`). All constituent TDA assertions enforce `inverse_evidence: false` and `aggregation_mode: "ALL_MUST_COMPLY"`. Level 1 measures the presence of baseline capability and awards positive capability points. Higher levels build cumulatively under the Cumulative Guttman Invariant ($L_1 \subset L_2 \subset L_3 \subset L_4 \subset L_5$). Inverting Level 1 into an error detector is strictly prohibited (Inverted Rubric Paradox ban).
  - *Track B (Diagnostic Error Radar Matrices: 8 matrices)*: Levels 1 and 2 operate strictly as error radars (`Kriittinen virhe / Vakava harhaluulo / Fatal Flaw`). All Level 1–2 TDA assertions enforce `inverse_evidence: true` and `aggregation_mode: "EXISTS"`. Zero positive assertions are permitted on Levels 1–2. Under the Null Hypothesis, clean baseline passes on Levels 1–2 award zero positive capability points, while detected errors trigger deterministic malus deductions. Positive capability points accrue exclusively from affirmative criteria on Levels 3–5 (`inverse_evidence: false`), allowing evaluative Track B matrices to achieve up to 100% normalized scores feeding directly into `global_score`.

### 2.15. Deterministic Causal Cohesion Metric Matrix & Holistic Workflow Topology
The static ontology includes pure system-evaluated metric matrices that assess structural reasoning rather than LLM text generation. The Causal Cohesion BARS Matrix (`matrix_causal_cohesion`, `blk_c0a1e50000000001`) defines a 5-level developmental competence scale evaluated deterministically from graph telemetry:
- **0-Token Execution Contract**: The matrix is strictly excluded from LLM `criteria_block_ids`. It consumes topological graph metrics (`logical_cohesion_score`, `cycle_detected`, `isolated_concept_count`) directly from upstream causal discovery step outputs, eliminating model token consumption and latency overhead for structural graph scoring.
- **Topological BARS Grounding**: Scale levels reflect structural reasoning integrity under the Cumulative Guttman Invariant ($L_1 \subset L_2 \subset L_3 \subset L_4 \subset L_5$). Cyclic dependencies trigger immediate defect grounding at Level 1 (Novice), and empty proposition graphs ground safely at the Novice floor without arithmetic faults.
- **Holistic Workflow Step Integration**: Workflows integrate causal discovery as a first-class execution step positioned in Zone B, establishing causal provenance for downstream specialist steps and funneling structural cohesion scores into synthesis comparison groups.

### 2.16. Declarative MCP Gateway Ontology & Tool Capabilities
External tool permissions and capabilities are configured declaratively in the static data vault under `system_config` (entity `sys_8172bda70c8641c5`):
- **Full-Duplex Contract Parity**: Tool definitions enforce 1:1 schema parity between backend `AllowedMCPTool` and frontend `AllowedMcpTool` models, validating `tool_id`, `name`, `description`, `enabled`, and the authoritative `capability: ToolCapability` attribute (`search`, `document_reader`, `action`).
- **Native Knowledge Ingress Tooling**: The seed vault registers primary information discovery and article extraction tools: `mcp_tavily_search` (`capability: search`), `mcp_wikipedia_search` (`capability: search`), and `mcp_wikipedia_read` (`capability: document_reader`).
- **Dynamic Studio Governance**: Tool definitions expose bilingual labels and toggle controls in Quorum Studio, enabling administrators to activate or constrain external MCP capabilities per gateway with immediate schema validation.

## 3. Logical Data Flow
```mermaid
flowchart TD
    A[Central Static Data Vault] --> B[Two-Phase Pre-Flight In-Memory Verification]
    B -- Schema Violation --> C[Fail-Fast & Abort Seeding]
    B -- 100% Valid --> D[Atomic Persistence & Reseed Engine]
    D --> E{Polymorphic Router}
    E -- Type: system_config --> F[System Config Registries]
    E -- Type: prompt_blocks --> G[AnyPromptBlock Domain Union]
    E -- Type: steps --> H[Step Blueprints & Governance]
    E -- Type: workflows --> I[DAG Orchestrator Workflows]
    E -- Type: output_profiles --> J[Output Profile Layouts]
    F & G & H & I & J --> K[Repository Reconstitution & In-Place Upsert Layer]
    K --> L[In-Memory / Database State]
    L --> M[Cognitive Execution Engine]
```
