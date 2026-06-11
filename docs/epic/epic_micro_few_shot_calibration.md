# Epic: Micro-Few-Shot Calibration Architecture (Standalone)

## Tiivistelmä (Executive Summary)

**Tämä Epic on eristetty Bilingual Schema -pääepicistä (Phase 1-5), ja se toteutetaan omana itsenäisenä kokonaisuutenaan vasta kun järjestelmään on ajettu riittävästi oikeaa dataa ja `diff_executions.py` on kerännyt merkittävän määrän aitoja Mismatch Trace -havaintoja.**

### Ongelman kuvaus
LLM-as-a-judge -mallit kärsivät "Out-of-Domain Few-Shot Degradation" -ongelmasta, jossa globaalit system promptin esimerkit eivät siirry uusiin aihealuisiin tai kieliin. Jos mallille syötetään pelkkä sääntö, konfirmaatiovinouma (Confirmation Bias) johtaa siihen, että malli keksii osumia tyhjästä.

### Ratkaisu (Micro-Few-Shot via Contrastive Rule Pairs)
Few-Shot esimerkit sidotaan suoraan yksittäiseen TDA-atomiin (Rule-Level Alignment) Pydantic-skeemassa (`contrastive_example: I18nText`). Prompt Compiler injektoi esimerkit (1 PASS, 1 FAIL) dynaamisesti suoraan kunkin säännön XML-lohkoon, opettaen mallille **kognitiivisen rajanvedon** riippumatta kohdetekstin aihealueesta.

---

## Kriittiset Arkkitehtuuririskit ja Mitigaatiot (System 2 Analyysi)

| Riski (2025-2026 Tutkimus) | Vaikutus | Pakollinen Mitigaatio |
|---|---|---|
| **1. Token Bloat (MECW)** | Kaikkien 186 atomin varustaminen esimerkeillä räjäyttää promptin (18 600+ lisätokenia), johtaen "Lost in the Middle" -hajoamiseen. | `contrastive_example` lisätään **VAIN 20-40 korkean varianssin atomille**, ei kaikille. |
| **2. Anchoring Bias** | LLM "ankkuroituu" esimerkin pintakuvioihin (esim. tiettyyn sanaan) ja hylkää validit osumat, joista kuvio puuttuu. | Esimerkin reasoning-kentän on oltava **abstrakti ja rakenteellinen**, se ei saa toistaa yksittäisiä sanoja. |
| **3. Overfitting** | Liian spesifiset esimerkit opettavat mallin muistamaan kaavan, eikä soveltamaan sääntöä tuotannossa. | **1 pari per atomi** (PASS/FAIL). Ei enempää ellei varianssidatalle ole tarvetta. |
| **4. Authoring Burden** | 186 atomin manuaalinen esimerkkien kirjoittaminen molemmilla kielillä on mahdoton urakka. | **Data Flywheel:** `mismatch_traces_raw.md` syöttää aidot LLM:n tekemät FAIL-virheet suoraan tietokantaan esimerkeiksi. |

---

## Toteutuksen askeleet (Kun dataa on kerätty)

### Phase 1: Tietokantamigraatio (High-Variance Atoms)
1. Tunnista `mismatch_traces_raw.md` tai `diff_executions.py` raporttien perusteella top 20 korkeimman varianssin atomia (esim. atomin `confidence` putoaa jatkuvasti alle 0.67 Best-of-Three ajoissa).
2. Aja ETL-skripti, joka lisää näihin 20 atomiin `contrastive_example: I18nText` Pydantic-rakenteen.
3. Rakenna PASS/FAIL -esimerkkiparit puhtaasti järjestelmän löytämien aitojen rajatapausten pohjalta. 

**Esimerkki (Toulmin: Absoluuttinen varmuus):**
```xml
<contrastive_few_shot>
  <example type="PASS">
     <quote>"Tämä uusi teknologia tulee takuuvarmasti korvaamaan kaiken ihmistyön."</quote>
     <reasoning>Tulevaisuuden arvio on esitetty absoluuttisena totuutena ilman varaumia. Sääntö täyttyy.</reasoning>
  </example>
  <example type="FAIL">
     <quote>"Vesi kiehuu aina 100 celsiusasteessa merenpinnan tasolla."</quote>
     <reasoning>Lause kuvaa todennettavissa olevaa luonnontieteellistä faktaa, ei subjektiivista ennustetta. Osuu anti_pattern-sääntöön. Sääntö EI täyty.</reasoning>
  </example>
</contrastive_few_shot>
```

### Phase 2: Kooditason Injektio (`localization_compiler.py`)
1. Muokkaa `backend_v2/services/orchestrator/localization_compiler.py` (Metodi: `compile_xml_rubrics`).
2. TDAAssertion -iteraation (assertion-loopin) sisällä, koodaa dynaaminen tarkistus ja injektio:

```python
contrastive = getattr(assertion, "contrastive_example", None)
if contrastive:
    resolved = self.resolve_i18n(contrastive, target_locale)
    if resolved:
        rule_text += f"\n<contrastive_few_shot>\n{resolved}\n</contrastive_few_shot>"
```

3. Varmista asynkroninen suoritus (TaskGroup) ja Pydantic Strict-mode (`ConfigDict(strict=True)`).

### Phase 3: Validointi ja Datan Keräys
1. Aja `backend_audit_loop.py` uusilla esimerkeillä.
2. Vertaile Cohen's κ (Kappa) -arvoa vanhaan. Tavoitteena varianssin absoluuttinen pieneneminen yli 0.85 tason.
3. Jos varianssi siirtyy toiseen suuntaan (Overfitting), abstrahoi `contrastive_example` -tekstejä vähemmän pintakuvioihin nojautuviksi.
