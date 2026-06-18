# EPIC 80: Global Document Cache & Matrix Instruction Decoupling (V2.5)

## 1. Context & Motivation

In the current V2 architecture, the **PromptBlock** strategy bundles both the **Static Source Text** (e.g., 13,000 - 30,000 character PDF extracts, chat logs) and the **Dynamic Evaluation Instructions** (specific Matrix criteria, strictness rules, and flattened atoms) into a single, cohesive System Prompt payload. 

While this maximizes LLM obedience (Zero-Variance Blind Evaluation), it creates a severe performance and FinOps bottleneck:
* Because each matrix has different criteria, the combined payload changes for every matrix.
* Vertex AI Context Caching requires an identical payload to register a Cache Hit.
* Therefore, the system is forced to create a **brand new Context Cache** for every single matrix, re-uploading the exact same 30,000 characters of static text repeatedly.
* This redundancy triggers heavy API rate-limiting (`Wait-and-Poll: Pacing lock active`) and inflates API write costs.

## 2. Proposed Architecture: Global Document Cache

The goal of this Epic is to decouple the static payload from the dynamic instructions, establishing a **Global Document Cache** that persists across the entire execution lifecycle.

### Core Mechanisms:
1. **Cache Initialization (Execution Start):**
   * At the beginning of an execution (`exe_xyz`), load all static inputs (`input_product_text.md`, `input_chat_log.md`) and core Universal Agent Rules.
   * Send this static bundle to Vertex AI to create a single **Global Context Cache**.
   * Store the resulting `Cache ID` in the execution state.

2. **Dynamic Querying (Chunk Workers):**
   * When `chunk_worker.py` processes a specific Matrix, it no longer creates a new cache.
   * Instead, it takes the Matrix-specific instructions and the flattened True/False atoms, and sends them as a **User Prompt** (or appended message) routed to the **existing Global Context Cache**.
   * The `gemini-2.5-flash` and `gemini-2.5-pro` models draw their grounding context from the shared cache, evaluating the dynamic atoms in milliseconds.

## 3. Analytical Impact Assessment

### 🟢 Performance & Latency (Estimated Impact: +40-60% Speedup)
* **Current State:** Re-uploading 30k characters 10 times causes severe network I/O and triggers 12-second pacing locks repeatedly.
* **Future State:** Uploading 30k characters once. Subsequent matrix evaluations only send a few hundred characters of instructions. Pacing locks will trigger significantly less often, reducing execution time from minutes to potentially under a minute.

### 🟢 FinOps & Cost Efficiency (Estimated Impact: -80% Write Costs)
* **Current State:** Paying Vertex AI "Cache Write" pricing for 300,000 tokens (30k * 10 matrices).
* **Future State:** Paying "Cache Write" pricing for 30,000 tokens (once), and heavily discounted "Cached Token Read" pricing for the subsequent queries.

### 🔴 Architectural Risks & Hazards
* **Instruction Obedience Degradation:** The primary risk. Currently, Matrix rules live in the System Prompt, commanding absolute LLM obedience (crucial for Pydantic JSON output and blind evaluation). Moving these rules to the dynamic "User Prompt" might cause the LLM to occasionally hallucinate or break schema formatting (`LLM Schema Validation Failed`).
* **Cache Lifetime Management:** Global caches must be explicitly deleted after the execution finishes to avoid lingering storage costs. The `execution_cleanup_service` must be hardened to guarantee Cache destruction even on catastrophic failures.

## 4. Implementation Phasing

* **Phase 1: Proof of Concept (PoC)**
  * Test LLM obedience. Does `gemini-2.5-flash` still perfectly output the required JSON schema if the Matrix rules are moved out of the cached System Prompt and injected dynamically?
* **Phase 2: Adapter Refactoring**
  * Modify `vertex_adapter.py` to allow passing an existing `Cache ID` instead of forcing creation.
* **Phase 3: Orchestrator Decoupling**
  * Update `execution_orchestrator.py` to build the Global Cache upfront.
  * Update `atom_flattening.py` and `chunk_worker.py` to construct pure dynamic prompts without the source text.

## 5. Conclusion
Transitioning to a Global Document Cache represents a massive leap in enterprise scalability for Cognitive Quorum. It directly addresses the "Pacing Lock" bottleneck while capitalizing on Vertex AI's most powerful cost-saving feature, paving the way for the V2.5 architecture.
