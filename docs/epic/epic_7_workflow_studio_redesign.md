# Epic 7: Workflow Studio Redesign (Master-Detail & Tabbed Architecture)

## 📌 Context
Käyttäjä palaute osoitti, että nykyinen "Työnkulun Asetukset" (Workflow Settings) -näkymä on sekava ja ylikuormittava. Se vaatii uudelleensuunnittelua (UX/UI refaktorointi) siten, että hallinta jaetaan loogisiin osiin. Lähtökohtana on selkeä listausnäkymä, josta siirrytään yksittäisen työnkulun editoimiseen.

Tämä Epic noudattaa Quorum V2 "De-Generator" ja "No-String Mandate" -sääntöjä.

## 🎯 Objectives
1. **Selkeyttää Navigaatio (Master-Detail):** Luodaan päälistausnäkymä (`WorkflowListView`), josta näkee yhdellä silmäyksellä kaikki järjestelmän työnkulut.
2. **Jakaa Editori Loogisiin Välilehtiin (Tabs):** Yksittäisen työnkulun muokkaus jaetaan useaan visuaaliseen välilehteen, jotta yksi ruutu ei hukuta käyttäjää informaatioon.
3. **Parantaa Lomake-UX:ää (Form Layout):** Rajoitetaan kenttien leveyttä (max-width), parannetaan visuaalista ryhmittelyä (Kortit) ja asettelua Desktop-koossa.

---

## 🏗️ Milestones & Implementation Tasks

### Milestone 1: Työnkulkujen Hakemisto (List View)
Työnkulkujen hallinnan "Etusivu".
- Ominaisuudet: Paginoitu lista, haku (Search), työnkulun kloonaus ja avaus.
- Arkkitehtuuri: SWR-tyyppinen välimuisti SDUIN de-generoidun Riverpod-arkkitehtuurin läpi.

### Milestone 2: Välilehtipohjainen App Shell (4 Tabia)
Laajennetaan välilehtirakenne kattamaan koko datan elinkaari:
- **Tab A: Yleiset (General):** Nimi, Slug ja metadata. Käyttää `I18nTextField` -komponenttia.
- **Tab B: Syötteet (Expected Inputs) [UUSI]:** UI-näkymä `expected_inputs`-taulukon hallintaan (tiedostot, chat, kyselylomakkeet).
- **Tab C: Työnkulun Rakentaja (DAG Builder):** Visuaalinen verkkoeditori askelten riippuvuuksien (`depends_on`) hallintaan.
- **Tab D: Raportit (Output Profiles) [UUSI]:** Kytkökset tulostedokumentteihin ja 2D/3D-näkymiin.

### Milestone 3: Solmun Ominaisuuspaneeli (Node Inspector)
Kun käyttäjä klikkaa DAG-editorissa solmua, oikeasta reunasta aukeaa Ominaisuuspaneeli (Property Drawer):
- **Strategiat:** `model_strategy` pudotusvalikko (hakee lennosta `system_config -> model_registry` avaimet).
- **Hookit:** Hallitaan `pre_hooks` ja `post_hooks` -listoja uudenlaisella monivalintakomponentilla (Multi-select Chips).
- **Datan reititys (Semantic Data Flow):** Älykäs Data Mapping UI (`input_mappings`). Määritetään lukeeko askel globaalia raakadataa (`$inputs`) vai aiemman askeleen tulosta (`$steps.x`).

### Milestone 4: Älykkäät Relaatiovalikot & Monikielinen Syöttökomponentti
- **The 5-Layer Strategy UI (I18nTextField):** Uusi lokalisointikomponentti, joka pakottaa "English-Only Mandate" -tekstit kognitiiviselle moottorille ja sallii lokaalit käännökset Pydantic `I18nText` muodossa.
- **Dynaamiset Dropdownit:** Relaatiovalikoissa vahva `SafeCast` ja V2 error boundaryt hyödynnetään estämään koko UI:n kaatuminen, sisältäen lokalisoinnin Fallback-mekanismit (`translations["en"]`).

### Milestone 5: Pre-Flight Validointi & Tilanhallinta (Dry Run)
Lisätään Editorin App Bariin pysyvä "Validoi Työnkulku" (Dry Run) -painike:
- Lähettää luonnoksen backendin algoritmeille validointia varten (Topological Sort).
- **Varoitukset:** Estää Orvot solmut (Orphan Nodes), katkenneet datareitit (viittaukset askeleisiin, joita ei ole `depends_on`-listalla) ja kehäviitteet.
- **Tilanhallinta:** Riverpod Dirty State -tilan ja API PUT Rollback -takaisinrullauksen hallinta (Fail-Fast RFC 7807 Exception -tilanteissa).


## 🛑 Rules of Engagement (Frontend)
- **No-String Mandate:** Kaikki uudet kiinteät UI-tekstit ("Yleiset Asetukset", "Työnkulun Vaiheet") on vietävä suoraan lokalisointitiedostoihin (`.arb`) eikä niitä saa hardkoodata koodiin.
- **Fail-Fast Boundary:** Kaikki lomakevalidaatiot (esim. tunnisteessa ei saa olla välilyöntejä) hoidetaan ensin Riverpod-tasolla välittömästi.

---

## 🛡️ Edge Cases & Error Handling

Epicin toteutuksessa on proaktiivisesti huomioitava seuraavat kriittiset V2-arkkitehtuurin asettamat reunaehdot:

1. **Välilehtien välinen tila ja "Likainen" (Dirty) Data:**
   - On määriteltävä selkeä **Auto-Save -mekanismi** tai tilaan sidottu **"Unsaved Changes" (Dirty State) -varoitus**, joka estää navigoinnin tai välilehden sulkemisen vahingossa, mikäli tallentamattomia muutoksia on olemassa (estää TTL-välimuistin katoamisen).

2. **DAG-Rakentajan Kehäviitteet ja Validointi (Pre-Flight):**
   - Käyttöliittymätasolla on oltava reaaliaikainen validointi. Kun pudotusvalikosta valitaan `depends_on`-riippuvuus toiseen askeleeseen, UI:n on matemaattisesti *disabloitava* askeleet, jotka johtaisivat kehäviitteeseen (infinite loop). Tämä estää viallisen graafin lähettämisen Backendin Kahnin algoritmille.

3. **Optimistisen päivityksen takaisinrullaus (Rollback):**
   - Jos API palauttaa virheen tallennuksesta (esim. RFC 7807 Exception), Riverpod-providerin on automaattisesti käynnistettävä Rollback-strategia palauttaen UI aiempaan jäädytettyyn, toimivaan tilaan, jotta UI ei jää synkronoimattomaan/korruptoituneeseen haamutilaan. Näytetään paikallinen `AppErrorExt` ilmoitus.

4. **Relaatiovalikkojen lokalisoinnin Fallback (The English-Only Mandate):**
   - Jos relaatiovalikossa haetaan esim. PromptBlockin nimeä, eikä käyttäjän UI-kielellä (esim. `fi`) löydy käännöstä tietokannasta, käyttöliittymän komponenteissa on implementoitava vahva fallback lukemaan enkku-data (`translations["en"]`) `SafeCast`-parsinnan kautta lennosta. Valikko ei saa renderöityä tyhjänä tai kaatua.

## 📝 Next Steps
Odotetaan käyttäjän hyväksyntää tai muutosehdotuksia `Epic 7` suunnitelmaan ja tämän jälkeen luodaan virallinen `implementation_plan.md` siirtyen koodaustilaan (Tier 2).
