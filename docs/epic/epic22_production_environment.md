# EPIC 22: Tuotanto ja Tuotantoympäristö (Production Environment)

Tämä on keräilydokumentti Epic 22 -kehityssyklille, joka keskittyy järjestelmän viemiseen ja skaalaamiseen tuotantoympäristössä (kuten Google Cloud Run ja Firestore). Tänne kerätään hajallaan olevia arkkitehtuurioivalluksia ja vaatimuksia tuotannon näkökulmasta sitä mukaa, kun niitä ilmenee.

---

## 1. Build-Time Artifacts (Valmisteluvaiheen Välimuistit ja Artefaktit)

Yksi tuotantoarkkitehtuurin tärkeimmistä säännöistä on datan irrotus koodista (Separation of State). Kehitysympäristössä kerääntyvät sadat paikalliset JSON-tiedostot tai konfiguraatiovälimuistit (kuten `atomization_cache.json`) eivät ole reaaliaikaisia tietokantoja. Tuotannossa nämä toimivat yksinomaan ns. **"Build-Time Artifacteina"**.

### Toimintaperiaate
Kun järjestelmä pystytetään uuteen tuotantoympäristöön (Deployment) tai siinä suoritetaan tietokannan alustus (Initialization/Seeding), näillä artefakteilla on vain yksi lyhyt elämäntehtävä:
1. **Lokaali asettelu:** Kehitys- ja CI/CD -putki (esim. GitHub Actions) pitää JSON-välimuistit mukanaan estääkseen turhat ja kalliit LLM-laskennat uutta kantaa pystyttäessä (esim. satojen kriteereiden atomisoinnin odottelu Vertex AI:lta).
2. **Kova siirto pilveen (Seeding):** Tietokannan alustusskripti (Seeder) lukee nämä JSON-tiedostot ja puskee niiden datan natiivisti suoraan Firestore-tietokantaan (esim. kirjoittaen valmiit atomit `prompt_blocks` kokoelman dokumenteiksi).
3. **Tuotantoajo (Runtime):** Tämän siemennyksen jälkeen lokaaleilla JSON-tiedostoilla ei ole enää mitään virkaa käynnissä olevassa ohjelmistossa. FastAPI-palvelin lukee kaiken konfiguraation, kriteeristöt ja arviointimallit yksinomaan Firestore-tietokannasta millisekuntitason NoSQL-hakuina, täysin eristettynä konttinsa fyysisestä lokaalista levytilasta.

Tämä ratkaisu takaa nopean palautumisen ohjelmistokaatumisissa, säästää valtavasti Cloud LLM -API kustannuksissa ja eristää tuotantopalvelimen tila-anarkiasta.
