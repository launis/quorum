# EPIC: System 2 Reliability Fixes & Fuzzy Match Integration

## 1. Nykytila (Baseline)

| Metriikka | Arvo | Tulkinta |
|---|---|---|
| **Cohen's κ** | 0.6189 | "Substantial Agreement" (Landis & Koch). Varsin solidi taso monimutkaisessa tekstianalyysissä. |
| **Self-Consistency** | 80.88% | ~1/5 atomista vaihtuu ajosta toiseen |
| **Mismatchit** | 26 / 136 | 19.1% varianssi |
| **DLQ** | 4–24 / ajo | Korkea — tuhlaa laskentaa ja sekoittaa prosessia |

> [!CAUTION]
> Matriisitasolla on jo käytössä **ENSEMBLE=3** (`is_lightweight_protocol = True`). Jos enemmistöäänestys ei pysty tasoittamaan tulosta, se todistaa että kyseessä on sääntöjen semanttinen tulkinnanvaraisuus ja LLM:n "Yes Man" -bias.

---

## 2. Järjestelmän Filosofiset ja Arkkitehtuuriset Rajat

### LLM Ei Ole Tilakone (Human Inter-Rater Reliability -katto)
Avoimen, kapulakielisen tekstin analysoinnissa on matemaattisesti epärealistista tavoitella "Almost Perfect" (Cohen's κ > 0.80) -tasoa. Jopa kaksi asiantuntijatason ihmistä jäävät kompleksisten konseptien poiminnassa usein 0.70–0.85 väliin, koska luonnollinen kieli on itsessään häilyvää. Stokastisen LLM:n kohdalla 15–20 % epäjohdonmukaisuus on hyväksyttävä ominaisuus, ei bugi.

### Tyhmistämisen Paradoksi (The Dumb-Down Paradox)
Jos järjestelmää pakotetaan saavuttamaan keinotekoinen κ = 0.90, ainoa keino on "tyhmistää" arviointisäännöt niin triviaaleiksi, että koko analyysi menettää liiketoiminta-arvonsa. Haluamme mallin tekevän syvää kognitiivista päättelyä, ja syvän päättelyn sivutuote on tilastollinen varianssi. 

**Realismi:** Odotusarvo ja tavoitetila Phase 2 päivityksen jälkeen on **κ = 0.70 - 0.75** ("Substantial Agreement" -alueen yläpää). 

---

## 3. Implementation Plan

Tavoitteena on saavuttaa realistinen optimi (Kappa 0.70-0.75) ja pudottaa DLQ nollaan, ilman ylisuunnittelua tai ylisovittamista.

### Phase 1: Arkkitehtuuritason Luotettavuus (Koodi)

Tämä vaihe poistaa False Negative -virheet ja tuhoaa LLM:n "Yes Man" -biasin (False Positivet) kooditasolla.

#### [MODIFY] `c:\src\quorum\backend_v2\models\dtos\evaluation_steps.py`
- **Paholaisen Asianajaja (Falsification Attempt):** Lisää uusi `falsification_argument: str` -kenttä sekä `StepDTOStrict` että `StepDTOSemantic` -luokkiin aivan juuri **ennen** `decision` -booleania. 
- Määritä Pydantic-kuvaus (description) vaatimaan, että mallin on keksittävä vähintään yksi vasta-argumentti (esim. *"Why this evidence might NOT satisfy the strict causal requirement of the rule."*) ennen päätöksentekoa.
- Koska LLM generoi JSON:ia autoregressiivisesti (vasemmalta oikealle), negatiivisten tokenien generoiminen ennen booleania pakottaa mallin System 2 -tilaan ja romahduttaa todennäköisyyden generoida perusteeton `true` -arvo.

#### [MODIFY] `c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py`
- Muuta `validate_evidence` ottamaan vastaan `strictness_level: int = 50`.
- Korvaa 100 % osuman vaatimus **Deterministisellä Porraskaavalla (Discrete Tiers) + Entropiaportilla**:
  1. **Entropiaportti:** Jos lainaus (`exact_quote`) on alle 20 merkkiä pitkä, **Fuzzy Match on kielletty** (Vaaditaan 100 %). Estää lyhyiden sanojen hallusinaatio-osumat `partial_ratio`:ssa.
  2. **Deterministiset Portaat (Discrete Tiers):** Kytkemme sumean kynnyksen suoraan `StrictnessAnchor` -enumien tasoihin:
     - `ABSOLUTE (100)`: 100.0 % (Fuzzy pois päältä)
     - `STRICT (85)`: 95.0 % (Sallii pienen kirjoitus/välimerkkivirheen)
     - `STANDARD (50)`: `base_threshold` (esim. 80.0 %) (Normaali OCR-toleranssi)
     - `RELAXED (30)`: 65.0 % (Raskaan OCR-kohinan sieto)
  3. Jos `fuzz.partial_ratio(quote, text) >= tier_kynnys`, hyväksy osuma.

#### [MODIFY] `c:\src\quorum\backend_v2\services\orchestrator\strategies\llm_execution\chunk_worker.py`
- Varmista että työnkulusta tuleva `strictness_level` välitetään loppuun asti `AnchorValidationService.validate_evidence` -kutsulle.

### Phase 2: Data-tason Robustius (Universal Prompt Structural Audit)

Toteutamme koko sääntökirjastoa koskevan universaalin standardoinnin poistaaksemme mallin "attention" murtumisen.

#### [MODIFY] `c:\src\quorum\backend_v2\seed\seed_data.json`
- **Sääntöluokan Standardi:** Määrittelemme, että *kaikki* atomit, jotka arvioivat kausaliteettia tai kompleksisia mekanismeja, **vaativat** abstraktin `contrastive_example` -kentän (esim. *Hyväksytty:* "X vaikuttaa Y:hyn Z:n kautta". *Hylätty:* "X liittyy Y:hyn").
- Tämä tehdään koko tietokannalle yhtenäisellä logiikalla. Tämä poistaa Testiaineistovuodon ja kognitiivisen kuorman pieneneminen korjaa Pydantic DLQ -virheet luonnollisella tavalla.

#### [EXECUTE] Paikallinen Seedaus-ajo
- Ajetaan `uv run python backend_v2/seed/run_seed.py local` muutosten jälkeen.

## 4. Verification Plan

- **Automated Tests:** `uv run python scripts/backend_audit_loop.py . --test` varmistamaan validointitestien läpimeno.
- **Unit Tests:** Päivitä testi `AnchorValidationService` -luokalle todistamaan Entropiaportti ja determinististen portaiden (Discrete Tiers) toiminta.
- **Manual Verification:** Käynnistä uusi arviointiajo (`diff_executions.py`) varmistamaan, että DLQ:t ovat kadonneet ja κ-arvo asettuu realistiseen liiketoiminnan optimiin (0.70-0.75).
