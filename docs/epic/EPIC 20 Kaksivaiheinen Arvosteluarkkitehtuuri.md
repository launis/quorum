# **EPIC: Vikasietoinen ja Syvä-atomisoitu Arviointimoottori (Threshold-BARS)**

## **1\. Ydinkonsepti ja Filosofia**

Tämä arkkitehtuuri perustuu mekaaniseen ja tilastollisesti kestävään koneistoon, joka poistaa perinteisen LLM-arvioinnin haurauden.

> [!IMPORTANT]
> **Ratkaistu haaste:** Jos tekoälyn on arvioitava abstraktia tavoitetta (esim. "Käyttäjä osoittaa epistemologista nöyryyttä"), asettuu se alttiiksi kognitiiviselle värinälle (hallusinaatiot, mielistely). Jos taas vaaditaan 100 % täydellisyyttä tiukoissa kriteereissä, yksikin tekoälyn tekemä lukuvirhe kaataa koko arvioinnin nollaan (False Negative -ansa). Tämä järjestelmä ohittaa molemmat sudenkuopat.

**Ratkaisu:** 
1. **Laajentaminen (Kerta-ajo):** Järjestelmä räjäyttää yksittäisen ihmisen kirjoittaman abstraktin kriteerin automaattisesti 15–20 konkreettiseksi mikro-atomiksi ennen kriteeristön käyttöönottoa.
2. **Kynnysarvo (Runtime):** Arvioinnissa ei vaadita 100 % osumaa, vaan riittää, että tekoäly löytää tekstistä todisteet esimerkiksi 75 prosenttiin näistä mikro-atomeista. Massa poistaa yksittäisten virheiden vaikutuksen luoden matemaattisen vesiputouksen.

---

## **2\. Arkkitehtuurin Vaiheistus (Step-by-Step)**

### **Vaihe 1: Pääkäyttäjän syöte (Human Input)**

Pääkäyttäjä (substanssiasiantuntija) luo perinteisen, yksinkertaisen BARS-matriisin. Hänen ei tarvitse huomioida tekoälyn rajoitteita.

* Pääkäyttäjä määrittelee 5-portaisen asteikon.  
* Hän kirjoittaa jokaiseen soluun vain **1–2 inhimillistä lausetta** (esim. Taso 4: *"Käyttäjä kyseenalaistaa mittarin luotettavuuden ja tunnistaa tilanteeseen liittyvät epävarmuudet."*).

### **Vaihe 2: Syvä-atomisointi ja Obfuskointi (Kerta-ajo / Design-Time)**

Tämä vaihe ajetaan vain kerran uuden matriisin tallennuksen yhteydessä. Se lukitsee "mittatikun" tietokantaan oikeudellisesti pitäväksi vakioksi.

1. **Kääntäjä-AI aktivoituu:** Järjestelmä syöttää pääkäyttäjän 1-2 lausetta erikoispromptatulle Kääntäjä-tekoälylle.  
2. **Laaja todistuspinta (Expansion):** Tekoäly tuottaa tästä yhdestä solusta **15 erilaista binääristä (Kyllä/Ei) väitettä**, jotka mittaavat samaa asiaa eri kulmista (sanavalinnat, kysymysrakenteet, konteksti).  
3. **Tunnistamattomuus (Obfuscation):** Kääntäjä-tekoäly on pakotettu poistamaan väitteistä kaikki toimialaspesifit termit.  
   * *Esimerkki mikro-atomista:* "Tekstissä esiintyy sana tai lauserakenne, joka viittaa epäilykseen tai riskin mahdollisuuteen."  

> [!NOTE]
> **Mekanismin poikkeus ("Scaffolded-tila"):** Täydellinen obfuskointi voi poistaa tarpeellisen toimialasanaston. Turvamekanismina, jos Kääntäjä-AI tunnistaa kriteerin vaativan syvää substanssiosaamista toimiakseen, se merkitsee kyseiset atomit "Scaffolded"-tilaan. Näille spesifeille kysymyksille ajetaan arvioinnissa *Rubric-aligned CoT* -malli, joka antaa tekoälylle luvan nähdä osan alkuperäisestä rubriikista kontekstin ymmärtämiseksi.

4. **Tietokannan lukitus (Seed Vault):** Näin syntynyt massiivinen JSON-matriisi (esim. 5 tasoa x 15 atomia = 75 atomia per ulottuvuus) tallennetaan ja lukitaan tietokantaan. **Atomeita ei enää koskaan generoida tai muuteta ajonaikaisesti.**

### **Vaihe 3: Runtime-ajon valmistelu (Rakenteellinen Silppuaminen)**

Kun loppukäyttäjä syöttää dokumenttinsa arvioitavaksi:

