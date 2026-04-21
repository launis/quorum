# **🚀 EPIC: The 2026 Foundation & The Big Bang Protocol**

**Epic ID:** EPIC-CORE-001

**Tila:** Ready for Development | **Prioriteetti:** P0 (Kriittinen Core-infrastruktuuri)

**Arkkitehtuuri:** Python 3.14+ (FastAPI), Pydantic V2 (Strict), PostgreSQL 16+ (JSONB) / TinyDB (Local DX), Firebase Auth (IdP-only), Flutter 3.27+.

## **🎯 Tavoite**

Rakentaa alusta alkaen kompromissiton, skaalautuva ja auditoitava (SOC2/ISO27001) B2B Enterprise SaaS \-alustan ydinarkkitehtuuri. Koska olemme puhtaalla pöydällä (Clean Slate), **emme tue taaksepäinyhteensopivuutta emmekä säästä legacy-koodia**. Kaikki vanhat tietomallit ja sekavat riippuvuudet tuhotaan ("The Big Bang").

Järjestelmän tuotantomoottoriksi pystytetään järeä **PostgreSQL (JSONB)** \-infrastruktuuri. Firebase typistetään pelkäksi "tyhmäksi" identiteetintarjoajaksi (Decoupled Identity), ja kaikki liiketoimintalogiikka, luvitus (RBAC) ja massadata siirretään täysin meidän hallinnassamme olevaan tietokantaan.

**Kriittinen reunaehto (The Local DX Mandate):** Kehittäjäkokemus (Developer Experience) on pyhä. Järjestelmä rakennetaan eristetyissä osissa. Jokaisen rakennetun osan on **aina oltava ajettavissa ja testattavissa lokaalisti PC:llä salamannopeasti asennusvapaan TinyDB:n (db\_v2.json) ja Firebase Emulatorin avulla**. PostgreSQL toimii rinnalla (Dockerissa), ja tietokantamoottoria voidaan vaihtaa lennosta pelkällä STORAGE\_BACKEND \-ympäristömuuttujalla ilman, että liiketoimintalogiikkaan tarvitsee koskea.

## ---

**🛑 Arkkitehtuurin Ehdottomat Säännöt (2026 Mandates)**

1. **The Zero Legacy Policy:** Koodiin ei jätetä yhtäkään \# TODO: legacy fallback \-kommenttia. Kaikki tietomallit noudattavat ConfigDict(strict=True, extra="forbid"). Ihmisluettavia tunnisteita ei sallita (Opaque ID: esim. org\_xyz123, usr\_abc987).  
2. **Storage Agnosticism (Dual-DX):** Liiketoimintalogiikka (Services) ja API-reitittimet eivät saa koskaan tietää tietokannan tyyppiä. Kaikki data I/O kulkee abstraktin StorageDriver-rajapinnan läpi.  
3. **Hybrid JSONB PostgreSQL:** Tuotantokantana on PostgreSQL. Emme luo kymmenien sarakkeiden jäykkiä relaatiotauluja. Tauluissa on vain kovat relaatiosarakkeet Tenant-turvallisuudelle (id, org\_id) ja dynaaminen document (JSONB) \-sarake Pydantic-malleille, suojattuna GIN-indekseillä.  
4. **Decoupled Identity (Auth-Only Firebase):** Firebase Auth hoitaa vain tunnistautumisen (Passkeys, SSO, MFA). JWT-tokenit ovat ohuita (Thin Tokens). Kaikki luvitus ja roolit (RBAC) asuvat omassa tietokannassamme O(1)-nopeudella luettavina.  
5. **Envelope Encryption (SOC2):** Kaikki sensitiivinen data (esim. asiakkaiden tuomat LLM-avaimet) salataan AES-GCM-algoritmilla ennen kantaan tallentamista (myös lokaalissa TinyDB:ssä\!). Tuotannossa Master-avain noudetaan GCP Secret Managerista, lokaalisti .env-tiedostosta.

## ---

**📋 VAIHEISTUS JA TYÖTEHTÄVÄT (Iterative Execution)**

Rakennamme perustan itsenäisissä vaiheissa. Vaihe katsotaan valmiiksi vasta, kun sen **Lokaali Testiportti (PC / TinyDB)** menee läpi vihreänä.

