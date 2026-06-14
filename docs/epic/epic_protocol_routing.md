# Epic: Protokollareititys ja Kognitiivisen Strictnessin Eriyttäminen

## 1. Tavoite ja Tausta

Quorum V2:n arkkitehtuuri on yhdistänyt matemaattisen pisteytyksen tiukkuuden (`strictness_level`) ja LLM:n kognitiivisen lukutavan (Zero-Trust vs. Freeform). Tämä Epic erottaa nämä toisistaan, mahdollistaen joustavammat "luovat" lukutavat (Freeform Semantic) menettämättä matemaattista kontrollia ja Phase 5 -turvatoimia.

System 2 -analyysi on tunnistanut 5 kriittistä vuotoreittiä (Leak Vectors), joissa protokollat voivat kontaminoitua. Korjaamme nämä vaiheittain Fail-Fast -arkkitehtuuria kunnioittaen.

---

## 2. Kontaminaatioriskit ja Linjaukset

1. **Step-tason kovakoodaus:** Nykyisin protokolla (`extraction_protocol_block_id`) määritellään staattisesti askeleessa. Tämä korvataan dynaamisella OutputProfile-viitteellä.
2. **Prompt-ristiriita:** `calibrate_strictness()` injektoi kognitiivista ohjausta. Tämä muutetaan puhtaasti matemaattiseksi varoitukseksi.
3. **Turvatoimien sekaantuminen:** Phase 5 pakottaa nopeiden mallien strictnessin arvoon 100, mikä estää semanttiset ohitukset (Track B). Tämä ratkaistaan eriyttämällä kognitiivinen strictness matemaattisesta strictnessistä.
4. **Kaksoisportinvartijat:** `scoring.py` ja `chunk_worker.py` käyttävät eri lippuja. Yhtenäistetään.
5. **Äänestyshallusinaatiot:** Majority Vote vaatii aina 2/3 -kynnyksen ohituksille, mutta Zero-Trust -tilassa ohitukset voidaan kieltää kokonaan.

---

## 3. Toteutussuunnitelma (Vaiheistettu)

### Vaihe A: Perusta ja Dynaaminen Reititys (Matala riski)
Tämä vaihe luo datamallit ja korjaa kriittisimmät reititysvuodot, jotta uusi protokolla välittyy LLM:lle oikein.

- [ ] **Malli:** Lisää `extraction_protocol_slug: str | None` `OutputProfile` ja `EmbeddedOutputProfile` -malleihin (`v2_core.py`, `output_profile.py`).
- [ ] **Seed Data:** Lisää kaksi uutta PromptBlockia `seed_data.json`:iin:
  - `blk_proto_guided` (Guided Semantic)
  - `blk_proto_freeform` (Freeform Semantic)
- [ ] **Reititys (Vuotoreitti 1):** Päivitä `llm.py:L170-181` lukemaan protokollaviite dynaamisesti: ensin OutputProfile, sitten Step-fallback.
- [ ] **Prompt (Vuotoreitti 2):** Päivitä `prompt_compiler.py` `calibrate_strictness()` siten, että se poistaa kognitiivisen sävyn ja käsittelee vain matemaattista ankaruutta.

### Vaihe B: Kognitiivinen Vapauttaminen (Keskisuuri riski)
Tämä vaihe muuttaa `chunk_worker.py`:n arviointilogiikkaa siten, että semanttinen ohitus (Contextual Override) aidosti sallitaan.

- [ ] **Strictness-eriyttäminen (Vuotoreitti 3):** Muuta `chunk_worker.py:L358` siten, että `strictness_level` jaetaan kahteen: `cognitive_strictness` (ohjaa LLM:ää) ja `scoring_strictness` (menee pisteenlaskentaan ja pakotetaan 100:ksi lightweight-tiloissa).
- [ ] **Track B päivitys:** Muuta `chunk_worker.py` Track B -logiikka (n. L64) sallimaan ohituksen Freeform-tilassa ilman fyysistä `premise_1_quote` -vaatimusta.

### Vaihe C: Konsensus ja Yhtenäistäminen (Pitkä tähtäin)
Tämä vaihe viimeistelee järjestelmän ja kiristää Zero-Trust -tilan hallusinaatiosuojaa.

- [ ] **Porttien yhtenäistäminen (Vuotoreitti 4):** Varmista, että `chunk_worker.py` ja `scoring.py` lukevat samoja `enable_contextual_overrides` (Workflow) ja `allow_contextual_override` (TDA) -lippuja.
- [ ] **Majority Vote (Vuotoreitti 5):** Päivitä `chunk_worker.py:L191` protokollatietoiseksi. Pidä 2/3 kynnys Freeform/Guided-tiloissa, mutta kiellä overridet vahvemmin Zero-Trustissa.

---

## 4. Vaikutusarviointi ja Raportointi

- **Cohen's Kappa:** Odotettu Kappa-arvo laskee Freeform-tilassa tasolle ~0.55 (kohtalainen), kun Zero-Trust pysyy tasolla ~0.85 (erinomainen). Tämä on sallittu kompromissi ideointi-tyyppisille Workfloweille, mutta ei auditointiin.
- **Pistevariaatio:** Odotettavissa on merkittävää pistenousua (jopa +2.0/5.0) samoille teksteille siirryttäessä Zero-Trustista Freeformiin.
- Jatkossa raportoinnissa/käyttöliittymässä on kyettävä viestimään käyttäjälle selkeästi, millä kognitiivisella protokollalla tulos on laskettu.
