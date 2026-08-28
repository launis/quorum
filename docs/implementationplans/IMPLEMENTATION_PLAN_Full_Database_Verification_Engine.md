<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_prompt_generation_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_de_generator_execution_paradigm.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: Full Database Verification Engine & Complete Prompt/Seed Sanitization

**Goal:** Establish a permanent, automated full database verification and sanitization engine across ALL prompt-feeding database collections (`prompt_blocks`, `steps`, `workflows`, `output_profiles` in `backend_v2/seed/seed_data.json`) to eliminate the **Split-Brain** cognitive failure state, prevent attention head hijacking from legacy scraping artifacts and chatbot-specific hardcoding, anchor deterministic epistemic decision thresholds, enforce Tripartite Pipeline Modality Invariance (universal Phase 1 sensor extraction vs. targeted Phase 2 synthesis recipient coaching), validate workflow input routing (`input_mappings`), and enforce strict Separation of Concerns between Ontology (`concept_description`) and Heuristics (`extraction_rule`).

1. **Layer 1 Hardening:** Inject the epistemic decision protocol into `MATRIX_SENSOR_SYSTEM_PROMPT` in `@[backend_v2/models/prompts/matrix_evaluation.py]`.
2. **Automated Verification Engine:** Build an automated static verification script `[NEW] @[scripts/audit_database_atoms.py]` enforcing strict heuristic, structural, and semantic prompt linting across all 4 prompt-feeding collections:
   - **`prompt_blocks`**: Forbidding "BANNED SOURCES", "EXTRACTION CONDITION", "FAIL FAST", "Do not evaluate", raw XML, "in an block", truncated sentences, empty extraction rules, user-prompt hardcoding / chatbot role prefixes, and imperative commands in ontology descriptions across all 152 atoms in 13 matrices.
   - **`steps`**: Validating `expected_inputs[].ai_description`, `model_strategy` presence, and referential integrity of `role_block_id`, `extraction_protocol_block_id`, and `criteria_block_ids`.
   - **`workflows`**: Validating `expected_inputs` (`ai_description` formatting), checking that all `steps[].input_mappings` point to valid `$inputs.<key>` or `$steps.<id>.<key>` paths, and verifying `system_prompt` purity (no raw XML).
   - **`output_profiles`**: Validating synthesis directives, section instructions, and layout block mappings (no raw XML, no unanchored text).
3. **Complete Database Sanitization (Layer 4):** Sanitize all 13 matrices in `@[backend_v2/seed/seed_data.json#L970-L3235]` (100% clean ontological concept descriptions, 49 populated extraction rules, 44 modality-decoupled atoms) plus any corrupted fields in `steps`, `workflows`, and `output_profiles` without mutating human coaching philosophy.
4. **Validation & Quality Gates:** Execute full verification, database re-seeding, and live statistical E2E variance tests.

---

## System 2 Tri-Axis Dialectical Analysis & Research

### 1. The Tri-Axis Dialectic (Prosecution, Defense, Realist)

#### ⚖️ Syyttäjä (The Prosecution - Maximum Pessimism & Failure Modes)
- **Attention Dilution & Head Hijacking:** Jos tietokanta-atomeihin tai workflow-kenttiin jätetään kehittäjäkomentoja (`BANNED SOURCES:`, `EXTRACTION CONDITION:`, `FAIL FAST and return null`), modernien mallien (Gemini 2.0, Claude 3.5, GPT-4o) turvallisuus- ja järjestelmätason huomiopäät aktivoituvat väärässä kontekstissa. Malli kokee **Split-Brain** -tilan: se ei tiedä, onko kyseessä ylätason esto (system jailbreak / data starvation) vai arvioitavan tekstin kriteeri.
- **Over-Sanitization Pitfall:** Kaikkien 152 atomin ja workflow-määritysten muokkaaminen sisältää riskin ihmisen laatiman valmennusfilosofian (`prompt_preservation_mandate`) tahattomasta vesittämisestä tai ontologisen tarkkuuden heikkenemisestä.
- **Empty Rule & Cognitive Overload Vulnerability:** 49 atomia sisältää täysin tyhjän `extraction_rule` -kentän (`""`), jolloin `<extraction_rule>`-tagi putoaa pois kehotteesta ja malli joutuu arvaamaan operationalisoinnin. Lisäksi 60+ atomissa operatiiviset käskyt (`CRITICAL DIRECTIVE: LOCATE...`, `IDENTIFY...`) on tungettu `concept_description`-kenttään saastuttaen johtoryhmän UI-raportit, ja 64 atomia sisältää kieltolauseita (`Do not evaluate...`), jotka laukaisevat *Ironic Rebound* -ilmiön.
- **Unverified Workflow Input Routing:** Jos `workflows.input_mappings` viittaa olemattomiin syötekenttiin tai väärin muotoiltuihin polkuihin, `PromptCompiler.build_xml_context()` epäonnistuu ajonaikaisesti tai jättää syötekenttiä pois LLM-kontekstista.
- **Context Caching Fragility:** Mikäli järjestelmäkehotteeseen tai atomeihin vuotaa dynaamisia ajonaikaisia muuttujia, Vertex AI / Gemini Context Caching -prefix rikkoutuu.

#### 🛡️ Puolustus (The Defense - Architectural Necessity & Value Anchor)
- **Kognitiivisen Neljännen Seinän Eheyttäminen & Separation of Concerns:**
  Four-Layer Clean Stack -hierarkian (`ki_llm_extraction_architecture.md`, `ki_prompt_generation_architecture.md`) mukaisesti:
  1. *Layer 1 (Static System Directives):* Sisältää globaalit päätöksentekosäännöt (`<epistemic_decision_protocol>`).
  2. *Layer 4 (Dynamic User Payload & Assertions):* Erotetaan puhtaat ontologiset konseptikuvaukset (`concept_description` = mitä käsite tarkoittaa loppukäyttäjälle ja teorialle) ja operatiiviset heuristiikat (`extraction_rule` = IF/THEN-tarkastusaskeleet sensorille) luonnollisella englannin kielellä ilman raakaa XML-koodia tai kehittäjäkomentoja.
