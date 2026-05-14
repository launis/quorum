# Haamuvarianssin Juurisyyanalyysi (Baseline V4.0)

**Päivämäärä:** 14.5.2026  
**Konteksti:** Epic 51, Deterministisen orkestrointilogiikan kovetus (V4.1 siirtymä)

## 1. Yhteenveto ja Mittarit

Tämä raportti dokumentoi "haamuvarianssin" (ghost variance) tilan kahden peräkkäisen, identtisen datapaketin LLM-arviointiajon välillä. Ajot suoritettiin V4.0-säännöstön alaisilla arviointimatriiseilla.

**Analysoidut ajot:**
1. `exe_ae646cba42ca4e5ca8411bbd841491e5`
2. `exe_fab8ea579487462380819afec268e91e`

**Tilastot:**
* Yhteisiä arvioituja atomeja (TDA Claims): **184 kpl**
* Epäjohdonmukaisia tuloksia (Mismatches): **36 kpl**
* **Kokoonpanon Haamuvarianssi: 19,6 %**

Liki joka viides arviointipäätös (PASSED / FAILED) kääntyi täysin päinvastaiseksi pelkän satunnaisuuden seurauksena. Deterministisessä `Fail-Fast` -järjestelmässä tämä on kestämätöntä.

---

## 2. Haamuvarianssin Juurisyyt

Raakadatan (`scratch/mismatch_traces_raw.md`) analyysi paljasti, että varianssi ei johdu yksinomaan LLM:n satunnaisuudesta, vaan sääntöjen rakenteellisista "tulkintavuodoista", jotka houkuttelevat LLM:n pohtimaan asioita semanttisesti mekaanisen poiminnan sijaan. 

Heilahtelut jakautuivat kolmeen kategoriaan:

### Juurisyy A: Leksikaalisen ankkurin ohittaminen ("Henki vs. Kirjain")
Vaikka säännöt pakottivat etsimään tiettyjä fyysisiä sanoja, ACCEPT/REJECT-logiikka antoi LLM:lle oikeuden tehdä poikkeuksia "kontekstin" perusteella.

* **Esimerkki-atomi:** `tda_46520c9743e9b881`
* **Sääntö:** Etsi rajausmerkkejä (*'only applies to', 'limited to'*). Jos teksti määrittelee populaation tai olosuhteen, ACCEPT.
* **Ajo 1 (Oikein - FAILED):** LLM totesi, että ilmaisu "Kaupallinen Johtoryhmä" asettaa kontekstin, mutta dokumentista puuttuvat ekspliittiset, ehdolliset lauseet. Sääntö hylättiin.
* **Ajo 2 (Hallusinaatio - PASSED):** LLM tarttui otsikkoon "Kohderyhmä: Kaupallinen Johtoryhmä" ja tulkitsi sen "hengen" mukaisesti rajoittavaksi tekijäksi, jättäen huomioimatta täydellisen leksikaalisten ankkurien puutteen.

### Juurisyy B: Polariteettisekaannus (Virtue vs. Vice -epävakaus)
Ns. "pahesäännöt" (FATAL FLAW / inverse_evidence), jotka etsivät virheitä, sekoittivat kielimallin pahan kerran. Malli ei ollut varma, tarkoittaako löydös säännön "täyttymistä" (hyvä asia) vai rikkomusta (paha asia).

* **Esimerkki-atomi:** `tda_2aec15ab07984f4d`
* **Sääntö:** Etsi 100% varmuutta ilmaisevia markkereita (*'guaranteed', 'always'*). Jos lause tekee subjektiivisen tulevaisuudenennusteen näillä markkereilla -> ACCEPT (Löydettiin virhe).
* **Ajo 1 (PASSED - Ei virhettä):** LLM tutki tekstin, ei löytänyt pakollisia sanoja ja päätti, ettei virhettä ole.
* **Ajo 2 (FAILED - Virhe löydetty):** LLM luki lauseen *"Vain kestävät liiketoimintamallit saavat tulevaisuudessa pääomaa"* ja tulkitsi sanan *"Vain"* 100 % varmuudeksi, kaataen koko atomin, vaikkei sanaa "vain" ollut leksikaalilistalla.

### Juurisyy C: Subjektiivinen intentiotulkinta
Kun säännöt pakottavat LLM:n päättelemään "tekijän aikomusta" (esim. onko kyseessä sävy- vai asia-argumentti), arviointi riippuu täysin kyseisen hetken "nopanheitosta".

* **Esimerkki-atomi:** `tda_b1bcf8b0c203b736`
* **Sääntö:** Jos käyttäjän pyyntö keskittyy "vain sävyyn" (performativity), mutta sivuuttaa faktojen puutteen -> ACCEPT. (Virhe)
* **Analysoitu lause:** *"Kirjoita tämä johtoryhmälle ja lisää hiukan kaupallisia vaikutuksia mukaan."*
* **Ajo 1 (FAILED):** Tulkitsi "kaupalliset vaikutukset" tyylilliseksi (sävyn muutos johtoryhmälle). Katsoi virheen tapahtuneen.
* **Ajo 2 (PASSED):** Tulkitsi "kaupalliset vaikutukset" uuden tiedon (faktan) vaatimiseksi. Katsoi, ettei kyse ollut pelkästä sävystä, eikä sääntöä rikottu.

---

## 3. Strategiset johtopäätökset ja V4.1 Siirtymä

Yllä oleva 19,6 % varianssi osoittaa kiistattomasti, että kognitiivinen ehdollisuus (`If... -> ACCEPT, otherwise -> REJECT`) LLM-prompteissa on hylättävä. Säännöistä on tehtävä **täysin mekaanisia parsinta-algoritmeja**.

Tämän pohjalta Epic 51:n ohjeisto (`epic51_seed_data_tda_refactor NEW VERSION.md`) on päivitetty V4.1-strictness -tasolle. Kaikkiin korjattaviin ai_rule_description -kenttiin ajetaan nyt seuraavat säännöt:

1. **Kognitiivisten Booleanien Kielto (Sääntö 6.1):** ACCEPT/REJECT -tulkinnat kielletään kokonaan.
2. **Mekaaninen Poiminta (EXTRACT EXACT QUOTE):** Säännöt pakotetaan imperatiiviseen Regex-maiseen hakuun: *"EXTRACT EXACT QUOTE IF AND ONLY IF THE EXACT WORDS [X, Y, Z] ARE PRESENT. IF MISSING, RETURN NULL."*
3. **Polariteetin Selkiyttäminen:** LLM:ää ei pyydetä arvioimaan "onko sääntö rikottu", vaan siltä pyydetään ainoastaan lainaus, jos tietyt sanat esiintyvät tietyssä kontekstissa. Järjestelmän taustalogiikka (Pydantic / aggregation_mode) hoitaa sen, kaatuuko laatuportti kyseiseen lainaukseen vai ei.

*Kun V4.1-ohjeisto on ajettu matriiseihin sisään, uudet ajot tehdään ja tämä baseline-raportti toimii verrokkina uuden järjestelmän determinismin todentamiseksi.*
