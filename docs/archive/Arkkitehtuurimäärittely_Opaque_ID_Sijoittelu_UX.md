# ARKKITEHTUURIMÄÄRITTELY: Opaque ID Sijoittelu ja UX-Abstraktio V2

Tämä dokumentti määrittelee, kuinka Quorum Admin Studio V2 -käyttöliittymä (Flutter/Riverpod) mukautetaan The Universal Opaque ID -migraation (V2) jälkeiseen todellisuuteen. 

## 1. Ongelman Kuvaus

Kun Quorum siirtyi manuaalisista, ihmisluettavista V1-tunnisteista (esim. `step_profiler`, `matrix_kahneman`) kryptografisesti vahvoihin ja koneellisesti luotuihin V2 Opaque ID -tunnisteisiin (esim. `steprule_d90f30d31b894ba2ba12507370eedb46`, `blk_9adcb55b7ba44baeaf8921cb2fb935dc`), saatiin järjestelmään absoluuttinen ID-kollisioturvallisuus.

**UX-ongelma:** Pääkäyttäjä ei enää kykene muistamaan, kirjoittamaan tai hahmottamaan pitkiä tunniste-ketjuja Admin Studiossa työnkulkuja (Workflows) ja tulosnäkymiä (Blueprints) rakentaessaan. 

Kriittiset ongelmakohdat Admin Studiossa:
1. **Blueprint Editor (Tulosten visualisointi):** *Datan Polku (Data Path)* -kenttien asettaminen. Esimerkiksi polun `$results.steprule_XYZ.blk_ABC_normalized` käsinkirjoitus on mahdotonta.
2. **DAG Builder (Työnkulun rakentaminen) - Riippuvuudet:** Askeleen *Riippuvuudet (DAG-reunat)* -valikossa käyttäjän pitäisi ymmärtää listalta pelkkiä `steprule_...` tunnisteita.
3. **DAG Builder - Syötemappaukset (Input Mappings):** Mistä aiemmasta askeleesta (*Datalähde / Source*) ja mistä tarkasta output-blokista (*Vaiheen ID*) arvo sijoitetaan nykyisen askeleen syötteisiin.

---

## 2. Arkkitehtuurinen Ratkaisu: The Cascading State Pattern (Visuaalinen Polunrakentaja)

Koska backend vaatii absoluuttista V2 Opaque ID -tarkkuutta ja ihminen vaatii selkokielisyyttä, ratkaisu on täydellinen abstraktio The UX -kerroksessa.

Käyttöliittymä (Flutter) ohjelmoidaan rakentamaan ja purkamaan The Opaque ID -merkkijonot (Strings) taustalla, samalla kun Pääkäyttäjälle näytetään vain riippuvaisia pudotusvalikoita (Cascading Dropdowns) tai askeleiden ihmisluettavia nimiä (Nomenclature).

### A. Kontekstitietoisuus (The Riverpod Workflow State)

Kaikki ratkaisut nojaavat siihen, että kun Admin avaa työnkulun, Riverpod-tilassa (esim. `workflowEditProvider`) on ladattu koko työnkulun puu:
* Koko `Workflow` objekti.
* Sen `steps` (Kaikki askeleet, esim. ID: `steprule_XYZ`, Nimi viitatussa `task_blueprint`:ssä: "Profiler")
* Jokaisen The Stepin `prompt_blocks` (ID: `blk_ABC`, Slug: "Kahneman Matriisi").

Tämä sallii Flutterin vääntää Opaque ID:n ihmiskielelle lennosta iteroiden tilaa vasten (`steps.firstWhere((s) => s.id == opaqueId)`).

---

## 3. Toteutukset Komponenttikohtaisesti

### Komponentti 1: Blueprint Editor (Data Path / Datan Polku)

Blueprint Editorissa elementin (esim. The Gauge tai The Matrix) datalähde osoitetaan aiemman DAG-askeleen tiettyyn The PromptBlockiin.

**Nykyinen (Huono) UX:** Vapaa tekstikenttä merkkijonolle `$results.steprule_XYZ.blk_ABC_normalized`.
**Tuleva UX:** Kolme dynaamista The Dropdownia (Pudotusvalikkoa):

1. **[Dropdown 1] Askeleen valinta (Luetaan Workflow-tilasta):**
   * *UI Näyttää:* "Vaihe 1: Profiler"
   * *Controller Tallentaa:* `steprule_d90f...`
