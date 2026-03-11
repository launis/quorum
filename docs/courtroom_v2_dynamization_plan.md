# ARKKITEHTUURIMÄÄRITTELY: Courtroom Audit V2 Dynaaminen Refaktorointi

**Tila:** Suunniteltu / Odottaa toteutusta (VAIHEET 1-3)
**Konteksti:** Quorum V2 Backend ja Flutter Client V2
**Tavoite:** Muokata `workflow_courtroom_20_full_audit` ja `workflow_courtroom_30_fused_critics` -työnkulut tukemaan täydellistä, rajoittamatonta dynaamisten syötteiden määrää (`extra="allow"`) ja poistaa askeleista agentteja hämmentävät, kovakoodatut sidokset tiedostonimiin. 

Tämä korjaus on V2-arkkitehtuurin (Enterprise V2.5) mukainen ja noudattaa ehdottomasti fail-fast, schema-driven AI ja append-only SSOT -käytäntöjä.

---

## 1. Arkkitehtuurisäännökset ja Vaatimuksenmukaisuus (V2.5 & Manifesto)

1. **Schema-Driven AI (Dynaaminen Pydantic):** Siirtymällä `$inputs` reititykseen varmistamme, että Pydanticin V2-domainmallit handlaavat rajattoman määrän validointiavaimia `WorkflowInputs` -mallissa, ja LLM saa validin, luotettavan injektion rajapintaan.
2. **Datan Reititys (Semantic Data Flow):** Työnkulun askeleet ohjataan lukemaan suoraan yleistä syötekohdetta (`$inputs`) sen sijaan, että askeleille tulisi antaa nimenomaiset kentät kuten `chat_log` tai `product_text`. Nämä vanhat kentät kielletään lennosta tehdyissä LLM kutsuissa, sillä agenttien täytyy käsitellä "kaikkea toimitettua aineistoa yhtenä kokonaisuutena".
3. **Universaali Mittausarkkitehtuuri ja Fail-Fast:** SDUI vaatii koneluettavia enumerointeja ja numeerisia skaaloja. Korvaamme vanhat tekstipohjaiset luokittelijat (esim. "Passenger vs Driver" tai "Korkea Riski") matemaattisiin 1-4 / 1-5 BARS-skaaloihin (Behaviorally Anchored Rating Scale) tai suoriin numeerisiin arvoihin (`type: "numeric"`, `allow_decimals: false`).

---

## 2. Toteutuksen Vaiheet (Execution Plan)

### VAIHE 1: Backend-integraatio (Python) 

**Tiedosto:** `backend_v2/core/registry.py` (funktio `agent_wrapper` kohdassa, jossa `vars_to_inject` tuotetaan).

**Logiikka:**
* Luetaan parhaillaan ajossa olevan V2 työnkulun (`workflows` tietokannasta) määrittelemät `expected_inputs`. Nämä sisältävät metatiedon kunkin dynaamisen syötteen luonteesta (esim. `{"fi": "Tämä on lopputuotteen dokumentaatio."}`).
* Kun suoritettava askel tarvitsee syötteet `{{INPUTS_JSON}}` tagiin, järjestelmä kokoaa jokaisen syötteen JSON-objektiksi:
  ```json
  [
    {
      "role_description": "Tämä on käyttäjän alkuperäinen keskusteluloki.", 
      "content": "... (lokin sisältö)"
    },
    {
      "role_description": "Tämä on lopputuotteen dokumentaatio.", 
      "content": "... (dokumentin sisältö)"
    }
  ]
  ```
* Injektoidaan lopullinen yhdistelty JSON-rakenne suoraan agentin System Instruction -kontekstiin (`INPUTS_JSON`).

---

### VAIHE 2: Ohjelmallinen DAG-Mappausten Korjaus (Python Skripti)

**Tiedosto:** `backend_v2/scripts/update_courtroom_dag.py` (Scripti tullaan luomaan ja ajamaan). Sisältö operoi tiedostoa `backend_v2/seed/seed_data.json`.

**Logiikka (Semantic Flow V2):**
Ei manuaalista `seed_data.json` editointia, vaan täysin deterministinen ajo `workflow_courtroom_20_full_audit` ja `workflow_courtroom_30_fused_critics` -verkkoihin. Jokaisen `step_node_X` `input_mappings`-taulukko viedään muotoon:
* **Uusi arvo:** `"inputs": "$inputs"` (korvaako kaikki `$inputs.jotain` avaimet, jotka viittasivat suoraan spesifiin tiedostoon)
* **Säilytetty:** Sisäiset riippuvuudet (DAG-polku ylhäältä alas, esim `"$steps.step_node_3.output"`) EIVÄT muutu. Riippuvuuksien turvaaminen on pakollista (Fail-Fast Boundary).

