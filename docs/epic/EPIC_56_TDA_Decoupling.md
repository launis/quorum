# EPIC 56: Decoupled TDA Architecture (Zero-Variance Protocol)

## 1. Tausta ja Oppimiset Ajoista (org.md -> org9.md)

Historiallisten analyysiajojen sarja (`org.md` – `org9.md`) paljasti syvällisiä arkkitehtuurisia kipupisteitä LLM:n toiminnassa ja todisti tarpeen purkaa TDA-putken (Target Data Analysis) nykyinen rakenne.

### Mitä ajoista opittiin?
1. **Varhainen Oskillaatio (org.md, 19.6 % varianssi):** 
   Ensimmäiset ajot näyttivät rajua lähes 20 % varianssia. Tämä johtui siitä, että kielimalli käytti vapaata Chain-of-Thought -päättelyä subjektiivisiin päätöksiin. Pehmeä rajanveto (esim. "onko tämä vähättelyä?") flippasi herkästi puolelta toiselle täysin samalla tekstillä API-kutsujen mikrotason kohinan vuoksi.
2. **Determinismin Illuusio ja Pydantic-vuoto (org8.md, 3.0 % varianssi):**
   Vaikutti siltä, että varianssi katosi lähes nollaan. Todellisuudessa `diff_executions.py` -skriptissä oli bugi, joka yhdisti "löydetyt lainaukset", "JSON nullit" ja LLM:n hallusinoimat haamu-nullit (esim. merkkijono `"none"`) samaan laariin (`"true"`). LLM ei siis tullut deterministisemmäksi; virheiden mittaus vain sokeutui niille.
3. **Puhdas Kognitiivinen Varianssi (org9.md, 15.6 % varianssi):**
   Kun Pydantic-skeemat tiukennettiin (Epic 55 / Haamu-nullien esto `@model_validator`:lla) ja vertailuskripti korjattiin, todellinen historiallinen varianssi paljastui. 15.6 % atomeista koki aitoa kognitiivista oskillaatiota: LLM löysi molemmilla kerroilla tismalleen saman ankkurin, mutta päätti itse logiikkavaiheessaan (`[5. VALIDATION DECISION]`) antaa toisella kerralla tuloksen `Pass` ja toisella `Fail`.
4. **The Reversal Curse (Käänteinen Logiikka):**
   Lokit todistivat kiistattomasti, että LLM kaatuu useimmiten ns. "Proof by Contradiction" -sääntöihin (esim. *"Jos väitteelle ON todisteita, palauta null"*). LLM on autoregressiivinen moottori; se on erinomainen löytämään asioita, mutta surkea päättelemään negatiivisia ehtoja tai hiljaisuutta.

## 2. Arkkitehtuurinen Ratkaisu: Decoupled TDA

Näiden oppien perusteella nykyinen arkkitehtuuri, jossa LLM sekä **etsii (Extract)** että **tuomitsee (Evaluate)**, hylätään. TDA-putki jaetaan tiukasti kahteen toisistaan eristettyyn vastuualueeseen.

### A. Semantic Extractor (LLM:n uusi rooli)
LLM pelkistetään sokeaksi, mutta semanttisesti älykkääksi poimijaksi. Siltä evätään oikeus tuottaa `[5. VALIDATION DECISION]` lokiinsa. Se ei ota kantaa siihen, meneekö sääntö läpi.
Se poimii Pydanticiin aina kaksi asiaa (Dual-Concept Extraction):
1. `primary_quote`: Ensisijainen ankkuri/väite.
2. `counter_evidence`: Vastaväite, data, tai kumoava konteksti samasta kappaleesta.

### B. Deterministic Evaluator (Pythonin uusi rooli)
TDA-atomin lopullinen Pass/Fail -tuomio siirretään 100 % deterministiseen Python-koodiin (`scoring.py` tai `matrix_reducer.py`). Backend lukee Pydanticin palauttamat kentät ja toteuttaa boolean-matematiikan:
- *Esimerkki säännöstä:* `if primary_quote and not counter_evidence: return PASSED`
Tämä poistaa 15.6 % varianssin kerralla ja siirtää vaikean boolean/negatiivisen logiikan sinne, missä se toimii matemaattisen täydellisesti.

---

## 3. Toteutussuunnitelma (Vaiheistus)

### Vaihe 1: Pydantic-skeemojen rakenteellinen uudistus (Data Mappays)
- **Kohde:** `prompt_compiler.py`
- **Toimenpiteet:**
  - Muuta `AtomResponse` -malliin kaksi louhintakenttää: `primary_quote` ja `counter_evidence`.
  - Poista `mechanical_trace` -kentästä vaatimus päätöksen tekemiselle (`[5. VALIDATION DECISION]`). Lokin uusi muoto: `[1. Scan] | [2. Primary Anchor Search] | [3. Counter-Evidence Search]`.
  - Säilytä äsken rakennettu tiukka Pydantic `@model_validator` estämään kummankin kentän "haamu-nullit".

### Vaihe 2: Deterministinen Arviointimoottori (Scoring)
- **Kohde:** `lightweight_matrix.py` (`AtomEvaluationItemDTO`) & `scoring.py`
- **Toimenpiteet:**
  - Refaktoroi `calculate_rule_satisfied` -metodi lukemaan `primary_quote` ja `counter_evidence` -kenttiä.
  - Toteuta tuki atomin `inverse_evidence` -lipulle, joka kääntää Python-koodin boolean-logiikan.
  - Varmista, että Python-koodi ei palauta "yllätyksiä", vaan puhtaan `True/False` booleanin tuloksena.

### Vaihe 3: Promptien ja Seed Datan siivous
- **Kohde:** `backend_v2/seed/seed_data.json`
- **Toimenpiteet:**
  - Poista sadoista atomeista LLM:ää hämmentävät raskaat litaniat, kuten: *"NEGATIVE CONDITION (RETURN NULL IF MET)... Do not rationalize failures."*
  - Rakenna säännöt uuteen formaattiin: 
    - `TARGET`: Mitä etsitään `primary_quote` -kenttään.
    - `NULLIFIER`: Mitä etsitään `counter_evidence` -kenttään kumoamaan löydös.
  - Lisää sääntöihin "Few-Shot" esimerkkejä, jotka opettavat mallille oikean JSON-palautuksen ilman monimutkaista selittämistä.

### Vaihe 4: Lexical Verifierin Päivitys (AnchorValidationService)
- **Kohde:** `AnchorValidationService.py`
- **Toimenpiteet:**
  - Poista "Trace Contradiction Ban" (koska LLM ei enää tuota tuomiota).
  - Aja RapidFuzz-tarkistus (Lexical Reality) rinnakkain molemmille kentille (`primary_quote` ja `counter_evidence`). Jos malli hallusinoi jommankumman, Self-Healing pakottaa vain kyseisen kentän korjauksen.