2. **[Dropdown 2] Datan lähteen valinta (Riippuvainen Valikosta 1):**
   * *UI Näyttää:* "Kahneman Matriisi", "Tuomarin raportti" (Filtteröi The PromptBlocks Valikon 1 Stepin the perusteella).
   * *Controller Tallentaa:* `blk_9adc...`
3. **[Dropdown 3] Jälkikäsittely / Modifier (Staattinen Enum):**
   * *UI Näyttää:* "Normalisoitu Tulos (0-100)", "Raaka Data", "Perustelut"
   * *Controller Tallentaa:* `_normalized`

**The Assembly:** Save-painikkeessa the Flutter the State yhdistää the kolme kenttää merkkijonoksi `$results.${valikko1}.${valikko2}${valikko3}` ja se tallennetaan The JSONiin. 
**The Disassembly:** Renderöidessä the Editoria the JSON luetaan The Regexillä ja käännetään the dropdownien valinnoiksi the asettamalla oikeat ID:t valituiksi arvoiksi.

---

### Komponentti 2: DAG Builder - Riippuvuudet (DAG-Reunat)

Kun askeleelle kytketään riippuvuus (Dependency / Arrow), sen the on the the suoritettava vain the kun parent-askel on valmis.

**Nykyinen (Huono) UX:** Usean the the the the valinnan List-Dropdown näyttää the the the The Opaque ID:n the (esim. `steprule_bd84403...`). 
**Tuleva UX:** Human-Readable Checkbox List / Multi-Select Dropdown.

* **UI:n Lataus:** Valikko ei the iteroi `StepRule.id` listan arvoja sellaisenaan, vaan the etsii the `task_blueprint` -viittauksen `steps` kokoelmasta the ja the näyttää the The Reference Stepin the the Localization the Namen (esim. "Falsifier (Kriittinen Audit)").
* **The Assembly:** the Käyttäjä ruksii "Falsifier", mutta the listaan the the the lisätään `steprule_fb67...`. UI-komponentin the the `ItemBuilder` the kääntää nayton lennossa Opaque -> String Nimi.

---

### Komponentti 3: DAG Builder - Syötemappaukset (Input Mappings)

Syötemappaus määrittää, the mitä dataa V2 the Engine injektoi the askeleen The The Agentille the. (esim. syöttää the the edellisen the matrix-tuloksen the AI:lle).

**Nykyinen (Huono) UX:** The Vapaa kenttä "Datalähde (Target)" jossa lukee the esim. `$steps.steprule_6364d00...`.
**Tuleva UX:** Sama kolmivaiheinen The Dropdown-putki kuin The Blueprint Editorissa!

Koska the Quorumin the the V2 DAG Executor tukee the Semanttista The The Reititystä ($inputs-injektion the lisäksi), voidaan the tulevaisuudessa the data the hakea tarkasti aiemmasta The Askeleesta. 

Mappaus-UI muuttuu the älykkääksi Boksiksi:
1. **Lähdetyyppi (Dropdown):** "Globaali Syöte (esim. $inputs)" TAI "Työnkulun Askel (V2 Matrix Output)".
2. **Jos Valittiin Työnkulun Askel:**
   * Aukeaa The Valikko A (Valitse Askel) -> *Näyttää the aiemmat the riippuvuudet the the ihmisnillä*.
   * Aukeaa The Valikko B (Valitse Tieto) -> *Näyttää aiemman askeleen The The matriisit/raportit*.

Taustalla The UI kääntää the mappauksen the Datalähteen (Target) muotoon the the the `$steps.steprule_XYZ.output.blk_ABC_normalized`, jolloin data The saavuttaa The Agentin the the millimetrin the tarkasti the Pydantic-turvallisessa muodossa.

## Yhteenveto

Quorum the Admin The Studio V2 ei the saa vaatia Pääkäyttäjää lukemaan tai kirjottamaan The Opaque ID:itä the. Kaikki editointi, oli the kyse Visualisoinneista (Blueprint) The tai The Työnkulun Injektioista The (DAG Builder), on refaktoroitava toisistaan The riippuvaisiin **Dropdown / Select -pudotusvalikkoihin**, jotka etsivät the ihmisluettavan The Nimen the Riverpod-tilassa olevasta Työnkulku-puusta.
