# Epic 67 Master Tracker: Provider-Agnostic Context Caching & FinOps Optimization

Tämä seurantaohjelma (tracker) valvoo ja ohjaa Epic 67:n tarjoajariippumattoman prompt-cachingin, static-first -promptoinnin ja FinOps-kuluseurannan vaiheittaista ja ryntäyssuojattua käyttöönottoa Cognitive Quorum V2 -arkkitehtuurissa.

## Suoritustila (Execution Pipeline)

- [OK] [phase1_caching_models.md](file:///c:/src/quorum/docs/epic/tasks_epic_67/phase1_caching_models.md) - Core-tietomallit (`CompiledPrompt`) ja kääntäjän eristävä sovitin (`PromptCompilerAdapter`)
- [OK] [phase2_adapter_factory.md](file:///c:/src/quorum/docs/epic/tasks_epic_67/phase2_adapter_factory.md) - Abstrakti `BaseLLMAdapter`, sovittimen tehdas (`LLMCacheAdapterFactory`) ja `MockCacheAdapter`-testi-infrastruktuuri
- [OK] [phase3_metadata_adapters.md](file:///c:/src/quorum/docs/epic/tasks_epic_67/phase3_metadata_adapters.md) - Anthropic Claude (rooliryhmitys, lohkotägit) ja OpenAI/DeepSeek (pass-through) sovittimet
- [OK] [phase4_vertex_adapter.md](file:///c:/src/quorum/docs/epic/tasks_epic_67/phase4_vertex_adapter.md) - Google Vertex AI välimuistinhallinta, Redis-lukitus (`SETNX`) ja odotussilmukat ryntäyssuojaukseen
- [OK] [phase5_provider_executor_integration.md](file:///c:/src/quorum/docs/epic/tasks_epic_67/phase5_provider_executor_integration.md) - `LLMCachingService`-julkisivu, `LiteLLMProvider`-päivitys ja `LLMTaskExecutor.execute_structured_task`-kytkentä
- [OK] [phase6_finops_and_purity_guard.md](file:///c:/src/quorum/docs/epic/tasks_epic_67/phase6_finops_and_purity_guard.md) - Moniulotteinen `TokenUsage`, ROI-laskennat, `Purity Scanner` -valvonta ja `PROMPT_CACHING_DRIFT_ALERT`-kuluhälytykset

---

## Universal Hardening Loop Mandate

Kun kaikki tiedostot on muutettu ja testit ovat vihreitä, on ehdottomasti suoritettava backend-auditointi:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/prompt.py backend_v2/services/orchestrator/prompt_compiler_adapter.py backend_v2/llm/adapters/base_adapter.py backend_v2/llm/adapters/adapter_factory.py backend_v2/llm/adapters/mock_adapter.py backend_v2/llm/adapters/anthropic_adapter.py backend_v2/llm/adapters/openai_adapter.py backend_v2/llm/adapters/vertex_adapter.py backend_v2/llm/caching_service.py backend_v2/llm/provider.py backend_v2/services/llm_task_executor.py backend_v2/models/enums.py backend_v2/models/domain/usage.py backend_v2/services/usage_service.py
```

---

## Clean-Slate Database Reset & Seed

Koska tietomalleista katkaistaan legacy-taaksepäinyhteensopivuus puhtaan arkkitehtuurin saavuttamiseksi, suorita testien päätteeksi uusi seedaus:
```powershell
uv run python scripts/run_seed.py
```

---

## Handover Instructions

Käynnistääksesi jatkuvan toteutussilmukan (continuous loop):
1. **Avaa uusi, täysin puhdas keskusteluikkuna (Context Window)** 'Context Amnesian' ja sääntörikkomusten ehkäisemiseksi.
2. Kopioi ja aja seuraava komento uudessa ikkunassa:
   ```powershell
   /tier5-resume --target docs/epic/EPIC_67_tracker.md
   ```
