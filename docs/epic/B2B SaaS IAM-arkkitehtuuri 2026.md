
# **🚀 EPIC: B2B Multi-Tenant IAM & Organisaatiomalli (SaaS 2026\)**

**Epic ID:** EPIC-IAM-001

**Tila:** Ready for Development | **Prioriteetti:** P0 (Kriittinen Core-infrastruktuuri)

**Arkkitehtuuri:** Python 3.14+ (FastAPI), Pydantic V2, Firebase Auth & Admin SDK, Flutter 3.27+ (Riverpod 3.0)

## **🎯 Tavoite**

Rakentaa täysin eristetty ja O(1)-nopeudella skaalautuva B2B SaaS IAM \-järjestelmä. Kirjautuminen delegoidaan Firebase Authille, mutta valtuutus (Authorization) ja tenant-eristys hoidetaan Python-backendin **Domain Service \-kerroksessa** hyödyntäen Firebase Custom Claimseja. Järjestelmä erottaa globaalit ylläpitäjät (System Root) ja asiakasorganisaatioiden käyttäjät (Tenants) toisistaan turvallisesti.

## **🛑 Arkkitehtuurin Ehdottomat Säännöt (2026 Mandates)**

1. **Opaque Stripe ID \-Mandaatti:** Ihmisluettavia ID-tunnisteita ei tietokannassa sallita. Kaikki pääavaimet pakotetaan muotoon org\_\[a-zA-Z0-9\]{8,} ja usr\_\[a-zA-Z0-9\]{8,}.  
2. **Pydantic Strict Protocol:** Tietomalleissa ei sallita implisiittisiä oletusarvoja eikä joustavia tyyppejä. Käytössä ConfigDict(strict=True, extra="forbid").  
3. **Anemic Routers:** FastAPI-reitittimet tekevät vain Pydantic-validoinnin. RBAC (Role-Based Access Control) ja tietokantakutsut delegoidaan aina Service-kerrokseen.  
4. **Fail-Fast Error Handling:** Oikeuksien puute nostaa välittömästi AppException(error\_code=ErrorCodes.FORBIDDEN) RFC 7807 \-standardin mukaisesti (Dual-Reporting: Lokiin tekninen syy, API:in turvallinen enum).
5. **The Zero Legacy Mandate (Clean Slate 2026):** Vanhaa IAM-koodia ei säästetä, eikä taaksepäinyhteensopivuutta (fallbacks/oikopolut) tueta. Kaikki rakennetaan täysin puhtaalta pöydältä alan tuoreimpien best practice 2026 -ohjeiden mukaisesti. Vanhaan IAM-infrastruktuuriin poltetaan sillat säälimättä.
6. **Immutable Audit Trail Mandate (SOC2/ISO27001):** Jokainen identiteetin ja luvituksen tilaa muuttava toimenpide (mutaatio) on käärittävä Saga-patterniin (Event Sourcing). Jokaisella mutaatiolla muodostetaan ja tallennetaan asynkronisesti erillinen muuttumaton `TraceEvent` (Action, Actor, Target). Tällä varmistetaan Enterprise B2B -vaatimusten mukainen 100% jäljitettävyys ilman hiljaisia tietokantaylikirjoituksia.

## **🌉 1. Testimaailman silta: The Emulator Protocol**
Lokaalin kehitysympäristön on kyettävä kryptografiseen JWT-purkuun aivan kuten tuotannonkin. Pakotamme järjestelmän käyttämään **Firebase Local Emulator Suitea**.
- **Backend (backend_v2/core/firebase_setup.py)**: Kun `.env`-tiedostossa on `USE_MOCK_DB=true`, FastAPI asettaa OS-tason ympäristömuuttujan `FIREBASE_AUTH_EMULATOR_HOST="127.0.0.1:9099"`. Pythonin `firebase_admin` reitittää kaikki `verify_id_token` ja `set_custom_user_claims` -kutsut lokaaliin emulaattoriin.
- **Frontend (Flutter)**: Sovelluksen käynnistyessä tarkistetaan ympäristö. Jos ajetaan debug-tilassa ja mock on päällä, suoritetaan `await FirebaseAuth.instance.useAuthEmulator('localhost', 9099);`.
- **Lopputulos**: Järjestelmä toimii millisekunnilleen samalla logiikalla koodatessa lokaalisti ja globaalissa pilvessä. Käyttäjätunnukset elävät emulaattorissa, mutta luvitukset tallentuvat litteään `db_v2.json` (TinyDB) -tiedostoon.

