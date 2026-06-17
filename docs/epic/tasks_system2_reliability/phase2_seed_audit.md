# Phase 2: Universal Prompt Structural Audit
Source: Epic System 2 Reliability Fixes, Phase 2

## Tavoite
Poistaa testiaineistovuoto (Selection Bias) ja LLM:n kognitiivinen kuorma standardoimalla sääntökirjasto universaalisti yli kaikkien kausaliteettia arvioivien atomien.

## Invariantit
- **03_seed_vault.md**: Kaikki datamuutokset tehdään V2 Seed JSON -tiedostoon, ja injektoidaan paikalliseen DB:hen Pydantic Seed Pipeline -kautta.
- **Domain-Agnosticismi**: Kaikkien uusien contrastive-esimerkkien on oltava geneerisiä (X/Y/Z) eikä niissä saa viitata mihinkään spesifiin toimialaan tai asiakkaaseen.

## Tiedostot
- **TARGET (Modify)**: `c:\src\quorum\backend_v2\seed\seed_data.json`

## Tehtävät

### 1. Sääntökirjaston Standardi-auditointi
Tiedosto: `seed_data.json`
- Etsi kaikki `PromptBlock` (atomit), jotka arvioivat kausaliteettia (syy/seuraus) tai monimutkaisia mekanismeja.
- Jokaiselle löydetylle kausaali-atomille, pakota tai päivitä abstrakti `contrastive_example` kenttä, joka laskee LLM:n kognitiivista kuormaa.
- **Esimerkkiformaatti:** *Hyväksytty:* "X vaikuttaa Y:hyn Z:n kautta". *Hylätty:* "X liittyy Y:hyn mutta mekanismia ei selitetä."
- Päivitä tarvittaessa `ai_description` erottamaan asiat selkeämmin toisistaan.

### 2. Y-Funnel Seeding
Komentorivi: `uv run python backend_v2/seed/run_seed.py local`
- Aja yllä mainittu komento injektoidaksesi uudet puhtaat säännöt paikalliseen tietokantaan Fail-Fast -validaation läpi.

## Testing & Quality Gate Plan
1. **DB Verifikaatio:** Varmista, että seed script päättyy "SUCCESS" -tilaan ilman Pydantic validation erroreita.
2. **Loppuarviointi (Manual):** Kun sekä Phase 1 että Phase 2 on ajettu, suorita rinnakkaisajo vanhaa lokia vastaan (`diff_executions.py`) varmistaen että DLQ = 0 ja varianssi (15-20%) on enää luonnollista stokastisuutta (Kappa ~0.70-0.75).

---
## Session Handover
Valmis! Siirry Master Trackerin pariin jatkaaksesi prosessia.
