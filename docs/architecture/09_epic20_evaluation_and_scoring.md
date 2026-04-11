# 09: Kognitiivinen Arviointiarkkitehtuuri ja Pisteytys (DINA-malli)

Tämä luku kuvaa asiantuntija-arviointijärjestelmän ydintä, jonka vastuulla on purkaa laajoja aineistoja mitattaviksi subatomisiksi yksiköiksi ("Deep Atomization") ja muuntaa ne matemaattisesti jatkuviksi, vikasietoisiksi arvosanoiksi (Cognitive Diagnostic Dampening) noudattaen järjestelmän Pydantic Fail-Fast ja No-String -mandatteja.

## 1. Miten Atomisoidut Väitteet Syntyvät?

Järjestelmän arviointi luottaa atomisaatioon, missä matriisin kriteerit on valmiiksi pureskeltu pienimpiin mahdollisiin logiikkayksiköihin.

**Nykyinen tilanne (Staattinen Siemennykseen Perustuva Atomisaatio):**
Tällä hetkellä atomisoidut väitteet luodaan järjestelmään konfiguraatiovaiheessa (Seeding). Esimerkiksi `PromptBlock`-objektiin liitettävät `MatrixClaim`-rakenteet valmistellaan erillisellä automaatiolla tai insinöörityönä ennen tuotantoajoa. Työkalu analysoi laajat asiantuntijakriteerit ja tallentaa järjestelmään 3–5 binääristä (True/False) kyselevää "micro_atom"-väitettä per laatutaso (esim. *"Asiakirjassa mainitaan tekoälyn etiikka"*, *"Strategia ottaa huomioon resurssien riskitekijät"*).

**Tulevaisuuden Visio (Sanoittava ja Itseorganisoituva Rubric Studio):**
Tulevaisuudessa järjestelmä kykenee atomisoimaan asiantuntijakriteereitä dynaamisesti suoraan käyttöliittymän kautta (Rubric Studio). Kun käyttäjä syöttää järjestelmään holistisen PDF- tai Word-muotoisen laatumatriisin, LLM-ohjattu "Compiler"-agentti purkaa tuon matriisin semanttisesti lennossa, luo automaattisesti siihen liittyvät subatomiset väittämät, tallentaa ne Pydantic-tietokantaamme, ja julkaisee uuden arviointimittariston ilman manuaalista koodaamista tai skriptiajoja.

## 2. Deep Atomization (Syvä Atomisaatio asynkronisessa ajossa)

Perinteinen LLM-pohjainen lausuntojen arviointi kykenee harvoin tuottamaan tiukkoja, luotettavia arvosanoja pelkällä holistisella "Lue tämä ja anna arvosana 1-5" -ohjeistuksella. Järjestelmä ratkaisee tämän pilkkomalla arvioinnin suoritusvaiheessa:

1. **Matriisin purkaminen:** 
   Arviointimatriisin (BARS) jokainen skaalaporras (1.0 - 5.0) pitää sisällään tietokannassa yksittäisiä `micro_atoms` -totuusväittämää. Täydellisessä arvioinnissa työnkulun moottori (Workflow Engine) kokoaa mallille testattavaksi jopa 75 erilaista atomia.
2. **Sokkoarviointi (Isolated Runtime AI):** 
   Välttääksemme LLM:n rakenteellisen ennakkoasenteen (Hierarchy Bias), matriisin kaikki atomit viedään `atom_flattening.py` -hookkiin ennen arviointia. Hookki sekoittaa atomit täysin sokeaan järjestykseen (`hashlib` + kryptografinen siemenluku `execution_id`) ja heittää arvioitavaksi erillisenä luettelona "Syvänä Atomisaationa".
3. **True/False Käsittely:** 
   Kun LLM suorittaa arvioinnin (`T=0.0`), se tarkastelee jokaista atomia itsenäisenä binäärisenä solmuna (Kyllä/Ei + Perustelu). Nämä palautetaan `scoring.py` -hookille puhtaana sanakirjana, minkä jälkeen hook tekee käänteisen hajautuksen (Reverse Hash Mapping) liittääkseen tulokset takaisin oikeisiin asteikon tasoihin (1–5).

## 3. Pisteytyslogiikka: Progressive Dampening (DINA-malli)

