# Epic 12: The Markdown Matrix Upgrade (LLM Context Optimization)

**Tavoitetila:** Vuoden 2026 Enterprise-tason AI-analyysien osumatarkkuuden maksimointi, hallusinaatioiden minimointi ja huomiomekanismin (Attention) hallinta. Siirtyminen raakatekstistä puhtaaseen kone-optimoituun Markdown-kontekstiin.

## 1. Tausta ja "Lost in the Middle" -ongelma

Modernit laajat kielimallit (LLM), kuten Gemini 2.5 Pro ja Claude 3.5, kärsivät tutkitusti ilmiöstä, jossa ne kykenevät lukemaan syötteen alun ja lopun, mutta sivuuttavat pitkien tekstien keskellä olevat monimutkaiset nyanssit. Tämä on suurin este "Zero-Compromise" -analyyseille,  kun tekoäly lukee arviointimatriisien pitkiä sääntöketjuja tai 100-sivuisia PDF-dokumentteja.

Tämä työrupeama ratkaisee ongelman hyödyntämällä sitä, miten tekoälymallit on opetettu: ne ymmärtävät Git/GitHub-Markdownia natiivisti. Markdownin otsikot (`#`) toimivat huomiomekanismille (Attention Weights) "kirjanmerkkeinä", estäen keskittymiskyvyn pettämisen. Taulukot (`| --- |`) säilyttävät datan 2D-avaruudellisen rakenteen, joka perinteisessä tekstin purkamisessa litistyy lukukelvottomaksi aakkoskeitoksi.

## 2. Kooditason Muutokset (Zero-Deploy)

Tämä Epic hyödyntää "De-Generator"-arkkitehtuurin tuomaa ylivoimaista etua: mikään muutos ei vaadi koskemista tietokantamalleihin tai Flutter-asiakasohjelmistoon. Kaikki muutokset tehdään keskitettyihin kääntäjiin ja hookeihin.

### Vaihe 1: `PromptCompiler` renderöintimoottorin päivitys
Nykyinen `PromptCompiler._extract_value_from_state` tuottaa lennosta pseudo-markdownia (tyylillä `--- OSIO ---`). 
Tämä vaihdetaan aitoon Markdowniin:
- Pääotsikot luodaan H1/H2 tason Markdownilla (`# Tulokset` , `## Askel 1`).
- JSON-avaimet tulostetaan rakenteellisesti erottuvina teksteinä, jolloin LLM:n konteksti-ikkuna havaitsee siirtymät selkärangan tasolla.

### Vaihe 2: Arviointimatriisien lennosta rakentaminen (Markdown Tables)
Kun työnkulkujen (Workflows) matriisit ja arviointisäännöt syötetään LLM:n ohjeisiin, `PromptCompiler` rakentaa niistä täydellisen Markdown-taulukon:
```markdown
# Arviointimatriisi: Taloudellinen Riski
| Kriteeri | Skaala | Piste (1) | Piste (5) |
|---|---|---|---|
| **Pääomarakenne** | 1-5 | Korkeasti velkaantunut | Vahva oma pääoma |
```
Tämä takaa, että AI ei yhdistä vääriä kriteerejä tai tulkitse sääntöjä ristiin, sillä kone "näkee" sarakkeiden raamit sisäisillä painokertoimillaan.

### Vaihe 3: PDF -> Markdown Input Processing (The Hook)
- Pre-Flight -vaiheessa (`input_processing.py`) siirrytään käyttämään uuden sukupolven kirjastoa (kuten `pymupdf4llm` tai `marker-pdf`).
- Käyttäjän lataamista alkuperäisistä 100-sivuisista PDF-tiedostoista puristetaan ulos täydellisesti jäsenneltyjä Markdown-dokumentteja, joissa alkuperäiset PDF-otsikot kääntyvät `# Headereiksi` ja PDF-taulukot `Markdown-taulukoiksi`.
- Tämä uusiutunut teksti tallentuu `inputs`-koriin, jolloin semanttinen reititin (Semantic Routing, esim. `$inputs.document`) välittää sen 10-kertaisesti älykkäämpänä LLM-solmuille.

## 3. DoD (Definition of Done)

* [ ] `PromptCompiler._extract_value_from_state` muotoilee syötteet ja historia-datat H1/H2 Markdowniin.
* [ ] Työnkulkujen säännöstöt (Matrices / PromptBlocks) muuttuvat LLM:lle näkyvässä promptissa visuaalisiksi Markdown-taulukoiksi.
* [ ] PDF-tiedostot prosessoidaan tallennettaessa leipätekstin sijaan 100% puhtaaksi Markdowniksi säilyttäen rivinvaihdot, kappale-erot, lihavoinnit ja taulukkorakenteet.
* [ ] Validaatio tehdyistä Pydantic Logician- ja Falsifier-ajoista osoittaa, ettei malli sekoita pitkien tekstien kriteerejä keskenään "Lost in the Middle" -ilmiön vuoksi.
