# Epic 52: LLM:n kognitiivisen vinouman ja järjestysharhan poistaminen – Arkkitehtuuri ja toteutus

## 1. Johdanto: Tekoälyn toteuttaminen ja miksi tällaista ylipäätään tarvitaan

Tekoälyn (erityisesti suurten kielimallien, LLM) hyödyntäminen tuotantotason ohjelmistoissa ei ole pelkkää "promptien kirjoittamista" ja API-kutsujen tekemistä. Kun LLM-malleja käytetään kriittiseen tiedonkäsittelyyn, auditointeihin tai päätöksentekoon (kuten Cognitive Quorum -järjestelmässä), kohtaamme perustavanlaatuisen ongelman: kielimallit ovat luonnostaan stokastisia (satunnaisia) ja alttiita erilaisille kognitiivisille vinoumille. Ne ovat kuin huippuälykkäitä, mutta äärimmäisen miellyttämisenhaluisia ja helposti väsyviä assistentteja.

Jos järjestelmä rakennetaan naiivisti, tekoäly tuottaa vakuuttavan kuuloisia mutta epäluotettavia tai jopa keksittyjä (hallusinoituja) tuloksia. Se saattaa suosia ensimmäisenä näkemiään asioita, unohtaa keskellä olevan datan tai tehdä nopean intuitiivisen päätöksen ja vasta sen jälkeen keksiä sille tekaistut perustelut (sycophancy).

Tämän vuoksi tarvitaan **insinöörimäistä, arkkitehtuuritason ohjausta**. Emme voi luottaa siihen, että "malli on älykäs". Meidän on rakennettava ohjelmistotason suojamuuri, joka *pakottaa* tekoälyn toimimaan matemaattisen tarkasti, deterministisesti ja auditoitavasti. Tämän dokumentin tarkoitus on avata nämä mekanismit rautalangasta vääntäen.

## 2. Tieteelliset ja kaupalliset opit 2026 (Best Practice)

Vuonna 2026 on tieteellisesti ja kaupallisesti todistettu, että kilpajuoksu "vain suurempiin ja älykkäämpiin malleihin" ei ratkaise luotettavuusongelmaa. Best practice 2026 on siirtynyt mallien koosta **orkestroinnin ja tietorakenteiden laatuun**. 

**Kaupallinen realiteetti:** Yritykset eivät osta "mustia laatikoita". Jos tekoäly tekee arvioinnin tai tuottaa tuloksen, jokainen askel on pystyttävä jäljittämään ja todistamaan. Tätä kutsutaan nimellä **Explainable AI (XAI)**.
**Tieteellinen best practice (Zero-Trust & System 2):** Tekoälyä kohdellaan nollaluottamuksella (Zero-Trust). Sitä ei pyydetä "miettimään ja vastaamaan", vaan siltä vaaditaan tiukkaan tietorakenteeseen (kuten Pydantic V2) pakotettu palaute. Malli pakotetaan Kahnemanin kaksoisprosessiteorian mukaiseen "System 2" -ajatteluun: hitaaseen, analyyttiseen ja systemaattiseen erittelyyn ennen minkään johtopäätöksen tekemistä.

## 3. Matemaattiset ja tilastolliset perusteet

LLM on pohjimmiltaan autokoregressiivinen tilastollinen kone, joka ennustaa seuraavaa tokenia todennäköisyysjakauman perusteella.
Tästä seuraa ohjelmistokehityksen kannalta kriittisiä ilmiöitä:

1. **Stokastisuus ja Determinismi:** Jos funktio on $f(x) = y$, odotamme tietotekniikassa, että tulos on aina sama. LLM:n kohdalla tulos on stokastinen: $f(x) = y \pm \epsilon$. Järjestelmän tehtävä on poistaa $\epsilon$ (satunnaisvarianssi) täysin. Emme voi hyväksyä tilannetta, jossa sama testi ajettuna kahtena eri päivänä antaa eri tuloksen.
2. **Context Fatigue & Lost in the Middle:** Kun mallille syötetään paljon dataa kerralla, huomion (attention) todennäköisyyspainot keskittyvät syötteen alkuun ja loppuun. Keskelle sijoitettu tieto "katoaa" tilastollisesti.
3. **Order Bias (Järjestysharha):** Tulokset korreloivat voimakkaasti sen kanssa, missä järjestyksessä asiat on promptissa. Tilastollisesti malli kiinnittyy herkemmin ensimmäisiin sääntöihin.

## 4. Nykyinen tapa: Epic 52 -muutokset ja ratkaisut

Näiden ongelmien taklaamiseksi Epic 52 -kokonaisuudessa järjestelmän orkestrointi refaktoroitiin täysin. Näin asiat tehdään nyt:

### A) Exhaustive Pydantic Chain-of-Thought (CoT)
- **Miten tehdään:** Emme kysy tekoälyltä "Oliko sääntö tyydytetty, kyllä vai ei?". Sen sijaan pakotamme tekoälyn tuottamaan vastauksen tiukassa JSON-muodossa, jossa avaimet on pakotettu numeeriseen järjestykseen.
- **Rautalangasta:** Mallin on pakko tuottaa ensin `step_1_reasoning_trace` (päättelyketju), sitten `step_2_falsification` (vastaväitteiden etsintä), sitten `step_3_coaching` ja vasta aivan viimeiseksi `step_4_rule_satisfied` (kyllä/ei). Pydantic-kirjasto tarkistaa, että tämä rakenne täyttyy 100%. Tämä pakottaa mallin tekemään työn ja ajattelemaan *ennen* kuin se saa tehdä loppupäätöksen.