### **💥 VAIHE 1: Pure Domain & Cryptography (Tietomallit ja Salaus)**

**Tavoite:** Määritellä järjestelmän uusi SSOT (Single Source of Truth) Pydantic V2 \-malleilla ja rakentaa salauksen perusta. Tuhotaan vanhat mallit täysin.

* **Task 1.1: Opaque ID:t & Enum-roolit (models/auth.py):** Määritä vahvat tyypit (StripeOrgId, StripeUserId) ja rooli-enumit (TenantRole: ADMIN, MANAGER, MEMBER, VIEWER).  
* **Task 1.2: Tiukat DTO-mallit (models/dtos/auth\_dto.py):** Luo OrganizationDTO, UserDTO ja MembershipDTO. Pakota tiukka validointi ja tuhoa vanhat luokat.  
* **Task 1.3: Enterprise Envelope Encryption (core/crypto.py):** Rakenna AES-GCM toteutus. Luo OrganizationSecretsDTO, johon tallentuu vain encrypted\_llm\_key ja salauksen IV. Master-avain haetaan lokaalisti .env:stä ja tuotantovalmius GCP Secret Managerille koodataan valmiiksi.  
* **Task 1.4: Dual-DX Siemennysskripti (seed\_v2\_local\_db.py):** Kirjoita uusi skripti, joka luo System Root \-organisaation ja lokaalin Admin-käyttäjän Opaque ID:illä suoraan valittuun kantaan StorageDriver:in läpi.

🟢 **Lokaali Testiportti 1:** Aja siemennysskripti TinyDB:tä vasten. Avaa db\_v2.json PC:lläsi: ID:t ovat muotoa org\_xyz ja BYOK-avaimet näyttävät AES-GCM-salatulta siansaksalta. Koodikanta on puhdas mypy-virheistä.

### **💥 VAIHE 2: The PostgreSQL Foundation (Tuotantoinfran Pystytys)**

**Tavoite:** Perustaa järjestelmän varsinainen tuotantotietokanta lokaalin TinyDB:n rinnalle.

* **Task 2.1: PostgreSQL Infra (docker-compose.yml):** Lisää postgres:16-alpine kontti lokaalia testausta varten niille tilanteille, kun halutaan simuloida tuotantoa.  
* **Task 2.2: Hybrid Skeeman Luonti (database/schema.sql):** Määritä taulut: CREATE TABLE {collection} (id VARCHAR(64) PRIMARY KEY, org\_id VARCHAR(64) NOT NULL, document JSONB NOT NULL, created\_at TIMESTAMPTZ DEFAULT NOW());. Lisää GIN-indeksit document-sarakkeelle.  
* **Task 2.3: PostgresDriver \-toteutus (database/postgres\_driver.py):**  
  * Toteuta StorageDriver-rajapinta asynkronisella asyncpg-kirjastolla.  
  * Käännä Filter-luokan ehdot lennosta PostgreSQL JSONB \-operaattoreiksi (-\>\>, @\>).  
  * Toteuta UPSERT-logiikka (ON CONFLICT (id) DO UPDATE).  
* **Task 2.4: Storage Factoryn kytkentä (database/factory.py):** Reititä I/O-kutsut StorageBackend.POSTGRES tai StorageBackend.LOCAL (TinyDB) \-ympäristömuuttujan perusteella.

🟢 **Lokaali Testiportti 2:** Nosta lokaali Postgres-kontti pystyyn (Docker). Vaihda .env-muuttuja STORAGE\_BACKEND=POSTGRES. Aja siemennys. Varmista tietokantatyökalulla (DBeaver/pgAdmin), että JSONB-tallennus toimii täsmälleen samalla logiikalla PostgreSQL:ssä kuin TinyDB:ssä. Vaihda takaisin STORAGE\_BACKEND=MOCK jatkaaksesi kevyttä PC-kehitystä.

### **💥 VAIHE 3: Decoupled Identity (Identiteetin ja Luvituksen Erotus)**

**Tavoite:** Eriyttää luvitus Firebasesta. Firebase tuottaa vain JWT-tokenin, kaikki luvitus tapahtuu meidän omassa tietokannassamme.