- **Täysi Tietokannan Prompt-Kattavuus (Full Database Verification):** Tarkastusmoottori ei rajoitu vain atomeihin, vaan tarkastaa kaikki 4 prompt-dataa syöttävää kokoelmaa (`prompt_blocks`, `steps`, `workflows`, `output_profiles`), varmistaen referentiaalisen eheyden ja syöterouttauksen.
- **Deterministic Epistemic Threshold & Oikeudellinen Syyttömyysolettama (Burden of Proof):**
  Kielimallien luontainen *Hyper-Kriittisyysharha (Hyper-Criticality Bias)* ratkaistaan injektoimalla `<epistemic_decision_protocol>`:
  > `"- INVERSE / NEGATIVE CLAIMS (Inverse Evidence): An error, fallacy, or structural weakness is considered present (is_true = true) ONLY if it is actively committed and unhedged. If the author acknowledges constraints, provides counter-evidence, or expresses appropriate epistemic humility, the negative claim is not substantiated (is_true = false)."`
  Tämä luo deterministisen loogisen kynnyksen, jossa kirjoittajan osoittama tiedostettu epävarmuus vapauttaa hänet virhesyytteestä.
- **Kaksipuolinen Tasapainotettu Symmetria:**
  1. *Positiivisilta väitteiltä (`is_inverse: false`)* vaaditaan aktiivinen rakenteellinen näyttö (poistaa positiiviset hallusinaatiot).
  2. *Käänteisiltä väitteiltä (`is_inverse: true`)* vaaditaan aktiivinen, korjaamaton virhe (poistaa stokastisen heilahtelun).
- **Automatisoitu Zero-Trust -linttaus:** `audit_database_atoms.py` varmistaa, ettei koodikantaan voi enää koskaan päätyä rikkinäisiä tokeneita, tyhjiä sääntöjä, viallisia input mappingeja tai injektiojäänteitä.

#### 🔭 Realisti (The Realist - Ground Truth & Pragmatic Execution Synthesis)
- **Synthesized Mandate:** Toteutetaan kattava monitauluinen tarkastusmoottori (`scripts/audit_database_atoms.py`), suoritetaan `seed_data.json` -tiedoston kirurginen sanitointi (13 matriisin 152 atomia sekä workflow/step/output_profile -kentät) vault-varmuuskopioinnin kautta ja päivitetään `matrix_evaluation.py` staattisella episteemisellä protokollalla. Todistetaan varianssin romahdus tilastollisella E2E-testillä.

---

## Codebase Verification Summary (Empirically Confirmed)

| Metric | Value | Source |
| :--- | :--- | :--- |
| Total matrices | 13 | `seed_data.json` (`category_id == "matrix"`) |
| Total TDA atoms | 152 | Nested at `scales[].claims[].tda_assertions[]` (3-level nesting) |
| Empty `extraction_rule` fields | 49 | Kahneman: 3, Archivist: 12, Causal Analyst: 1, Judge: 9, XAI Reporter: 1, TaskGuard: 8, Causal Abductive: 3, TaskXAI: 6, Epistemic Humility: 6 |
| Atoms with raw XML in `concept_description` / `extraction_rule` | 4 | Confirmed via script |
| Atoms with chat hardcoding (`user prompt`, `role prefixes`, `Scan ONLY`) | 33 | Confirmed via script |
| Blocks with raw XML in `ai_description` | 11 | 5 personas, 2 matrix `ai_description`s, 2 system_rules, 1 protocol, 1 task_definition |
| Total Steps in seed vault | 19 | `seed_data.json` (`steps` array) |
| Total Workflows in seed vault | 1 | `seed_data.json` (`workflows` array) |
| Total Output Profiles in seed vault | 1 | `seed_data.json` (`output_profiles` array) |
| `MATRIX_SENSOR_SYSTEM_PROMPT` current state | 20 lines, missing `<epistemic_decision_protocol>`, contains ambiguous open-ended examples on L6 and L13 | `@[backend_v2/models/prompts/matrix_evaluation.py]` |
| `test_matrix_evaluation.py` current state | 31 lines, 2 tests, no ISTQB negative partitions | `@[backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py]` |
| `scripts/audit_database_atoms.py` | Does NOT exist | Confirmed via `list_dir` |
| TDAAssertion model `extraction_rule` field | `str \| None = Field(default=None)` | `@[backend_v2/models/v2_core.py#L202]` |
| `concept_description` field | `Annotated[str, StringConstraints(min_length=10)]` | `@[backend_v2/models/v2_core.py#L153-L257]` (TDAAssertion class) |
| Seed registry validation path | `STANDARD_REGISTRY["prompt_blocks"]["model"]` = `TypeAdapter(AnyPromptBlock)` | `@[backend_v2/seed/seed_registry.py#L48]` |
| `seed_data.json` size | 476KB, 8498 lines | Confirmed |

---

## 8-Item Technical Debt & Anomaly Sweep (Audit Findings)

