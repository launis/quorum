# Epic: Protokollareititys ja Kognitiivisen Strictnessin Eriyttäminen

## 1. Tavoite ja Tausta

Quorum V2:n arkkitehtuuri on yhdistänyt matemaattisen pisteytyksen tiukkuuden (`strictness_level`) ja LLM:n kognitiivisen lukutavan (Zero-Trust vs. Freeform). Tämä Epic erottaa nämä toisistaan, mahdollistaen joustavammat "luovat" lukutavat (Freeform Semantic) menettämättä matemaattista kontrollia ja Phase 5 -turvatoimia.

System 2 -analyysi on tunnistanut 7 kriittistä vuotoreittiä (Leak Vectors), joista 2 on katastrofaalista. Korjaamme nämä vaiheittain Fail-Fast -arkkitehtuuria kunnioittaen.

### 1.1 Esiehtojen tila (Epic: Execution Consistency)

Seuraavat arkkitehtuurimuutokset muodostavat tämän Epicin perustan. **System 2 -analyysi on validoinut niiden tilan koodikantaa vasten (2026-06-15):**

1. **Code-as-a-Judge (P3): ✅ Toteutettu.** `evaluate_extraction()` (`chunk_worker.py:40-105`) tekee jo deterministisen dual-track (Track A/B) arvioinnin + `is_negative_rule` -flippauksen audit-logilla (L91-103). LLM ei tee loogisia päätöksiä (inversio, override), ainoastaan uuttamista. Tämä mahdollistaa kognitiivisen strictnessin eriyttämisen turvallisesti.
2. **Sokea DTO (P4): ✅ Toteutettu.** `chunk_worker.py:360-366` lisää `rule_anchor` ja `atom_id` blind-itemeihin. `compile_xml_rubrics` sisältää `allow_contextual_override` -rajauksen (`localization_compiler.py:L150`), joka injektoi `[CONTEXTUAL OVERRIDE ALLOWED]` -mandaatin vain sallituille TDA-assertioille.
3. **Seed Vault puhdas (P0+P2): ❌ Rikottu.** Aiempi manuaalinen analyysi oli virheellinen tiedoston suuren koon vuoksi. Todellisuudessa `seed_data.json` on **vahvasti kontaminoitunut**: `concept_description` esiintyy 152 kertaa (usein tyhjänä) ja kielletty `"Do not evaluate"` -ohje esiintyy 46 kertaa. Nämä on puhdistettava erillisellä Python-skriptillä ennen Vaiheen A aloitusta. Lisäksi myös `steps` ja `workflows` **ovat** osa `seed_data.json`:ia, joten niiden protokollaviittaukset (`extraction_protocol_block_id`) auditoidaan samassa yhteydessä.
4. **Immuutti tila (P3 Rule 14/91): ❌ Rikottu.** `model_copy(update=...)` on vakiintunut pattern, mutta `chunk_worker.py:383` tekee **in-place -mutaation** (`strictness_level = max(strictness_level, 100)`) funktiargumentille. Tämä kontaminoi kaikki myöhemmät viittaukset (L391, L415, L453, L504, L542, L587). Korjattava Vaiheessa B.
5. **Schema Purity Mandate (P1): ✅ Toteutettu.** `SCHEMA_PURITY_MANDATE` XML-lohko löytyy `localization_compiler.py:L224-L232`:stä, jota `prompt_compiler.py` kutsuu delegoidusti `compile_xml_rubrics()`:n kautta. Tämä on jo toiminnassa kaikissa matriisiarvioinneissa.

---

## 2. Kontaminaatioriskit ja Linjaukset

### Alkuperäiset vuotoreitit (1-6)

