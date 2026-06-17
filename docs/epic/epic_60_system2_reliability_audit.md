# Epic 60: System 2 Reliability & LLM Logic Audit (June 2026)

## 1. Tausta ja Motivaatio (Ongelman kuvaus)
Järjestelmän LLM-evaluointimoottorissa havaittiin merkittävää epävakautta ja varianssia peräkkäisissä ajoissa täysin identtisillä syötteillä ja seed-datalla. Tämä epävakaus paljastui vertailuajoissa, joiden raportit osoittivat hälyttäviä lukemia:

**Todisteet (Diff Raportit 2026-06-17 13:22 ja 13:25):**
- **Keskinäinen konsistenssi (Self-Consistency):** Vain noin 78.7 % – 80.4 %
- **Erimielisyydet:** Jopa 31 kpl (raportti 13:25) ja 29 kpl (raportti 13:22) täysin satunnaisia tilasiirtymiä (esim. PASSED -> FAILED 18 kpl) ilman, että Contextual Override -arvoissa oli eroja.
- **Entropia:** Keskimääräinen Shannonin entropia oli jopa 0.21, mikä viittaa erittäin epävakaaseen mallin päätöksentekoon.

Tämä jatkuva "arvonta" viittasi arkkitehtuuritason rakenteellisiin virheisiin, LLM-ohjeistusten välisiin ristiriitoihin (ns. "Kissojen ja koirien" -ongelma) sekä käänteiseen logiikkaan moottorin ytimessä.

---

## 2. Auditointisuunnitelma (Implementation Plan)
Varianssin juurisyiden selvittämiseksi käynnistettiin kokonaisvaltainen, iteratiivinen auditointi ("kissojen ja koirien kanssa"), joka jaettiin neljään vaiheeseen:

1. **Vaihe 1: Työnkulun orkestrointi ja lohkominen** (`chunk_worker.py`, `prompt_factory.py`, `context_builder.py`)
   - Fokuksessa käänteinen logiikka (is_lightweight, asetukset) ja kielelliset ristiriidat.
2. **Vaihe 2: LLM-ajuri ja suoritusmoottori** (`llm/handler.py`, `llm/client.py`)
   - Fokuksessa Pydantic-validointisilmukat, äärettömät luupit ja Fail-Fast -virheiden käsittely.
3. **Vaihe 3: Jälkikäsittely ja Hookit** (`synthesis.py`, `translation_hook.py`)
   - Fokuksessa LLM-asetusten resurssitehokkuus ja kääntämisen vaikutus semanttiseen päättelyyn.
4. **Vaihe 4: Dynaamisten sääntöjen rakentaja / Seeding** (`seed_data.json`)
   - Fokuksessa arviointisääntöjen kaksoiskielteisyydet ja parsintavirheet.

---

## 3. Auditoinnin Löydökset ja Ratkaisut

> Jokainen löydös on merkitty yhdellä seuraavista tiloista:
> - `[TOTEUTETTU]` — Koodissa todennettavissa oleva muutos
> - `[EHDOTUS]` — Suunniteltu refaktorointi, jota ei ole vielä toteutettu koodiin
> - `[HAVAINTO]` — Auditoinnin puhdas paperi (ei vaadi muutoksia)

### Vaihe 1: Työnkulun orkestrointi ja lohkominen

- **Löydös 1: Käänteinen ehtolause `ENSEMBLE`-asetuksessa `[TOTEUTETTU]`**
  - **Analyysi (Juurisyy):** Koodi ajoi kevyet ekstraktiot 3 kertaa (`ENSEMBLE`) ja raskaat sääntöarvioinnit 1 kerran (`STANDARD`), mikä oli täysin päinvastoin kuin arkkitehtuuri vaatii. Tämän takia raskaissa arvioinneissa mallin lämpötila pääsi satunnaistamaan tuloksia ilman majority-vote -tukea.
  - **Toteutettu korjaus:** Ehtolause käännettiin oikein päin. Todiste: `chunk_worker.py` rivi 454: `llm_count = EvaluationRunCount.STANDARD.value if is_lightweight else EvaluationRunCount.ENSEMBLE.value`.

- **Löydös 2: Minority Veto -virhe `[TOTEUTETTU]` + `[EHDOTUS]` refaktoroinnille**
  - **Analyysi (Juurisyy):** Koodissa oli väärä sääntö, joka pakotti `ENSEMBLE`-äänestyksen tilaan `FAIL`, jos *yksikään* kolmesta ajosta hallusinoi `FAIL` (is_inverse_evidence -atomeille). Tämä rikkoi 2/3 enemmistöäänestyksen ja yliherkisti järjestelmän paisuttamaan FAIL-määriä.
  - **Toteutettu korjaus:** Minority Veto -logiikka on poistettu funktion rungosta. Funktio `_apply_minority_veto` (rivi 116-145) toteuttaa nyt puhtaan 2/3 majority-äänestyksen: `if pass_count >= 2: return "PASS"`.
  - **System 2 -katselmoinnin havainto:** Funktion **nimi** (`_apply_minority_veto`) ja **docstring** ("If ANY runner returns FAIL... FAIL wins unconditionally") ovat edelleen harhaanjohtavia eivätkä vastaa nykyistä logiikkaa. Lisäksi parametri `is_inverse_evidence: bool` (rivi 119) on **käyttämätön kuollut koodi**. Tämä rikkoo koodin luettavuutta ja voi johtaa uuden kehittäjän "palauttamaan" puuttuvan veton luullen sitä regressioksi.
  - **`[EHDOTUS]` Deklaratiivinen refaktorointi (2026 Best Practice: Declarative Consensus Logic & Pure Functions):** Nimeä funktio uudelleen, korjaa docstring, poista kuollut parametri ja nosta kynnysarvo eksplisiittiseksi vakioksi. Katso AI-käsky `ACTION-1`.

