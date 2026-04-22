# **🚀 EPIC: The 2026 Agile Launchpad & CI/CD Pipeline**

**Epic ID:** EPIC-INFRA-002 (PaaS Edition)

**Tila:** Ready for Development | **Prioriteetti:** P1 (Julkaisuinfra)

**Infrastruktuuri (Phase 1):** Render.com / Railway (FastAPI), Neon.tech / Supabase (Serverless Postgres), Firebase Hosting (Flutter Web), GitHub Actions (CI/CD).

## **🎯 Tavoite**

Pystyttää Quorumille nopea, kustannustehokas ja täysin automatisoitu tuotantoympäristö (PaaS) hyödyntäen markkinoiden parhaita Serverless-työkaluja. Tavoitteena on saavuttaa tuotantovalmius päivissä ilman monimutkaisen VPC-infrastruktuurin pystytystä, mutta säilyttää koodin 100 % yhteensopivuus myöhempää GCP-siirtymää varten.

Rakennetaan **"Zero-Touch" CI/CD-putki** GitHub Actionsin avulla: jokainen Pull Request testataan automaattisesti lokaalilla In-Memory/TinyDB-kannalla ja main-haaraan yhdistetty koodi julkaistaan saumattomasti (Zero-Downtime) tuotantoon.

## ---

**🛑 Infrastruktuurin ja CI/CD:n Ehdottomat Säännöt (2026 Mandates)**

1. **The Ephemeral Backend Mandate:** FastAPI-kontti (Render/Railway) on täysin tilaton. Se voi käynnistyä uudelleen tai kaatua milloin tahansa datan katoamatta. Kaikki pysyvä tila on PostgreSQL:ssä (Neon). Lokaalia levytilaa ei käytetä mihinkään.  
2. **Single Source of Secrets:** Kehittäjien koneilla ei pyöri tuotantoavaimia. Tuotannon QUORUM\_MASTER\_KEY (Envelope Encryptionille) ja DATABASE\_URL asuvat vain PaaS-palveluntarjoajan salaisuusvarastossa (Environment Variables). Ne eivät koskaan päädy GitHubiin.  
3. **Automated Quality Gates (Fail-Fast):** Koodia ei voi julkaista tuotantoon, jos CI-putki kaatuu. Putken on läpäistävä pytest (Mock-kannalla), mypy (Strict Typing) ja ruff (Linter) ennen kontin rakentamista. Nollatoleranssi varoituksille.  
4. **Decoupled Edge:** Frontend (Flutter Web) julkaistaan erilliseen CDN-verkkoon (Firebase Hosting) irrallaan backendistä. Tämä mahdollistaa käyttöliittymän salamannopean latautumisen globaalisti backend-katkoista riippumatta.

## ---

**📋 VAIHEISTUS JA TYÖTEHTÄVÄT (The Deployment Blueprint)**

### **💥 VAIHE 1: The Serverless Database (PostgreSQL JSONB)**

**Tavoite:** Pystyttää moderni PostgreSQL 16+ \-tietokanta minuuteissa nollakonfiguraatiolla.

