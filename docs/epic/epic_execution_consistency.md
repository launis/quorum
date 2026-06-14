# Ajojen Epäjohdonmukaisuuden Juurisyyanalyysi ja Korjaussuunnitelma

## Lähtötilanne

| Metriikka | Arvo | Tavoite |
|---|---|---|
| Variance | 37.9% (69/182) | < 10% |
| Self-Consistency | 62.09% | > 90% |
| Cohen's Kappa | 0.2390 ("fair") | > 0.61 ("substantial") |
| Average Entropy | 0.3791 | < 0.10 |

Molempien ajojen **input-data on identtinen** (product_text: 5999 B, reflection_text: 1557 B, chat_log: ero 3 tavua — todennäköisesti trailingnewline). **Frozen context -JSON on identtinen** (119 323 B). Ohjelmistoversio on sama (sama git commit `ea15fd14`). Kyseessä on siis puhdas **reproducibility-ongelma** samalla konfiguraatiolla.

## Kvantitatiivinen Juurisyyluokittelu (69 mismatch-atomia)

Automatisoidulla luokitteluskriptillä (`scratch/classify_mismatches.py` + `scratch/classify_drift.py`) saatu tarkka jakauma:

| # | Juurisyy | Atomeja | Osuus | Korjattavissa? |
|---|---|---|---|---|
| **A** | Schema Validation Failed (`condition_met` hallusinaatio) | 6 | 8.7% | ✅ Kyllä |
| **B** | Contextual Override -erimielisyys (meta-sääntöjen tulkinta) | 21 | 30.4% | ✅ Kyllä |
| **C** | Tyhjät/puuttuvat extraction_rule -säännöt | 11 | 15.9% | ✅ Kyllä |
| **D** | Inverse Evidence -sekaannus (käänteissäännön tulkinta) | 12 | 17.4% | ⚠️ Osittain |
| **E** | Aito semanttinen drift (LLM-stokastisuus) | 17 | 24.6% | ❌ Vain osittain |
| **F** | System Error (LLM Unable to verify) | 2 | 2.9% | ✅ Kyllä |

**Rakenteellisesti korjattavissa: 52/69 = 75.4%**

> [!IMPORTANT]
> Edellisessä suunnitelmassa (V1) tunnistettiin vain kategoriat A, B ja C. Tämä revisio lisää kriittisen kategorian **D (Inverse Evidence -sekaannus)** ja tarkentaa kategorian **E (aito drift)** todellista laajuutta — se on vain 24.6% eikä 58% kuten aiemmin väitettiin.

---

## Vuoto A: Schema Validation Failed (6 atomia, 8.7%)

**Mekanismi:** LLM palauttaa `AtomResponse`-objektissa kentän `"condition_met": true/false`, jota Pydantic V2 -skeema ei salli (`additionalProperties: false`). Koko 8 atomin chunk kaatuu yhdellä kertaa, koska Pydantic validoi kaikki `evaluations`-listan jäsenet atomaarisesti.

**Miksi tämä vaikuttaa niin paljon:** Yksi hallusinoitu kenttä kaataa koko chunkin (8 atomia kerralla). R2:ssa tämä tapahtui **6 eri chunkissa** identtisellä virheellä, mikä viittaa yhteen LLM-kutsuun, joka oppi "condition_met"-pattern:n esimerkiksi prompt-tekstistä tai few-shot-esimerkistä.

**Korjaus (Päivitetty P1_Analysis -dokumentin pohjalta):**

> [!IMPORTANT]
> Aiemmin suositeltu skeeman strippaus rikkoo arkkitehtuurin nollatoleranssi- (Zero Compromise Pledge) ja Fail-Fast -sääntöjä (kts. p1_analysis.md). Siksi siirrymme yksinomaan prompt-tason ohjaukseen yhdistettynä olemassa olevaan self-healing -luuppiin.

