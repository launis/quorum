# Epic 47: Unified Execution Visibility & Soft Scoring Engines V3

## 1. Yhteenveto (Executive Summary)
Tämä yhdistetty Master Epic integroi kaksi järjestelmän kriittisintä päivitystä: arviointilogiikan matemaattisen kypsyysloikan (Soft Scoring V3) sekä tausta-ajojen täydellisen läpinäkyvyyden käyttöliittymässä (Virtual System Steps).

Tavoitteena on luoda **yleinen Arq-työnkulkujen (tausta-ajojen) hallinta- ja visualisointimenetelmä**. Pitkään kestävät tausta-ajot, kuten dynaaminen tulostemallikohtainen pisteiden laskenta (Scoring), LLM-synteesi ja PDF-raporttien koonti, tuodaan näkyväksi täsmälleen samaan käyttöliittymän työnkulkunäkymään kuin perinteiset AI-askeleet. Tämä tehdään "Virtuaalisten System-Askelien" (Virtual System Steps) avulla ilman, että rikotaan GraphEnginen tiukkaa DAG-moottorin SSOT-historiaa.

**Liiketoiminta-arvo:** Parantaa järjestelmän UX:ää ja läpinäkyvyyttä. Käyttäjä ei enää koe järjestelmän "jumittavan" työnkulun päätyttyä, vaan näkee selkeästi visualisoituna, miten "Pisteiden laskenta" tai "Raportin koonti" etenee muiden työvaiheiden jonossa. Tämä menetelmä kattaa saumattomasti sekä automaattisen päätyönkulun loppuajot että yksittäisten, on-demand -tulosteiden (esim. tulostemallin vaihdon tai erillisen PDF-luonnin) visualisoinnin.

Lisäksi tämä Epic ratkaisee B2B SaaS LLM -tuotteen kriittisimmät haasteet arvioinnin osalta: kovat matemaattiset "seinät" poistuvat. Pehmeä pisteytys (Lerp, Sigmoid, suhteelliset kaskadit) varmistaa, että osoitettu osaaminen palkitaan aina. Optimaalisilla asetuksilla (esim. Syväarvostelu + Strictness 50) luodaan tieteellisesti pätevä, jatkuva jakauma.

**Dokumentaation päivitys:** `c:\src\quorum\docs\architecture` -hakemiston arkkitehtuuridokumentaatiota on täydennettävä uusilla ominaisuuksilla sitä mukaa, kun kukin Epicin osa valmistuu.

## 2. Arkkitehtoniset Taustat ja Haasteet

### 2.1. Kuiluefekti (Cliff Effect) ja Nollahypoteesi
Järjestelmän aiempi arviointilogiikka toimi absoluuttisella "Hard Wall" -matematiikalla. Yksittäinen virhe alatasolla nollasi koko tuloksen, mikä teki arvioinnista kohtuuttoman ankaran ja epäreilun. Kuten syväanalyysissä havaittiin, LLM:n deterministiset asetukset (`temperature=0.0`) luovat armottoman nollahypoteesin. Kun tämä yhdistettiin vanhaan Waterfall-kynnykseen, syntyi massiivinen kuiluefekti (esim. 42 % osuma antoi täydet 100 %, ja 38 % romahdutti pisteet täysin). Tätä on mahdotonta korjata puhtaasti matematiikalla, jos tekoäly on tehnyt loogisen "laiskuusvirheen" itse rakenteessa.

### 2.2. Nykytilanne Tausta-ajojen Näkyvyydessä
Kun työnkulku (DAG) valmistuu, `worker.py` asettaa `ExecutionRecord`-tilan välittömästi `COMPLETED`-tilaan ja lähettää synteesin (`render_profile_job`) erillisenä taustatyönä Redis-jonoon. Käyttöliittymä näyttää "Completed" heti, eikä kerro synteesin tai PDF-generoinnin edistymisestä mitään.

Jos synteesistä tehtäisiin aito GraphEnginen solmu (`PromptBlock`), sen uudelleenajaminen (esim. kun käyttäjä haluaa vaihtaa raporttipohjaa on-demand) vaatisi valmiin työnkulun tilan ja historian rikkomista tai rinnakkaisen, kokonaan piilossa olevan suorituspolun rakentamista uudelleenluonneille.