---

### VAIHE 3: PromptBlockien Korvaaminen ja Skaalojen Normalisointi

**Tiedosto:** Sama skripti päivittää `backend_v2/seed/seed_data.json` -tiedoston `prompt_blocks` rakenteen.

Käyttäjä on toimittanut puhtaat ja modernit "V2-tekstit". Päivitetään ohjelmallisesti tarkalleen seuraavat blokit:

#### A. Sanalliset ohjeet (Block Texts)
Asetetaan `description.translations.fi` vastaamaan täsmälleen alla olevia arvoja.

* **block_globalcontext**: Sääntö nykyhetkestä, {{INPUTS_JSON}}-injektion käsittelystä ja rooleista.
* **block_headerinstructions**: "Chain-of-Thought" sääntö `reasoning_trace` vaatimus, ja "Driver vs Passenger" vertailu erotettuna AI-datasta.
* **block_oprule2**: (Erottelu 2) Jos 80% tekoälyn, pelkkää automaatiota.
* **block_oprule3**: (Erottelu 3) Empiiriset teot vs. käyttäjän väitteet itsearvioinneissa.
* **block_instructionnohallucination**: Pysyttävä datassa, ei keksittyjä esimerkkejä.
* **block_instructionanon**: PII datan käsittely ("Ei havaittu").
* **block_instructionnodataleak**: "DATA_CHECKED_AND_SECURED" (Huge Data Protection). Estetään alkuperäisen massadatan litistäminen JSON schemaan.
* **block_instructioncitationobligation**: Citation Snippet pakko (viitedata vaaditaan).
* **block_taskguard**: Input Hygiene Audit ja ohjeet risk_levelille ("KORKEA" riski lazy-prompteissa).
* **block_taskanalyst**: Truth protocol, Say-Do gap. Pydantic-valinnat (Verified/Violation/Hallucination), todisteet (rag_evidence).
* **block_taskinteraction**: Driver Metrics. Riippuvuus, valintojen (Strategy/Archetype) täyttö. (Huom: Näille tehdään erillinen asetus alla).
* **block_taskprofiler**: Cognitive Bias Audit. "Illusion of Competence" Say-Do gap.
* **block_tasklogician**: Toulmin Audit. Syvä 6-osainen analysologia. Probative Value (KORKEA/KESKI/MATALA). *ÄLÄ LITISTÄ* sääntö.
* **block_taskfalsifier**: Falsifiointi ja teroitettu iteraatiosilmukan arvio ("HEIKKO" fidelity auditissa). *ÄLÄ LITISTÄ* sääntö.
* **block_taskcausal**: Abduktiivinen ja vastafaktuaalinen päättely (Post Hoc testaus). *ÄLÄ LITISTÄ* sääntö.
* **block_taskoverseer**: Hallucination Management, faktatarkistus. *ÄLÄ LITISTÄ* sääntö.
* **block_taskarchivist**: Best practices audit, compliance analyysi ("Critically Misaligned" vs "Strongly Aligned").
* **block_taskjudge**: GRAND UNIFICATION. Kuljettaja vs Matkustaja. Hierarkinen pisteytys.
* **block_taskcoach**: Kehityksen jalkauttaminen / Konstruktiivinen palaute.
* **block_taskxai**: License Certification, moniagenttisen XAI-tuloksen lopputiivistys selkokielellä.
* **block_taskpanel**: Unified Critics tason kooste logiikasta, falsifioinnista, kausaalisuudesta, performatiivisuudesta ja hallusinaatioista (Rinnakkaisajojen yhteenveto).

#### B. Pydantic / Frontend-Skaalojen Normalisointi (SDUI Compliance)
Seuraaville blokeille muutetaan tyyppi (`"type": "numeric"`) ja asetetaan matemaattiset `scales`-kentät SDUI-arkkitehtuurin (Riverpod / De-Generator) lukemiin mittoihin.