| Debt Category | Scope & Affected Matrices | Concrete Anomaly Examples (Identified via Script) | Architectural Remediation |
| :--- | :--- | :--- | :--- |
| **1. Prompt Injection Residuals & Scraping Artifacts (Split-Brain)** | 14 atoms across Bloom, Archivist, Falsifier, TaskGuard, Causal Abductive, TaskXAI, Epistemic Humility | `tda_92680081ffb244d8abbdc99120a3291f`: `"BANNED SOURCES: Reject matches from user inputs or prefixes."`<br>`tda_d262dd4421bd4af68191eb1f4d0faf26`: `"EXTRACTION CONDITION: role prefixes exist, focus on output compared to input. ."`<br>`tda_715eb98a6f4a4a1e944db99f5eaaded9`: `"Find epistemic boundary markers. If absent, FAIL FAST and return null."` | Strip all meta-commands, uppercase shouting, and pseudokoodi; formulate clean, professional declarative English descriptions defining exact semantic targets. |
| **2. Negative Guidance in Concepts & Rules (Ironic Rebound)** | 64 atoms across 13 matrices (Toulmin, Bloom, Goodhart, Archivist, Causal Analyst, Falsifier, Epistemic Humility, etc.) | `tda_92680081ffb244d8abbdc99120a3291f`: `"Do not evaluate."`<br>`tda_0b7512034e6f40db9b4ea46b64af4e0d`: `"Do not judge subjectively."`<br>`"Do not accept purely theoretical analogies."`, `"DEPRECATED - V4..."` | Translate negative phrasing into positive, objective ontological target criteria (specifically: *"Require structured empirical data points, statistical metrics, or peer-reviewed citations"*). |
| **3. Grammar Corruptions & Truncated Text (Entropy Growth)** | 8 atoms (Goodhart, Archivist, Falsifier, Epistemic Humility) | `tda_c642cbc768fa4f54a8718452d779c607`: `"Scan the document. 3 or more exist."`<br>`tda_3eed2113bd9842f3b8fd050046505e4d` + 10 atoms: `"If role prefixes exist, the exact quote MUST be located in an block."` | Reconstruct complete, grammatically coherent English sentences specifying exact target entities. Broken grammar raises model token entropy ($H$), forcing the LLM to waste reasoning tokens decoding cryptic fragments instead of evaluating content. Ensure `concept_description` contains full ontological definitions and `extraction_rule` contains complete actionable IF/THEN detection steps. |
| **4. Raw XML in Data & Block Fields (XML Sovereignty & Prompt Escape)** | 4 atoms (TaskGuard `tda_65cb33b82c54425aa86df7e84b66ffde`, Causal Analyst `tda_c5804a91...`, Epistemic Humility `tda_22e3598e...`), 2 matrix blocks (`matrix_causal_abductive`, `matrix_taskxai_clarity`), and 7 persona/synthesis blocks (`blk_e6b638d1...` - `blk_14cd9c4b...`, `blk_34def5d6...`, `blk_ad303690...`) | `tda_65cb33b82c54425aa86df7e84b66ffde`: `<ambiguity_protocol> ABSOLUTE LEXICAL ENFORCEMENT: You are a mechanical parser... </ambiguity_protocol>`<br>`blk_c3bc5f3eb8e74110`: `<role_enforcement>`, `<banned_concepts>`<br>`blk_34def5d628ba4ed4`: `<section_rules>`, `<objective>`, `<rules>` | Strip all raw XML tags and `< / >` delimiters completely from data fields per `de_generator_mandate_no_xml` and `compiler_xml_sovereignty_mandate`. Enforce pure Markdown/declarative text in seed data and reserve XML encapsulation exclusively for Layer 1 AST Prompt Compiler. |
| **5. Empty Extraction Rules & Cognitive Overload (Separation of Concerns)** | 49 atoms across 9 matrices (Kahneman: 3, Archivist: 12, Causal Analyst: 1, Judge: 9, XAI Reporter: 1, TaskGuard: 8, Causal Abductive: 3, TaskXAI: 6, Epistemic Humility: 6) and 60+ atoms with screaming imperatives in ontology | `tda_3a362e01de66444c813e5b79adec27bf`: `extraction_rule: ""` with `concept_description: "the conclusion is presented without a multi-step logical deduction."`<br>`tda_eb8a7a13bbe54bcca5474cc8219229e2`: `extraction_rule: ""` with `concept_description: "CRITICAL DIRECTIVE: EXTRACT evidence where a required standard operating procedure is explicitly bypassed."` | Enforce strict Separation of Concerns: 1) `concept_description` = Pure ontological description (what the concept means), 2) `extraction_rule` = Operational IF/THEN heuristic steps (how to locate and verify). Populate all 49 empty rules and strip screaming imperatives (`CRITICAL DIRECTIVE: LOCATE...`, `IDENTIFY...`, `Scan...`) from ontology descriptions. |
| **6. User-Prompt Hardcoding & Modality Coupling (Split Modality)** | 44 atoms across 8 matrices (Judge: 14, Goodhart: 10, Falsifier: 10, Causal Analyst: 4, Causal Abductive: 3, TaskGuard: 1, TaskXAI: 1, Epistemic Humility: 1) | `tda_282059a3bea94b6c94e5f290a9cb75a7`: `"Scan ONLY the user prompts. the user accepts the AI output..."`<br>`tda_85ef05fdcd2f48afb925fd03b6c54d4d`: `"the user asks the AI to act as an infallible oracle..."`<br>`tda_236ebf69629e41a58b0f13eb82b44875`: `"EXTRACTION CONDITION: role prefixes (user: ai:) exist..."`<br>`tda_92680081ffb244d8abbdc99120a3291f`: `"Reject matches from user inputs or prefixes."` | Re-architect sensors to be 100% modality-invariant per Tripartite Pipeline Architecture (`ki_tripartite_pipeline_architecture.md`). Map terms to universal epistemic anchors (`the author`, `the practitioner`, `the evaluated context`, `external propositions`, `secondary claims`). Relegate all recipient coaching, dialogue contextualization, and conversational tone strictly to Phase 2 Synthesis (`OutputProfile`). |
| **7. Ambiguous Wordings in Prompt Directives** | 1 prompt file (`matrix_evaluation.py`) | `(specifically: repeating 'merely', 'only', 'just', 'simply')` | Replace open-ended lists with explicit closed lists to satisfy `anti_ambiguity_mandate`. |
| **8. Multi-Collection Prompt & Input Mapping Verification Debt** | `steps`, `workflows`, `output_profiles` in `seed_data.json` | Unverified `input_mappings` variable paths, uninspected `expected_inputs[].ai_description` fields, unlinted `output_profiles` synthesis directives. | Expand `scripts/audit_database_atoms.py` into a unified 4-collection database prompt audit engine validating referential integrity and prompt cleanliness across all entities. |

