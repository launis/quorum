# **🛡️ Antigravity V6.1: Agenttisten Työnkulkujen (Workflows) Käyttöopas**

Tämä opas on suunniteltu ohjelmistoarkkitehdille (sinulle). Se selittää .agents/workflows/ \-hakemiston työkalujen tarkoituksen, käyttöajankohdan sekä sisäisen logiikan.

Järjestelmä perustuu vahvasti **Agenttiseen Orkestrointiin**. Emme vain "juttele" tekoälyn kanssa, vaan ohjaamme sitä tiukoissa kognitiivisissa tiloissa (Tiers 1-5). Tämä estää tekoälyä hallusinoimasta, pakottaa sen testaamaan koodinsa (TDD) ja eliminoi kontekstiamnesian.

Vuoden 2026 päivityksessä agentilta on viety oikeus arvailla koodin laatua. **Tekoäly on vain työntekijä – lokaalit Python-skriptit ovat armoton tuomari.**

## ---

**1\. Työnkulkujen Komennot (Milloin ja Miksi?)**

Agentin komentaminen tapahtuu kutsumalla työnkulkua chattiin sen nimellä (esim. *"Aja /tier1-planner"*). **Kultainen sääntö (Strict Execution Mandate):** Tekoäly on koodattu kieltäytymään automaattisesta koodaamisesta. Jokainen vaihe vaatii tekoälyn herättämisen oikealla komennolla.

### **🗺️ Suunnittelu ja Toteutus**

* **/tier1-planner (Okkultistinen Arkkitehti):**  
  * **Milloin:** Uuden laajan ominaisuuden (Epic) tai arkkitehtuurimuutoksen aloitus.  
  * **Mitä se tekee:** Aktivoi **DISCOVER-lukon** (skannaa oikeat tiedostot ensin, kieltää arvaamisen). Tuottaa loogisesti jaetun virstanpylvässuunnitelman implementation\_plan.md. Koodia ei tuoteta vielä riviäkään.  
* **/tier2-execute (Mekaaninen Toteuttaja):**  
  * **Milloin:** Kun Tier 1 suunnitelma on valmis ja hyväksytty.  
  * **Mitä se tekee:** Pakottaa agentin toteuttamaan suunnitelmaa vain **yhden askeleen kerrallaan**. Vaatii koodauksen, testit ja Laatuportin (Audit Loop) komentojen luovutuksen sinulle ajettavaksi, ennen kuin se saa jatkaa.

### **🛠️ Päivittäinen Työ ja Debuggaus**

* **/tier3-feature-refactor (Yksittäinen Koodari):**  
  * **Milloin:** Yksittäisen ominaisuuden rakennus tai refaktorointi ilman isoa suunnitelmaa.  
  * **Mitä se tekee:** Toimii nopeana koodausassistenttina, mutta sisältää ehdottoman TDD-mandaatin: koodia ei rakenneta ilman yksikkötestiparia (pytest / flutter test).  
* **/tier3-database-reset (Tietokannan Siivooja):**  
  * **Milloin:** Lokaalin TinyDB-kehityskannan pyyhintä ja uudelleensiemennys (seed\_data.json) turvallisesti ilman manuaalisia koodimuutoksia.  
* **/tier4-bug-hunting (Verikoira & Testilukko):**  
  * **Milloin:** Sovellus kaatuu (esim. Red Screen tai 500 API Error).  
  * **Mitä se tekee:** Aktivoi **PROOF OF FAILURE** \-lukon. Agentin on ensin kirjoitettava bugin toisintava yksikkötesti ja *pysähdyttävä*. Se ei saa jatkaa, ennen kuin ajat testin ja liimaat punaisen virhelokin chattiin. Tämä estää oireiden summittaisen paikkailun purkkakoodilla.

## ---

**2\. Kognitiiviset Lukot ja "Shift-Left" \-Testaus**

Antigravity V6.1 ei luota tekoälyn "hyvään tahtoon" tai kykyyn arvioida omia virheitään (vahvistusharha). Olemme siirtäneet valvonnan fyysisille Python-skripteille ja rajoittaneet agentin psykologiaa.