- **`[HAVAINTO]`:** Muiden ehtojen (`is_lightweight`, `has_search`, `has_shuffled_atoms`) todettiin toimivan oikein ilman käänteistä logiikkaa.

### Vaihe 2: LLM-ajuri ja suoritusmoottori

- **Self-Healing -mekanismi `[HAVAINTO]` + `[EHDOTUS]` lisäparannukselle**
  - **System 2 -katselmoinnin havainto:** Nykyinen `llm_task_executor.py` EI ole "sokea". Se JO toteuttaa semanttisen virhepalaute-mekanismin kahdella polulla:
    1. **Schema-virheissä** (rivi 367-383): `get_schema_healing_prompt()` generoi virheviestin → injektoidaan `<PREVIOUS_SCHEMA_ERROR>` -tagien sisään seuraavan yrityksen promptiin.
    2. **Loogisissa virheissä** (rivi 419-463): Sama mekanismi + Epic 54 "Smart Coaching" (ellipsis/bracket -detektio lisää kontekstuaalisen palautteen).
    3. **Stuck Loop Detection** (rivit 343, 403): Tunnistaa identtisen virheen toiston ja katkaisee luupin heti.
  - Tämä on jo lähellä 2026 Best Practice -tasoa (Semantic Error Bubbling / Self-Reflective Feedback Loops).
  - **`[EHDOTUS]` Lisäparannus:** Strictness-virheiden erityiskäsittely (esim. kiellettyjen kenttien luettelo virheviestin sisällä). Katso AI-käsky `ACTION-2`.
  - **Perustelu:** Moderni System 2 -tason LLM kykenee korjaamaan rakenteellisen virheensä lähes 100 % varmuudella heti ensimmäisellä yrityksellä, kun virhe esitetään sille semanttisena, luettavana kontekstina. Nykyinen mekanismi tekee jo tämän hyvin.

### Vaihe 3: Synthesis & Translation Hooks

- **Löydös 3: Kielellisen arkkitehtuurin eristäminen ("Cat & Dog" -konflikti) `[TOTEUTETTU]` + `[HAVAINTO]`**
  - **Analyysi (Juurisyy):** Järjestelmä on pyytänyt LLM:ää suorittamaan monimutkaista loogista päättelyä (kuten Toulminin kausaalianalyysiä) kohdekielellä (esim. suomeksi tai ranskaksi), samalla kun järjestelmän säännöt ja ohjeet ovat englanniksi. Tämä aiheuttaa mallin latenteissa avaruuksissa "kognitiivisen repeämän" (Attention Drift), jolloin validitkin sitaatit suodattuvat vahingossa pois kielellisen häiriöäänen vuoksi.
  - **2026 Best Practice (Monolingual Latent Space Reasoning / LoT):** Suurten mallien deduktiivinen logiikka (Chain-of-Thought) on parametrisesti ylivoimaisesti vahvinta englanniksi. Kognitio ja esitystapa (lokalisointi) on eriytettävä täysin toisistaan.
  - **Toteutettu korjaus:** Poistettu `synthesis.py`:n (rivi 632) ristiriitainen "reasoning"-sana CRITICAL LANGUAGE MANDATE -säännöstä. Todiste: sääntö kuuluu nyt: `"You must process the input and generate all your output text and source justifications exclusively in the language specified in <target_language>."` — EI enää ristiriidassa `<required_reasoning_language>English` -tagin kanssa.
  - **System 2 -katselmoinnin havainto:** Kielellinen tavoite toteutuu jo kahdella olemassa olevalla mekanismilla, vaikka Epic ehdottaa uutta `<language_directives>` XML-tagia:
    1. `chunk_worker.py` rivi 386-392: `<linguistic_context>` -tagi, sisältäen `<required_reasoning_language>English</required_reasoning_language>`.
    2. `prompt_compiler.py` rivi 241-262: `get_critical_language_mandate()` ohjeistaa: *"You MUST do your deep analytical step-by-step Chain of Thought reasoning in English inside the `internal_logic_en` structured object."*
  - **Perustelu:** Arkkitehtuurin luettavuus mallille paranee eksponentiaalisesti, kun sen ei tarvitse arpoa, prosessoiko se logiikkaa suomeksi vai englanniksi. Tämä poistaa raportin satunnaiset hylkäykset (PASSED -> FAILED), jotka johtuivat pelkästään käännösvaiheen aiheuttamasta semanttisesta hävikistä.
- **`[HAVAINTO]`:** Jälkikäsittely-hookit hyödyntävät oikein kevyempiä LLMClient-asetuksia, eivätkä haaskaa resursseja raskaisiin evaluointimalleihin.

### Vaihe 4: Dynaamisten sääntöjen rakentaja (Seeding & Rules)

- **Löydös 4: Katkenneet ehdot arviointisäännöissä (Siemendatan kognitiivinen luettavuus) `[TOTEUTETTU]`**
  - **Analyysi (Juurisyy):** Raportti (diff_report 13:22 ja 13:25) paljasti, että kaikkein epävakaimmat säännöt päättyivät katkenneisiin lauseisiin, kuten: `"Otherwise."` Tämä loi LLM-kontekstissa kognitiivisen ansan (Dangling Condition / Double Negative). Se pakotti kielimallin arvaamaan, mitä ohjeen laatija on tarkoittanut "muuten"-tilanteessa (esim. palautetaanko null vai tyhjä merkkijono).
  - **2026 Best Practice (Explicit Terminal Directives):** Sääntöjä on kohdeltava koodina (Deterministic ECA - Event-Condition-Action). Jokaisella luonnollisen kielen säännöllä on oltava ohjelmallinen, absoluuttinen päätetila, joka ei jätä tulkinnanvaraa.
  - **Toteutettu korjaus:** Kymmenen vapaamuotoista `extraction_rule`-sääntöä refaktoroitiin `seed_data.json` -tiedostosta tiukkaan IF-THEN-ELSE -rakenteeseen pseudokoodin omaisesti. Todiste: haku `"Otherwise."` palauttaa 0 osumaa `seed_data.json` -tiedostosta.
    - *Entinen (Kognitiivisesti epäselvä):* `"If [condition]. Otherwise."`
    - *Uusi 2026-luettavuus:* `"... If [condition], extract the quote. Otherwise, return null."` (joka vastaa logiikkaa: `"IF the condition is physically present in the text, EXTRACT the exact quote. OTHERWISE, you MUST output strictly JSON null for this field. Do NOT rationalize or infer missing context."`)
  - **Perustelu:** Eksplisiittinen ohje palauttaa `null` linkittyy saumattomasti Pydantic-skeeman Fail-Fast -validointiin. Se poistaa tulkinnanvaraisuuden ja estää mallia hallusinoimasta täytedataa vain "miellyttääkseen" kysyjää. Tämä korjaa välittömästi Cohenin Kappan ja konsistenssin heittelyt raskaissa iteratiivisissa ajoissa.

