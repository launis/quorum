# Epic 40 — Työskentelyohje (Jatkuva Protokolla)

> Tämä tiedosto on pysyvä ohje. Lue se **joka ikkunan alussa** ennen töiden aloittamista.

---

## Mikä tämä epic on?

Epic 40 on `docs/architecture/`-dokumenttien systemaattinen auditointi ja päivitys vastaamaan
nykyistä koodipohjaa. Työ on jaettu milestoneihin, joista jokainen tehdään **omassa 
konteksti-ikkunassaan**.

**Periaate: Koodi on totuus. Dokumentaatio seuraa koodia, ei toisinpäin.**

---

## Tiedostorakenne

```
docs/epic/
├── epic40_architecture_doc_audit.md          ← Master-suunnitelma (kaikki 7 milestonea)
├── epic40_working_guide.md                   ← TÄMÄ TIEDOSTO
└── tasks_architecture_audit/
    ├── m2_orchestrator_strategies.md         ← M2 taskitiedosto (ensimmäinen)
    ├── m1_services_layer.md                  ← M1 taskitiedosto
    ├── m3_domain_models.md                   ← M3 taskitiedosto
    └── ...
```

---

## Järjestys ja Edistymisen Seuranta

> **Tämä taulukko ON edistymisen seuranta.**  
> AI päivittää Status-sarakkeen `✅ Valmis` automaattisesti jokaisen milestonen lopussa.  
> Seuraava ikkuna lukee tämän tiedoston ja tietää mistä jatkaa.

| # | Milestone | Status | Taskitiedosto |
|---|---|---|---|
| **M2** | Orchestrator Strategiat | ✅ Valmis | `m2_orchestrator_strategies.md` |
| **M1** | Backend Services Layer | ✅ Valmis | `m1_services_layer.md` |
| **M3** | Domain Models | ✅ Valmis | `m3_domain_models.md` |
| **M4** | Hooks & LLM täydennys | ✅ Valmis | `m4_hooks_llm.md` |
| **M5** | Flutter Client | ✅ Valmis | `m5_flutter_client.md` |
| **M6** | Persistointi & Infra | ✅ Valmis | `m6_persistence_infra.md` |
| **M7** | API & Core Registry | ✅ Valmis | `m7_api_core.md` |

**Seuraava suoritettava milestone:** Ensimmäinen `⬜ Tekemättä` -rivi ylhäältä.

---

## Protokolla per ikkuna

### Vaihe 1 — Ikkunan avaus (kopioi tämä prompti)

```
/tier3-feature-refactor

Lue ensin tämä työskentelyohje JA tarkista edistymistaulukko:
c:\src\quorum\docs\epic\epic40_working_guide.md

Lue master-suunnitelma tarvittaessa:
c:\src\quorum\docs\epic\epic40_architecture_doc_audit.md

Toteuta SEURAAVA ⬜ Tekemättä -milestone edistymistaulukon mukaan.
Taskitiedosto löytyy: c:\src\quorum\docs\epic\tasks_architecture_audit\[tiedostonimi]
```

### Vaihe 2 — Milestone-sessio

AI tekee seuraavassa järjestyksessä:
1. **Lukee** `epic40_working_guide.md` → selvittää mikä milestone on seuraavana
2. **Lukee** vastaavan taskitiedoston
3. **Lukee** kaikki taskitiedostossa listatut kooditiedostot
4. **Tunnistaa** puutteet vertaamalla koodiin ja nykyiseen dokumentaatioon
5. **Esittää löydökset** — sinä hyväksyt tai pyydät muutoksia
6. **Kirjoittaa** dokumentaatiomuutokset
7. **Näyttää diffit** — sinä hyväksyt

### Vaihe 3 — Milestonen päätyttyä (AI tekee automaattisesti)

AI päivittää tätä tiedostoa:
- Status `⬜ Tekemättä` → `✅ Valmis` kyseiselle milestonelle
- Lisää merkintä Suorituslogiin (alla)
- Sulje ikkuna — seuraava ikkuna tietää automaattisesti mistä jatkaa

---

## Tarkistusrutiini uuden ikkunan alussa

Ennen töiden aloittamista AI tarkistaa:
- [ ] Mikä milestone on seuraavana jonossa (tämä tiedosto, Status-sarake)
- [ ] Onko vastaava taskitiedosto olemassa `tasks_architecture_audit/`-hakemistossa
- [ ] Onko aiempi milestone todellisuudessa valmis (doc päivitetty)

---

## Hyväksyntäsäännöt

- **Dokumentaatiomuutokset:** Sinä hyväksyt jokaisen `multi_replace_file_content`-kutsun
- **Uudet tiedostot:** Sinä hyväksyt uuden doc-tiedoston sisällön ennen kirjoittamista
- **Koodimuutokset:** Ehdottomasti kielletty tässä epicissä

---

## Muistiinpanot edellisistä sessioista

### Sessio 2026-04-26 (Alkusessio)
- Päivitetty: `04_hooks_and_llm.md` — synthesis.py + reporting.py detail
- Päivitetty: `08_dynamic_rendering_engine.md` — Token Shield fix + SDUI §6
- Korjattu: `synthesis.py` L341 — `if not` → `if ... is None`
- Luotu: Epic 40 master-suunnitelma ja M2 taskitiedosto

---

## Suorituslog (AI täyttää automaattisesti)

| Päivämäärä | Milestone | Muutetut tiedostot |
|---|---|---|
| 2026-04-26 | Alkusessio (ei milestone) | `04_hooks_and_llm.md`, `08_dynamic_rendering_engine.md` |
| 2026-04-26 | M2 — Orchestrator Strategiat | `03b_orchestrator_strategies.md`, `03_business_services_and_dag.md` |
| 2026-04-26 | M1 — Backend Services Layer | `03_business_services_and_dag.md` |
| 2026-04-26 | M3 — Domain Models | `02_domain_models.md` |
| 2026-04-26 | M4 — Hooks & LLM täydennys | `04_hooks_and_llm.md` |
| 2026-04-26 | M5 — Flutter Client | `06_desktop_first_flutter_client.md` |
| 2026-04-26 | M6 — Persistointi & Infra | `05_data_persistence_and_seeding.md`, `07_infrastructure_and_observability.md` |
| 2026-04-26 | M7 — API & Core Registry | `01_backend_api_and_core.md` |
