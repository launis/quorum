# Clean Pydantic Transition Catalog & Refactoring Guide
*(Puhdas Pydantic -arkkitehtuuri, juurisyyanalyysi ja sanakirjojen poistoluettelo)*

---

## 1. Visio ja tavoitetila (Vision & Invariants)

Quorumin backendin tavoitetila on **täysin vahvasti tyypitetty, tyyppiohjattu arkkitehtuuri (Type-Driven Architecture)**, jossa:
1. **Ei naked-sanakirjoja tilansiirrossa (`no_naked_dicts_in_state`):** Kaikki rajapintojen, koukkujen (hooks), strategioiden ja palveluiden välinen data kulkee tiukkojen Pydantic V2 -mallien kautta (`strict=True, extra="forbid"`).
2. **Ei puolustuksellisia `isinstance(x, dict)`- tai `.get()`-haaroja:** Palvelukerros ei tarkistele ajonaikaisesti datan muotoa. Jos data pääsee palvelulle asti, sen rakenne ja tyypit ovat 100 % taattuja Pydanticin toimesta.
3. **Suora pistenotaatio:** Kaikki kenttien luvut tehdään suoraan pistenotaatiolla (`context.metadata.target_locale`, `step.model_strategy`), ei koskaan sanakirja-avaimilla (`context.metadata["target_locale"]` tai `data.get("key")`).
4. **Ei `model_dump()` -> dict -> `model_copy()` -silppua:** Olioita ei pureta sanakirjoiksi vain siksi, että niihin halutaan liittää uusia kenttiä. Kaikki tarvittavat ajonaikaiset tilakentät määritellään eksplisiittisesti tietomalleissa.
5. **Ei hiljaisia oletusarvoja pakollisille liiketoimintakentille (*No Silent Defaults for Mandatory Fields*):** Jos kenttä on kriittinen järjestelmän toiminnalle (kuten `target_locale`), sillä ei saa olla laiskaa oletusarvoa (`target_locale: str = "en"`), vaan puuttuva tieto kaataa validoinnin heti (Fail-Fast).
6. **Tyypitetyt tilamuutokset (Typed State Deltas):** Koukut ja strategiat palauttavat vahvasti tyypitettyjä DTO-deltamalleja geneerisen `dict[str, Any]` sijaan, jolloin tilansiirtymät tapahtuvat tyyppiturvallisesti.

---

## 2. Juurisyyanalyysi: Miksi velkaa syntyi tiukoista perussäännöistä huolimatta?

Vaikka koodikannan ohjeissa (`00-antigravity-core.md` ja `01-python-backend.md`) on aina ollut tiukkoja periaatteita (`zero_service_layer_fallbacks`, `the_zero_compromise_pledge`), velkaa kertyi neljän konkreettisen mekanismin kautta:

### 1. "Laiskat Unionit" rajapinnoissa (`Model | dict[str, Any]`)
- **Ilmiö:** Kun vanhaa koodikantaa refaktoroitiin kohti Pydanticia, rajapintoihin jätettiin siirtymäkompromisseja, jotta vanhat testit eivät hajoaisi kerralla (esim. `HookState.metadata: ExecutionMetadata | HookStateMetadata | dict[str, Any]`).
- **Seuraus:** Kun rajapinta sallii sanakirjan, jokainen sitä käyttävä alavirran palvelu ja koukku (`strategies/llm.py`, `synthesis_distiller.py`) oli pakotettu kirjoittamaan `if isinstance(x, ExecutionMetadata) else x.get(...)` -tarkistuksia.

### 2. Mallien alimitoitus (*Under-modeling*) ja elinkaaripuutteet
- **Ilmiö:** Kun Pydantic-malleja luotiin, niihin mallinnettiin vain "alkutila" (kuten `target_locale`, `profile_id`), mutta **ei ajonaikana syntyvää dataa** (kuten `step_metrics`, `dag_cost_usd`, `prompt_tokens`).
- **Seuraus:** Koska mallissa oli `extra="forbid"`, agentit eivät voineet asettaa telemetriaa suoraan malliin. Agentti valitsi "helpoimman tien" ja teki `model.model_dump()` $\rightarrow$ lisäsi kentät sanakirjaan $\rightarrow$ tallensi tilan sanakirjana.

