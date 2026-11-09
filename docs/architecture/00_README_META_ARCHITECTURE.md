# META-GOVERNANCE: THE DUAL-AXIS DOCUMENTATION PARADIGM

This directory (`docs/architecture/`) contains the foundational meta-architecture for the Quorum V2 system. These documents are governed by a strict Dual-Axis paradigm designed to prevent architectural rot and Context Amnesia.

> [!IMPORTANT]
> **Not a Pillar**
> This `00_README_META_ARCHITECTURE.md` file is a meta-governance document. It is NOT part of the system architecture itself. Files `01_` through `09_` represent the architectural pillars of the Quorum capability-driven architecture.

## 1. The Dual-Axis Documentation Paradigm

Architecture in Quorum is defined along two isolated axes:
1. **The Theoretical Axis (The Narrative):** This directory (`docs/architecture/`). It explains the *why*, the *concepts*, and the *capabilities* of the 9 pillars without referencing specific file paths, temporary code snippets, or implementations.
2. **The Physical Axis (The Map):** The `.agents/rules/04_directory_reference.md` rule file. It contains the hardcoded, physical paths and module boundaries (`backend_v2/services/` and `client_app_v2/lib/features/`).

By separating the theoretical from the physical, the system can continuously refactor directories without invalidating the architectural theory, and vice-versa.

## 2. Core Pillars of Capability-Driven Architecture

The core architecture is structured across dedicated architectural pillars:
1. **System Context & Invariants (`01_`)**: Foundational constitution, universal fail-fast invariants, zero permissive typing, canonical domain imports, and fatal AST guardrail enforcement.
2. **Data Seeding & Ontology (`02_`)**: Database schemas, seed registry, declarative MCP gateway ontology with native knowledge tools (Wikipedia search/read, Tavily search/extract) and closed JSON Schema Draft 2020-12 tool parameter contracts, and two-phase in-memory seeder pre-flight validation.
3. **Cognitive Orchestration Engine (`03_`)**: DAG workflow evaluation, dynamic capability-driven MCP tool dispatching (search, document reader, action) with direct node-level retrieval, sovereign execution subservices, pure Arq worker daemon runtimes, and Best-of-Three Flash consensus.
4. **Server-Driven UI (SDUI) & Presentation (`04_`)**: Flat polymorphic `inner_sdui_blocks`, co-located forward-reference hydration, and Dumb Painter rendering.
5. **Resilience & Observability (`05_`)**: Distributed circuit breaking, telemetry, and error classification.
6. **Enriched Atom Graph Engine (`06_`)**: Topological assertion evaluation, atomic quotes, and lexical validation.
7. **EU AI Act Compliance & Governance (`07_`)**: Regulatory transparency, audit trails, and human oversight.
8. **Matrix Theory Explanations Compendium (`08_`)**: Conceptual grounding and evaluation matrices.
9. **LLM Prompt Orchestration & Matrix Evaluation Architecture (`09_`)**: Four-Layer Clean Stack hierarchy and static-first caching.

## 3. The Golden Rule: Timelessness & Pure Present-Tense Description

The documents in this directory MUST remain absolutely timeless, stateless, and focused purely on what the system currently consists of:
- **BANNED:** Project development stages ("vaiheet" or rollout stages).
- **BANNED:** Mentioning task or initiative identifiers.
- **BANNED:** Historical comparisons or legacy migrations ("The old V1 system used X, but now we use Y").
- **BANNED:** Dates, future roadmaps, or "in-progress" markers.
- **BANNED:** Physical file paths (`backend_v2/api/routers/`) inside pillar documents `01_` through `09_`.
- **BANNED:** Artificial meta-rule framing (`- **Law:**`, `- **Enforcement:**`, or `(The Laws)`).

The documents must describe the system purely and exclusively as it exists *now*, in the present tense, as an objective state of truth ("kerro ainoastaan ja puhtaasti se mitä meillä on nyt").

## 4. How to Update the Architecture

> [!WARNING]
> **Direct Edits Forbidden**
> Human developers and AI agents (unless explicitly running a Tier 7 workflow) are FORBIDDEN from manually editing `01_` through `09_` in this directory. 

