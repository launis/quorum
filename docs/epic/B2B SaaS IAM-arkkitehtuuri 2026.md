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

**📋 VAIHEISTUS JA TYÖTEHTÄVÄT**

## **VAIHE 1: Tietomallit ja Pydantic V2 Validointi (Backend SSOT)**

**Kuvaus:** Rakennetaan tiukasti tyypitetyt Pydantic-mallit, jotka kuvaavat järjestelmän SSOT-tilan (Single Source of Truth). Relaatiot hoidetaan litteänä (Flat Referencing).

> **Graceful Migration Strategy:** Uudet tiukat mallit nimetään päätteellä `*DTO` (esim. `OrganizationDTO`, `UserDTO`, `TokenDataDTO`), ja ne luodaan olemassa olevien legacy-mallien viereen. Tämä estää välittömän "Big Bang" -rikkoutumisen niissä kymmenissä FastAPI-reitittimissä, jotka vielä nojaavat vanhaan `TokenData`-luokkaan (jossa rooli ja org_id olivat suoraan juuressa). `seed_registry.py` päivitetään välittömästi käyttämään uusia DTO-malleja, ja reitittimet siirretään näihin iteratiivisesti.

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
  * **Logiikka:**  
    1. Kirjoita uusi/päivitetty MembershipDTO tietokantaan (Unified Workflow Repository).  
    2. Hae käyttäjän nykyiset Custom Claimsit Firebase Admin SDK:lla.  
    3. Päivitä sanakirjaa: claims\[org\_id\] \= role.value.  
    4. Puske päivitetyt leimat takaisin Firebaseen: auth.set\_custom\_user\_claims(user\_id, claims).  
  * *Sääntö:* Kääri asynkroniset tietokanta- ja verkkopyynnöt Python 3.11+ asyncio.TaskGroup() \-kontekstiin.  
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

* **Task 5.1: Seed Data JSON (backend_v2/seed/seed_data.json)**  
  * Määritä JSONiin "System Administration" -organisaatio (esim. org_system000001).
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