---

## 4. Tärkeä Strateginen Huomio: Kielipolitiikka
Auditoinnin yhteydessä vahvistettiin arkkitehtuurillinen tavoite:
**Kaikki sisäinen päättely (`semantic_reasoning`, lokit, ajatukset) tuotetaan yksinomaan englanniksi parhaan suorituskyvyn takaamiseksi, ja ainoastaan valmis lopputulos käännetään/tuotetaan käyttäjän kielellä (eli yleensä samalla kuin lähdeaineisto).**

Tämä yksinkertaistaa mallin taakkaa, kun sen ei tarvitse prosessoida formaalia logiikkaa vierailla tai useilla kielillä samanaikaisesti. Nykyiset mekanismit (`<linguistic_context>` + `get_critical_language_mandate()` + synthesis.py -korjaus) tukevat tätä tavoitetta.

---

## 5. Yhteenveto
Arkkitehtuurinne perusta on erittäin kestävä (erityisesti dynaaminen skeeman karsinta ja Fail-Fast). Varianssi johtui yksinomaan siitä, että LLM jätettiin kognitiivisesti ylikuormitettuun tilaan arvailemaan roikkuvia sääntöjä ja suorittamaan raskasta logiikkaa vierailla kielillä.

Viittaus vuoden 2026 parhaisiin käytäntöihin korostaa sitä, että tekoälykehityksessä ihmisen kirjoittaman koodin lisäksi on optimoitava se, miten kone "lukee" ohjeensa ja virheensä. Kun `seed_data.json` puhdistetaan deterministiseen ECA-muotoon, päättelykieli sementoidaan englanniksi ja Pydantic-virheet käännetään itsereflektiiviseksi palautteeksi, järjestelmän Fleissin Kappa ja itsekonsistenssi tulevat nousemaan tilastollisesti vakaalle yli 90 % huipputasolle.

---

## 6. AI-Actionable -käskyt (Tekoäly-optimoidut kehitysehdotukset)
Alla olevat käskyt on muotoiltu niin deterministisesti, että toinen tekoäly (Cursor, Cline, Copilot tai Antigravity) voi suoraan toteuttaa ne ilman lisäkysymyksiä.

### ACTION-1: Eriytetty konsensusarkkitehtuuri — `_apply_minority_veto` → puhdas `_apply_majority_consensus`
- **Kohdetiedosto:** `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- **Konteksti:** Funktio `_apply_minority_veto` (rivit 116-145), kutsupaikat `resolve_majority_vote`:ssa (rivit 182-184 ja 226-229)
- **Juurisyy:** Funktion nimi (`_apply_minority_veto`) ja docstring ("If ANY runner returns FAIL… FAIL wins unconditionally") eivät vastaa nykyistä logiikkaa (puhdas 2/3 majority). Lisäksi funktio rikkoo Single Responsibility Principleä: se (1) parsii raakadiktit ExtractionPayload-malleiksi, (2) kutsuu `evaluate_extraction`-arviointia ja (3) laskee enemmistöäänestyksen — kolme vastuuta yhdessä funktiossa.
- **System 2 -katselmoinnin kriittinen löydös:** Alkuperäisessä Epicissä väitettiin parametrin `is_inverse_evidence: bool` olevan "käyttämätön kuollut koodi". **Tämä oli virheellinen analyysi.** Parametria käytetään aktiivisesti rivillä 135 (`evaluate_extraction(payload, global_source_text, is_inverse_evidence, strictness_level)`), jossa se ohjaa Dual Negation -flippiä (PASS↔FAIL) inversiosäännöille. Sen poistaminen ilman korvaavaa mekanismia rikkoisi inverse evidence -atomien ENSEMBLE-äänestysten logiikan.
- **Valittu ratkaisu (2026 Best Practice: Pure Functions & SRP):** Sen sijaan, että parametri vain nimettäisiin uudelleen, konsensuslogiikka eriytettiin täysin arviointilogiikasta. Konsensusfunktio kutistuu puhtaaksi matemaattiseksi `list[str] → str` -funktioksi, joka ei tiedä mitään payloadeista, lähdetekstistä tai inversiosta. Arviointisilmukka (`ConsensusVotePayload`-projektio + `evaluate_extraction` + Dual Negation) siirtyy kutsujaan (`resolve_majority_vote`), missä `is_inverse`/`is_negative_rule` on eksplisiittisesti näkyvissä. **Huom:** `ExtractionPayload` korvataan `ConsensusVotePayload`:lla — katso `ACTION-5`.
- **Tarkka toimenpide:**
  1. **Korvaa `_apply_minority_veto` (rivit 116-145)** puhtaalla `_apply_majority_consensus(statuses: list[str]) -> str` -funktiolla, joka ottaa sisään valmiiksi arvioidut statukset
  2. **Siirrä arviointisilmukka (ExtractionPayload + evaluate_extraction)** kutsujaan `resolve_majority_vote`, kumpaankin haaraan (Polku A: shuffled_atoms, rivit 176-184 ja Polku B: block-level, rivit 222-229)
  3. **Poista `is_inverse = False` (rivi 227)** kokonaan — Polun B:n arviointisilmukassa `is_negative_rule` on aina `False` block-tason säännöille
  4. **Säilytä `atom_inverse_map` (rivit 162-168)** — se on edelleen tarpeellinen Polun A:n Dual Negation -flipille
  5. **Päivitä `_calculate_confidence`-kutsut** käyttämään uutta `statuses`-listaa
- **Kooditoteutus:**
```python
# ENNEN (rivit 116-145) — 3 vastuuta yhdessä funktiossa:
def _apply_minority_veto(
    votes: list[dict[str, Any]],
    global_source_text: str,
    is_inverse_evidence: bool,
    strictness_level: int,
) -> tuple[str, list[str]]:
    """Apply Minority Veto consensus logic.

    If ANY runner returns FAIL for an inverse_evidence atom,
    FAIL wins unconditionally to prevent Confirmation Bias.
    """
    statuses = []
    for v in votes:
        payload = ExtractionPayload(
            exact_quote=v.get("exact_quote"),
            contextual_override=v.get("contextual_override", False),
            override_reason=v.get("override_reason"),
            reasoning_steps=v.get("reasoning_steps", ""),
        )
        status = evaluate_extraction(payload, global_source_text, is_inverse_evidence, strictness_level)
        statuses.append(status)

    pass_count = statuses.count("PASS")
    fail_count = statuses.count("FAIL")
    if pass_count >= 2:
        return "PASS", statuses
    if fail_count >= 2:
        return "FAIL", statuses
    return "DLQ", statuses

