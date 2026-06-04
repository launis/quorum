# EPIC 68: XAI Extension Scope Separation & Polymorphic Routing Hardening

> [!IMPORTANT]
> **EPIC 63 PREREQUISITE & CONSTRAINTS (Zero-Compromise Pledge)**:
> Tämä suunnitelma on täysin riippuvainen Epic 63:n luomasta arkkitehtuurista. Epic 63 teki järjestelmästä 100% MyPy-puhtaan ja kielsi löyhien sanakirjojen (dict) käytön testeissä ja reitityksessä. 
> Kun toteutat tätä Epiciä:
> 1. **Mallit**: `OutputProfile` ja `EmbeddedOutputProfile` perivät suoraan `V2CoreBase`:n, joten MyPy-ongelmia (kuten Epic 63:n `ExecutionRecord`:n periytymisbugi) ei pitäisi syntyä. Mutta muista PEP 695 (esim. `list[LaxXaiExtensionType] | None`).
> 2. **Rivinumerot**: Epic 63 lisäsi `v2_core.py` -tiedostoon `TYPE_CHECKING` -lohkoja, joten tässä asiakirjassa mainitut `v2_core.py`:n rivinumerot (esim. L942, L980) ovat siirtyneet alemmas.
> 3. **Testit**: Kaikki tässä mainitut testit (esim. `test_context_router.py`) täytyy refaktoroida käyttämään vahvasti tyypitettyjä Pydantic-malleja (esim. `OutputProfileConfig(visible_block_extensions=[...])`). Pydanticin mockaaminen löyhästi `MagicMock`:illa kaataa Universal Quality Gaten!

## 1. Background & Motivation
In the current Quorum architecture, both Block-level extensions (e.g., `falsification`, `emotional_sentiment`) and Workflow-level global extensions (e.g., `variance_validation`) are compressed into a single data model field: `OutputProfileConfig.visible_extensions`.

This "Domain Model Collision" forced the `ContextRouter` (which should act strictly as a dumb data extraction layer) to implement hardcoded "Leaky Abstractions":
```python
if ext_str == XaiExtensionType.VARIANCE_VALIDATION.value:
    continue
```
This violates the Open/Closed Principle (SOLID). Adding new global metrics in the future would require manually modifying the routing logic. This Epic aims to pay off this technical debt by restructuring the data model to natively separate these concerns.

> [!CAUTION]
> **KOVAKOODAUKSEN TODELLINEN LAAJUUS (Agentille Kriittinen Ohje)**:
> `variance_validation` -kovakoodaus ei rajoitu pelkästään `context_router.py`:hyn. Alla kaikki kovakoodauspisteet:
>
> | # | Tiedosto | Rivi | Kovakoodaus |
> |---|---|---|---|
> | 1 | `services/orchestrator/context_router.py` | L95-99 | `if ext_str == "variance_validation"` routing bypass |
> | 2 | `services/blueprint.py` | L287-291 | `if ext.get("extension_type") == "variance_validation"` report context extraction |
> | 3 | `services/blueprint.py` | L294-324 | Koko `variance_validation` dynamic VarianceEngine calculation block (~30 riviä) |
> | 4 | `services/blueprint.py` | L589-590 | `if ext_key == "variance_validation": continue` sort/limit bypass |
> | 5 | `hooks/synthesis.py` | L616 | `active_exts = active_profile_dto.visible_extensions` — lähettää KAIKKI extensionit LLM:lle ilman scope-erottelua |
> | 6 | `hooks/synthesis.py` | L745-756 | XAI highlights fail-fast validoi `visible_extensions` kokonaisuutena, mukaan lukien workflow-tason extensiot |
>
> Kaikki kuusi pistettä on refaktoroitava. Pelkän `context_router.py`:n korjaaminen jättää 4 kovakoodauspistettä eloon.

## 2. Architectural Objectives
1. **SOLID Compliance:** Ensure `ContextRouter` is open for extension but closed for modification.
2. **Domain Segregation:** Split extensions into `visible_block_extensions` (handled by ContextRouter & SynthesisHook) and `visible_workflow_extensions` (handled by the Orchestrator/VarianceEngine in BlueprintTransformer).
3. **Enum Scope Classification:** Introduce a scope classification mechanism for `XaiExtensionType` so future extensions are automatically routed without modifying routing logic.
4. **Context-Aware UI Filtering (Poka-yoke):** Ensure the UI only allows selecting block extensions that the underlying Workflow's target matrices are explicitly configured to produce.
5. **Fail-Fast Safety:** All `seed_data.json` structures updated to new schema, clean-slate seeder re-run.

## 3. Implementation Phases

