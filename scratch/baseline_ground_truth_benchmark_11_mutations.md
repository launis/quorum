# BASELINE GROUND TRUTH BENCHMARK REPORT: 11 Kohdennettua Muutosta

## 1. Yhteenveto & Tarkoitus (Purpose of this Benchmark)

Tämä raportti arkistoi ja lukitsee aiemmassa osasuunnitelmassa ([implementation_plan.md](file:///C:/Users/risto/.gemini/antigravity-ide/brain/fad37aca-93c3-411a-ba7f-23b53e39e4c3/implementation_plan.md)) analysoidut ja manuaalisesti verifioidut **11 täsmämuutosta**. 

Tätä raporttia käytetään **automaattisena vertailutyökaluna (Ground Truth Oracle)**, kun suoritamme uuden, koko tietokannan (13 matriisia, 152 atomia) kattavan analyysi- ja korjausajon. Uuden kokonaisajon tulee todistetusti löytää ja ratkaista vähintään nämä samat 11 kohtaa täysin samalla laadullisella tarkkuudella.

---

## 2. Lukittu Vertailusetti (11 Kohdennettua Muutosta)

### OSA 1: Järjestelmäkehote (`MATRIX_SENSOR_SYSTEM_PROMPT`)
- **Tiedosto:** `backend_v2/models/prompts/matrix_evaluation.py`
- **Korjauskriteeri:** Injektoidaan `epistemic_decision_protocol`, joka määrittää selkeän todistuskynnyksen:
  - Positiiviset väitteet (`is_inverse: false`): vaatii eksplisiittisen rakenteen tai empiirisen pohjan.
  - Käänteiset/negatiiviset väitteet (`is_inverse: true`): virhe on läsnä vain, jos se on aktiivinen ja korjaamaton; hylätään (`is_true = false`), jos kirjoittaja tekee varauksia tai käsittelee vastaväitteet.

---

### OSA 2: Toulmin-matriisin 5 Atomin Vertailukriteerit (`blk_440a5fef9331451b`)

| Atomin Tunniste (`tda_id`) | Alkuperäinen Virheellinen Tila | Odotettu Korjattu Muoto (Ground Truth) |
| :--- | :--- | :--- |
| **`tda_69cc84e0b0c44996a8a95e09b356c692`** | `extraction_rule: "it connects two facts but lacks any explanatory mechanism. Do not accept explicit causal mechanisms."` | `extraction_rule: "A declarative assertion is made with zero supporting data, rationale, or operational mechanism provided in the sentence or its immediate context."` |
| **`tda_3613ef7137cc4e48a2d62b9921e5583c`** | `extraction_rule: "an anecdote is used to justify a systemic rule or broad policy. Do not flag rigorous case studies."` | `extraction_rule: "A universal or organizational rule is justified solely by a single personal anecdote or isolated individual experience without supporting systemic data or logical principles."` |
| **`tda_b03e802130ef46c781ff49c6a71d6ada`** | `extraction_rule: "complexity or opposing views are dismissed without data. Data-driven rebuttals."` *(Typistetty)* | `extraction_rule: "The argument asserts a conclusion while completely dismissing opposing constraints or counter-arguments without offering operational rationale, trade-off analysis, or empirical reasoning."` |
| **`tda_25f0540101174b66a09fe7770a28d110`** | `extraction_rule: "a counter-argument is mentioned but dismissed without presenting counter-data. Rebuttals that provide counter-data."` *(Typistetty)* | `extraction_rule: "Data is presented alongside a claim, but the underlying logical rule explaining how the data leads to the claim is omitted or ungrounded."` |
| **`tda_1d7531b5f5944175bb1eee7eaed44f69`** | `extraction_rule: "consensus is the ONLY backing for a logical rule. Verifiable empirical sources."` *(Typistetty)* | `extraction_rule: "The rationale for a rule relies exclusively on generic assertions of consensus ('everyone agrees', 'standard industry practice') without citing empirical evidence, theoretical principles, or operational mechanisms."` |

---

### OSA 3: Kausaalisuus-matriisin 5 Atomin Vertailukriteerit (`blk_c5804a9143c34cb1`)

| Atomin Tunniste (`tda_id`) | Alkuperäinen Virheellinen Tila | Odotettu Korjattu Muoto (Ground Truth) |
| :--- | :--- | :--- |
| **`tda_bd90e5a66c5d433a9ed650f295132625`** | `concept_description: "Do not evaluate."` *(Haamuteksti)* | `concept_description: "Asserting that statistical correlation or simultaneous occurrence implies direct causation without demonstrating a mechanism."` <br>`extraction_rule: "Two concurrent events or correlated trends are asserted as a direct cause-and-effect relationship without identifying an explanatory causal mechanism."` |
| **`tda_51a1544a321e4a18b3f4ea09b5bbe02e`** | `concept_description: "Do not evaluate."` *(Haamuteksti)* | `concept_description: "Asserting that event A caused event B solely because event A occurred prior in time to event B (Post-hoc ergo propter hoc)."` <br>`extraction_rule: "Temporal succession is treated as definitive causal proof: the author claims A caused B solely because A preceded B in time."` |
| **`tda_3eed2113bd9842f3b8fd050046505e4d`** | `concept_description: "If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under prefix are REJECTED."` *(Rikkoutunut koodiohje)* | `concept_description: "Attributing real-world physical or organizational outcomes to subjective feelings, intuition, or metaphysical forces."` <br>`extraction_rule: "A causal explanation relies exclusively on subjective intuition, vibes, or metaphysical inevitability rather than observable mechanisms or empirical variables."` |
| **`tda_8ecd3f17b3984e4fa1bb6a8cb5576b65`** | `extraction_rule: "Extract the quote IF a highly complex outcome is attributed to a SINGLE cause."` | `concept_description: "Attributing a complex multi-variable outcome entirely to a single isolated factor while ignoring interacting variables."` <br>`extraction_rule: "A systemic, multi-faceted outcome is definitively claimed to be caused by a single isolated variable, rejecting or ignoring known co-factors."` |
| **`tda_01edff70b75047ec9f6df0c49745f46e`** | `concept_description: "Do not evaluate humility."` ja sisältää raakaa `<ambiguity_protocol>` XML-tekstiä. | `concept_description: "Extrapolating a local causal finding to universal applicability without acknowledging context limitations."` <br>`extraction_rule: "A causal relationship discovered in a specific, narrow context is asserted as universally true across all environments without stating boundary conditions or prerequisites."` |

---

## 3. Vertailuprotokolla Uudelle Kokonaisajolle (Verification Protocol)

Kun uusi kokonaisvaltainen auditointi- ja korjausajo suoritetaan:
1. **Regressiosuoja (Regression Gate):** Skannerin ja korjausputken on automaattisesti katettava yllä mainitut 11 kohdetta ($\text{Kattavuus} \ge 100\%$).
2. **Laajennussuoja (Expansion Gate):** Kokonaisajon on löydettävä ja korjattava vastaavalla tieteellisellä tarkkuudella myös muut 11 matriisia ja niiden 44 epäselvää atomia.
3. **Tulosten Vahvistus:** Ajon valmistuttua ajetaan vertailutesti, joka varmistaa, että kaikki 11 kohdetta vastaavat tätä Ground Truth -raporttia.
