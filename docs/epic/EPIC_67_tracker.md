# Epic 67 Master Tracker: Provider-Agnostic Context Caching & FinOps Optimization

This tracker monitors the phased implementation of Epic 67 to implement provider-agnostic prompt caching adapters, static prompt compilation, and cost-tracking telemetry.

## Active Phases
- [ ] **Phase 1: High-Fidelity Static Prompt Isolation** - Restructure `prompt_compiler.py` and `LLMTaskExecutor` to isolate dynamic steering parameters to dynamic user messages, ensuring that large systemic prompt structures and source inputs remain 100% static across runs.
- [ ] **Phase 2: Unified Caching Service** - Create `backend_v2/llm/caching_service.py` with multi-provider mapping (Vertex AI explicit cache initialization, Anthropic `cache_control` block tags, and OpenAI/DeepSeek automatic prefix matching).
- [ ] **Phase 3: LLMTaskExecutor Integration** - Intercept outbound structured tasks to calculate size and apply caching payloads before execution.
- [ ] **Phase 4: Telemetry & Cost Accounting** - Capture `cached_tokens` inside `LiteLLMProvider` and update `UsageService` to persist cache hits and apply appropriate pricing discounts.
- [ ] **Phase 5: Self-Healing & Fallback Tests** - Write unit/integration tests confirming that explicit cache failures trigger clean, non-blocking fail-soft default executions.

## Universal Hardening Loop Mandate
When all modified files are completed, the user must run:
```powershell
/tier2-hardening-backend
```
to audit PEP 257 standards and complete the Quality Gate verification.

---

## Handover Instructions
To start the execution loop:
1. Open a fresh context window.
2. Run command: `/tier5-resume --target docs/epic/EPIC_67_tracker.md`