Ratkaisuksi irrotamme "tilaseurannan" ja "DAG-suorituksen" toisistaan. Injektoimme manuaalisesti `ExecutionRecord.steps` -sanakirjaan uuden askeleen (esim. `sys_render_default`), jota Arq Worker ja API-endpointit hallitsevat manuaalisesti ohi DAG-moottorin.

---

## 3. Antigravity-komentolista (Backend Tasks)
Seuraavat tehtävät on muotoiltu suoraan tekoälyagenteille syötettäviksi prompteiksi. Koko backend-toteutuksessa on noudatettava ehdottomasti **c:\src\quorum\.agents\rules\00-antigravity-core.md** (Zero-Compromise Pledge) ja **c:\src\quorum\.agents\rules\01-python-backend.md** (Pydantic V2, The Duct Tape Ban) laatuportteja. Toteutetaan `[/tier2-hardening-backend]` -työnkululla.

### Task 1: DINA-moottori (Syväarvostelu) - Lerp ja matemaattinen turvallisuus
```text
Target files: backend_v2/utils/scoring/dampening_engine.py, backend_v2/utils/math_utils.py

Refactor the `DampeningScoringEngine` (Now called: "Syväarvostelu") and related functions to use Linear Interpolation (Lerp) and dynamic exponential dampening instead of a flat `max()` threshold.

New logic requirements:
1. Replace `max(hit_rate, base_forgiveness)` with Lerp: 
   `effective_hit_rate = base_forgiveness + (hit_rate * (1.0 - base_forgiveness))`.
2. Calculate a dynamic exponent based on `strictness_level` (50 -> 0.5, >50 -> higher, <50 -> lower). Note: Strictness 50 is the optimal baseline for cognitive matrices.
3. Math Safety: Safely handle edge cases like `0.0 ** exponent` to avoid `FloatingPointError`. Ensure `dynamic_exponent` is explicitly clamped within reasonable bounds (e.g., 0.2 to 3.0) to prevent overflow/underflow.
4. Apply the exponent: `modifier = modifier * (effective_hit_rate ** dynamic_exponent)`.
5. Ensure strict monotonicity: a higher raw hit rate must ALWAYS result in a higher or equal effective modifier.
6. **Agent Rule Compliance**: Strictly adhere to `c:\src\quorum\.agents\rules\01-python-backend.md` (Math Safety & The Duct Tape Ban). Do not use generic `except Exception: pass` to catch floating point errors; handle them explicitly.
```

### Task 2: Vesiputousmoottori (Koearvostelu) - Liukuva rangaistuskerroin ja kaskadointi
```text
Target file: backend_v2/utils/scoring/waterfall_engine.py

Refactor `WaterfallScoringEngine.calculate` (Now called: "Koearvostelu") to use a proportional/sliding penalty multiplier instead of a fixed binary penalty. This engine is strictly for compliance pass/fail audits.

New logic requirements:
1. Optimal baseline: Must be configured to use Strictness 85 (Tiukka, threshold 0.70) when evaluating absolute pass/fail audits.
2. When `hit_rate < target_threshold`, calculate the shortfall distance: 
   `shortfall = (target_threshold - hit_rate) / target_threshold`.
3. Edge Case: If `target_threshold == 0.0`, fallback shortfall to 0.0 (ZeroDivisionError prevention).
4. Calculate sliding penalty: `sliding_penalty = 1.0 - (shortfall * (1.0 - base_forgiveness))`.
5. Cascade Rule: The `sliding_penalty` MUST be cumulatively multiplied to ALL SUBSEQUENT (higher) levels ONLY, not the current level where the threshold was initially missed: `next_multiplier = current_multiplier * sliding_penalty`.
```

