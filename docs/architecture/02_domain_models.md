# 02: Pydantic V2 Datamallit ja Verkkotopologia (Domain)

Cognitive Quorum rakentuu vahvasti tyypitettyjen, "Fail-Fast" periaatetta noudattavien Pydantic V2 -mallien varaan. Nämä mallit muodostavat backendin hermoston (Single Source of Truth), johon koko järjestelmän toiminta (FastAPI-reititys, tietokantamuutokset ja käyttöliittymän renderöinti) perustuu.

## V2CoreBase ja Tiukka Validointi (Strict Nirvana)

Kaikki järjestelmän ydinmallit perivät `V2CoreBase`-luokan. Tämä asettaa arkkitehtuurille ehdottoman tiukat säännöt, joilla estetään "hiljaiset virheet" ja kognition lipsuminen vuotavien rajapintojen läpi.

```python
class V2CoreBase(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
```

1. **Rust Core Parsing:** FastAPI-reitittimissä JSON puretaan suoraan `model_validate_json()` -metodilla, hyödyntäen Pydantic V2:n Rust-moottoria ohi hitaiden Python-kirjastojen.
2. **Extra='forbid':** Jos käyttöliittymä, LLM tai taustajärjestelmä lähettää malliin kuulumatonta (esim. hallusinoitua tai vanhentunutta) dataa, koodi kaatuu välittömästi (Validation Error 422). Järjestelmä ei koskaan niele tuntemattomia avaimia.
3. **No-String Mandate (I18nText):** Kaikki käyttöliittymään päätyvä teksti on kapseloitu `I18nText` Pydantic-malliin. Se pakottaa ("English-Only Mandate"), että kaikesta tekstistä löytyy englanninkielinen perusversio, johon kieli-middleware voi nojata silloinkin kun käännös puuttuu. Tekoälyn kognitiiviset ohjeet puolestaan eristetään yksinomaan englanninkielisiin `ai_description` -kenttiin UI-lokalisaatiosta irralliseksi.

## Ydinmallisto ja Opaque ID -reititys

Järjestelmä hylkää ihmisluettavat "slugit" identifioijina taustalogiikassa. Kaikki relaatiot ja datamallit pakottavat joustavan "Opaque Stripe ID" -reitityksen (esim. `blk_abc12345`), joka takaa sen, että mallien sisäiset ihmisluettavat nimimuutokset eivät koskaan riko järjestelmän topologiaa.

```mermaid
classDiagram
    class V2CoreBase{
        <<Pydantic>>
        +ConfigDict strict=True
        +ConfigDict extra="forbid"
        +model_validate()
    }

    class I18nText{
        +String en
        +String fi
    }

    class Workflow{
        +String id (Opaque Stripe ID 'wor_')
        +List~StepRule~ steps
        +validate_dag_integrity()
    }

    class StepRule{
        +String task_blueprint (Opaque Step ID 'stp_')
        +int ui_pos_x
        +int ui_pos_y
        +List~String~ depends_on
        +dict input_mappings
    }
    
    class Step{
        +String id
        +String type
        +List~String~ prompt_blocks
    }

    class PromptBlock{
        +String id (Opaque Block ID 'blk_')
        +I18nText content
        +String ai_description
        +List~MatrixScale~ scales
        +validate_block_consistency()
    }

    class ExecutionRecord{
        <<Event Sourcing Root>>
        +String id
        +String status
        +ConfigDict frozen=True
        +FrozenContext frozen_context
        +List~TraceEvent~ execution_trace
    }

    V2CoreBase <|-- I18nText
    V2CoreBase <|-- Workflow
    V2CoreBase <|-- StepRule
    V2CoreBase <|-- Step
    V2CoreBase <|-- PromptBlock
    V2CoreBase <|-- ExecutionRecord

    Workflow *-- StepRule : "sisältää (Opaque DAG Nodes)"
    StepRule --> Step : "viittaa (Blueprint Reference)"
    Step --> PromptBlock : "fuusioi kognition"
```

### Keskeiset Arkkitehtuuriset Kokonaisuudet

1. **PromptBlock (Unified Directive Model):**
   * Työnkulun pienin atomaarinen osa. Tämä malli fuusioi sisäänsä arviointimatriisit (BARS, Bipolar), odotetut datatyypit sekä tekoälyn suoritusohjeet (`ai_description`).
   * Validointi (`validate_block_consistency`) pakottaa raskailla säännöillä sen, että matriisin min/max -arvot ja niihin linkitetyt asteikot (MatrixScale) ovat strukturaalisesti virheettömiä ja johdonmukaisia ennen tallennusta.

2. **Step ja StepRule (Opaque Nodes):**
   * **Step:** Eristetty, uudelleenkäytettävä logiikkamalli (esim. koodin ajo, MCP Tool -kutsu tai LLM-agentti). Määrittelee sallitut MCP-työkalut ja reititysstrategian.
   * **StepRule:** Määrittelee solmun todellisen paikan työnkulun verkossa (Directed Acyclic Graph). Sisältää UI-koordinaatit (`ui_pos_x`, `ui_pos_y`), riippuvuudet (`depends_on`) ja datan syötelokeroinnin (`input_mappings`), joilla muiden askelten injektoimat lokaalit syötteet parsitaan LLM:lle.

3. **Workflow (DAG Orchestrator):**
   * Kokoaa yhteen StepRulet, PromptBlockien viittaukset sekä Output Profilet.
   * Järjestelmä estää puutteelliset Workflown tilat ennen ajoa: `validate_dag_integrity` suorittaa Depth-First Search (DFS) -algoritmin, joka paljastaa työnkulun solmukohdista syklit (kehät) pystyen katkaisemaan suorituksen (RFC 7807) ennen ajon alkua. Se on absoluuttinen vaatimus turvalliselle asynkroniselle taustaprosessoinnille.

## Suoritusmallit ja Event Sourcing

Työnkulun ajanhetkellinen tila ja lopullinen valmis raportti tallennetaan tiukkaan Event Sourcing -malliseen arkkitehtuuriin.

1. **ExecutionRecord:** Tallentaa tekoälyajon koko elinkaaren. Se lukitsee sisäänsä tarkan `FrozenContext` kopion kaikista siinä hetkessä käytetyistä PromptBlockeista ja säännöistä. Tämän konseptin ansiosta kone pystyy kuukausia myöhemmin selittämään tarkasti, miksi tekoäly on tietyt päätökset tehnyt (Explainable AI / Forensic Sovereignty).
2. **TraceEvent & MCPAuditTrace:** Työn lennossa, taustaprosessi lähettää atomisia `TraceEvent`-objekteja tilanteesta tietokantaan. Samalla kaikki Vertex AI-hakujen tai vastaavien ulkoisten MCP-työkalujen haut tallentuvat `MCPAuditTrace`-jäljeksi lokiin. Mahdollistaa deterministisen UI-piirron jälkikäteen ilman järjestelmän sisäisiä muistitiloja.