1. **Step-tason kovakoodaus:** Nykyisin protokolla (`extraction_protocol_block_id`) määritellään staattisesti askeleessa (nykyisin usein `blk_573802341db9d68c` eli Zero-Trust). Protokollan valinta pidetään Step-tasolla, mutta järjestelmää laajennetaan tukemaan uusia, roolikohtaisia PromptBlockeja (esim. `blk_f23a9b1c7d4e5082` eli Freeform). OutputProfile-reititys on hylätty, koska se aiheuttaisi kalliita LLM-uusinta-ajoja raportointivaiheessa.
2. **Prompt-ristiriita (KRIITTINEN):** `calibrate_strictness()` (`prompt_compiler.py:390-445`) injektoi kognitiivista ohjausta kuten *"You are an unforgiving auditor"* ja *"Be extremely generous and forgiving"*. Kun uusi protokolla-PromptBlock (`blk_f23a9b1c7d4e5082`) lisää oman persoonan, LLM saa kaksi ristiriitaista ohjetta → **kognitiivinen romahdus**. Tämä muutetaan puhtaasti matemaattiseksi varoitukseksi.
3. **Turvatoimien sekaantuminen (KRIITTINEN):** `chunk_worker.py:382-383` pakottaa `strictness_level = max(strictness_level, 100)` **kaikille** matriisivaiheille (`has_shuffled_atoms = True`). Kun tämä arvo saapuu `evaluate_extraction()`:een (`chunk_worker.py:72`), Track B:n `contextual_override = True` saa automaattisesti `FAIL`. **Track B on fyysisesti mahdoton kaikissa matriisivaiheissa.** Tämä ratkaistaan eriyttämällä kognitiivinen strictness matemaattisesta strictnessistä.
4. **Kaksoisportinvartijat:** `scoring.py` ja `chunk_worker.py` käyttävät eri lippuja. Yhtenäistetään.
5. **Äänestyshallusinaatiot:** `resolve_majority_vote()` (`chunk_worker.py:158-268`) tuottaa ristiriitaisen Audit Trail -tilan: kun `strictness_level = 100`, kaikki Track B -äänet ovat `FAIL`, mutta fallback-logiikka (L199: `valid_votes = votes`) poimii silti LLM:n palauttamat `contextual_override = True` -arvot. Lopputulos: `status = FAIL` + `contextual_override = True` → UI näyttää "Semanttinen ohitus käytössä" mutta pisteet ovat 0. Ratkaistaan protokollatietoisella äänestyksellä.
6. **Sokean DTO -periaatteen laajennus:** Kognitiivinen konfiguraatio (protokollavalinta) ei saa vuotaa `scoring_strictness`:iä LLM:lle, eikä `enable_contextual_overrides` -lippu saa näkyä LLM:lle Freeform-tilassa.

7. **OutputProfile `strictness_level` -tyyppirajoitus (RATKAISTU):** Koska kognitiivinen strictness hoidetaan nyt suoraan Step-tason protokolla-Blockilla, OutputProfile voi säilyttää tiukan matemaattisen rajoitteen `Literal[85, 100] | None` puhtaasti numeerista kynnystä varten ilman ristiriitoja.

---

## 3. Toteutussuunnitelma (Vaiheistettu)

### Vaihe A: Perusta ja Uudet Protokollat (Matala riski)
Tämä vaihe luo uudet protokollat olemassa olevan Zero-Trust -protokollan (`blk_573802341db9d68c`) rinnalle.

- [ ] **Seed Data:** Lisää uudet PromptBlockit `seed_data.json`:iin olemassa olevan protokollan rinnalle:
  - `blk_8b4c2e1f9a0d3765` (slug: `proto_guided`, Guided Semantic)
    - `ai_description`: "REQUIRED TARGET: Scan the Target Data. You are a Guided Semantic Extractor. You must look for explicit or strongly implied semantic matches to the rules. Contextual reasoning is permitted if the evidence logically supports the criteria. Output the 5-step piped Parsing Log. You may use contextual reasoning to justify 'CONDITION MET' if direct quotes are absent but the meaning is clear."
  - `blk_f23a9b1c7d4e5082` (slug: `proto_freeform`, Freeform Semantic)
    - `ai_description`: "REQUIRED TARGET: Scan the Target Data. You are a Freeform Semantic Evaluator. Evaluate the holistic meaning of the text against the rules. You are encouraged to use deep contextual reasoning, read between the lines, and infer meaning. Explicit syntactic matches are not required. Output the 5-step piped Parsing Log. Use 'CONDITION MET' or 'CONDITION NOT MET'."
  - Uudet blockit tulee noudattaa täsmälleen olemassa olevaa rakennetta: `category_id: "protocol"`, `type: "instruction"`, `is_evaluative: false`, sekä lisätään uusi kenttä `allows_semantic_override: true`.