### **Tekoälyn Psykologian Rajoitteet**

1. **Pakotettu Ajattelu (Chain of Thought):** Agentti ei saa aloittaa koodausta miettimättä. Sen on pakko prosessoida arkkitehtuuri ääneen \<thinking\_process\> \-blokissa, jotta se ei lukkiudu huonoihin impulsseihin.  
2. **Kirurgiset Muokkaukset:** Agentti ei saa typistää tiedostoja kirjoittamalla laiskasti // ... rest of the code .... Sen on toimitettava kokonainen rakenne tai käytettävä MCP-muokkaustyökaluja tarkasti.  
3. **Circuit Breaker (Ikuisen luupin esto):** Jos laatuportti tai testi kaatuu täsmälleen samaan virheeseen 3 kertaa peräkkäin, agentin "sulake" laukeaa (\<circuit\_breaker\_tripped\>). Se lopettaa sokean arvailemisen automaattisesti ja odottaa ihmisen apua.  
4. **Dependency Firewall:** Agentti ei saa asentaa ongelmien kiertämiseksi uusia NPM/PIP/Pub-kirjastoja. Kaikki pitää ratkaista natiivilla koodilla.

### **Deterministinen Python-Tuomaristo**

1. **Network Airgap:** conftest.py katkaisee fyysisesti ulkoiset verkkokutsut. Tekoäly ei voi vahingossa kirjoittaa testiä, joka polttaa LLM-pilviresursseja soittamalla oikeisiin rajapintoihin.  
2. **Kielletty JSON-hallusinointi:** Tekoäly ei saa arvailla mock-dataa käsin. Sen on pakko käyttää polyfactory \-kirjastoa (esim. UserFactory.build()), joka luo 100 % validia dataa suoraan Pydantic-malleista.  
3. **Kattavuuslukko (Coverage \>90%):** Backendin Audit Loop kaatuu fyysisesti, jos uuden koodin testikattavuus on alle 90%. Agentti pakotetaan koodaamaan testit puuttuville riveille ennen hyväksyntää.

## ---

**3\. Kontekstin Vaihto: "Viestikapula" (Tier 5 Clean Room)**

Kielimallit kärsivät "kontekstiamnesiasta" (Context Fatigue). Kun chat-sessio venyy tuntien mittaiseksi, tekoäly väsyy ja alkaa vuotaa muistiin hallusinaatioita ("Prompt Bleed"). Lääke tähän on armoton ikkunoiden nollaus uudella, jaetulla Tier 5 \-protokollalla.

### **Askel 1: Vanhan chatin sulkeminen (Lähettäjä)**

Kun yksi tiketti on valmis, siirrytte Backendistä Frontendiin, tai tekoäly alkaa väsyä:

1. Kirjoita chattiin: **/handover**.  
2. Tekoäly skannaa tekemänne työn, niputtaa oikeat koodi- ja testitiedostot ja tuottaa valmiin kopioitavan viestikapulan (Payloadin), joka sisältää suoritetun liiketoiminta-arvon (--done) ja seuraavan askeleen (--next).  
3. Kopioi tekoälyn antama Git-komento ja tallenna työsi. **Sulje nykyinen chat-ikkuna kokonaan.**

### **Askel 2: Uuden chatin herätys (Vastaanottaja & Sniper)**

1. Avaa täysin puhdas chat-ikkuna.  
2. Liimaa kenttään tekoälyn antama herätyskomento (esim. /tier5-resume backend\_v2/user.py \--done="..." \--next="...").  
3. Uusi, terävä tekoäly lukee siirretyt tiedostot, **auditoi ne säälimättömästi (Zero-Shortcut Audit)** edellisen ikkunan sääntörikkeiden varalta, ja asettuu valmiustilaan jatkamaan työtä puhtaalta pöydältä.

## ---

**4\. Massiiviset Refaktoroinnit (Hardening Loops)**

Kun haluat siivota kokonaisia legacy-hakemistoja kerralla (esim. koko backend\_v2/routers) uuden V6.1-arkkitehtuurin mukaisiksi, käytä työnkulkuja **/tier2-hardening-backend** tai **/tier2-hardening-frontend**.