#### Ensisijainen Ratkaisu: `SCHEMA_PURITY_MANDATE` + Self-Healing
1. **Pydantic Strict Mode (Mekaaninen palomuuri):** Varmistetaan, että kaikki LLM-vasteita parsivat Pydantic-mallit (kuten `AtomResponse` ja chunk-vastaukset) sisältävät eksplisiittisesti asetuksen `model_config = ConfigDict(strict=True, extra="forbid")`. Tämä takaa absoluuttisen Fail-Fast -kaatumisen heti rajapinnassa, jos LLM yrittää palauttaa keksittyjä kenttiä.
2. Lisätään system promptin staattiseen osaan (esim. XML-lohkona `compile_xml_rubrics()` -funktiossa) eksplisiittinen kielto luoda ylimääräisiä kenttiä.
3. Luotetaan nykyiseen `LLMTaskExecutor`-luokan schema healing -luuppiin, joka yrittää automaattisesti korjata mallin Pydantic-virheet kovan kaatumisen jälkeen.
4. Päivitetään healing prompt (`get_schema_healing_prompt`) selittämään *miksi* ylimääräiset kentät hylättiin, jotta iteratiivinen luuppi toimii tehokkaammin.
5. **Clean Slate Retries (Roskadatan eristäminen):** Varmistetaan `LLMTaskExecutor`:n healing-luupissa, että LLM:n tuottama rikkinäinen/hallusinoitu JSON-vastaus **ei ikinä** jää osaksi lähetettävää chatin viestihistoriaa. Uusi yritys on rakennettava puhtaalta pöydältä, jotta malli ei "opi" omasta roskadatastaan.

**Hardening Mandates (Koodaustason vaatimukset `hardening.xml`:stä):**
- **Rule 2 (`strict_pydantic_v2_rust`):** "All NEW classes MUST define `model_config = ConfigDict(strict=True, extra='forbid')`". (Koskee kaikkia LLM:ltä palautuvia DTO-luokkia).
- **Rule 20 (`the_self_healing_ban`):** "Attempting to dynamically patch AI-generated quotes or JSON formatting errors on-the-fly using Regex is STRICTLY PROHIBITED. Data validation belongs 100% to Pydantic." (Perustelee, miksi käytämme schema-luuppia Regexin sijaan).
- **Rule 73 (`anti_hallucination_guardrail`):** "DO NOT hallucinate or invent new Pydantic models."

---

## Vuoto B: Contextual Override -erimielisyys (21 atomia, 30.4%)

**Mekanismi:** 21 atomi laukaisee tilanteen, jossa R1 asettaa `contextual_override = True` ja R2 asettaa `False` (tai päinvastoin). Jakauma on hyvin yksipuolinen:
- 18/21: R1 co=True, R2 co=False
- 3/21: R1 co=False, R2 co=True

**Kaksi alatyyppistä:**

### B1: Meta-säännöt ("Do not evaluate X") — ~12 atomia
Säännön `concept_description` sisältää meta-ohjeen kuten *"Do not evaluate humility"*, *"Do not evaluate creativity"*, *"Do not evaluate perfection"*. R1 tulkitsee tämän oikein poikkeukseksi (contextual_override=True). R2 ei tunnista meta-ohjetta ja yrittää arvioida atomin normaalisti, tuottaen FALSE.

**Korjaus:** Lisätään prompt-compilerin pre-processing -vaiheeseen deterministinen suodatin: jos atomin `concept_description` alkaa merkkijonolla *"Do not evaluate"*, atomi **ei lähde LLM:lle lainkaan** vaan saa automaattisesti `contextual_override=True` + `mapped_state=N/A` (tai muu vakioarvo).

### B2: Tyhjä question-kenttä — ~9 atomia
Atomin `question` on tyhjä merkkijono. R1 laukaisee contextual_overriden ("syntactic chain severed"), R2 yrittää arvioida normaalisäännöllä.

**Korjaus:** Lisätään prompt-compilerin pre-processing -vaiheeseen toinen suodatin: jos atomin question-kenttä on tyhjä tai `None`, atomi saa automaattisesti `mapped_state=DLQ` ja se ohitetaan LLM-arvioinnissa.

---

## Vuoto C: Tyhjät extraction_rule -säännöt (11 atomia, 15.9%)

**Mekanismi:** `seed_data.json`-tiedostossa on TDA-assertioita, joiden `extraction_rule` on tyhjä merkkijono `""` tai sisältää vain kontekstuaalisen fragmentin (esim. pelkkä sana `"found."`). Ilman konkreettista sääntöä LLM keksii itse, mitä etsiä — johtaen täysin satunnaiseen tulokseen.

**Esimerkkejä löydetyistä ongelmista:**
- `tda_a63362bd...`: extraction_rule = `"found."` (1 sana)
- `tda_545c0c67...`: extraction_rule = `""` (tyhjä)
- `tda_5b057322...`: concept_description = `""` ja extraction_rule = `""` (molemmat tyhjiä)

**Korjaus:**

1. **Seed Vault -auditointi**: Ajetaan skripti, joka listaa kaikki TDA:t joissa `extraction_rule` on tyhjä tai alle 10 merkkiä pitkä. Nämä ovat "broken atoms".
2. **Päätös per atomi:** Joko korjataan sääntöteksti tai merkitään atomi `disabled: true` -lipulla ja ohitetaan arvioinnissa.
3. Uudelleenseedaus `backend_v2/seed/run_seed.py local` vahvistuksen jälkeen.