---

## Target Scope & Files

### TARGET Files
- **[MODIFY]** `@[backend_v2/models/prompts/matrix_evaluation.py]`
- **[MODIFY]** `@[backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py]`
- **[NEW]** `@[scripts/audit_database_atoms.py]`
- **[NEW]** `@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]`
- **[MODIFY]** `@[backend_v2/seed/seed_data.json#L312-L6500]` (via deterministic migration script in `scratch/`)

### CONTEXT Files (Read-Only SSOT)
- `@[.agents/rules/00-antigravity-core.md]`
- `@[.agents/rules/01-python-backend.md]`
- `@[.agents/rules/03_seed_vault.md]`
- `@[.agents/rules/05_llm_architecture.md]`
- `@[backend_v2/models/v2_core.py#L153-L257]` (TDAAssertion class)
- `@[backend_v2/seed/seed_registry.py]` (STANDARD_REGISTRY with TypeAdapter)
- `@[backend_v2/models/domain/prompt_blocks.py]` (AnyPromptBlock discriminated union)
- `@[docs/implementationplans/IMPLEMENTATION_PLAN_Zero_Variance_Engine_Hardening.md]`
- `@[scratch/diff_report_2026-08-28_0405.md]`
- `@[scratch/diff_report_2026-08-28_0501.md]`
- `@[scripts/diff_executions.py#L272-L778]`
- `@[scripts/run_e2e_variance_test.py#L368-L499]`

---

## Empiirinen Varianssianalyysi & Diff-Raporttien Vertailu (Empirical Variance Analysis)

Kahden peräkkäisen 2-ajon tilastollisen varianssitestin tulokset osoittavat kognitiivisen episteemisen kynnyksen ja puhtaiden atomien välttämättömyyden:
- **1. Mittaus (04:05, ennen moottorikovennusta):** `@[scratch/diff_report_2026-08-28_0405.md]` (`exe_8376ad276c6243d38e78bfda314933cd` vs. `exe_5cdbb10c98c540caab5b6cbd84fca61d`).
- **2. Mittaus (05:01, moottorikovennuksen jälkeen):** `@[scratch/diff_report_2026-08-28_0501.md]` (`exe_c68c03e0a28e4486b3d2489ae155e887` vs. `exe_e4470f64e5194d0699a0653b5a20eeff`).

### Metriikoiden ja Erotilojen Vertailutaulukko

| Metriikka / Ominaisuus | 1. Mittaus (`diff_report_0405.md`) | 2. Mittaus (`diff_report_0501.md`) | Eron Analyysi & Havainto |
| :--- | :--- | :--- | :--- |
| **Yhteiset Arvioidut Atomit ($N$)** | 152 atomia (13 matriisia) | 152 atomia (13 matriisia) | 100 % kattavuus kummassakin ajossa ilman yhtäkään DLQ-pudotusta tai kaatumista. |
| **Itse-konsistenssi (Self-Consistency)** | **91.45 %** (13 erimielisyyttä) | **87.50 %** (19 erimielisyyttä) | Konsistenssi heikkeni 3.95 prosenttiyksikköä, kun syötteiden luentaa tiukennettiin ilman epistämisen kynnyksen lukitsemista. |
| **Fleissin Kappa ($\kappa_{Fleiss}$)** | **0.8273** (Lähes täydellinen) | **0.7343** (Huomattava) | $\kappa$-arvon merkittävä lasku osoittaa satunnaisuuden kasvaneen mallin tulkinnoissa. |
| **Cohenin Kappa ($\kappa_{Cohen}$)** | **0.8275** | **0.7352** | $\kappa_{Cohen} \approx \kappa_{Fleiss}$ osoittaa, ettei kyseessä ole systemaattinen kalibrointiharha vaan stokastinen epävarmuus. |
| **Shannonin Entropia (Epävarmuus)** | **0.0855** | **0.1250** | Entropian 46.2 % kasvu todistaa arviointikriteerien tulkinnanvaraisuuden lisääntyneen. |
| **Contextual Override -erimielisyydet** | **13 / 13 (100 %)** | **19 / 19 (100 %)** | **100 % kaikista varianssitapauksista** johtuu semanttisesta ohitustulkinnasta (`allow_contextual_override = true`). |
| **Siirtymäsuunnat (R1 $\rightarrow$ R2)** | 4 PASSED $\rightarrow$ FAILED / 9 FAILED $\rightarrow$ PASSED | 14 PASSED $\rightarrow$ FAILED / 5 FAILED $\rightarrow$ PASSED | Käänteisten väitteiden (`is_inverse: true`) epävakaa tulkinta vaihtelee voimakkaasti ajojen välillä. |

### Syy-seurausanalyysi: Miksi tietokannan auditointimoottori ja järjestelmäkehote ovat välttämättömiä?

1. **Semanttinen Kaksoissidos (Double-Bind) & Käänteisväitteiden Varianssi:**
   100 % havaituista erimielisyyksistä kohdistuu atomeihin, joissa sovelletaan semanttista ohitusta. Käänteisväitteissä (`is_inverse: true`, esim. Toulmin ja Kausaalimatriisit) malli tulkitsee toisessa ajossa kirjoittajan passiivisen varauksen virheen myöntämiseksi (FAILED), kun taas toisessa ajossa se katsoo saman kohdan osoittavan episteemistä nöyryyttä (PASSED).
2. **Saastuneet Etsintäsäännöt ja Split-Brain -tila:**
   Raporteissa eniten heittelevät atomit (`tda_6e904f7c369a410ab9988e49ca3213e0`, `tda_1361cf5ec5b5420c905cd2a1f80893a7`, `tda_fba3218b2c5443d89ad105d945f71255`, `tda_d95b263f55504cc38901001296374825`) sisältävät tyhjiä sääntöjä, "Do not evaluate" -kieltoja, "FAIL FAST" -komentoja tai sekoittuneita XML-ohjeita.
