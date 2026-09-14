# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Ympäristö ja Konteksti (Execution State)
> **[ONNISTUNUT] (Kaikki kelvollista):** Kaikki vertaillut ajot ovat valmistuneet onnistuneesti (PASSED) ilman teknisiä kaatumisia, DLQ-pudotuksia tai aineiston näivettymistä (Data Starvation).

> **[ERISTETTY] TÄYSI SYÖTE-ERISTYS (Ei välimuistivuotoa):** Kaikkien syötetiedostojen SHA-256-tiivisteet poikkesivat toisistaan ajojen välillä. Googlen prefiksipohjainen KV-välimuisti ei ole voinut siirtyä ajosta toiseen.

- **Palvelintason välimuistikytkin:** `DISABLE_VERTEX_CACHE=false` (Oletustila / Ei pakotettu)
- **Git / Epic -tila:** Branch: main | Commit: 40a9b11c - feat(scripts): enhance verify quote with dual-substitution normalization and precomputation (Mon Sep 14 15:02:30 2026 +0300)
- **Kriittiset järjestelmäarvot (Enums):**
  - **ExecutionStatus**: PASSED = PASSED, FAILED = FAILED, N_A = N_A, SYSTEM_ERROR = SYSTEM_ERROR, BLOCKED = BLOCKED, PENDING = PENDING, RUNNING = RUNNING, QUEUED = QUEUED
  - **VerificationResult**: VERIFIED = RESULT_VERIFIED, DEBUNKED = RESULT_DEBUNKED, UNVERIFIED = RESULT_UNVERIFIED
  - **EvaluationRunCount**: STANDARD = 1, ENSEMBLE = 3
  - **EvaluationCategory**: MATHEMATICAL = MATHEMATICAL, SEMANTIC = SEMANTIC, LINGUISTIC = LINGUISTIC, LOGICAL = LOGICAL, BEHAVIORAL = BEHAVIORAL, UNKNOWN = UNKNOWN
  - **ScoringStrategy**: WATERFALL = WATERFALL, AVERAGE = AVERAGE, WEIGHTED_AVERAGE = WEIGHTED_AVERAGE, PURE_MATH = PURE_MATH
  - **LLMProviderName**: VERTEX_AI = vertex_ai, GOOGLE = google, AI_STUDIO = ai_studio, ANTHROPIC = anthropic, OPENAI = openai, DEEPSEEK = deepseek, MOCK = mock_llm_99
  - **LLMCachingStrategy**: PROMPT_CACHING = prompt_caching, EPHEMERAL = ephemeral, ANTHROPIC_EPHEMERAL = anthropic_ephemeral, GEMINI_NATIVE = gemini_native, NONE = none
  - **SystemConcurrency (Settings)**:
    - max_concurrent_llm_steps = 3
    - llm_max_retries = 0
- **Vertailtavat ajot (R1, R2...):**
  - **R1:** `exe_26f38060c9bd4ef3`
  - **R2:** `exe_1aaabc9556704edc`
- **Aktiiviset Säännöt ja Asetukset (Frozen Context):** Ei saatavilla
- **Työnkulun Provenienssi ja Hallintokytkimet (Workflow Provenance & Invariants):**
  - **Työnkulku:** `wf_03a1d71000000003` (Syvällinen Ongelmanratkaisu ja Kognitio / Deep Problem Solving & Cognition)
  - **Versio:** v1 | **Aktiivisia askeleita:** 7 kpl | **Koko atomipopulaatio:** 85 atomia
  - **Hallintokytkimet:** Kontekstuaaliset ohitukset: `SALLITTU (ENABLED)`, Pisteytystapa: `AVERAGE`, Tiukkuustaso: `50`
  - **Prompt-direktiivien tiiviste (SHA-256):** `d4d856505d3aae09...` (736,361 merkkiä)
- **Fyysiset Mallisidokset (Physical Model Bindings):**
  - **fast:** `gemini/gemini-3.8-flash` (T=0.1, MaxTok=32768)
  - **reasoning:** `gemini/gemini-3.8-flash` (T=0.2, MaxTok=65536, Thinking=8192 tok)
  - **synthesis:** `gemini/gemini-3.8-flash` (T=0.3, MaxTok=65536, Thinking=2048 tok)
  - **deep:** `gemini/gemini-3.8-flash` (T=0.2, MaxTok=65536, Thinking=4096 tok)
  - **strict:** `gemini/gemini-3.8-flash` (T=0.0, MaxTok=32768)

