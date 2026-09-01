# Backlog: AliasEngine Refactoring & Complete Dict Traversal Purge

<domain_boundary>
    <role>TECHNICAL DEBT & TYPING PURITY BACKLOG</role>
    <instruction>This backlog documents the remaining architectural cleanups required to completely eliminate ad-hoc dictionary traversals, duck-typing compromises, and dead code from `backend_v2/utils/alias_engine.py` and `backend_v2/utils/math_utils.py`.</instruction>
</domain_boundary>

---

## 1. Tausta ja ongelmankuvaus (Context & Problem Statement)

Vaikka tietokantaprotokollat (15/15) ja `dict_utils.py` refaktoroitiin onnistuneesti vahvoiksi Pydantic V2 DTO -malleiksi ja puhtaiksi tilanvähentäjiksi (`state_reducer.py`), koodikantaan jäi vielä tiettyjä historiallisia sanakirjanläpikäyntifunktioita ja ad-hoc tyyppitarkastuksia (`type(node) is dict`, `getattr`):

1. **`AliasEngine` (`backend_v2/utils/alias_engine.py`)**:
   - Sisältää kuollutta koodia (`hydrate_dict_list`), jota ei kutsuta missään tuotantokoodissa, vaan ainoastaan sen omissa vanhoissa yksikkötesteissä.
   - Sisältää rekursiivisen sanakirjapuun läpikäyjän (`hydrate_and_filter_aliases`), joka ottaa vastaan `node: Any` ja suorittaa dynaamista tyypintunnistusta (`dict` vs. `list` vs. skalaarit) sen sijaan, että hydraus tapahtuisi tyypitetyllä Pydantic DTO -tasolla.
2. **`math_utils.py` (`backend_v2/utils/math_utils.py`)**:
   - `resolve_dot_notation` sisältää geneerisen tilanselaajan (`isinstance(curr, dict)` ja `getattr(curr, part)`), joka vaatii `# noqa`-ohituksen toimiakseen dynaamisilla syöterajoilla.
3. **`synthesis_engine.py` (`backend_v2/services/orchestrator/engines/synthesis_engine.py`)**:
   - Muuntaa validoidun Pydantic-mallin sanakirjaksi (`output_dict = validated_model.model_dump()`) ennen aliasten hydrausta sen sijaan, että hydraus tehtäisiin suoraan DTO-tasolla.

---

## 2. Backlog-tehtävät (Actionable Backlog Items)

### Tehtävä 1: Poista kuollut koodi `hydrate_dict_list()` ja sen vanhat testit
- **Kohdetiedosto**: `backend_v2/utils/alias_engine.py`
- **Kuvaus**: 
  - Poista funktio `hydrate_dict_list(self, items: list[dict[str, Any]], field_name: str) -> int`.
  - Poista vanhat sanakirjatestit `backend_v2/tests/unit/utils/test_alias_engine.py` -tiedostosta:
    - `test_hydrate_dict_list_replaces_aliases`
    - `test_hydrate_dict_list_recursive_hydration`
    - `test_hydrate_dict_list_skips_unknown_aliases`
- **Hyväksymiskriteeri**: `grep_search("hydrate_dict_list")` palauttaa 0 osumaa koko koodikannassa.

---

### Tehtävä 2: Refaktoroi `hydrate_and_filter_aliases` DTO-tason hydraukseksi
- **Kohdetiedostot**: 
  - `backend_v2/utils/alias_engine.py`
  - `backend_v2/services/orchestrator/engines/synthesis_engine.py`
  - `backend_v2/tests/unit/utils/test_alias_engine.py`
- **Kuvaus**:
  - Korvaa `hydrate_and_filter_aliases(data: Any, field_names: set[str])` vahvasti tyypitetyllä DTO-tason hydraajalla tai kenttäkohtaisella tekstikorvaajalla.
  - Refaktoroi `synthesis_engine.py#L191-L202` siten, että aliasten hydraus ja hallusinoitujen UUID-tunnisteiden pudotus tehdään suoraan Pydantic DTO -instanssin kentille ennen `TraceEvent`-luomista (ilman mielivaltaisen JSON-sanakirjapuun rekursiota).
- **Hyväksymiskriteeri**: `alias_engine.py` ei sisällä yhtäkään `type(node) is dict`- tai `isinstance(..., dict)` -tarkastusta.

---

### Tehtävä 3: `resolve_dot_notation` -funktion tyyppitietoisuus (`math_utils.py`)
- **Kohdetiedosto**: `backend_v2/utils/math_utils.py`
- **Kuvaus**:
  - Refaktoroi `resolve_dot_notation(state: Any, path: str)` siten, että polkuhaku tukeutuu Pydantic-mallien `__pydantic_fields__` / `getattr`-vapaisiin kenttäindekseihin tai puhtaaseen tyyppierotteluun ilman `# noqa: QGR001` ja `# noqa: QGR012` -ohituksia.
- **Hyväksymiskriteeri**: `math_utils.py` läpäisee `scripts/_ast_guardrails.py` ilman yhtäkään `# noqa`-ohitusta.

---

### Tehtävä 4: AST Guardrail -sääntöjen kiristys (`scripts/_ast_guardrails.py`)
- **Kohdetiedosto**: `scripts/_ast_guardrails.py`
- **Kuvaus**:
  - Lisää tarkastus, joka kieltää `type(x) is dict` ja `type(x) == dict` -kierrot domain-koodissa (`QGR012`:n laajennus).
  - Varmista, että `backend_v2/utils/` -kansiossa ei sallita mitään tyyppiohituksia ilman välitöntä CI-virhettä.
- **Hyväksymiskriteeri**: `type(x) is dict` tuottaa `FATAL`-virheen kaikissa ei-ajuritiedostoissa.

---

## 3. Prioriteetti ja riippuvuudet

| ID | Tehtävä | Prioriteetti | Arvioitu laajuus | Riippuvuudet |
| :--- | :--- | :--- | :--- | :--- |
| **BL-01** | Poista kuollut `hydrate_dict_list()` ja testit | **Korkea (Quick Win)** | Pieni (15 min) | Ei riippuvuuksia |
| **BL-02** | DTO-tason aliashydraus `synthesis_engine.py`:ssä | **Keskisuuri** | Keskikokoinen (1 h) | BL-01 |
| **BL-03** | `resolve_dot_notation` puhdistus `math_utils.py`:ssä | **Keskisuuri** | Pieni (30 min) | Ei riippuvuuksia |
| **BL-04** | AST-laajennus: kiellä `type(x) is dict` kiertotavat | **Matala** | Pieni (30 min) | BL-02, BL-03 |
