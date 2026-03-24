# Arkkitehtuurisuunnitelma V3: Puhdas Työnkulku-Orkestraatio (WorkflowState & StateDelta)

**Tila:** Ehdotus (V3)
**Konteksti:** Cognitive Quorum Backend - Hook-arkkitehtuurin tiukentaminen
**Ongelma jota ratkaistaan:** Dynaamisten DAG-työnkulkujen (V2) joustavuus saavutettiin välittämällä tila asynkronisille Hook-komponenteille löyhänä `dict[str, Any]` -sanakirjana. Tämä salli Hookien mutatoida tilakonetta (Context) suoraan, mikä rikkoo "Fail-Fast" -validointirajapinnat, heikentää forensiikka-lokitusta ja luo alttiuden piilotetuille sivuvaikutuksille (esim. kriittisten datakenttien tahaton ylikirjoittaminen).

---

## 1. Arkkitehtuurin Ydinkonsepti (Functional Core)

Siirtyminen V3-aikakaudella vahvasti tyypitettyyn, muuttumattomaan (immutable) tilaan, jossa moottori (Orchestrator) hallitsee yksinoikeudella tilapäivityksiä vähennysfunktion (Reducer) tavoin. Hookeista tehdään "puhtaita funktioita" (Pure Functions).

### 1.1 Vahva Pydantic-tila (`WorkflowState`)
Nykyinen `context: dict[str, Any]` korvataan eksplisiittisellä Pydantic-mallilla. Myös dynaamiset avaimet sallitaan (esim. `extra="allow"` -konfiguraatiolla), mutta ydinrakenteet (`chat_log`, `results`, `metadata`) ovat tiukasti tyypitettyjä ja kääntöaikana suojattuja sivuulottuvuuksia vastaan.

### 1.2 Mutaatioiden Kieltäminen (`StateDelta`)
Hook-komponenteille välitetty `WorkflowState` on **syväjäädytetty (frozen)**.
Jos Hook (esim. `sanitize_text`) haluaa muuttaa ajon aikaista tilaa, se ei voi suorittaa operaatiota `state["chat_log"] = new_text`. 

Sen sijaan Hookin **täytyy palauttaa** uusi Pydantic-rajapinta, `StateDelta`.

```python
class StateDelta(BaseModel):
    """Edustaa yhtä atomista muutosta työnkulun tilaan."""
    updated_keys: dict[str, Any] = Field(default_factory=dict)
    deleted_keys: list[str] = Field(default_factory=list)
    metadata_log: str | None = Field(default=None, description="Forensiikka-lokitus muutoksen syystä")
```

### 1.3 Orkestraattori Päättäjänä (Reducer)
Vain workflow-moottori itse saa suorittaa tilamuutoksen.
Moottorin suoritusloki näyttää konseptuaalisesti tältä:

```python
for hook in node.hooks:
    # 1. Suorita puhdas funktio luku-tilalla
    delta: StateDelta = await hook.execute(frozen_state)
    
    if delta:
        # 2. Kirjaa forensiikka/audit-loki
        logger.info(f"[Orchestator] Hook {hook.name} mutated keys: {list(delta.updated_keys.keys())}")
        
        # 3. Yhdistä (Merge) delta uuteen tilaan
        frozen_state = merge_state(frozen_state, delta)
```

---

## 2. Hyödyt Quorum-järjestelmälle

Tämä arkkitehtuuri palvelee suoraan Quorumin alkuperäistä missiota: *Mustan laatikon tekoälyn purkamine täydelliseen läpinäkyvyyteen*.

1. **Jäljitettävyys kooditasolla (Auditability):** Suoritushistoriasta (`ExecutionRecord`) pystytään aukottomasti todistamaan, *kuka* agentti tai skripti muutti tilamuuttujaa `$inputs.X` milläkin sekunnilla. 
2. **Turvallinen Laajennettavuus:** Kun luodaan uusia, ulkopuolisia Hookeja (esim. web-haut tai MCP-työkalut), ne eivät voi rikkoa ohi rajapintojen kriittistä V2 Core -tilaa (esim. token_usage tai result_storage_path).
3. **Automatisoitu testaus:** Puhtaiden funktioiden testaaminen on triviaalia. `test_hook(MockState) -> StateDelta`. In-place mutaatioiden poistaminen poistaa tilariippuvaiset "Flaky"-testit välittömästi.

---

## 3. Implementaatiopolku (Vaiheistus V3)

Tämä muutos on laaja ja koskee koko `engine/reporting_hook_hoisting.py` -orkestraatiota. Implementaatio tulisi eristää omaksi Milestonekseen seuraavasti:

* **Finaali 1 (Skeemat):** Määrittele `v2_core.py`:een `StateDelta` ja `WorkflowState` (joka eristää dynaamiset inputit `extra_data` -kenttään).
* **Finaali 2 (Työkalupäivitys):** Refaktoroi V2-järjestelmän nykyiset 15+ Hookkia palauttamaan Delta. Useimmat nykyisistä Hookeista vain palauttavat päivitetyn arvon moottorille ja orkestraattori hoitaa sijoituksen, mutta monimutkaisemmat list-append -operaatiot (kuten citation_integrity) vaativat selkeän `Delta.updated_keys = {"citations": new_list}` palautuksen.
* **Finaali 3 (Moottorin päivitys):** Päivitä `execute_node_hooks` -funktio `Reducer`-logiikalla ja kytke Logfire/Arkkitehtuurilokitus seuraamaan avainten muutoksia.