## **🚀 2. Firebasen 2026 B2B-Kärkiominaisuudet (OOTB)**
- **A. Salasanaton B2B Onboarding (Passkeys & Magic Links):** Passkey (biometriikka) on ensisijainen. Kutsut (InvitationDTO) luodaan backendissä `auth.generate_sign_in_with_email_link()` -metodilla, mistä GoRouter nappaa syvälinkin (/invite/inv_8x7y6z) ja kirjaa sisään ilman salasanaa.
- **B. Enterprise SSO (SAML & OIDC):** Firebase Identity Platform hoitaa SAML/OIDC-tulkkauksen (Entra ID / Okta). Backend on SSO-agnostikko ja saa aina saman standardin Firebase JWT -tokenin.
- **C. The Invite Guard (Blocking Functions):** Firebasen `beforeCreate` -webhook pysäyttää tilinluonnin ja ampuu pyynnön (POST /api/internal/auth/before-create) FastAPI-backendille. Jos kutsuttua sähköpostia ei löydy kannasta, järjestelmä palauttaa synkronisesti 403 Forbidden.
- **D. Pakotettu Step-Up MFA:** Reititin lukee JWT-tokenista `amr` (Authentication Methods References) -taulukon. Jos reititin vaatii MFA:n mutta leima puuttuu, syntyy Fail-Fast `AppException(ErrorCodes.MFA_REQUIRED)`. Riverpod nappaa virheen, aukaisee Firebasen natiivin MFA-haasteen, virkistää tokenin ja jatkaa.

## ---


## **🛡️ 3. Firebase Auth 2026 Parhaat Käytännöt (Standardit)**
Vuoden 2026 arkkitehtuurissa perinteinen salasanakirjautuminen on toissijainen varajärjestelmä (Passkey-First). Turvallisuusmekanismit nojaavat vahvasti kryptografisiin JWT-leimoihin ja proaktiiviseen istunnonhallintaan.

**A. Salasanan vaihto ja "Re-Authentication Guard" (Zero-Trust):**
Salasanan tai Passkeyn lisääminen/muuttaminen vaatii aina tuoreen session. FastAPI-backend hylkää kriittiset mutaatiot deterministisesti, jos tokenin auth_time on yli 5 minuuttia vanha.
Fail-Fast & UI: Jos istunto on vanhentunut, API nostaa välittömästi AppException(ErrorCodes.REAUTH_REQUIRED). Frontendin Riverpod-interceptor nappaa tämän, avaa lokaalin uudelleentunnistautumisen (esim. sormenjälki/Windows Hello) nollaviiveellä (Zero-Latency Illusion) ja toistaa alkuperäisen API-kutsun taustalla.
Salasanan vaihdon jälkeen Service-kerros kutsuu välittömästi firebase_admin.auth.revoke_refresh_tokens(uid), joka tappaa luvattomat istunnot muilla laitteilla.

**B. Monivaiheinen tunnistautuminen (MFA & Step-Up Guard):**
SMS-pohjainen MFA on turvallisuusriskinä hylätty (Deprecated). Järjestelmä sallii ainoastaan TOTP (Authenticator) ja FIDO2 (YubiKey/Passkey) -menetelmät.
Toteutus: MFA-oikeuksia ei tarkisteta tietokannan lipuista, vaan JWT-tokenin amr (Authentication Methods References) -leimasta lennosta O(1)-nopeudella. FastAPI-reitittimissä kriittiset toiminnot suojataan injektiolla: RequireMFA(). Puuttuva leima ampuu Fail-Fast 403:n, johon UI reagoi näyttämällä Firebasen natiivin MFA-haasteen (Actionable Hint).

**C. Turvallinen tilin poistaminen (Right to be Forgotten & Saga Pattern):**
Asiakasohjelmasta (Flutter) ei koskaan kutsuta suoraan user.delete(), koska se rikkoo Event Sourcing -lokien (TraceEvent) eheyden ja jättää kantaan orpoa dataa (Banned Pattern).
Toteutus: Asiakas kutsuu DELETE /api/v1/users/me. API palauttaa 202 Accepted ja delegoi työn Arq Redis -taustajonoon. Worker pyyhkii PII-datan (anonymisointi), tuhoaa MembershipDTO -kytkökset, peruu tokenit ja kutsuu auth.delete_user(uid). Järjestelmään jää vain anonyymi Opaque ID (usr_abc123) aiempien työnkulkujen eheyden säilyttämiseksi.

## **⚙️ 4. Käyttäjän Asetusnäkymä ja API (Pro-Tool 2026)**
Asetusnäkymä suunnitellaan IDE-työkalun tavoin Desktop-First -periaatteella. Se ei vie käyttäjää pois aktiivisesta työtilasta, vaan hyödyntää Inspector-paneeleita.

