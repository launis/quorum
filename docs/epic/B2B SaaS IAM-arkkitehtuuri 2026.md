# **🚀 EPIC: IAM & Organisaatiomalli (SaaS 2026 - Nykyarkkitehtuurin Vahvistus)**

**Epic ID:** EPIC-IAM-001

**Tila:** Ready for Documentation/Hardening | **Prioriteetti:** P0 (Kriittinen Core-infrastruktuuri)

**Arkkitehtuuri:** Python 3.14+ (FastAPI), Pydantic V2, Local JWT Auth, Flutter 3.27+ (Riverpod 3.0)

## **🎯 Tavoite**

Vahvistaa ja dokumentoida Quorum V2 -järjestelmän nykyinen, litteä 1:1 -organisaatiomalli (Single-Tenant per User). Kirjautuminen ja valtuutus (Authorization) hoidetaan täysin Python-backendin lokaalilla JWT-mekanismilla. Järjestelmä luottaa yksinkertaiseen rakenteeseen, jossa yksi käyttäjä kuuluu tasan yhteen organisaatioon (`organization_id`), ja hänellä on järjestelmänlaajuinen litteä rooli (`UserRole`). Tämä malli takaa nopeuden, O(1) monimutkaisuuden luvituksessa ja yksinkertaisen koodikannan ylläpidon.

## **🛑 Arkkitehtuurin Ehdottomat Säännöt (2026 Mandates)**

1. **Opaque Stripe ID -Mandaatti:** Ihmisluettavia ID-tunnisteita ei tietokannassa sallita. Kaikki pääavaimet pakotetaan muotoon `org_[a-zA-Z0-9]{8,}` ja `usr_[a-zA-Z0-9]{8,}`.  
2. **Pydantic Strict Protocol:** Tietomalleissa ei sallita implisiittisiä oletusarvoja eikä joustavia tyyppejä. Käytössä `ConfigDict(strict=True, extra="forbid")`.  
3. **Anemic Routers:** FastAPI-reitittimet tekevät vain Pydantic-validoinnin. RBAC (Role-Based Access Control) ja tietokantakutsut delegoidaan aina luvitusinjektioille ja Service-kerrokseen.  
4. **Fail-Fast Error Handling:** Oikeuksien puute nostaa välittömästi `AppException(error_code=ErrorCodes.FORBIDDEN)` RFC 7807 -standardin mukaisesti.
5. **Flat 1:1 Identity Mandate:** Käyttäjä on kiinteästi sidottu yhteen organisaatioon `organization_id`-kentällä. Moniasiakkuutta (Multi-Tenant) ei tueta, jotta tietokantamalli pysyy äärimmäisen nopeana O(1) litteänä rakenteena ilman erillisiä "Membership" -liitostauluja.

## **🛡️ 1. Lokaali JWT ja Nollaluottamus (Zero-Trust)**

Järjestelmä luottaa 100% lokaaliin JWT-arkkitehtuuriin ilman ulkoista monoliittia (kuten Firebase Auth). Tämä takaa absoluuttisen kontrollin payloadin rakenteeseen.

- **Backend:** `auth.py` luo `TokenData`-mallin mukaisen payloadin, joka allekirjoitetaan turvallisesti backendin salaisuudella (`SECRET_KEY`).
- **Token Payload (`TokenData`):** Sisältää asiat, jotka määrittelevät identiteetin: `id` (StripeUserId), `role` (UserRole) ja `organization_id` (StripeOrgId).
- **Frontend:** Riverpod varastoi tokenin lokaalisti ja liittää sen automaattisesti jokaiseen pyyntöön `Authorization: Bearer` -otsakkeessa.
- **Validointi (Zero-Latency):** Reitittimen Injektio (`Depends(RequireRole)`) lukee tiedot tokenista suoraan muistissa purkamisen jälkeen, ilman yhtäkään asynkronista tietokantahakua. 

## **👥 2. Käyttäjäroolit ja Käyttöoikeudet (Flat Enum)**

Valtuutus perustuu yksittäiseen litteään `UserRole`-enumiin, joka määrittelee käyttäjän globaalin identiteetin. Erillistä "SystemRole" ja "TenantRole" -jaottelua ei ole olemassa, vaan rooli on absoluuttinen.

