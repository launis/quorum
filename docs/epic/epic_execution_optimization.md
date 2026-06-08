# Epic: LLM Execution Persona & Poimintaprotokollien Optimointi (Kustannus & Tehokkuus)

**Dokumentin tarkoitus:**
Tämä epic-dokumentti analysoi ja ratkaisee havaitun kustannusvuodon Quorum-arkkitehtuurissa. Lähes 60 % yhden monimutkaisen työnkulun (esim. Megatrendi-analyysien) LLM-kustannuksista kuluu tällä hetkellä "reasoning-tokeneihin" (Chain-of-Thought), joiden tuottaminen 2.5 Flash / 3.5 Flash -malleilla on kallista ja usein tarpeetonta rutiinipoiminnoissa.

---

## 1. Tarve, syy ja käyttötapaukset

Quorum on tiukkaan Pydantic-validointiin perustuva järjestelmä ("Fail-Fast"). Roolien ja protokollien tehtävä on rajoittaa ja sitoa kielimallin luontaista arvaamista (hallusinointia).

*   **Execution Persona:** Määrittää järjestelmätason "pohjavireen" tai sääntökirjan koko LLM-kutsulle. (Käyttötapaus: Asettaa globaalit säännöt, kuten *MORPHO-SYNTACTIC DETERMINISM*, jotka estävät mallia keksimästä merkityksiä asioille, joita tekstissä ei ole).
*   **Evidenssin poimintaprotokolla (Extraction Protocol):** Ohjaa mallia siinä, miten yksittäisiä datakappaleita tai sääntöjen toteutumisia (Assertions) etsitään. (Käyttötapaus: Varmistaa, että jokainen löytö perutuu joko täydelliseen osumaan tai nollahypoteesiin. Estää arvailun).
*   **Tekoälyn roolipersoona (AI Role Persona):** Määrittää mallin asenteen tai näkökulman luovassa tai argumentoivassa tuotossa. (Käyttötapaus: "Paholaisen asianajaja" tai "Valmentaja"). Poimintatehtävissä usein täysin tarpeeton ja potentiaalinen hallusinaation lähde.

---

## 2. Nykytilan kartoitus (Current State)

Koodikannan ja tietokannan (`seed_data.json`) perusteella nykytila on seuraava:

1.  **Execution Persona:** Pääasiassa `DETERMINISTIC_PARSER`. Tämä on kytketty backendin `system_directives.py`:n `GLOBAL_HARDENING_FRAMEWORK` -vakioon. Se kieltää mallia päättelemästä asioita ("Phantom Extraction Ban", "Anti-Semantic-Stretching"), mutta **ei kiellä** mallia ajattelemasta ääneen.
2.  **Evidenssin poimintaprotokolla:** Nykyään järjestelmässä kiertää `blk_573802341db9d68c` eli *"Globaali Zero-Trust evidenssin poimintaprotokolla"*. Tämä lohko **pakottaa** mallin tuottamaan 5-vaiheisen lokin ("Output ONLY the 5-step piped Parsing Log").
3.  **Tekoälyn roolipersoona:** UI tarjoaa vaihtoehtoja (esim. "Ei mitään / Oletus"). Rutiinipoiminnoissa oletus on ollut riittävä.

---

## 3. Tulevaisuuden tavoitetila (Target State & Justifications)

**Tavoitetilan perusfilosofia: "Zero-Reasoning Mandate" rutiinitehtäviin.**
Järjestelmän tulisi kyetä mekaaniseen, "tyhmään" datan poimintaan ilman kognitiivista ääneen ajattelua.

*   **Execution Persona:** `DETERMINISTIC_PARSER` säilyy, mutta siihen lisätään globaali sääntö, joka eliminoi `<thought>`-lohkot ja askel-askeleelta-päättelyn.
*   **Poimintaprotokollat:** Jaetaan kahtia:
    *   *Heavy Zero-Trust:* Käytetään vain Tier 4 / syväanalyyseissä, missä 5-vaiheinen loki on tarpeen XAI:n (Explainable AI) vuoksi.
    *   *Light JSON Extraction:* Uusi protokolla rutiiniaskeleille. Kieltää kaiken tekstin tuoton JSON-rakenteen ulkopuolella.
*   **Vaikutukset:**
    *   **Hinta:** Token-kulutus (output) putoaa jopa 60 %, laskien kompleksin ajon hintaa esim. $4.00 -> $1.50 per tiedosto.
    *   **Tehokkuus / Nopeus:** Malli palauttaa validin JSONin sekunneissa sen sijaan, että se pyörittäisi satoja tuhansia `reasoning` tokeneita.
    *   **Laatu:** JSON-muotovirheet vähenevät, koska "ajattelu" ei sotke API:n odottamaa rakennetta. Osumatarkkuus säilyy globaalien sääntöjen ansioista deterministisenä.

---

## 4. Nykyisen Workflow'n stepit

