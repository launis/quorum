# Epic 5: Natiivi LLM Context Caching (Gemini 2.5 & Anthropic)

**Tila:** Suunniteltu (Maaliskuu 2026)
**Konteksti:** Quorum V2 Backend & Event Sourcing Engine

## Tavoite
Pudottaa LLM-kustannuksia jopa 90 % pakottamalla raskaat asiantuntijaohjeet (matrices & static instructions) ilmaiseen Context Caching -välimuistiin. Samalla korjataan V2-moottorin tunnistettu bugi, joka aiemmin unohti `instruction`-tyyppiset promptit kokonaan sallituista LLM-kutsuista rakentaessaan pelkkiä Pydantic-skeemoja.

## Vaihe 1: Arkkitehtuurin "Kategoriointi" (Tietokanta)
*   **Ongelma:** Jos yksikään järjestelmän prompti sisältää vaihtuvan sanan (esim. sekunnintarkka kellonaika), koko asiantuntijalogikka (satoja tuhansia sanoja) tipahtaa välimuistista ja joudutaan lukemaan alusta joka kerta.
*   **Ratkaisu (Toteutettu):** Luotiin uusi kategoria `runtime_variables` olemassa olevaan `data/db_v2.json` -kantaan. Siirrettiin kelloa ja päivää käsittelevät promptit (esim. Prompt 34) tähän kategoriaan. Jäljelle jääneet tyypin `instruction` promptit (kuten `agent_role` tai `system_rule`) pysyivät omissa staattisissa lokeroissaan.

## Vaihe 2: Kehä 1 – Kääntäjän elvytys (`prompt_compiler.py`)
Ohjemassan tekstikääntäjä herätetään takaisin henkiin luomalla kaksi uutta reittiä:
*   **Reitti A (Staattiset Ohjeet):** Kääntäjä poimii kaikki tietokannasta tulevat promptit, joiden `type: instruction` ja joiden `category_id` **EI** ole `runtime_variables`. Nämä vain liimataan yhteen isoksi sääntökirjaksi.
*   **Reitti B (Dynaamiset Ohjeet):** Kääntäjä poimii promptit, joiden `category_id == runtime_variables`. Se avaa niiden tekstin auki ja etsii sieltä koodisanat (kuten `{{CURRENT_DATE}}` tai `{{DYNAMIC_TIME}}`) ja korvaa ne lennosta palvelimen sekunnintarkalla kellonajalla.

## Vaihe 3: Kehä 2 – Moottorin ohjaus ja Välimuistitus (`dag_executor.py`)
Moottori kutsuu kääntäjää ja asettaa palat oikeille paikoilleen:
1.  **The Head (System Prompt):** Moottori laittaa koko Raskaan Matriisipaketin ja Reitti A:sta tulleet "Staattiset Ohjeet" tänne System Promptiin täysin sellaisenaan. Tämä takaa sen, että koko asiantuntijalogikka pysyy matemaattisen staattisena päivästä toiseen, jolloin Anthropic ja Gemini antavat sille **Context Caching -välimuistialennuksen**.
2.  **The Cache Instruction:** Rakennetaan Anthropic-yhteensopiva `cache_control: {"type": "ephemeral"}` injektio dokumenttisyötteiden perään, jotta raskaat potilas/asiakirjatekstit menevät myös ilmaiseen välimuistiin.
3.  **The Tail (User Prompt):** Moottori sijoittaa aivan viestin perälle, kaiken muun jälkeen Reitti B:stä tulleen laatikon `"--- RUNTIME AWARENESS ---"`. Tässä laatikossa sykkii nyt sekunnintarkka päivämäärä (Promptista 34) ja Execution ID. Koska tämä on viestin lopussa, se ei riko alkuosan välimuistia koskaan!

## Vaihe 4: Raportointi (`backend_v2/llm/client.py`)
*   Datahubiin ja lokeihin asennetaan "Säästömittari". Kun LLM-palvelin ilmoittaa lukeneensa tokenia suoraan välimuistista (`cached_tokens`), järjestelmä kykenee tunnistamaan, kuinka monta millisenttiä kognitiivista työtä säästyi uuden arkkitehtuurijohdonmukaisuutemme ansiosta.