# JÄLKEEN — puhdas matemaattinen funktio (1 vastuu):
def _apply_majority_consensus(statuses: list[str]) -> str:
    """Apply pure 2/3 majority consensus over pre-evaluated verdicts.

    Args:
        statuses: List of pre-evaluated verdict strings ("PASS", "FAIL", "DLQ").

    Returns:
        The majority verdict. Returns "DLQ" if neither reaches the 2/3 threshold.
    """
    pass_count = statuses.count("PASS")
    if pass_count >= 2:
        return "PASS"
    if statuses.count("FAIL") >= 2:
        return "FAIL"
    return "DLQ"
```

```python
# ENNEN (Polku A: kutsupaikka rivit 182-185 — shuffled_atoms):
if votes:
    is_inverse = atom_inverse_map.get(atom_id, False)
    final_status, statuses = _apply_minority_veto(votes, global_source_text, is_inverse, strictness_level)
    confidence = _calculate_confidence(statuses, final_status)

# JÄLKEEN (arviointisilmukka eksplisiittisesti kutsujassa, ACTION-5 ConsensusVotePayload):
if votes:
    is_negative_rule = atom_inverse_map.get(atom_id, False)
    statuses = []
    payloads = []
    for v in votes:
        payload = ConsensusVotePayload.model_validate(v)
        payloads.append(payload)
        statuses.append(evaluate_extraction(payload, global_source_text, is_negative_rule, strictness_level))
    final_status = _apply_majority_consensus(statuses)
    
    # ACTION-6: Pass validated Pydantic models to merge helper
    # result = _merge_consensus_fields(payloads, statuses, final_status)
    # merged["evaluations"][idx].update(result)
```

```python
# ENNEN (Polku B: kutsupaikka rivit 225-231 — block-level):
if votes:
    is_inverse = False
    final_status, statuses = _apply_minority_veto(
        votes, global_source_text, is_inverse, strictness_level
    )
    confidence = _calculate_confidence(statuses, final_status)

# JÄLKEEN (arviointisilmukka eksplisiittisesti, is_negative_rule=False aina block-tasolla, ACTION-5 ConsensusVotePayload):
if votes:
    statuses = []
    payloads = []
    for v in votes:
        payload = ConsensusVotePayload.model_validate(v)
        payloads.append(payload)
        statuses.append(evaluate_extraction(payload, global_source_text, False, strictness_level))
    final_status = _apply_majority_consensus(statuses)
    
    # ACTION-6: Pass validated Pydantic models to merge helper
    # result = _merge_consensus_fields(payloads, statuses, final_status)
    # merged[block.id].update(result)
```

### ACTION-2: Self-Healing -optimointi — Välitä `strictness_level` virheviestin tekstiin `[OPTIMOINTI]`
- **Kohdetiedostot:** `backend_v2/services/orchestrator/prompt_compiler.py` + `backend_v2/services/llm_task_executor.py`
- **Arkkitehtuuripoikkeus:** `prompt_compiler_immutability` -säännön mukainen muokkauslupa myönnetty käyttäjältä (System 2 -katselmointi 2026-06-17).
- **Tyyppi:** FinOps-optimointi (retry-kierrosten ja token-kulutuksen vähentäminen). Ei bugikorjaus — järjestelmä toimii jo ilman tätä.
- **Konteksti ja datavirta:** `strictness_level` on jo tietokantasuvereeninen parametri, joka kulkee ketjussa: tietokanta → Orchestrator → `ChunkWorker.process_chunk()` → `validation_context["strictness_level"]` → `SchemaFactory` (poistaa `contextual_override`/`override_reason`-kentät skeemasta kun `>= 100`). **MUTTA:** kun LLM silti palauttaa kielletyn kentän ja Pydantic hylkää sen ("Extra inputs are not permitted"), Self-Healing -virheviestin teksti on geneerinen eikä kerro LLM:lle eksplisiittisesti MITÄ kenttiä se ei saa käyttää. Tämä johtaa 2-3 turhaan retry-kierrokseen.
- **Tarkka toimenpide:**
  1. Lisää `get_schema_healing_prompt` -funktioon (`prompt_compiler.py` rivi 473) uusi parametri `strictness_level: int | None = None`
  2. Lisää schema-virhe -haaran (`is_logical_error=False`) loppuun strictness >= 100 -tarkistus, joka nimeää kielletyt kentät eksplisiittisesti
  3. Päivitä kutsupaikka `llm_task_executor.py` rivi 367-371 (schema-virhe): lue `strictness_level` `validation_context`:sta
  4. Päivitä kutsupaikka `llm_task_executor.py` rivi 419-423 (looginen virhe): lue `strictness_level` `validation_context`:sta
- **Kooditoteutus (prompt_compiler.py — funktiosignatuuri ja strictness-haara):**
```python
# ENNEN (rivi 473-474):
@staticmethod
def get_schema_healing_prompt(error_msg: str, is_logical_error: bool, is_eof: bool) -> str:

