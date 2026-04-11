# **EPIC 18: Deterministinen Arvostelumoottori (Flat Atomic Scoring)**

## **Ydinkonsepti**

Tämän Epicin ainoa tavoite on korjata järjestelmän arviointilogiikka muuttamalla se täysin kirkkaaksi, painottamattomaksi matematiikaksi (ns. Flat Atomic Scoring). Kaikki token-optimointeihin, kustannussäästöihin, Y-Funnel-reitityksiin tai välimuististrategioihin (Prompt Caching) liittyvät vaatimukset on jätetty tarkoituksellisesti tämän dokumentin ulkopuolelle. Fokus on yksinomaan tulosten absoluuttisessa tarkkuudessa ja oikeudellisen tason läpinäkyvyydessä.

Kielimalli (LLM) alennetaan kliiniseksi "tiedonerottelijaksi" (Feature Extractor). Siltä viedään täysi kyky antaa arvosanoja, ja sitä kielletään analysoimasta tai arvottamasta tekstiä. Sen ainoa tehtävä on etsiä kapeita, atomisia väitteitä aineistosta. Uusi Python-backend laskee loppuarvosanan sataprosenttisesti saavutettujen osumien (True) lukumäärän perusteella ilman piilotettuja painotuskertoimia tai miinuspisteitä.

---

## **Toteutuksen Vaiheistus**

### **Vaihe 1: Datan Rakenteellinen Pakotus (Micro-CoT)**
**Tavoite:** Pakotetaan kielimalli etsimään fyysinen todiste aineistosta ennen boolean-johtopäätöksen sallimista.
* **Toimenpide:** Uudelleenkirjoitetaan backendin `schema_builder.py` niin, että LLM:ltä vaaditaan dynaaminen sisäkkäinen Pydantic-malli jokaiselle atomiselle väitteelle (claim).
* **Tietorakenne pakollisessa järjestyksessä:**
  1. `exact_quote` (string) – Pakollinen sanatarkka todiste lähdetekstistä.
  2. `reasoning` (string) – Tekoälyn lyhyt havainto, miten lainaus vastaa väitettä.
  3. `criteria_met` (boolean) – Päättely pitääkö kriteeri paikkansa (T/F).
* **Vaikutus:** Autoregressiivinen malli ei voi antaa "mutuun" perustuvaa True-vastausta, vaan sen on fyysisesti löydettävä ja generoitava lainaus ensimmäiseksi.

### **Vaihe 2: Arvosanan laskennan irrottaminen kielimallilta**
**Tavoite:** Viedään subjektiiviselta kielimallilta kyky päättää kokonaisarvosanaa tai soveltaa omia armahduksiaan.
* **Toimenpide:** LLM:n luomasta Pydantic-skemasta poistetaan KAIKKI numeeriset arvokyselyt (esim. `step_4_final_score`). Tekoäly saa palauttaa ainoastaan edellisen vaiheen Micro-CoT -rakenteita.
* **Vaikutus:** Tekoäly ei voi enää kaunistella arviota omilla "keskiarvopesuillaan" hyödyntäen aineiston sujuvaa kieltä poikkeuksena huonolle asiasisällölle.