- [ ] **Protokollan omistajuus (Vuotoreitti 1):** Protokollan omistajuus **säilyy Stepissä** (`Step.extraction_protocol_block_id`). Sitä ei siirretä OutputProfileen, jotta vältetään raskaat LLM-uusinta-ajot raporttinäkymää vaihtaessa. Uusissa Workflow-määrityksissä Stepit voivat viitata uusiin protokolliin vanhan Zero-Trustin sijaan.
- [ ] **Prompt (Vuotoreitti 2):** Päivitä `prompt_compiler.py` `calibrate_strictness()`:
  - **✅ HYVÄKSYTTY POIKKEUS:** Sääntö `01-python-backend.md` (Rule `prompt_compiler_immutability`) kieltää `prompt_compiler.py`:n muokkauksen. Tämä poikkeus on nyt virallisesti hyväksytty tätä refaktorointia varten.
  - Poista kognitiiviset adjektiivit ("unforgiving", "generous") — nämä kuuluvat `cognitive_strictness`:iin.
  - Muunna puhtaasti matemaattiseksi numeeriseksi kynnysarvoksi: `"SCORING_STRICTNESS: {val}/100"` ilman semanttista ohjausta.
  - *Huom (Schema Purity & Code-as-a-Judge):* Schema Purity Mandate on jo toteutettu (`localization_compiler.py:L224-L232`). Uusi strictness-ohje ei saa tuottaa uusia kenttiä. Kognitiivinen sävy siirretään protokolla-PromptBlockiin.
- [ ] **Seed-datan Step-päivitykset:** `seed_data.json`:ssa on tällä hetkellä `Step`-dokumentteja, joiden `extraction_protocol_block_id` viittaa suoraan nykyiseen Zero-Trust -protokollaan (`blk_573802341db9d68c`). Osalle näistä Stepeistä on tarkoituksenmukaista päivittää viittaus uusiin protokolliin (esim. Freeform) seed-vaiheessa, jotta oikea kognitiivinen reititys tapahtuu oletuksena. Muutokset tehdään suoraan `seed_data.json`:iin (ei `db_v2.json`:iin).
- [ ] **studio.py -kovakoodaus:** `studio.py:L595` kovakoodaa `blk_573802341db9d68c` uusien Step-pohjien oletusarvoksi. Tämä tulee päivittää dynaamiseksi (esim. haetaan ensimmäinen `category_id == "protocol"` -block).

### Vaihe B: Kognitiivinen Vapauttaminen (Keskisuuri riski)
Tämä vaihe muuttaa `chunk_worker.py`:n arviointilogiikkaa siten, että semanttinen ohitus (Contextual Override) aidosti sallitaan. P3:n `evaluate_extraction` (Code-as-a-Judge) on asettanut tälle turvalliset raamit.

- [ ] **Rule 14 -korjaus (esivaatimus):** Poista in-place -mutaatio `chunk_worker.py:383` (`strictness_level = max(strictness_level, 100)`). Luo erillinen muuttuja `scoring_strictness` — alkuperäinen `strictness_level` parametri pysyy muuttumattomana. Tämä on **esivaatimus** eriyttämiselle, koska nykyinen mutaatio kontaminoi kaikki myöhemmät viittaukset (L391, L415, L453, L504, L542, L587).
- [ ] **Strictness-eriyttäminen (Vuotoreitti 3):** Säilytetään `scoring_strictness = max(strictness_level, 100)` pakotus puhtaasti matemaattisena kriteerinä matriiseille. Track B -estologiikka erotetaan tästä arvosta — ohitus sallitaan jatkossa protokollan perusteella riippumatta matemaattisesta `scoring_strictness`:istä.
- [ ] **`cognitive_override_allowed` -arkkitehtuuripäätös (✅ HYVÄKSYTTY RATKAISU):**
  - Johdetaan `cognitive_override_allowed` suoraan protokolla-Blockin uudesta boolean-kentästä `allows_semantic_override: bool = False` (Pydantic-mallissa `PromptBlock`).
  - Tämä on hyväksytty poikkeus `pydantic_schema_freeze_mandate` -sääntöön.
  - Tämä kenttä propagoituu: `protocol_block` (seed) → `LLMNodeStrategy` (runtime) → `ChunkWorker.process_chunk()` (uusi parametri) → `evaluate_extraction()` (uusi parametri). Zero-Trust -blokin kenttä on `False`, Freeform/Guided-blokkien `True`.
