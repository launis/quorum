# **EPIC 19: Kaksivaiheinen Arvosteluarkkitehtuuri (Design & Runtime)**

## **Ydinkonsepti & Arkkitehtuurinen Pääsääntö**

Tämä Epic ratkaisee suurimman pullonkaulan BARS-matriisien (Behaviorally Anchored Rating Scales) käyttöönotossa: substanssiasiantuntijoiden valtavan manuaalisen työtaakan. Samalla se sementoi EPIC 18 -mallin ytimen, eli 100 % deterministisen oikeudellisen auditoitavuuden.

Ratkaisu perustuu ehdottomaan kaksivaiheiseen arkkitehtuuriin. Järjestelmään luodaan kriittinen ohjaustason pääsääntö:

> **Tekoäly saa generoida arviointikriteerejä (atomeita) VÄIN KERRAN: matriisin suunnitteluvaiheessa (Design-time).**
> Arvosteluvaiheessa (Run-time) tekoäly ei koskaan lue alkuperäistä BARS-kuvausta tai keksi kriteereitä lennosta. Matriisi ja sen atomit lukitaan koodiin ja relaatiotietokantaan **ennen** ajoa, jotta kaikilla arvioitavilla kohteilla on sataprosenttisen sama, staattinen ja muuttumaton mittatikku.

---

## **Vaihe 1: Matriisin Atomisointi (Design-vaihe / Kääntäjä-AI)**

Asiantuntija ei enää laadi satoja mikroväitteitä manuaalisesti. Rakennetaan sisäinen työkalu, johon asiantuntija syöttää vanhan 4x5 BARS-matriisin solukuvauksineen ("Excel-sanahirviöt"). Taustalla pyörivä **Kääntäjä-LLM** hoitaa rutiinityön purkamalla nämä laadulliset kuvaukset koneellisesti luettaviksi atomeiksi.

**Kääntäjä-LLM:n Systeemikehote (System Prompt):**
> *"Olet sääntömoottoreiden asiantuntija. Tehtäväsi on purkaa annettu BARS-matriisin solun kuvaus erillisiksi, atomisiksi ja binäärisiksi (True/False) väitteiksi. Jokaisen väitteen on oltava sellainen, että se voidaan todistaa sanatarkalla lainauksella tekstistä. Poista laadulliset adjektiivit (esim. 'hyvin', 'kattavasti') ja muuta ne konkreettisiksi havaittaviksi teoiksi. Palauta tulos puhtaana JSON-listana."*

**Esimerkki Kääntäjä-LLM:n toiminnasta:**
* **Alkuperäinen solu (Ongelmanratkaisu, Taso 3):** *"Asiakaspalvelija pahoittelee viivästystä, selvittää juurisyyn ja tarjoaa asiakkaalle kaksi vaihtoehtoa ongelman korjaamiseksi."*
* **LLM:n generoima atomisoitu tietomalli (JSON):**
  1. *Asiakaspalvelija esittää pahoittelun viivästyksestä.*
  2. *Asiakaspalvelija kertoo asiakkaalle viivästyksen juurisyyn.*
  3. *Asiakaspalvelija tarjoaa asiakkaalle ensimmäisen ratkaisuvaihtoehdon.*
  4. *Asiakaspalvelija tarjoaa asiakkaalle toisen, vaihtoehtoisen ratkaisun.*

---

## **Vaihe 2: Ihmisen Validointi ja Lukitus (Human-in-the-Loop)**

Jotta arviointi on oikeudellisesti validia compliance-dokumentaatiota, Kääntäjä-LLM:n keksintöjä ei viedä suoraan tuotantoon. 

1. **Auditointi-UI:** Substanssiasiantuntija näkee matriisin solua klikkaamalla tekoälyn äsken laatimat atomit.
2. **Hienosäätö:** Asiantuntija hyväksyy, poistaa (esim. *"Tuo vaihtoehtoinen ratkaisu ei ole oikeasti absoluuttinen pakko, ruksitaan se pois"*) tai muokkaa atomien sanamuotoja.
3. **Master Template -Lukitus (Freeze):** Kun asiantuntija painaa "Julkaise matriisi", nämä atomit lukitaan relaatiotietokantaan. Tämän jälkeen 4x5 matriisin takana on kiinteä, kiveenhakattu säännöstö (esim. n. 60 atomia per matriisi), jota ei enää koskaan muuteta ilman Versionhallintaa.

---

## **Vaihe 3: Runtime-ajo (Arvostelu-AI & Sokkouttaminen)**