3. **Ratkaisun Vaikuttavuus:**
   Lisäämällä staattinen `<epistemic_decision_protocol>` järjestelmäkehotteeseen ja puhdistamalla kaikki 13 matriisia automatisoidun `audit_database_atoms.py` -moottorin kautta poistetaan tulkinnanvaraisuus ja palautetaan $\kappa$-arvo sekä konsistenssi pysyvästi yli 95 % tasolle.

---

## 5-Column Architectural Directives

| 1. Kohdealue & Skoopit (Target Scope) | 2. 🚫 KIELLETTY PURKKA (Eradicated Duct-Tape) | 3. 🎯 TEE NÄIN (Approved Best Practice) | 4. ✂️ KARSITTU YLISUUNNITTELU (Pruned Over-Engineering) | 5. 🔒 VERIFIOINTI & FAIL-FAST (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`seed_data.json` Sanitointimenetelmä (13 matriisia, 152 atomia sekä Persona-, Synteesi-, Workflow- ja Step-lohkot)**<br>`@[backend_v2/seed/seed_data.json#L312-L6500]` | Massiivisen 8 499 rivin JSON-tiedoston paloittelu ja sokea korvaaminen tekstinä `multi_replace_file_content` -työkalulla (altis aaltosulkeiden/pilkkujen hukkumiselle ja LLM-kontekstin leikkaantumiselle). Kertakäyttöiset inline-komentosarjat (`python -c`, `sed`). Tyhjät arviointisäännöt (`extraction_rule: ""`), meta-ohjeet (`BANNED SOURCES`), pseudokoodi (`STEP 1: ...`), huutavat komennot (`FAIL FAST`, `CRITICAL DIRECTIVE: LOCATE`), kielto-ohjeet (`Do not judge`), raaka XML (`<ambiguity_protocol>`, `<role_enforcement>`, `<global_framework>`, `<section_rules>`), sekä chatbot-kovakoodaus (`Scan ONLY user prompts`, `Reject AI outputs`, `role prefixes (user: ai:) exist`, `located in an block`). | Suoritetaan sanitointi deterministisellä Python-migraatioskriptillä (`scratch/sanitize_seed_atoms.py`), joka lataa JSON-puun muistiin, päivittää kaikki 152 atomia eksplisiittisestä suljetusta sanakirjakartasta (Ontologia vs. Heuristiikka, tyhjien sääntöjen täyttö, chatbot-viitteiden yleistys, XML-stripit), validoi `steps`-, `workflows`- ja `output_profiles`-kenttien eheydet, validoi jokaisen entiteetin `seed_registry.py`:n `STANDARD_REGISTRY`-malleilla ja tallentaa UTF-8 -muodossa. | Ei luoda dynaamista tietokanta-ajonaikaista välikerrosta, monimutkaista ORM-migraatiokehystä tai rinnakkaisia "chatti-" ja "dokumenttimatriiseja"; yksinkertainen muistissa tapahtuva JSON-käsittely `scratch/`-kansiossa riittää. | `backend_v2/seed/backups/` varmuuskopiointi ennen ajoa, Pydantic V2 `validate_python()` jokaiselle entiteetille, `json.load()`-syntaksitarkastus heti tallennuksen jälkeen, sekä `uv run python scripts/audit_database_atoms.py --strict` (0 virhettä kaikissa 4 kokoelmassa). |
| **Synteesikerros & Output Profiles**<br>`@[backend_v2/models/prompts/synthesis_directives.py]` & `output_profiles` | Oletus, että sensoriatomin (Phase 1) pitää osata puhutella käyttäjää tai valmentaa häntä suoraan. Raaka XML `output_profiles`-synteesiohjeissa. | Synteesikerros ottaa vastaan puhtaan `StepOutputDTO`-tuloksen ja personoi palautteen (`"Sinä johtajana..."`, `"Analysoidussa aineistossa..."`) vastaanottajalle `OutputProfile`-konfiguraation mukaisesti. Puhdas deklaratiivinen teksti synteesiohjeissa. | Ei generoida uutta arviointidataa synteesissä; vain olemassa olevan datan kielellinen ja pedagoginen paketointi. | Unit-testit `test_synthesis_distiller.py`, `audit_database_atoms.py` ja snapshot-testit generoivat kohdennetun valmennusraportin ilman sensoritason saastumista. |
| **Workflow Input Routing & Step Governance**<br>`workflows` & `steps` kokoelmat | Virheelliset tai olemattomiin syötekenttiin viittaavat `$inputs.x` -polut `input_mappings`-määrityksissä; puuttuvat `model_strategy`-määritykset; orvot lohkoviitteet (`role_block_id`, `extraction_protocol_block_id`). | `audit_database_atoms.py` tarkastaa, että jokainen `steps[].input_mappings` viittaa olemassa olevaan `expected_inputs`-avaimeen tai upstream-steppiin, ja että kaikki lohkoviitteet ratkeavat `prompt_blocks`-kokoelmaan. | Ei monimutkaisia ajonaikaisia heittoliitäntöjä; staattinen verifiointi takaa syöteputken determinismin. | `audit_database_atoms.py --strict` verifioi `workflows` ja `steps` referentiaalisen eheyden. |
| **`matrix_evaluation.py` (`MATRIX_SENSOR_SYSTEM_PROMPT`)**<br>`@[backend_v2/models/prompts/matrix_evaluation.py]` | Epäselvä arviointiohje ilman episteemistä kynnystä ja käänteisen todistusaineiston käsittelyä. Avointen esimerkkilistojen käyttö kehotteessa. | Injektoidaan staattinen `<epistemic_decision_protocol>` XML-osio: positiivisille väitteille vaaditaan eksplisiittinen rakenteellinen/empiirinen tuki; käänteisille väitteille (`is_inverse: true`) virhe katsotaan läsnä olevaksi vain, jos se on aktiivinen ja korjaamaton. Korvataan epämääräiset esimerkit täsmällisillä suljetuilla säännöillä. | Ei luoda dynaamisia ehtoja tai runtime-muokkauksia; pidetään kehote 100 % staattisena Context Caching -yhteensopivana. | `uv run pytest backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py` |
| **`scripts/audit_database_atoms.py`** (Täyden tietokannan tarkastusmoottori)<br>`[NEW] @[scripts/audit_database_atoms.py]` | Manuaalinen tai pistokoeluontoinen JSON-tarkistus; `grep_search` CRLF-tiedostoihin ilman rivirajoja; vain atomeihin rajoittuva suppea tarkastus; salliva linttaus, joka ohittaa XML-merkit, tyhjät säännöt tai chat-spesifit kovakoodaukset; reflection-kutsujen (`getattr`, `hasattr`) käyttö. | Luodaan deterministinen Pydantic V2 -pohjainen tarkastusmoottori, joka tarkastaa kaikki 4 prompt-kokoelmaa (`prompt_blocks`, `steps`, `workflows`, `output_profiles`): 1) Kielletyt haamutekstit (`BANNED SOURCES`, `EXTRACTION CONDITION:`, `FAIL FAST`, `Do not evaluate...`, `DEPRECATED`), 2) Rikkinäiset tokenit ja chat-kovakoodaukset (`in an block`, `Scan ONLY user prompts`, `Scan ONLY`, `role prefixes`, `user prompt`, `user inputs`, `AI output`), 3) Raaka XML kaikissa datakentissä (`if "<" in val and ">" in val`), 4) Tyhjät säännöt (`extraction_rule` ja `concept_description` min_length >= 10 pakollinen kaikille 152 atomille), 5) Referentiaalinen eheys ja syöterouttaus (`input_mappings` -> `expected_inputs`, lohkoviitteet). Täysi Zero Reflection -noudattaminen. | Ei rakenneta tietokantayhteyksiä tai raskaita riippuvuuksia; luetaan suoraan `seed_data.json` Pydantic-validoituna DTO-rakenteena. | `uv run python scripts/audit_database_atoms.py --strict` palauttaa exit code 0 puhtaalla datalla ja exit code 1 virheillä; `uv run pytest backend_v2/tests/unit/scripts/test_audit_database_atoms.py` todistaa kaikki ISTQB-partitiot. |

