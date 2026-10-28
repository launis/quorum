# Backlog: AST Guardrails Expansion & Quality Gate Enhancements

<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
</required_context_rules>

<domain_boundary>
    <role>AST GUARDRAIL & STATIC ANALYSIS EXPANSION BACKLOG</role>
    <instruction>Tämä backlog dokumentoi PostgreSQL 19 -kovennuskierroksen (18 tiedostoa) aikana havaitut ja opitut tulevat AST-laatuporttien laajennuskohteet. Kohteet eivät estä nykyistä tuotantokelpoisuutta, mutta tarjoavat seuraavan tason ennaltaehkäisevän suojan kyselysuodattimien, operatiivisten skriptien ja Polyfactory-mallitehtaiden laadulle.</instruction>
</domain_boundary>

---

## 1. Tausta ja opit kovennuskierrokselta (Hardening Learnings Context)

Järjestelmällisen ennaltaehkäisyn ja 18 tiedoston PostgreSQL 19 -kovennusjonon (`auto_hardening_runner.py`) aikana havaittiin kolme konkreettista aluetta, joissa nykyinen valvonta nojaa joko ajonaikaiseen validointiin (`__post_init__`), käsin ylläpidettyihin tiedostolistoihin tai yksittäisten testien varaan:

1. **Kyselysuodattimet (`Filter`):** [backend_v2/database/driver.py](file:///c:/src/quorum/backend_v2/database/driver.py) validoi nyt sallitut operaattorit (`_VALID_OPERATORS`) ajonaikaisesti `__post_init__`-metodissa. Virheellinen operaattori tai tyhjä kenttänimi heittää `AppException(VALIDATION_FAILED)` vasta koodia ajettaessa.
2. **Operatiivisten skriptien laatuportti:** [scripts/reconcile_storage.py](file:///c:/src/quorum/scripts/reconcile_storage.py) ja [scripts/run_e2e_variance_test.py](file:///c:/src/quorum/scripts/run_e2e_variance_test.py) olivat aiemmin jääneet laatuporttien katvealueelle, koska laatuportit tarkistivat vain `backend_v2/`-kansion tai eksplisiittisesti listatut skriptit.
3. **Polyfactory-mallitehtaiden oletusarvot:** Monimutkaisten Pydantic-mallien testitehtaissa (kuten `CausalGraphPayloadDTOFactory`) tehtaan `.build()`-kutsun ilman parametreja on tuotettava heti 100 % skeemavalidi malli ilman referenssirikkoa, jotta yksikkötestit eivät kaadu sisäisiin validointivirheisiin.

---

## 2. Toimenpidekohteet (Actionable AST Improvements)

### Tehtävä 1: `QGR031` – Kyselysuodattimien staattinen validointi (`Query Filter Static Strictness`)

- **Prioriteetti:** Keskitaso (Laadullinen suoja)
- **Taso:** `FATAL`
- **Kohdetiedostot:**
  - `@[scripts/_ast_guardrails.py]`
  - `@[backend_v2/database/driver.py]`
  - `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
- **Syntaksipuun analyysi (`ast.NodeVisitor`):**
  - Etsii `ast.Call`-solmut, joissa kutsuttava funktio tai luokka on `Filter(...)`.
  - **Tarkistus A (Operaattori):** Jos 2. argumentti on merkkijonoliteraali (`ast.Constant`), sen on kuuluttava sallittuun joukkoon:
    `{"==", "!=", "<", "<=", ">", ">=", "in", "array-contains"}`.
  - **Tarkistus B (Kenttä):** Jos 1. argumentti on merkkijonoliteraali, se ei saa olla tyhjä `""` tai pelkkää välilyöntiä.
  - **Tarkistus C (`in`-operaattorin arvo):** Jos operaattori on literaali `"in"`, 3. argumentin on oltava lista tai tupla (`ast.List` tai `ast.Tuple`), ei yksittäinen merkkijono tai skalaari.
- **Mitä virheitä tämä löytää:**
  ```python
  # ❌ AST estää: Vieraat SQL- tai MongoDB-operaattorit
  Filter("status", "eq", "active")        # Typo: pitää olla "=="
  Filter("name", "LIKE", "%test%")        # Ei tuettu abstraktissa ajurissa
  Filter("price", "=", 100)               # Yhden yhtäsuuruusmerkin SQL-tapa
  
  # ❌ AST estää: Salakavala Python-merkkijonon iterointibugi
  Filter("role", "in", "admin")           # Pythonissa 'admin' iteroituu kirjaimiksi ['a', 'd', 'm', 'i', 'n']!
  
  # ✅ AST sallii:
  Filter("status", "==", "active")
  Filter("role", "in", ["admin", "editor"])
  Filter("tags", "array-contains", "ai")
  ```

---

### Tehtävä 2: `scripts/`-hakemiston dynaaminen automaattiskannaus (`Dynamic Zero-Shadow Tooling`)

- **Prioriteetti:** Keskitaso (Teknisen velan esto)
- **Kohdetiedostot:**
  - `@[scripts/backend_audit_loop.py]`
  - `@[scripts/_ast_guardrails.py]`
  - `@[scripts/audit_zero_orm_strictness.py]`
- **Kuvaus:**
  - Muutetaan `scripts/backend_audit_loop.py` ja `scripts/_ast_guardrails.py` käyttämään dynaamista polkuhakua (`Path("scripts").glob("*.py")`) kovakoodatun `_MACRO_AUTHORITATIVE_SCRIPTS` -listan sijaan.
  - Määritellään pieni, eksplisiittinen poissulkulista vain puhtaasti erillisille meta-apureille (esim. `scripts/_script_base.py`).
- **Mitä virheitä tämä löytää:**
  1. **Varjoskriptit:** Uudet luodut ylläpito-, analyysi- tai migraatioskriptit joutuvat välittömästi samojen AST- (`QGR001`–`QGR030`), MyPy- ja Ruff-sääntöjen alle ilman erillistä manuaalista rekisteröintiä.
  2. **Orvoksi jääneet työkalut:** Havaitsee heti, jos jokin `scripts/`-työkalu käyttää poistettuja rajapintoja, vanhentuneita malleja tai rikkinäisiä tuonteja.

---

### Tehtävä 3: Polyfactory-mallitehtaiden invarianttivartija (`ModelFactory Zero-Crash Invariant`)

- **Prioriteetti:** Matala / Ylläpidollinen
- **Kohdetiedostot:**
  - `@[scripts/_ast_guardrails.py]`
  - `@[backend_v2/tests/factories/model_factories.py]`
  - `@[backend_v2/tests/factories/test_model_factories.py]`
- **Kuvaus:**
  - **Staattinen AST-tarkistus (`QGR032`):** Varmistaa, että jokaisessa `ModelFactory`-määrittelyssä ID-kenttien generoijaksi on asetettu `Use(lambda: generate_opaque_id(EntityPrefix.<TYPE>))` tai vastaava heksadesimaalinen generaattori kovakoodattujen testistringien (kuten `"user_123"`) sijaan.
  - **Automaattinen metatesti:** Laajennetaan `test_model_factories.py` käymään reflektiivisesti läpi kaikki `ModelFactory`-aliluokat ja varmistamaan, että kutsut `Factory.build()` ilman argumentteja palauttavat poikkeuksetta skeemavalidin Pydantic V2 -mallin.
- **Mitä virheitä tämä löytää:**
  ```python
  # ❌ AST estää: QGR030 heksavaatimuksen rikkova tehdas
  class WorkflowFactory(ModelFactory[Workflow]):
      id = "wor_sample_test"              # Ei-heksadesimaalinen ID
  
  # ✅ AST sallii:
  class WorkflowFactory(ModelFactory[Workflow]):
      id = Use(lambda: generate_opaque_id(EntityPrefix.WORKFLOW))
  ```

---

## 3. Toteutussuositus ja ajoitus

Nämä kolme toimenpidettä ovat **ennaltaehkäiseviä laadunparannuksia**, eivätkä ne vaadi välitöntä hätäkorjausta. Ne suositellaan toteutettavaksi seuraavan laatu- tai refaktorointiepicin yhteydessä omana hallittuna kokonaisuutenaan.
