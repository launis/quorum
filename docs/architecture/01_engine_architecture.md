# 10. Engine Architecture & Schema-Driven Routing

## Arkkitehtuuridokumenttien Roolijako (Lukemisopas)

Cognitive Quorum V2:n monimutkainen arviointi- ja pisteytysjärjestelmä on jaettu neljään eri dokumenttiin, joista jokainen vastaa tiettyyn kysymykseen:

* **Miksi?** Tämä dokumentti (`10_engine_architecture_and_schema_routing.md`) on ylätason konsepti. Se selittää *miksi* moottori eristää matematiikan LLM:stä (Tripartite) ja miksi järjestelmä ei luota dynaamisiin sanakirjoihin.
* **Miten?** Dokumentti `09_evaluation_and_scoring.md` kuvaa DINA-mallin ja CDM:n (Cognitive Diagnostic Model). Se kertoo *miten* se matematiikka ja rangaistukset fyysisesti lasketaan kaavojen tasolla.
* **Missä?** Dokumentti `04_hooks_and_llm.md` on toteutuskatalogi. Se kertoo *missä* tiedostoissa (esim. `scoring.py`, `integrity.py`) nämä ylätason säännöt fyysisesti asuvat ja mitä kyseiset funktiot tekevät.
* **Mitä?** Dokumentti `02_domain_models.md` on järjestelmän hermosto. Se kertoo *mitä* laatikkoja (Pydantic-rakenteet kuten `LightweightMatrixOutput` ja `ExecutionRecord`) tämä koko koneisto liikuttelee ja mihin muottiin data on pakotettava.

---


## Filosofia: Pelimoottori vs. Pelikenttä

Cognitive Quorum V2:n backend ei ole perinteinen, kovakoodattuja liiketoimintapolkuja suorittava monoliitti. Se on suunniteltu **Moottoriarkkitehtuurin (Engine Architecture / Rule Engine Pattern)** mukaisesti, jossa järjestelmä on jaettu kahteen täysin eristettyyn vastuualueeseen:

1. **Staattinen Moottori (Koodi):** Kiveen hakatut fysiikan lait ja turvarajat. Pydantic-mallit (esim. `GuardOutput`, `EvaluationResult`) ovat muuttumattomia (`frozen=True`) ja kieltävät kaiken ylimääräisen datan (`extra="forbid"`). Tämä vastaa pelimoottoria (esim. Unreal Engine).
2. **Dynaaminen Kenttä (Tietokanta):** Admin Studiosta käsin rakennettavat työnkulut, DAG-graafit (Directed Acyclic Graph), promptit ja askeleet (Steps). Nämä elävät `seed_data.json` -tietokannassa. Tämä vastaa pelikenttää, jota pelimoottori pyörittää.

Tämän erottelun ansiosta järjestelmä kykenee toteuttamaan **Zero-Deploy joustavuutta**: Pääkäyttäjä voi rakentaa loputtomasti uusia liiketoimintaprosesseja ja tekoälyagentteja tietokantaan, eikä ohjelmistokehittäjän tarvitse julkaista uutta koodiversiota, kunhan uudet askeleet noudattavat moottorin staattisia rajapintoja.

## Kaaoksen hallinta: Dynamic Schema Compilation ja TypeAdapter-pakotus

Tekoäly (LLM) on luonteeltaan vapaamuotoinen tekstin tuottaja. Jos sallisimme backendin logiikan muovautua dynaamisesti tietokannan ja LLM:n mukana, järjestelmä menettäisi tyyppiturvallisuutensa ja kaatuisi hiljaisesti (Silent Failures). 

Cognitive Quorum V2:n arkkitehtuuri ratkaisee tämän kaksivaiheisella **Dynamic Schema Compilation & Hook Interception** -mallilla. Se sitoo tietokannan vapauden tiukkaan koodiin ilman purkkaviritelmiä:

### Vaihe 1: Dynaamisen Pydantic-mallin kääntäminen lennosta (PromptCompiler)
Kun dynaaminen työnkulku ajetaan, järjestelmä ei kysy tietokannalta staattisen mallin nimeä. Sen sijaan koodi (PromptCompiler) lukee askeleeseen liitetyt arviointikriteerit (`PromptBlock`) ja rakentaa lennosta täysin uuden Pydantic-luokan (Dynamic Model). 

Palvelu päättelee liiketoimintalogiikasta rakenteen:
* **Output Extensions:** Jos kriteerille on aktivoitu Admin Studiossa `falsification`, luokkaan injektoidaan vaatimus: `step_2_falsification: str`. Jos `risk_flag`, vaaditaan `bool`.
* **Theory Grounding (Kirjallisuuslähteet):** Jos arviointi pohjautuu lakiin tai teoriaan, kääntäjä luo `Literal[<tarkka_lainaus>]` -kentän, joka **pakottaa** tekoälyn palauttamaan täsmälleen saman merkkijonon.
* Kääntäjä paketoi tämän `strict=True` ja `frozen=True` -luokaksi (Pydanticin `create_model` -funktiolla), jota tekoälyn on pakko noudattaa OpenAI:n Structured Outputs -rajapinnassa.

### Vaihe 2: Post-Hook TypeAdapter-sitominen
Jotta koko järjestelmän (pelimoottorin) integriteetti säilyy, dynaamisen mallin antama JSON-tulos täytyy vielä validoida järjestelmän staattisiin ydinmalleihin.

