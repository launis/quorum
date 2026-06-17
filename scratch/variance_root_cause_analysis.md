# Root Cause Analysis (RCA): LLM-Arviointien Varianssin Syyt ja Seuraukset

## 1. Yleiskatsaus Ongelmaan
Vaikka teknisesti kaatuneet arvioinnit poistettiin, kahden täydellisen ajon välillä havaittiin silti **19,1 % "aito" varianssi** (`gemini-2.5-flash` -mallilla). Tämä tarkoittaa, että malli päätyy matemaattisesti eri johtopäätökseen noin joka viidennessä kysymyksessä täsmälleen samalla syötteellä (Zero-Shot).

Tämä RCA porautuu tietokannasta nostettujen esimerkkisääntöjen kautta siihen, **miksi** malli oikkuilee.

## 2. Varianssin Pääsyyt (Root Causes)

### Syy A: Sääntöjen Abstraktius ja Subjektiivisuus (Zero-Shot -tulkinnanvaraisuus)
Esimerkkinä **tda_8275735bde0244e2bdbf3ab915838d59** (Performatiivisuus ja Goodhartin laki):
> *"The user demands optimization of a surface metric without linking it to a qualitative real-world outcome. Do not accept if the metric is explicitly tied back to a measure of effectiveness."*

- **Analyysi:** Sääntö on erittäin filosofinen. Mikä tarkalleen erottaa "pintatason metriikan" (surface metric) ja "laadullisen tosimaailman lopputuloksen"? 
- **Seuraus (1.000 Entropia):** Koska mallille ei anneta esimerkkejä, se joutuu arpomaan. Ensimmäisessä ajossa se tulkitsi, että "1 sivun raportti" on hyödyllinen työkalu (FALSE). Toisessa ajossa se tulkitsi sen puhtaaksi pintametriikaksi (TRUE). Zero-Shot (nollaesimerkin) tilassa LLM:n semanttinen raja on liian häilyvä.

### Syy B: "Compound Rules" eli Moniosaiset Säännöt ja Kognitiivinen Ylikuorma
Esimerkkinä **tda_453ddf8b14a442e988836098e3c7b55c** (Oman tiedon rajat / Riskiarviointi):
> *"the risk is identified but no physical action verb follows to mitigate it. <ambiguity_protocol>ABSOLUTE MITIGATION ENFORCEMENT: You must strictly scan the paragraph containing the risk identification marker. If the paragraph contains a physical action verb that describes a technical, administrative, or physical mitigation or control, the absence of mitigation is falsified..."*

- **Analyysi:** Sääntö vaatii kolmen erillisen asian samanaikaista hallintaa: (1) Etsi riski, (2) Etsi fyysinen toimintaverbi, (3) Varmista että molemmat ovat samassa kappaleessa.
- **Seuraus:** Kun nopea ja kevyempään päättelyyn tarkoitettu `gemini-2.5-flash` saa syötteekseen massiivisen PDF-dokumentin ja joutuu prosessoimaan tällaisen kolmivaiheisen säännön, iskee **"Attention Exhaustion"** (huomiokyvyn ylikuormitus). Se löytää riskin, mutta saattaa skannata toimintaverbin vahingossa seuraavasta kappaleesta. Seuraavalla kerralla se suorittaa saman tiukemmin ja muuttaa mieltään.

### Syy C: Lohkojen Koko (Chunking Limits)
Backend-parametreissa (`enums.py`) on asetettu:
- `SCHEMA_MAX_EVALUATIONS = 10`
- `SCHEMA_MAX_CHUNK_RECORDS = 15`

- **Analyysi:** Pakotamme mallin arvioimaan 10-15 näin monimutkaista sääntöä *samassa* API-kutsussa ja tuottamaan valtavan, jäsennellyn JSON-vastauksen.
- **Seuraus:** Kun malli joutuu pitämään työmuistissaan 15 eri sääntöä kerrallaan ja skannaamaan koko raporttia niiden läpi, sen päättelyn tarkkuus laskee väistämättä.

## 3. Ratkaisuehdotukset Varianssin Merkittävään Pienentämiseen

Jotta varianssi saataisiin pienennettyä radikaalisti (esim. alle 5 prosenttiin), meidän tulisi toteuttaa seuraavat toimenpiteet:

### Toimenpide 1: Few-Shot Esimerkkien Injektio (Vaikutus: Erittäin Suuri)
Abstraktit säännöt muutetaan "ohje + esimerkki" -muotoon `seed_data.json` -tiedostossa.
> **Ennen:** *"Optimize a surface metric."*
> **Jälkeen:** *"Optimize a surface metric. <example>TRUE: Make this exactly 1 page.</example> <example>FALSE: Make this 1 page so the board can read it quickly.</example>"*
Tämä pakottaa mallin semanttisen avaruuden ankkuroitumaan esimerkkeihin, eikä se enää "arvo" rajaa itse.

### Toimenpide 2: Sääntöjen Atomisointi (Vaikutus: Suuri)
"A + B + C" -säännöt pilkotaan, tai niitä yksinkertaistetaan merkittävästi. Jos malli arvioi vain yhtä selkeää asiaa kerrallaan, sen huomiokyky ei petä.

### Toimenpide 3: Lohkokokojen Pienentäminen (Vaikutus: Kohtalainen)
`enums.py` -tiedostosta pienennetään arvoja:
`SCHEMA_MAX_EVALUATIONS = 5`
Tämä vapauttaa mallin kognitiivista kapasiteettia, koska sen tarvitsee pitää työmuistissaan vain 5 sääntöä kerrallaan. (Tämä tosin vaatii sen Epic 79 -konesalivalitsimen, jottei pienempi lohkokoko räjäytä 429-virheiden määrää API-kutsujen kasvaessa).

### Toimenpide 4: Mallitason Vaihto (Vaikutus: Massiivinen)
Jos 19 % varianssi on ehdottoman ei-hyväksyttävää eikä sääntöjen muokkaus auta tarpeeksi, looginen ratkaisu on vaihtaa laatuportteja suorittava malli `gemini-2.5-flash` -> `gemini-2.5-pro`. Pro-malli on koulutettu raskaaseen, monivaiheiseen kausaalipäättelyyn ja se kykenee säilyttämään tiukan huomiokyvyn monimutkaisimmissakin *Compound Rules* -säännöissä.
