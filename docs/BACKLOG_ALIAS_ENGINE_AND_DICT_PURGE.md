# Backlog: AliasEngine Refactoring & Complete Dict Traversal Purge

<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
</required_context_rules>

<domain_boundary>
    <role>TECHNICAL DEBT & TYPING PURITY BACKLOG</role>
    <instruction>Tämä backlog dokumentoi tarvittavat arkkitehtuuriset puhdistukset, joilla eliminoidaan ad-hoc sanakirjanläpikäynnit, duck-typing -kierrot ja kuollut koodi tiedostoista `backend_v2/utils/alias_engine.py` ja `backend_v2/utils/math_utils.py` sekä päivitetään niihin liittyvät säännöt.</instruction>
</domain_boundary>

---

## 1. Tausta ja ongelmankuvaus (Context & Problem Statement)

Vaikka tietokantaprotokollat (15/15) ja `dict_utils.py` refaktoroitiin onnistuneesti vahvoiksi Pydantic V2 DTO -malleiksi ja puhtaiksi tilanvähentäjiksi (`state_reducer.py`), koodikantaan jäi vielä tiettyjä historiallisia sanakirjanläpikäyntifunktioita ja ad-hoc tyyppitarkastuksia (`type(node) is dict`, `getattr`):

1. **`AliasEngine` (`backend_v2/utils/alias_engine.py`)**:
   - Sisältää kuollutta koodia (`hydrate_dict_list`), jota ei kutsuta missään tuotantokoodissa, vaan ainoastaan sen omissa vanhoissa yksikkötesteissä. Sääntötiedostossa `01-python-backend.md` (rivi 94) on edelleen vanhentunut viittaus tähän funktioon.
   - Sisältää rekursiivisen sanakirjapuun läpikäyjän (`hydrate_and_filter_aliases`), joka ottaa vastaan `node: Any` ja suorittaa dynaamista tyypintunnistusta (`type(node) is dict` vs. `list` vs. skalaarit) sen sijaan, että hydraus tapahtuisi tyypitetyllä Pydantic DTO -tasolla.
2. **`math_utils.py` (`backend_v2/utils/math_utils.py`)**:
   - Sisältää matemaattisen apukirjaston ulkopuolisen tilanselaajan `resolve_dot_notation(state: Any, path: str)` (`isinstance(curr, dict)` ja `getattr(curr, part)`), joka vaatii `# noqa: QGR001` ja `# noqa: QGR012` -ohitukset.
   - Ainoa tuotantokoodin käyttökohde funktiolle on `context_builder.py` (`backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L271`).
3. **`synthesis_engine.py` (`backend_v2/services/orchestrator/engines/synthesis_engine.py`)**:
   - Muuntaa validoidun Pydantic-mallin sanakirjaksi (`output_dict = validated_model.model_dump()`) ennen aliasten hydrausta sen sijaan, että hydraus tehtäisiin suoraan DTO-tasolla.

---

## 2. Backlog-tehtävät (Actionable Backlog Items)

### Tehtävä 1: Poista kuollut koodi `hydrate_dict_list()`, vanhat testit ja päivitä sääntö
- **Kohdetiedostot**: 
  - `@[backend_v2/utils/alias_engine.py]`
  - `@[backend_v2/tests/unit/utils/test_alias_engine.py]`
  - `@[.agents/rules/01-python-backend.md]`
- **Kuvaus**: 
  - Poista funktio `hydrate_dict_list(self, items: list[dict[str, Any]], field_name: str) -> int` tiedostosta `alias_engine.py`.
  - Poista vanhat sanakirjatestit `test_alias_engine.py` -tiedostosta:
    - `test_hydrate_dict_list_replaces_aliases`
    - `test_hydrate_dict_list_recursive_hydration`
    - `test_hydrate_dict_list_skips_unknown_aliases`
  - Päivitä sääntötiedoston `@[.agents/rules/01-python-backend.md]` rivi 94 (`alias_engine_llm_isolation_mandate`) poistamalla vanhentunut `hydrate_dict_list()` -viite ja korvaamalla se DTO-tason hydrausohjeella.
- **Hyväksymiskriteeri**: `grep_search("hydrate_dict_list")` palauttaa 0 osumaa koko koodikannassa.

---