**Roolimäärittelyt (Strict Enums):**
```python
class UserRole(str, Enum):
    ROOT = "ROOT"        # System Owner / Platform Admin (Jumaltila)
    ADMIN = "ADMIN"      # Organization Admin (Tenantin hallinta)
    MANAGER = "MANAGER"  # Workflow/Process Lead (Työnkulkujen rakentaja)
    MEMBER = "MEMBER"    # Standard User (Operatiivinen ajo)
    VIEWER = "VIEWER"    # Read-Only Stakeholder
```

**Luvituslogiikka (API Guard):**
Jos reititin vaatii vähintään `MANAGER`-tason, Injektio tarkistaa onko tokenin `role` riittävä (esim. `MANAGER`, `ADMIN` tai `ROOT`). Jos tokenin organisaatio `organization_id` poikkeaa pyydetystä reitistä (ja rooli ei ole ROOT), API ampuu välittömästi Fail-Fast `403 Forbidden`. ROOT-rooli ohittaa automaattisesti organisaatiorajat vianmääritystä varten.

## **🔐 3. Bring Your Own Key (BYOK) ja Resurssien Eristys**

Quorum tukee aseta-kerran -tyylistä BYOK-mallia tekoälyavaimille, nojaten Pydantic-turvallisuuteen ja litteään organisaatioperimykseen.

**A. Tietokanta (The Secrets Vault):**
Avaimia ei saa koskaan palauttaa normaalin `Organization` -mallin tai `User` -mallin mukana, jotta niitä ei vahingossa sarjallisteta UI-kerrokseen. Avaimet tallennetaan erilliseen loogiseen lokeroon tai salaisuutena tietokantaan, johon pääsy on rajoitettu vain `ADMIN` tai `ROOT` -rooleille. Itse avain luokitellaan koodissa `pydantic.SecretStr` -tyypillä.

**B. Resolvoitumisen Hierarkia (Zero-Latency Loop):**
Kun järjestelmä tekee LLM-kutsun, se etsii avainta "Fallback" -hierarkialla:
1. Onko käyttäjän omalla `organization_id`:llä asetettu custom-avain? -> Jos kyllä, käytä sitä (Custom Quota).
2. Jos ei, lue globaalin juuriorganisaation (esim. `org_system000000`) tallentama oletusavain (Quorum Global Quota).
3. Jos järjestelmä-avainkin puuttuu -> Nosta deterministinen `AppException(ErrorCodes.QUOTA_EXHAUSTED)`.

## **⚙️ 4. The "Root" Bootstrap (Seed Protocol)**

Tietokantaa ei koskaan manipuloida suoraan (esim. JSON-tiedostoa muokkaamalla), koska Opaque ID -avaimet voivat korruptoitua helposti ihmisen käsittelyssä.

* **Tier 3 Database Reset (The IAM Clean Slate):**
  Kehitystyössä tietokannan nollaus tehdään tuhoamalla litteä `db_v2.json` ja ajamalla turvallinen Seed-prosessi tyhjästä.
* **Seed Data JSON & System Root:**
  Tiedoston `backend_v2/seed/seed_data.json` organisaatio (`"id": "org_system000000"`) pitää huolen siitä, että ensimmäiselle käyttäjälle konfiguroituu automaattisesti `ROOT`-oikeudet tietokannan generoinnin yhteydessä. Näin varmistetaan puhdas aloitus jokaiselle kehittäjälle lokaalissa ympäristössä.

## **✅ Laatuportit (Definition of Done)**

1. **Opaque Strictness:** Yksikään API-päätepiste ei ota vastaan ihmisluettavia avaimia. Kaikki ID:t ovat Pydantic-validoituja Opaque-tunnisteita (`org_`, `usr_`).
2. **Zero-Trust JWT Security:** API hylkää pyynnön 0 millisekunnissa DI-kerroksessa (403 Forbidden), jos tokenin `role` on riittämätön tai `organization_id` ei täsmää.
3. **ORM Leakage Estetty:** Yksikään reititin (`router.py`) ei koske tietokantaan. Tietokanta on kapseloitu Pydantic-validoituun Service- ja Repository -kerrokseen.
4. **1:1 Flat Integrity:** Koodiin ei vahingossakaan lisätä Multi-Tenant -relaatiotauluja (`MembershipDTO` jne). Käyttäjän tietue on täysin litteä ja O(1) haettava.