### 3. AST Guardrail -valvonnan puute ja feilaamattomat laatuportit
- **Ilmiö:** Teksti ohjetiedostossa ei yksin riitä estämään tekoälyä oikomasta ("Path of Least Resistance"), jos automaattinen laatuportti ei estä PR:ää/committia.
- **Seuraus:** Laatuportti (`backend_audit_loop.py`) valvoi aiemmin vain varoituksina tiettyjä kutsuja, muttei estänyt `isinstance(..., dict)` -haaroja tai `model_dump() -> dict` -muunnoksia palvelukerroksessa.

### 4. Puuttuva KI-malliesimerkki immutaabelin tilan päivitykseen
- **Ilmiö:** Koodikannassa ei ollut selkeää malliesimerkkiä siitä, miten sisäkkäistä immutaabelia tilaa (`frozen=True`) päivitetään oikeaoppisesti ilman sanakirjamutaatioita.
- **Seuraus:** Kehittäjät ja agentit turvautuivat sanakirjapurkuihin (`model_dump()`), koska eivät tienneet Pydanticin sisäkkäistä `model_copy(update={...})` -rakennetta.

---

## 3. Koodikannan anti-pattern-arkkityypit ja esimerkkikohteet

### Arkkityyppi 1: Kahden kerroksen kaksoishaarautuminen (`isinstance(Model) else dict.get(...)`)

Kun rajapinta hyväksyy unionin `Model | dict[str, Any]`, koodiin syntyy puolustuksellista ja vaikeaselkoista tarkistuslogiikkaa:

#### Esimerkki 1: `backend_v2/services/orchestrator/strategies/llm.py` (Rivit 226–235 & 300–309)
```python
# NYKYINEN ANTI-PATTERNI:
target_profile = (
    context.metadata.profile_id
    if isinstance(context.metadata, ExecutionMetadata)
    else context.metadata.get("profile_id")
    if isinstance(context.metadata, dict)
    else None
)
if not target_profile:
    raise ConfigurationError("Missing profile_id")

target_locale = (
    context.metadata.target_locale
    if isinstance(context.metadata, ExecutionMetadata)
    else context.metadata.get("target_locale")
    if isinstance(context.metadata, dict)
    else None
)
```

#### Tavoitetila (Clean Pydantic):
```python
# PUHDAS TAVOITETILA:
# StrategyContext.metadata on aina ExecutionMetadata
target_profile = context.metadata.profile_id
target_locale = context.metadata.target_locale
```

---

#### Esimerkki 2: `backend_v2/services/usage_service.py` (Rivit 150–158)
```python
# NYKYINEN ANTI-PATTERNI:
if isinstance(model_pricing_config, dict):
    input_rate = model_pricing_config.get("input_cost_per_token", 0.0)
elif isinstance(model_pricing_config, PricingConfig):
    input_rate = model_pricing_config.input_cost_per_token
```

#### Tavoitetila (Clean Pydantic):
```python
# PUHDAS TAVOITETILA:
# Syötteen tyyppi on aina PricingConfig
input_rate = model_pricing_config.input_cost_per_token
```

---

### Arkkityyppi 2: Mallin purkaminen sanakirjaksi kenttien lisäämiseksi (`model_dump() + {**d} + model_copy()`)

Kun immutaabeliin Pydantic-tilaan halutaan lisätä ajonaikaisia lippuja, malli puretaan sanakirjaksi ja kasataan uudestaan:

#### Esimerkki: `backend_v2/services/orchestrator/strategies/llm.py` (Rivit 290–298)
```python
# NYKYINEN ANTI-PATTERNI:
initial_meta_updates: dict[str, Any] = {"execution_id": context.execution_id}
if is_lightweight:
    initial_meta_updates["is_lightweight_extraction"] = True
current_hook_meta = (
    hook_state.metadata.model_dump()
    if isinstance(hook_state.metadata, (ExecutionMetadata, HookStateMetadata))
    else dict(hook_state.metadata or {})
)
hook_state = hook_state.model_copy(update={"metadata": {**current_hook_meta, **initial_meta_updates}})
```

