# Epic 6: XAI Output Extensions (Proaktiivinen Valmentaja)

**Tila:** Suunniteltu (Maaliskuu 2026)
**Konteksti:** Quorum V2 Backend (Structured Outputs) & Flutter Client V2

## Tavoite
Viedä Quorum V2 perinteisestä *"Kylmästä Auditoijasta"* proaktiiviseksi *"Valmentajaksi"* laajentamalla Explainable AI (XAI) -tietokenttien arkkitehtuuria. Mahdollistetaan joustava ja dynaaminen Pydantic-skeema, johon käyttäjä voi Admin Studiossa valita, mitä kaikkea tekoälyn täytyy palauttaa vastauksen kyljessä.

Tämä korvaa kömpelön `require_justification: bool` on/off -kytkimen uudella `output_extensions: list[str]` -arkkitehtuurilla.

## 1. Soveltamisala ja Tuetut Tyypit
Tämä ominaisuus koskee **KAIKKIA** sellaisia prompteja, joihin tekoäly joutuu antamaan erillisen validoidun vastauksen:
*   `type: float` / `int` (Matriisit)
*   `type: string` (Avoimet kysymykset)
*   *Ei koske: `type: instruction` (koska näihin ei odoteta tekoälyltä vastausta, vain LLM:n lukemista).*

## 2. Modulaariset Output Extensions (Sallitut arvot)
*   **[ ] `justification`**: Pakottaa tekoälyn kirjoittamaan `_justification`-kenttään loogisen perustelun sille, miksi se ylipäätään antoi kyseisen arvosanan (esim. 3).
*   **[ ] `citation`**: Pakottaa tekoälyn liittämään suoran leikkaa-liimaa -todisteen lähdetekstistä estämään hallusinointia (`_citation`).
*   **[ ] `coaching`**: Pakottaa tekoälyn antamaan valmennusvinkin tai parannusehdotuksen. *"Mitä toimenpiteitä lukijan tulisi tehdä nostaakseen tämän kriteerin arvosanan vitoseen ensi kerralla?"* (`_coaching`). Pääasiassa laadullisiin matriiseihin.
*   **[ ] `confidence`**: **(`type: float`)** Tekoäly ilmoittaa numeerisen varmuuden (0.0 - 100.0) arviostaan annetun lähtöaineiston perusteella (`_confidence`). Erittäin hyödyllinen epäselvissä tai ristiriitaisissa dokumenteissa. Pydantic pakottaa rajat `ge=0, le=100`.
*   **[ ] `falsification`**: **(`type: string`)** Paholaisen asianajaja. Pakottaa LLM:n argumentoimaan omaa antamaansa arvosanaa vastaan ja etsimään vasta-argumentteja. Estää tehokkaasti vahvistusvinoumaa.
*   **[ ] `missing_context`**: **(`type: string`)** Pakottaa LLM:n erittelemään, mikä tieto aineistosta puuttui, jotta arvosana olisi voinut olla parempi. Valideraa tarjouspyyntöjen laatua.
*   **[ ] `risk_flag`**: **(`type: boolean`)** Riski-indikaattori. Nostaa natiivin Boolen-lipun (True/False) jos aineistossa esiintyy taloudellinen, juridinen tai prosessillinen riski. Voidaan heittää UI:hin automaatti-häläri. Tutkitaan kääntäjässä tarvitaanko kylkeen erillinen `risk_reason: str`.
*   **[ ] `remediation_steps`**: **(`type: list[str]`)** Konkreettiset toimenpiteet. Antaa abstraktin "valmennuksen" sijaan natiivin JSON-arrayn (listan) toimenpiteistä, joilla asia korjataan fyysisesti heti. Yksi indeksi per selkeä askel.
*   **[ ] `emotional_sentiment`**: Sävy ja Asenne. Analysoi arvioitavan alkuperäisen leipätekstin kirjoittajan tunnetilaa juuri kriteerin osalta (esim. rakentava, defensiivinen, ylpeä).
*   **[ ] `theory_link`**: Teoriakehys. Pakottaa vastaajan linkittämään analyysinsa suoraan System Promptissa annettuun tieteelliseen / strategiseen kehykseen (esim. Sitra-Megatrendit).

## 3. Tietokantamallin Päivitys (`v2_core.py` / `db_v2.json`)
*   Vanha tapa: `"require_justification": true`
*   Uusi tapa: `"output_extensions": ["justification", "citation", "coaching"]`

## 4. Kääntäjän Älykkyys (`prompt_compiler.py`)
Kun kääntäjä muuttaa PromptBlockit tekoälyn Pydantic-skeemaksi, se katsoo uutta listaa: 
1. *"Ahaa, `type: float`. Minun pitää vaatia tekoälyltä vastauskenttä `score_leadership` (numero)."*
2. *"Ahaa, `output_extensions` listassa on 'coaching'. Pakotan lisäksi kentän `coaching_leadership` ja annan tekoälylle tiukan ohjeen: 'Kirjoita tähän konkreettinen valmennusvinkki siitä, miten kohde voi parantaa suoritustaan tässä asiassa'."*

## 5. UI:n Renderöintimoottori (Flutter & PDF) - "Automaattinen Tulostus"
Arkkitehtuuri pidetään ihanan yksinkertaisena ja ehdottomana. UI ja PDF-generaattori eivät sisällä monimutkaisia piilotuslogiikoita tai painikkeita.