Nykyinen monivaiheinen `kokonaisvaltainen_auditointi` -workflow (ja vastaavat) sisältää askeleita kuten `step_input_processing`.

*   **Missä käytetään:** Poimintaprotokollia käytetään juuri `step_input_processing` -tyyppisissä datan pureskelun alkuvaiheissa faktojen suodattamiseen.
*   **Miksi käytetään:** Halutaan varmistaa, ettei tausta-aineistosta tartu mukaan tunnepohjaista "melua" (emotional noise).
*   **Mitä saavutetaan (nykytilassa):** Puhdas aineisto, mutta valtavalla "ääneen ajattelun" hintalapulla, kun malli käy protokollan pakottamana 5-vaiheista prosessia jokaisen lauseen kohdalla.

---

## 5. Nykyiset matriisit ja Execution Personat

Järjestelmä on ladattu raskailla arviointimatriiseilla: `matrix_toulmin`, `matrix_bloom`, `matrix_kahneman`, `matrix_goodhart` jne.

*   **Missä käytetään:** Näitä evaluatiivisia matriiseja käytetään silloin, kun lähdetekstiä halutaan arvioida akateemisten viitekehysten kautta (esim. Toulminin argumentaatiomalli).
*   **Miksi käytetään & Mitä saavutetaan:** Ne saavuttavat ällistyttävän korkean ja deterministisen poimintalaadun, koska ne kytkeytyvät `ExecutionPersona: DETERMINISTIC_PARSER` -rooliin.
*   **Ongelma:** Nämä matriisit ovat äärimmäisen akateemisesti sanoitettuja. Kun malli lukee ohjeen "Evaluate the cognitive mode of operation using Kahneman's Dual Process Theory", sen luontainen reaktio on avata laaja esseemäinen `<thought>`-lohko suorittaakseen analyysin. Ilman "Zero-Reasoning" -sääntöä, tämä on kallein yksittäinen prosessi koko järjestelmässä.

---

## 6. Syvällinen raportti ja taulukko (Nykytila vs. Tavoitetila)

| Ominaisuus | Nykytila (Current State) | Tavoitetila (Target State) |
| :--- | :--- | :--- |
| **Output Tokenit (Keskiarvo)** | ~1.35 miljoonaa (josta ~800k Reasoning) | ~500 000 (0 Reasoning tokeneita) |
| **Ajon Hinta (esim. 2.5 Flash)** | ~$4.00 per workflow-ajo | ~$1.50 per workflow-ajo |
| **Execution Persona (Parser)** | Määrää syntaktisen ja semanttisen tiukkuuden, ei ota kantaa lokitukseen. | Kieltää globaalisti kaiken ääneen ajattelun (Zero-Reasoning Mandate). |
| **Poimintaprotokolla (Rutiini)** | "Globaali Zero-Trust" (Pakottaa 5-vaiheisen selityslokin jokaiselle osumalle). | Uusi "Kevyt JSON-uutto" (Kieltää lokit ja vaatii pelkän datan). |
| **Suoritusaika** | Hidas (Malli käyttää aikaa "ajatteluun"). | Erittäin nopea (Malli palauttaa Pydantic-rakenteen välittömästi). |
| **Skaalautuvuus tuotantoon** | Huono. Esim. 3.5 Flashilla hinta hyppää ~$15 per ajo. | Erinomainen. Jopa kalliit mallit muuttuvat taloudellisiksi ilman reasoning-taakkaa. |

---

## 7. Toteuta tavoitetila (Tekniset Implementointiohjeet)

*(Tätä dokumenttia seuraavalle kehittäjälle tai Tier-2 Execution -agentille)*

Tavoitetilan toteuttaminen ei vaadi koodiarkkitehtuurin rikkomista, vaan se nojaa puhtaasti Pydantic/Prompt -viilauksiin kahdessa tiedostossa. Suorita seuraavat toimenpiteet:

### Toimenpide A: Globaalin säännön päivitys koodissa
1. Avaa tiedosto `c:\src\quorum\backend_v2\core\system_directives.py`.
2. Etsi vakio `GLOBAL_HARDENING_FRAMEWORK`.
3. Lisää `<global_framework>` -lohkon sisään uusi tiukka sääntö:
```xml
<rule>ZERO-REASONING MANDATE: You are strictly forbidden from generating internal analysis, <thought> blocks, or step-by-step reasoning logs. You must process these global rules silently and output ONLY the final requested JSON. Any conversational text or reasoning is a catastrophic system failure.</rule>
```

