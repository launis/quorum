# Pro-mallin (`gemini-2.5-pro`) kustannus- ja token-analyysi

Tarkistin järjestelmän ydinasetukset (`backend_v2/seed/seed_data.json`). Kallis Pro-malli on kiinnitetty seuraaviin avainstrategioihin:
1. **`deep`**: Käytetään todennäköisesti raskaaseen analytiikkaan ja maadoitusta vaativiin hakuihin (`supports_grounding: true`).
2. **`synthesis`**: Käytetään loppuraportin ja synteesin tuottamiseen.
3. **`precise` & `strict`**: Käytetään tiukkaan sääntöpohjaiseen validointiin.

## Miksi Pro-malli syö niin valtavasti tokeneita?
1. **Toistuva lähdedatan skannaus:** Jokainen matriisi/steppi saa syötteenään (`$inputs`) koko alkuperäisen datan (`Chat_Log`, `Product_Text`, jne.). Jos näitä steppejä ajetaan rinnakkain useita, massiivinen lähdedata monistuu jokaiseen LLM-kutsuun.
2. **Massiiviset järjestelmäpromptit:** Quorumin arkkitehtuuri luo dynaamisesti erittäin laajoja "Thick XML" -rubriikkeja ja monimutkaisia Pydantic JSON Schema -rakenteita.
3. **Mekaaninen työ raskaalla mallilla:** Kuten aiemmin huomasimme, LLM tekee paljon mekaanista "etsi tämä sana ja palauta lainaus" -työtä. Pro-mallin käyttäminen tällaiseen "regex-tyyppiseen" hakuun on kuin käyttäisi ydinpommia kärpäsen tappamiseen.

---

## 4 Kehitysehdotusta (Kustannusoptimointi ilman laadun heikkenemistä)

### 1. Hybridimalli: Mekaniikka Flashille, Aivot Prolle (Suositus #1)
- **Ongelma:** Käytätte tällä hetkellä Pro-mallia luultavasti sekä sääntöjen tarkistamiseen (Matrix-atomit) että loppusynteesiin.
- **Ratkaisu:** Koska huomasimme aiemmin, että sääntöjen tarkistus on erittäin mekaanista, **siirtäkää kaikki Matrix-tason validoinnit `fast` (Flash) -strategialle**. Flash on salamannopea ja halpa etsimään lainauksia. **Pitäkää `synthesis`-strategia Pro-mallissa.** Näin halpa malli tekee raskaan tekstin louhinnan, ja kallis malli saa eteensä valmiit lainaukset (`evaluations`) ja kirjoittaa niistä upean loppuraportin. Kustannukset romahtavat, mutta lopputuloksen laatu pysyy samana!

### 2. Prompt Caching -strategian optimointi
- **Ongelma:** Asetuksissa on päällä `"caching_strategy": "prompt_caching"`. Jotta tämä säästää rahaa (esim. Gemini Context Caching), promptin alkuosan on oltava *täsmälleen sama* eri kutsuissa. Jos dynaaminen JSON Schema tai `atom_id` on promptin alussa, välimuisti "hutiutuu" (cache miss) joka kerta ja maksatte täyden hinnan.
- **Ratkaisu:** Varmistakaa, että raskas lähdedata (`source_data`) ja muuttumattomat XML-rubriikit injektoidaan promptin aivan alkuun, ja dynaamiset säännöt vasta aivan loppuun. Tämä voi nostaa välimuistin osumatarkkuuden 90 %:iin, mikä pudottaa input-tokenien hinnan murto-osaan.

### 3. Matriisien Aggregointi (PromptBlock Fusion)
- **Ongelma:** Jos jokainen "sääntö" tai "atomi" lähetetään omana LLM-kutsunaan, järjestelmäprompti ja lähdedata lähetetään kymmeniä kertoja uudelleen.
- **Ratkaisu:** Varmistakaa, että `PromptCompiler` pakkaa mahdollisimman monta atomia yhteen ja samaan kutsuun (JSON array of evaluations). Yksi kutsu, joka palauttaa 10 atomin analyysit, on kertaluokkaa halvempi kuin 10 erillistä kutsua. (Tämä vaikutti jo olevan osittain käytössä, mutta aggregaatiotasoa voi nostaa).

### 4. Välitulosten karsiminen (Data Pruning)
- **Ongelma:** Synteesi-hook saa tällä hetkellä koko valtavan `execution_trace.json` -historian luettavakseen.
- **Ratkaisu:** Sen sijaan, että synteesi-LLM:lle syötetään kaikki matriisien raakadata, luokaa kevyt "Data Pruner" -hook (ajetaan Flashilla), joka tiivistää matriisien tulokset, tai filtteröikää kooditasolla pois kaikki ne atomit, joiden `exact_quote` on `null`. Turhan datan poistaminen synteesipromptista säästää suoraan Pro-mallin tokeneita.