### Task 3: Painotettu Keskiarvo (Sigmoid-skaalaus ilman ulkoisia riippuvuuksia)
```text
Target files: backend_v2/utils/scoring/average_engine.py, backend_v2/utils/math_utils.py

Refactor `WeightedAverageScoringEngine` to utilize a Sigmoid (logistic) scaling curve.

New logic requirements:
1. Replace linear scaling with a Sigmoid curve using standard Python `math.exp()`. DO NOT introduce external libraries like NumPy or SciPy.
2. Formula: `raw_sigmoid = 1 / (1 + math.exp(-steepness * (hit_rate - midpoint)))`.
3. Shift the `midpoint` dynamically based on `strictness_level`. Higher strictness = higher midpoint.
4. Normalization: Normalize the output mathematically so that a raw hit_rate of 0.0 yields EXACTLY the mathematical minimum (e.g., 1.0), and 1.0 yields EXACTLY the maximum (e.g., 5.0).
```

### Task 4: Lineaarinen Keskiarvo (Konkreettinen Outlier Rejection)
```text
Target file: backend_v2/utils/scoring/average_engine.py

Refactor `PureAverageScoringEngine` (Now called: "Lineaarinen Keskiarvo") to implement a statistically sound 'Outlier Rejection' mechanism utilizing the robust MAD (Median Absolute Deviation) method.

New logic requirements:
1. Before flattening stats, calculate the `hit_rate` for each level.
2. Calculate the Median of the hit rates. Then calculate the absolute deviations from this median, and find the median of those deviations (this is the MAD). Use standard Python `statistics.median`.
3. Edge case: If MAD is 0.0, fallback to a minimum MAD of `0.05` to prevent overly aggressive rejection in nearly uniform datasets.
4. Define a concrete heuristic for an anomaly: `hit_rate < (median - 3.0 * MAD) AND hit_rate < 0.30`.
5. If an anomaly is found, mitigate it by multiplying that specific outlier level's total weight by `0.25` before calculating the final pure average.
```

### Task 5: Backend - Keskitetty Strictness-konfiguraatio (Score Clamping)
```text
Target files: backend_v2/utils/math_utils.py, backend_v2/models/enums.py

Create a centralized strictness mapping and ensure absolute mathematical boundary safety.

New logic requirements:
1. Clean up unused enums (e.g., `SelfHealingThresholdRatio`) from `enums.py`.
2. Implement a pure function `get_strictness_config(level: int)` returning an object/dict with `base_forgiveness`, `sigmoid_midpoint`, and `dynamic_exponent`.
3. Replace all hardcoded strictness logic inside engines with calls to this centralized mapper.
4. Implement `clamp_score(score: float, math_min: float, math_max: float) -> float`. Every single scoring engine MUST pass its final numerical result through this clamp before returning it.
5. **Agent Rule Compliance**: Enforce `c:\src\quorum\.agents\rules\01-python-backend.md` (Strict Pydantic V2 & Mutability). New domain models (e.g., for strictness config) must use `ConfigDict(frozen=True)` and strict validations. Enum conversion must use `Annotated[Enum, Field(strict=False)]`.
```

### Task 6: Arkkitehtuuri - LLM-virheiden korjaus (Anomaly Hook & Circuit Breaker)
```text
Target files: backend_v2/hooks/validation.py, backend_v2/services/orchestrator/

Implement a pre-scoring `LLMAnomalyDetectionHook` to catch Guttman logic failures (e.g., L1=0%, L3=100%).

New logic requirements:
1. If a logical anomaly is detected in the matrix, trigger an LLM Self-Correction loop via the Orchestrator.
2. Implement the Circuit Breaker explicitly: Store `retry_count` in the Orchestrator's internal node state (NO global variables). 
3. Set the maximum retries to 2.
4. If max retries are exceeded, swallow the anomaly, set `anomaly_unresolved=True` in the state payload, and proceed gracefully to mathematical scoring without crashing the workflow.
5. **Agent Rule Compliance**: Must comply with `c:\src\quorum\.agents\rules\05_llm_architecture.md` for Circuit Breaker implementation and `c:\src\quorum\.agents\rules\01-python-backend.md` for the Duct Tape Ban (all retry loops and LLM failures must be explicitly logged, never silently swallowed with god blocks).
```