### The Continuous Integration Pipeline (Tier 7)
1. **Create Knowledge Items (KIs):** When a new feature or architectural pattern is implemented, the developer or AI must create a localized Knowledge Item (KI) containing the specific physical details and code samples.
2. **Execute Tier 7:** The user invokes the `/tier7-describe-architecture` workflow.
3. **Synthesis:** The AI reads the new KIs and automatically synthesizes the theoretical concepts into the `01_` through `09_` pillar documents while strictly enforcing the Timelessness mandate.
4. **Physical Map Update:** If directories were changed, the AI updates `.agents/rules/04_directory_reference.md` directly.

This creates a "Write-Once, Synthesize-Everywhere" paradigm that ensures the global architecture remains universally accurate without manual chore-work.

## 5. Scientific Verification, Multi-Model Variance & Component Ablation Runbook

To obtain the most rigorous, unbiased empirical verification of the Quorum neurosymbolic runtime and eliminate single-model self-confirmation bias, cache-assisted false consistency, and tokenization artifacts, execute the **Dual-Tier Two-Model Verification Protocol** across two independent foundation model families (Google Gemini and OpenAI GPT).

### 5.1 Environment & Authentication Architecture
1. **Infrastructure Bootstrap vs. Database Credentials (`tenant_secrets`):**
   - Runtime LLM provider (`LLMProvider.AI_STUDIO`, `LLMProvider.VERTEX_AI`, `LLMProvider.OPENAI`, `LLMProvider.ANTHROPIC`), MCP gateway (`SystemConfigMCPGateways`), and observability (`SecretScope.TELEMETRY`, `target_identifier="logfire"`) credentials resolve 100% from PostgreSQL 19 `tenant_secrets` (under `SystemOrganizations.ROOT_SYSTEM` `org_0195f3a0000070008000000000000001` or tenant BYOK `org_<hex32>`) via `SecretService.resolve_llm_key`, `SecretService.resolve_mcp_credential`, and `SecretService.resolve_telemetry_secret`.
   - For local HTTP variance execution against the backend API, ensure `DATABASE_URL`, `JWT_SECRET_KEY`, `KMS_MASTER_KEY_ID`, and `SERVICE_AUTH_SECRET` are configured in `.env` and that local baseline secrets have been seeded from `.env.secrets.local` via `uv run python backend_v2/seed/run_seed.py local`.
2. **Decoupled Authentication Mechanics:**
   - **Macro E2E Variance Runner (`scripts/run_e2e_variance_test.py`):** Communicates over HTTP and SSE with the active FastAPI backend and Arq worker daemon. It authenticates via `POST /api/v2/iam/auth/exchange` using `service_auth_secret` (`settings.service_auth_secret.get_secret_value()`) and `target_user_id="usr_0195f3a00000700a83fd6b3d77c748f4"` (Root Platform Administrator), receives a 15-minute Quorum Local JWT, and automatically refreshes the token at the 13-minute mark (`_get_or_refresh_cli_session`) to prevent `401 Unauthorized` expirations during multi-hour runs, while the backend and worker resolve provider, MCP, and telemetry secrets exclusively from PostgreSQL 19 `tenant_secrets`.
   - **Micro Component Ablation Runner (`scripts/run_ablation_benchmark.py`):** Executes in-process via `scripts/ablation_live_executor.py` directly against `LiteLLMProvider` and `AnchorValidationService` without HTTP or Arq worker overhead. It requires no HTTP JWT token and resolves cognitive tier mappings from `backend_v2/seed/seed_data.json`.

### 5.2 Step 1 — Macro End-to-End Two-Model Production Variance Run
With PostgreSQL 19, Redis, the FastAPI backend (`uv run uvicorn backend_v2.main:app --port 8000`), and the Arq background worker (`uv run arq backend_v2.worker.WorkerSettings`) running, execute the full E2E variance test across both Google and OpenAI model registries:

```powershell
# 1. Execute 3 un-cached production DAG runs per model registry (Google Gemini vs. OpenAI GPT)
#    with default Unicode whitespace perturbation (U+00A0, U+2002, U+2003, U+2009) and 15s cooldowns:
uv run python scripts/run_e2e_variance_test.py --compare-registries google openai --num-runs 3 --no-cache --cooldown-seconds 15 --output-dir data/files/variance_reports

# 2. Run deep differential and root-cause disagreement analysis across the resulting execution IDs:
uv run python scripts/diff_executions.py <google_exec_1> <google_exec_2> <google_exec_3> <openai_exec_1> <openai_exec_2> <openai_exec_3>
```

**Why this guarantees maximum scientific honesty:**
- **`--compare-registries google openai`**: Evaluates the exact same workflow and source documents across two distinct model families (`sys_0195f3a00000700e826807f3bfa3454d` and `sys_0195f3a0000070038ba992b15075498b`), automatically restoring the original workflow registry inside a `try...finally` block upon completion.
- **`--no-cache` + Default Stride Whitespace Perturbation**: Disables semantic and LLM caching and injects distinct non-breaking Unicode spaces into Layer 4 source documents on each run, breaking Byte-Pair Encoding (BPE) token sequence identity and SHA-256 prefix cache hashes while preserving 100% semantic meaning.
- **`--num-runs 3 --cooldown-seconds 15`**: Enables multi-rater Fleiss' Kappa ($\kappa_{\text{Fleiss}}$) and non-redundant binary Shannon Entropy ($\bar{H}$) estimation while preventing upstream RPM rate-limit throttling from skewing Best-of-3 consensus.

### 5.3 Step 2 — Micro 5-Configuration Two-Provider Live Component Ablation
Execute the controlled 5-configuration component ablation benchmark (`1: Full Quorum Bo3 + Lexical Firewall`, `2: Quorum without Lexical Firewall`, `3: Quorum Single-Pass k=1`, `4: Atom-Level Unconstrained Judge`, `5: Monolithic Step-Level Judge`) across all $N = 220$ proposition frames (`Pair A: Remote Work Policy` and `Pair B: Strategic Foresight / Sitra`) on both providers:

```powershell
# 1. Live Dual-Provider Component Ablation (AI Studio Gemini vs. OpenAI GPT) with blinded human audit manifest export:
uv run python scripts/run_ablation_benchmark.py --mode live --config all --runs 2 --compare-providers ai_studio openai --strictness 85 --export-manifest all --manifest-format csv

# 2. Zero-Token Replay Strictness Sensitivity Sweep across frozen production execution traces:
uv run python scripts/run_ablation_benchmark.py --mode replay --config all --strictness-levels 0 50 70 85 100

# 3. Zero-Token In-Silico Stress Test (19.7% chimera attack pressure and 0.9% transient API drop pressure):
uv run python scripts/run_ablation_benchmark.py --mode in-silico --config all --inject-chimera-rate 0.197 --inject-dlq-rate 0.009
```

**Key Scientific Outputs Produced (`data/files/ablation_reports/`):**
- **Within-Provider & Cross-Provider Agreement**: Reports Observed Raw Agreement ($P_o$), Cohen's Kappa ($\kappa_{\text{Cohen}}$), Fleiss' Kappa ($\kappa_{\text{Fleiss}}$), and cross-provider inter-rater reliability (`cross_provider_kappa` between `ai_studio` and `openai`).
- **Hierarchical Cluster-Bootstrapped Confidence Intervals**: Reports both naive asymptotic standard errors and two-stage cluster-bootstrapped 95% confidence intervals (`ClusterBootstrapMetricsDTO`, $K = 10$ step clusters, $B = 2,000$ iterations) accounting for intra-batch correlation ($\text{Deff}^{1/2}$).
- **Mechanistic Defense Quantification**: Measures exact Chimera Quote Interception Rate ($\text{Specificity}_{\text{lex}} = 1.000$ in Configuration 1 vs. unanchored leakage in Configuration 2) and Monolithic Criterion Omission Rate (`DLQ` in Configuration 5).
- **Blinded Human Calibration Manifest (`--export-manifest all --manifest-format csv`)**: Exports a deterministic, randomized CSV manifest stripping internal system verdicts so domain experts can perform blind manual annotation to establish external construct validity ($\widehat{\text{PPV}}$, $\widehat{\text{FOR}}$, and human–AI $\kappa$).