### **Vaihe 3: Painottamaton Atominen Laskenta (Flat Atomic Claims)**
**Tavoite:** Muutetaan subjektiiviset BARS-matriisit tasa-arvoisiksi väitelistoiksi, joissa ei ole piilotettuja kertoimia tai rankaisevia kattolukituksia.
* **Mekanismi:** Vanhat matriisitasot puretaan pieniin, binäärisiin yksityiskohtiin (atomic claims). Jokainen kriteeri on samanarvoinen. Pisteitä annetaan yksinomaan havaintojen määrästä (esim. algoritmi laskee "Loytyykö X? Kyllä -> +1").  Arvosanassa ei ole lainkaan negatiivista vähennyslaskua, vaan tila nousee pohjamudasta ainoastaan saavutetun näytön (True boolean) perusteella.
* **Miksi painotuksia ei käytetä:** Erilaisten painotusten (esim. "tämä väite on 1.5 pisteen arvoinen") jakaminen siirtäisi subjektiivisuuden ja arvailun tekoälyltä takaisin matriisin suunnittelijalle. Täysin tasa-arvoinen malli pakottaa asiantuntijat laadukkaan matriisin muotoiluun: jos tietty BARS-asteikon ylätason konsepti on elintärkeä, se on vain pilkottava useammaksi erilliseksi mikroväitteeksi. Näin konseptin tärkeys heijastuu suoraan kysymysten lukumääränä, eikä mystisenä painokertoimena.
* **Tulos:** Laskennasta tulee päivänselvää murtolukumatematiikkaa. 10 kysymystä, 7 osumaa = arvosana on 7/10:sta maksimivolyymista.

### **Vaihe 4: N-gram Hallusinaatiosuodatin (Aitouden Varmistus)**
**Tavoite:** Varmistetaan algoritmisesti (ei-tekoälyllä), että kielimallin poimima `exact_quote` on peräisin asiakirjasta.
* **Mekanismi:** Luodaan `integrity.py`-suodatin, joka käyttää esim. `difflib.SequenceMatcher`-liukuvaa ikkunaa tekoälyn suoltaman tekstin paikantamiseen alkuperäisestä, ladatusta PDF-aineistosta. 
* **Vaikutus:** Jos suodatin ei löydä tekstiä OCR-suttutoleranssin puitteissa (tekoäly keksi sen), suodatin kääntää väitteen `criteria_met` -tilan säälimättä `False`:ksi. Tämä eliminoi saadun Plus-pisteen suoraan laskennasta ilman, että XAI tarvitsee monimutkaisia selityksiä. Se oli valhe, sitä ei lasketa.

### **Vaihe 5: Semanttinen Sanitaatio (Kliininen Ohjeistus)**
**Tavoite:** Puhdistetaan tekoälyn "mieli" rankaisemisesta ja opettamisesta.
* **Toimenpide:** Matriisien `seed_data.json` ja mallin järjestelmäohjeistukset puhdistetaan. Kaikki tunteikkaat tai arvioivat käskyt ("SEVERE PENALTY", "Judge strictly") poistetaan.
* **Mekanismi:** Tilalle ohjelmoidaan kuiva, neutraali direktiivi: _"Olet kliininen tiedonerottelija. Etsi aineistosta kriteeriä vastaava sanatarkka lainaus. Älä arvioi luetun teksti laatua. Älä anna pisteitä tai miinuksia, tuota vain pyydetyt tekstilöydökset."_

---

## **Odotetut Vaikutukset & Työkalun Identiteetin Muutos**

* **Maksimaalinen Läpinäkyvyys asiakaskohtaamisessa:** Asiakkaan on äärettömän helppo ymmärtää puhdasta Plus-matematiikkaa. Tuleva XAI-raportti on selkeä ja motivoiva: *"Järjestelmä etsi 10 edellytystä tälle laatustandardille. Löysimme niistä tasan 7. Arvosanasi on 7/10. Tässä ovat nuo 3 puuttuvaa havaintoa jotka korjaamalla nouset kymppiin."*
* **100 % Oikeudellinen Toistettavuus:** Ei tekoälyn satunnaista vaihtelua, ei mustia matemaattisia painokerroin-laatikoita. Tuloksen voi aina toisintaa pyytämällä ihmistä lukemaan tuotetut kysymykset.
* **Matriisidesignin Rakenteellinen Terävöityminen:** Järjestelmä nostaa älyn ulos "mustan laatikon" kertoimista ihmisen maailmaan. Se pakottaa substanssiasiantuntijat konkretisoimaan epämääräiset "Vahva asiantuntijuus" -huutelut yksiselitteisiksi, lukumääräisiksi, atomin tarkoiksi tarkistuslistoiksi.