**A. Frontend UI (Flutter 3.27+ & Riverpod 3.0):**
Asettelu: Toteutetaan TwoPane (Split-Screen) -rakenteena. Vasemmalla on navigaatio (Yleiset, Turvallisuus, Ilmoitukset), oikealla dynaaminen lomake tiukalla FocusTraversalGroup -näppäimistönavigaatiolla (Sääntö 5.9).
Tila (Optimistic Updates): userPreferencesProvider käyttää SWR-välimuistia (Stale-While-Revalidate). Kun käyttäjä vaihtaa teeman (Tumma/Vaalea) tai kielen, tila muuttuu paikallisesti 0 millisekunnissa. Koko ruudun lataus-spinnerit ovat kiellettyjä. Riverpod Mutation lähettää pyynnön serverille taustalla.

**B. Backend API (Strict Pydantic V2 & Anemic Router):**
Mallit noudattavat Anti-Hallucination sääntöä (extra="forbid") eikä implisiittisiä arvoja sallita.

```python
# models/dtos/user_dto.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

class UserPreferencesDTO(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    
    theme: Literal["LIGHT", "DARK", "SYSTEM"]
    locale: Literal["fi", "en", "sv"]
    # Ei arvailuja: Puuttuva aikavyöhyke on eksplisiittisesti None
    timezone: str | None = Field(default=None, pattern=r"^[A-Za-z_]+/[A-Za-z_]+$")

# api/routers/users.py (MANDAATTI 3.1: Aneeminen reititin)
@router.patch("/me/preferences")
async def update_preferences(
    payload: UserPreferencesDTO,
    current_user: Annotated[TokenDataDTO, Depends(RequireValidToken())],
    user_service: Annotated[UserService, Depends()]
) -> UserPreferencesDTO:
    return await user_service.update_preferences(current_user.id, payload)
```

## **🌐 5. Nykyaikaiset puuttuvat käyttäjäasetukset (SaaS B2B)**
Enterprise-tason B2B-alustalta odotetaan seuraavia vakio-ominaisuuksia:

**Aktiivisten istuntojen hallinta (Device Fingerprinting):**
Näkymä: Lista käyttäjän laitteista (esim. "Windows 11, Edge - Tampere - Aktiivinen nyt"). IP ja User-Agent tallennetaan middlewaren toimesta.
Toiminto: "Kirjaudu ulos muilta laitteilta" kutsuu APIa, joka ajaa revoke_refresh_tokens(uid) ja asettaa Custom Claimseihin force-logout -aikaleiman.

**Tekoälyn Opt-Out ja Tietosuoja (AI Consent Management):**
Ominaisuus: Kytkin: "Älä käytä yritykseni DAG-työnkulkudataa Quorumin sisäisten LLM-mallien koulutukseen." Jos kytkin on päällä, backend pakottaa ehdottomat zero-data-retention -liput kaikkiin OpenAI/Anthropic-kutsuihin lennosta.

**Granulaarinen Ilmoitusmatriisi (Omni-Channel):**
Ei yksinkertaista On/Off-kytkintä. Asetukset ovat Ristiintaulukko (Matriisi): Tapahtumat (Ajo epäonnistui, Uusi jäsen, Maininta) vs. Kanavat (Sähköposti, Selain-Push, Slack-Webhook).

**GDPR Datan Vienti (Data Takeout):**
Käyttäjä voi ladata koko arkistonsa. Raskaita purkuoperaatioita ei koskaan tehdä synkronisesti FastAPI-reitittimessä. Pyyntö siirretään Arq-taustajonoon, API palauttaa 202 Accepted ja käyttäjä saa myöhemmin sähköpostiinsa aikarajatun, suojatun latauslinkin.

**API-avainten hallinta (Personal Access Tokens - PAT):**
Opaque ID -pohjaisten tunnisteiden (pat_[a-zA-Z0-9]{32}) generointi ulkoisille skripteille. Vaatii aina Step-Up MFA:n luontihetkellä ja avain näytetään UI:ssa vain kerran.

## **✉️ 6. Kutsumekanismi: Yksittäiset ja Massakutsut (Excel/CSV)**
Mekanismin on noudatettava täysin Opaque ID -, Dart Isolate - ja Python TaskGroup -mandaatteja varmistaakseen O(1) nopeuden myös 5000 rivin Excel-tiedostoilla.