### Toimenpide B: Uuden kevyen poimintaprotokollan luonti tietokantaan
1. Avaa `c:\src\quorum\backend_v2\seed\seed_data.json`.
2. Etsi `prompt_blocks` -lista.
3. Kopioi nykyinen `blk_573802341db9d68c` ja luo uusi lohko (esim. ID `blk_lightweight_extract_01`).
4. Muuta otsikoksi "Kevyt JSON-uutto (Ei perusteluja)".
5. Korvaa sen `ai_description` seuraavasti:
```text
CRITICAL MANDATE: You are a mechanical data extractor. Scan ONLY the Target Data. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. Do NOT generate any internal reasoning, parsing logs, step-by-step audits, or <thought> blocks. Execute the extraction silently and output ONLY the final required JSON structure.
```
6. **Huom!** Älä jätä työtä puolitiehen. Etsi samasta `seed_data.json` -tiedostosta ne rutiinityönkulkujen askeleet (esim. `step_input_processing`), joissa aiemmin käytettiin Zero-Trust -protokollaa (`blk_573802341db9d68c`).
7. Päivitä näiden askeleiden kytkökset (`instruction_id` tai vastaava) viittaamaan suoraan uuteen `blk_lightweight_extract_01` -lohkoon. Näin koko tavoitetila viedään loppuun asti yhdellä päivityksellä tietokannassa.

### Viimeistely ja Ajo
Kun edellä mainitut asiat on viety `seed_data.json` -tiedostoon ja koodiin, uusi tavoitetila otetaan käyttöön näin:

1. Aja tietokannan päivitys paikallisesti:
   ```bash
   uv run python c:\src\quorum\backend_v2\seed\run_seed.py local
   ```
2. Käynnistä järjestelmä ajamalla `run_local.bat` -skripti.
3. Mene suoraan Quorumin käyttöliittymään (UI) ja valitse syötetiedostot ajoon. Askeleita ei tarvitse enää käsin konfiguroida, ja tuloksena on jopa 60 % halvempi ja paljon nopeampi ajo!

### Toimenpide C: Arkkitehtuuridokumentaation päivitys (Kaiken lopuksi)
Kun kaikki edellä kuvatut toimenpiteet on toteutettu ja meillä on varmistus uusista ihannearvoista (protokollista ja rooleista), täydennetään virallista dokumentaatiota:
1. Etsi hakemistosta `c:\src\quorum\docs\architecture` olemassa oleva, sopiva dokumentti (tai dokumentteja).
2. Kirjaa sinne auki *Execution Personan*, *Evidenssin poimintaprotokollan* ja *Tekoälyn roolipersoonan* tarkat määritelmät. (Tämän Epic-dokumentin rivien 12-15 tiivistelmät ovat tähän tarkoitukseen jo erinomainen pohja).
3. Lisää dokumentaatioon viralliset suositukset siitä, minkälaisia arvoja (esim. "Kevyt JSON-uutto" vs. "Globaali Zero-Trust") näille tulisi eri käyttötapauksissa antaa.

---

## 8. Tarkkuuden ja Luotettavuuden Varmistaminen (Toimenpide D)

Vaikka Zero-Reasoning Mandate säästää kustannuksia, se voi heikentää LLM-mallien kykyä noudattaa monimutkaisia Pydantic-skeemoja, mikä johtaa Dead Letter Queue (DLQ) -virheisiin. Tämän estämiseksi arkkitehtuuriin tulee tuoda seuraavat kolme lisäparannusta:

### D1. Schema-tason kevennys (Dynamic Schema Pruning)
Sen sijaan, että pakotamme mallia täyttämään raskaan skeeman ja käskemme promptissa olemaan käyttämättä sen kenttiä (esim. "Laita semantic_reasoning arvoksi N/A"), koodiin luodaan erillinen kevennetty Pydantic-malli (esim. `LightweightExtractionAtom`). Tästä mallista on kokonaan poistettu "ajattelukentät", mikä pienentää mallin kognitiivista kuormaa ja poistaa vahinkotäyttöjen riskin.

### D2. "Few-Shot" -esimerkkien pakotus kevyisiin protokolliin
Kevyt JSON-uutto -PromptBlockiin (Tietokannassa tai UI:ssa) on **pakollisena** lisättävä yksi oikeaoppinen JSON-esimerkki. LLM-mallit (kuten Gemini 2.5 Flash) noudattavat malliesimerkkejä huomattavasti luotettavammin kuin kieltoja (esim. "älä tuota listaa exact_quoteen"). Esimerkin tulee näyttää `atom_id`:n ja merkkijonon oikea asettelu.

### D3. Dynaaminen Kognitio-Reititys (Cognitive Routing)
Järjestelmän tulee suojella syväanalyysien laatua estämällä kevyen protokollan käyttö väärissä paikoissa:
* **Mekaaninen tiedonhaku:** Käytetään Kevyttä protokollaa + nopeaa Flash-mallia (säästää rahaa ja aikaa).
* **Syväanalyysi (esim. Kahneman, Bloom):** Kielletään Kevyt protokolla. Pakotetaan Globaali Zero-Trust (5-vaiheinen lokitus sallittu) ja reititetään raskaammalle Pro-mallille, sillä näissä tehtävissä kognitiivisia "reasoning"-tokeneita on pakko käyttää oikeellisuuden saavuttamiseksi.