---

## Vuoto D: Dual Negation Hazard / Käänteissäännön Sekaannus (12 atomia, 17.4%)

**Mekanismi (Päivitetty P3_Analysis -dokumentin pohjalta):** 
Inverse-atomien kohdalla tapahtuu arkkitehtuurinen ristiriita (Dual Negation Hazard). Järjestelmässä on samanaikaisesti kaksi mekanismia yrittämässä flippausta:
1. LLM yrittää päätellä inverse-logiikan semanttisesti prompt-ohjeen pohjalta (Systeemi 2).
2. Backend (`evaluate_extraction`) flippaa mekaanisesti `PASS` ↔ `FAIL` (Code-as-a-Judge).
Tämä aiheuttaa kaksoiskäännöksiä: LLM jättää löydöksen raportoimatta ohjeen perusteella, jolloin backend flippaa tyhjän löydöksen "virheellisesti" PASS-tilaan. Tulos on täysin stokastinen.

> [!CAUTION]
> Alkuperäinen ehdotus (P3: "Prompt-tason selkeytys") pahentaisi ongelmaa. Jos LLM ymmärtää inverse-ohjeen "paremmin", se rationalisoi ja piilottaa löydöksiä useammin, mikä rikkoo backendin Code-as-a-Judge -mekanismin.

**Korjaus (Code-as-a-Judge Mandate):**

1. **Poistetaan inverse-ohje promptista kokonaan (`localization_compiler.py`):** LLM:lle annetaan ainoastaan positiivinen uuttamistehtävä ("Etsi onko tekstissä piirre X. Jos on, palauta lainaus"). LLM:ltä poistetaan kognitiivinen kuorma käänteislogiikasta.
2. **Luotetaan backendin flippaukseen:** `ChunkWorker.evaluate_extraction` tekee jo deterministisen käännöksen. Vahvistetaan tätä lisäämällä selkeä audit-loki käännöksestä (Code-as-a-Judge).
3. **Immuutti Tila (State Immutability):** Kun `ChunkWorker` tekee käännöksen (PASS → FAIL), alkuperäistä objektia **ei saa mutatoida in-place** (esim. `obj.status = "FAIL"`). On luotava täysin uusi, puhdas kopio Pydanticin rakenteilla. Tämä estää kilpatilanteet asynkronisessa ajossa.

**Hardening Mandates (Koodaustason vaatimukset `hardening.xml`:stä):**
- **Rule 17 (`the_duct_tape_ban`):** Ongelman ytimen korjaaminen (negaation siirto ohjelmalliseksi) on ainoa arkkitehtonisesti hyväksyttävä tapa käsitellä interferenssiä, "purkkaviritykset" promptissa ovat kiellettyjä.
- **Rule 22 (`zero_legacy_fallback_hacks`):** "Legacy fallback hacks are entirely unsupported. If requisite data is absent, the execution MUST trigger a Fail-Fast crash immediately."
- **Rule 18 (`rfc7807_dual_reporting_strict`):** Flippauksen mahdolliset virheet ja itse lokitus pitää aina hoitaa rakenteellisella Quorum AppException -/ logger.debug -mallilla.
- **Rule 14 (`frozen_state_mutability`):** "You MUST NOT mutate state in-place. Hooks MUST purely return new objects."
- **Rule 91 (`pydantic_mutation_optimization_mandate`):** Muuta immutaabelia tilaa suorituskykyisesti käyttämällä `model.model_copy(update={...})`.

---

## Vuoto E: Atom-to-Rule Mapping -Vuoto (12 atomia) ja Aito Drift (5 atomia)

**Mekanismi (Päivitetty P2_Analysis -dokumentin pohjalta):** 
Aiemmin luulimme, että 17 atomia kärsi satunnaisesta "semanttisesta driftistä". P2-analyysi paljasti, että todellinen juurisyy 12 tapauksessa on **rakenteellinen Atom-to-Rule Mapping -vuoto**. `FlattenedAtom` kantaa vain kysymystä, ja säännöt injektoidaan irrallaan. LLM joutuu päättelemään linkityksen stokastisesti. Vain n. 5 atomia on aitoa stokastista driftiä.

