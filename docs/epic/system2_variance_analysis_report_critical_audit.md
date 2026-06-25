# System 2 -varianssiraportin kriittinen auditointi ja toinen mielipide

> **Konteksti**: Tämä asiakirja sisältää System 2 -tason koodi- ja tietokanta-auditoinnin sekä toisen mielipiteen (Second Opinion) liittyen dokumenttiin [system2_variance_analysis_report.md](file:///c:/src/quorum/docs/epic/system2_variance_analysis_report.md). Analyysi keskittyy varmentamaan, onko raportoidut varianssinvähennysominaisuudet implementoitu kokonaisuudessaan, ja nostaa esiin kriittisiä sokeita pisteitä ja korjaustarpeita.

---

## 1. Johdanto ja tavoite

Tämän auditoinnin tavoitteena on selvittää empiirisen analyysin ja lähdekoodin/tietokannan suoran tarkastelun kautta, vastaako nykyinen backend- ja seeding-toteutus [system2_variance_analysis_report.md](file:///c:/src/quorum/docs/epic/system2_variance_analysis_report.md) -dokumentissa esitettyjä lupauksia ja muutoksia. 

Auditoinnissa tutkittiin seuraavat tiedostot:
1. [scoring.py](file:///c:/src/quorum/backend_v2/hooks/scoring.py) (matriisipistelaskenta ja dynaamiset sakot)
2. [chunk_worker.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py) (konsensusäänestys ja pre-flight-sensorit)
3. [lightweight_matrix.py](file:///c:/src/quorum/backend_v2/models/dtos/lightweight_matrix.py) (matriisirakenne, statusmääritykset ja inversiobypass)
4. [evaluation_steps.py](file:///c:/src/quorum/backend_v2/models/dtos/evaluation_steps.py) (CoT-ohjeistuksen yhtenäistäminen)
5. [localization_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/localization_compiler.py) (inversio-ohjeiden poisto)
6. [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) (seeding-prompteihin sallittu CONTESTED ja model_strategy strict-päivitykset)
7. [db_v2.json](file:///c:/src/quorum/data/db_v2.json) (TinyDB:n aktiivinen tila)

---

## 2. Koodin ja tietokannan tila vs. Raportin väitteet

Auditoinnin perusteella System 2 -varianssiraportin toimenpiteet on implementoitu suurilta osin, mutta toteutuksesta löytyy **kolme kriittistä arkkitehtuurista sokeaa pistettä/eroavuutta**, jotka altistavat järjestelmän virheille tai romahduksille.

### 2.1 CONTESTED-tila ja Guttman-matematiikka
* **Väite**: `CONTESTED`-tila tallentuu rajatapauksissa ja bypassaa kooditasolla inversiologian, jolloin se lasketaan True-tyyppiseksi evidenssiksi Guttman-waterfallin jatkumiseksi.
* **Verifiointi koodista**: 
  * Tiedostossa [lightweight_matrix.py](file:///c:/src/quorum/backend_v2/models/dtos/lightweight_matrix.py#L207) luokissa `LightweightExtractionAtom` ja `AtomEvaluationItemDTO` on seuraava toteutus:
    ```python
    if self.status == "CONTESTED":
        return True
    ```
  * Tämä bypassaa `inverse_evidence` -inversiot ja estää Guttman-vesiputouksen katkeamisen epävarmuuden vuoksi.
  * *Tulos*: **Vahvistettu**. Toteutettu oikein.

### 2.2 Kaksiportainen turvalukko (Cognitive Collapse)
* **Väite**: Koko matriisi hylätään tilaan `[INDETERMINATE]`, jos matriisissa on joko yli 3 `CONTESTED`-atomiä (absoluuttinen kynnys) tai yli 50 % kaikista atomeista on `CONTESTED` (suhteellinen kynnys).
* **Verifiointi koodista**:
  * Tiedostossa [scoring.py](file:///c:/src/quorum/backend_v2/hooks/scoring.py#L878-L886) on toteutettu:
    ```python
    cognitive_collapse = n_contested > 3 or (global_total > 0 and (n_contested / global_total) > 0.5)
    ...
    if cognitive_collapse:
        is_indeterminate = True
    ```
  * Jos `is_indeterminate` on tosi, asetetaan `raw_score = None` ja justificationiin asetetaan "[INDETERMINATE] Matrix score invalidated because the cognitive collapse safety lock was triggered...".
  * *Tulos*: **Vahvistettu**. Kognitiivinen romahduslukko on asennettu ja toimii.

### 2.3 Tuplainversio-ansan eliminointi ja kognitiivinen purkutila
* **Väite**: Legacy V1 -inversio-ohjeet on poistettu promptikääntäjästä ja `reasoning_steps` on yhtenäistetty 3-vaiheiseksi auditointijäljeksi.
* **Verifiointi koodista**:
  * Tiedostossa [localization_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/localization_compiler.py) ei ole enää `inverse_evidence` -promptiin liittyviä ehtolausekkeita XML-generoinnissa.
  * Tiedostossa [evaluation_steps.py](file:///c:/src/quorum/backend_v2/models/dtos/evaluation_steps.py#L55) `reasoning_steps`-kentän description on yhtenäistetty muotoon:
    `"Step-by-step mechanical audit trace BEFORE making a decision. Format: '1) Rule requires X. 2) Text provides Y. 3) Y meets/fails X.' Max 3 sentences."`
  * *Tulos*: **Vahvistettu**.

### 2.4 Strategioiden strict-nostot ja Zero-Trust-protokolla
* **Väite**: Analyst, Falsifier, Logician, Overseer ja Judge -solmut nostettu strict-reititykselle (Gemini Pro) ja protokolla sallii `CONTESTED`-arvon.
* **Verifiointi kannasta**:
  * Sekä [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json) että live-tietokanta [db_v2.json](file:///c:/src/quorum/data/db_v2.json) sisältävät kyseiset solmut strategialla `"model_strategy": "strict"`.
  * Globaalin Zero-Trust-protokollan (`blk_573802341db9d68c`) `ai_description` on päivitetty sallimaan `CONTESTED` ja pelottamaan sen ylikäytöstä.
  * *Tulos*: **Vahvistettu**.

---

## 3. Havaitut kriittiset puutteet ja riskit (Critical Gaps)

Koodi- ja logitarkastelun aikana löydettiin seuraavat **sokeat pisteet**, jotka vaativat muutoksia ominaisuuksien luotettavaan loppuunsaattamiseen:

### 3.1 Gap 1: Asymmetrinen konsensus-gating (`resolve_majority_vote` sudenkuoppa)
Tiedoston [chunk_worker.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py#L173-L190) majority vote -äänestys sisältää vakavan asymmetrian:
```python
if pass_votes > fail_votes and pass_votes > contested_votes:
    chosen = best_pass if best_pass else votes[0]
    confidence = pass_votes / total_votes
    if confidence <= 0.67:
        chosen["status"] = "CONTESTED"  # Overridden for PASS majority
    ...
elif contested_votes >= pass_votes and contested_votes >= fail_votes:
    ...
else:
    chosen = best_fail if best_fail else votes[0]
    chosen["status"] = "FAIL"
    chosen["confidence"] = fail_votes / total_votes if total_votes > 0 else 1.0
    # HUOMIO: Ei confidence-gatingia FAIL-enemmistöille!
```
* **Ongelma**: Jos ensemblen 3 ajosta 2 antaa `FAIL` ja 1 antaa `PASS` (confidence 0.67), tulos ohjataan suoraan `else`-haaraan ja palautetaan strict `FAIL`.
* **Vaikutus**: Jos kyseessä on positiivinen sääntö (`inverse_evidence = False`), tämä 2-1 split katkaisee Guttman-waterfallin välittömästi, vaikka 1 malli löysi todisteen ja tilanne oli epävarma. Jos kyseessä on negatiivinen sääntö (`inverse_evidence = True`), tämä 2-1 split hyväksytään virheettömänä PASS-tuloksena ilman mitään rangaistusta, vaikka 1 malli löysi viitteitä rikkomuksesta.
* **Perusteltu korjausehdotus**: Molemmat 2-1 splits (sekä PASS- että FAIL-enemmistöt) on gatedttava epävarmoina `CONTESTED`-tilaan, jotta äänestys on loogisesti symmetrinen ja heijastaa todellista epistemologista epävarmuutta.

### 3.2 Gap 2: Dynaamisen sakon kaavamismatch
* **Ongelma**: [system2_variance_analysis_report.md](file:///c:/src/quorum/docs/epic/system2_variance_analysis_report.md) ehdottaa Liitteessä 3.2 dynaamista, lohkon kokoon suhteutettua sakkoa:
  `penalty_factor = (n_contested / global_total) * 0.15`
  Toteutunut backend-koodi [scoring.py](file:///c:/src/quorum/backend_v2/hooks/scoring.py#L964) käyttää kuitenkin kovaa flat-sakkoa:
  `raw_score = raw_score * (1 - 0.05 * n_contested)`
* **Vaikutus**: 2 atomin pienessä matriisissa 1 contested antaa flat-sakkona 5 % miinusta (proposoitu relative olisi `1/2 * 0.15 = 7.5%`). 20 atomin suuressa matriisissa 1 contested antaa edelleen 5 % sakkoa (proposoitu relative olisi vain `1/20 * 0.15 = 0.75%`). flat-kaava rankaisee suuria matriiseja suhteettoman ankarasti ja poikkeaa suunnitellusta dynaamisuudesta.
* **Perusteltu korjausehdotus**: Sakon dynaaminen relative-luonne tulisi palauttaa tai vähintään korjata justification vastaamaan laskettua arvoa.

### 3.3 Gap 3: Järjestelmäromahduksen (500 crash) riski Indeterminate-tilassa
* **Ongelma**: Kun kognitiivinen romahduslukko tai 10 % DLQ-kipuraja laukeaa, matriisille asetetaan `raw_score = None`.
* [scoring.py](file:///c:/src/quorum/backend_v2/hooks/scoring.py#L1134) normalize-metodissa oleva tarkastus:
  ```python
  raw_val = parsed_payload.raw_score
  if not isinstance(raw_val, (int, float)):
      continue
  ```
  Tämä ohittaa kyseisen matriisin kokonaan, eikä sitä lisätä `_evaluative_matrices` -karttaan.
* Jos vaiheessa (step) on vain tämä yksi matriisi (yleinen tapaus useimmissa työvaiheissa), `_evaluative_matrices` jää tyhjäksi.
* Tämän seurauksena [apply_scoring_logic_hook](file:///c:/src/quorum/backend_v2/hooks/scoring.py#L233-L240) heittää fatal-tason poikkeuksen:
  `Strict Fail-Fast Enforced: '_evaluative_matrices' missing from state.`
* **Vaikutus**: Järjestelmä kaatuu 500-virheeseen onnistuneen epävarmuuden tunnistamisen sijaan.
* **Perusteltu korjausehdotus**: `apply_scoring_logic_hook` pitää muuttaa sallimaan tyhjä tai puuttuva matriisipisteytys silloin, kun kyseinen matriisi on asetettu validisti `is_indeterminate` -tilaan, jolloin loppupisteeksi palautetaan `None` tai hylätty ilman järjestelmäromahdusta.

### 3.4 Gap 4: Dormant `contrastive_example` metadata
* **Ongelma**: [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py#L249) sisältää `contrastive_example` -kentän, jolle on määritelty 152 atomille X/Y-abstraktio. Kuten raportti toteaa, kenttää ei kuitenkaan koskaan injektoida promptikääntäjässä [localization_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/localization_compiler.py).
* **Vaikutus**: Malli ei koskaan hyödy näistä abstrakteista esimerkeistä. Kenttä on täysin dormant.
* **Perusteltu korjausehdotus**: Kentän injektio tulisi joko aktivoida kääntäjässä tai poistaa metadata kokonaan.

### 3.5 Gap 5: Vanhentunut integraatiotesti (test_inverse_logic_injected)
* **Ongelma**: Integraatiotesti `test_inverse_logic_injected` tiedostossa [test_prompt_compiler.py](file:///c:/src/quorum/backend_v2/tests/integration/test_prompt_compiler.py#L5) tarkistaa edelleen vanhaa V1-käänteisen logiikan ohjetta (Vice-tekstiä), joka on tietoisesti poistettu osana kognitiivisen ylikuorman ja tuplainversio-ansan eliminointia.
* **Vaikutus**: Järjestelmän testi- ja auditointilooppi epäonnistuu (`AssertionError: Inverse logic text was not injected properly.`), vaikka koodi toimii oikein.
* **Perusteltu korjausehdotus**: Integraatiotesti on päivitettävä poistamalla kyseisen legacy-tekstin olemassaoloon liittyvät väitteet (assertit) ja varmistettava, että se heijastaa uutta, puhtaasti sensoripohjaista arkkitehtuuria.

---

## 4. Second Opinion & Toinen mielipide

### 4.1 Onko CONTESTED epistemologinen hopealuoti vai oireen siirto?
`CONTESTED`-tilan ja epävarmuuden hallinnan siirto backend-pisteisiin on matemaattisesti ja loogisesti erinomainen ratkaisu. Se hyväksyy tekoälyn stokastisuuden ja poistaa pakotetun binääriarvonnan.

**Kriittinen vastalause (Abstention Bias -uhka)**:
Kun LLM:lle annetaan mahdollisuus valita kolmas tila (`CONTESTED`), se luo luontaisen "laiskuuden" riskin. Monimutkaiset ja pitkää päättelyä vaativat rajatapaukset reititetään herkästi `CONTESTED`-tilaan, koska se on mallille pienimmän kognitiivisen vastuksen polku. Vaikka Zero-Trust-protokollassa on nyt "Excessive use... will result in failure" -pelote, se ei välttämättä riitä, jos malli havaitsee, ettei yksittäisestä `CONTESTED`-valinnasta rangaista tarpeeksi.

### 4.2 Positiivisten vs. Negatiivisten sääntöjen BARS-asymmetria
BARS-matriisin tasojen 1–2 negatiiviset säännöt (`inverse_evidence = True`) ovat edelleen vaikeammin arvioitavia kuin korkeammat tasot. 

Kun koodi suorittaa inversiobypassin `CONTESTED`-tilalle palauttamalla aina `True` (vesiputouksen jatkumiseksi), se tarkoittaa:
* **Positiivisessa säännössä** (met): Todisteita löytyi osittain / rajatapaus -> Sääntö täyttyy (True) + sakko.
* **Negatiivisessa säännössä** (vice): Virheitä löytyi osittain / rajatapaus -> Sääntö täyttyy eli virheitä EI löydetty tarpeeksi (True) + sakko.

Tämä on matemaattisesti johdonmukaista, mutta epistemologisesti asymmetristä: rajatapaus virheenetsinnässä (vice) johtaa "ei virhettä" (True) -päätelmään kooditasolla, kun taas rajatapaus hyveenetsinnässä (met) johtaa "hyve löytyi" (True) -päätelmään. Tässä mielessä järjestelmä suosii lievää tulkintaa molemmissa suunnissa.

### 4.3 Jitter ja Cross-Model Ensemble -vaihtoehto
Raportti hylkäsi "Paras kolmesta" (Thermal Jitter) -äänestyksen ja korvasi sen strict-nostoilla. Tämä on oikea ratkaisu, koska älyllistä kapasiteettivajetta ei voida korjata keskiarvoistamalla heikompia Flash-ajoja.

**Suositus tulevaisuuteen**:
Jotta jäljelle jäävä mekaaninen hardware-tason varianssi saadaan täysin eliminoitua, ainoa kestävä ratkaisu on aito heterogeeninen ensemble (esim. 2× Flash + 1× Pro) painotetulla äänestyksellä. Nykyinen strict-strategia (1× Pro ilman ensembleä raskaissa solmuissa) tekee mallista vakaan mutta silti haavoittuvaisen yksittäisille stokastisille heilahteluille. 1× Pro -ajo on vakaampi kuin 1× Flash, mutta ei täysin deterministinen. 

---

## 5. Suositellut toimenpiteet varianssikorjauksen loppuunsaattamiseksi

Seuraavat koodimuutokset ovat välttämättömiä Gap 1:n, Gap 2:n ja Gap 3:n korjaamiseksi (suositellaan toteutettavaksi seuraavassa refaktorisessiossa):

### 5.1 Korjaus: Symmetrinen konsensus-gating (`chunk_worker.py`)
Päivitetään [chunk_worker.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py) siten, että gating koskee myös FAIL-enemmistöjä:
```python
# Uusi symmetrinen gating-logiikka:
if pass_votes > fail_votes and pass_votes > contested_votes:
    chosen = best_pass if best_pass else votes[0]
    confidence = pass_votes / total_votes
    if confidence <= 0.67:
        chosen["status"] = "CONTESTED"
    else:
        chosen["status"] = "PASS"
    chosen["confidence"] = confidence
elif fail_votes > pass_votes and fail_votes > contested_votes:
    chosen = best_fail if best_fail else votes[0]
    confidence = fail_votes / total_votes
    if confidence <= 0.67:
        chosen["status"] = "CONTESTED"  # Gated also on FAIL splits
    else:
        chosen["status"] = "FAIL"
    chosen["confidence"] = confidence
...
```

### 5.2 Korjaus: Indeterminate-romahduksen hallinta (`scoring.py`)
Muutetaan [scoring.py](file:///c:/src/quorum/backend_v2/hooks/scoring.py#L233) siten, että se tunnistaa validit indeterminate-tilat eikä heitä fatal-poikkeusta:
```python
# Tarkistus apply_scoring_logic_hookissa:
if count == 0:
    # Tarkistetaan, johtuuko nollatulos validista indeterminate-tilasta
    is_valid_indeterminate = False
    for wrapper in _extract_payloads(lookup_ctx):
        for block_id in prompt_block_ids:
            block_payload = lookup_ctx.get(block_id)
            if isinstance(block_payload, dict) and "[INDETERMINATE]" in block_payload.get("justification", ""):
                is_valid_indeterminate = True
                break
                
    if is_valid_indeterminate:
        logger.warning("[ScoringHook] Matrix score is indeterminate due to Cognitive Collapse or DLQ limits. Skipping crash.")
        result = {
            "total_score": None,
            "final_score": None,
            "penalties_applied": penalties,
            "aggregation_status": "INDETERMINATE - Cognitive Collapse / Quality Check Failed",
        }
        return HookResult(success=True, state_delta={"scoring_result": result})
        
    msg = "Strict Fail-Fast Enforced: '_evaluative_matrices' missing from state."
    raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
```

### 5.3 Korjaus: Vanhentuneen integraatiotestin päivitys (`test_prompt_compiler.py`)
Päivitetään [test_prompt_compiler.py](file:///c:/src/quorum/backend_v2/tests/integration/test_prompt_compiler.py) siten, että legacy Vice-ohjeistusta ei enää testata:
```python
# Poistetaan tai kommentoidaan väite (rivit 62-71):
# expected_inverse_text = (
#     "This is an inverse rule (Vice). "
#     ...
# )
# assert expected_inverse_text in rubrics, "Inverse logic text was not injected properly."

# Tilalle voidaan testata, että inversiosäännön muut kentät ovat kohdillaan ilman Vice-lisätekstiä:
assert "<rule id=\"tda_22222222222222222222222222222222\">" in rubrics
```