### Phase 1: Enum Scope Classification & Domain Model Refactoring (Backend)
- **Files Affected:**
  - `backend_v2/models/enums.py`
  - `backend_v2/models/dtos/output_profile.py`
  - `backend_v2/models/dtos/lightweight_matrix.py`
  - `backend_v2/models/v2_core.py` (OutputProfile, EmbeddedOutputProfile)
  - `backend_v2/api/routers/system/workflow.py`
- **Actions:**

  #### 1.1. Enum Scope Classification (`enums.py`)
  Introduce a scope mapping to classify extension types without breaking existing code:
  ```python
  class XaiExtensionScope(str, Enum):
      """Scope classification for XAI extensions.

      Attributes:
          BLOCK: Produced per-matrix by LLM strategies.
          WORKFLOW: Computed globally by mathematical engines.
      """
      # R55: PEP 257 Google-style docstring with Attributes ^

      BLOCK = "block"
      WORKFLOW = "workflow"

  # R47: zero_db_hardcoding_mandate — tämä dict korvaa kaikki
  #      kovakoodatut 'if ext == "variance_validation"' tarkistukset.
  # Runtime O(1) lookup — the SSOT for scope routing
  XAI_EXTENSION_SCOPE: dict[XaiExtensionType, XaiExtensionScope] = {
      XaiExtensionType.CITATION: XaiExtensionScope.BLOCK,
      XaiExtensionType.JUSTIFICATION: XaiExtensionScope.BLOCK,
      XaiExtensionType.FALSIFICATION: XaiExtensionScope.BLOCK,
      XaiExtensionType.THEORY_LINK: XaiExtensionScope.BLOCK,
      XaiExtensionType.RISK_FLAG: XaiExtensionScope.BLOCK,
      XaiExtensionType.COACHING: XaiExtensionScope.BLOCK,
      XaiExtensionType.MISSING_CONTEXT: XaiExtensionScope.BLOCK,
      XaiExtensionType.REMEDIATION_STEPS: XaiExtensionScope.BLOCK,
      XaiExtensionType.EMOTIONAL_SENTIMENT: XaiExtensionScope.BLOCK,
      XaiExtensionType.CONFIDENCE: XaiExtensionScope.BLOCK,
      XaiExtensionType.SOURCE_ID: XaiExtensionScope.BLOCK,
      XaiExtensionType.CONTEXTUAL_OVERRIDE: XaiExtensionScope.BLOCK,
      XaiExtensionType.VARIANCE_VALIDATION: XaiExtensionScope.WORKFLOW,
  }
  ```

  #### 1.2. Domain Model Split (Kaikki OutputProfile-mallit)

  > [!WARNING]
  > **Agentille Kriittinen Ohje**: `visible_extensions`-kenttä esiintyy **viidessä** eri mallissa:
  > 1. `OutputProfileCreateDTO` (`models/dtos/output_profile.py` L38)
  > 2. `OutputProfileUpdateDTO` (`models/dtos/output_profile.py` L74)
  > 3. `OutputProfileResponseDTO` (`models/dtos/output_profile.py` L109)
  > 4. `OutputProfile` (`models/v2_core.py` L942)
  > 5. `EmbeddedOutputProfile` (`models/v2_core.py` L980)
  > 6. `OutputProfileConfig` (`models/dtos/lightweight_matrix.py` L15) ← **KRIITTINEN, ContextRouter käyttää tätä**
  >
  > Kaikissa kuudessa `visible_extensions` korvataan kahdella kentällä:
  > ```python
  > visible_block_extensions: list[LaxXaiExtensionType] = Field(
  >     default_factory=list,
  >     description="Block-level XAI extensions (per-matrix, LLM-produced).",
  > )
  > visible_workflow_extensions: list[LaxXaiExtensionType] = Field(
  >     default_factory=list,
  >     description="Workflow-level global extensions (mathematical engines).",
  > )
  > ```

  #### 1.3. Available Extensions Endpoint
  - Create backend computation logic (e.g., in `WorkflowService`) that calculates the union of all `output_extensions` defined across all Target Matrices within a specific DAG.
  - Expose this via a new endpoint (e.g. `/api/v2/workflows/{id}/available-extensions`) or append it to the existing Workflow DTO to serve the Frontend.
  - Ensure strict Pydantic V2 schemas are maintained without autonomous `extra="allow"` enforcement.