**A. Yksittäiskutsut & Zero-Trust Tilinluonti:**
The Invite Guard: Orgaaninen (avoin) rekisteröityminen on B2B-palvelussa estetty. Kun uusi käyttäjä yrittää luoda tilin Magic Linkistä, Firebasen beforeCreate -webhook iskee FastAPI-reittiin (POST /api/internal/auth/before-create). Jos sähköpostille ei löydy kannasta valmiiksi generoitu InvitationDTO:ta (esim. ID inv_xyz123), API ampuu 403 Forbidden ja tilinluonti kuolee välittömästi.
Pääkäyttäjä luo kutsun API:n kautta. Backend (Service Layer) käyttää auth.generate_sign_in_with_email_link() -metodia luodakseen syvälinkin (/invite/inv_xyz123), jonka GoRouter poimii tyyppiturvallisesti sisään.

**B. Massatuonti (Bulk Excel/CSV):**
Frontend (The Isolate Mandate): Pro-käyttäjä raahaa massiivisen CSV:n Infinite Canvas -alueelle. Pääsäiettä (UI Thread) ei saa koskaan blokata datan parsimisella, jotta näyttö ei jäädy. Flutter siirtää purkamisen välittömästi uuteen säikeeseen: final payload = await Isolate.run(() => parseAndValidateCsv(bytes));. Validoitu JSON-lista lähetetään API:lle.
Backend (Arq Worker & TaskGroup Mandate): Reititin ei jää odottamaan kutsujen prosessointia, vaan palauttaa heti 202 Accepted ja delegoi työn Redis/Arq-jonoon.
Työn suoritus: Arq-worker ottaa vastaan pyynnön ja ampuu satoja kutsuja Firebaseen rinnakkain hyödyntämällä Python 3.11+ asyncio.TaskGroup() -rakennetta. Tämä varmistaa nopeuden ja estää orpojen zombisäikeiden (Memory Leak) synnyn, vaikka yksi yksittäinen sähköposti kaataisi kutsuprosessin (virheet napataan ExceptionGroup -oliolla).

## **👥 7. SaaS Käyttäjäroolit ja Käyttöoikeudet (2026 OOTB)**
Valtuutus (Authorization) hoidetaan täysin litteästi Firebasen Custom Claimseilla, jotka injektoidaan tokeniin Service-kerroksessa. Aneemiset reitittimet tarkistavat luvituksen O(1) nopeudella suoraan Pydantic DTO:sta ilman tietokantahakuja.

**Roolimäärittelyt (Strict Enums):**
```python
type StripeOrgId = str
class SystemRole(str, Enum): ROOT = "ROOT"; NONE = "NONE"
class TenantRole(str, Enum): ADMIN = "ADMIN"; MANAGER = "MANAGER"; MEMBER = "MEMBER"; VIEWER = "VIEWER"
```

**Roolikohtainen Matriisi ja UI-Reagointi:**

| Rooli | Custom Claims (Leima) | Valtuudet ja Rajoitteet (API Guard) | Frontend UI-Degradointi |
| --- | --- | --- | --- |
| **ROOT** | `{"system_role": "ROOT"}` | Globaali Jumal-tila: Ohittaa asiakasrajat täysin (if token.system_role == "ROOT": return True). Voi luoda uusia B2B-asiakkaita (Tenants), asettaa globaaleja mallipohjia ja nähdä järjestelmätason Audit-lokit vianmääritystä varten. Asetetaan vain Seed-skriptillä (run_seed.py), ei koskaan UI:sta. | Näkee "System Admin" -päänavigaation. Suojattu Tenant-tason 403-virheiltä. |
| **ADMIN** | `{"org_xyz": "ADMIN"}` | Organisaation Omistaja: Täysi valta tenantin sisällä. Hallinnoi Stripe-laskutusta, voi asettaa organisaatiotason Enterprise SSO:n (Entra ID / SAML) ja hallita globaaleja tietosuoja-asetuksia. Alisteinen Last Admin Guardille (Ei voi poistaa/alentaa itseään, jos on ainoa). | Pääsy Inspectorin "Laskutus", "SSO" ja "Käyttäjähallinta" -välilehtiin. |
| **MANAGER** | `{"org_xyz": "MANAGER"}` | Työnkulkuesimies (Power User): Kognitiivisten DAG-työnkulkujen arkkitehti. Voi suunnitella, muokata ja tuhoaa työnkulkuja Infinite Canvasilla. Oikeus kutsua asiantuntijoita (MEMBER, VIEWER). Ei pääsyä: Laskutukseen tai API-avainten (PAT) generointiin. | Laskutus ja SSO -välilehdet piilotettu. Kutsumodaalissa 'ADMIN' -roolin valinta on estetty. |
| **MEMBER** | `{"org_xyz": "MEMBER"}` | Operatiivinen Asiantuntija: Järjestelmän aktiivinen "työhevonen". Voi suorittaa workflow-ajoja (Executions), täyttää asetuslomakkeita ja tuottaa analyyseja. Voi muokata vain omia luomuksiaan ja lukea tiimin yhteisiä tuloksia litteän tietokantamallin puitteissa. | Operoi työtilassa vapaasti. Navigaatiossa ei ole "Jäsenet" -hallintanäkymää. |
| **VIEWER** | `{"org_xyz": "VIEWER"}` | Sidosryhmä / Audit (Vain-luku): Näkee kojelaudat ja Event Sourcing -tulokset (TraceEvent). Strict Read-Only. API:n injektio RequireTenantRole hylkää POST/PATCH/DELETE -pyynnöt automaattisesti 0ms viiveellä. | Arkkitehtuurin sääntö: Graceful Degradation. Riverpod purkaa tokenin lokaalisti, ja piilottaa "Tallenna" / "Kutsu" / "Suorita" -painikkeet ohjelmallisesti SizedBox.shrink() avulla ilman UI-nykimistä. |