### Task 7: UX/XAI - Asynkroninen UX-palaute (SSE)
```text
Target files: backend_v2/api/routers/system/telemetry.py, client_app_v2/lib/features/execution/views/dynamic_start_screen.dart

Implement a real-time UX feedback mechanism for the LLM Anomaly Retry loop to prevent the perception of a frozen app.

New logic requirements:
1. Backend: When the Orchestrator triggers an anomaly retry, dispatch a specific Server-Sent Event (SSE) to the client: `{"status": "processing", "message_code": "event_llm_anomaly_retry"}`.
2. Frontend: Intercept this SSE message in the execution loading state listener.
3. Frontend UI: Dynamically update the loading spinner text to use an i18n translation key mapping to a string like: "Quality Assurance: The AI detected an inconsistency and is verifying its reasoning (Attempt 2)...".
```

### Task 8: XAI:n Inhimillistäminen (Strict i18n & Debug Erottelu)
```text
Target files: backend_v2/utils/scoring/*_engine.py, backend_v2/models/dtos/

Refactor XAI logging to support global localization and maintain developer debuggability.

New logic requirements:
1. DO NOT hardcode Finnish or English natural language explanations in the backend Python code. This violates i18n principles.
2. Refactor the `calculation_log` into a structured DTO: `XAILogDto` with two fields: `pedagogical_key: str` and `engine_debug_trace: dict`.
3. Return ONLY translation keys (e.g., `xai_soft_waterfall_penalty`) to the frontend for the pedagogical explanation.
4. Place raw math details, thresholds, and multipliers strictly inside the `engine_debug_trace` dictionary for admins and developers.
5. **Agent Rule Compliance**: Must adhere to `c:\src\quorum\.agents\rules\01-python-backend.md` (Schema-Driven Routing). No natural language magic strings allowed in Python code.
```

### Task 9: Backend - Yleinen Arq-työnkulkujen Hallintamenetelmä (Virtual Steps) & Tulostemallikohtainen Matematiikka
```text
Target files: backend_v2/worker.py, backend_v2/api/routers/execution/executions.py, backend_v2/models/v2_core.py, backend_v2/models/dtos/output_profile.py, backend_v2/hooks/scoring.py

Refactor scoring logic to detach `strictness_level` and `scoring_strategy` from the Execution phase and bind them to the Output Profile phase (Arq Worker).

New logic requirements:
1. Data Models: Remove `strictness_level` and `scoring_strategy` from `ExecutionCreate` and `ExecutionRecord`. Add them to `OutputProfile`, `EmbeddedOutputProfile`, and `OutputLayoutBlock`. Add them as defaults to the `Workflow` model (which will cascade them via `default_profile_id`).
2. Execution Hook: Refactor `matrix_scoring_hook`. It must no longer calculate the mathematical score or use `dampening_score`. It should ONLY aggregate the raw hit/miss boolean counts (`evaluated_atoms`, `true_atoms_count`) into the Frozen Context.
3. Arq Background Method - Trigger: When `execute_workflow` finishes (or when On-Demand endpoint `POST /{execution_id}/render_pdf` is called), the system injects a Virtual Step (e.g. `sys_render_X`) into `ExecutionRecord.steps` with `status="running"`. If On-Demand, it forces the execution status back to `RUNNING` from `COMPLETED`. Send an SSE immediately.
4. Report Generation Phase (Inside Arq): The Arq-worker (`render_profile_job`) takes over. It loads the `Frozen Context` raw atoms, dynamically runs the math (`get_scoring_engine`) using the selected Output Profile's `strictness_level` and `scoring_strategy`, feeds the scores to LLM synthesis, and caches the `ReportDataDTO`.
5. Arq Background Method - Completion: On success (`status="completed"`) or failure (`status="failed"`), update the `sys_render_<profile>` step state in the DB. In both cases, ensure the overall `ExecutionRecord` status is returned to `COMPLETED`.
6. Taaksepäin Yhteensopivuus ja Zero-Trust: Uudet virtuaaliset askeleet tunnistetaan selkeästi `sys_` -etuliitteellä, jotta ne erotetaan aidoista AI-arviointiasteleista. SSOT säilyy tietokannassa. Kaikkien päivitysten on tapahduttava keskitetysti `repository.update_execution()` -metodin kautta atomisesti.
7. **Agent Rule Compliance**: CRITICAL. Enforce `c:\src\quorum\.agents\rules\01-python-backend.md` (Fail-Fast Hydration Mandate). Parse dictionary data into `OutputProfile` immediately using `.model_validate()`. Follow `c:\src\quorum\.agents\rules\00-antigravity-core.md` Zero-Legacy standard (no `dict.get(key, default)` hacks in logic layers).
```