### Phase 2: Orchestration, Routing & Synthesis Cleanup
- **Files Affected:**
  - `backend_v2/services/orchestrator/context_router.py`
  - `backend_v2/services/blueprint.py`
  - `backend_v2/hooks/synthesis.py`
  - `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- **Actions:**

  #### 2.1. ContextRouter Cleanup (`context_router.py`)
  - Remove the `variance_validation` bypass at L95-99.
  - Refactor `route_and_prune()` to read `output_profile.visible_block_extensions` instead of `output_profile.visible_extensions`.
  - The router becomes scope-blind: it iterates over whatever list it receives.

  #### 2.2. BlueprintTransformer Cleanup (`blueprint.py`)
  Four hardcoding sites to refactor:

  > [!WARNING]
  > **Agentille eksplisiittinen korvauskartta:**
  >
  > | Rivi | Nykyinen kovakoodaus | Korvaava logiikka |
  > |---|---|---|
  > | L201 | `visible_extensions = [v.value for v in ...]` | Jaetaan: `block_exts` luetaan `visible_block_extensions`:sta, `workflow_exts` luetaan `visible_workflow_extensions`:sta |
  > | L287-291 | `if ext.get("extension_type") == "variance_validation"` | Korvataan: `if ext.get("extension_type") in workflow_ext_values` (workflow_ext_values tulee `visible_workflow_extensions`:sta) |
  > | L294-324 | Koko `variance_validation` VarianceEngine block | Refaktoroidaan: iterointi `visible_workflow_extensions`:n yli, VarianceEngine-kutsut ajetaan jokaiselle workflow-tason extensiolle |
  > | L589-590 | `if ext_key == "variance_validation": continue` | Korvataan: `if ext_key in workflow_ext_values: continue` |

  #### 2.3. Synthesis Hook Scope Fix (`synthesis.py`)
  Two scope leaks to fix:

  - **L616**: `active_exts = active_profile_dto.visible_extensions` → muutetaan lukemaan **vain** `visible_block_extensions`. Workflow-tason extensiot (kuten `variance_validation`) ovat matemaattisia laskentoja — LLM:n ei tule "harvestoida" niitä.
  - **L745-756**: XAI highlights fail-fast validointi. Tarkistuksen on koskettava **vain** `visible_block_extensions` -listaa, koska workflow-tason extensioilla ei ole LLM-tuotettuja highlighteja.
  - **L634-637**: `<target_extensions_to_harvest>` XML-direktiiviin lähetetään vain `visible_block_extensions`.

### Phase 3: Seed Data Update & Clean-Slate Reset
- **Files Affected:** `backend_v2/seed/seed_data.json`
- **Strategy:** Clean-Slate — vanhoja ajoja ei tarvitse säästää. Ei migraatioskriptiä.
- **Actions:**
  - Päivitä `seed_data.json` suoraan uuteen skeemaan. Kaksi esiintymää:
    1. **L7184-7190** (kokonaisvaltainen_auditointi / embedded profile):
       ```json
       // ENNEN:
       "visible_extensions": ["falsification", "coaching", "remediation_steps", "emotional_sentiment", "variance_validation"]
       // JÄLKEEN:
       "visible_block_extensions": ["falsification", "coaching", "remediation_steps", "emotional_sentiment"],
       "visible_workflow_extensions": ["variance_validation"]
       ```
    2. **L8239-8245** (output_profiles-kokoelma):
       ```json
       // ENNEN:
       "visible_extensions": ["justification", "coaching", "falsification", "remediation_steps", "variance_validation"]
       // JÄLKEEN:
       "visible_block_extensions": ["justification", "coaching", "falsification", "remediation_steps"],
       "visible_workflow_extensions": ["variance_validation"]
       ```
  - Aja seeder clean-slate -moodissa:
    ```powershell
    uv run python backend_v2/seed/run_seed.py local
    ```

### Phase 4: Flutter Admin Studio Updates
- **Files Affected:** Admin Studio output profile editor -komponentit
- **Actions:**
  - Split the "XAI Extensions" multiselect into two distinct semantic UI blocks:
    - *Vaihekohtaiset laajennokset* (Block-level) — populated from `visible_block_extensions`
    - *Globaalit työnkulun laajennokset* (Workflow-level) — populated from `visible_workflow_extensions`
  - **Dynamic Dropdown Population:** The Block-level dropdown MUST be dynamically populated based on the selected `workflow_id`. If a workflow does not produce `emotional_sentiment`, it MUST NOT appear as a selectable option, physically preventing users from configuring unfulfillable demands.
  - The Workflow-level dropdown will remain populated by the statically supported global metrics from `XAI_EXTENSION_SCOPE` where scope is `WORKFLOW`.
  - Ensure Optimistic UI updates handle the new dual-array state payload.

### Phase 5: Test Updates & Quality Gates
- **Actions:**
  - Update all existing tests that reference `visible_extensions`:
    - `tests/unit/services/orchestrator/test_context_router.py` — update `OutputProfileConfig` instantiations
    - `tests/unit/models/dtos/test_output_profile.py` — update DTO validation tests
    - `tests/unit/models/dtos/test_lightweight_matrix.py` — update `OutputProfileConfig` tests
    - `tests/unit/services/test_blueprint.py` — update profile fixture data
    - `tests/integration/test_xai_reporter_integration.py` — update integration assertions
  - Add a new meta-test `test_xai_extension_scope_completeness` that verifies every `XaiExtensionType` enum member has an entry in `XAI_EXTENSION_SCOPE`.
  - Run full audit:
    ```powershell
    uv run python scripts/backend_audit_loop.py backend_v2/ --test
    ```
  - Aja `/tier2-hardening-backend` kaikille muutetuille tiedostoille `hardening.xml` -profiilia vasten. Muutetut tiedostot:
    - `models/enums.py`
    - `models/dtos/output_profile.py`
    - `models/dtos/lightweight_matrix.py`
    - `models/v2_core.py`
    - `services/orchestrator/context_router.py`
    - `services/blueprint.py`
    - `hooks/synthesis.py`

> [!IMPORTANT]
> **Hardening-compliance tarkistuslista (hardening.xml -säännöt)**:
> Agentti MUST varmistaa, että jokainen muutettu tiedosto noudattaa seuraavia sääntöjä:
>
> | Sääntö | ID | Vaatimus tässä Epicissä |
> |---|---|---|
> | R2 | `strict_pydantic_v2_rust` | `XaiExtensionScope` perii `(str, Enum)`, Output Profile DTO:t käyttävät `V2CoreBase`:n strictiä |
> | R18 | `rfc7807_dual_reporting_strict` | Uudet scope-validointivirheet → `AppException(error_code=ErrorCodes.XYZ)` |
> | R24 | `python_314_modern_syntax` | `X \| None`, ei `Optional[X]`. PEP 695 generics. |
> | R47 | `zero_db_hardcoding_mandate` | `XAI_EXTENSION_SCOPE` dict korvaa KAIKKI `if ext == "variance_validation"` -vertailut |
> | R55-59 | `pep257_google_style` | Kaikki uudet/muutetut luokat ja funktiot: Summary + Attributes/Args/Returns/Raises |
> | R82 | `data_parsing_preservation` | `blueprint.py`:n VarianceEngine-laskentalogiikka (L294-324) SÄILYTETÄÄN algoritmisesti — vain routing-logiikka muuttuu |
> | R83 | `preservation_of_inline_comments` | Kaikki `# ARCHITECTURE LOCK` ja `# Epic XX:` -kommentit säilytetään |
> | R88 | `architecture_lock_mandate` | `blueprint.py`:n `ARCHITECTURE LOCK` -merkityt lohkot eivät muutu — vain scope-routing niiden ympärillä |
>
> **R78/R85 tietoinen poikkeus**: Tässä Epicissä `visible_extensions`-kenttä nimetään uudelleen kahdeksi kentäksi (`visible_block_extensions`, `visible_workflow_extensions`). Tämä ON tietoinen, ihmisen hyväksymä arkkitehtuurimuutos — EI agentin autonominen päätös. Clean-slate seeder validoi lopputuloksen.