- [ ] **Track B päivitys:** Muuta `chunk_worker.py` Track B -logiikka (`evaluate_extraction()`:n L70-88). Uusi logiikka: `scoring_strictness >= 100` hylkää Track B -ohituksen *vain* jos `cognitive_override_allowed = False`. Freeform-protokollalla `cognitive_override_allowed = True`, jolloin ohitus sallitaan vaikka matemaattinen tiukkuus pysyy sadassa.
  - **Huomio:** `evaluate_extraction()` -funktion signatuuri laajenee: `strictness_level: int` → `strictness_level: int, cognitive_override_allowed: bool = False`. Tämä vaikuttaa kaikkiin kutsupisteisiin (4 kpl `chunk_worker.py`:ssä + `_apply_minority_veto()`:n delegaatio).
  - **Kaksoislippuyhteys (Vuotoreitti 4 ennakko):** Nykyisin `scoring.py` käyttää kaksiporttilogiikkaa (`Workflow.enable_contextual_overrides` × `TDA.allow_contextual_override`), mutta `evaluate_extraction()` ei tiedä kummastakaan. Track B -päivityksen tulee huomioida tämä: `cognitive_override_allowed` on kolmas, protokollatason lippu joka toimii rinnakkain olemassa olevien kanssa.

### Vaihe C: Konsensus ja Yhtenäistäminen (Pitkä tähtäin)
Tämä vaihe viimeistelee järjestelmän ja kiristää Zero-Trust -tilan hallusinaatiosuojaa.

- [ ] **Porttien yhtenäistäminen (Vuotoreitti 4):** Varmista, että `chunk_worker.py` ja `scoring.py` lukevat samoja `enable_contextual_overrides` (Workflow) ja `allow_contextual_override` (TDA) -lippuja. **Kolmitasoinen override-hierarkia:** Protokolla (`cognitive_override_allowed`) × Workflow (`enable_contextual_overrides`) × TDA (`allow_contextual_override`). Kaikkien kolmen tulee olla `True` jotta semanttinen ohitus sallitaan.
- [ ] **Majority Vote paradox (Vuotoreitti 5):** Päivitä `resolve_majority_vote()` protokollatietoiseksi.
  - **Konkreettinen ongelma:** Kun kaikki äänet ovat `FAIL`, fallback-logiikka (L198-199: `valid_votes = votes`) poimii `contextual_override = True` LLM:n vastauksista. L207 laskee `final_override = sum(1 for o in overrides if o) >= 2` → `FAIL + contextual_override = True` ristiriita.
  - **Huomioitava:** `_apply_minority_veto()` (L121-155) tekee jo protokollatietoisen päätöksen `is_inverse_evidence`:n perusteella. Epic ei saa ohittaa tätä olemassa olevaa logiikkaa.
  - Ratkaisut:
    - Zero-Trust: Kiellä overridet kokonaan (pakota `contextual_override = False` tulokseen).
    - Freeform/Guided: Pidä 2/3 kynnys, mutta `contextual_override` -arvo tulee asettaa `False` kun `final_status = FAIL`.
    - (Nojaa P3:n Code-as-a-Judge -malliin).
