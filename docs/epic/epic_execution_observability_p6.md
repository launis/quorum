# Epic P6: Execution Observability & Cache Optimization

## Lähtötilanne
Ajojen varianssia ja johdonmukaisuutta korjaava massiivinen "Execution Consistency" (P0-P5) -epic on saatu koodin osalta valmiiksi ja arkkitehtuuri on osoittautunut toimivaksi Pydantic-tason (Code-as-a-Judge, Schema Purity) suhteen.

Varianssitestin ensimmäinen ajo (`exe_add8965fdc7342c5950678fd9745dfb6`) paljasti kuitenkin kaksi merkittävää uutta pullonkaulaa:
1. **Forensinen Sokea Piste:** Järjestelmän tuottama `execution_trace.json` ei tällä hetkellä kirjaa lähetettyjä prommpteja (`LLM_PROMPT`). Vaikka koodi todistetusti rakentaa promptit oikein (esim. `SCHEMA_PURITY_MANDATE` ja `rule_anchor`), emme voi todistaa audit-lokista *mitä LLM tarkalleen näki*. Tämä estää varianssitilanteiden tarkan debuggaamisen jälkikäteen.
2. **Suorituskyky ja Caching:** Ajo kesti yli 22 minuuttia. Vaikka P4-hybridimalli optimoi token-käyttöä, pitkä kesto viittaa siihen, että ulkoisen LLM-providerin välimuisti (Prompt Caching) ei ota osumia. Todennäköisesti staattiseksi tarkoitettuun kontekstiin on vuotanut dynaamisia muuttujia, jotka rikkovat välimuistin avaimen jokaisella chunkilla.

## Tavoitteet
1. **100% Forensic Traceability:** Jokaisen suoritetun askeleen (Step) tarkka LLM-prompti on tallessa ja auditoitavissa jokaisen ajon dumpista.
2. **Cache Hit Rate > 90%:** Järjestelmä pystyy hyödyntämään tehokkaasti LLM-providerien (esim. Anthropic/Vertex) välimuistia, laskien suoritusajan 22 minuutista murto-osaan.

## Toteutettavat Tehtävät

### 1. Execution Trace Prompt Logging (Forensics)
**Ongelma:** `LLMTaskExecutor` tai DAG-moottori ei vie injektoituja prommpteja lopulliseen lokiin.
**Ratkaisu:** 
- Päivitetään ajomoottoria (`chunk_worker.py` / `worker.py`) siten, että jokaisesta LLM-kutsusta tallennetaan puhdas `LLM_PROMPT` -tapahtuma `execution_trace` -listaan.
- Vaihtoehtoisesti (JSON-tiedoston koon pitämiseksi maltillisena), promptit voidaan tallentaa suoraan ajodumpin `inputs/` -hakemistoon erillisinä tekstiedostoina (esim. `inputs/step_X_chunk_Y_prompt.md`).
- Varmistetaan, että tallennettu data sisältää tismalleen sen string-formaatin, joka lähetettiin API:lle, sisältäen kaikki XML-tägit ja ankkurit.

### 2. API Cache Observability & Metrics
**Ongelma:** Emme tiedä kuinka paljon välimuistia hyödynnetään.
**Ratkaisu:**
- Laajennetaan LLM-rajapinnan (esim. Vertex AI -integraatio) metadatan keruuta poimimaan providerin palauttamat välimuisti-osumat (`cached_content_token_count` tai vastaava).
- Nämä luvut on syötettävä suoraan atomin `profiler_metrics` tai `step_metadata` -objektiin, jotta niitä voidaan seurata `execution_trace.json`:sta.

### 3. Prompt Caching vuotojen tukkiminen (Optimization)
**Ongelma:** Välimuisti ei toimi, koska dynaaminen data (kuten chunk_id tai satunnaiset muuttujat) injektoidaan staattisen järjestelmäpromptin tai asiakirjakontekstin sisään.
**Ratkaisu:**
- Auditoidaan `compile_xml_rubrics` ja `context_builder.py` varmistaen, että dynaamiset muuttujat asuvat *vain* promptin lopussa erillisessä `<execution_parameters>` -lohkossa (Rule 29: `high_fidelity_prompting`).
- Puhdistetaan staattinen osa täysin, jotta API-caching toimii odotetusti peräkkäisissä chunkeissa.

## Arkkitehtuuriset Rajoitteet (Hardening Mandates)
- **Forensic Boundary Protocol:** Kaikki LLM-vuorovaikutus on kyettävä toistamaan identtisesti auditoinnin aikana. Sokeita pisteitä ei sallita.
- **Rule 52 (`ephemeral_caching_topology`):** System Prompts must remain 100% static to maximize ephemeral prompt caching hit rates.
- **Rule 29 (`high_fidelity_prompting`):** Dynamic execution variables MUST be isolated within an `<execution_parameters>` tag at the tail of the message.