> [!IMPORTANT]
> Aiemmin ehdotettu "deterministinen chunk-järjestys" (Hash-siemen) ei ratkaise ongelmaa. Se vain vakioi bugeja. Oikea korjaus vaatii arkkitehtonisen muutoksen, jossa atomin ja säännön linkitys tehdään ohjelmallisesti eksplisiittiseksi promptissa.

**Ensisijainen Ratkaisu (Hybridimalli):**
1. **Laajennetaan `FlattenedAtom` -skeemaa:** Lisätään `extraction_rule`, `anchor_target` ja `is_inverse` -kentät suoraan atomiobjektiin (`atom_flattening.py`) backendin sisäistä käsittelyä varten.
2. **Rajataan `compile_xml_rubrics`:** Suodatetaan XML-rubriikkiin vain ne TDA-säännöt, joiden atomit oikeasti sisältyvät kyseiseen chunkkiin (estää sääntöjen valumisen chunkkien välillä ja säästää valtavasti tokeneita).
3. **Eksplisiittinen Linkitys Promptissa (Sokea DTO):** Lisätään sääntöviittaus (`rule_anchor`), jotta LLM tietää mitä XML-sääntöä soveltaa. **KRIITTISTÄ:** Backendin laajennettua `FlattenedAtom`-mallia EI SAA syöttää sellaisenaan promptiin. Se on projisoitava riisuttuun DTO-muotoon (jossa on vain esim. `atom_id`, `rule_anchor` ja `question`), jotta `is_inverse` ja muu backend-logiikka eivät vuoda LLM:lle ja kumoa P3-korjausta (Dual Negation Hazardin esto).
4. **Opaakit Ankkurit ja Semantic Fencing (Attention Drift -esto):** Varmistetaan, että `rule_anchor` käyttää olemassa olevia opaakkeja tunnisteita (kuten `tda_` alkuisia tiivisteitä), eikä deskriptiivisiä nimiä. Tämä pakottaa LLM:n lukemaan varsinaisen säännön arvaamisen sijaan. XML-rubriikki ja JSON-payload on rajattava eristetyiksi "sandbox"-kokonaisuuksiksi (esim. `<rule id="tda_123">`), jotta eri säännöt samassa chunkissa eivät kontaminoidu keskenään.

**Hardening Mandates (Koodaustason vaatimukset `hardening.xml`:stä):**
- **Rule 29 (`high_fidelity_prompting`):** "Prompt core instructions MUST remain completely static to enable Prompt Caching. Dynamic execution variables MUST be isolated within an `<execution_parameters>` tag at the tail of the message."
- **Rule 51 (`hybrid_prompting_mandate`):** "System prompts MUST use a hybrid of XML for structural control and Markdown for nested content formatting."
- **Rule 52 (`ephemeral_caching_topology`):** "System Prompts must remain 100% static to maximize ephemeral prompt caching hit rates on external LLM provider APIs."
- **Rule 8 (`duck_typing_token_shield_exception`):** `FlattenedAtom` luokitellaan Data Projection Modeliksi, jolle `extra="ignore"` on sallittua token-suojauksen vuoksi, vastoin yleistä kieltoa.

---

## Vuoto F: System Error (2 atomia, 2.9%)

Kaksi atomia tuotti *"[SYSTEM ERROR: LLM Unable to verify.]"*. Tämä on todennäköisesti timeout tai rate limit -ongelma.

**Korjaus:** `FAIL_FAST_MAX_RETRIES = 1` → nostaminen arvoon 2 tai 3 riittää.

---

## Priorisoitu Toteutussuunnitelma

| Prioriteetti | Korjaus | Vaikutus (atomeja) | Työmäärä |
|---|---|---|---|
| **P0** | B1+B2: Deterministinen meta-sääntöjen ja tyhjien kysymysten suodatus prompt-compilerissa | 21 → 0 | Pieni |
| **P1** | A: `SCHEMA_PURITY_MANDATE` XML-lisäys prompt-compileriin + healing-luupin tuki | 6 → 0 | Pieni |
| **P2** | C: Seed Vault -auditointi + broken atoms -siivous | 11 → 0 | Keskisuuri |
| **P3** | D: Inverse-ohjeen poisto promptista (Code-as-a-Judge delegation) | 12 → 0 | Pieni |
| **P4** | E: Hybridimalli (FlattenedAtom-laajennus + rubriikin rajaus + eksplisiittinen linkitys) | 17 → ~5 (vain aito drift jää) | Suuri |
| **P5** | F: Retry-logiikan vahvistus | 2 → 0 | Pieni |

**Odotettu vaikutus P0–P2 jälkeen:** 69 → ~31 mismatch-atomia → Variance ~17% → Kappa ~0.55
**Odotettu vaikutus P0–P5 jälkeen:** 69 → ~12 mismatch-atomia → Variance ~6.6% → Kappa ~0.80+

