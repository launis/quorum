# Epic 67 Master Tracker: Provider-Agnostic Context Caching & FinOps Optimization

This tracker monitors the phased implementation of Epic 67 to implement provider-agnostic prompt caching adapters, static prompt compilation, and cost-tracking telemetry.

## Active Phases
- [ ] **Phase 1: Tyyppimääritelmät (`CompiledPrompt`)** - Luodaan `CompiledPrompt`-tietomalli tiedostoon `backend_v2/models/prompt.py` ja toteutetaan suoraviivainen `.to_flat_messages() -> list[dict]` -apuohjelma testien ja downstream-kutsujen vihreyden takaamiseksi.
- [ ] **Phase 2: Kääntäjätason (`PromptCompiler`) refaktorointi ja Purity-testaus** - Päivitetään `prompt_compiler.py` palauttamaan `CompiledPrompt` ja varmistetaan staattisen osan SHA-256 -hasheksen deterministisyys.
- [ ] **Phase 3: Rajapinta, Tehdas ja Mock-infrastruktuuri (Core & Mock Adapter)** - Luodaan `BaseLLMAdapter` ja `LLMCacheAdapterFactory` sekä `MockCacheAdapter` rekisteröiden se testitarjoajalle `mock_llm_99` verkkokutsuvapaiden testien takaamiseksi (`mocking_mandate_for_llm`).
- [ ] **Phase 4: Anthropic Claude ja OpenAI -sovittimet (Metadata Caching)** - Toteutetaan `AnthropicCacheAdapter` (rooliryhmitys, raaka content-merkkijonojen muunnos lohkorakenteeksi ja `cache_control` annotaatiot) sekä `OpenAICacheAdapter` (pass-through).
- [ ] **Phase 5: Vertex AI -sovitin ja Natiivit SDK-yhteydet** - Luodaan `VertexCacheAdapter`-perusmalli asynkronisille GCP-kontekstivälimuistikutsuille, palauttaen `cached_content` viitteen `extra_kwargs` sanakirjassa. Kaikki `teardown_cache`-kutsut toteutetaan No-Op (`pass`) blockeina Option B mukaisesti.
- [ ] **Phase 6: Hardening & Synkronointi (Redis-lukitus & Thundering Herd)** - Kapseloidaan jaettu Redis-lukitus (asetus `PX 300000` zombi-tilojen estämiseksi) ja odotussilmukka (500ms poll-viive, 20s odotusraja `SystemConcurrency`-arvojen mukaisesti) `vertex_adapter.py`-tiedostoon.
- [ ] **Phase 7: LiteLLMProvider-integraatio ja parametriohjaus** - Päivitetään `LiteLLMProvider` vastaanottamaan adapterin tuottamat muokatut viestit ja `extra_kwargs` (kuten `cached_content`) ja välittämään ne suoraan LiteLLM-kutsulle.
- [ ] **Phase 8: Task Executor -integraatio ja Fail-Soft -testaus** - Kytketään `LLMCachingService` osaksi `LLMTaskExecutor.execute_structured_task`-metodia ja todennetaan virheiden nielaisu/Fail-Soft.
- [ ] **Phase 9: Moniulotteinen FinOps-seuranta ja ROI-laskenta** - Päivitetään `TokenUsage` tietokantamalli (strict-oletusarvoilla) ja delegoitetaan ROI-kaavat sovittimien `calculate_cost`-metodeille. Jätetään passiivinen Vertex AI tallennusaikalaskenta kokonaan pois koodista.
- [ ] **Phase 10: Purity Scanner ja Cache Drift -hälytykset** - Toteutetaan passiivinen, ainoastaan lokittava (`logger.warning`) Purity Scanner `system`-viesteille sekä `PROMPT_CACHING_DRIFT_ALERT`-alitusvalvonta.

## Universal Hardening Loop Mandate
When all modified files are completed, the user must run:
```powershell
/tier2-hardening-backend [files modified for this epic]
```
to audit PEP 257 standards and complete the Quality Gate verification.

---

## Handover Instructions
To start the execution loop:
1. Open a fresh context window.
2. Run command: `/tier5-resume --target docs/epic/EPIC_67_tracker.md`
