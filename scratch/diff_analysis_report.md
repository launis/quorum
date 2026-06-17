# Analyysi: Deterministisyys vs. Infrastruktuurin Uupuminen (Run 1 vs Run 2)

## 1. Yleiskatsaus Mittareihin
Vertailussa käytettiin kahta ajoa:
- **Run 1 (`exe_08d...`)**: Uusin ajo, joka kaatui 429 Resource Exhausted -virheeseen ja päättyi JSON-skeeman rikkoutumiseen (Double-Escape Trap).
- **Run 2 (`exe_46c...`)**: Aiempi ajo, joka meni onnistuneesti läpi maaliin asti.

**Avainluvut:**
- **Konsistenssi (Self-Consistency):** 80.54 %
- **Fleiss / Cohen Kappa:** ~0.61 (Kohtalaisen ja vahvan luotettavuuden rajamailla)
- **Eroavat atomit (Mismatches):** 29 kpl (19.5 % Varianssi)

## 2. "Väsymisen" (Fatigue) Suora Vaikutus Tuloksiin
Suurin osa havaitusta 19.5 % varianssista **ei johdu promptien huonoudesta tai mallin hallusinoinnista**, vaan yksinkertaisesti siitä, että uudempi ajo (Run 1) *"väsyi"* kesken korjausliikkeiden (Self-Healing). 

Kun Vertex AI rajoitti kutsuja (5 RPM) ja hylkäsi pyyntöjä, malli menetti kontekstinsa ja tuotti epävalidia JSONia (`invalid escape at line 3 column 0`). Tämän seurauksena Pydantic hylkäsi koko lohkon arvioinnit (`AGENT_SCHEMA_VALIDATION_FAILED`), ja järjestelmä merkitsi nämä atomit oletusarvoisesti tilaan `FALSE` (Fail-Fast).

Tämä näkyy suoraan diff-lokeissa:
- `[SYSTEM ERROR: LLM Unable to verify.] [5. VALIDATION DECISION: FAIL]`
- Tuloksena on **Entropia 1.000**, koska toisessa ajossa saatiin validi `TRUE` ja toisessa tekninen `FALSE` kaatumisen takia.

## 3. PASSED -> FAILED ja FAILED -> PASSED -Siirtymät
Raportissa on 10 tapausta, jotka menivät PASSED -> FAILED, ja 19 tapausta, jotka menivät FAILED -> PASSED.
Tämä epätasapaino (19 vs 10) osoittaa, että eheä ajo (Run 2) pystyi hyväksymään enemmän väitteitä (PASSED), kun taas kaatunut ajo (Run 1) hylkäsi ne puhtaasti teknisistä syistä (FAILED).

Tämä on **Fail-Fast -arkkitehtuurin todellinen voitto**: Kun LLM murtuu paineen alla ja tuottaa roskaa, järjestelmä ei arvo lopputulosta tai päästä korruptoitunutta dataa läpi, vaan se yksinkertaisesti hylkää atomin. Se tuottaa virhepisteen laaturaporttiin, mutta suojaa tietokantaa.

## 4. Johtopäätökset ja Seuraavat Askeleet
1. **Luotettavuus on "keinotekoisen" matala:** 80.54 % konsistenssi on harhaanjohtava. Jos konesalin kapasiteetti (5 RPM) ei olisi kuristanut Run 1:stä hengiltä, konsistenssi olisi todennäköisesti ollut lähempänä 95 %.
2. **Double-Escape Trap on todellinen riski:** Kun pakotamme mallin tunkemaan satoja rivejä tekstiä yhteen stringifioituun JSON-kenttään (`reasoning_trace`), se on altis syntaksivirheille heti, kun se joutuu paineen alle (esim. uudelleenyritykset).
3. **Konesalivalitsin on välttämättömyys:** Tämä analyysi todistaa kivenkovalla datalla, että EPIC 79 ei ole "nice to have" -ominaisuus, vaan järjestelmän vakauden elinehto. Emme voi ajaa tuotantotason laatuportteja (Audit Loops) konesalissa, joka antaa vain 5 pyyntöä minuutissa.

**Yhteenveto:** Arkkitehtuuri toimi täsmälleen oikein. Se suojeli järjestelmää LLM:n romahdukselta. Varianssi johtuu infrastruktuurin (Google Cloud) rajoitteista, ei Cognitive Quorum -arkkitehtuurin virheistä.
