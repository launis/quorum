# EPIC 22: Tuotanto ja Tuotantoympäristö (Production Environment)

Tämä on keräilydokumentti Epic 22 -kehityssyklille, joka keskittyy järjestelmän viemiseen ja skaalaamiseen tuotantoympäristössä (Google Cloud Run ja Firestore). Tänne kerätään arkkitehtuurioivallukset ja vaatimukset tuotannon näkökulmasta sitä mukaa, kun niitä ilmenee.

---

## 1. Datan ja Tilan Eristäminen (Separation of State)

Yksi tuotantoarkkitehtuurin (`StorageBackend.FIRESTORE`) tärkeimmistä säännöistä on lokaalin tilan irrotus koodista (Separation of State). 

**Nykytilan ja Epicin Selvennys:** 
Kehitysympäristössä (`StorageBackend.LOCAL`) käytämme NoSQL-tietokantana fyysistä `data/db_v2.json` -tiedostoa. Tuotannossa tätä tiedostoa **ei käytetä lainkaan**, sillä Cloud Run -kontit ovat tilattomia (stateless) ja skaalautuvat horisontaalisesti. Kaikki reaaliaikainen data elää yksinomaan Firestore-tietokannassa. Lokaalin ja tuotannon välinen rajanveto hoidetaan `backend_v2/settings.py` -tiedoston `StorageBackend`-enumilla.

## 2. Build-Time Artifacts (Valmisteluvaiheen Välimuistit)

Tuotanto-käyttöönoton (Deployment) yhteydessä lähdekoodin mukana kulkee JSON-tiedostoja (erityisesti `backend_v2/seed/seed_data.json` ja `backend_v2/seed/atomization_cache.json`). Näitä ei käytetä tuotannossa lennosta (Runtime), vaan ne toimivat yksinomaan **"Build-Time Artifacteina"** tietokannan siemennysvaiheessa.

### Toimintaperiaate (The Seeding Pipeline)
Kun järjestelmä pystytetään uuteen tuotantoympäristöön, näillä artefakteilla on tarkasti rajattu rooli:

1. **Lokaali asettelu (CI/CD):** Kehitys- ja CI/CD -putki pitää `atomization_cache.json` -välimuistin mukanaan estääkseen turhat, hitaat ja kalliit LLM-laskennat uutta kantaa pystyttäessä (esim. raskaiden arviointikriteereiden purku `PromptAtomizerilla`). Tämä on kriittinen FinOps-mekanismi.
2. **Kova siirto pilveen (Seeding):** Tietokannan alustusskripti (`run_seed.py`) lukee `seed_data.json` ja välimuistitiedostot, pureskelee ne Pydantic-malleiksi, ja puskee datan natiivisti suoraan Firestore-tietokantaan. Data reititetään `Unified Workflow Repositoryn` kautta oikeisiin kokoelmiin. Aiemmassa luonnoksessa puhuttu "prompt_blocks-kokoelma" ei ole kirjaimellinen totuus, sillä V2-arkkitehtuuri nojaa yhtenäistettyyn Repository-reititykseen.
3. **Tuotantoajo (Runtime):** Tämän siemennyksen jälkeen lokaaleilla JSON-tiedostoilla (`seed_data.json`, `atomization_cache.json`, saatika `db_v2.json`) ei ole enää mitään virkaa käynnissä olevassa ohjelmistossa. FastAPI-palvelin lukee kaiken konfiguraation, kriteeristöt ja arviointimallit yksinomaan Firestoresta millisekuntitason NoSQL-hakuina, täysin eristettynä konttinsa fyysisestä levytilasta.

Tämä ratkaisu takaa nopean palautumisen ohjelmistokaatumisissa, säästää valtavasti Cloud LLM -API kustannuksissa ja varmistaa, että tuotantopalvelimet voivat skaalautua vapaasti ilman tila-anarkiaa.
