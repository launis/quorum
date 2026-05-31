# Epic: Provider-Agnostic Context Caching Hardening (Token Proxy Score)

Tämä Epic korjaa arkkitehtuurisen "Anti-TDD / Duct Tape" -riskin Vertex AI:n välimuistinhallinnassa. Nykyinen 130 000 merkin staattinen heuristiikka on liian hauras ja voi johtaa Fail-Fast -säännön rikkoutumiseen (väärät positiiviset) tai säästöjen menettämiseen (väärät negatiiviset). Ratkaisuna siirrämme vastuun `InputProcessingHook`:ille, joka vakioi datan ja tuottaa älykkään `Token Proxy Scoren` kaikille järjestelmään syötetyille teksteille.

## User Review Required

> [!WARNING]
> **Arkkitehtuurinen Muutos**
> Tämä muutos tekee `InputProcessingHook`:ista (pre-flight) pääasiallisen vastuunkantajan tekstin pituuden arvioinnissa, jotta LLM-adapterien ei tarvitse arvailla. Onko `estimated_token_count` tarkoitus tallentaa suoraan tietokannan `execution`-dokumentin metatietoihin, vai syötetäänkö se ajonaikaisesti Workflow-moottorin (DAG) stateen (esim. `step_metadata`)?

## Open Questions

> [!IMPORTANT]
> **Sanalaskennan Kerroin ja Monikielisyys**
> Suunnitelma ehdottaa dynaamista kerrointa (esim. `sanojen_määrä * 1.5` englannille ja `sanojen_määrä * 1.8` suomelle), koska suomi on agglutinoiva kieli, joka tuottaa tiheämmin tokeneita per sana. Tulisiko `InputProcessingHook`:in suorittaa nopea O(1) kielen tunnistus (esim. hyödyntäen nykyistä `SystemLocale` -asetusta), jotta Token Proxy Score on aidosti kielitietoinen ja tarkka eri markkinoilla? Mikä laskentatapa katsotaan riittävän tarkaksi Quorum Phase 9 -standardien valossa?

## Proposed Changes

---

### Backend: Hooks & Normalization

Vastuu keskitetään Y-Funnelin alkuun.

#### [MODIFY] `backend_v2/hooks/input_processing.py`
- **Uusi ominaisuus:** Laajennetaan hook käsittelemään **kaikki** syötteet, ei pelkästään chat-lokeja. Jokainen teksti käy läpi whitespace-normalisoinnin.
- **Kielitietoinen Token Proxy Score:** Lisätään funktio, joka laskee siivotusta tekstistä nopean arvion huomioiden monikielisyyden (esim. `len(text.split()) * multiplier`, missä kerroin mukautuu kielen mukaan). Suomen kielen tiheämpi token-rakenne otetaan huomioon väärän negatiivisen riskin minimoimiseksi.
- **Injektio:** Tallennetaan tämä luku inputin metatietoihin (esim. `ai_description` -rakenteen rinnalle tai osaksi `StepMetadataa`), jotta se kulkee deterministisesti DAG:n mukana.

---

### Backend: LLM Adapters

Poistetaan purkkaviritelmä (duct tape) ja siirrytään data-ohjattuun logiikkaan.

#### [MODIFY] `backend_v2/llm/adapters/vertex_adapter.py`
- **Muutos:** Poistetaan koodista logiikka `if total_static_chars < 130000`.
- **Korvaus:** Adapteri lukee `estimated_token_count` -arvon suoraan promptin metatiedoista. 
- **Logiikka:** `if estimated_token_count < 32768: bypass caching`. Tämä takaa, että välimuistia yritetään vain silloin, kun kynnys oikeasti ylittyy.

---

## Verification Plan

### Automated Tests
- Päivitetään ja luodaan uusia `pytest`-yksikkötestejä `input_processing.py`:lle, jotka varmistavat, että tyhjää tilaa sisältävä data saa realistisen token-arvion.
- Luodaan Mock-testi `VertexCacheAdapter`:ille, joka varmistaa, että se ohittaa välimuistin oikein kun `estimated_token_count < 32768`, riippumatta tekstin merkkimäärästä.
- Tarkistetaan muutokset komennolla `uv run python scripts/backend_audit_loop.py backend_v2/hooks/input_processing.py backend_v2/llm/adapters/vertex_adapter.py --test`

### Manual Verification
- Aja `run_local.bat` ja syötä sama Sitran testikeissi.
- Tarkista `backend_debug.log`:sta, että Vertex AI Adapter lukee metatiedosta tarkan Token Proxy Scoren ja ohittaa välimuistin ilman merkkimäärään perustuvaa arvailua.