1. Python-backend noutaa lukitun 75 atomin matriisin tietokannasta.  
2. **Flatten & Shuffle:** Python "litistää" rakenteen. Se poistaa tiedot siitä, mitkä atomit kuuluvat millekin tasolle, ja sekoittaa 75 mikro-atomia täysin satunnaiseen järjestykseen (random.shuffle).  
3. Tässä vaiheessa kysymyspatteristo on täysin kontekstiton: se on vain lista irrallisia, satunnaisia tekstianalyysikysymyksiä.

### **Vaihe 4: Sokea Tiedonerottelu (Eristetty Runtime-AI)**

Nyt arvioiva tekoäly (LLM) suorittaa skannauksen tiukoissa rajoitteissa (Fencing).

1. **Nollavarianssi:** LLM:n lämpötila on lukittu arvoon T=0.0. Järjestelmällä ei ole pääsyä internetiin (ei MCP-työkaluja).  
2. **Sokea suoritus:** LLM ei tiedä arvioivansa taitotasoa 1–5. Sille annetaan ainoastaan käyttäjän teksti ja lista 75 satunnaisesta väitteestä.  
3. **Context-isolated Micro-CoT:** Tekoälyn ainoa tehtävä on palauttaa massiivinen JSON-taulukko, jossa se on käynyt läpi jokaisen 75 väitteestä. 
   * quote: Sanatarkka lainaus tekstistä (tai null).  
   * reasoning: Yhden lauseen perustelu.  
   * boolean: True tai False.

> [!IMPORTANT]
> Perinteinen *Rubric-aligned CoT* on hylätty tietoisesti tässä nimenomaisessa vaiheessa absoluuttisen obfuskoinnin ja objektiivisuuden saavuttamiseksi asiantuntijoharhojen eliminoimiseksi.  

LLM:n suoritus on puhtaasti mekaanista skannausta. Tämän jälkeen tekoäly sammutetaan tästä prosessista.

### **Vaihe 5: Vikasietoinen Vesiputouslaskenta (Python-moottori)**

Python-backend (joka pitää hallussaan matriisin alkuperäistä "salaista karttaa") ottaa LLM:n tuottaman 75 True/False -tuloksen listan ja kokoaa palapelin luotettavasti luvuiksi.

1. **Re-mapping:** Python sijoittaa satunnaistetut vastaukset takaisin omille paikoilleen (Tasot 1–5).  
2. **Kynnysarvon laskenta (Hit Rate):** Python tarkistaa, ylittyykö ennalta säädetty kynnys (esim. 0.75 eli 75 %).

```python
def check_level_passed(cell_atoms, threshold=0.75):
    total_atoms = len(cell_atoms) # Esim. 15
    hits = sum(1 for atom in cell_atoms if atom['boolean'] == True) # Esim. 12
    hit_rate = hits / total_atoms # 12 / 15 = 0.80 (80%)
    return hit_rate >= threshold # 80% >= 75% -> TRUE (Taso saavutettu)
```

3. **Vesiputous:** Python nousee tasoja ylöspäin (Taso 1 -> Taso 2...). Heti kun vastaan tulee taso, jossa osumatarkkuus jää *alle* 75 %, vesiputous katkeaa ja edellinen taso lukitaan lopulliseksi arvosanaksi. 

> [!NOTE]
> Tämä ratkaisu tekee arvioinnista 100 % deterministisen ja vikasietoisen suhteessa LLM:n satunnaiseen epätarkkuuteen.

### **Vaihe 6: Valmentava Synteesi (XAI & MCP Shift)**

Kun tuomio on lukittu matemaattisesti, järjestelmä hyödyntää lopuksi valmentavaa tekoälymallia (Synteesi-AI).

1. **Asetukset:** Tällä mallilla on luovuutta (esim. T=0.3) ja lupa etsiä netistä tietoa (MCP Grounding).  
2. **Datan syöttö:** Synteesi-AI:lle syötetään Pythonin antamat kylmät faktat: *"Käyttäjä saavutti Tason 3 (osumatarkkuus 85%). Taso 4 hylättiin (osumatarkkuus vain 40%). Erityisesti nämä mikro-atomit [A, B, C] jäivät puuttumaan."* Lisäksi Synteesi-AI käyttää apunaan alkuperäistä asiantuntijarubriikkia.
3. **Raportti (Rubric-aligned Chain-of-Thought):** Synteesi-AI hyödyntää "Rubric-aligned Chain-of-Thought (Scaffolded CoT)" -mallia. Tämä mahdollistaa sen, että irrallisista ja obfuskoiduista atomeista sidotaan yhteen laadukas, koulutuksellisesti pätevä ja tavoitteisiin peilaava sanallinen arviointi: *"Pääsit tasolle 3. Suorituksesi oli hyvä, mutta jäit paitsi tasosta 4, koska tekstistäsi puuttui selkeä epävarmuuksien tunnistaminen. Ensi kerralla, muista lisätä tekstin loppuun kappale, jossa haastat omia oletuksiasi."* 