### Tehtävä 2: Refaktoroi `hydrate_and_filter_aliases` DTO-tason hydraukseksi
- **Kohdetiedostot**: 
  - `@[backend_v2/utils/alias_engine.py]`
  - `@[backend_v2/services/orchestrator/engines/synthesis_engine.py]`
  - `@[backend_v2/tests/unit/utils/test_alias_engine.py]`
- **Kuvaus**:
  - Korvaa `hydrate_and_filter_aliases(data: Any, field_names: set[str])` vahvasti tyypitetyllä DTO-tason aliashydraajalla (esim. `AliasEngine.hydrate_synthesis_dto()` tai DTO-kohtaisella kenttähydrauksella).
  - Refaktoroi `synthesis_engine.py#L191-L202` siten, että aliasten hydraus ja hallusinoitujen UUID-tunnisteiden suodatus tehdään suoraan Pydantic DTO -instanssin kentille ennen `TraceEvent`-luomista ilman `validated_model.model_dump()` -sanakirjamutaatiota.
- **Hyväksymiskriteeri**: `alias_engine.py` ja `synthesis_engine.py` eivät sisällä yhtäkään `type(node) is dict`- tai `isinstance(..., dict)` -tarkastusta.

---

### Tehtävä 3: Poista `resolve_dot_notation` kokonaan `math_utils.py`:stä ja siirry puhtaaseen DTO-pistenotaatioon
- **Kohdetiedostot**:
  - `@[backend_v2/utils/math_utils.py]`
  - `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]`
  - `@[backend_v2/tests/unit/utils/test_math_utils.py]`
  - `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]`
- **Kuvaus**:
  - `resolve_dot_notation` on käytössä ainoastaan tiedostossa `context_builder.py` (rivi 271). Se ei kuulu matemaattiseen apukirjastoon (`math_utils.py`).
  - Poista `resolve_dot_notation` kokonaan tiedostosta `math_utils.py` sekä sen vanhat yksikkötestit tiedostosta `test_math_utils.py`.
  - Refaktoroi `context_builder.py` siten, että dynaamisen sanakirjapolun etsinnän sijaan käytetään suoraa pistenotaatiota tai vahvasti tyypitettyä `ExecutionContextDTO` / `StepOutputDTO` -adapteria ilman Pydanticin sisäistä `__pydantic_fields__`-heijastusta tai `getattr`-kutsuja.
- **Hyväksymiskriteeri**: `resolve_dot_notation` on poistettu kokonaan ja `math_utils.py` sekä `context_builder.py` läpäisevät `scripts/_ast_guardrails.py` ilman yhtäkään `# noqa`-ohitusta.

---

### Tehtävä 4: AST Guardrail -sääntöjen kiristys (`scripts/_ast_guardrails.py`)
- **Kohdetiedosto**: `@[scripts/_ast_guardrails.py]`
- **Kuvaus**:
  - Lisää tarkastus, joka kieltää `type(x) is dict` ja `type(x) == dict` -kierrot domain-koodissa (`QGR012`:n laajennus).
  - Varmista, että `backend_v2/utils/` -kansiossa ei sallita mitään tyyppiohituksia ilman välitöntä CI-virhettä.
- **Hyväksymiskriteeri**: `type(x) is dict` ja `type(x) == dict` tuottavat `FATAL`-virheen kaikissa ei-ajuritiedostoissa.

---

## 3. Prioriteetti ja riippuvuudet

| ID | Tehtävä | Prioriteetti | Arvioitu laajuus | Riippuvuudet |
| :--- | :--- | :--- | :--- | :--- |
| **BL-01** | Poista kuollut `hydrate_dict_list()`, testit ja päivitä `01-python-backend.md` | **Korkea (Quick Win)** | Pieni (15 min) | Ei riippuvuuksia |
| **BL-02** | DTO-tason aliashydraus `synthesis_engine.py`:ssä | **Keskisuuri** | Keskikokoinen (1 h) | BL-01 |
| **BL-03** | Poista `resolve_dot_notation` `math_utils.py`:stä ja refaktoroi `context_builder.py` | **Keskisuuri** | Keskikokoinen (45 min) | Ei riippuvuuksia |
| **BL-04** | AST-laajennus: kiellä `type(x) is dict` ja `type(x) == dict` | **Matala** | Pieni (30 min) | BL-02, BL-03 |