### Task 10: Laadunvarmistus - Matemaattisen Monotonisuuden Testiautomaatio
```text
Target files: tests/backend_v2/utils/scoring/test_*.py

Implement rigorous Pytest coverage for the refactored 'Soft Scoring' engines.

New logic requirements:
1. Boundary Tests: Test absolute 0.0 and 1.0 hit rates across all strictness levels. Assert values strictly clamp between `math_min` and `math_max`.
2. Monotonicity Tests: Programmatically loop through hit rates from 0.0 to 1.0 in 0.01 increments. Assert that `f(x) <= f(x + 0.01)` is ALWAYS true for all engines. The score must never flatline or decrease when the raw hit rate increases.
3. Outlier Mitigation Tests: Pass an array `[1.0, 1.0, 0.0, 1.0]` to the Lineaarinen Keskiarvo Engine and assert the `0.0` value's weight is significantly reduced compared to a standard mean calculation.
4. **Hardening Verification**: The implementing agent MUST execute the `[/tier2-hardening-backend]` workflow rules upon completion. Explicitly run `ruff check .`, `ruff format .`, `mypy .`, and `pytest tests/backend_v2/utils/scoring/` to ensure zero errors. If any error occurs, fix it immediately before concluding the task.
```

---

## 4. Antigravity-komentolista (Frontend Tasks)
Kaikissa UI-tehtävissä on ehdottomasti noudatettava **c:\src\quorum\.agents\rules\02_flutter_desktop.md** vaatimuksia. Toteutetaan `[/tier2-hardening-frontend]` -työnkululla.

### Task 11: Frontend Hardening - Tyhjentävä käsittely (Dart 3 Exhaustive Switches)
```text
Target files: client_app_v2/lib/core/models/, client_app_v2/lib/features/execution/, client_app_v2/lib/l10n/app_fi.arb

Enforce 'Zero DB Hardcoding' and Exhaustive Handling for Strictness and Engine Selection.

New logic requirements:
1. Replace backend/frontend enums to match the new plain-language taxonomy: "Koearvostelu", "Syväarvostelu", "Lineaarinen Keskiarvo", "Painotettu Keskiarvo".
2. Backend API must return strictness configurations as structured DTOs (e.g., `{"level": 15, "localization_key": "strictness_lenient"}`).
3. Frontend must map the `localization_key` to `AppLocalizations` to eliminate duplicate UI texts (e.g., fixing `Salliva (15) (15)` to just `Salliva (15)`).
4. Enforce Dart 3 EXHAUSTIVE switch expressions for enums (NO `default:` branch allowed).
5. For Freezed unions, strictly use `.map()` or `.when()`. Do not use `.maybeWhen()` or `??` fallbacks.
6. Instruct the AI to run `dart run build_runner build --delete-conflicting-outputs` after updating frontend DTOs.
7. **Agent Rule Compliance**: Enforce `c:\src\quorum\.agents\rules\02_flutter_desktop.md` (Zero-Compromise UI & Zero DB Hardcoding Mandate). No UI component may assume specific database IDs or magic strings.
```

### Task 12: Tulostemallikohtaiset Kontrollit (UI)
```text
Target files: client_app_v2/lib/features/studio/views/output_profile_editor.dart

Expose the new Dynamic Profile Scoring controls in the Flutter UI.

New logic requirements:
1. Profile Editor: Add "Arvostelumoottori" (Scoring Strategy) and "Ankaruustaso" (Strictness Level) dropdowns to the "Muokkaa tulostusprofiilia" view. Ensure these bind to the updated OutputProfile DTOs.
2. **Agent Rule Compliance**: Follow `c:\src\quorum\.agents\rules\02_flutter_desktop.md` for Strongly Typed State. The UI layer must use Riverpod generators and strictly typed DTO models without dynamic `Map` recycling.
```