## Arkitehtuuripäätökset (Resolutions to Open Questions)

### 1. Schema (P1): Strippaus vs. Prompt-kielto
**Päätös:** Eksplisiittinen prompt-kielto (`SCHEMA_PURITY_MANDATE`) yhdistettynä olemassa olevaan schema healing -luuppiin.
**Perustelu:** Kuten `p1_analysis.md` osoittaa, ylimääräisten kenttien hiljainen strippaus rikkoo järjestelmän Fail-Fast-arkkitehtuuria (`the_duct_tape_ban`, `universal_fail_fast`). Hallusinoitu kenttä on oire kognitiivisesta romahduksesta, jota ei pidä peittää (maskaus). Arkkitehtonisesti puhdas ratkaisu on estää virhe `SCHEMA_PURITY_MANDATE`-injektiolla system promptiin ja antaa valmiiksi olemassa olevan `get_schema_healing_prompt()` -logiikan pakottaa korjaus.

### 2. Meta-säännöt (P0): Miten käsitellä "Do not evaluate"
**Päätös:** Siivotaan pois Seed Vaultista (Tietokannasta).
**Perustelu:** TDA-järjestelmässä (Task-Driven Assertion) jokainen atomi oletetaan arvioitavaksi väitteeksi. "Do not evaluate" -atomit tai täysin tyhjät kysymykset ovat selkeästi viallista roska-dataa, joka on syntynyt tietokannan seedausvaiheessa (blueprint/funnel). Niiden ohjelmallinen ohittaminen ajonikana vain laastaroi oiretta. Oikea korjaus on poistaa tällaiset vialliset TDA:t suoraan `seed_data.json` -tiedostosta `disabled: true` -lipulla tai skriptillä.

### 3. Dual Negation Hazard (P3): Prompt-negaatio vs. Code-as-a-Judge
**Päätös:** Poistetaan käänteinen logiikka (negaatio) promptista kokonaan; LLM tekee vain uuttamista, koodi (ChunkWorker) hoitaa loogisen flippauksen.
**Perustelu:** Analyysi `p3_analysis.md` paljasti kognitiivisen interferenssin (Systeemi 1 vs 2). Jos LLM yrittää hoitaa negaation, se rationalisoi pois rikkomuksia. Tämä rikkoo `llm_cognitive_offloading_mandate` -sääntöä. Looginen flippaus on deterministinen operaatio ja siksi se kuuluu backendin vastuulle (Code-as-a-Judge).

### 4. Atom-to-Rule Mapping (P4): Täysi kapselointi vs. Hybridimalli
**Päätös:** Hybridimalli (Atomin sisäinen sääntöviittaus + rajattu XML-rubriikki).
**Perustelu:** Kuten `p2_analysis.md` osoittaa, pelkkä chunk-järjestyksen vakiointi hash-siemenellä on laastarikorjaus, joka ei korjaa irrallisia sääntöjä (atomit on jo valmiiksi generoitu deterministisessä järjestyksessä `atom_flattening.py`:ssä). Käyttäjän ehdottama "täysi kapselointi" (myös `text_chunk` atomiin) rikkoisi Context Cache Mandaten ja räjäyttäisi token-kulutuksen. Hybridimalli on täydellinen tasapaino: se säilyttää staattisen cachen (`<source_data>`), kutistaa promptia suodattamalla chunkkiin vain aidosti kuuluvat säännöt, ja tekee linkityksen LLM:lle deterministiseksi ohjelmallisella `rule_anchor`-kentällä.

## Verification Plan

1. **P1 (Schema):** Lisätään `SCHEMA_PURITY_MANDATE` XML-lohko system promptiin ja tarkennetaan `get_schema_healing_prompt()` -virheohjetta.
2. **P0 (Seed):** Etsitään ja poistetaan "Do not evaluate" sekä tyhjät atomit `seed_data.json`:sta.
3. **P4 (Mapping):** Laajennetaan `FlattenedAtom` (`atom_flattening.py`), rajataan `compile_xml_rubrics` chunk-atomien perusteella ja lisätään `rule_anchor` promptiin.
4. **P3 (Inverse):** Poistetaan inverse-ohjeteksti täysin `localization_compiler.py`:stä, lisätään audit-logiikka flippaukseen `chunk_worker.py`:hyn.
5. **Varmennus:** Uudelleenajetaan `diff_executions.py` korjausten jälkeen. Tavoite: Variance < 10%.