### B) Semantic Micro-Batching
- **Miten tehdään:** Iso työkuorma pilkotaan tismalleen maksimissaan 10 atomin kokoisiin eriin (Micro-batch). 
- **Rautalangasta:** Poistimme kaiken satunnaisuuden (kuten `random.shuffle()`). Erät järjestetään aina täysin deterministisesti aakkosnumeerisella hash-lajittelulla. Näin sama data paloitellaan maailman tappiin asti tismalleen samoiksi 10 atomin pinoiksi. Tämä estää Context Fatiguen täysin, koska malli ei koskaan näe liikaa dataa kerralla, ja takaa auditoitavan toistettavuuden.

### C) TaskGroup Concurrency Refactor
- **Miten tehdään:** Rinnakkaisuuden hallinnassa käytetään modernia `asyncio.TaskGroup` -rakennetta ja tiukkaa Semaforia (Semaphore).
- **Rautalangasta:** Jos lähetämme 10 erää tekoälylle tutkittavaksi rinnakkain, meidän on hallittava kaistaa. Semafori on kuin ovimies, joka päästää vain tietyn määrän kyselyitä sisään kerrallaan. TaskGroup varmistaa "Fail-Fast" -periaatteen: jos yksikin tekoälykutsu kaatuu täydellisesti (esim. API on alhaalla), koko ryhmän työ keskeytetään heti puhtaasti sen sijaan, että järjestelmä jäisi jumiin (deadlock) tai jatkaisi virheellisen datan prosessointia.

### D) Reducer Logic & 3-tilalogiikka
- **Miten tehdään:** Kun mikrobätseistä tulee tulokset takaisin, Map-Reduce -yhdistäjä ei tee arvauksia. Se noudattaa tiukkaa 3-tilalogiikkaa: `PASSED`, `FAILED` tai `DLQ` (Dead Letter Queue).
- **Rautalangasta:** Jos yksikin tulos on epämääräinen "null" tai puuttuu, koko pino siirretään hylättyjen listalle (DLQ). Emme koskaan pyöristä tai arvaa puuttuvaa dataa, sillä se korruptoisi koko arvostelumatriisin luotettavuuden.

## 5. Vaihtoehtoiset tavat ja miksi ne EIVÄT onnistu

Miksi emme voisi tehdä tätä helpommin? Tässä vaihtoehdot ja niiden ongelmat:

1. **Vaihtoehto: Annetaan kaikki teksti kerralla yhtenä isona promptina.**
   - **Miksi ei toimi:** "Lost in the Middle" ja Context Fatigue. Malli katsoo alun ja lopun, väsyy, ja jättää huomioimatta 80% säännöistä keskellä. Tilastollinen harha tekee tuloksista arvottomia.
   
2. **Vaihtoehto: Random Shuffle (sekoitetaan järjestys sattumanvaraisesti), jotta järjestysharha katoaa tilastollisesti monella ajolla.**
   - **Miksi ei toimi:** Menetämme täyden determinismin ja auditoitavuuden. Tuotantojärjestelmän (erityisesti finanssi- tai lääketieteessä) pitää antaa tismalleen sama vastaus joka kerta samoilla lähtötiedoilla. "Satunnaistaminen" vie pohjan koko järjestelmän uskottavuudelta.
   
3. **Vaihtoehto: Vapaamuotoinen tekstivastaus ja tulkinta jälkikäteen (ei pakotettua Pydantic CoT -järjestystä).**
   - **Miksi ei toimi:** Sycophancy. Malli ampuu lonkalta päätöksen (esim. "Sääntö on täytetty") ensimmäisen millisekunnin aikana (System 1). Loppu tekstivastaus on vain mallin epätoivoista yritystä perustella tämä nopeasti tehty intuitiivinen heitto. Pakottamalla `step_1`, `step_2` avaimet, mallin on pakko generoida perustelu-tokenit ennen päätös-tokeneita. Koska LLM ei voi palata taaksepäin muuttamaan luotuja tokeneita, sen on pakko "lukea omia ajatuksiaan" ja tehdä lopullinen päätös generoidun rationaalisen ketjun perusteella.
   
4. **Vaihtoehto: Virheiden "pehmeä" ohittaminen (Try-Catch, joka palauttaa esim. tyhjän sanakirjan tai "Ei tietoa" jos API kaatuu).**
   - **Miksi ei toimi:** "Fail-Fast" -arkkitehtuurin vastainen katastrofi. Tämä johtaisi hiljaiseen datakorruptioon (Silent Data Corruption). Raportti näyttäisi vihreää valoa, vaikka todellisuudessa testi jäi ajamatta. On parempi, että järjestelmä räjähtää näkyvästi silmille, kuin että se tuottaa kauniisti formatoitua väärää dataa.
