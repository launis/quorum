# KÄYTTÖOHJE: Massiivisten "God Code" -tiedostojen purkaminen (Tier 3 & Tier 2)

Tämä ohje kuvaa, miten Quorumin agentit purkavat turvallisesti yli 500-rivisiä legacy-tiedostoja (kuten `v2_core.py` tai `worker.py`) noudattaen **Strangler Fig** -mallia ja **Zero Behavioral Change** -sääntöä.

## Ydinongelmat ja niiden ratkaisut

1. **Context Amnesia (Kontekstin ylitäyttyminen):** Massiivista tiedostoa ei voi antaa LLM:lle kokonaisena. **Ratkaisu:** Tier 3 -agentti tutkii tiedoston rakennetta `grep_search`:llä ja säännöllisillä lausekkeilla, ja paloittelee työn lukematta koko tiedostoa kerralla.
2. **Infinite Loop (Ikuinen silmukka):** Autonominen koodaus voi jäädä jumiin korjatessaan itseään. **Ratkaisu:** Kaikissa "Self Healing" -skripteissä on Circuit Breaker (Max 3 yritystä), jonka jälkeen työ pysähtyy ja vaatii ihmisen puuttumista.
3. **Teknisen velan piiloutuminen (Tech Debt Proliferation):** Purkuvaiheessa koodia ei saa muuttaa (vaan kopioida 1:1), jolloin huono koodi siirtyy sellaisenaan. **Ratkaisu:** Tier 3 tekee analyysivaiheessa "Tech Debt Inventoryn", joka siirretään ekspliittisiksi tehtäviksi Tier 2 Hardening -vaiheelle purkamisen *jälkeen*.

---

## Oikea suoritusputki (Pipeline)

Massiivista Epic-dokumenttia (esim. `EPIC_133`) ei koskaan suoriteta kerralla. Se viedään läpi seuraavalla iteratiivisella liukuhihnamallilla:

### 1. Epicin pilkkominen (Tiedostotason eristys)
Jaa massiivinen Epic ensin tiedostokohtaisiin osiin (esim. `EPIC_133A_worker.md`, `133B_v2_core.md`). Yhtä God Code -tiedostoa käsitellään kerrallaan.

### 2. Tier 3 Suunnittelu (Micro-Chunking & Lazy Planning)
- **Komento:** Käynnistä suunnittelu antamalla `/tier3-god-code-decomposition` ja kohteeksi yksittäinen God Code -tiedosto.
- **Mitä tapahtuu:** Agentti **ei koodaa vielä mitään**. Se luo erillisen hakemiston (esim. `docs/epic/tasks_v2_core/`) ja generoi yksityiskohtaiset Markdown/XML-suunnitelmat **vain askeleille 1 ja 2** (rajoittaakseen Cognitive Overloadia). Lopuille askeleille se luo Tracker-tiedostoon (`*_tracker.md`) tyhjät paikkavaraukset.
- **Tech Debt:** Agentti kirjaa ylös tunnistamansa arkkitehtuurivirheet (esim. `asyncio.gather`, kovakoodaukset) Trackerin "Tier 2 Hardening" -osioon tulevaisuutta varten.

### 3. Handover ja Suoritus (Tier 2 Execution)
- **Komento:** Tier 3 pysähtyy ja antaa sinulle `/tier5-resume --workflow=/tier2-execute` -komennon. **Avaa täysin uusi keskusteluikkuna** ja suorita komento siellä.
- **Mitä tapahtuu:** Puhdas, täydellä muistilla varustettu Tier 2 -agentti lukee Trackerin ja suorittaa *vain* Askeleen 1.
  - Se siirtää logiikan 1:1 (verbatim) uuteen paikkaan.
  - Se ajaa automaattiset testit (kuten `backend_audit_loop.py`) varmistaakseen Zero Behavioral Changen.
  - Kun testit menevät läpi, se kuittaa askeleen tehdyksi ja jatkaa Askeleeseen 2.

### 4. Silmukan sulkeminen (Iteratiivinen Suunnittelu)
- Kun Askeleet 1 ja 2 on suoritettu, Tracker ohjeistaa Tier 2 -agenttia pysähtymään ja pyytämään uuden Tier 3 -suunnittelijan apua.
- Uusi Tier 3 -agentti analysoi päivittyneen koodikannan tilan ja generoi yksityiskohtaiset suunnitelmat vaiheille 3 ja 4. Suoritus jatkuu kohdasta 3.

### 5. Tier 2 Hardening (Velan maksu)
- Vasta kun koko tiedoston purku on onnistuneesti koodattu ja testattu 1:1, Tracker ohjaa agentin viimeiseen, eli "Tier 2 Hardening" -vaiheeseen.
- Tässä vaiheessa Tier 2 -agentti käy läpi Tier 3:n keräämän Tech Debt Inventoryn ja korjaa vanhat anti-patternit (esim. vaihtaa Literalit Enumeihin) yksitellen nyt jo uudessa, puhtaassa kansiorakenteessa.

Tällä metodilla vältämme massiivisten tiedostojen refaktoroinnissa yleiset riskit: koodin katoamisen, testien hajoamisen ja arkkitehtuurisääntöjen unohtamisen.