* **Task 3.1: Emulator Bridge & Thin Tokens (services/auth\_service.py):** Reititä SDK lukemaan tokenit PC:n emulaattorista (127.0.0.1:9099). Pura Firebase-tokenista vain UID ja sähköposti (TokenDataDTO). Hylkää Firebasen omat Custom Claimsit (koska ne ylittäisivät 1KB rajan).  
* **Task 3.2: JIT (Just-In-Time) Provisioning (services/iam\_service.py):**  
  * Kun backend näkee uuden Firebase UID:n ensimmäistä kertaa, se luo käyttäjän lennosta omaan tietokantaamme (Upsert).  
  * Toteuta roolien ja luvitusten CRUD-operaatiot UnifiedWorkflowRepositoryn (StorageDriverin) kautta MembershipDTO:n avulla.

🟢 **Lokaali Testiportti 3:** Yksikkötestit TinyDB:llä varmistavat, että uusi Firebase-käyttäjä tallentuu eheästi db\_v2.json \-kantaan, ja oikeudet voidaan lukea ilman yhtäkään verkkokutsua Firebaseen.

### **💥 VAIHE 4: Aneemiset Reitittimet & O(1) Guards (API-Turvallisuus)**

**Tavoite:** Suojata API salamannopeilla riippuvuuksilla (Dependencies) ja estää IDOR-haavoittuvuudet deterministisesti.

* **Task 4.1: Active Tenant API (api/routers/auth.py):** Rakenna reititin työtilan vaihtamiselle. Aseta aktiivinen työtila muistiin (kiertää 1KB rajan ja mahdollistaa rajattomat jäsenyydet).  
* **Task 4.2: O(1) Revocation Guard (api/dependencies.py):** Rakenna In-Memory Mock Redis lokaaliin PC-kehitykseen (Python dict) ja aito Redis-integraatio tuotantoon. Takaa UID-tason käyttöoikeuksien välitön 0ms kumoaminen.  
* **Task 4.3: RequireTenantRole Guard:** Rakenna injektio, joka hakee käyttäjän aktiivisen roolin meidän kannastamme ja ampuu Fail-Fast 403 Forbidden \-virheen 0ms viiveellä, jos oikeudet eivät riitä pyydettyyn org\_id:hin.  
* **Task 4.4: Reitittimien siivous:** Refaktoroi reitittimet käyttämään yksinomaan uusia tiukkoja DTO-malleja ja Guard-injektiota.

🟢 **Lokaali Testiportti 4 (Swagger Validation):** Käynnistä FastAPI TinyDB:llä. Generoi lokaali emulaattori-token ja yritä hakea dataa väärällä org\_id:llä Swagger UI:sta. Varmista, että API hylkää pyynnön (403) heti ja deterministisesti.

### **💥 VAIHE 5: The Pro-Tool Client (Flutter & Zero-Latency UX)**

**Tavoite:** Kytkeä Desktop-First Flutter-sovellus saumattomasti uuteen arkkitehtuuriin.

* **Task 5.1: Dart DTO & Emulaattori-kytkentä:** Päivitä Flutterin datamallit vastaamaan Strict Pydantic \-malleja. Yhdistä lokaalisti localhost:9099 (Auth) ja localhost:8000 (FastAPI).  
* **Task 5.2: Optimistic UI (Zero-Latency SWR):** Riverpod-tila ylläpitää työtilan luvituksia lokaalisti. Työtilan vaihto tapahtuu UI:ssa 0 millisekunnissa.  
* **Task 5.3: Graceful Degradation:** UI piilottaa napit (esim. SizedBox.shrink()) lokaalin roolitiedon perusteella. API:n palauttamat 403-virheet näytetään tyylikkäinä Toast-ilmoituksina eikä kaatumisina.

🟢 **Lokaali Testiportti 5 (The Ultimate End-to-End Run):**

Koko järjestelmä pyörii lokaalisti PC:lläsi TinyDB:n ja emulaattoreiden varassa. Kirjaudut sisään, luot organisaation, vaihdat työtilaa ja tallennat LLM-avaimen täysin saumattomasti. Sammutat serverin, vaihdat .env \-tiedostosta STORAGE\_BACKEND=POSTGRES, nostat Postgres-kontin pystyyn ja toteat järjestelmän toimivan tismalleen samalla koodilla tuotantovalmiina\!