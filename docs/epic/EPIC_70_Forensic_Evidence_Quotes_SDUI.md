# EPIC 70: Forensic Evidence Quotes in SDUI (Config Sovereignty)

## 1. Yhteenveto & Tavoite (Executive Summary)
Quorum V2:n arkkitehtuurin ydinperiaate on **Forensic Sovereignty** (Läpinäkyvyys ja Todistettavuus). Tällä hetkellä `AtomEvaluationItemDTO` poimii LLM-analysaattorilta tarkat lainaukset (`exact_quote`) sekä tarvittaessa rakenteelliset ankkurit (`structural_location`), mutta matriisin pisteytyskoukku (`matrix_scoring_hook`) käyttää niitä vain onnistumisen (PASS/FAIL) laskemiseen ja jättää itse tekstit näyttämättä käyttöliittymän loppuraportissa.

**Tämän Epicin tavoite:** 
Luoda täysin dynaaminen, "Config Sovereignty" -sääntöjä noudattava ratkaisu, jossa raportin laatija (Output Profilen hallinnoija) voi ottaa käyttöön uuden **Lainaukset (quotes)** -sarakkeen `Matrix Summary` -taulukoihin. Kun tämä ominaisuus on päällä, käyttöliittymä tulostaa tekoälyn synteesin sijasta (tai rinnalla) tarkat alkuperäislähteen lainaukset, jotka johtivat osumaan.

## 2. Arkkitehtuurinen Konsepti

Koska lainaukset vievät valtavasti tilaa, niitä ei pakoteta kaikkiin raportteihin. Sen sijaan tämä ominaisuus delegoidaan **Server-Driven UI (SDUI)** -konfiguraatioon:
1. **Dynaaminen Sarake:** `OutputProfileConfig` saa uuden mahdollisen arvon `quotes` sallittujen sarakkeiden (`visible_columns`) listaan.
2. **Käyttäjän Vastuu:** Admin Studion käyttöliittymässä "Lainaukset"-täpän aktivoiminen näyttää suosituksen: *"Vinkki: Kun lainaukset ovat käytössä, on suositeltavaa poistaa Jakauma ja Selite tilan säästämiseksi."*
3. **Kontekstuaalinen Ankkuri (Contextual Pinpoint):** Jos atomin osuma tuli tila-asetuksella `contextual_override=True` (jolloin suoraa lainausta ei fyysisesti ole olemassa), järjestelmä käyttää hienostunutta puskuria. Lainausmerkkien sijaan se näyttää ikonin ja rakenteellisen sijainnin (esim. `📍 Sivu 3, Kappale 2`) yhdistettynä LLM:n semanttiseen perusteluun.

### Konseptuaalinen Lopputulos (SDUI Mockup)

Kun aktiivisena ovat vain sarakkeet `Otsikko (label)` ja `Lainaukset (quotes)`, SDUI-taulukon leveys jakautuu optimaalisesti:

| Osaamisen osa-alueet (25% leveys) | Otteet ja alkuperäistodisteet (75% leveys) |
| :--- | :--- |
| **Oman tiedon rajat (Episteeminen Nöyryys) \***<br>*Arvioi kykyäsi tunnistaa, mitä et tiedä.* | ❝ *"Tämän väitteen tueksi ei löytynyt suoraa faktaa Q3-raportista."* ❞ |
| **Päättelyn rehellisyys (Kausaalinen Integr.) \***<br>*Varmistaa, että johtopäätöksesi ovat...* | 📍 **Sivu 2, Kappale 4:**<br>*Käyttäjä implikoi epävarmuuden esittämällä kaksi toisensa poissulkevaa vaihtoehtoa tasavahvoina.* |

## 3. Toteutuksen Vaiheet (Implementation Tiers)

### Vaihe 1: Backend DTO & Seeder-muutokset
- Päivitetään `OutputProfileConfig` ja/tai `ComponentConfig` hyväksymään `"quotes"` osaksi `visible_columns`-literaalia.
- Varmistetaan, että Pydantic-mallit (esim. `v2_core.py`) tunnistavat uuden saraketyypin.

### Vaihe 2: Scoring Hook State Hoisting (`scoring.py`)
- Muokataan `matrix_scoring_hook`:ia. Kun `ev_dto` käsitellään ja sen `final_state` on `TRUE`, nostetaan atomin data ylös (hoisting).
- Tallennetaan `content_payload["atom_quotes"]` -objektiin lista atomeista, jotka menivät läpi, ja sisällytetään:
  - `exact_quote` (jos olemassa)
  - `structural_location` & `semantic_reasoning` (jos `contextual_override=True`)

### Vaihe 3: SDUI Transformer (`blueprint.py` / `sdui.py`)
- Muokataan `BlueprintTransformer`:ia käsittelemään `visible_columns: ["quotes"]`.
- Jos `quotes` on valittu, generaattori ohittaa / korvaa `row_explanation` (Selite) -kentän uudella `quotes_list` -kentällä.
- Asetetaan kooditason katkaisu (truncation), esim. max 150 merkkiä per lainaus, jotta käyttöliittymä ei rikkoudu.

### Vaihe 4: Admin Studio Frontend (Flutter)
- Lisätään asetusnäkymään (Tulostusprofiili) uusi Checkbox `Lainaukset (quotes)`.
- Lisätään ehdollinen UI-varoitusteksti (Vinkki tilansäästöstä), kun asetus kytketään päälle.
- Päivitetään Raportti-näkymän taulukkokomponentti (`DataTable` / `SDUIGrid`) renderöimään uusi saraketyyppi tyylikkäästi markdown-tuella.

## 4. Onnistumisen Kriteerit
- [ ] Tuotantotietokanta ei rikkoudu uuden asetuksen myötä.
- [ ] SDUI sietää jopa 10 osuman matriiseja katkaisulogiikan (150 char) ansiosta.
- [ ] Contextual Override -tilanteet eivät kaadu, vaan näyttävät siroja 📍 -ankkureita.
- [ ] Arkkitehtuuri säilyy täydellisesti De-Generator / Fail-Fast -yhteensopivana.
