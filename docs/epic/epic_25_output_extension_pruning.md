# Epic 25: Output Extension Pruning & FinOps Hardening

## 1. Liiketoiminnallinen Tavoite ja Ongelman Kuvaus
Tällä hetkellä `output_extensions` -avaimet (`[citation, falsification, coaching, ...]`) ovat aktivoituna lähes jokaisessa `seed_data.json` -tiedoston PromptBlockissa. Tämä aiheuttaa merkittävää token-räjähdystä, altistaa mallin hallusinaatioille ylianalysoinnin vuoksi ja hidastaa suorituskykyä aiheuttaen Google Vertex AI 429 -kiintiökattojen laukeamista.

Tämän Epicin tavoitteena on poistaa `output_extensions` armottomasti kaikista muista paitsi `category_id: "matrix"` (arvioivista) lohkoista. Synteesi-, raportti- ja ohjetekstilohkot pakotetaan muotoon `output_extensions: []`. Tällä on suora kustannuksia leikkaava ja AI:n kognitiivista virhemarginaalia pienentävä vaikutus.

## 2. Suoritusstrategia (Python Migration)
Yli puolen megatavun `seed_data.json` -tiedostoa ei saa muokata käsin. Muutos suoritetaan täysin deterministisellä ja monivarmistetulla Python-skriptillä (`scripts/epic25_prune_extensions.py`).

### 2.1 Monivarmistettu Työnkulku
1. **Turvaverkko (Varmuuskopiointi):** Skripti kopioi automaattisesti `seed_data.json` -> `seed_data_backup_epic25.json` ennen yhdenkään bitin muuttamista. Jos jokin menee vikaan, palautus on yhden komennon päässä.
2. **Looginen Karsinta:** Skripti iteroi `prompt_blocks` -sanakirjan läpi. Jos `category_id != "matrix"` ja `output_extensions` sisältää arvoja, taulukko tyhjennetään. Jos kategoria on matriisi, taulukko jätetään ennalleen (tai karsitaan tietyistä haittakentistä, jos niin määritetään myöhemmin).
3. **Kolminkertainen Varmistus (Triple-Validation):**
   - *Matemaattinen tasapaino:* Skripti tarkistaa, että prosessoinnin jälkeen `prompt_blocks`-avainten kokonaismäärä on täsmälleen sama kuin alussa. Yhtäkään tietuetta ei saa kadota.
   - *Matriisien Koskemattomuus:* Ohjelmallinen Assertion varmistaa, että vahingossakaan yksikään matriisi-luokan tietue ei ole menettänyt alkuperäistä extensions-listaansa.
   - *Pydantic Compile-Test:* Uusi JSON ajetaan välittömästi V2 Pydantic -skeemojen (`model_validate`) läpi skriptin muistissa estäen `extra="forbid"` kaatumiset lennosta.
4. **Tekoälyavusteinen Pistokoe (AI Spot Check):** Skripti valitsee satunnaisesti 2 karsittua synteesilohkoa ja 1 säilytetyn matriisin, lähettää muutoksen taustalla paikalliselle LLM:lle tarkistettavaksi Promptina ("Onko tämä muutos tehty arkkitehtuuriohjeistuksen mukaisesti?") ja vaatii skriptin ajajalta `y/n` vahvistuksen näytölle tulostetun tekoälyn audit-lausunnon perusteella ennen lopullista tiedostoon tallentamista.

## 3. Käyttöliittymän (Frontend) Odotukset
Muutoksen on heijastuttava saumattomasti Flutter-asiakasohjelmaan (Admin Studio V2).
* UI-renderöintimoottori päättelee sallitut kytkimet suoraan `output_extensions` -taulukosta (`lib/core/models/prompt_block.dart`).
* Kun synteesilohkojen taulukot tyhjennetään backendissä, Frontendin De-Generator UI ymmärtää lennosta piilottaa kaikki "Citation", "Coaching" ja "Justification" -painikkeet näiden lohkojen konfiguraatiovalikosta.
* Tämä poistaa Admin-käyttäjiltä UI-sekamelskan ja estää heitä aktivoimasta epäyhteensopivia kytkimiä tästä eteenpäin.

## 4. Hyväksymiskriteerit (DoD)
- [ ] Varmuuskopio `seed_data.json` -tiedostosta luotu scriptin toimesta.
- [ ] Python-karsintaskripti ajaa onnistuneesti läpi "Triple Validation" -tarkistukset.
- [ ] Sisäänrakennettu tekoälyn pistokoe-evaluaatio raportoi nollavirhettä ja vahvistaa operaation laadun stdoutissa.
- [ ] Kaikki non-matrix -lohkot sisältävät vain tyhjän listan `output_extensions: []`.
- [ ] `run_seed.py` -komento populoitsee tietokannan ilman virheitä uudella datalla.
- [ ] UI ei näytä enää rasti-ruutuun valitoja Extensions-ominaisuuksille, jos kyseessä on synteesilohko.
