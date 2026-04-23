# Epic 29: XAI Extension Anti-Sycophancy & Hardening ("Garbage In, Garbage Out Halt")

## 1. Yhteenveto & Tavoite (Epic Goal)
Quorumin V2-arkkitehtuurissa globaali loppusynteesi ja näyttöjen pääkomponentit noudattavat jo tiukkaa, säälimätöntä ja täysin dataan ankkuroituvaa (Zero-Compromise) linjaa. Kuitenkin apulaatikot ja matriisikohtaiset laajennukset eli ns. **XAI Output Extensions** (`coaching`, `falsification`, `missing_context`, jne.) kärsivät vielä satunnaisesta *Fluff-In, Fluff-Out* -ongelmasta. 

Tämän Epicin tavoitteena on estää tekoälyä oletusarvoisesti liukumasta kohteliaaseen "yrityskonsulttimoodiin" (Sycophancy) luodessaan lisätietokenttiä. Laajennusten on opastettava käyttäjää ja annettava tiukkaa, konkreettista palautetta tehtyjen liiketoiminta- tai logiikkavirheiden pohjalta, ilman ylimalkaista tsemppaamista tai teoreettista jargonia.

## 2. Nykytilan Ongelma (The Problem)
Tällä hetkellä matriisien arviointiluuppi (Map-Reduce) rakentaa laajennukset lennosta generoitujen Pydantic-kuvausten perusteella.
* Esimerkki nykyisestä tilasta ohjelmistossa (`schema_builder.py`): Tuotettaessa kenttää `coaching`, tekoälylle annetaan ainoaksi ohjeeksi: *"Concrete coaching tip/remediation advice to the subject."*
* Tämä ylikaupallinen ja löysä ohje mahdollistaa sen, että malli palauttaa ympäripyöreää tsemppiä.
* Koska Globaali Synteesi (`synthesis.py`) ainoastaan *kokoaa ja tiivistää* nämä arvioinnit, se joutuu työskentelemään heikon raakamateriaalin kanssa. Jos yksittäinen laatikko tuottaa pelkkää jargonia, loppuraporttikin täyttyy jäännösjargonilla (GIGO).

## 3. Toteutuksen Vaiheet (Implementation Phases)

### Phase 1: Pydantic-skeemojen Ankkurointi (Schema Level Hardening & Enum Parity)
Päivitetään dynaamisen mallinlukijan (`backend_v2/llm/schema_builder.py`) Field-kuvaukset raaemmiksi ja yksiselitteisemmiksi. Teoriatermit korvataan selkeällä rakenteellisella vaatimuksella.

**Phase 9 Mandaatit (Zero-Compromise):**
* **Strict Enum Parity:** Poistetaan kovakoodatut string-vertailut (esim. `if "coaching" in extensions:`). Laajennusten tarkistus ja kenttien generointi on tehtävä hyödyntämällä suoraan `XaiExtensionType` Enumia (`backend_v2/models/enums.py`), joka poistaa No-String Mandaten rikkomukset.
* **Coaching & Remediation:** Kuvaus ei saa sallia "vinkkejä". Ohjeen tulee pakottaa esittämään yksi konkreettinen toimenpide, jolla havaittu aukko datassa tai logiikassa paikataan.
* **Falsification & Risk Flag:** Kuvauksen on kiellettävä lieventävät sanat. Tekoälyä käsketään listaamaan armottomasti tismalleen se liiketoimintaskenaario, jossa käyttäjän malli tai väite kaatuu sataprosenttisesti.

### Phase 2: Globaalin XAI-Mandatin Injektio (Evaluation Chunk Hardening)
Yksittäisten kenttien kuvaukset eivät riitä, jos tekoälyn globaali sävy on kohtelias. Orkesroinnin moottoriin (`backend_v2/services/orchestrator/prompt_compiler.py`) lisätään uusi **Anti-Sycophancy XAI Header**, joka liimataan jokaiseen yksittäisen matriisin arviointipromptiin.

* **Injektion rooli:** "Kaikkien lisäkenttien (extensions) on noudatettava samaa ankaraa ja viileän analyyttistä linjaa kuin pääarvosanan. Jos käyttäjän tulos on matala, *coaching* ja *missing_context* eivät saa olla kannustavia. Niiden pitää osoittaa sormella tarkasti puuttuvaa dataa, virheellistä mittaria tai huteraa syy-seuraussuhdetta. Puhu kuin ankara ammatillinen ohjaaja."

### Phase 3: Synteesin Päätoimittajan (Chief Editor) Suvereniteetti [✅ COMPLETED]
Synteesimoottorin (`backend_v2/hooks/synthesis.py`) Master Prompt on jo päivitetty varmistamaan, että fragmentoituneiden laajennusten sulauttaminen tapahtuu fiksusti.
* `TARGET EXTENSIONS TO HARVEST` -logiikka on todettu toimivaksi: se karsii pois löysät itsestäänselvyydet ja pakottaa tekoälyn nostamaan vain 3 kovinta ("TOP 3 most critical, high-impact global highlights"). Tämä osio on valmis ja tuotannossa.

## 4. Onnistumisen Kriteerit (Definition of Done)
1. **Ei enää "Tsemppikonsulttia":** Koko arkkitehtuuri ei anna yhtään "Jatka hyvää työtä" tai "Harkitse tätä" -tyylistä apulaatikko-ohjetta, jos pallo kyntää pohjamudissa.
2. **Single Source of Truth:** Coaching ei hallusinoi uusia ohjeita, vaan rakentaa ne ainoastaan 1:1 todettujen datapuutteiden (XAI-löydös) varaan.
3. **Fail-Fast Compliance (Phase 9):** Arkkitehtuuria ei rikota. Yksikään näistä muutoksista ei muuta litistettyjen avainten mallia (esim. `blk_abc_coaching`), vaan parantaa ainoastaan sisällön laatua arvoketjun alkupäässä. `schema_builder.py` on puhdistettu raaoista string-vertailuista ja nojaa täysin `XaiExtensionType` Enumiin.