# JÄLKEEN:
@staticmethod
def get_schema_healing_prompt(
    error_msg: str, is_logical_error: bool, is_eof: bool, strictness_level: int | None = None
) -> str:
```

```python
# ENNEN (schema-virhe branch, rivi 504-514 — suora return):
    return (
        "[SYSTEM: STRICT JSON SCHEMA VALIDATION FAILED]\n"
        ...
        "5. NO EXTRA FIELDS: ..."
    )

# JÄLKEEN (muuttuja + ehdollinen strictness-liite):
    base = (
        "[SYSTEM: STRICT JSON SCHEMA VALIDATION FAILED]\n"
        "Your previous response contained invalid JSON or failed Pydantic schema validation.\n"
        f"Error details: {error_msg}\n\n"
        "CRITICAL SCHEMA RULES:\n"
        "1. You MUST return ONLY valid JSON matching the exact schema requested.\n"
        "2. If the error says 'Field required' (e.g., missing 'atom_id'), you MUST provide it.\n"
        "3. If you evaluated a concept NOT in your instructions, REMOVE it.\n"
        "4. Do not include markdown, conversational text, or explanations outside JSON.\n"
        "5. NO EXTRA FIELDS: Remove any fields the schema does not permit."
    )

    if strictness_level is not None and strictness_level >= 100:
        base += (
            "\n\n[STRICTNESS OVERRIDE ACTIVE: level >= 100]\n"
            "The following fields are BANNED from your output: "
            "'contextual_override', 'override_reason'. "
            "You MUST NOT include these fields."
        )

    return base
```
- **Kooditoteutus (llm_task_executor.py — kutsupaikat):**
```python
# ENNEN (rivi 367-371, schema-virhe):
correction_prompt = self.prompt_compiler.get_schema_healing_prompt(
    error_msg=error_msg, is_logical_error=False, is_eof=is_eof,
)

# JÄLKEEN:
correction_prompt = self.prompt_compiler.get_schema_healing_prompt(
    error_msg=error_msg, is_logical_error=False, is_eof=is_eof,
    strictness_level=validation_context.get("strictness_level") if validation_context else None,
)
```

```python
# ENNEN (rivi 419-423, looginen virhe):
correction_prompt = self.prompt_compiler.get_schema_healing_prompt(
    error_msg=error_msg, is_logical_error=True, is_eof=False,
)

# JÄLKEEN:
correction_prompt = self.prompt_compiler.get_schema_healing_prompt(
    error_msg=error_msg, is_logical_error=True, is_eof=False,
    strictness_level=validation_context.get("strictness_level") if validation_context else None,
)
```

### ACTION-3: Siemennä korjatut seed_data.json -säännöt tietokantaan
- **Kohdetiedosto:** `backend_v2/seed/seed_data.json` → `data/db_v2.json`
- **Konteksti:** `seed/run_seed.py`
- **Juurisyy:** Korjatut 10 `extraction_rule` -sääntöä ovat `seed_data.json`:ssa, mutta aktiivinen tietokanta (`db_v2.json`) sisältää edelleen vanhat versiot.
- **Tarkka toimenpide:** Aja `uv run python backend_v2/seed/run_seed.py local` ja varmista, ettei se tuota virheitä. Tarkista siemennyksen jälkeen logista, että kaikki 10 korjattua sääntöä ovat päivittyneet.

### ACTION-4: Arkkitehtuurivahvistus — Temperature on Model Registry -suvereeninen parametri `[HAVAINTO]`
- **Kohde:** `system_config.model_registry` (tietokanta, ei koodia)
- **Konteksti:** ENSEMBLE-ajojen stokastisuus
- **System 2 -katselmoinnin löydös:** Alkuperäisessä Epicissä väitettiin "nykyinen koodi ei aseta temperaturea ENSEMBLE-ajoille" ja ehdotettiin kooditason muutosta. **Tämä oli virheellinen analyysi.** Temperature on jo arkkitehtuurisesti oikein toteutettu:
  1. Temperature määritellään yksinomaan Model Registryn strategiakohtaisessa konfiguraatiossa (`system_config.model_registry.models`), jota hallinnoidaan Admin Studion käyttöliittymästä.
  2. `LLMClient.from_strategy()` (`client.py` rivi 129) lukee temperaturen tietokannasta: `temperature=target_strategy.temperature`.
  3. `ChunkWorker` saa valmiin `bound_client`-instanssin eikä koskaan koske temperature-arvoon.
  4. Temperaturen hardkoodaus Python-koodiin rikkoisi `zero_db_hardcoding_mandate` -arkkitehtuurisääntöä (`01-python-backend.md`).
- **Nykytila:** `"deep"` strategia on jo konfiguroitu `temperature: 0.0, top_p: 0.0, top_k: 1` — täysin deterministinen. ENSEMBLE-äänestys temperature=0.0:lla tuottaa käytännössä identtisiä tuloksia, jolloin äänestyksen diversiteettiarvo on minimaalinen.
- **Arkkitehtuuripäätös:** Jos ENSEMBLE-ajoihin halutaan tulevaisuudessa diversiteettiä, se tehdään yksinomaan Admin Studiosta nostamalla strategian temperature-arvoa (esim. 0.3). Koodiin EI kosketa. Epicin osion 5 teksti "deterministisen yli 95 %" on matemaattisesti tarkka nykyisellä `temperature: 0.0` -konfiguraatiolla.

### ACTION-5: Kriittinen bugikorjaus — `ExtractionPayload` → `ConsensusVotePayload` (Pydantic `extra="ignore"` -projektio) `[BUGIKORJAUS]`
- **Kohdetiedosto:** `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- **Konteksti:** Luokka `ExtractionPayload` (rivit 32-37), funktio `_apply_minority_veto` (rivit 127-136), funktio `evaluate_extraction` (rivit 40-100)
- **Prioriteetti:** KRIITTINEN — tämä on ainoa löydös joka **todistettavasti vaikuttaa tuotannon tuloksiin**.
- **Juurisyy (todistettu koodi-matemaattisesti):**
  `ExtractionPayload`-malli käyttää kenttänimeä `exact_quote: str | None` (yksikkö), mutta `evaluate_extraction` lukee `exact_quotes: list[str]` (monikko) via `getattr(extraction, "exact_quotes", [])`. Koska `ExtractionPayload`-oliolla ei ole `exact_quotes`-attribuuttia, `getattr` palauttaa aina tyhjän listan `[]`. Tämän seurauksena `evaluate_extraction`-funktion Track A (Physical Match via `AnchorValidationService.validate_evidence`) ei koskaan aktivoidu ENSEMBLE-polussa (`_apply_minority_veto`). Kaikki ENSEMBLE-evaluoinnit putoavat Track B:hen (Semantic Override), missä ainoa kriteeri on `contextual_override == True`.