---

## **🔐 8. Bring Your Own Key (BYOK) ja Resurssien Eristys**
Enterprise B2B SaaS -alustoissa on kriittistä sallia asiakkaiden tuoda omat tekoälyavaimensa (OpenAI / Vertex AI) suurten API-kustannusten kiertämiseksi ja LLM-rajapintojen "Rate Limitien" osioimiseksi per Tenant. Ohjelmisto tukee aseta-kerran -tyylistä BYOK-mallia, joka nojautuu Pydantic-turvallisuuteen.

**A. Tietokanta (The Secrets Vault):**
Avaimia ei saa koskaan tallentaa pääasialliseen `OrganizationDTO` -malliin, jotta `GET /orgs` -reititin ei vuoda avaimia VIEWER-jäsenille.
* Pydantic V2 Domainiin luodaan erillinen `OrganizationSecretsDTO` -holvi, jonka FK asettuu 1:1 `org_xyz123` -Tunnisteeseen.
* Kentät, kuten `custom_llm_key`, määritellään tyypillä `pydantic.SecretStr`. Tämä nollatoleranssi estää avaimien vahingollisen vuotamisen lokaalin terminaalin uumeniin (`print`) tai Python-lokituksiin (`logger.info`).

**B. FastAPI Reitittimet & Aneeminen Guard:**
Vain organisaation `ADMIN` tai globaali `ROOT` voi käsitellä BYOK-asetuksia.
* `GET /api/v1/orgs/{org_id}/secrets/status`: Ei palauta arvoa, vaan tila-indikaattorin (esim. `{"has_openai": true}`).
* `PUT /api/v1/orgs/{org_id}/secrets`: Kirjoittaa/korvaa olemassa olevan avaimen. Opaque ID Takaa, ettei Mutaatio karkaa väärille riveille.

**C. Desktop-First Tuonti (UI-Rooli):**
* Organisaation "Kiintiö & Avaimet" -Inspector-asetusvälilehti piilotetaan (Fallback: `SizedBox.shrink()`), mikäli rooli on alempi kuin `ADMIN`. 
* Syötettyä avainta ei pysty näkemään käyttöliittymästä enää sen tallentamisen jälkeen, sen voi ainoastaan ylikirjoittaa uudella (Tämä standardoi Pro-Tool -hallinnan turvatason).
* Päätyönkulussa (Orkestraatio) näkyy visuaalisesti joko "Käytetään Quorum -oletuskiintiötä" tai "Käytetään Yksityistä Kiintiötä", reagoivalla SWR-värityksellä.

**D. Resolvoitumisen Hierarkia (System Organization Equality):**
Järjestelmän juuriorganisaatio ("System") ja asiakkaat toimivat 1:1 samalla litteällä BYOK-mallilla. Kovakoodattuja avaimia ei siis leivota `.env` -tiedostoihin FastAPI-koodin luitavaksi. Sen sijaan koko järjestelmän globaali oletusavain asuu juuri-organisaation (esim. `org_system000001`) salaisessa holvissa.
* **Fall-Fast Zero-Latency Loop:** Kun järjestelmä (Service-kerros) yrittää ratkaista LLM-kutsun "Apple Corp":ille, prosessi noudattaa litteää perimysketjua 0 millisekunnissa:
  1. Onko `org_apple_123` -tenantilla säädetty oma avain tietokannassa? -> Jos kyllä, käytä sitä kutsuun (Custom Quota).
  2. Jos ei, luvu juuren `org_system000001` -tenantin avain ja käytä sitä (Quorum Global Quota).
  3. Jos ROOT-avauskin on mitätön tai puuttuu -> FastAPI noudattaa arkkitehtuurimandaattia ja nostaa: `AppException(ErrorCodes.QUOTA_EXHAUSTED)`. Asiakas kokee asian selkokielisenä Toast Error -viestinä.