#### Tavoitetila (Clean Pydantic):
Ajonaikaiset liput kulkevat suoraan `ExecutionMetadata`- tai `StrategyContext`-kenttinä tai `HookState`-attribuutteina ilman sanakirjamutaatioita:
```python
# PUHDAS TAVOITETILA:
hook_state = hook_state.model_copy(
    update={
        "metadata": hook_state.metadata.model_copy(
            update={
                "is_lightweight_extraction": is_lightweight,
            }
        )
    }
)
```

---

### Arkkityyppi 3: Usean tason sisäkkäinen sanakirjakaivelu (`dict -> dict -> dict`)

Kun syöteobjektit ovat määrittelemättömiä `dict`-rakenteita, koodi joutuu tekemään monitasoista `isinstance`- ja `.get()`-ketjutusta:

#### Esimerkki: `backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py` (Rivit 40–55)
```python
# NYKYINEN ANTI-PATTERNI:
if isinstance(llm_context_data, dict):
    raw_inputs = llm_context_data.get("inputs")
    if isinstance(raw_inputs, dict):
        dynamic_inputs = raw_inputs.get("dynamic_inputs")
        if isinstance(dynamic_inputs, dict):
            doc_date = dynamic_inputs.get("document_creation_date")
            ...
```

#### Tavoitetila (Clean Pydantic):
Syötedata validoidaan kerralla Pydantic-malliksi (`ExecutionInputsDTO` / `DynamicInputsDTO`):
```python
# PUHDAS TAVOITETILA:
doc_date = llm_context_data.inputs.dynamic_inputs.document_creation_date
```

---

### Arkkityyppi 4: Löysät Union-tyypit tilarajapinnoissa

Kun tilaluokat sallivat geneerisen sanakirjan, tyyppiturva murtuu alavirrassa:

#### Esimerkki: `backend_v2/core/hook_registry.py` (Rivit 40–45)
```python
# NYKYINEN ANTI-PATTERNI:
class HookState(BaseModel):
    execution_id: str
    workflow_id: str
    inputs: dict[str, Any] | BaseModel = Field(default_factory=dict)
    metadata: ExecutionMetadata | HookStateMetadata | dict[str, Any] = Field(default_factory=dict)
    global_context_vars: dict[str, Any] = Field(default_factory=dict)
```

#### Tavoitetila (Clean Pydantic):
```python
# PUHDAS TAVOITETILA:
class HookState(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    
    execution_id: str
    workflow_id: str
    inputs: dict[str, Any]  # Tai vahvasti tyypitetty ExecutionInputs
    metadata: ExecutionMetadata
    global_context_vars: GlobalContextVarsDTO
```

---

### Arkkityyppi 5: Telemetrian ja suoritustuloksen manuaalinen sanakirjakirjoitus

Kun suorituksen lopputulosta tallennetaan, rakennetaan sanakirjoja ilman Pydantic-validaatiota:

#### Esimerkki: `backend_v2/worker.py` (Rivit 310–325)
```python
# NYKYINEN ANTI-PATTERNI:
updated_meta = dict(exec_record.metadata or {})
updated_meta["execution_summary"] = execution_summary
updated_meta["step_metrics"] = step_metrics
updated_meta["dag_cost_usd"] = total_cost_usd
updated_meta["prompt_tokens"] = total_prompt_tokens
...
```

#### Tavoitetila (Clean Pydantic):
```python
# PUHDAS TAVOITETILA:
updated_metadata = exec_record.metadata.model_copy(
    update={
        "execution_summary": execution_summary,
        "step_metrics": step_metrics,
        "dag_cost_usd": total_cost_usd,
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
        "cached_tokens": total_cached_tokens,
        "reasoning_tokens": total_reasoning_tokens,
    }
)
```

---

### Arkkityyppi 6: Hiljaiset oletusarvot pakollisille liiketoimintakentille (*Silent Default Masking*)

Kun kriittiselle liiketoimintakentälle annetaan mielivaltainen oletusarvo tietomallissa, se naamioi puuttuvat tai virheelliset syötteet:

#### Esimerkki: `backend_v2/models/v2_core.py` (Rivit 1376–1379) & `execution_core.py` (Rivi 62)
```python
# NYKYINEN ANTI-PATTERNI:
metadata: ExecutionMetadata = Field(
    default_factory=lambda: ExecutionMetadata(target_locale="en"),
    description="Strictly typed metadata for the execution",
)
# Tai:
target_locale: str = "en"
```

#### Miksi tämä on virheellistä?
- Ohjelmisto ei voi toimia ilman eksplisiittisesti tiedossa olevaa kieltä (käyttöliittymä, promptit, matriisit ja SDUI vaativat aina todellisen kielen).
- Oletusarvo `"en"` sallii kutsujan luoda `ExecutionRecord`-olion ilman `target_locale`-tietoa, jolloin ohjelmisto ajaa hiljaa väärällä kielellä sen sijaan, että se kaatuisi heti selkeään validointivirheeseen.

#### Tavoitetila (Clean Pydantic):
```python
# PUHDAS TAVOITETILA:
# Pakolliset kentät vaaditaan aina ilman oletusarvoja
target_locale: Annotated[str, Field(description="Target locale for outputs, e.g. 'fi', 'en'.")]
metadata: Annotated[ExecutionMetadata, Field(description="Strictly typed metadata for the execution.")]
```

---

### Arkkityyppi 7: Sanakirjamutaatiot ja manuaalinen `pop()`-poiminta tilamuutoksissa (*Untyped State Deltas & Manual Pop Harvesting*)

Kun koukut palauttavat geneerisen sanakirjan `state_delta: dict[str, Any]`, tilakontekstien päivitys orkestroijassa muuttuu mutkikkaaksi:

#### Esimerkki: `backend_v2/services/orchestrator/strategies/base.py` (Rivit 296–308)
```python
# NYKYINEN ANTI-PATTERNI:
if ph_res.success and ph_res.state_delta:
    delta = dict(ph_res.state_delta)
    metadata_updates = delta.pop("metadata", None)
    if metadata_updates and isinstance(metadata_updates, dict):
        new_metadata = hook_state.metadata.model_copy(update=metadata_updates)
        hook_state = hook_state.model_copy(update={"metadata": new_metadata})

    gvars_updates = delta.pop("global_context_vars", None)
    if gvars_updates:
        new_gvars = dict(hook_state.global_context_vars)
        new_gvars.update(gvars_updates)
        hook_state = hook_state.model_copy(update={"global_context_vars": new_gvars})
```

#### Miksi tämä on monimutkaista?
- `state_delta` on tyypittämätön sanakirja, joten orkestroijan täytyy arvailla ja purkaa (`pop()`) avaimia yksitellen ja tarkistaa `isinstance(metadata_updates, dict)`.
- Sisäkkäistä immutaabelia tilaa päivitetään kahdessa eri vaiheessa (`new_metadata` ensin, sitten `hook_state`).

#### Tavoitetila (Clean Pydantic):
1. **Tyypitetty Delta-malli:** `HookResult` palauttaa tyypitetyn `HookDeltaDTO`-olion.
2. **Kapseloitu tilasiirtymä:** `HookState` tarjoaa suoran metodin deltan soveltamiseen (`hook_state = hook_state.apply_delta(ph_res.delta)`) ilman manuaalisia sanakirjapurkuja:
```python
# PUHDAS TAVOITETILA:
if ph_res.success and ph_res.delta:
    hook_state = hook_state.apply_delta(ph_res.delta)
```

---

### Arkkityyppi 5: Repositorion sanakirjavastuu vs. DDD-rekonstruointi (DAL dict return leak)

Kun repositoriot palauttavat `dict[str, Any]` (vanhentuneen `polymorphic_parsing_mandate` -säännön mukaisesti), jokainen kutsuva palvelu pakotetaan toistamaan Pydantic-hydratointia ja kirjoittamaan puolustuksellisia tarkistuksia:

#### Esimerkki: `backend_v2/services/studio/system_config_service.py` (Rivit 327–367)
```python
# NYKYINEN ANTI-PATTERNI:
# Repositorio palauttaa dict[str, Any], palvelu joutuu validoimaan joka kerta erikseen
raw_dict = await self.system_repo.get_mcp_gateways()
if not raw_dict or raw_dict.get("type") != "mcp_gateways":
    raise ResourceNotFoundError(...)
return SystemConfigMCPGateways.model_validate(raw_dict, strict=False)
```