## 4. Zero-Compromise Pledges
- **Seed Integrity:** `seed_data.json` updated in-place. Clean-slate seeder run validates new schema.
- **Fail-Fast:** All changes validated via strict Pydantic parsing (`extra="forbid"`).
- **Anti-Hallucination:** Hardcoded extension strings in routing/synthesis layers strictly prohibited. All scope routing driven by `XAI_EXTENSION_SCOPE` dict (R47).
- **Scope Completeness:** Meta-test ensures every enum member has a scope classification.

## 5. Definition of Done (DoD)

1. **Zero Hardcoded Extension Strings**: No `if ext == "variance_validation"` or equivalent string comparisons exist in routing, blueprint, or synthesis layers. (R47 compliant)
2. **Dual-List Schema**: All six `OutputProfile` model variants use `visible_block_extensions` and `visible_workflow_extensions` instead of `visible_extensions`.
3. **Enum Scope SSOT**: `XAI_EXTENSION_SCOPE` dict maps every enum member to `BLOCK` or `WORKFLOW`. Meta-test enforces completeness.
4. **Synthesis Scope Isolation**: `text_consolidation_hook` sends only block-level extensions to LLM for harvesting.
5. **Clean Seed Data**: `seed_data.json` uses the new dual-list structure. Seeder runs clean.
6. **PEP 257 Compliance**: All new/modified classes, methods and functions have Google-style docstrings with Args/Returns/Raises. (R55-59 compliant)
7. **Hardening Gate Passed**:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/ --test
   ```