- [ ] **Testivelka (Migration Debt):** Päivitä ~35 tiedostoa joissa `blk_573802341db9d68c` on kovakoodattu. Tämä kattaa:
  - **Yksikkötestit:** `test_v2_core_strictness.py` (3), `test_steps.py`, `test_dag_executor_prompt_blocks.py` (2), `test_api_workflow_fail_fast.py`, `test_api_seed_mutations.py`, `test_api_clone_endpoints.py`, `test_llm.py` (4), `test_epic_60_decoupling.py`, `test_scoring.py`, `test_synthesis.py`, `test_atom_flattening.py`, `test_studio.py` (2).
  - **Domain-koodi:** `studio.py:L595` (kovakoodattu Step-pohjien oletus).
  - Lisäksi `calibrate_strictness` -testit (5+ assertia) päivitetään odottamaan puhtaasti matemaattista muotoa.

---

## 4. Vaikutusarviointi ja Raportointi

### 4.1 Positiiviset vaikutukset

| Skenaario | Nykyinen | Odotettu | Muutos |
|---|---|---|---|
| Track B (Semantic Override) matriisivaiheissa | 100% FAIL (rikki) | Toimii Freeform/Guided-tilassa | ✅ Korjaa |
| Kognitiivinen ristiriita promptissa | `calibrate_strictness` + persona ristiriidassa | Puhtaasti matemaattinen + erillinen persona | ✅ Korjaa |
| Cohen's Kappa (Freeform) | ~0.24 (estimaatio) | ~0.55 (kohtuullinen) | ↑ Paranee |
| Cohen's Kappa (Zero-Trust) | ~0.85 (erinomainen) | ~0.85 (säilyy) | → Sama |
| Pistevariaatio tekstien välillä | Monotoninen (kaikki Zero-Trust) | Reititetty (±2.0/5.0 ero) | ✅ Tarkoituksenmukainen |
| Raportoinnin selkeys | Ei tietoa protokollasta | Protokolla näkyy raportissa | ✅ Uusi ominaisuus |

### 4.2 Negatiiviset vaikutukset ja kompromissit

| Riski | Vaikutus | Mitigointi |
|---|---|---|
| **Testivelka (~35 tiedostoa)** | Testien päivittäminen tukemaan useita protokollia | Vaiheistettu käyttöönotto |
| **`prompt_compiler_immutability` -poikkeus** | `calibrate_strictness()` -muokkaus rikkoo jäädytyssääntöä | Poikkeus hyväksytty ja dokumentoitu |
| **`cognitive_override_allowed` -arkkitehtuuripäätös** | Uusi kenttä vaatii Pydantic-mallin, seedin ja frontendin muutoksia | Ratkaistu: lisätään `allows_semantic_override` (Hyväksytty) |
| **Execution Consistency -riippuvuus** | Schema Purity (P1) ✅ ja Sokea DTO (P4) ✅ ovat valmiita | Immuutti tila (P3 Rule 14) korjattava Vaiheessa B |

### 4.3 Arkkitehtuuripäätökset (Vahvistettu)

1. **OutputProfile `strictness_level` -rajoitus (Ratkaistu):** Koska OutputProfile-reitityksestä luovuttiin (katso kohta 2), OutputProfile voi säilyttää Pydanticin `Literal[85, 100]` -rajoitteensa muuttumattomana. Se edustaa vain ja ainoastaan matemaattista rajaa.
2. **Protokollan omistajuus (Ratkaistu):** Protokollan (Extraction Protocol) omistajuus **pysyy Step-tasolla**. Siirto OutputProfileen olisi arkkitehtuurillinen virhe, joka johtaisi raskaaseen laskentakustannukseen (LLM-uusinta-ajoihin) pelkän raporttinäkymän vaihtamisen vuoksi. Phantom ID korvataan valideilla uusilla ID-viitteillä.
3. **Zero-Trust poikkeukset matriiseissa (Ratkaistu):** `scoring_strictness = 100` -pakotus matriiseille säilytetään puhtaasti matemaattisena kriteerinä (shuffled atoms -mätsäys), mutta `evaluate_extraction()`:n Track B -estologiikka eriytetään tästä. Track B -ohitus sallitaan jatkossa puhtaasti protokollan (esim. `proto_freeform`) perusteella.