## Ajojen Lähdetiedostot ja Syötteet
- **Run 1:** `exe_26f38060c9bd4ef3` (Lähde: [data\files\executions\exe_26f38060c9bd4ef3\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_26f38060c9bd4ef3/execution_trace.json))
  - **Malli(t):** `fast (908,605 tok), reasoning (384,686 tok), synthesis (44,172 tok)` (Chunk size: None, Max Evals: None, Sampling: 0 (Kaikki 85 atomia, Tuotanto))
  - **Ajotila ja Rinnakkaisuus:** Tila: `production`, Max retries: `2`, Chunk size: `-`, Max Evals: `-`, Sampling: `0 (Kaikki 85 atomia, Tuotanto)`
  - **Kesto:** `6.4 minuuttia (385.2 s)`
  - **API-kutsut:** `6` kpl (Välimuistiosumat: `3/6` (50.0 %))
  - **Tokenit:** `1,631,086` (Syöte: `1,156,305`, Tuotos: `181,158`, Ajattelu: `136,022`, Välimuisti: `526,812`, Synteesi: `157,601`)
  - **Kustannusarvio:** `$1.3399` (DAG: `$1.1910`, Synteesi: `$0.1489`)
  - **Hitain askel (Pullonkaula):** `sr_03c1d71000000004` (127.9 s)
  - **Tekniset virheet (Crash):** `0` kpl
  - **DLQ-pudotetut atomit:** `0` kpl
  - **Kelvollisuus:** [KELVOLLINEN]
  - **Käytetyt syötetiedostot:**
    - [input_assignment_context.md](file:///C:/src/quorum/data/files/executions/exe_26f38060c9bd4ef3/inputs/input_assignment_context.md) (SHA-256: `946641d434e0aabf...`, Variaatio: `No-Break Space (U+00A0)`)
    - [input_chat_log.md](file:///C:/src/quorum/data/files/executions/exe_26f38060c9bd4ef3/inputs/input_chat_log.md) (SHA-256: `025fcbf541095f8a...`, Variaatio: `No-Break Space (U+00A0)`)
    - [input_chat_log_ai_only.md](file:///C:/src/quorum/data/files/executions/exe_26f38060c9bd4ef3/inputs/input_chat_log_ai_only.md) (SHA-256: `93c6a88e70f188d2...`, Variaatio: `No-Break Space (U+00A0)`)
    - [input_chat_log_user_only.md](file:///C:/src/quorum/data/files/executions/exe_26f38060c9bd4ef3/inputs/input_chat_log_user_only.md) (SHA-256: `22a644923e7d9532...`, Variaatio: `No-Break Space (U+00A0)`)
    - [input_product_text.md](file:///C:/src/quorum/data/files/executions/exe_26f38060c9bd4ef3/inputs/input_product_text.md) (SHA-256: `41c484dd97d537a2...`, Variaatio: `No-Break Space (U+00A0)`)
    - [input_reflection_text.md](file:///C:/src/quorum/data/files/executions/exe_26f38060c9bd4ef3/inputs/input_reflection_text.md) (SHA-256: `ea0dcff828f98b52...`, Variaatio: `No-Break Space (U+00A0)`)
- **Run 2:** `exe_1aaabc9556704edc` (Lähde: [data\files\executions\exe_1aaabc9556704edc\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_1aaabc9556704edc/execution_trace.json))
  - **Malli(t):** `fast (1,019,332 tok), reasoning (345,937 tok), synthesis (54,268 tok)` (Chunk size: None, Max Evals: None, Sampling: 0 (Kaikki 85 atomia, Tuotanto))
  - **Ajotila ja Rinnakkaisuus:** Tila: `production`, Max retries: `2`, Chunk size: `-`, Max Evals: `-`, Sampling: `0 (Kaikki 85 atomia, Tuotanto)`
  - **Kesto:** `8.8 minuuttia (528.9 s)`
  - **API-kutsut:** `6` kpl (Välimuistiosumat: `4/6` (66.7 %))
  - **Tokenit:** `1,710,560` (Syöte: `1,324,108`, Tuotos: `95,429`, Välimuisti: `726,144`, Synteesi: `291,023`)
  - **Kustannusarvio:** `$2.1993` (DAG: `$1.7925`, Synteesi: `$0.4068`)
  - **Hitain askel (Pullonkaula):** `sr_03c1d71000000004` (175.6 s)
  - **Tekniset virheet (Crash):** `0` kpl
  - **DLQ-pudotetut atomit:** `0` kpl
  - **Kelvollisuus:** [KELVOLLINEN]
  - **Käytetyt syötetiedostot:**
    - [input_assignment_context.md](file:///C:/src/quorum/data/files/executions/exe_1aaabc9556704edc/inputs/input_assignment_context.md) (SHA-256: `18b5c2c559051109...`, Variaatio: `En Space (U+2002)`)
    - [input_chat_log.md](file:///C:/src/quorum/data/files/executions/exe_1aaabc9556704edc/inputs/input_chat_log.md) (SHA-256: `c55857579b879eda...`, Variaatio: `No-Break Space (U+00A0), En Space (U+2002)`)
    - [input_chat_log_ai_only.md](file:///C:/src/quorum/data/files/executions/exe_1aaabc9556704edc/inputs/input_chat_log_ai_only.md) (SHA-256: `1fc65c285a708a3e...`, Variaatio: `En Space (U+2002)`)
    - [input_chat_log_user_only.md](file:///C:/src/quorum/data/files/executions/exe_1aaabc9556704edc/inputs/input_chat_log_user_only.md) (SHA-256: `014fb904a981a893...`, Variaatio: `No-Break Space (U+00A0), En Space (U+2002)`)
    - [input_product_text.md](file:///C:/src/quorum/data/files/executions/exe_1aaabc9556704edc/inputs/input_product_text.md) (SHA-256: `733c893514dca15e...`, Variaatio: `En Space (U+2002)`)
    - [input_reflection_text.md](file:///C:/src/quorum/data/files/executions/exe_1aaabc9556704edc/inputs/input_reflection_text.md) (SHA-256: `cd91b605a16e8ad6...`, Variaatio: `En Space (U+2002)`)

### Syöteaineiston Profiili ja Rakenneanalyysi (Input Corpus Profile)

Taulukko erittelee syötetiedostojen volyymin (sanat, lauseet, merkit) ja rakenteen (kappaleet, luetelmat) kustakin ajosta. Tämä todentaa aineiston riittävyyden (Data Sparsity vs. Cognitive Failure) sekä semanttisen ekvivalenssin.

| Ajo | Tiedosto | Ontologinen Rooli | Sanat | Lauseet | Merkit | Kappaleet | Luetelmat | Variaatio / Kohina |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **R1 (exe_26f38060c9bd4ef3)** | `input_assignment_context.md` | Ulkoinen konteksti (External Normative Context) | 114 | 9 | 1,016 | 15 | 7 | No-Break Space (U+00A0) |
| **R2 (exe_1aaabc9556704edc)** | `input_assignment_context.md` | Ulkoinen konteksti (External Normative Context) | 114 | 9 | 1,016 | 15 | 7 | En Space (U+2002) |
| **R1 (exe_26f38060c9bd4ef3)** | `input_chat_log.md` | Raakaloki (Combined Raw Dialogue) | 5,489 | 330 | 48,790 | 462 | 0 | No-Break Space (U+00A0) |
| **R2 (exe_1aaabc9556704edc)** | `input_chat_log.md` | Raakaloki (Combined Raw Dialogue) | 5,865 | 330 | 49,166 | 462 | 0 | No-Break Space (U+00A0), En Space (U+2002) |
| **R1 (exe_26f38060c9bd4ef3)** | `input_chat_log_ai_only.md` | Ulkoinen konteksti (External Normative Context) | 5,334 | 328 | 47,127 | 448 | 0 | No-Break Space (U+00A0) |
| **R2 (exe_1aaabc9556704edc)** | `input_chat_log_ai_only.md` | Ulkoinen konteksti (External Normative Context) | 5,710 | 328 | 47,503 | 448 | 0 | En Space (U+2002) |
| **R1 (exe_26f38060c9bd4ef3)** | `input_chat_log_user_only.md` | Käyttäjädokumentaatio (Candidate Deliverable) | 113 | 2 | 922 | 14 | 0 | No-Break Space (U+00A0) |
| **R2 (exe_1aaabc9556704edc)** | `input_chat_log_user_only.md` | Käyttäjädokumentaatio (Candidate Deliverable) | 113 | 2 | 922 | 14 | 0 | No-Break Space (U+00A0), En Space (U+2002) |
| **R1 (exe_26f38060c9bd4ef3)** | `input_product_text.md` | Käyttäjädokumentaatio (Candidate Deliverable) | 442 | 42 | 5,355 | 22 | 9 | No-Break Space (U+00A0) |
| **R2 (exe_1aaabc9556704edc)** | `input_product_text.md` | Käyttäjädokumentaatio (Candidate Deliverable) | 442 | 42 | 5,355 | 22 | 9 | En Space (U+2002) |
| **R1 (exe_26f38060c9bd4ef3)** | `input_reflection_text.md` | Käyttäjädokumentaatio (Candidate Deliverable) | 128 | 13 | 1,053 | 7 | 0 | No-Break Space (U+00A0) |
| **R2 (exe_1aaabc9556704edc)** | `input_reflection_text.md` | Käyttäjädokumentaatio (Candidate Deliverable) | 128 | 13 | 1,053 | 7 | 0 | En Space (U+2002) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **YHTEENSÄ R1** | **3 tiedostoa** | **Käyttäjädokumentaation volyymi** | **683** | **57** | **7,330** | **43** | **9** | **Puhdas kandidaattisisältö** |
| **YHTEENSÄ R2** | **3 tiedostoa** | **Käyttäjädokumentaation volyymi** | **683** | **57** | **7,330** | **43** | **9** | **Puhdas kandidaattisisältö** |

> **[HUOMIO]:** Syötetiedostoissa havaittiin asiasisällöllisiä eroja normalisoidun tekstivertailun perusteella.

### Syöte-eristyksen ja Välimuistiohituksen Matemaattiset Todisteet

Tämä osio todentaa matemaattisesti ja empiirisesti, että jokainen ajo on suoritettu toisistaan täysin eristetyillä syötteillä ilman pilvitarjoajan kontekstivälimuistivuotoa (Context Cache Bleed).

#### 1. Kryptografinen SHA-256 Hajautustiiviste-erottelu
| Ajo | Tiedosto | SHA-256 Tiiviste (Hash) | Status |
| :--- | :--- | :--- | :---: |
| **R1 (exe_26f38060c9bd4ef3)** | `input_assignment_context.md` | `946641d434e0aabfb108952d273a9ca6c2837946e87d30290e08e9b94c305af8` | `ERISTETTY` |
| **R2 (exe_1aaabc9556704edc)** | `input_assignment_context.md` | `18b5c2c5590511097cb12dcee73869c8d19d07267b402f01afc7ee87cdf8e1b6` | `ERISTETTY` |
| **R1 (exe_26f38060c9bd4ef3)** | `input_chat_log.md` | `025fcbf541095f8ae1256e61c0deab8d636d588b4aff6abf1c92d3146bc88012` | `ERISTETTY` |
| **R2 (exe_1aaabc9556704edc)** | `input_chat_log.md` | `c55857579b879eda3d9a2253c4a7ba636e89007bcaca476d4748595c34ac8713` | `ERISTETTY` |
| **R1 (exe_26f38060c9bd4ef3)** | `input_chat_log_ai_only.md` | `93c6a88e70f188d2452cf337792b912c514fb35147bcd51990a5566a47b34997` | `ERISTETTY` |
| **R2 (exe_1aaabc9556704edc)** | `input_chat_log_ai_only.md` | `1fc65c285a708a3ed4b12e57009b30a40a1e7c2a0710597bc5e36e0084511cfc` | `ERISTETTY` |
| **R1 (exe_26f38060c9bd4ef3)** | `input_chat_log_user_only.md` | `22a644923e7d9532594abfeabf50995c2139a6289144dd038a4530052eeae7ef` | `ERISTETTY` |
| **R2 (exe_1aaabc9556704edc)** | `input_chat_log_user_only.md` | `014fb904a981a89366acaa41f4b8fecc1e9427703bd791f1f47a5518874e3641` | `ERISTETTY` |
| **R1 (exe_26f38060c9bd4ef3)** | `input_product_text.md` | `41c484dd97d537a241102352418ceb523ec57d38060184fadc57c6ee2fe821ec` | `ERISTETTY` |
| **R2 (exe_1aaabc9556704edc)** | `input_product_text.md` | `733c893514dca15eb32014f269a741e31ae9c95a7717954236bcbddd5b143af8` | `ERISTETTY` |
| **R1 (exe_26f38060c9bd4ef3)** | `input_reflection_text.md` | `ea0dcff828f98b5252cb9656b45bdd18b514334f34b012cb93d74290d71db3cc` | `ERISTETTY` |
| **R2 (exe_1aaabc9556704edc)** | `input_reflection_text.md` | `cd91b605a16e8ad6957e100ea9650093d5ed5152a73f092182ef7f3ca1f5c483` | `ERISTETTY` |

#### 2. Pilvitarjoajan Telemetriavahvistus (Zero Cached Tokens)
| Ajo | Välimuistitokenit (Cached Tokens) | Välimuistiaste (Osumat) | Telemetriatodiste | Tulos |
| :--- | :---: | :---: | :---: | :---: |
| **exe_26f38060c9bd4ef3** | 526,812 | 3/6 (50.0 %) | Osittainen välimuistihyödyntäminen | `VÄLIMUISTIOSUMA (526,812 tok)` |
| **exe_1aaabc9556704edc** | 726,144 | 4/6 (66.7 %) | Osittainen välimuistihyödyntäminen | `VÄLIMUISTIOSUMA (726,144 tok)` |

#### 3. Hajautettu Variaatiosyvyys ja Unicode-avaruus
| Ajo | Tiedosto | Havaittu Unicode-avaruus | Sanat | Semanttinen Invarianssi |
| :--- | :--- | :--- | :---: | :---: |
| **R1 (exe_26f38060c9bd4ef3)** | `input_assignment_context.md` | No-Break Space (U+00A0) | 114 | `TÄYSI (100%)` |
| **R2 (exe_1aaabc9556704edc)** | `input_assignment_context.md` | En Space (U+2002) | 114 | `TÄYSI (100%)` |
| **R1 (exe_26f38060c9bd4ef3)** | `input_chat_log.md` | No-Break Space (U+00A0) | 5,489 | `TÄYSI (100%)` |
| **R2 (exe_1aaabc9556704edc)** | `input_chat_log.md` | No-Break Space (U+00A0), En Space (U+2002) | 5,865 | `POIKKEAMA` |
| **R1 (exe_26f38060c9bd4ef3)** | `input_chat_log_ai_only.md` | No-Break Space (U+00A0) | 5,334 | `TÄYSI (100%)` |
| **R2 (exe_1aaabc9556704edc)** | `input_chat_log_ai_only.md` | En Space (U+2002) | 5,710 | `POIKKEAMA` |
| **R1 (exe_26f38060c9bd4ef3)** | `input_chat_log_user_only.md` | No-Break Space (U+00A0) | 113 | `TÄYSI (100%)` |
| **R2 (exe_1aaabc9556704edc)** | `input_chat_log_user_only.md` | No-Break Space (U+00A0), En Space (U+2002) | 113 | `TÄYSI (100%)` |
| **R1 (exe_26f38060c9bd4ef3)** | `input_product_text.md` | No-Break Space (U+00A0) | 442 | `TÄYSI (100%)` |
| **R2 (exe_1aaabc9556704edc)** | `input_product_text.md` | En Space (U+2002) | 442 | `TÄYSI (100%)` |
| **R1 (exe_26f38060c9bd4ef3)** | `input_reflection_text.md` | No-Break Space (U+00A0) | 128 | `TÄYSI (100%)` |
| **R2 (exe_1aaabc9556704edc)** | `input_reflection_text.md` | En Space (U+2002) | 128 | `TÄYSI (100%)` |

## Globaalit Metriikat & Tieteellinen Luotettavuus (Kappa Benchmark)
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 85
- **Havaittujen luokkien kirjo:** failed, passed
- **Parittainen konsistenssi (Self-Consistency):** 92.94 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.8529
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.8529
- **Kappan Tieteellinen Tasoluokitus:** Lähes täydellinen sopivuus (Almost Perfect Agreement)
- **Keskivirhe (SE) ja 95 % Luottamusväli:** SE = `0.0579`, 95% CI = `[0.7395, 0.9664]`
- **Vertailu Ihmisasiantuntijoiden Benchmarkiin:** Ylittää ihmisasiantuntijoiden tyypillisen tason (0.65–0.80) — huipputason luotettavuus.
- **Marginaalinen vinouma (Marginal Bias / Run 1 vs Run 2):** `+0.0000`
- **Keskimääräinen Shannonin Entropia:** 0.0706
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Skaalatasokohtainen Erimielisyysjakauma (0–100 Vaativuustasot)

Atomit on normalisoitu emolohkonsa ääriarvojen perusteella universaalille 0–100 % vaativuusasteikolle. Tämä eliminoi eri pituisten asteikkojen (1–5 vs 1–6) aiheuttamat vertailuvirheet.

| Normalisoitu Vaativuustaso (0–100 %) | Yhteensä Atomeja | Erimielisyydet | Konsistenssi (%) |
| :--- | :---: | :---: | :---: |
| **81–100%: Korkein vaativuustaso (Top Mastery / Critical Rigor)** | 20 | 0 | 100.0 % |
| **61–80%: Korkea vaativuustaso (High Standard)** | 10 | 2 | 80.0 % |
| **41–60%: Keskitaso (Mid Standard)** | 20 | 1 | 95.0 % |
| **21–40%: Matala vaativuustaso (Low Standard)** | 10 | 1 | 90.0 % |
| **0–20%: Perustaso (Baseline / Minimum Viable)** | 25 | 2 | 92.0 % |

## Lohkokohtainen Erimielisyyskartta (Block Heatmap)

Taulukko havainnollistaa, missä matriisilohkoissa ilmenee eniten arviointieroja ajojen välillä. Lohkot, joissa on eniten erimielisyyksiä, on nostettu kärkeen sääntöjen kirkastamista varten.

| Lohko / Matriisi | Lohkon ID | Asteikko | Atomeja Yhteensä | Erimielisyydet | Konsistenssi (%) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Luovuus ja syvyys (Bloomin Taksonomia)** | `blk_f921c7c0989b47e8` | 1–6 | 30 | 4 | 86.7 % |
| **Luottamusarvio (XAI-Raportoija)** | `blk_6b8c766185294f7e` | 1–3 | 15 | 1 | 93.3 % |
| **Harkintakyky (Kahnemanin Kaksoisprosessiteoria)** | `blk_109dab5b6b3f403a` | 1–3 | 15 | 1 | 93.3 % |
| **Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)** | `blk_53f32679aa514fcb` | 1–5 | 25 | 0 | 100.0 % |

## Erimielisyyksien Juurisyydiagnoosi (Root Cause Triage)

Kaikki erimielisyydet on luokiteltu deterministisesti neljään kategoriaan: 1) Tiedonhaun aukko (yksi ajo löysi sitaatin, toinen ei), 2) Päättelyn aukko (molemmat löysivät tai molemmilta puuttui, mutta päätös eri), 3) Kontekstuaalinen ohitus, ja 4) Tekninen virhe / DLQ.

| Erimielisyyden Juurisyy | Esiintymiskerrat | Osuus Erimielisyyksistä (%) |
| :--- | :---: | :---: |
| **Tiedonhaun aukko (Retrieval Gap)** | 4 | 66.7 % |
| **Päättelyn aukko (Reasoning Gap)** | 0 | 0.0 % |
| **Kontekstuaalinen ohitus (Contextual Override)** | 2 | 33.3 % |
| **Tekninen virhe / DLQ (Technical Error)** | 0 | 0.0 % |
| **Yhteensä** | **6** | **100.0 %** |

## Makrotason Pistemäärä- ja Luottamusdiffit (Macro Score Drift 0–100)

Lohkokohtaiset pistemäärät perustuvat ajojen `normalized_score` -kenttään (0–100 asteikko) sekä atomitason läpäisyasteeseen.

- **Keskimääräinen itseisarvopoikkeama (MAD - Mean Absolute Delta):** `11.96` pistettä
- **Suurin yksittäisen lohkon poikkeama (Max Drift):** `31.05` pistettä

| Lohko / Matriisi | Run 1 Pisteet (Raaka & Norm) | Run 2 Pisteet (Raaka & Norm) | $\Delta$ Norm | Run 1 Waterfall-katkos | Run 2 Waterfall-katkos | Run 1 Läpäisy | Run 2 Läpäisy | $\Delta$ Läpäisy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`blk_53f32679aa514fcb` (Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki), Asteikko 1–5)** | Raw: 2.2 / 5 | Norm: 28.9 % | Raw: 2.2 / 5 | Norm: 28.9 % | +0.0 % | Taso 1.0 (3/5 osumaa) | Taso 1.0 (3/5 osumaa) | 52.0 % | 52.0 % | +0.0 % |
| **`blk_f921c7c0989b47e8` (Luovuus ja syvyys (Bloomin Taksonomia), Asteikko 1–6)** | Raw: 2.9 / 6 | Norm: 37.9 % | Raw: 3.3 / 6 | Norm: 46.3 % | +8.4 % | Taso 1.0 (3/5 osumaa) | Taso 1.0 (2/5 osumaa) | 60.0 % | 66.7 % | +6.7 % |
| **`blk_6b8c766185294f7e` (Luottamusarvio (XAI-Raportoija), Asteikko 1–3)** | Raw: 2.4 / 3 | Norm: 68.9 % | Raw: 1.8 / 3 | Norm: 37.9 % | -31.1 % | Taso 2.0 (4/5 osumaa) | Taso 2.0 (3/5 osumaa) | 66.7 % | 60.0 % | -6.7 % |
| **`blk_109dab5b6b3f403a` (Harkintakyky (Kahnemanin Kaksoisprosessiteoria), Asteikko 1–3)** | Raw: 1.9 / 3 | Norm: 46.3 % | Raw: 1.8 / 3 | Norm: 37.9 % | -8.4 % | Taso 2.0 (3/5 osumaa) | Taso 1.0 (4/5 osumaa) | 66.7 % | 60.0 % | -6.7 % |

## Evidenssiluokkien ja Ohitusten Jakauma (Evidence Class & Override Distribution)

Taulukko erittelee arvioitujen atomien jakauman kussakin ajossa: suorat empiiriset sitaatit, käänteisen evidenssin läpäisyt (Null Hypothesis), kontekstuaaliset ohitukset, sääntödemootiot ja hylkäykset.

| Ajo | Empiiriset sitaatit | Käänteiset läpäisyt (Null Hypothesis) | Kontekstuaaliset ohitukset | Sääntödemootiot | Hylätyt (FAILED) | Yhteensä arvioitu |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **R1 (exe_26f38060c9bd4ef3)** | 6 | 45 | 0 | 0 | 34 | 85 |
| **R2 (exe_1aaabc9556704edc)** | 8 | 43 | 0 | 0 | 34 | 85 |

## FinOps & Välimuistisäästöt (Cache Economics & Cost Drift)

| FinOps -metriikka | Run 1 | Run 2 | $\Delta$ (R2 - R1) |
| :--- | :---: | :---: | :---: |
| **Kokonaiskustannus ($)** | $1.3399 | $2.1993 | $+0.8595 |
| **Syötetokenit (Prompt)** | 1,156,305 | 1,324,108 | +167,803 |
| **Tuotostokenit (Completion)** | 181,158 | 95,429 | -85,729 |
| **Välimuistitokenit (Cached)** | 526,812 | 726,144 | +199,332 |
| **Välimuistin tuoma säästö ($)** | $0.0296 | $0.0408 | +0.0112 |

## Lainausten Aitoustarkastus (Lexical Grounding Audit)

Kaikki mallin poimimat suorat sitaatit tarkastetaan sanatarkasti ja whitespace-normalisoidusti (`str.find`) suhteessa alkuperäisiin syötetiedostoihin chimera- ja hallusinaatioriskien varalta.

| Ajo | Syötteet Saatavilla | Sitaatteja | Verifioidut | Vahvistamattomat | Aitoustaso (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **exe_26f38060c9bd4ef3** | Kyllä | 6 | 6 | 0 | 100.0 % |
| **exe_1aaabc9556704edc** | Kyllä | 8 | 7 | 1 | 87.5 % |

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 6 kpl
- **Contextual Override -lähtöiset erimielisyydet koko setissä:** 2 / 6
- **PASSED -> FAILED:** 3
- **FAILED -> PASSED:** 3
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Kysytyt Säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt ja kysymykset, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_5198e13cde3447fe9d0737a80abe458c` (Entropia: 1.000, Konsistenssi: 0.0%)
- **Lohko / Matriisi:** `Luovuus ja syvyys (Bloomin Taksonomia)` (`blk_f921c7c0989b47e8`)
- **Skaala / Taso:** `Arviointi` (Arvo: `5`)
- **Skooppi (Scope):** `paragraph` | **Käänteinen evidenssi (Inverse):** `Ei (False)`
- **Kysymys / Konsepti:** Grounding evaluative assessments in objective benchmarks, regulatory standards, or quantitative criteria.
- **Etsintäsääntö (Extraction Rule):** Evaluations are systematically anchored to explicit external standards, quantitative metrics, or formalized benchmarks.
- **Ankkuritargetti (Anchor Target):** Find evaluations anchored to formal benchmarks or regulatory standards.
- **Esimerkki (Contrastive Example):**
  - *Acceptable:* The authentication service complies with ISO/IEC 27001 Annex A.9 by enforcing multi-factor verification across all administrative endpoints.
  - *Rejected:* Our authentication system provides robust security features that safeguard sensitive customer data.

**Havaitut tilat, sitaatit ja perustelut ajoittain:**
- **Run 1 (exe_26f38060c9bd4ef3) - [FAILED]:**
  - **Sitaatti (Ei sitaattia):** -
  - **Perustelu:** *Vaikka CSRD-direktiivi ja EU-taksonomia mainitaan sääntelypaineena, tekstissä ei mitata havainnoitua suorituskykyä suoraan näitä standardeja vasten.*
- **Run 2 (exe_1aaabc9556704edc) - [PASSED]:**
  - **Sitaatti (Löytyi, 157 merkkiä):** `**Sääntelypaine:** CSRD-direktiivin ja
EU-taksonomian kaltaiset säädökset
tekevät kestävyydestä pakollista
(compliance) ja rajoitavat ei-kestävää
rahoitusta.`
  - **Perustelu:** *Tekstissä arvioidaan sääntelyn vaikutusta ja viitataan eksplisiittisesti EU-standardeihin (CSRD, EU-taksonomia), joita käytetään mittapuuna sille, mikä liiketoiminta säilyy rahoituskelpoisena.*

---

### Atom-ID: `tda_6a779cd5e9714994b83168dd0fef0ef7` (Entropia: 1.000, Konsistenssi: 0.0%)
- **Lohko / Matriisi:** `Luovuus ja syvyys (Bloomin Taksonomia)` (`blk_f921c7c0989b47e8`)
- **Skaala / Taso:** `Soveltaminen` (Arvo: `3`)
- **Skooppi (Scope):** `paragraph` | **Käänteinen evidenssi (Inverse):** `Ei (False)`
- **Kysymys / Konsepti:** Applying an abstract conceptual rule directly to an operational entity or workflow problem.
- **Etsintäsääntö (Extraction Rule):** The text applies an abstract framework to govern a concrete operational scenario or architectural artifact.
- **Ankkuritargetti (Anchor Target):** Find theoretical frameworks mapped to operational workflows.
- **Esimerkki (Contrastive Example):**
  - *Acceptable:* Applying the principle of bounded contexts, we assign customer billing and catalog management to separate isolated domain services.
  - *Rejected:* Bounded contexts represent linguistic and operational boundaries within Domain-Driven Design.

**Havaitut tilat, sitaatit ja perustelut ajoittain:**
- **Run 1 (exe_26f38060c9bd4ef3) - [FAILED]:**
  - **Sitaatti (Ei sitaattia):** -
  - **Perustelu:** *Teksti esittelee yleisiä strategisia suosituksia, mutta ei sovella abstraktia ohjaavaa sääntöä konkreettiseen operatiiviseen työnkulkuun.*
- **Run 2 (exe_1aaabc9556704edc) - [PASSED]:**
  - **Sitaatti (Löytyi, 107 merkkiä):** `Investoinnit**kiertotalouden ratkaisuihin** ja
**omaan uusiutuvaan**
**energiantuotantoon**. Toimitusketjun`
  - **Perustelu:** *Abstrakti malli (supermegatrendit, tulevaisuusresilienssi) kytketään konkreettisiin toimenpiteisiin, kuten kiertotalousinvestointeihin, omaan energiantuotantoon ja työntekijöiden hyvinvointipanostuksiin, jotka operationalisoivat periaatteet.*

---

### Atom-ID: `tda_216cc3fd45284deb8d51ea4cf2b2fd93` (Entropia: 1.000, Konsistenssi: 0.0%)
- **Lohko / Matriisi:** `Luovuus ja syvyys (Bloomin Taksonomia)` (`blk_f921c7c0989b47e8`)
- **Skaala / Taso:** `Muistaminen` (Arvo: `1`)
- **Skooppi (Scope):** `paragraph` | **Käänteinen evidenssi (Inverse):** `Kyllä (True)`
- **Kysymys / Konsepti:** Dogmatic assertion of universal fact presented without epistemic qualification, empirical proof, or literature citation.
- **Etsintäsääntö (Extraction Rule):** The proposition asserts absolute certainty regarding an empirical claim without providing epistemic boundaries or citation.
- **Ankkuritargetti (Anchor Target):** Find dogmatic assertions of unchallengeable fact.
- **Esimerkki (Contrastive Example):**
  - *Acceptable:* It is universally established that monolithic architectures are obsolete for all contemporary software deployments.
  - *Rejected:* Empirical studies suggest that microservice topologies yield scaling advantages primarily when team boundaries align with bounded contexts.

**Havaitut tilat, sitaatit ja perustelut ajoittain:**
- **Run 1 (exe_26f38060c9bd4ef3) - [PASSED] **[CONTEXTUAL OVERRIDE]**:**
  - **Sitaatti (Ei sitaattia):** -
  - **Perustelu:** *Väitteet ja tulevaisuuden kehityskulut ankkuroidaan viittauksilla Sitran megatrendiraportteihin ja EU-sääntelyyn, eikä dogmaattisia perusteettomia yleistyksiä esitetä ilman kontekstuaalista taustoitusta.*
- **Run 2 (exe_1aaabc9556704edc) - [FAILED]:**
  - **Sitaatti (Ei sitaattia):** -
  - **Perustelu:** *Kirjoittaja esittää useita kategorisia väitteitä tulevaisuuden luonteesta ja yritysten menestyksen ehdoista ilman lähteitä tai ehdollista kieltä, kohdellen niitä itsestään selvinä totuuksina.*

---

### Atom-ID: `tda_ab3ebf5a42f0d72eca9acceeb2e12ce1` (Entropia: 1.000, Konsistenssi: 0.0%)
- **Lohko / Matriisi:** `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` (`blk_109dab5b6b3f403a`)
- **Skaala / Taso:** `Systeemi 1 (Nopea)` (Arvo: `1`)
- **Skooppi (Scope):** `paragraph` | **Käänteinen evidenssi (Inverse):** `Ei (False)`
- **Kysymys / Konsepti:** The text links concepts through qualitative semantic associations, narrative metaphors, or intuitive analogies rather than formal mathematical or statistical derivations.
- **Etsintäsääntö (Extraction Rule):** Locate and extract substantive evidence demonstrating that the text connects at least two concepts via qualitative semantic association, descriptive analogy, or narrative flow without formal mathematical derivation.
- **Ankkuritargetti (Anchor Target):** Find qualitative associative links, intuitive metaphors, or narrative transitions connecting concepts.
- **Esimerkki (Contrastive Example):**
  - *Acceptable:* Technology evolves like a natural force of nature, requiring organizational culture to flow organically alongside it.
  - *Rejected:* A formal statistical derivation yielded a Pearson correlation coefficient of 0.84 between the two variables.

**Havaitut tilat, sitaatit ja perustelut ajoittain:**
- **Run 1 (exe_26f38060c9bd4ef3) - [PASSED]:**
  - **Sitaatti (Löytyi, 84 merkkiä):** `Sitran näkemyksen mukaan tulevaisuus ei vain vyöry päälle, vaan sen suunta on avoin.`
  - **Perustelu:** *Käyttäjä kytkee käsitteet toisiinsa laadullisen ja metaforisen assosiaation kautta ilman formaalia matemaattista johtamista.*
- **Run 2 (exe_1aaabc9556704edc) - [FAILED]:**
  - **Sitaatti (Ei sitaattia):** -
  - **Perustelu:** *Käyttäjä ei itse rakenna selittäviä analogioita tai metaforia; lähinnä pyytää rakenteellisia muutoksia (esim. supermegatrendejä, taulukoiden poistoa).*

---

### Atom-ID: `tda_a3d407a71ade4ea4aa3afeaf1bb61b3c` (Entropia: 1.000, Konsistenssi: 0.0%)
- **Lohko / Matriisi:** `Luovuus ja syvyys (Bloomin Taksonomia)` (`blk_f921c7c0989b47e8`)
- **Skaala / Taso:** `Arviointi` (Arvo: `5`)
- **Skooppi (Scope):** `paragraph` | **Käänteinen evidenssi (Inverse):** `Ei (False)`
- **Kysymys / Konsepti:** Formulating a defensible judgment regarding the efficacy, validity, or systemic viability of an architectural option.
- **Etsintäsääntö (Extraction Rule):** The text delivers an explicit evaluative conclusion grounded in documented technical, economic, or operational evidence.
- **Ankkuritargetti (Anchor Target):** Find evaluative conclusions regarding system viability or merit.
- **Esimerkki (Contrastive Example):**
  - *Acceptable:* Based on failover latency measurements and recovery time objectives, we judge asynchronous replication inadequate for our financial transaction ledger.
  - *Rejected:* Asynchronous replication is our preferred approach for synchronizing data stores.

**Havaitut tilat, sitaatit ja perustelut ajoittain:**
- **Run 1 (exe_26f38060c9bd4ef3) - [FAILED]:**
  - **Sitaatti (Ei sitaattia):** -
  - **Perustelu:** *Teksti esittää laajoja strategisia väitteitä kestävyydestä, mutta ei perustele ratkaisujen elinkelpoisuutta dokumentoidulla teknisellä tai empiirisellä evidenssillä.*
- **Run 2 (exe_1aaabc9556704edc) - [PASSED]:**
  - **Sitaatti (Löytyi, 169 merkkiä):** `Yrityksemme
menestys riippuu kyvystämme integroida nämä kolme supermegatrendiä strategiseen
päätöksentekoon ja nähdä **kestävyys ja autonomia** uusina kilpailutekijöinä.`
  - **Perustelu:** *Tekstissä on eksplisiittinen johtopäätös yrityksen menestyksen edellytyksistä, joka nojaa aiemmin kuvattuihin ekologisiin, geopoliittisiin ja sosiaalisiin perusteluihin.*

---

### Atom-ID: `tda_42390948661c457983a7b60879a41eca` (Entropia: 1.000, Konsistenssi: 0.0%)
- **Lohko / Matriisi:** `Luottamusarvio (XAI-Raportoija)` (`blk_6b8c766185294f7e`)
- **Skaala / Taso:** `Keskivarma (50%)` (Arvo: `2`)
- **Skooppi (Scope):** `sentence` | **Käänteinen evidenssi (Inverse):** `Kyllä (True)`
- **Kysymys / Konsepti:** BANNED PATTERN: Providing recommendations without bounding operational assumptions or validity scope.
- **Etsintäsääntö (Extraction Rule):** Detect where recommendations are formulated as universal prescriptions without defining the boundary conditions, environmental assumptions, or constraints under which the synthesized advice remains reliable.
- **Ankkuritargetti (Anchor Target):** Find unbounded recommendations lacking scope conditions.
- **Esimerkki (Contrastive Example):**
  - *Acceptable:* This advisory holds provided customer acquisition cost remains under 45€€ and interest rates do not exceed 4%. (Explicitly bounds operational validity).
  - *Rejected:* This organizational model will guarantee success across all operating units regardless of market conditions. (Unbounded universal prescription without constraints).

**Havaitut tilat, sitaatit ja perustelut ajoittain:**
- **Run 1 (exe_26f38060c9bd4ef3) - [PASSED] **[CONTEXTUAL OVERRIDE]**:**
  - **Sitaatti (Ei sitaattia):** -
  - **Perustelu:** *Tekstissä ei esitetä sitovia toimintasuosituksia yleispätevinä totuuksina ilman toimintaympäristön reunaehtoja tai soveltuvuusalueen rajausta.*
- **Run 2 (exe_1aaabc9556704edc) - [FAILED]:**
  - **Sitaatti (Ei sitaattia):** -
  - **Perustelu:** *Teksti esittää vahvoja, yleispätevinä kuulostavia suosituksia (esim. vain kestävät mallit saavat rahoitusta) ilman eksplisiittisiä rajausehtoja tai toimintaympäristön rajoja.*

---

## Kaikkien Arvioitujen Atomien Yhteenvetotaulukko (Complete Atom Consensus Manifest)

Taulukko listaa kaikki vertailluissa ajoissa arvioidut yhteiset atomit, niiden tason ja lohkon, suoritustilat sekä lainausten aitoustarkastuksen tilan.

| Atom-ID | Lohko (Block) | Taso (Scale) | Run 1 | Run 2 | Konsistenssi | Sitaatti | Verifioitu |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `tda_07ef835fd139e70fd9d9f2151dc9a5aa` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Luominen | PASSED | PASSED | 100% | Kyllä | Kyllä |
| `tda_10f455c36f754d33a3a551e9e7b61da4` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Analysointi | PASSED | PASSED | 100% | Kyllä | Kyllä |
| `tda_131403148eab4c739149e6bd29164ce2` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Ymmärtäminen | PASSED | PASSED | 100% | Kyllä | Kyllä |
| `tda_135ee4d2f4e28b3305cbae57482e34b0` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Navigaattori (Pintapuolinen) | FAILED | FAILED | 100% | Ei | - |
| `tda_20e76f768d24458fb2cc131b2bde4e04` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Soveltaminen | PASSED | PASSED | 100% | Ei | - |
| `tda_20f87ebd0c5b7de765cc4f6abc9b0fdd` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Systeemi 1 (Nopea) | PASSED | PASSED | 100% | Kyllä | Kyllä |
| `tda_216cc3fd45284deb8d51ea4cf2b2fd93` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Muistaminen | PASSED | FAILED | 0% | Ei | - |
| `tda_2a2677a8c8b277adb2162dd56259ff22` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Ymmärtäminen | FAILED | FAILED | 100% | Ei | - |
| `tda_2d12f15e1c2d4488b7c2ef32d0ccfa26` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Systeemi 1 (Nopea) | PASSED | PASSED | 100% | Ei | - |
| `tda_339c95ad646e7212972ceee0faf0d024` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Arviointi | FAILED | FAILED | 100% | Ei | - |
| `tda_353aa6c896db47fb9d29b06a69bf77d4` | `Luottamusarvio (XAI-Raportoija)` | Keskivarma (50%) | PASSED | PASSED | 100% | Ei | - |
| `tda_3a362e01de66444c813e5b79adec27bf` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Systeemi 1 (Nopea) | PASSED | PASSED | 100% | Ei | - |
| `tda_3c7ad640672b2c4bf2240572fae8d45a` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Arkkitehti (Aktiivinen haastaja) | FAILED | FAILED | 100% | Ei | - |
| `tda_3db25a2bde2741e4a68a8313a8fa9aea` | `Luottamusarvio (XAI-Raportoija)` | Keskivarma (50%) | FAILED | FAILED | 100% | Ei | - |
| `tda_3ee4fe63a8ac50d24595bd3e90a6b016` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Matkustaja (Sokea usko) | FAILED | FAILED | 100% | Ei | - |
| `tda_40c435f393cb4357b31cf835ca601a54` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Luominen | FAILED | FAILED | 100% | Ei | - |
| `tda_42390948661c457983a7b60879a41eca` | `Luottamusarvio (XAI-Raportoija)` | Keskivarma (50%) | PASSED | FAILED | 0% | Ei | - |
| `tda_43739e72c1b44b9abaac57e2052bad96` | `Luottamusarvio (XAI-Raportoija)` | Erittäin Epävarma (0%) | PASSED | PASSED | 100% | Ei | - |
| `tda_4798b15b4e6643769461d2b1e6731031` | `Luottamusarvio (XAI-Raportoija)` | Korkea Luottamus (100%) | FAILED | FAILED | 100% | Ei | - |
| `tda_4839249852bba22f357b425f51648317` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Luominen | PASSED | PASSED | 100% | Ei | - |
| `tda_4967c2791d574142b113692976c60d54` | `Luottamusarvio (XAI-Raportoija)` | Keskivarma (50%) | PASSED | PASSED | 100% | Ei | - |
| `tda_4ba32055738247d28e00a597f505ce9e` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Ymmärtäminen | PASSED | PASSED | 100% | Ei | - |
| `tda_4cdfcc7d7fda5582ba8f695b916a7ecd` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Analysointi | PASSED | PASSED | 100% | Ei | - |
| `tda_4ee8a21f82b94f07bec131c867a9bde6` | `Luottamusarvio (XAI-Raportoija)` | Korkea Luottamus (100%) | FAILED | FAILED | 100% | Ei | - |
| `tda_5198e13cde3447fe9d0737a80abe458c` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Arviointi | FAILED | PASSED | 0% | Kyllä | Kyllä |
| `tda_5257ba1edae34afe8b837c8c238cf743` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Systeemi 2 (Hidas) | FAILED | FAILED | 100% | Ei | - |
| `tda_5568f81c93bc4d1fb524fbfc1d9f0e04` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Siirtymä | PASSED | PASSED | 100% | Ei | - |
| `tda_58a9677a26f05176837fdd0ddf490619` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Reaktiivinen huomioija | PASSED | PASSED | 100% | Ei | - |
| `tda_5a44b123cfdb8ed9d8cfe4d997c60968` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Arkkitehti (Aktiivinen haastaja) | PASSED | PASSED | 100% | Ei | - |
| `tda_5c038283b551f38d4b73d57ba6f220f4` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Arkkitehti (Aktiivinen haastaja) | PASSED | PASSED | 100% | Ei | - |
| `tda_5c74fc143b2f4a11a7b16ca370902414` | `Luottamusarvio (XAI-Raportoija)` | Erittäin Epävarma (0%) | PASSED | PASSED | 100% | Ei | - |
| `tda_5fc55ef72665907c426e2598cddde565` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Siirtymä | PASSED | PASSED | 100% | Kyllä | Kyllä |
| `tda_64cce5cf564a497dbbc2341248cea637` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Systeemi 2 (Hidas) | FAILED | FAILED | 100% | Ei | - |
| `tda_657fb164be984788a760eed250b3bc61` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Kuljettaja (Kriittinen ohjaaja) | FAILED | FAILED | 100% | Ei | - |
| `tda_68d4f9593be9742fcc5879b9a535496d` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Muistaminen | PASSED | PASSED | 100% | Ei | - |
| `tda_6a779cd5e9714994b83168dd0fef0ef7` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Soveltaminen | FAILED | PASSED | 0% | Kyllä | Kyllä |
| `tda_6df2bc5ac5e194367107f8d29fa6503e` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Siirtymä | FAILED | FAILED | 100% | Ei | - |
| `tda_71e60846894545b2bc43a3361b7a5a9c` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Arkkitehti (Aktiivinen haastaja) | FAILED | FAILED | 100% | Ei | - |
| `tda_7722eed3ab8338b64bf6c1e0ec07b2e0` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Navigaattori (Pintapuolinen) | FAILED | FAILED | 100% | Ei | - |
| `tda_7730ca085ba090f491a5a9bb2da229e4` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Siirtymä | FAILED | FAILED | 100% | Ei | - |
| `tda_77b39157c15d08be6d7d368c72370382` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Matkustaja (Sokea usko) | PASSED | PASSED | 100% | Ei | - |
| `tda_7b88a578c3824b31b83a5154f7d3667a` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Systeemi 1 (Nopea) | PASSED | PASSED | 100% | Ei | - |
| `tda_7cee768453a6f28915b429b87f465ce6` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Matkustaja (Sokea usko) | PASSED | PASSED | 100% | Ei | - |
| `tda_7d8a6c9af1db63c4ad372fe7b4768578` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Arviointi | PASSED | PASSED | 100% | Ei | - |
| `tda_7db7dc21a6ce417abd9322c34f8c6242` | `Luottamusarvio (XAI-Raportoija)` | Erittäin Epävarma (0%) | PASSED | PASSED | 100% | Ei | - |
| `tda_8275735bde0244e2bdbf3ab915838d59` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Reaktiivinen huomioija | PASSED | PASSED | 100% | Ei | - |
| `tda_85156bd626adcdf9c7d3dba38a3964d4` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Siirtymä | PASSED | PASSED | 100% | Ei | - |
| `tda_85988e1249fe8a9a3ec181163f17c006` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Analysointi | FAILED | FAILED | 100% | Ei | - |
| `tda_85ef05fdcd2f48afb925fd03b6c54d4d` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Matkustaja (Sokea usko) | PASSED | PASSED | 100% | Ei | - |
| `tda_86b9e792dd604b37a3443bffe25de8dd` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Kuljettaja (Kriittinen ohjaaja) | FAILED | FAILED | 100% | Ei | - |
| `tda_87b3fb9180df54e6c951fb7099283994` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Ymmärtäminen | PASSED | PASSED | 100% | Ei | - |
| `tda_9a8a71406006c7c7d8a21ac227050494` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Analysointi | PASSED | PASSED | 100% | Ei | - |
| `tda_9e809ba2555530294da291e98728c6ac` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Kuljettaja (Kriittinen ohjaaja) | PASSED | PASSED | 100% | Ei | - |
| `tda_9e86b88424442e661d4a9e9737b6d78a` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Navigaattori (Pintapuolinen) | PASSED | PASSED | 100% | Ei | - |
| `tda_9fd2fff3ab4a46d29b5df31488561dd4` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Arkkitehti (Aktiivinen haastaja) | FAILED | FAILED | 100% | Ei | - |
| `tda_a08f0bc1e4f14623ab2248528ae42a3d` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Navigaattori (Pintapuolinen) | PASSED | PASSED | 100% | Ei | - |
| `tda_a127d4437acf03201ec861134693f96f` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Soveltaminen | PASSED | PASSED | 100% | Ei | - |
| `tda_a3d407a71ade4ea4aa3afeaf1bb61b3c` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Arviointi | FAILED | PASSED | 0% | Kyllä | Kyllä |
| `tda_a88bbeb79f8bf88f989913cf1ce6fbba` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Systeemi 2 (Hidas) | FAILED | FAILED | 100% | Ei | - |
| `tda_a9c96a0c55fe4ac884795440c722eb5d` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Reaktiivinen huomioija | FAILED | FAILED | 100% | Ei | - |
| `tda_ab3ebf5a42f0d72eca9acceeb2e12ce1` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Systeemi 1 (Nopea) | PASSED | FAILED | 0% | Kyllä | Kyllä |
| `tda_b120e2c0a40840358df1e64a4b788b30` | `Luottamusarvio (XAI-Raportoija)` | Erittäin Epävarma (0%) | PASSED | PASSED | 100% | Ei | - |
| `tda_b36d3ec7b1f94fe9ad4b45795a8a104b` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Muistaminen | FAILED | FAILED | 100% | Ei | - |
| `tda_b3c69e002634430ca9f2e2a33f7b280e` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Luominen | FAILED | FAILED | 100% | Ei | - |
| `tda_b7dfe23403db4db5b92a29a8bda9957c` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Ymmärtäminen | PASSED | PASSED | 100% | Ei | - |
| `tda_bd85f009b0fb4f7899b40ff0e763dee7` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Kuljettaja (Kriittinen ohjaaja) | FAILED | FAILED | 100% | Ei | - |
| `tda_bda074845f0c4add8c00591689694299` | `Luottamusarvio (XAI-Raportoija)` | Erittäin Epävarma (0%) | PASSED | PASSED | 100% | Ei | - |
| `tda_bfbe65b639b54106913902d5bd0ae6ab` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Analysointi | FAILED | FAILED | 100% | Ei | - |
| `tda_c09b70a9063fcf5510726fda9a004deb` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Kuljettaja (Kriittinen ohjaaja) | PASSED | PASSED | 100% | Ei | - |
| `tda_c17684acfcbe4a918e5ae0705b452b06` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Navigaattori (Pintapuolinen) | PASSED | PASSED | 100% | Ei | - |
| `tda_c430fd70a5b143bdb79214ecfb8fa81c` | `Luottamusarvio (XAI-Raportoija)` | Korkea Luottamus (100%) | PASSED | PASSED | 100% | Ei | - |
| `tda_c69a7f252b234e938fbac7adfaadb302` | `Luottamusarvio (XAI-Raportoija)` | Keskivarma (50%) | PASSED | PASSED | 100% | Ei | - |
| `tda_c95740149e215669c54536c9d4f48e50` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Arviointi | PASSED | PASSED | 100% | Ei | - |
| `tda_ca18fc149c7b3ea9488cf8e943c619c7` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Soveltaminen | FAILED | FAILED | 100% | Ei | - |
| `tda_ca7f2adeb115f03037fdb404ae22d983` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Reaktiivinen huomioija | FAILED | FAILED | 100% | Ei | - |
| `tda_cb81a913f1f571b8db459fc2136cdf51` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Systeemi 2 (Hidas) | PASSED | PASSED | 100% | Ei | - |
| `tda_cef8b22d81ee58ec18084d05b9d430f4` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Reaktiivinen huomioija | PASSED | PASSED | 100% | Ei | - |
| `tda_cf5901a7a1694d719cdcaf246a5dddd0` | `Luottamusarvio (XAI-Raportoija)` | Korkea Luottamus (100%) | FAILED | FAILED | 100% | Ei | - |
| `tda_d04a2a547f224316ae52a2f3a454240b` | `Luottamusarvio (XAI-Raportoija)` | Korkea Luottamus (100%) | FAILED | FAILED | 100% | Ei | - |
| `tda_d29b77c237394ccab4b8d52502f873f9` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Muistaminen | PASSED | PASSED | 100% | Ei | - |
| `tda_d95b263f55504cc38901001296374825` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Luominen | PASSED | PASSED | 100% | Ei | - |
| `tda_daf7e137f58333015ad078c35a873ecc` | `Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)` | Matkustaja (Sokea usko) | FAILED | FAILED | 100% | Ei | - |
| `tda_defc33928bb9c172f2f64e090b90f935` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Muistaminen | FAILED | FAILED | 100% | Ei | - |
| `tda_eec00de564394e9dbcc5744ca77f8e60` | `Luovuus ja syvyys (Bloomin Taksonomia)` | Soveltaminen | PASSED | PASSED | 100% | Ei | - |
| `tda_f125f44e05ca70b4617f6ce8ca007977` | `Harkintakyky (Kahnemanin Kaksoisprosessiteoria)` | Systeemi 2 (Hidas) | PASSED | PASSED | 100% | Ei | - |

