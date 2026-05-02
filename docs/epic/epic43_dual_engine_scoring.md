# Epic 43: Dual-Engine Scoring Architecture

## 1. Yhteenveto (Executive Summary)
Tavoitteena on mahdollistaa kahden täysin erillisen matemaattisen arviointimallin (Waterfall / Auditointi ja Dampening / Valmennus) vapaa valinta käyttöliittymästä, saumattomasti yhdessä Epic 42:n Kireystason (Strictness Level 0-100) kanssa.

**Liiketoiminta-arvo:** Mahdollistaa saman SaaS-alustan myymisen sekä armottomaan compliance-auditointiin että psykologiseen HR-valmennukseen, säilyttäen täyden arkkitehtonisen eheyden (Zero-Trust).

## 2. Arkkitehtoniset Tavoitteet
- **Laskennan eriyttäminen (Decoupling):** Matematiikka pidetään täysin erillään Pydantic-validaatioista. Laskentafunktiot elävät eristettyinä tiedostossa `backend_v2/utils/math_utils.py`.
- **DRY-periaate (Don't Repeat Yourself):** Pydantic-validaatiot (Kireystason `IMPLIED_INTENT` vs `EXPLICIT_QUOTE`) ja tekoälyn LLM-haut pysyvät samoina. Laskentamalli on ainoastaan "kytkin", joka muuttaa sokeiden `True/False` -osumien muuntamista lopulliseksi arvosanaksi Hook-kerroksessa.

## 3. Tekniset Vaatimukset (Backend)

### 3.1. Tietokanta ja Mallit (Pydantic / Enums)
- **Uusi Enum:** Lisätään `ScoringStrategy` (Arvot: `WATERFALL_FLOOR`, `PROGRESSIVE_DAMPENING`) domain-malleihin.
- **Päivitys:** `ExecutionCreate` ja `ExecutionRecord` DTO-malleihin lisätään `scoring_strategy` -kenttä (oletuksena `WATERFALL_FLOOR`).

### 3.2. Hook-Kerros (`backend_v2/hooks/scoring.py`)
- Muutetaan nykyinen `waterfall_scoring_hook` dynaamiseksi `matrix_scoring_hook` -hookiksi.
- Lisätään haaroitus: `if execution.scoring_strategy == ScoringStrategy.PROGRESSIVE_DAMPENING:`
- Haaroituksesta kutsutaan olemassa olevaa `calculate_progressive_dampening_score` -funktiota.
- Muuten kutsutaan nykyistä `calculate_waterfall_floor` -funktiota.

### 3.3. Synteesi-Hook (`text_consolidation_hook.py`)
- Varmistetaan, että valittu `scoring_strategy` siirtyy kirjoittaja-tekoälyn kontekstiin, jotta tekoäly osaa mainita raportissa, kummalla asteikolla auditointi suoritettiin (esim. "Tämä on valmennuksellinen arvio..." vs. "Tämä on tiukka compliance-auditointi...").

## 4. Tekniset Vaatimukset (Frontend / Flutter)
- **Käyttöliittymä (Työnkulun käynnistys):** Sama modal-ikkuna, missä valitaan Kireystaso (Slider 0-100), päivitetään sisältämään Radio Button tai Dropdown-valikko matemaattiselle mallille.
- **Valintavaihtoehdot:**
  - `[x] Auditointi-laskenta (Waterfall - Vaatii ehdottoman loogisen ketjun)`
  - `[ ] Valmennus-laskenta (Dampening - Palkitsee potentiaalista)`
- Valittu parametri lähetetään backendin `POST /executions` -rajapintaan.

## 5. Taaksepäin yhteensopivuus ja Migraatio
- Kaikki olemassa olevat työnkulut ja oletusajot käyttävät automaattisesti `WATERFALL_FLOOR` -strategiaa. 
- Nollatason migraatiota vanhaan tietokantaan ei tarvita; jos kenttä puuttuu, Pydantic default = Waterfall.
