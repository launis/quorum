# Tietojen Hallinta ja Tietokannat

Tämä dokumentti kuvaa Cognitive Quorum -järjestelmän tiedonhallinnan arkkitehtuuria. Järjestelmä on **data-driven**, eli sen toimintalogiikka, kehotteet (prompts) ja työnkulut (workflows) on määritelty tietokannassa eikä kovakoodattu sovelluslogiikkaan.

## Datarakenne

Kaikki data sijaitsee `data/`-hakemistossa. Järjestelmä käyttää tiedostopohjaista lähestymistapaa, joka on helppo varmuuskopioida ja versioida.

### 1. Alustusdata (`data/seed_data.json`)

Tämä tiedosto toimii järjestelmän "tehdasasetuksina". Se sisältää:

*   **Komponentit**: Agenttien ja kehotteiden määritelmät.
*   **Vaiheet (Steps)**: Työnkulun yksittäiset vaiheet, niiden syöte- ja tuloskaavat (schemas) sekä suoritettavat Python-koukut (hooks).
*   **Työnkulut (Workflows)**: Miten vaiheet linkittyvät toisiinsa.

**Käyttö:**
Kun järjestelmä käynnistetään (tai tietokanta nollataan), `seed_data.json` luetaan ja sen sisältö viedään ajonaikaiseen tietokantaan. Tämä mahdollistaa järjestelmän logiikan muuttamisen pelkästään JSON-tiedostoa muokkaamalla.

### 2. Ajonaikainen Tietokanta (`data/db.json`)

Järjestelmä käyttää **TinyDB**:tä, joka on kevyt, dokumenttipohjainen tietokanta. `db.json` on tämän tietokannan fyysinen tiedosto.

Se sisältää kaksi päätyyppiä tietoa:
1.  **Konfiguraatio**: Kopio `seed_data.json`:n sisällöstä (komponentit, vaiheet, työnkulut). Tätä voidaan muokata ajonaikaisesti ilman koodimuutoksia.
2.  **Suoritushistoria (Executions)**: Jokainen ajettu analyysi tallennetaan tänne. Tämä sisältää:
    *   Käyttäjän syötteet.
    *   Jokaisen agentin tuottamat vastaukset ja välitulokset.
    *   Lopullisen raportin.
    *   Aikaleimat ja tilatiedot.

> **Huomio:** `db.json` voi kasvaa suureksi, koska se säilyttää kaiken historian.

### 3. Fragmentit (`data/fragments/`)

Tämä kansio sisältää uudelleenkäytettäviä tekstikatkelmia (JSON-muodossa), joita käytetään kehotteiden rakentamisessa.

*   `mandates.json`: Järjestelmän ylätason mandaatit (esim. "Järjestelmä 2 -ajattelu").
*   `rules.json`: Globaalit säännöt (esim. "Ei ulkoisia työkaluja ilman lupaa").
*   `criteria.json`: Arviointikriteerit (BARS-matriisi).
*   `protocols.json` & `methods.json`: Muut metodologiset ohjeet.

**Hyöty:** Fragmenttien avulla vältetään toistoa. Sama sääntö voidaan sisällyttää useaan eri kehotteeseen viittaamalla siihen, jolloin säännön muuttaminen yhdessä paikassa päivittää sen kaikkialle.

### 4. Mallipohjat (`data/templates/`)

Kansio sisältää **Jinja2**-mallipohjia (`.j2`), jotka määrittelevät agenttien kehotteiden rakenteen.

Esimerkiksi `prompt_analyst.j2` voi näyttää tältä:
```jinja2
{{ MASTER_INSTRUCTIONS }}

VAIHE 2: ANALYYTIKKO-AGENTTI
...
NOUDATA SEURAAVIA SÄÄNTÖJÄ:
{% for rule in rules %}
- {{ rule }}
{% endfor %}
```

Järjestelmä yhdistää ajonaikaisesti:
1.  `seed_data.json`:sta tulevan konfiguraation.
2.  `fragments/`-kansiosta tulevat säännöt.
3.  `templates/`-kansion mallipohjan.

Lopputuloksena on täydellinen kehote, joka lähetetään kielimallille (LLM).

### 5. Lataukset (`data/uploads/`)

Tämä on väliaikainen tallennuspaikka käyttäjän käyttöliittymän kautta lataamille tiedostoille (esim. PDF-dokumentit).

*   Tiedostot prosessoidaan (esim. tekstin irrotus PDF:stä).
*   Prosessoinnin jälkeen sisältö syötetään työnkulkuun.
*   Kansiota voidaan siivota automaattisesti tai manuaalisesti.

## Yhteenveto Tietovirrasta

```mermaid
graph TD
    subgraph Initialization
        Seed[seed_data.json] -->|Load| DB[(db.json)]
    end

    subgraph PromptEngineering
        Tpl[templates/*.j2] -->|Render| Prompt
        Frag[fragments/*.json] -->|Inject| Prompt
        DB -->|Config| Prompt
    end

    subgraph Execution
        User[User Input] --> Engine
        Uploads[data/uploads/*] -->|Process| Engine
        Prompt -->|Context| Engine
        Engine -->|Call| LLM[LLM API]
        LLM -->|Response| Engine
        Engine -->|Save History| DB
    end

    style DB fill:#f9f,stroke:#333,stroke-width:2px
    style LLM fill:#ff9,stroke:#333,stroke-width:2px
```