* **Task 1.1 (Neon.tech / Supabase):** Luo uusi tietokantaprojekti. Neon skaalautuu nollaan (säästää rahaa yöllä) ja tukee natively JSONB-operaattoreita ja vektorihakuja (pgvector).  
* **Task 1.2:** Ota talteen yhteysmerkkijono (Connection String: postgresql://user:pass@host/dbname?sslmode=require).

### **💥 VAIHE 2: The PaaS Backend (FastAPI Docker)**

**Tavoite:** Yhdistää Docker-kontti julkiseen verkkoon ilman SSL-sertifikaattien tai load balancereiden manuaalista säätämistä.

* **Task 2.1 (Render.com / Railway.app):** Luo uusi "Web Service" ja yhdistä se suoraan GitHub-repoon. Alusta tunnistaa backend\_v2/Dockerfile:n automaattisesti.  
* **Task 2.2:** Määritä tuotannon ympäristömuuttujat alustan hallintapaneeliin:  
  * STORAGE\_BACKEND=POSTGRES  
  * DATABASE\_URL=\<Neonin\_osoite\>  
  * QUORUM\_MASTER\_KEY=\<vähintään 32-merkkinen satunnainen aes-avain\>

### **💥 VAIHE 3: The Edge Frontend (Flutter Web)**

**Tavoite:** Varmistaa, että asiakassovellus on aina saatavilla ja latautuu nopeasti.

* **Task 3.1 (Firebase Hosting):** Koska käytämme jo Firebase Authia identiteetinhallintaan, Firebase Hosting on loogisin ja nopein paikka kääntää Flutter Web \-sovellus.  
* **Task 3.2:** Lisää PaaS-backendin URL (esim. https://quorum-api.onrender.com) Firebase Authin sallittuihin domain-osoitteisiin (Authorized Domains).

### **💥 VAIHE 4: Continuous Integration (CI \- Laatuportit GitHubissa)**

**Tavoite:** Varmistaa, että rikkinäinen koodi ei koskaan päädy tuotantoon.

* **Task 4.1: The Quality Gate Workflow (.github/workflows/backend-ci.yml):**  
  * **Laukaisin:** Kaikki Pull Requestit (PR) kohti main-haaraa.  
  * **Steppi 1 (Linterit):** Ajaa uv run ruff check . ja uv run mypy .. (Pydantic-tyyppivirheet tai Opaque ID \-sääntöjen rikkominen kaatavat putken välittömästi).  
  * **Steppi 2 (Yksikkötestit):** Ajaa uv run pytest.  
    * *Arkkitehtuurin taika:* Testit ajetaan asettamalla CI-putkessa STORAGE\_BACKEND=MOCK (TinyDB). Näin testit ovat salamannopeita (millisekunteja) ja ne testaavat Envelope Encryptionin sekä RBAC-luvituksen täydellisesti ilman, että GitHubin palvelimelle tarvitsee pystyttää raskasta Postgres-konttia\!

### **💥 VAIHE 5: Continuous Deployment (CD \- Automaattinen Julkaisu)**

**Tavoite:** Nollakäyttökatkon (Zero-Downtime) julkaisu heti, kun koodi yhdistetään päähaaraan.

* **Task 5.1: Backend Deploy Workflow (.github/workflows/backend-cd.yml):**  
  * **Laukaisin:** Koodi yhdistetään main-haaraan, ja CI-laatuportti on vihreä.  
  * **Steppi:** GitHub Action kutsuu Renderin "Deploy Hook URL" \-osoitetta (tai käyttää Renderin omaa GitHub-integraatiota). Render rakentaa Docker-kontin taustalla ja siirtää liikenteen uuteen versioon vasta, kun FastAPI:n /health \-endpoint palauttaa 200 OK.  
* **Task 5.2: Frontend Deploy Workflow (.github/workflows/frontend-cd.yml):**  
  * **Laukaisin:** Muutoksia client\_app\_v2/ kansiossa main-haarassa.  
  * **Steppi:** GitHub Actions asentaa Flutter SDK:n (3.27+), kääntää tuotanto-optimoidun WebAssembly-version (flutter build web \--wasm) ja julkaisee sen Firebase Hostingiin (firebase deploy \--only hosting) GitHub Secrets \-varastoon tallennetulla CI-avaimella.

### ---

**✅ Miksi tämä on ylivoimainen 2026 MVP \-lähestymistapa?**

1. **Infran pystytys tunneissa, ei viikoissa:** Vältämme raskaat Terraform-koodaukset ja IAM-roolien virittelyt GCP:ssä. Alusta on livenä samana päivänä.  
2. **Korkea Kehitysnopeus (Velocity):** Git Push main-haaraan on ainoa asia, mitä kehittäjän tarvitsee tehdä. GitHub, Render ja Firebase hoitavat loput.  
3. **Tuotantovalmius:** Vaikka kyse on PaaS-infrasta, alla pyörii aito PostgreSQL 16\. Datamalli (JSONB \+ Opaque ID:t \+ Envelope Encryption) on tismalleen sama kuin myöhemmässä raskaassa GCP-infrassa. Tietokannan migraatio Neonista GCP Cloud SQL:ään myöhemmin on triviaali pg\_dump \-operaatio.  
4. **Local DX Säilyy:** PC:lläsi voit edelleen kehittää pelkän TinyDB:n ja .env-tiedoston varassa vailla huolta pilvipalvelimista tai Dockereista.