Pelkkä osumien aritmeettinen painotettu keskiarvo johtaisi "Sycophancy"-ongelmaan: Jos alimmat faktat (Taso 1) uupuvat kohdetekstistä, mutta malli kehuu keksittyjä strategioita yli vuolaasti (Taso 5), keskiarvo antaa vaarallisen hyväksyvän lopputuloksen, antaen perusteetonta arvoa rakenteettomalle datalle.

Järjestelmä hyödyntää ratkaisuna **Kognitiivista Diagnostiikkamallia (Cognitive Diagnostic Dampening - DINA)**.

### Matemaattinen Malli (Kognitiivinen Virta)
Pisteytysmalli rakentuu Markov-ketjumaiseen jatkumoon, jossa alimmat tasot portinvaroijina määrittävät kognitiivisen virtauksen (*Cognitive Flow*) vahvuuden kerroin kerrokselta ylöspäin.

* Arvosana lähtee rakentumaan perusarvosta `scale_min` (yleensä 1.0) jolloin virtakerroin `modifier` vastaa suoraan ensimmäisen tason onnistumisprosenttia (esim. 0.90).
* Ylemmillä tasoilla jokainen saavutettu atomi tuo absoluuttisia desimaalipisteitä ohjelmistolle **vain sen verran, minkä alapuolelta tuleva virta sallii** (`achieved_score += step_value * hit_rate * modifier`).
* Välittömästi kunkin tason pisteiden annon jälkeen itse virtakerroin vaimentuu edelleen kuluvan tason onnistumisprosentilla (`modifier = modifier * hit_rate`).

**Lopputulos:** Järjestelmä pystyy erottelemaan logiikasta äärimmäisen tarkkoja ja aitoja jatkuvia desimaaleja analyytikolle (esim. 3.42 tai 4.89). "Fail-Fast" periaatteen mukaisesti malli on rakennettu siten, että ylemmän tason sataprosenttinenkaan luovuus ei tuo raporttiin kuin enimmillään murto-osan alkuperäispisteistään, jos perustason tosiasiayhteys (Taso 1 tai 2) romahti varhaisessa vaiheessa. Zero-Trust -auktoriteetti säilyy matemaattisesti lukittuna.

## 4. eXplainable AI (XAI) ja Audit Trail -jäljitettävyys

Dynaaminen laskentamoottori hyödyntää sääntöjen mukaista backend-integraatiota purkaakseen lasketun datan puhtaaksi ihmiskieliseksi XAI-tulkinnaksi (eXplainable AI).

**The Black Box -Mitigaatio:**
Jokaista laskettua desimaalitulosta varten rakennetaan erillinen `pb_ID_justification` Markdown-tietue, joka arkistoidaan `frozen_context.json` -tasolle tilarakenteeseen.
* Tämän tekstin tehtävä on avata ihmisille (kuten valmentajille tai auditoijille) tekoälyn laskukaava (`Cognitive Diagnostic Model Breakdown`) sekunnin murto-osassa.
* Tuloste kääntää monimutkaisen dynaamisen matematiikan selkokielisiksi ja arkkitehtuurisesti suojatuiksi ENUM-lauseikkeiksi, esimerkiksi: *"Level 3: 4/10 (40% - Cognitive flow degrades significantly)"*.
* Dokumentti näyttää aina vertailuksi myös raa'an painotetun keskiarvon (Shadow Calculation), jolloin loppukäyttäjä voi todeta lennosta tuomion ja vaimennusleikkurin voimakkuuden suoran numeerisen eron ja puuttua asiaan.

Tällä XAI-arkkitehtuurilla varmistamme, että tekoälyn esittämiin tuloksiin ei tarvitse koskaan sokeasti luottaa, vaan toimintaa voidaan seurata matemaattisesti suoraan tietokannan ytimestä verifioitavana näyttönä.

## 5. UI Rendering ja Zero-Math Pariteetti

Graafinen käyttöliittymä (Flutter Client) on alistettu tiukkaan **Zero-Math sääntöön** koko Pydantic-tuotantoketjun pituudelta. 