> [!TIP]
> Tämä synteesi kytkee sokeat osumat takaisin alkuperäisen matriisin sanavalintoihin tavalla, joka huomioi pedagogisesti koko suorituksen.

---

## **3\. Miksi tämä on absoluuttinen nykystandardi?**

1. **Ratkaisee False Negative -ongelman:** Arviointi ei kaadu siihen, että sokea tekoäly on yhdessä 75 atomin kysymyksessä liian ankara tai tekee lukuvirheen. 25 % virhemarginaali imee sisäänsä tekoälyn tilastollisen varianssin luonnostaan.
2. **Kuminen mittatikku on eliminoitu (Oikeusturva):** Kääntäjä-tekoäly on tehnyt mikro-atomit vain kerran. Kaikki käyttäjät arvioidaan täysin samalla 75 atomin listalla. Auditoija voi tarkistaa tietokannasta heti, mitkä kysymykset johtivat mihin tahansa arvosanaan.  
3. **Täydellinen Sokeus (Obfuskointi):** Koska kysymykset tarkistetaan riisuttuna asiayhteydestä, Runtime-tekoäly ei kykene päättelemään mitä taitoa se on arvioimassa. Joten hallusinaatiot ja mielistely-yritykset on teknillisessä mielessä tehty mahdottomiksi.  
4. **Vaivattomuus Pääkäyttäjälle:** Asiantuntija on kirjoittanut vain lauseita per taso. Nykymalli hoitaa niiden matemaattisen työstämisen itse.

---

## **4\. Rubric-CoT -logiikka ja järjestelmän kokonaisvaltainen toiminta**

Rubric-CoT -logiikka vaikuttaa saumattomasti EPIC-moottorin integraatiossa. Tämä vahvistaa sen, että järjestelmä ottaa kaikki hahmotettavat nykytilanteet huomioon automaattisesti:

> [!NOTE]
> **Kokonaisvaltainen suunnittelu (Holistinen toiminta):**
> Arkkitehtuuri on modulaarinen ja nykyisellään se kattaa täysin niin kaksoismoottori-auditoinnin kuin kääntäjä-tekoälyn prosessin. Kaikki rakenteet toimivat osana nykyistä jatkuvaa vuota, taaten pettämättömän laadun eri skenaarioissa.

**A. Pedagogisesti yhtenäisen palautteen tuottaminen (Vaihe 6)**
Sokea Python-moottori on erinomainen laskemaan pisteet ilman harhaa (bias), mutta pelkkään inhimilliseen palautteeseen sovelletaan vaihetta 6. Synteesi-AI hyödyntää alkuperäistä asiantuntijarubriikkia *Rubric-aligned CoT* -rakenteen mukaisesti. Se kirjoittaa rakentavan palautteen kytkien sokeat osumat suoraan oppimistavoitteiden asettamiin alkuperäisiin sanavalintoihin, huomioiden jokaisen käyttäjän yksilillisen suoritustason kaikenkattavasti.

**B. Kääntäjä-AI:n laadunvarmistus (Vaihe 2)**
Estääksemme 15 mikro-atomin ajautumisen ohi aiheen (Context Drift), Kääntäjä-AI:n promptissa on tiukka *Rubric-CoT -vaatimus*. Tekoäly kirjoittaa jokaisen atomin kohdalla auki, miten kyseinen binäärinen atomi pohjautuu täydellisesti alkuperäiseen arviointikriteeriin, jotta laatu on taattu alusta lähtien.

**C. Dual-Engine Auditointi (Väärät positiiviset ja poikkeamat)**
Äärimmäisen objektiivisuuden saavuttamiseksi kriittiset dokumentit kulkevat järjestelmän hallinnoimassa rinnakkaisessa tuplaputkessa:
1. **Sokea, matemaattinen EPIC-vesiputous** (Karsii mielistelyn ja virhe-ansoittumiset kynnysarvolaskennallaan).
2. **Holistinen Rubric-CoT -tuomari** (Käsittelee kokonaisuutta inhimillisesti asiantuntijarubriikkia kunnioittaen).

Nämä moottorit toimivat rinnakkain varmana sisäänrakennettuna check-and-balance -mekanismina. Mikäli moottoreiden välinen tulkinta ammottaa ääripäissä (esim. Taso 4 vs. Taso 2), järjestelmä liputtaa dokumentin välittömästi manuaaliseen ja asiantuntijan suorittamaan arviointiin. Tämä mekanismi kerää datassa ilmenevät poikkeamat huolellisesti ylös ylläpitääkseen laadun täydellistä hallintaa.