Kun järjestelmään valuu arvioitavaa reaaliaikaista dokumentaatiota, uusi Runtime-vaihe astuu voimaan. **Alkuperäiset laadulliset BARS-kuvaukset on piilotettu kokonaan.** Arvoistelu-AI toimii puhtaana, sokeana tiedonerottelijana (ylläpitäen EPIC 18 -filosofiaa).

1. Python-backend noutaa tietokannasta matriisiin kuuluvat 60 lukittua atomia.
2. Backend pakottaa dynaamisesti **Micro-CoT -vastauksen** (Quote -> Reasoning -> Boolean), mutta Runtime-kielimallille **EI kerrota missään vaiheessa janoavansa tasoja 1-5**. Se saa käsiteltäväkseen vain litteän 60 kysymyksen listan ymmärtämättä kokonaiskontekstia.
3. Runtime-AI palauttaa sokeat löydöksensä: *"Etsin näitä 60 asiaa tekstistä, löysin nämä 42. Tässä ovat lainaukset."*
4. Vaiheen 4 (Epic 18) **N-gram-hallusinaatiosuodatin** tarkastaa generoidun lainauksen alkuperäistä aineistoa vasten ja mitätöi väitteen oikosululla lennosta, mikäli tekoäly on keksinyt sitaatin omasta päästään.

---

## **Vaihe 4: Python-laskentamoottori (Deterministinen Vesiputous)**

Kun tiedonerottelu on saatu maaliin, tekoäly sammutetaan ja Python astuu valtaan. **Python laskee BARS-arvosanan 100 % deterministisesti.**

**A. Solun arvon laskenta (Onko yksittäinen Tason 3 solu saavutettu?):**
```python
def is_cell_achieved(cell_atoms: list[dict]) -> bool:
    """
    Kaikkien soluun liittyvien lukittujen atomien on oltava totta (ALL).
    Jos juurisyy ja 1. ratkaisu löytyi, mutta 2. ratkaisu puuttui (False), solu hylätään.
    """
    return all(atom["criteria_met"] == True for atom in cell_atoms)
```

**B. Ulottuvuuden eli Rivin laskenta vesiputousmallilla:**
Perinteinen BARS-matriisi on kumulatiivinen vesiputous.
```python
def calculate_dimension_level(cells_by_level: dict) -> int:
    achieved_level = 0
    # Iteroidaan solut tasoilta 1 -> 5
    for level in range(1, 6):
        if cells_by_level.get(level) == True:
            achieved_level = level # Noustaan seuraavalle askelmalla
        else:
            # VESIPUTOUS KATKEAA. BARS-sääntöjen mukaisesti tason 2 hylkäys 
            # pysäyttää nousun armotta tasolle 1, vaikka teksti täyttäisi tason 4 ihanteet.
            break 
    return achieved_level
```

**C. Koko Matriisin Kokonaislaskenta:**
Lopuksi Python koostaa tuloksen halutulla mekanismilla (esim. ulottuvuuksien keskiarvo).

---

## **Yhteenveto: Miksi tämä arkkitehtuuri on paras mahdollinen?**

1. **Skaalautuvuus & Aika:** Asiantuntijoiden ei tarvitse opetella ohjelmoimaan tai kirjoittamaan JSON-rakenteita. He voivat tuoda omat perinteiset matriisinsa sisään, ja järjestelmä atomisoi sen Kääntäjä-tekoälyllä silmänräpäyksessä heidän tarkistettavakseen.
2. **Nollatoleranssi mielistelylle:** Arviointihetkellä toimiva Runtime-tekoäly on sokea. Koska siltä on viety konteksti (tavoitteleeko dokumentti tasoa 2 vai 4), siltä on viety paine mielistellä tai joustaa standardeista ("ihmisluonto" piiloavaruudessa). Päättelyn tekee aina kylmä, tunteeton if-else-logiikka.
3. **Mikrokirurginen, valmentava XAI-raportti (Explainable AI):** Järjestelmän antama selite käyttäjälle ei ole enää tekoälyn ympäripyöreä jälkirationalisointi. Selite tulostuu koodista käsin: *"Matkasi katkesi Ongelmanratkaisu-ulottuvuudessa Tasolle 2, koska Tason 3 neljästä atomista puuttui pakollinen 'Toisen vaihtoehtoisen ratkaisun esittäminen'. Se korjaamalla saat tason 3."* Tämä tekee työkalusta mystisen tuomarin sijaan käytännön valmentajan.