Kaikki pistelaskennan desimaalit, normalisoinnit sekä tasojen kynnysarvojen (`computed_min` & `computed_max`) suhteutus kootaan pelkästään Pythonin backendillä. Frontend olettaa aina saavansa valmiiksi arvoiltaan yhdenmukaistettua 0–1 X/Y-dataa, piirtäen hajontakuviot suoraan valmiiden matemaattisten tulosten ilmentyminä ohittaen tarpeen asiakaspohjaiselle liukulukulaskennalle kokonaan. DINA-malli on täydellisessä synkroniassa tämän "Smart Backend, Dumb Frontend" -käsialan kanssa.

## 6. Tietorakenteet ja Tallennus (Storage & Persistence)

Arviointiarkkitehtuurin tilanhallinta ja datan tallennus on jaettu tiukasti kolmeen toisistaan eristettyyn elinkaareen, jotta järjestelmä pysyy "Event Sourced" -yhteensopivana ja säilyttää auditoitavuuden. Seuraavat rakenteet soveltuvat sekä tuotantoon (Firestore) että paikalliseen lokaalikehitykseen (TinyDB).

### A. Atomisoidut Väittämät (Konfiguraatio / Siemendata)
Itse arviointimatriisit ja niiden kriteerit ovat muuttumatonta tuotantodataa. 
* Atomit (`micro_atoms`) luodaan asiantuntijoiden mittaristosta järjestelmän siemennysvaiheessa (Seeding). Pysyvä siemendata luetaan hakemistosta `c:\src\quorum\backend_v2\seed\`.
* Ne tallentuvat tietokantatiedostoon (esim. paikallisesti `data\db_v2.json` taulukkoon `prompt_blocks`) Pydantic-mallin mukaiseen `scales`-hierarkiaan. Lisäksi dynaamisen nopeuttamiseksi olemme ottaneet käyttöön välimuistitiedoston **`backend_v2\seed\atomization_cache.json`**, joka estää LLM:ää atomisoimasta vanhoja kriteereitä jatkuvasti uudelleen.

### B. Raaka-arvioinnit ja True/False -tulokset (Suoritustila)
Tekoälyn tekemä sokea atomien arviointityö on puhdasta prosessidataa, jota ei koskaan hävitetä.
* Kun LLM suorittaa 75 atomin True/False -analyysin, jokaisen atomin vastaus (tiiviste, totuusarvo ja LLM:n tuottama subatominen perustelu) paketoidaan listaksi.
* Fyysisesti tämä pitkä prosessilista upotetaan paikallisessa kehityksessä **`data\db_v2.json`** -tiedoston `executions`-taulukkoon. Koska säilytämme raaan lokin (`ExecutionRecord.execution_trace`) jokaisesta `True/False` päätöksestä tietokannassa muuttumattomana lokina, voimme milloin tahansa jälkikäteen tutkia syitä ilman että ajoa täytyy toistaa.

### C. Lopulliset arvosanat ja XAI-perustelut (Output-tila)
Itse matemaattinen päättely (`scoring.py` DINA-laskenta) muodostetaan vasta aivan lopuksi edellä mainittujen True/False -osumien perusteella.
* Muodostetut jatkuvat desimaaliarvosanat (esim. `3.42`) ja kognitiivisen virran ihmiskielinen Markdown-selitys (`pb_ID_justification`) tallennetaan ylätason tulosrekisteriin, joka tunnetaan nimellä **`Frozen Context`**.
* Tämän tuloksen pakastus ohjataan aina yhtenäisen **`StorageService` (FileDriver)** -rajapinnan läpi. Asiakassovellus tai hook-koodi ei koskaan käytä natiiveja Python-tallennuksia. 
* Lokaalissa kehityksessä `StorageService` on konfiguroitu pudottamaan tulos levylle litteänä JSON-tiedostona (*Hard Artifact*) polkuun `c:\src\quorum\data\files\executions\exe_{id}\frozen_context.json`. Tuotannossa (`StorageBackend.FIRESTORE`) täsmälleen sama koodi ohjaa pakastuksen suoraan Google Cloud Storage -bucketiin.
* Tämän valmiin fyysisen JSON-tiedoston rakentaminen on selkäranka Zero-Math -mandatille: Frontend (Flutter) tai erillinen asynkroninen PDF-generointimoottori (Arq Worker) kykenee lukemaan valmiin UI-datan suoraan FileDriverin yli nanosekunneissa suorittamatta raskaita ohjelmallisia tietokantaliitoksia.
