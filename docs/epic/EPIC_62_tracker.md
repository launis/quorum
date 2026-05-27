# Epic 62 Master Tracker: LLM Concurrency Hardening & Universal Provider Decoupling

Tämä seurantadokumentti (Tracker) valvoo **Epic 62** -suunnitelman vaiheittaista toteutusta. Epicin tavoitteena on poistaa kovakoodatut konesalisidokset, toteuttaa dynaaminen ympäristömuuttujien interpolointi `additional_params` -kenttien kautta, parantaa rate-limit -sietokykyä eksponentiaalisella jitter-perääntymisellä ja ottaa käyttöön universaali välimuistin hallinta.

## Aktiiviset Vaiheet ja Tehtävät (Phased Checklist)

### [ ] Phase 1: Tietokannan ja Seeding-rakenteen Päivitys (Database Refactoring)
- [ ] Varmuuskopioi seed-lähdetiedosto `backend_v2/seed/seed_data.json` ennen muutoksia.
- [ ] Päivitä Google-pohjaisten mallistrategioiden `vertex_location` -kovakoodaukset dynaamiseksi viitteeksi `"additional_params": {"vertex_location": "${VERTEX_LOCATION}"}`.
- [ ] Aja siementietokannan päivitys komennolla `uv run python backend_v2/seed/run_seed.py`.

### [ ] Phase 2: Dynaamisen Ympäristöresoluution Toteutus (Provider Decoupling)
- [ ] Kirjoita apufunktio `resolve_env_variables(params: dict[str, Any]) -> dict[str, Any]` tiedostoon `backend_v2/llm/provider.py`.
- [ ] Poista `provider.py` -koodista kaikki kiinteät `VERTEX_LOCATION` -ympäristömuuttujaviitteet ja kovakoodatut sijaintikaatumiset.
- [ ] Sovella `resolve_env_variables` -metodia `self._config.additional_params` -sanakirjalle ja pura (`**`) se osaksi `acompletion`-kutsua.

### [ ] Phase 3: Jitter-perääntymisen Integrointi (Retry Resiliency)
- [ ] Korvaa `provider.py` -tiedoston kiinteä tenacityn `wait_fixed`-odotus dynaamisella `wait_combine(wait_exponential(multiplier=2, min=2, max=30), wait_random(1, 5))` -odotuksella.
- [ ] Päivitä lokitus viestimään dynaamisesta eksponentiaalisesta odotuksesta perääntymisen aikana.

### [ ] Phase 4: Universaalin Välimuistin Hallinnan Päivitys (Context Caching)
- [ ] Päivitä `client.py` dynaamisesti soveltamaan cache_control-tageja riippuen `self._config.caching_strategy` -arvosta (esim. `anthropic_ephemeral`, `gemini_native`).

### [ ] Phase 5: Laadunvarmistus & Laatuportti (Verification Loop)
- [ ] Kirjoita uusi yksikkötesti `test_adaptive_retry.py` testaamaan backoffin toimivuutta ja transienttien virheiden käsittelyä.
- [ ] Suorita staattinen backend-laatuporttitarkistus komennolla `/tier2-hardening-backend`.

---

## Universal Hardening Loop Mandate
Kun kaikki työvaiheet on saavutettu, aja backend-laatuporttisilmukka:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/ --test
```
varmistamaan eheyden säilyminen.

---

## Handover-ohjeet (Handover Instructions)
Aloittaaksesi suorituksenFresh-ikkunassa:
1. Avaa uusi konteksti-ikkuna.
2. Aja käynnistyskomento: `/tier5-resume --target docs/epic/EPIC_62_tracker.md`
