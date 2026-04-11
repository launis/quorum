# 🏛️ Zero-Trust Arkkitehtuuri & Tallennusmekanismit (EPIC 20)
**Tila:** Verifioitu & Tuotannossa (Huhtikuu 2026)

Tämä dokumentti purkaa auki "Kaksivaiheisen Arvosteluarkkitehtuurin" (Epic 20) konepellin alusen. Ydinongelmana oli taata tekoälyn *Nollaluottamus (Zero-Trust)* sekä se, ettei massiivinen XAI-lokidata (Explainable AI) lamauta tai räjäytä tietokannan kokoa ja hidasta "Fail-Fast" infrastruktuuria.

---

## 1. Kuumadata vs. Kylmädata (Suorituskykyarkkitehtuuri)

Antigravity V2 irrottaa operatiivisen metadatan ja massiivisen oikeuslääketieteellisen (forensic) lokidatan fyysisesti toisistaan:

* **Kuumadata (TinyDB `db_v2.json`):**
  Ladataan suoraan Python-ympäristön RAM-muistiin. Sisältää ainoastaan konfiguraatiot (Workflows, PromptBlocks, Matrices) sekä **suoritusten metadatan** (`executions`-taulu). Metadatasta löytyvät vain ajo-ID:t (esim. `exe_c83d...`) sekä laskettu numeerinen `final_score`. Tämän ansiosta järjestelmän reitittimet prosessoivat oikeustarkistukset ja käyttöliittymän litteät kyselyt `O(1)` millisekunnin viiveellä.
* **Kylmädata (Storage Service File Blobs):**
  Itse arviointiprosessi generoi tuhansia rivejä Micro-CoT tekstiä ja useiden megatavujen kokoisia Base64-pakattuja PDF-möhkäleitä. Koko tämä massiivinen The Hookin palauttama tilapuu (State Tree) dumpataan irralliseksi **`.json`** -tiedostoksi levylle S3/Kylmävarastointi -tyylillä. 
  Polku: `c:\src\quorum\data\files\executions\[EXEC_ID]\execution_trace.json`.

---

## 2. Kognitiivinen Liukuhihna (6- Vaiheinen Tehdas)
Tekoälyn hallusinaatiot ja laiskuus on estetty silppuamalla tehtävä pieniin deterministisiin atomeihin:

1. **Human Input**: Asiantuntija luo BARS-matriisin selkokielellä.
2. **Deep Atomization (Obfuskointi)**: "Kääntäjä-AI" pilkkoo arvostelukriteerit 75:ksi "Mikro-atomiksi" neutraaliin muotoon piilottaen alkuperäisen viitekehyksen.
3. **Runtime Flattening**: Atomien kaikki tasotiedot riisutaan ja ne sekoitetaan täyteen satunnaisjärjestykseen ennen syöttämistä varsinaiselle tuomarille.
4. **Isolated Runtime AI ("The Blind LLM")**: Tämä on puhdas, armoton binaarituomari (T=0.0). Se evaluoi 75 satunnaista väitettä pelkkinä eristettyinä "True" tai "False" väitteinä pystymättä päättelemään kohteesta isoa kuvaa.
5. **Waterfall Calculation (Python)**: Arkkitehtuurin sydän. (Katso luku 3).
6. **Synthesis and XAI (Valmentaja)**: Viimeinen tekoäly lukee Python-vesiputouksen langettaman raa'an matemaattisen pisterivin ja kaikki nollapisteen ("False") saaneet kriteerit (esim. puuttuva kausaatio). Se kirjoittaa näiden pohjalta asiantuntijamaisen, yksityiskohtaisen synteesin ihmisen luettavaksi.

---

## 3. The Hook & Waterfall Scoring Engine (Vesiputouslaskenta)

Kun "Sokea LLM" palauttaa Pydantic-muodossa 75 `True` tai `False` väittämää, kontrolli siirtyy takaisin Python-moottorille (`backend_v2/hooks/scoring.py`). 

Mekaniikka:
1. **Hash-karttojen kääntö**: Python-moottori vertaa kryptografisia hashejä palauttaakseen atomit niiden alkuperäisille BARS-tasoille (1-5).
2. **Osumatiheys (Hit Rate)**: Jokaiselle tasolle lasketaan osumaprosentti (`Hits / Total`).
3. **Pysäytyskynnys (75%)**: Jos tason väittämistä jää alle 75 % saavuttamatta, vesiputous "murtuu" eikä tekoäly pääse enää ylemmille portaille.
4. **Vesiputouslattia (Floor)**: Se ylin taso, jonka osumatarkkuus ylitti 75% ennen murtumista, lukitaan matemaattiseksi lattiaksi (esim. `3.0`).
5. **Hybrid Cap -Kattosääntö**: Lopullinen arvosana silotellaan (Weighted Score), mutta sille asetetaan ehdoton katto `min(weighted, floor + 1.0)`. Jos taso 4 murtui, ei arvosana koskaan voi ylittää tasalukua `4.0`, vaikka yksittäisiä summittaisia arvauksia löytyisi tasolta 5. 

Tämä on ohjelmallinen turvallisuuseste "Goodhartin Laille": LLM ei voi vain antaa huippupisteitä tai keksiä hyviä perusteluja ohittamatta mekaanista lattian turvaverkkoa.

---

## 4. XAI-Oikotiet (Kuinka lukea `execution_trace.json` Blobia)

Jos arkkitehdin tai auditoijan on tarve mennä todellisen raakadatan ytimeen lukemaan langetettuja Micro-CoT Pydantic -tuomioita, niitä on turha etsiä tietokannasta. Ne sijaitsevat Blob-tiedostossa. Isoa tiedostoa voi navigoida seuraavilla hakusanoilla (Ctrl+F):

* **Raaka Sokean-LLM Data (True/False):**
  The Hook tallentaa arvaukset litteänä listana välimuistiin muuttujaan `evaluations`. Tämä on listajärjestelmä muodossa `{"boolean": true/false}`.
* **Loppuarvostelu & Tekstiperustelut (Micro-CoT):**
  Pääagenttien (Falsifier, Judge jne.) itse generoimat raskaammat tekstiperustelut nousevat sanakirjoihin avaimella **`_is_evaluative": true`**. Tästä voi seurata kyseisen sanakirjan Pydantic-puuta eteenpäin kenttiin, kuten `"step_1_evidence"` tai `"step_4_final_score"`.
* **Raskas PDF Syöte (Base64):**
  Alkuperäinen koneen sisään syömä laaja analyysimateriaali sijaitsee aivan listan alkuosassa: **`content_base64`**. Tämä takaa sen, että koko ajo ja lähtödata kyetään palauttamaan forensisessa mielessä takaisin myöhemmin (XAI Restore & Re-Evaluation) pelkän yhden Storage Service JSOn-tiedoston avulla.