---

```xml
<execution_protocol>
  <phase id="1" name="PRE-IMPLEMENTATION CLEANUPS &amp; PROMPT PROTOCOL HARDENING">
    <step id="1.1" name="Inject epistemic decision protocol into MATRIX_SENSOR_SYSTEM_PROMPT">
      <target>@[backend_v2/models/prompts/matrix_evaluation.py]</target>
      <action>
        Update `MATRIX_SENSOR_SYSTEM_PROMPT` to include `<epistemic_decision_protocol>` and eliminate ambiguous examples:
        ```python
        MATRIX_SENSOR_SYSTEM_PROMPT = (
            "<evaluation_directives>\n"
            "- CRITICAL EVALUATION DIRECTIVE: Evaluate if the claims in the dynamic parameters are true based strictly on the provided context.\n"
            "- Match each evaluation strictly to its claim's alias (specifically: `a0`, `a1`, `a2`).\n"
            "</evaluation_directives>\n"
            "<epistemic_decision_protocol>\n"
            "- POSITIVE CLAIMS (Standard Evidence): Evaluate whether the required analytical, empirical, or methodological structure is explicitly substantiated in the context.\n"
            "- INVERSE / NEGATIVE CLAIMS (Inverse Evidence): An error, fallacy, or structural weakness is considered present (is_true = true) ONLY if it is actively committed and unhedged. If the author acknowledges constraints, provides counter-evidence, or expresses appropriate epistemic humility, the negative claim is not substantiated (is_true = false).\n"
            "</epistemic_decision_protocol>\n"
            "<reasoning_constraints>\n"
            "- CONCISE CHAIN-OF-THOUGHT: Provide concise, high-density reasoning (maximum 2-3 sentences per claim).\n"
            "- Do NOT output stream-of-consciousness, verbose explanations, or ungrounded speculation.\n"
            "</reasoning_constraints>\n"
            "<anti_repetition_mandate>\n"
            "- CRITICAL ANTI-REPETITION MANDATE: NEVER enter repetitive token loops, keyword chanting, or repeating anchor terms.\n"
            "- State your concise analytical deduction once directly and conclude immediately.\n"
            "</anti_repetition_mandate>\n"
            "<output_mandate>\n"
            "- Complete all required schema fields (`alias`, `reasoning`, `is_true`) for every single requested claim.\n"
            "</output_mandate>"
        )
        ```
        Key changes:
        1. Added `<epistemic_decision_protocol>` section with symmetric positive/inverse burden of proof.
        2. Replaced ambiguous open-ended alias example on L6 with closed list `(specifically: a0, a1, a2)`.
        3. Removed open-ended repetition word enumeration on L13 — anchor terms are self-evident from context.
      </action>
      <constraint invariant="prompt_asset_ssot_mandate">Keep system prompt 100% static to maximize context caching.</constraint>
      <constraint invariant="ephemeral_caching_topology">Zero dynamic variables in system prompt.</constraint>
    </step>

    <step id="1.2" name="Update and expand unit tests with ISTQB negative partitions">
      <target>@[backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py]</target>
      <action>
        Update and expand `test_matrix_evaluation.py` to cover:
        1. Positive Partition: Assert presence and proper closure of `<evaluation_directives>`, `<epistemic_decision_protocol>`, `<reasoning_constraints>`, `<anti_repetition_mandate>`, and `<output_mandate>`.
        2. Negative Partition 1: Assert absence of banned ambiguous expressions (specifically and exhaustively: `"e.g."`, `"etc."`, `"such as"`, and `"l]ike "` (with trailing space, bracket removed in actual test)).
        3. Negative Partition 2: Assert absence of forbidden open-ended repetition word lists containing parenthesized examples.
        4. Negative Partition 3: Assert absence of unclosed XML tags or mismatched tags via regex `<([a-z_]+)>` vs `</\1>` matching.
      </action>
      <constraint invariant="anti_happy_path_mandate">Ensure test suite includes both positive assertions and negative partition guards under `backend_audit_loop.py`.</constraint>
    </step>
  </phase>

  <phase id="2" name="AUTOMATED FULL DATABASE PROMPT VERIFICATION ENGINE &amp; TEST SUITE">
    <step id="2.1" name="Build scripts/audit_database_atoms.py with 4-Collection Inspection Gates">
      <target>[NEW] @[scripts/audit_database_atoms.py]</target>
      <action>
        Create `scripts/audit_database_atoms.py` with strict Pydantic V2 DTOs and zero-reflection multi-collection audit visitor:
        1. DTO Definitions:
           - `AuditIssue`: `(collection: str, entity_id: str, field_path: str, issue_type: str, message: str, severity: str)` with `ConfigDict(strict=True, extra="forbid", frozen=True)`.
           - `FullDatabaseAuditReport`: `(total_matrices: int, total_atoms: int, total_steps: int, total_workflows: int, total_profiles: int, issues: list[AuditIssue], all_passed: bool)` with `ConfigDict(strict=True, extra="forbid", frozen=True)`.
        2. **Gate 1: `prompt_blocks` Inspection:**
           - Traverses 13 matrices at `scales[].claims[].tda_assertions[]` (152 total atoms):
             - Forbid `DEPRECATED` in `concept_description` or `extraction_rule`.
             - Forbid negative guidance phrases (`Do not evaluate`, `Do not judge`, `Do not accept`, `Do not flag`) in `concept_description`.
             - Forbid prompt injection / pipeline artifacts (`BANNED SOURCES`, `EXTRACTION CONDITION:`, `role prefixes`, `FAIL FAST`, `STEP 1:`, `STEP 2:`).
             - Forbid chatbot-specific hardcodings &amp; modality coupling (`Scan ONLY user prompts`, `Scan ONLY`, `role prefixes (user: ai:)`, `user prompt`, `user inputs`, `AI output`, `Reject AI outputs`).
             - Forbid raw XML tags and delimiters (`<...>`, `<`, `>`) in unrendered atom fields (`concept_description`, `extraction_rule`).
             - Forbid corrupted grammar tokens and truncated fragments (specifically: `in an block`).
             - Mandate `min_length >= 10` for both `concept_description` and `extraction_rule` across all 152 atoms.
             - Forbid screaming imperatives in ontology descriptions (`CRITICAL DIRECTIVE`, `IDENTIFY`, `LOCATE`, `Scan the document.`, `Verify`, `CHECK`).
           - Traverses non-matrix blocks (`PersonaPromptBlock`, `ProtocolPromptBlock`, `SystemRulePromptBlock`, `TaskDefinitionPromptBlock`):
             - Forbid raw XML in `ai_description`, `role_enforcement`, `protocol_instructions`, and `instruction_text`.
        3. **Gate 2: `steps` Inspection:**
           - Validates each Step: `type == "llm"` must have non-empty `model_strategy`, `criteria_block_ids`, and `extraction_protocol_block_id`.
           - Referential Integrity: asserts that all referenced `role_block_id`, `extraction_protocol_block_id`, `execution_persona_block_id`, and `criteria_block_ids` exist in `prompt_blocks`.
           - Validates `expected_inputs` keys formatting.
        4. **Gate 3: `workflows` Inspection:**
           - Validates `Workflow.expected_inputs`: `ai_description` formatting, forbidden raw XML.
           - Validates `Workflow.steps[].input_mappings`: Each value must follow `$inputs.<key>` or `$steps.<step_id>.<key>`, and all referenced `$inputs.<key>` must exist in `workflow.expected_inputs`.
           - Validates `Workflow.system_prompt` (if present, forbid raw XML).
        5. **Gate 4: `output_profiles` Inspection:**
           - Validates `synthesis_config.system_prompt` (if present, forbid raw XML).
           - Validates `matrix_synthesis_groups[].synthesis_directive` (if present, forbid raw XML) and verifies `target_blocks` exist in `prompt_blocks`.
        6. Zero reflection: forbid `getattr`/`hasattr`. Access attributes directly via typed Pydantic models.
        7. CLI interface with `--strict` flag exiting with code 1 on violations and code 0 on clean pass.
      </action>
      <constraint invariant="ast_guardrail_mandate">Enforce standard CLI interface with `--strict` flag exiting with non-zero on violations.</constraint>
      <constraint invariant="pep257_google_style_docstrings">All functions and classes must have PEP 257 Google-style docstrings.</constraint>
    </step>

    <step id="2.2" name="Build comprehensive unit test suite in test_audit_database_atoms.py">
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]</target>
      <action>
        Create unit tests in `test_audit_database_atoms.py` validating all 4 collection inspection gates and ISTQB partitions:
        1. `test_audit_dto_structure`: Validates Pydantic V2 DTO creation, immutability, and serialization.
        2. `test_audit_clean_pass`: Proves valid seed data produces 0 findings and exit code 0.
        3. `test_audit_atoms_banned_phrases`: Proves detection of `BANNED SOURCES`, `FAIL FAST`, `EXTRACTION CONDITION`, `DEPRECATED`.
        4. `test_audit_atoms_negative_guidance`: Proves detection of `Do not evaluate`, `Do not judge`, `Do not accept`.
        5. `test_audit_atoms_chat_hardcoding`: Proves detection of `Scan ONLY user prompts`, `role prefixes`, `located in an block`.
        6. `test_audit_atoms_raw_xml`: Proves detection of raw XML tags and angle brackets in concept descriptions, extraction rules, and block ai_descriptions.
        7. `test_audit_atoms_empty_rules`: Proves detection of empty or short extraction rules (`min_length < 10`).
        8. `test_audit_atoms_screaming_imperatives`: Proves detection of screaming imperatives in ontology descriptions (`CRITICAL DIRECTIVE`, `LOCATE`, `IDENTIFY`).
        9. `test_audit_steps_referential_integrity`: Proves detection of orphan `role_block_id`, `extraction_protocol_block_id`, or `criteria_block_ids`.
        10. `test_audit_workflows_input_mappings`: Proves detection of invalid `$inputs.unknown_key` or malformed mapping paths.
        11. `test_audit_output_profiles_directives`: Proves detection of raw XML in synthesis directives or orphan target block references.
        12. `test_audit_cli_exit_codes`: Tests `--strict` CLI behavior with exit code 0 on clean and exit code 1 on violations via `subprocess.run`.
        13. `test_audit_zero_reflection`: Uses Python AST parser to mathematically verify zero `getattr`/`hasattr` calls exist in `scripts/audit_database_atoms.py`.
      </action>
      <constraint invariant="tdd_mandate">Ensure test suite achieves >90% coverage under `backend_audit_loop.py`.</constraint>
      <constraint invariant="anti_happy_path_mandate">Cover all collection inspection gates with dedicated negative test functions.</constraint>
    </step>

    <step id="2.3" name="Verify baseline failure before seed data sanitization">
      <action>
        Execute `uv run python scripts/audit_database_atoms.py --strict` to verify it correctly flags legacy defects across all collections.
      </action>
      <constraint invariant="tdd_mandate">Confirm the audit engine catches the legacy defects.</constraint>
    </step>
  </phase>

  <phase id="3" name="COMPLETE 4-COLLECTION SEED DATA SANITIZATION VIA DETERMINISTIC IN-MEMORY MIGRATION">
    <step id="3.1" name="Vault Backup &amp; Comprehensive Seed Sanitization (Deterministic In-Memory Migration Script)">
      <target>@[backend_v2/seed/seed_data.json#L312-L6500]</target>
      <action>
        1. Create timestamped vault backup:
           `New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_full_sanitization.json`
        2. In accordance with `03_seed_vault.md` (`temporary_workspace_sandbox`), `00-antigravity-core.md` (`temporary_workspace_sandbox`), and `04_directory_reference.md` (`ephemeral_storage_mandate`), write a deterministic in-memory Python migration script to `scratch/sanitize_seed_atoms.py`.
        3. The migration script executes the following bulletproof sequence:
           a. Loads `backend_v2/seed/seed_data.json` into memory as a UTF-8 JSON structure.
           b. Iterates through `prompt_blocks` (sanitizes 152 atoms across 13 matrices: populating 49 empty extraction rules, eliminating chatbot hardcoding, separating ontology vs heuristics, stripping raw XML from blocks and atoms).
           c. Iterates through `steps`, `workflows`, and `output_profiles` (validates referential integrity, cleans raw XML, ensures valid `input_mappings`).
           d. Validates every mutated block/entity through `backend_v2.seed.seed_registry.STANDARD_REGISTRY[collection]["model"].validate_python(entity)` to guarantee strict Pydantic V2 conformance before writing to disk.
           e. Safely dumps the sanitized JSON back to `backend_v2/seed/seed_data.json` with UTF-8 encoding and 2-space indentation.
           f. Immediately executes a dry-run `json.load()` validation on the saved file to verify syntax integrity.
        4. Execute the script via `uv run python scratch/sanitize_seed_atoms.py`.
      </action>
      <constraint invariant="prompt_preservation_mandate">Preserve user intellectual property while cleansing architectural corruptions. NEVER rewrite coaching philosophy or conceptual intent.</constraint>
      <constraint invariant="database_schema_hallucination">Do NOT alter root persistence array structures in seed_data.json.</constraint>
    </step>

    <step id="3.2" name="Execute Verification Engine on Sanitized Seed Vault">
      <action>
        Run: `uv run python scripts/audit_database_atoms.py --strict`
      </action>
      <constraint invariant="zero_tolerance_audit_loop">Verify 100% PASS with 0 flagged issues across all 4 collections (prompt_blocks, steps, workflows, output_profiles).</constraint>
    </step>

    <step id="3.3" name="Re-seed Database">
      <action>
        Run: `uv run python backend_v2/seed/run_seed.py local`
      </action>
      <constraint invariant="database_schema_hallucination">Ensure zero Pydantic validation errors during local database wipe and seed synchronization.</constraint>
    </step>
  </phase>

  <phase id="4" name="QUALITY GATES &amp; STATISTICAL E2E VARIANCE VALIDATION">
    <step id="4.1" name="Execute Backend Quality Gate">
      <action>
        Run: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
      </action>
      <constraint invariant="quality_gate_execution">Ensure 100% Ruff, MyPy, and Pytest passing with 0 warnings.</constraint>
    </step>

    <step id="4.2" name="Execute Live E2E Variance Test on Real PDF Data">
      <action>
        Run 2-run variance test:
        PowerShell: `$env:DEV_EXECUTION_MODE="full"; uv run python scripts/run_e2e_variance_test.py docs\jwdatat`
      </action>
      <constraint invariant="anti_hallucination_read">Verify generated diff report in `scratch/` demonstrates zero Boolean inversion crashes, zero data starvation, and improved statistical consistency (target: kappa > 0.85, self-consistency > 92%).</constraint>
    </step>
  </phase>
</execution_protocol>
```

---

## Verification Plan

### Automated Unit & Quality Gates
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/prompts/matrix_evaluation.py --test
uv run pytest backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py
uv run pytest backend_v2/tests/unit/scripts/test_audit_database_atoms.py
uv run python scripts/audit_database_atoms.py --strict
uv run python scripts/backend_audit_loop.py backend_v2 --test
```

### Database Seeding Gate
```powershell
uv run python backend_v2/seed/run_seed.py local
```

### Live E2E Variance Gate
```powershell
$env:DEV_EXECUTION_MODE="full"
uv run python scripts/run_e2e_variance_test.py docs\jwdatat
```

### Final E2E REST API Verification Gate
```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```
