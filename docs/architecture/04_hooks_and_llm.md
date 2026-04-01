# 04: Natiivit Hookit ja Kieli-integraatiot (LLM)

Quorum V2:ssa puhtaat työnkulkujen kognitiiviset lisäosat ja ulkoiset tekoälyintegraatiot on eriytetty vahvasti `hooks/` ja `llm/` kerroksiin. Tämä mahdollistaa deterministisen laadunvarmistuksen ohi LLM:n mustan laatikon hallusinaatioiden.

## The Hook Layer (`backend_v2/hooks/`)

Natiivit Python-koukut (Hooks) ovat tilattomia funktioita, joita työnkulun solmut kutsuvat ennen (Pre-Hook) tai jälkeen (Post-Hook) varsinaisen LLM-kutsun. Hookeilla on pääsy työnkulun siihenastiseen `HookState`-kontekstiin ja ne on rekisteröity järjestelmään `hook_registry.py`:n kautta.

```mermaid
sequenceDiagram
    participant Dag as DAGExecutor
    participant Pre as Pre-Hooks (input_processing)
    participant Compiler as prompt_compiler.py
    participant LLM as LLM Client (REST)
    participant Post as Post-Hooks (scoring.py)

    Dag->>Pre: Aloita solmu (HookState)
    activate Pre
    Pre->>Pre: Eager Extraction & Document Parsinta
    Pre-->>Dag: Puhdistettu Context
    deactivate Pre
    
    Dag->>Compiler: Renderöi Jinja2 Prompt
    Compiler-->>Dag: Rakennettu Prompt + JSON Schema

    Dag->>LLM: Async Kutsu (Structured Output)
    activate LLM
    LLM-->>Dag: Raaka vastaus (Pydantic Strict Object)
    deactivate LLM
    
    Dag->>Post: Syötä JSON Post-Hookiin
    activate Post
    Post->>Post: Micro-CoT Flattening (_quote, _falsification)
    Post->>Post: Math Scaling & Normalization (1-100)
    Post->>Post: Algorithmic Tyranny / Passivity Checks
    Post-->>Dag: Rankastu & Normalisoitu Lopullinen DTO
    deactivate Post
```

### Keskeisimmät Hook-vastuut

1. **Scoring ja Arviointien Normalisointi (`scoring.py`):**
   * **Micro-CoT (Chain of Thought) Litistäminen:** V2 LLM vastaa tyypillisesti monivaiheisella syy-seuraus -verkolla (esim. Quote -> Falsification -> Score). Hook purkaa (`flatten`) nämä monimutkaiset rakenteet kooditasolla atomaarisiksi `_cited_text_quote` ja `_falsification` Data-avaimiksi XAI (Explainable AI) UI-komponenteille.
   * **Nollalaskenta (Zero-Math UI):** Muuntaa karkeat AI:n antamat numeeriset matriisitulokset natiivisti `_scaled` ja `_normalized` (1-100%) arvoiksi, varmistaen ehdottoman yhteneväisen matemaattisen vertailupohjan kaikkien moduulien välille.
   * **Algorithmic Tyranny Kill Switch:** Suojamekanismi, joka tarkkailee generoituja arvoja (esim. `control_ratio` ja sanaston monimuotoisuus). Jos tekoäly tuottaa monotonista huipputulosta ilman variaatiota, hook devalvoi täysin solmun pisteet ja asettaa lokiin "Kill Switch" rangaistuksen.
   * **Passivity Penalty:** Havaitsee tilanteet, joissa LLM valitsee järjestelmällisesti arviointiasteikon pienimmän vaivan tien (minimi score), jolloin tekoälylle annetaan matemaattinen rangaistuskerroin.

2. **Integriteetti ja Turvallisuus (`integrity.py` & `security.py`):**
   * Validointihookit, jotka pysäyttävät suorituksen, jos sisältö osuu estettyihin avainsanoihin tai jos kognition palauttamat lainaukset (Citations) eivät täsmää alkuperäiseen dokumenttiin (Source Hallucination).

3. **Informaation Pre-prosessointi (`input_processing.py`):**
   * Huolehtii mm. massiivisten PDF/Word -tiedostojen ennakkojaottelusta, metatiedustelusta ja normalisoinnista "Eager Extraction" -malliin ennen kalliita LLM-kutsuja.

## Tekoälyintegraatiot (`backend_v2/llm/`)

Kieli-integraatiokerros erottaa ulkoiset mallintarjoajat (Vertex AI, OpenAI) järjestelmän sisäisestä asynkronisesta ytimestä.

### Rakenne ja Validointi

* **`client.py` & `provider.py`:** Huolehtivat rajapintatason (HTTP) kommunikaatiosta, asynkronisista aikatasauksista (Retry/Rate Limit) sekä erilaisten mallien `Parsing Mode`ista (esim. JSON Structured Output -pakotukset `GEMINI_JSON` modessa).
* **`schema_builder.py`:** Generoi natiivista Pydantic V2 `Step.output_schema` määrityksestä lennossa tekoälylle tarkan JSON-skeeman (Function Calling / Structured Output). Pakottaa LLM:n rakentamaan syntaktisesti 100% oikeaa objektidataa.
* **Abstraktion pakotus:** LLM-moduulit *eivät koskaan* rakenna työnkulun dynaamisia prompteja itse. Promptsien Jinja2-kokoaminen ja teoria-aineistojen injektointi suoritetaan erillisessä raskaassa `prompt_compiler.py` Service-kerroksen aggregaatissa, minkä jälkeen valmis tekstinäyte tarjoillaan LLM-klientin suoritettavaksi. Tämän säännön avulla yksittäisen LLM-toteutuksen voi korvata hetkessä toisella (esim. Vertex AI -> Anthropic) ilman minkäänlaisia muutoksia kognitiivisen logiikan reititykseen.