---


**📋 VAIHEISTUS JA TYÖTEHTÄVÄT**

## **VAIHE 1: Tietomallit ja Pydantic V2 Validointi (Backend SSOT)**

**Kuvaus:** Rakennetaan tiukasti tyypitetyt Pydantic-mallit, jotka kuvaavat järjestelmän SSOT-tilan (Single Source of Truth). Relaatiot hoidetaan litteänä (Flat Referencing).

> **The Big Bang Protocol:** Kaikki vanhaan IAM/Token-malliin liittyvät legacy-luokat (esim. vanha `TokenData`, vanhat `auth.py` funktiot) on tuhottava säälimättä. Uudet `*DTO`-mallit ylikirjoittavat vanhat suoraan. Hyväksymme sen, että koodikanta (FastAPI-reitittimet) "hajoaa" hetkellisesti pirstaleiksi. Tuki vanhalle koodille ja siirtymän fallbackit on ehdottomasti kielletty. Korjaukset tehdään systemaattisesti ajamalla `uv run mypy .` ja korjaamalla rikkinäiset reitititmet ankarasti yksi kerrallaan uuteen DTO-standardiin, kunnes koko linter on puhdas nollalla virheellä.

* **Task 1.1: Opaque ID \-tyypit ja Enumit (PEP 695\) (models/auth.py)**  
  * Määritä tyyppialiakset: type StripeUserId \= str ja type StripeOrgId \= str.  
  * Määritä vahvat Enumit rooleille: SystemRole (ROOT, NONE) ja TenantRole (ADMIN, MANAGER, MEMBER, VIEWER).  
* **Task 1.2: Strict Pydantic Domain \-mallit**  
  * **OrganizationDTO:** id: StripeOrgId, slug: str (Ihmisluettava URL), name: str, tier: str, is\_active: bool, created\_at: datetime (UTC ISO 8601).  
  * **UserDTO:** id: StripeUserId (Vastaa Firebase UID:ta), email: str, display\_name: str, created\_at: datetime.  
  * **MembershipDTO:** user\_id: StripeUserId, org\_id: StripeOrgId, role: TenantRole.  
* **Task 1.3: Token Payload DTO (models/dtos/auth\_dto.py)**  
  * Luo TokenDataDTO, johon Firebasesta saapuva JWT purkautuu: custom\_claims: dict\[StripeOrgId, TenantRole\] ja system\_role: SystemRole | None.
* **Task 1.6: Emulator-Aware Admin SDK (backend_v2/core/firebase_setup.py)**
  * Alusta firebase_admin siten, että se lukee `FIREBASE_AUTH_EMULATOR_HOST` -ympäristömuuttujan ja käyttää sitä saumattomasti, kun `USE_MOCK_DB=true`.
* **Task 1.7: MFA Claim DTO (models/dtos/auth_dto.py)**
  * Laajenna `TokenDataDTO` lukemaan tokenista MFA-status: `amr: list[str] = Field(default_factory=list)`. Pydantic parsii lennosta tiedon toisesta vaiheesta.

## **VAIHE 2: Firebase Custom Claims & Service Layer (Backend)**

**Kuvaus:** Luodaan liiketoimintalogiikka, joka pitää tietokannan ja Firebase Authin Custom Claimsit synkronissa.

* **Task 2.1: Jäsenyyksien hallinta (services/iam\_service.py)**  
  * Toteuta assign\_user\_to\_org(user\_id: StripeUserId, org\_id: StripeOrgId, role: TenantRole).  
  * **Saga-logiikka (Event Sourced):**  
    1. Kirjoita uusi/päivitetty MembershipDTO tietokantaan (Unified Workflow Repository).  
    2. Hae käyttäjän nykyiset Custom Claimsit Firebase Admin SDK:lla.  
    3. Päivitä sanakirjaa: claims\[org\_id\] \= role.value.  
    4. Puske päivitetyt leimat takaisin Firebaseen: auth.set\_custom\_user\_claims(user\_id, claims).  
    5. Kirjoita `TraceEvent` (Action: ROLE_ELEVATED, Actor: "kutsujan_id", Target: user_id) erilliseen audit-tauluun samassa transaktiossa vahvistamaan mutaation valmistuminen.
  * *Sääntö:* Kääri asynkroniset tietokanta- ja verkkopyynnöt Python 3.11+ asyncio.TaskGroup() \-kontekstiin turvalliseksi Sagaksi (jos Firebase kaatuu, mutaatio rollbackataan).