**Sääntö on yksinkertainen:**
Mitä ikinä olet Admin Studiosta matriisille valinnut (esim. `coaching` ja `justification`), se pakotetaan tekoälyltä JSON-vastaukseen.
Kun Flutter tai PDF-rakentaja näkee, että `_coaching` on olemassa ja siinä on tekstiä, se piirretään kuvaruutuun/paperille automaattisesti! 

Jos et halua tulostaa jotain XAI-laajennusta raporttiin, *älä ruksita sitä päälle Admin Studiossa kyseiselle matriisille*. Näin säästetään myös token-kulut tekoälyn päässä, ja renderöintimoottorilla on vain yksi tehtävä: **Näytä kaikki mitä sille annetaan.**

**Nolla-arvojen Piilottaminen (Graceful Degradation):**
Sääntöön kuuluu oleellisesti myös totaalinen null-turvallisuus. Kaikki UI- ja PDF-komponentit koodataan ehdolla `if (val != null && val.toString().isNotEmpty)`. Joskus LLM saattaa (Pydantic-pakotuksesta huolimatta) epäonnistua yksittäisessä XAI-kentässä tai se saattaa tietoisesti olla antamatta Float-arvosanaa (null). Mikäli arvo (esim. `confidence: float`) puuttuu JSON-vastauksesta tai se on tyhjä, mitään virhelaatikkoa ei piirretä ruudulle (ei "Red Screen of Death"); komponentti katoaa täydellisesti ja hiljaisesti raportista (Graceful Degradation), suojellen loppukäyttäjän lukukokemusta rikkoutumatta.

**Tietokantamallin Ylivalta (Database Truth over AI Truth):**
Renderöintimoottori tarkistaa aina ensin alkuperäisestä `PromptBlock.output_extensions`-listasta (eli Admin Studion asetuksesta), tuliko XAI-kenttää ylipäätään pyytää! Jos tekoäly sattuu jostain syystä "hallusinoimaan" tai vuotamaan ylimääräisen vastauksen (esim. antaa _coaching-vinkin vaikka sitä ei pyydetty), **UI ja PDF eivät piirrä sitä**. Arvoa ei tulosteta, sillä se ei kuulu matriisin malliin. Vain tietokannassa ruksatut ja LLM:n onnistuneesti generoimat kentät saavat näkyvyyden.
- Raporttipyyntöön (`GET /api/v2/execution/.../render?format=pdf`) lisätään uusi query-parametri: `&visible_extensions=justification,risk_flag,coaching`
- Backendin PDF-templatemallintaja lukee URL-parametrin ja rakentaa HTML/PDF-tulosteen jättäen valitsemattomat XAI-datat ohjelmallisesti kokonaan ulos PDF-dokumentista nollamatematiikalla. Käyttäjä saa siis kustomoidun tiivistelmän ajosta.

---

## 6. Suositellut Konfiguraatiot Admin Studiossa (Best Practices)
Tässä kultaiset säännöt sille, mitä `output_extensions` -rasteja kannattaa asettaa erilaisiin PromptBlock-kriteereihin Admin Studiossa:

### 1. Kevyet Avoimet Kysymykset (Tyyli: "Tiivistä tekstin pääpointit")
* **Suositus:** `[]` (Tyhjä, ei mitään)
* **Miksi:** Pelkkä `type: string` riittää. Turha pakottaa tekoälyä perustelemaan omaa tiivistelmäänsä ("Miksi tiivistit näin?"). Säästää token-kuluja ja viivettä.

### 2. Vakiomatriisit & Perusarvioinnit (Tyyli: "Arvioi johtamistyyli 1-5")
* **Suositus:** `["justification", "citation", "coaching"]`
* **Miksi:** Pakollinen auditoitavuus. Käyttäjä näkee heti perustelun ja onko se totta (lähdelainaus). Coaching antaa palautteen saajalle positiivisen suunnan jatkoon.

### 3. Korkean Riskin Auditoinnit & Tarjouspyynnöt (Tyyli: "Täyttääkö GDPR:n?")
* **Suositus:** `["justification", "citation", "confidence", "falsification", "missing_context", "risk_flag"]`
* **Miksi:** Jos asialla on oikeudellisia tai taloudellisia seurauksia, tekoälyn on paljastettava kuinka varma se on (`confidence`). `falsification` haastaa oman päätöksen, ja `missing_context` heilahtaa jos dokumentaatio onkin vain puutteellista eikä välttämättä hylättyä.

### 4. Prosessipoikkeamat & Virhelokit (Tyyli: "Etsi virheet logista")
* **Suositus:** `["justification", "citation", "risk_flag", "remediation_steps"]`
* **Miksi:** Ei tarvita valmennusta tai tunneanalyysia. Vaaditaan tiukka numeerinen hätäsuunnitelma (`remediation_steps`) siitä, miten virhe ratkaistaan *heti*, ja onko laitteisto nyt vaarassa (`risk_flag`).

### 5. Kvalitatiivinen HR / Mentorointi (Tyyli: "Analysoi työntekijän vuorovaikutusta")
* **Suositus:** `["justification", "coaching", "emotional_sentiment", "theory_link"]`
* **Miksi:** Ei tarvita armotonta faktantarkistusta (citation/falsification), vaan pehmeämpi analyysi asenteesta (`emotional_sentiment`) ja peilaus yrityksen johtamisteoriaan (`theory_link`). Valmennusvinkki on tässä tärkein työkalu.