Suorituksen jälkeen LLM:n tuottama JSON-tulos ajetaan **Integrity Hookien** (esim. `verify_citation_integrity`) läpi. Näissä hookeissa käytetään Pydanticin `TypeAdapter`ia, joka "pakottaa" dynaamisen tuloksen kiveen hakattuun staattiseen luokkaan (esim. `EvaluationResult` tai `AnalystOutput`). Jos dynaaminen JSON ei vastaa ydinscheman tiukkoja minimivaatimuksia, validointi epäonnistuu välittömästi (Fail-Fast). 

*(Huom: Natiiveissa Python-logiikka-askeleissa (ei LLM) sidonta tehdään suoraan `TaskRegistry`n kautta koodissa `input_schema` / `output_schema` -määrityksillä.)*

## Tripartite Matrix Scoring (Matematiikan Eristäminen)

Moottoriarkkitehtuuri eristää myös LLM:n ja matemaattisen pisteytyksen toisistaan **Tripartite (Kolmiosaisella)** rakenteella. Tekoälyä ei koskaan päästetä keksimään numeerisia arvosanoja hatusta.

1. **Sokko-käännös (PromptCompiler):** Kun askeleessa on matriiseja (kriteereitä arvosanoilla), kääntäjä injektoi ne LLM:n promptiin `<EVALUATION_RUBRICS>` -lohkona. Samalla se injektoi ankaran `<ANTI_SCORE_MANDATE>` -käskyn, joka kieltää tekoälyä antamasta lopullista arvosanaa.
2. **Boolean-Kytkimet (LLM-suoritus):** LLM:n dynaaminen skeema pakottaa sen antamaan ainoastaan `True/False` -päätöksen (`step_5_boolean`) ja perustelun jokaista matriisin yksittäistä faktaväittämää kohden.
3. **Deterministinen Matematiikka (Scoring Hook):** JSON-tuloksen palattua `backend_v2/hooks/scoring.py` -tiedoston `matrix_scoring_hook` ottaa ohjat. Se lukee tekoälyn asettamat True/False -kytkimet ja laskee tarkan, deterministisen arvosanan (raw_score ja normalized_score) askeleen strategian perusteella. Lopuksi hook pakottaa sekä tulokset että lasketun matematiikan staattiseen `LightweightMatrixOutput` -domainmalliin.

Tämä takaa, että tekoäly toimii vain "sokeana liukuhihnatyöläisenä" etsien faktoja, kun taas lopullinen pisteytys tapahtuu 100% varmalla Python-koodilla sääntömoottorin sisällä.


## Arkkitehtuurikaavio

Alla oleva Mermaid-kaavio havainnollistaa, miten dynaaminen tietokanta (vasemmalla) muuntuu LLM-moottorin kautta staattiseksi, tyyppiturvalliseksi Pydantic-malliksi (oikealla).

```mermaid
graph TD
    subgraph "Dynaaminen Tietokanta (TinyDB/Firestore)"
        DB1["Workflow (Työnkulku)"]
        DB2["Step (Askel esim. stp_123)"]
        DB3["PromptBlock (Kriteerit, XAI Extensions)"]
        
        DB1 --> DB2
        DB2 --> DB3
    end

    subgraph "Moottori: Dynamic Compiler & Task Executor"
        E1(("PromptCompiler<br>(Dynamic Schema)"))
        E2["LLM Client<br>(Structured Output)"]
        
        DB3 -.->|Lukee metadatan| E1
        E1 -->|"1. create_model(strict=True)"| E2
    end

    subgraph "Moottori: Hook Interception & Registry"
        H1["Integrity Hooks"]
        H2{{"TypeAdapter<br>(AnalystOutput | EvaluationResult)"}}
    end

    subgraph "Staattinen Domain (Python/Pydantic)"
        M1["EvaluationResult"]
        M2["AnalystOutput"]
        M3["GuardOutput (TaskRegistry)"]
        
        M1 -.- M1a["frozen=True<br>extra='forbid'"]
    end
    
    E2 -->|2. Palauttaa raa'an JSONin| H1
    H1 --> H2
    H2 -->|3. Pakottaa staattiseen muotoon| M1
    H2 --> M2
    
    DB2 -.->|Logic Step (ei LLM)| M3
    
    M1 --> OUT[("Turvallinen, tyyppitarkastettu<br>Dynaaminen Suoritus")]
    M2 --> OUT
    M3 --> OUT

    style E1 fill:#81ecec,stroke:#00cec9,stroke-width:2px,color:#2d3436
    style H2 fill:#ffeaa7,stroke:#fdcb6e,stroke-width:2px,color:#2d3436
    style M1 fill:#55efc4,stroke:#00b894,stroke-width:3px,color:#2d3436
    style M1a fill:#ff7675,color:#fff
```

### Yhteenveto

"Duct tape" -purkkaviritys olisi sitä, että koodissa jouduttaisiin avaamaan sanakirjoja (`dict.get("score")`) ja yrittää onkia niistä lennosta muuttuvia kenttiä hiljaisin virhein. V2:n **Engine Architecture** tekee täsmälleen päinvastoin: se luo tiukan dynaamisen mallin askeleen kriteereistä lennosta (PromptCompiler), ja sen jälkeen Post-Hookit pakottavat (`TypeAdapter`) tulokset äärimmäisen kovaan ja rajalliseen joukkoon fyysisiä rakenteita (Domain Models). Tämä tarjoaa pelikentälle loputtoman variaation menettämättä pelimoottorin absoluuttista tyyppiturvallisuutta.

<br><hr>

➡️ **Seuraavaksi:** Kun moottorin filosofia on ymmärretty, siirry lukemaan [02_domain_models.md](./02_domain_models.md), joka listaa ne fyysiset Pydantic-laatikot, joita moottori liikuttelee.