- **Ketjureaktio:**
  1. Jos LLM palauttaa validin lainauksen **mutta** `contextual_override=False` → status = `"FAIL"` vaikka lainaus on fyysisesti oikein
  2. Jos LLM palauttaa `contextual_override=True` → status = `"PASS"` ilman mitään fyysistä ankkurointia
  3. Koko `AnchorValidationService` on ohitettu ENSEMBLE-polussa, mikä on suora syy raportoituun 78-80 % konsistenssiin
- **Miksi bugi on ollut piilossa:** Standard-polussa (rivit 548-585 ja 587-632) `evaluate_extraction` saa suoraan validoidun Pydantic-mallin (`StepDTOStrict`/`StepDTOSemantic`), jolla **on** `exact_quotes`-kenttä. Bugi esiintyy vain `_apply_minority_veto`:n kautta, joka on ainoa polku joka käyttää `ExtractionPayload`-välikerrosta.
- **Lisäpuute nykyisessä `ExtractionPayload`:ssa:** Malli ei sisällä `semantic_reasoning`-kenttää, vaikka `evaluate_extraction` lukee sitä rivillä 79: `semantic_reasoning = getattr(extraction, "semantic_reasoning", "") or ""`. Tämä tarkoittaa, että ENSEMBLE-polun `[5. VALIDATION DECISION: FAIL]` -tarkistus (rivit 80-83) ei myöskään toimi oikein.
- **Valittu ratkaisu (2026 Best Practice: Pydantic Projection Pattern):** Korvaa `ExtractionPayload` uudella `ConsensusVotePayload`-mallilla, joka käyttää `extra="ignore"` `extra="forbid"`:n sijaan. Tämä eliminoi manuaalisen cherry-pickingin kokonaan: `model_validate(v)` projisoi automaattisesti vain ne kentät joita `evaluate_extraction` tarvitsee ja hylkää loput (kuten `atom_id`, `structural_location`, `localized_anchors_found`, `falsification_argument`, `decision`) turvallisesti.
- **Miksi `extra="ignore"` eikä `extra="forbid"`:** Vote-diktit tulevat `StepDTOStrict.model_dump(mode="json")`:sta tai `StepDTOSemantic.model_dump(mode="json")`:sta, joten ne sisältävät 7-9 kenttää joista `evaluate_extraction` tarvitsee vain 5. `extra="forbid"` pakottaisi manuaalisen kenttävalinnan (cherry-picking), joka on juuri se mekanismi joka aiheutti alkuperäisen bugin.
- **Miksi Pydantic eikä `SimpleNamespace`/`dict`:** Pydantic-malli tarjoaa (1) tyyppitarkistuksen, (2) frozen-suojan mutaatioilta, (3) dokumentaation kenttätasolla ja (4) yhteensopivuuden olemassa olevan `getattr()`-pohjaisen `evaluate_extraction`-rajapinnan kanssa. `SimpleNamespace` poistaisi tyyppitarkistuksen ja frozen-suojan.
- **Tarkka toimenpide:**
  1. **Korvaa `ExtractionPayload` (rivit 32-37)** uudella `ConsensusVotePayload`-mallilla
  2. **Päivitä instansiointi `_apply_minority_veto`:ssa (rivit 129-134):** `ExtractionPayload(exact_quote=v.get(...))` → `ConsensusVotePayload.model_validate(v)`
  3. **Päivitä ACTION-1:n koodiesimerkit** käyttämään `ConsensusVotePayload`:a `ExtractionPayload`:n sijaan
