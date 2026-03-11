# Search, Grounding, and Retrieval Architecture (V5.1)

This document defines the three distinct paradigms of information retrieval and fact-checking employed within the Cognitive Quorum system. To prevent "Context Collapse" and ensure strict fidelity in multi-agent orchestration, the system segregates information gathering into three distinct layers: 

1. **Analyst Hypothesis Search (Evidence Gathering)**
2. **Dynamic Vertex Grounding (Fact-Checking & Citation)**
3. **Internal Knowledge Base Retrieval (Compliance & Domain Context)**

---

## 1. Analyst Hypothesis Search (`backend/hooks/search.py`)
**Role:** Generative Evidence Gathering
**Trigger Phase:** *Pre-Execution Hook* (e.g., Before `step_overseer` or `step_panel`)

### Purpose
This process is designed to independently test the *User's* inputs or the *Analyst's* hypotheses. It expands the system's awareness by actively searching the internet for new information related to the ongoing case before any final synthesis is drafted. 

### Mechanism
- The `AnalystAgent` strictly generates JSON output containing `hypotheses` with specific `search_query` strings and sequential IDs (e.g., `HYP-1`).
- The `execute_google_search` hook (`search.py`) intercepts the workflow, takes these queries, and performs explicit internet searches using a dedicated Vertex AI LLM.
- The resulting web snippets and URLs are converted to strict Pydantic `search_result` dicts and injected into the global context variable.
- Downstream agents (like the Factual Overseer or Koonti-Panel) now possess deterministic external context they can use to build their arguments, isolated from hallucination risks.

---

## 2. Dynamic Vertex Grounding (`backend/llm/provider.py`)
**Role:** In-line Fact-Checking and AI Citation
**Trigger Phase:** *Execution Phase* (Attached directly to `LiteLLMProvider` LLM calls)

### Purpose
While the Analyst Search finds evidence, Grounding ensures that the *AI's own claims* are factual and traceably cited. It prevents hallucination at the exact moment the text is generated.

### Mechanism
- Enabled dynamically via the UI configuration (`Model Registry` -> `supports_grounding: true`). Usually reserved strictly for the "Deep" reasoning strategy to save latency.
- Appended directly to the LLM invocation (`tools=[{"googleSearch": {}}]`).
- When the LLM formulates a response, the Vertex backend transparently cross-references the tokens with Google Search.
- The LLM returns `grounding_metadata`. Quorum intercepts this metadata and injects a formatted Markdown bibliography (e.g., `[1] Source Title: URL`) directly into the final output.
- **Strict Distinction:** Grounding does *not* search for new ideas; it verifies the ideas the LLM has already decided to generate based on the System Prompt and Blackboard context.

---

## 3. Internal Knowledge Base Retrieval (`backend/hooks/references.py` & `knowledge_base_service.py`)
**Role:** Domain/Brand Compliance and Internal Documentation
**Trigger Phase:** *Pre-Execution / Post-Execution Hooks*

### Purpose
Unlike generic web searches or external Google Grounding, this subsystem enforces adherence to strictly controlled *internal* documents (e.g., Brand Books, Organization Guidelines, internal PDFs). Its mandate is to "police" the output against internal rules.

### Mechanism
- **Ingestion (`knowledge_base_service.py`):** Documents are uploaded, chunked, parsed for references via Regex, and semantically categorized via a rapid LLM pass into `Concepts`, `Claims`, and `References`.
- **Retrieval (`references.py`):** Hooks scan the generated texts or workflow inputs against this ingested knowledge base.
- If a generated text violates or aligns with the Brand Book, the hook extracts those citations and injects them as a `BibliographyResult`.

### Current Status (Work in Progress)
The core infrastructure for the Internal Knowledge Base exists but requires completion:
- The in-memory text comparison inside `retrieve_context` needs to be upgraded to Vector Semantic Search (Embeddings).
- The `references.py` implementation currently relies heavily on string matching; it needs integration with the newer `GraphEngine` dynamic retrieval loops.
- Tasks to complete this have been added to the `docs/product_roadmap.md` Backlog.