* **Task 2.2: Tokenin vahvistus (services/auth\_service.py)**  
  * Toteuta rutiini, joka käyttää Firebase Adminia vahvistamaan Frontendiltä saapuvan tokenin ja palauttaa puhtaan TokenDataDTO:n.
* **Task 2.4: Magic Link Invitation Engine**
  * Toteuta Service-metodi, joka luo Opaque ID:llä varustetun InvitationDTO:n kantaan ja generoi kirjautumislinkin: `auth.generate_sign_in_with_email_link(email, ActionCodeSettings(url="https://app.quorum.fi/invite/inv_123xyz"))`.
* **Task 2.5: FastAPI Blocking Webhook (api/routers/iam_hooks.py)**
  * Toteuta `POST /api/internal/auth/before-create`. Tämä webhook ottaa vastaan Firebasen pyynnön, tarkistaa InvitationDTO:n ja hylkää tilinluonnin nollatoleranssilla (Zero-Trust), jos kutsua ei löydy.

## **VAIHE 3: FastAPI Portinvartijat & Aneemiset Reitittimet**

**Kuvaus:** Varmistetaan The Anti-Mirror Protocolin mukaisesti, että yksikään tietopyyntö ei pääse Service-kerrokseen ilman oikeaa organisaatio-leimaa.

* **Task 3.1: Tenant Isolation Guard (Fail-Fast Dependency)**  
  * Luo FastAPI-injektio: RequireTenantRole(allowed\_roles: list\[TenantRole\]).  
  * **Luvituslogiikka:**  
    1. Tarkistaa löytyykö tokenista {"system\_role": "ROOT"}. Jos kyllä \-\> **Salli pääsy aina** (Superadmin-ohitus asiakasdatan vianmääritykseen).  
    2. Lukee pyydetyn org\_id:n (URL:sta tai Headerista) ja tarkistaa tokenin custom\_claims \-sanakirjasta, onko käyttäjällä riittävä rooli tähän nimenomaiseen Tenantiin.  
    3. Jos oikeutta ei ole, nosta heti AppException(ErrorCodes.FORBIDDEN).  
* **Task 3.2: Reitittimien toteutus (api/routers/iam.py)**  
  * Käytä modernia Annotated syntaksia:  
    Python  
    @router.get("/{org\_id}/members")  
    async def get\_members(  
        org\_id: StripeOrgId,  
        current\_user: Annotated\[TokenDataDTO, Depends(RequireTenantRole(\[TenantRole.ADMIN, TenantRole.MANAGER\]))\],  
        iam\_service: Annotated\[IAMService, Depends()\]  
    ) \-\> list\[MembershipDTO\]:  
        return await iam\_service.get\_org\_members(org\_id)
* **Task 3.4: Step-Up MFA Guard (api/dependencies.py)**
  * Luo `RequireMFA()` -injektio. Guard tarkistaa: `if "mfa" not in current_user.amr: raise AppException(ErrorCodes.MFA_REQUIRED)`.

## **VAIHE 4: Flutter Client & The Pro-Tool Experience**

**Kuvaus:** Rakennetaan Desktop-First IDE-kokemus Riverpod 3.0:lla noudattaen nollaviiveen illuusiota (Zero-Latency Illusion).

* **Task 4.1: JWT Lokaali purku & Riverpod Tila**  
  * Kuuntele FirebaseAuth.instance.authStateChanges().  
  * Kun JWT vastaanotetaan, purkaa sen Base64-payload *lokaalisti* Dartissa. Näin UI (Riverpod-tila) tietää välittömästi, mihin organisaatioihin ja rooleihin käyttäjällä on oikeus, ilman erillistä ja hidasta /me API-pyyntöä.  
* **Task 4.2: Opaque ID & GoRouter Hybrid URL**  
  * Reititys on 100% tyyppiturvallista (esim. OrganizationRouteData).  
  * URL-malli: /orgs/org\_123xyz/demo-corp/dashboard. Reititin käyttää hakuun **vain** Opaque ID:tä (org\_123xyz). Slug (demo-corp) on SEO/ihmisluettavuus-kosmetiikkaa, joka estää linkkien hajoamisen (Link Rot).  
* **Task 4.3: Riverpod Mutaatiot & Tokenin Virkistys**  
  * Jos käyttäjä lisätään uuteen organisaatioon (Mutaatio), Frontendin on **pakotettava** tokenin päivitys (await user.getIdToken(true)), jotta uusi Custom Claim aktivoituu käyttöliittymässä ilman uloskirjautumista.  