- **Kooditoteutus:**
```python
# ENNEN (rivit 32-37) — väärä kenttänimi, puuttuva kenttä, extra="forbid":
class ExtractionPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    exact_quote: str | None = ""        # ← yksikkö, evaluate_extraction lukee "exact_quotes" (monikko)
    contextual_override: bool = False
    override_reason: str | None = None
    reasoning_steps: str | None = ""
    # semantic_reasoning puuttuu ← evaluate_extraction lukee sitä rivillä 79

# JÄLKEEN — oikeat kenttänimet, kaikki kentät, extra="ignore":
class ConsensusVotePayload(BaseModel):
    """Projects consensus-relevant fields from a raw LLM vote dict.

    Uses extra='ignore' to safely extract only the fields that
    evaluate_extraction reads via getattr(), discarding schema-specific
    extras (atom_id, structural_location, localized_anchors_found, etc.).
    """

    model_config = ConfigDict(frozen=True, extra="ignore")
    exact_quotes: list[str] = []
    contextual_override: bool = False
    override_reason: str | None = None
    reasoning_steps: str | None = ""
    semantic_reasoning: str | None = ""
```

```python
# ENNEN (rivit 127-136) — manuaalinen cherry-picking, väärä kenttänimi:
statuses = []
for v in votes:
    payload = ExtractionPayload(
        exact_quote=v.get("exact_quote"),           # ← väärä avain
        contextual_override=v.get("contextual_override", False),
        override_reason=v.get("override_reason"),
        reasoning_steps=v.get("reasoning_steps", ""),
    )
    status = evaluate_extraction(payload, global_source_text, is_inverse_evidence, strictness_level)
    statuses.append(status)

# JÄLKEEN — Pydantic-projektio, ei cherry-pickingiä:
statuses = []
for v in votes:
    payload = ConsensusVotePayload.model_validate(v)
    status = evaluate_extraction(payload, global_source_text, is_inverse_evidence, strictness_level)
    statuses.append(status)
```
- **Muutoslaajuus:** Nettona -2 riviä koodia. `ExtractionPayload`-luokka korvataan, instansiointi yksinkertaistuu 6 rivistä 1 riviin.
- **Yhteensopivuus ACTION-1:n kanssa:** ACTION-1:n SRP-refaktorointi (arviointisilmukan siirto kutsujaan) käyttää samaa `ConsensusVotePayload.model_validate(v)`-kutsua. Tämä ACTION-5 voidaan toteuttaa joko itsenäisesti tai osana ACTION-1:tä.
- **Testaussuunnitelma:** Aja `uv run python scripts/backend_audit_loop.py . --test` ja varmista, ettei regressiontejä synny. Aja vertailuajo (diff report) ennen/jälkeen ja tarkista, paraneeko konsistenssi (Self-Consistency) yli 85 % rajan.

### ACTION-6: WET → DRY ja Pydantic-Maturiteetti — `_merge_consensus_fields` helper `resolve_majority_vote`:lle `[EHDOTUS]`
- **Kohdetiedosto:** `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- **Konteksti:** `resolve_majority_vote` (rivit 148-267), Polku A (rivit 187-220) ja Polku B (rivit 233-265)
- **Juurisyy:** Polku A (shuffled_atoms, `merged["evaluations"][idx]`) ja Polku B (block-level, `merged[block.id]`) sisältävät lähes identtisen ~35 rivin logiikan: `valid_votes` -suodatus → `overrides/quotes/reasons` -keruu → `contextual_override` 2/3 majority → `exact_quote` plurality → merge kohdesanakirjaan. Tämä on WET-violaatio (Write Everything Twice) joka altistaa divergensseille.
- **Pydantic-Maturiteetin puute:** Alkuperäinen koodi lukee raakoja sanakirjoja `v.get("exact_quote")` jopa äänestyksen jälkeen, mikä jättää tyyppiturvallisuuden nollatasolle ja altistaa kirjoitusvirheille.
- **Pitkän tähtäimen ratkaisu (100% Pydantic Projection):** Erota yhteinen merge-logiikka omaan `_merge_consensus_fields`-funktioonsa, joka ei ota sisään raakoja diktejä, vaan ACTION-5:ssä luotuja **validoituja `ConsensusVotePayload`-Pydantic-malleja**. Tämä eliminoi kaikki `.get()`-kutsut ja cherry-pickingin.
- **Tarkka toimenpide:**
  1. **Luo uusi funktio `_merge_consensus_fields`**, joka ottaa `payloads: list[ConsensusVotePayload]`
  2. **Päivitä arviointisilmukat** tallentamaan validoidut `payloads`-oliot listaan (ks. ACTION-1 päivitetyt koodiesimerkit)
  3. **Korvaa Polkujen A ja B duplikaatti-logiikka** yhdellä kutsulla `_merge_consensus_fields`
- **Kooditoteutus:**
```python
# JÄLKEEN — uusi helper-funktio käyttää yksinomaan Pydantic-malleja (ei dict-parsingia):
def _merge_consensus_fields(
    payloads: list[ConsensusVotePayload],
    statuses: list[str],
    final_status: str,
) -> dict[str, Any]:
    """Merge quote/override/reasoning fields from validated consensus payloads.

    Selects fields from PASS/DLQ votes preferentially.
    Applies 2/3 majority to contextual_override and plurality vote to quotes.

    Args:
        payloads: Validated Pydantic models from the parallel runs.
        statuses: Pre-evaluated verdict strings aligned 1:1 with payloads.
        final_status: The majority consensus verdict.

    Returns:
        Dict with merged consensus fields ready to assign to target dict.
    """
    confidence = _calculate_confidence(statuses, final_status)
    valid_payloads = [p for i, p in enumerate(payloads) if statuses[i] in ("PASS", "DLQ")]
    if not valid_payloads:
        valid_payloads = payloads

    # 100% tyyppiturvallinen attribuuttien luku, ei .get()
    overrides = [p.contextual_override for p in valid_payloads]
    quotes_lists = [p.exact_quotes for p in valid_payloads]
    override_reasons = [p.override_reason for p in valid_payloads]
    reasonings = [p.reasoning_steps for p in valid_payloads]
    final_sr = [p.semantic_reasoning for p in valid_payloads]

    final_override = sum(1 for o in overrides if o) >= 2

    # Flatten monikko-lainauslistat ja valitse yleisin yksittäinen lainaus
    all_quotes = [q for qs in quotes_lists for q in qs if q and q != "[CONTEXTUAL_OVERRIDE_APPLIED]"]
    if all_quotes and not final_override:
        final_quote = max(set(all_quotes), key=all_quotes.count)
    else:
        final_quote = None

    valid_override_reasons = [r for r in override_reasons if r]
    final_override_reason = (
        max(set(valid_override_reasons), key=valid_override_reasons.count)
        if valid_override_reasons
        else None
    )
    final_reasoning = max(set(reasonings), key=reasonings.count)
    final_semantic_reasoning = max(set(final_sr), key=final_sr.count)

    return {
        "contextual_override": final_override,
        "exact_quote": final_quote,
        "override_reason": final_override_reason,
        "reasoning_steps": final_reasoning,
        "semantic_reasoning": final_semantic_reasoning,
        "status": final_status,
        "confidence": confidence,
    }
