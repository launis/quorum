# V2 Production Deployment Strategy & CI/CD Blueprint

Tässä dokumentissa on hahmoteltu holistinen arkkitehtuuri, jolla eristetään turvallisesti paikallinen kehitys (PC + TinyDB) loppukäyttäjien tuotantoympäristöstä (Google Cloud / Firebase + Cloud Firestore), samalla kun kaikki ohjataan puhtaan GitHub Actions -liukuhihnan (CI/CD) kautta.

---

## 1. Ympäristöjen eristys (Dual-Environment Architecture)

### 🔴 Paikallinen ympäristö (Development / Studio)
*Ideologia: Nopea iteraatio, nolla kustannusta, kokeilu vapaata as in "Poor Man's Prod".*
- **Tietokanta:** `TinyDB` (data tallentuu tiedostoihin `data/db_v2.json` ja `data/db.json`).
- **Backend:** `FastAPI` ajetaan lokaalisti `localhost:8000`.
- **Frontend:** `Flutter Web` tai työpöytäsovellus osoittaa osoitteeseen `localhost:8000/v2/`.
- **Datagovernance:** Kaikki uudet matriisit ja kokoonpanot luodaan lokaalilla Admin Studiolla, ladataan myöhemmin `seed_data.json` -tiedostoon, ja testataan ajamalla `python backend_v2/seed/run_seed.py local`.

### 🟢 Tuotantoympäristö (Production / End-Users)
*Ideologia: 100% vakaa, skaalautuva, vain GitHub CI/CD:n kautta julkaistava, julkinen loppukäyttäjille.*
- **Tietokanta:** Google Cloud Firestore (Hallinnoi käyttäjädataa, valmiita Workflow-runkoja ja matriiseja).
- **Backend:** Google Cloud Run (Palvelin skaalautuu nollasta ylöspäin tarpeen mukaan. Koodi pyörii eristetyssä Docker-kontissa GCP:ssä).
- **Frontend:** Firebase Hosting (Tarjoilee Flutter-sovelluksen globaalin CDN-verkon (Content Delivery Network) kautta salamannopeasti selaimeen).
- **Datagovernance:** `seed_data.json`-päivitykset "pusketaan" tuotannon Firestore-tietokantaan käskyllä `python backend_v2/seed/run_seed.py firestore` joko CI/CD-putken kautta tai manuaalisesti tuotannon päivityssyklin yhteydessä.

---

## 2. GitHub Versionhallinta ja Haarat (Branching Strategy)

Koska teet kehitystä yksin ja haluat pitää tuotannon vakaana:

- **`main` -haara (Tuotanto):**
  - Tässä haarassa on vain ja ainoastaan se koodi, jonka haluat loppukäyttäjien näkevän.
  - Mitään koodia ei koskaan kirjoiteta suoraan tänne.
- **`dev` tai `feature` -haarat (Kehitys):**
  - Ohjelmoit täällä paikallisella PC:llä TinyDB:tä vasten.
  - Kun ominaisuus (esim. Epic 6) on valmis ja paikallisesti testattu, teet Pull Requestin tai Mergen suoraan `main`-haaraan.

---

## 3. Automaatio: GitHub Actions (CI/CD Pipeline)

Rakennamme `.github/workflows/deploy-prod.yml` -tiedoston. Jatkossa **aina kun teet git push -komennon `main` -haaraan**, GitHub työntekijät (runners) suorittavat automaattisesti seuraavan putken (Pipeline) minuuteissa:

### Steppi 1: Lähdekoodin tarkastus
- Ajaa `ruff` ja `mypy` -tarkistukset varmistaen, ettei tuotantoon mene rikkinäistä arkkitehtuuria (`Fail-Fast`).
- Ajaa `pytest` -yksikkötestit.

### Steppi 2: Frontendin (Flutter) Tuotanto-build
- Caching-avusteinen Flutter-kääntäjä lataa koodin.
- Suorittaa komennon `flutter build web --release`.
- Ottaa automaattisesti yhteyden Firebaseen (salakirjattu `FIREBASE_TOKEN` GitHub Secrets -asetuksissa).
- Suorittaa komennon `firebase deploy --only hosting`. => **Käyttöliittymä päivitetty!**

### Steppi 3: Backendin (GCP Cloud Run) Tuotanto-build
- Rakentaa Docker-imagen `backend_v2/Dockerfile`:n perusteella.
- Puskee Docker-imagen Google Cloudin Artifact Registryyn (GCP).
- Käynnistää Cloud Run -komennon vaihtaen uuden imagen livenä ilman käyttökatkoa (Zero-Downtime Deployment). => **Backend päivitetty!**

---

## 4. Kriittiset päätökset yhteiseen pohdintaan (Kysymyksiä sinulle)

Haluan varmistaa, että arkkitehtuuri palvelee visiotasi täsmälleen. Pallotellaan näitä kolmea asiaa:

**A. API-osoitteen (URL) ohjaus:**
Tuotanto-Flutterin täytyy tietää, että sen pitää yhdistää Cloud Runin osoitteeseen (esim. `https://quorum-api-...run.app/v2/`), eikä `localhost:8000/v2/`. Haluatko, että tämä hoidetaan .env -tiedostolla (esim. `--dart-define=API_URL=...`), vai teemmekö logiikan, joka päättelee sen selaimeesta itse, jottei sinun tarvitse muistaa kumpaakaan käynnistäessäsi buildin?

**B. Tietokannan julkaisu (Seeding-sykli):**
Kun Pushaat koodin `main`-haaraan, päivittyykö myös Firestoren `seed_data.json` -sisältö *automaattisesti*, vai haluatko mieluummin ajaa tietokannan rakenteelliset päivitykset (`run_seed.py firestore`) **manuaalisesti** PC:ltäsi turvallisuuden vuoksi, kun tiedät koodin siirtyneen tuotantoon oikein? 

**C. Autentikaatio (Firebase Auth):**
Koska Firebase on jo käytössäsi, ja aiot tuoda aitoja käyttäjiä: paikallisesti et ehkä halua tuhlata Firebase Auth -kutsuja kehityksen aikana. Tällä hetkellä Quorumissa voi mockata identiteettejä paikallisesti. Pidetäänkö kiinni siitä, että "LOCAL" tilassa Auth ohitetaan tai reititetään testitokensiin, ja vasta Cloud Runissa Firebase-tunnistus on 100% ehdoton?
