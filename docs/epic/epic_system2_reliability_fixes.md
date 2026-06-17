# EPIC: System 2 Reliability Fixes & Fuzzy Match Integration

## 1. Nykytila (Baseline)

| Metriikka | Arvo | Tulkinta |
|---|---|---|
| **Cohen's κ** | 0.6189 | "Substantial Agreement" (Landis & Koch). Hyvä, mutta ei vielä "Almost Perfect" (κ > 0.8) |
| **Self-Consistency** | 80.88% | ~1/5 atomista vaihtuu ajosta toiseen |
| **Mismatchit** | 26 / 136 | 19.1% varianssi |
| **PASSED→FAILED** | 9 | LLM löytää "todisteita" vain toisinaan |
| **FAILED→PASSED** | 17 | **Tämä on pääongelma:** LLM keksii perusteluita jotka eivät ole johdonmukaisia |
| **DLQ** | 4–24 / ajo | Korkea — laskee kappaa ja tuhlaa laskentaa |

> [!CAUTION]
> Molemmat ajot käyttivät **jo ENSEMBLE=3** (Best-of-Three) -tilaa matriisitasolla (`is_lightweight_protocol = True`). Jos edes enemmistöäänestys ei pysty tasoittamaan tulosta, se on absoluuttinen todiste siitä, että säännöt (`concept_description`) ovat LLM:lle liian tulkinnanvaraisia!

---

## 2. Arkkitehtuurin Laajuus ja Ongelmat

### Strictness Level
`strictness_level` vaikuttaa tällä hetkellä järjestelmän kolmeen ytimeen:
1. **Matemaattiset Rangaistukset:** Ohjaa `StrictnessConfig`-profiilin avulla pisteiden armottomuutta (waterfall/dampening).
2. **Prompt Directives:** Injektoi `SCORING_STRICTNESS: {val}/100` ohjaamaan LLM:n asennetta.
3. **Override Ban:** Pakottaa tiukkuuden tasolle 100 tietyissä protokollissa kieltäen selitykset.

**Puuttuva pala (Fuzzy Match):** Tällä hetkellä `AnchorValidationService` vaatii 100 % eksaktia teksti-osumaa eikä hyödynnä `strictness_level`iä laisinkaan. RapidFuzz on vain lokitusta varten. Tämä tuottaa massiivisesti ylisovittamista puhtaalle datalle ja aiheuttaa False Negative -virheitä OCR/PDF -skannauksissa.

### Ylisovitusriski (Overfitting Hazard) - KRIITTINEN
Tämänhetkiset testit ajettiin Sitran raporttidatalla. Jos sääntöjä tiukennetaan tai promptien esimerkkejä ("contrastive_example") kirjoitetaan liian tarkasti juuri tähän dataan sopiviksi, järjestelmä romahtaa erilaisen datan edessä.
*Vaatimus:* Kaikkien uusien `contrastive_example` -esimerkkien on oltava täysin abstrakteja ja toimialariippumattomia (Domain-Agnostic).

---

## 3. Implementation Plan

Tavoitteena on nostaa luotettavuus (Kappa) tilaan "Almost Perfect" (0.75+) ja pudottaa DLQ nollaan, ilman overfittausta.

### Phase 1: Arkkitehtuuritason Luotettavuus (Koodi)

Tämä vaihe poistaa False Negative -virheet ja tekniset DLQ-epäonnistumiset.

#### [MODIFY] `c:\src\quorum\backend_v2\models\enums.py`
- Nosta `SystemConcurrency.FAIL_FAST_MAX_RETRIES` arvo 3:sta -> 5:een. Tämä pudottaa 24 DLQ-virhettä lähelle nollaa antamalla LLM:lle tilaa toipua Pydantic-skeemavirheistä.

#### [MODIFY] `c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py`
- Muuta `validate_evidence` ottamaan vastaan `strictness_level: int = 50`.
- Poista 100 % osuman kova vaatimus ja korvaa se **Dynaamisella Lerp-kaavalla**:
  1. Hae `base_threshold` (esim. FI = 80.0) käyttäen `get_lexical_fuzz_threshold(locale)`.
  2. Jos `strictness_level == 100`, kynnys = 100.0 (Fuzzy pois päältä).
  3. Jos `50 <= strictness_level < 100`, laske: `base + ((strictness_level - 50) / 50.0) * (100.0 - base)`.
  4. Jos `strictness_level < 50`, laske joustavasti alaspäin minimikynnykseen (esim. 60.0).
  5. Jos `fuzz.partial_ratio(quote, text) >= kynnys`, hyväksy osuma ja ohita `SemanticEvidenceError`.

#### [MODIFY] `c:\src\quorum\backend_v2\services\orchestrator\strategies\llm_execution\chunk_worker.py`
- Varmista että UI:lta / työnkulusta tuleva `strictness_level` välitetään loppuun asti `AnchorValidationService.validate_evidence` -kutsulle.

### Phase 2: Data-tason Robustius (Seed Data Prompt Engineering)

Tämä vaihe poistaa False Positive -virheet (johtuen liian moniselitteisistä säännöistä). Kohdistamme muutokset *vain* niihin 26 atomiin, jotka todistettavasti vaihtelivat R1/R2-ajoissa (`mismatch_traces_raw.md`).

#### [MODIFY] `c:\src\quorum\backend_v2\seed\seed_data.json`
- **Abstraktit Contrastive Esimerkit:** Lisää `contrastive_example` -kenttä kaikkein epävakaimmille atomeille (esim. "tarkka mekanismi", "yksisuuntaiset komennot"). Esimerkit muodossa: *Hyväksytty:* "X vaikuttaa Y:hyn Z:n kautta". *Hylätty:* "X liittyy Y:hyn".
- **Concept Description -tarkennus:** Lisää ongelmallisimpiin kuvauksiin yksiselitteinen lause siitä, mitä asioita ei pidä sekoittaa keskenään.

#### [EXECUTE] Paikallinen Seedaus-ajo
- Ajetaan `uv run python backend_v2/seed/run_seed.py local` muutosten jälkeen. Y-Funnel arkkitehtuuri puskee prompti-muutokset lokaaliin tietokantaan turvallisesti.

## 4. Verification Plan

- **Automated Tests:** `uv run python scripts/backend_audit_loop.py . --test` varmistamaan, että `test_chunk_dlq_fallback_bug.py` ja muut validointitestit menevät läpi uudella Fuzzy Match -moottorilla.
- **Unit Tests:** Päivitä testi `AnchorValidationService` -luokalle todistamaan Lerp-kaavan toiminta.
- **Manual Verification:** Käynnistä uusi arviointiajo (`diff_executions.py`) varmistamaan, että DLQ:t ovat kadonneet ja κ-arvo lähestyy 0.75-0.80 rajaa.