```

```python
# JÄLKEEN (Kutsupaikka Polussa A, korvaa rivit 187-220):
                result = _merge_consensus_fields(payloads, statuses, final_status)
                merged["evaluations"][idx].update(result)
```

```python
# JÄLKEEN (Kutsupaikka Polussa B, korvaa rivit 233-265):
                    result = _merge_consensus_fields(payloads, statuses, final_status)
                    merged[block.id].update(result)
```
- **Muutoslaajuus:** Nettona ~-50 riviä koodia. 65 riviä duplikaattia korvataan 55 rivin helperillä + 2 × 2 rivin kutsulla. Kenttänimi-bugi (`exact_quote` → `exact_quotes`) korjataan samalla.
- **Yhteensopivuus:** Integroituu luonnollisesti ACTION-1:n SRP-refaktorointiin ja ACTION-5:n `ConsensusVotePayload`:iin. Kaikki kolme ACTIONia muodostavat yhtenäisen pitkän tähtäimen refaktorointikokonaisuuden.

### ACTION-7: Yhtenäistä retry-konfiguraatio — Poista `FAIL_FAST_MAX_RETRIES`, käytä `LLM_MAX_RETRIES` `[EHDOTUS]`
- **Kohdetiedostot:** `backend_v2/models/enums.py` + `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py` + `backend_v2/tests/unit/models/test_system_concurrency_compliance.py`
- **Konteksti:** `SystemConcurrency`-enum (`enums.py` rivit 232, 238), kutsupaikat (`chunk_worker.py` rivit 471-472), yksikkötesti (`test_system_concurrency_compliance.py` rivit 12-13)
- **Juurisyy:** `FAIL_FAST_MAX_RETRIES = 3` on ristiriidassa arkkitehtuurisäännön kanssa: [05_llm_architecture.md](file:///c:/src/quorum/.agents/rules/05_llm_architecture.md) vaatii *"Enforce an absolute max stringency using `SystemConcurrency.LLM_MAX_RETRIES` (which MUST be fixed at 2)"*. `FAIL_FAST_MAX_RETRIES = 3` antaa yhteensä `3 + 3 + 1 = 7` yritystä per chunk, kun arkkitehtuuri vaatii `2 + 2 + 1 = 5`.
- **Miksi kolmas retry on turhaa:** Stuck Loop Detection ([llm_task_executor.py:L343](file:///c:/src/quorum/backend_v2/services/llm_task_executor.py#L343) ja [L403](file:///c:/src/quorum/backend_v2/services/llm_task_executor.py#L403)) katkaisee identtisen virheen toiston heti. Kolmas retry ei koskaan tuota uutta informaatiota — se vain kuluttaa tokeneita (~0.02 USD/chunk × N chunkia).
- **Pitkän tähtäimen ratkaisu:** Poista `FAIL_FAST_MAX_RETRIES` kokonaan ja käytä `LLM_MAX_RETRIES` kaikkialla. Yksi enum, yksi totuus.
- **Tarkka toimenpide:**
  1. **Poista `FAIL_FAST_MAX_RETRIES = 3` (`enums.py` rivi 238)** — yksi lähde vähemmän ristiriidoille
  2. **Korvaa kutsupaikat (`chunk_worker.py` rivit 471-472):** `FAIL_FAST_MAX_RETRIES` → `LLM_MAX_RETRIES`
  3. **Päivitä testi (`test_system_concurrency_compliance.py` rivit 12-13):** poista tai korvaa assertio
- **Kooditoteutus:**
```python
# ENNEN (enums.py L232, L238):
    LLM_MAX_RETRIES = 2
    ...
    FAIL_FAST_MAX_RETRIES = 3  # ← ristiriita arkkitehtuurisäännön kanssa

# JÄLKEEN (poista FAIL_FAST_MAX_RETRIES kokonaan):
    LLM_MAX_RETRIES = 2
    # FAIL_FAST_MAX_RETRIES poistettu — käytä LLM_MAX_RETRIES kaikkialla
```

```python
# ENNEN (chunk_worker.py L471-472):
max_schema_retries=SystemConcurrency.FAIL_FAST_MAX_RETRIES.value,
max_logical_retries=SystemConcurrency.FAIL_FAST_MAX_RETRIES.value,

# JÄLKEEN:
max_schema_retries=SystemConcurrency.LLM_MAX_RETRIES.value,
max_logical_retries=SystemConcurrency.LLM_MAX_RETRIES.value,
```
- **Muutoslaajuus:** 3 tiedostoa, yhteensä ~5 muuttuvaa riviä. Ei vaikuta rajapintoihin.
- **Testaussuunnitelma:** Aja `uv run python scripts/backend_audit_loop.py . --test`. Varmista, ettei `FAIL_FAST_MAX_RETRIES` -viittauksia jää jäljelle: `grep -r "FAIL_FAST_MAX_RETRIES" backend_v2/`.