1. **Kartoitus (Mapping):** Agentti listaa hakemistot ja tekee tarkistuslistan chattiin. Odottaa komentoa *"PROCEED"*.  
2. **Auditointi (Yksi kerrallaan):** Agentti lukee *vain yhden* alihakemiston tiedostot kerrallaan. Vertaa niitä sääntöihin (esim. onko käytetty Pydanticin natiivia Field() funktiota) ja listaa virheet. Odottaa komentoa *"FIX"* tai *"NEXT"*.  
3. **Korjaus (Remediation):** Agentti korjaa koodin suoraan sisäisillä työkaluillaan ja antaa sinulle Audit-komennon lokaaliin testaukseen.  
4. **Huom:** Tee Tier 5 /handover aina 3-5 korjatun kansion välein estääksesi agentin ylikuormittumisen\!

## ---

**5\. Työnkulkujen Kultainen Sääntö: Atomiset Tallennukset**

Tekoälyn kanssa koodatessa yhden ison "perjantai-iltapäivän commitin" taktiikka on valtava riski. Siksi järjestelmä pakottaa säännön: **Atomic Checkpoint Mandate**.

### **🍄 Pelikonsolin "Save States" (Super Mario \-malli)**

Ajattele Gitiä pelikonsolin tallennuspisteenä. Jokainen looginen, testattu askel tallennetaan välittömästi Gitiin tarkoilla poluilla (esim. git add backend\_v2/routers/user.py && git commit \-m "feat: uusi reititin").

* **Ei komentoa git add . :** Jotta lokaalit kehitystietokannat (esim. db\_v2.json) ja lokaali roska eivät päädy repoosi, tekoäly antaa aina täsmälliset tiedostopolut.  
* **Voittamaton Rollback:** Jos agentti hallusinoi askeleessa 5 ja tuhoaa tiedoston, aiemmat 4 askelta ovat yhä turvassa. Ajat vain lokaalisti git restore . ja olet sekunneissa takaisin edellisessä turvallisessa tallennuspisteessä. Tekoälyn virheet ovat merkityksettömiä, kun sinulla on turvaverkko.  
* **Puhtaat tauot:** Koska sinulla ei roiku tallentamatonta massaa työtilassasi, voit koska tahansa sulkea chat-ikkunan ilman pelkoa työn menettämisestä.

## ---

**6\. Manuaaliset Ylläpitotyökalut (Audit Loops)**

Nämä skriptit sijaitsevat scripts/ \-hakemistossa. Tekoäly antaa näitä sinulle ajettavaksi, mutta ne ovat elintärkeitä myös manuaalisessa koodauksessa varmistamassa laatuportin (The Universal Quality Gate) läpäisyn.

### **🦋 Frontend Audit Loop (Flutter)**

**Käyttö:** Aina ennen Git commitia client\_app\_v2 \-muutoksissa.

PowerShell

uv run python scripts/flutter\_audit\_loop.py client\_app\_v2

* Hoitaa automaattisesti koodin formatoinnin (dart format) ja staattisen analyysin (dart analyze).  
* **Datan ja Rakenteiden muutos (--build):** Jos muutit @riverpod tai @freezed \-annotaatioilla varustettuja tiedostoja, aja skripti tällä liitteellä. Se pakottaa build\_runner generaattorin päivittämään rakenteet ensin.

### **🐍 Backend Audit Loop (Python)**

**Käyttö:** Aina ennen Git commitia backend\_v2 \-muutoksissa.

PowerShell

uv run python scripts/backend\_audit\_loop.py backend\_v2

* Hoitaa automaattisesti ruff-korjaukset, formatoinnin, mypy-tyyppitarkastuksen ja estää arkkitehtuurivirheet (Archon).  
* **OpenAPI Generointi (--openapi):** Päivittää openapitools.json rajapinnat automaattisesti, kun muutat reitittimiä tai Pydantic-malleja.  
* **Testien ajo & Kattavuuslukko (--test):** Ajaa Pytestin ja **kaatuu heti, jos muokatun koodin testikattavuus on alle 90%**.