#### Miksi tämä on teknistä velkaa?
- **DDD-periaatteen rikkoutuminen:** Repositorion tehtävä arkkitehtuurissa on nimenomaan *rekonstruoida tietokannan raakadatasta aitoja Domain-olioita*. Alin tietokanta-ajuri (`JSONFileDriver`, `FirestoreDriver`) palauttaa `dict[str, Any]`, mutta `Repository` palauttaa valmiiksi validoidun Pydantic-mallin.
- **Koodin duplikaatio:** Kaikki palvelut (`BlueprintTransformer`, `StudioSystemConfigService`, taustatyöt), jotka käyttävät samaa repositoriota, joutuvat toistamaan `SystemConfigMCPGateways.model_validate(raw, strict=False)` -kutsun.
- **MyPy- ja IDE-tyyppiturvan hajoaminen:** `dict[str, Any]` piilottaa kenttien nimet, estäen staattisen analyysin ja refaktorointityökalujen toiminnan.

#### Tavoitetila (Clean Pydantic):
```python
# PUHDAS TAVOITETILA:
# ISystemRepository.get_mcp_gateways(id) palauttaa suoraan SystemConfigMCPGateways
gateway_config: SystemConfigMCPGateways = await self.system_repo.get_mcp_gateways(id=workflow_obj.mcp_gateway_id)
tools_map = {tool.tool_id: tool for tool in gateway_config.tools}
```

---

## 4. Järjestelmätason korjaustoimenpiteet (Systemic Remedies & Guardrails)

Jotta Pydantic-velka ei pääse enää koskaan syntymään uudelleen, toteutetaan kolme järjestelmätason muutosta:

### 1. Sääntöpäivitys (`.agents/rules/01-python-backend.md`)
Lisätään uusi ehdoton kielto `no_loose_state_unions` ja `no_silent_defaults_mandate`:
- Tila- ja kontekstiobjektit (`HookState`, `StrategyContext`, `ExecutionContext`) eivät saa koskaan sisältää unionia sanakirjan kanssa (`Model | dict`).
- Pakollisille liiketoimintakentille (`target_locale`, `id`, `workflow_id`) ei saa asettaa oletusarvoja, jotka naamioivat puuttuvan syötteen.
- Kumotaan vanhentunut `polymorphic_parsing_mandate`: Repositoriot palauttavat vahvasti tyypitettyjä Pydantic Domain -malleja (`SystemConfigMCPGateways`, `Workflow`, `ExecutionRecord`). Alin I/O-ajuri (`JSONFileDriver`) vastaa raakasanakirjoista.

### 2. Uusi Knowledge Item (`ki_pydantic_v2_ssot_patterns.md`)
Luodaan tietokantaan selkeä viitedokumentti, joka sisältää:
- Täydellisen Pydantic V2 -elinkaarimallin (alkutila $\rightarrow$ suoritus $\rightarrow$ telemetria $\rightarrow$ tallennus).
- Valmiin koodimallin sisäkkäisen immutaabelin tilan päivittämiseen (`model_copy`).
- Gateway-validoinnin periaatteet ulkoisille syötteille ja repositoriokerrokselle.

### 3. Laatuportin AST Guardrail -tiukennus (`backend_audit_loop.py`)
Nostetaan laatuportin AST-tarkistukset varoituksista estäviksi virheiksi:
- Palvelukerroksessa (`services/` ja `hooks/`) esiintyvät `isinstance(..., dict)`, `getattr()` ja `d.get()` estävät laatuportin läpimenon automaattisesti.

---

## 5. Siivousvaiheen etenemissuunnitelma (Refactoring Roadmap)