* **Task 4.4: Actionable Hints (Graceful Degradation)**  
  * Käytä lokaalia JWT-tilaa piilottamaan käyttöliittymäelementit (esim. "Kutsu jäsen" \-nappi piilotetaan SizedBox.shrink() avulla, jos rooli on VIEWER). Jos Backend ampuu 403-virheen, näytä tyylikäs Actionable Hint \-Toast alakulmassa.
* **Task 4.7: Emulator Auto-Connect & Passkey First**
  * Määritä `main.dart` yhdistämään `FirebaseAuth.instance.useAuthEmulator` lokaalissa debug-tilassa. Käytä `firebase_ui_auth` -paketin modernia käyttöliittymää, jossa Passkey ja Enterprise SSO ovat priorisoituna ja sähköposti jää "Magic Link" -fallbackiksi.
* **Task 4.8: MFA Interceptor (Riverpod)**
  * Jos API-verkkovirhe palauttaa `MFA_REQUIRED`, Riverpod-interceptor näyttää Actionable Hintin, avaa lokaalin Firebase MFA -haasteikkunan, virkistää tokenin, ja yrittää API-kutsua automaattisesti uudelleen.

## **VAIHE 5: The "Root" Bootstrap (Seed Protocol)**

**Kuvaus:** Tietokantaa ei saa käsin muokata lennosta (ID:t korruptoituvat). Luomme Seed-skriptin ensimmäisen Root-käyttäjän (sinun) luomiseksi.

* **Task 5.0: Tier 3 Database Reset (The IAM Clean Slate)**
  * **Mandaatti:** Ennen IAM-koodauksen tai testaamisen aloittamista koko vanha varsinainen tietokanta `db_v2.json` (tai testikannan tila) pyyhitään `tier3-database-reset` -työnkululla **täysin tyhjäksi, mukaan lukien vanhat ajohistoriat**. Tämä on turvallista, sillä itse siementiedosto (`backend_v2/seed/seed_data.json`) on suojattu ja säästetään täysimääräisenä. Kun siemennysskripti ajetaan uudelleen, se palauttaa kaikki kognitiiviset matriisit ja työnkulut puhtaalle pöydälle.
* **Task 5.1: Seed Data JSON & System Root -säilytys**  
  * Tiedostoa `seed_data.json` saa (ja pitää) muokata, jotta se vastaa uusia tiukkoja Pydantic DTO -rakenteita (esim. poistetaan tuettomuudet tai validointivirheet). Ainoa ehdoton sääntö on, että valmiiksi määritelty siemenorganisaatio `"id": "org_system000000"` ja `"display_name": "System Root"` säilytetään tismalleen näillä arvoilla. Muutoin tiedosto on täysin päivitettävissä.
* **Task 5.2: Siemennysskripti (run_seed.py local)**  
  * Skripti luo organisaation kantaan.
  * Skripti etsii antamasi sähköpostiosoitteen perusteella Firebase UID:si, luo MembershipDTO:n kantaan, ja käyttää Firebase Admin SDK:ta ampumaan profiiliisi leiman: `{"system_role": "ROOT"}`.
  * Tämän jälkeen kirjaudut sisään ja järjestelmä aukeaa sinulle "Jumal-tilassa", josta voit käyttöliittymän kautta luoda ensimmäiset B2B-asiakkaat.

## ---

**✅ Laatuportit (Definition of Done)**

1. **Opaque Strictness:** Yksikään API-päätepiste ei ota vastaan ihmisluettavia avaimia. Kaikki ID:t ovat Pydantic-validoituja (org\_..., usr\_...).  
2. **Zero-Trust Security:** API hylkää pyynnön deterministisesti 0 millisekunnissa DI-kerroksessa (403 Forbidden), jos tokenin Custom Claimsista ei löydy kyseistä org\_id:tä vaaditulla roolilla (tai ROOT-oikeutta).  
3. **ORM Leakage Estetty:** Yksikään reititin (router.py) ei ota suoraa yhteyttä db-luokkaan tai Firebase Adminiin.  
4. **Mypy & Ruff:** Backendin Strict Typing \-linterit (uv run ruff check . ja uv run mypy .) menevät läpi nollalla virheellä. @override dekoraattoreita on käytetty.  
5. **UI Zero-Latency:** Flutter ei näytä koko ruudun Loading-spinnereitä tenanttia vaihtaessa, vaan käyttää SWR (Stale-While-Revalidate) lokaalia JWT-välimuistia.