1. **block_taskarchivist (Compliance Score)**
   - `type`: "numeric", `allow_decimals`: false
   - `1`: Täysin satunnainen prosessi ilman linjakkuutta. Vastaa 'Critically Misaligned'.
   - `2`: Hajanaista prosessin noudattamista. Vastaa 'Misaligned'.
   - `3`: Jonkinlainen prosessi näkyvissä, mutta ei noudata alan standardeja täysin. Vastaa 'Neutral'.
   - `4`: Noudattaa alan standardeja ja best practiceja hyvin. Vastaa 'Aligned'.
   - `5`: Täydellinen State-of-the-Art (esim. OpenAI Cookbook) käytäntöjen noudattaminen. Vastaa 'Strongly Aligned'.

2. **block_taskinteraction (Role Classification / Arkkityyppi)**
   - `type`: "numeric", `allow_decimals`: false
   - `1`: Passenger (Matkustaja): Passiivinen tilaaja. Antaa vain 1-2 sanan komentoja ja odottaa tekoälyn tekevän työn.
   - `2`: Navigator (Suunnistaja): Suunnistaa olemassa olevan aineiston varassa, pyytää korjauksia mutta ei ohjaa logiikkaa.
   - `3`: Driver (Kuljettaja): Aktiivinen ohjaaja. Antaa kontekstia, määrittää tavoitteen ja hallitsee prosessia.
   - `4`: Architect (Arkkitehti): Suunnittelija. Strateginen tason johtaja, hyödyntää tekoälyä omien ajatusmalliensa skaalaamiseen.

3. **block_taskinteraction (Strategy)**
   - *(Huom! Mikäli yhdessä blokissa on 2 numeroa, ne erotellaan Pydanticissa, mutta PromptBlock vaatii oman blokkinsa kullekin numeeriselle arvioinnille. Tässä tapauksessa Strategialle voidaan tarvita oma blokkinsa (esim. `block_taskinteraction_strategy`), tai jos se upotetaan samaan JSON-kenttään, se selitetään vain PromptBlockin tekstissä ja validoidaan Pydanticilla - varmistamme toteutuksessa luodaanko oma blokki).*
   - `1`: Zero-shot... `2`: Few-shot... `3`: Chain-of-Thought...

4. **block_taskcausal (Simulation Result / Counterfactual Test)**
   - `type`: "numeric", `allow_decimals`: false
   - `1`: Mahdoton (Aito riippuvuus): Jos käyttäjä ei olisi esittänyt väitettä...
   - `2`: Mahdollinen: Vaikka käyttäjä poistettaisiin...
   - `3`: Todennäköinen (Riippumaton): Käyttäjän väitteellä ei ole vaikutusta...

5. **block_taskxai (Confidence Score)**
   - `type`: "numeric", `allow_decimals`: false
   - `0`: Täysin epävarma (0%). Data on erittäin ristiriitaista...
   - `25`: Epävarma (25%). Huomattavasti tulkinnanvaraista...
   - `50`: Neutraali (50%). Data on osittain ristiriitaista...
   - `75`: Melko varma (75%). Vahvaa näyttöä...
   - `100`: Ehdottoman varma (100%). Raskas ja kiistaton todistusaineisto lokissa.

6. **block_taskguard (Risk Level)**
   - `type`: "numeric", `allow_decimals`: false
   - `1`: Matala riski: Strukturoitua, turvallista ja asiallista dataa...
   - `2`: Keskisuuri riski: Epämääräinen tai heikosti strukturoitu pyyntö...
   - `3`: Korkea riski: 'Lazy Prompting' (alle 5 sanaa, ei kontekstia)...
   - *(Myös Guardin ohjeista on poistettava manininta `simulation_result` -kentän täyttämisestä, koska se kuuluu Arkkityypille).*

---

### Lopputulos / Onnistumisen Kriteerit
- [ ] Backend injektoi työnkulun dynaamiset syötteet `ai_description` -kenttien kanssa oikein `registry.py`:ssä tekoälyn system-kontekstiin.
- [ ] Courtroom-työnkulku lukee syötteet deterministisesti `$inputs` parametrin takaa rikkomatta DAG-riippuvuuksia.
- [ ] Kaikki 21 blokkia ovat tarkalleen pyydetyissä muodoissa ja tukevat virheettömästi V2:n Schema-Driven AI:tä ja numeraalista de-generointia numeerisilla tyypeillään (ei lennokkaita desimaaleja).

Tämän dokumentin pohjalta aloitamme koodimuutosten toteuttamisen VAIHEISTA 1, 2 ja 3. Valmis.