| Vaihe | Kohdealue | Tavoite | Keskeiset tiedostot |
|---|---|---|---|
| **Vaihe 1** | **Tietomallit & SSOT** | Lukitse `ExecutionMetadata` kattamaan kaikki telemetriakentät. Poista hiljaiset `target_locale="en"` -oletusarvot `ExecutionRecord`- ja `ExecutionCoreFields`-malleista. Poista `HookStateMetadata` ja `dict` unionit. | `backend_v2/models/execution_core.py`<br>`backend_v2/models/v2_core.py`<br>`backend_v2/core/hook_registry.py`<br>`backend_v2/services/orchestrator/strategies/base.py` |
| **Vaihe 2** | **Repositoriot & DAL** | Päivitä `ISystemRepository` ja muut repositoriot palauttamaan suoraan tyypitettyjä Pydantic Domain -malleja (`SystemConfigMCPGateways`, `OutputProfile`) tyypittömien sanakirjojen sijaan. | `backend_v2/database/interfaces.py`<br>`backend_v2/database/repositories/system.py`<br>`backend_v2/database/repositories/output_profile.py` |
| **Vaihe 3** | **Orkestrointi & Strategiat** | Poista kaikki `isinstance(..., dict)` ja `metadata.get()` haarat `DAGExecutor`- ja `strategies/llm.py`-luokista. Siirry 100 % suoraan pistenotaatioon. | `backend_v2/services/orchestrator/dag_executor.py`<br>`backend_v2/services/orchestrator/strategies/llm.py` |
| **Vaihe 4** | **Koukut (Hooks) & Deltamallit** | Poista `sanitize_text_hook`, `atom_flattening` ja `source_verification_hook` sanakirjaluvut. Siirry tyypitettyihin `HookDeltaDTO`-malleihin. | `backend_v2/hooks/security.py`<br>`backend_v2/hooks/atom_flattening.py`<br>`backend_v2/hooks/source_verification_hook.py` |
| **Vaihe 5** | **Konteksti- & Apupalvelut** | Korvaa `execution_time_resolver.py` ja `usage_service.py` sanakirjakaivelut tiukasti tyypitetyillä DTO-malleilla. | `backend_v2/services/orchestrator/strategies/llm_execution/`<br>`backend_v2/services/usage_service.py` |
| **Vaihe 6** | **Taustatyöt & Tallennus** | Päivitä `worker.py` käyttämään `exec_record.metadata.model_copy(...)` tyypitetyillä kentillä ilman `dict()`-välivaiheita. | `backend_v2/worker.py`<br>`backend_v2/database/repositories/execution.py` |

---

## 6. Pydantic Best Practice -säännöt Quorumissa

1. **`ConfigDict(strict=True, extra="forbid")`:** Kaikki uudet DTO:t ja tilamallit määritellään estämään ylimääräiset kentät.
2. **Ei koskaan `getattr(obj, "field", default)` tai `d.get("field", default)`:** Jos kenttä on olemassa mallissa, käytä `obj.field`. Jos kenttä on valinnainen, käytä tyyppiä `T | None = None` ja käsittele `None` eksplisiittisesti (`if obj.field is not None:`).
3. **Piste-notaation ensisijaisuus:** `record.target_locale`, ei `record["target_locale"]`.
4. **Ei hiljaisia oletusarvoja pakollisille kentille:** Jos kieli tai ID on pakollinen, älä aseta sille oletusarvoa (`="en"`), vaan pakota kutsuja toimittamaan se (Fail-Fast).
5. **Tyypitetyt tilamuutokset:** Käytä DTO-rakenteita deltoissa sen sijaan, että palautat `dict[str, Any]`.
6. **Validaatio rajapinnassa (Gateway Validation):** Kaikki ulkoiset JSON- ja HTTP-syötteet validoidaan heti saapuessa Pydanticilla (`Model.model_validate(raw_data)`). Palvelukerroksessa data on aina jo validoitua oliotietoa.
7. **Repositorion tehtävä on palauttaa Pydantic Domain -malli (Repository Reconstitution Mandate):** Alin tietokanta-ajuri (`JSONFileDriver`) vastaa I/O-raakasanakirjoista, mutta Repositorio (`SystemRepository`, `WorkflowRepository`) rekonstruoi ja palauttaa aina suoraan vahvasti tyypitetyn Pydantic-mallin, jolloin palvelukerros välttyy toistuvilta `model_validate`-kutsuilta.
