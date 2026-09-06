# META-GOVERNANCE: THE DUAL-AXIS DOCUMENTATION PARADIGM

This directory (`docs/architecture/`) contains the foundational meta-architecture for the Quorum V2 system. These documents are governed by a strict Dual-Axis paradigm designed to prevent architectural rot and Context Amnesia.

> [!IMPORTANT]
> **Not a Pillar**
> This `00_README_META_ARCHITECTURE.md` file is a meta-governance document. It is NOT part of the system architecture itself. Files `01_` through `06_` represent the 6 core pillars of the Quorum capability-driven architecture.

## 1. The Dual-Axis Documentation Paradigm

Architecture in Quorum is defined along two isolated axes:
1. **The Theoretical Axis (The Narrative):** This directory (`docs/architecture/`). It explains the *why*, the *concepts*, and the *capabilities* of the 6 pillars without referencing specific file paths, temporary code snippets, or implementations.
2. **The Physical Axis (The Map):** The `.agents/rules/04_directory_reference.md` rule file. It contains the hardcoded, physical paths and module boundaries (e.g., `backend_v2/services/`, `client_app_v2/lib/features/`).

By separating the theoretical from the physical, the system can continuously refactor directories without invalidating the architectural theory, and vice-versa.

## 2. The 7 Pillars of Capability-Driven Architecture

The core architecture is strictly divided into 7 timeless pillars:
1. **System Context & Invariants (`01_`)**
2. **Data Seeding & Ontology (`02_`)**
3. **Cognitive Orchestration Engine (`03_`)**
4. **Server-Driven UI (SDUI) & Presentation (`04_`)**
5. **Resilience & Observability (`05_`)**
6. **Enriched Atom Graph Engine (`06_`)**
7. **EU AI Act Compliance & Governance (`07_`)**

## 3. The Golden Rule: Timelessness & Pure Present-Tense Description

The documents in this directory MUST remain absolutely timeless, stateless, and focused purely on what the system currently consists of:
- **BANNED:** Project phases or development stages (e.g., "Phase 1", "Phase 2", "vaiheet", "rollout phases").
- **BANNED:** Mentioning Epic IDs (e.g., "In Epic 115 we added...").
- **BANNED:** Historical comparisons or legacy migrations (e.g., "The old V1 system used X, but now we use Y").
- **BANNED:** Dates, future roadmaps, or "in-progress" markers.
- **BANNED:** Physical file paths (e.g., `backend_v2/api/routers/`).
- **BANNED:** Artificial meta-rule framing such as `- **Law:**` / `- **Enforcement:**` or labeling sections as "(The Laws)".

The documents must describe the system purely and exclusively as it exists *now*, in the present tense, as an objective state of truth ("kerro ainoastaan ja puhtaasti se mitä meillä on nyt").

## 4. How to Update the Architecture

> [!WARNING]
> **Direct Edits Forbidden**
> Human developers and AI agents (unless explicitly running a Tier 7 workflow) are FORBIDDEN from manually editing `01_` through `07_` in this directory. 

### The Continuous Integration Pipeline (Tier 7)
1. **Create Knowledge Items (KIs):** When a new feature or architectural pattern is implemented, the developer or AI must create a localized Knowledge Item (KI) containing the specific physical details and code samples.
2. **Execute Tier 7:** The user invokes the `/tier7-describe-architecture` workflow.
3. **Synthesis:** The AI reads the new KIs and automatically synthesizes the theoretical concepts into the `01_` through `07_` pillar documents while strictly enforcing the Timelessness mandate.
4. **Physical Map Update:** If directories were changed, the AI updates `.agents/rules/04_directory_reference.md` directly.

This creates a "Write-Once, Synthesize-Everywhere" paradigm that ensures the global architecture remains universally accurate without manual chore-work.