### Task 13: Yhtenäinen Askel-UI (Virtual Steps Visualization)
```text
Target files: client_app_v2/lib/features/execution/views/dashboard.dart, client_app_v2/lib/features/execution/widgets/step_card.dart

New logic requirements:
1. Frontend (Flutter) lukee jo valmiiksi kaikki askeleet `ExecutionRecord.steps` -sanakirjasta. Koska virtuaalinen askel on tietorakenteeltaan täysin validi `StepRecord` (sisältää tilan ja nimen), sen pitäisi automaattisesti piirtyä UI-komponenttina (`StepCard` tms.) oikein ilman suuria koodimuutoksia.
2. Frontendin on hyödynnettävä täsmälleen samaa käyttöliittymäkomponenttia (askeleiden listanäkymä ikoneineen ja lataus-spinnereineen) virtuaalisten askeleiden esittämiseen kuin mitä se käyttää aitojen LLM-askeleiden (kuten "Faktantarkistaja", "Analyst") esittämiseen.
3. Käyttäjän ei pidä visuaalisesti erottaa, onko kyseessä tekoälyn suorittama solmu vai Arq-taustatyö (kuten "Scoring Engine" tai "PDF Generointi"). Kaikki askeleet näkyvät yhtenäisenä, alaspäin rakentuvana listana.
4. Yksittäiset tulostukset (On-Demand): Kun käyttäjä painaa UI:ssa myöhemmin "Luo uusi raportti" tai vaihtaa tulostemallia jo valmiissa ajossa (Execution Dashboardin "Valitse tulostemalli" popup), olemassa olevaan askeleiden listaan on ilmestyttävä lennosta uusi virtuaalinen askel pyörivällä spinnerillä ja backendin uusi laskenta käynnistyy.
5. Testaus: Varmistettava, että käyttöliittymän "Kokonaisedistyminen" (Progress Bar) ymmärtää lennosta dynaamisesti kasvavan askelmäärän (Total Steps = AI-askeleet + Virtuaaliaskeleet) eikä sekoa prosenttilaskennassaan 100 % yli.
6. **Hardening Verification**: The implementing agent MUST execute the `[/tier2-hardening-frontend]` workflow rules upon completion. Explicitly run `dart format .`, `flutter analyze`, and `flutter test` to ensure zero errors. If the analyzer or tests fail, fix them immediately before concluding the task.
```

---

## 5. Kokonaisarvio: Epic 47:n liiketoiminta-arvo (Maturity Leap)

Kun tämä Epic on suoritettu, järjestelmä ottaa merkittävän kypsyysloikan Enterprise-tasolle:

*   **Ilmainen Simuloitavuus (Zero Re-runs):** Arvioinnin matematiikka (Engine & Strictness) irrotetaan raskaasta LLM-ajosta. Käyttäjä voi testata sekunneissa kymmeniä eri tiukkuustasoja samaan raakadataan muuttamalla vain Tulostemallia.
*   **Tuotelupauksen lunastaminen:** Tekoälypohjainen arvostelu ei tunnu mekaaniselta rangaistusautomaatilta. Pehmeä pisteytys palkitsee aina suorituksesta, ja koodattu XAI muutetaan pedagogiseksi, lokalisoiduksi palautteeksi.
*   **Kestävä tekoälyintegraatio (Defensive AI):** Ohjelmisto ei luota sokeasti kielimallien virheettömyyteen. Orkestraattori valvoo ja pakottaa LLM:n korjaamaan loogiset mahdottomuutensa reaaliajassa.
*   **Läpinäkyvä Käyttökokemus:** Tausta-ajojen visualisointi yhdenmukaiseksi askeleeksi (Virtual Steps) poistaa järjestelmän "jumittumisen" tunteen. Käyttäjä näkee tarkalleen, missä vaiheessa Arq-workerin suorittama PDF-koonti tai pisteiden laskenta on menossa.
*   **Arkkitehtuurinen ylläpidettävyys:** Kovakoodauksien poistaminen, keskitetty matematiikka ja täysi DTO/Enum -ohjautuvuus takaavat, ettei käyttöliittymä kaadu piileviin virheisiin päivitysten yhteydessä. Tier 2 -laatuporttien pakotus varmistaa pitkän aikavälin koodihygienian.
