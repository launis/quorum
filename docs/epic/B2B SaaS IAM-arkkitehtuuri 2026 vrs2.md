# **🚀 EPIC: IAM, Hybrid-Organisaatiomalli & Enterprise Hardening (SaaS 2026\)**

**Epic ID:** EPIC-IAM-003

**Tila:** Ready for Implementation / Enterprise Hardening

**Prioriteetti:** P0 (Kriittinen Core-infrastruktuuri / SOC2 Compliance)

**Arkkitehtuuri:** Python 3.14+ (FastAPI), Pydantic V2, PostgreSQL (RLS), Firebase Auth (AuthN), Token Exchange (AuthZ), Redis, Flutter 3.27+ (Riverpod 3.0)

## **🎯 Tavoite**

Rakentaa vikasietoinen, SOC2-yhteensopiva ja salamannopea identiteetinhallinta, joka hyödyntää saumattomasti **Firebase Authenticationin** asynkronista helppoutta (Identity Provider) ja Quorum V2:n **tiukkaa B2B-organisaatiomallia (Flat 1:1 Tenant)**.

Tässä mallissa Firebase toimii järjestelmän "ovimiehenä" (AuthN), tuottaen globaalisti yksilöllisen Firebase UID:n, joka toimii suoraan tietokannan litteän User-taulun **pääavaimena (Primary Key)**. Tunnistautumisen jälkeen backend tekee **Session Upgrade (Token Exchange)** \-operaation: Firebasen token vaihdetaan lennosta Quorumin omaan lyhytikäiseen lokaaliin JWT-tokeniin. Tämä lokaali token sisältää vahvan Opaque Organisaatio-ID:n (org\_xxx) ja työntekijän litteän roolin.

Ratkaisu eristää Googlen infrastruktuurin yksinomaan kirjautumisruutuun, takaa 0 ms latenssin API-luvituksessa (AuthZ) ja mahdollistaa massiivisen mittakaavan AI-orkestraation FinOps-hallinnan, hätäsulut sekä ehdottoman tietokantatason eristyksen (RLS).

## 📜 2026 Standardien ja Best Practices Yhteensopivuus

Tämä arkkitehtuuri on suunniteltu vastaamaan suoraan vuoden 2026 kriittisimpiin B2B SaaS -turvallisuusstandardeihin ja alan parhaisiin käytäntöihin:

*   **OWASP API Security Top 10 (BOLA / IDOR):** Opaque Stripe ID -mandaatti (`org_xxx`) on suora vastaus BOLA-haavoittuvuuksiin (Broken Object Level Authorization), estämällä numeraalisen arvaamisen ja pakottamalla vuokralaisten (tenant) välisen kryptografisen eristyksen.
*   **NIST 800-207 (Zero Trust Architecture):** "Never Trust, Always Verify" -periaate toteutuu aneemisilla reitittimillä ja `require_role`-luvitusinjektiolla. Luvitusta ei jätetä reitittimen satunnaisen koodin varaan, vaan se tapahtuu keskitetysti 0 ms viiveellä lokaalista JWT:stä, jota täydentää Rediksen reaaliaikainen hätäsulku (Kill-Switch).
*   **RFC 8693 (OAuth 2.0 Token Exchange):** Firebasen ulkoisen ID Tokenin vaihtaminen (Session Upgrade) lokaaliin, tiukasti rajattuun ja lyhytikäiseen (15 min) Quorum JWT -tokeniin. Tämä minimoi hyökkäyspinta-alan, jos token vuotaa.
*   **SOC2 Type II & Logical Tenant Isolation:** Tietokantatason Row-Level Security (RLS) PostgreSQL:ssä (`SET LOCAL quorum.current_org`) takaa loogisen eristyksen, mikä on SOC2-auditoinneissa B2B SaaS -yritysten ehdoton vaatimus.
*   **GDPR & CCPA (Right to Erasure):** Pehmeä poisto (Soft Delete) anonymisoinnilla varmistaa, että henkilötiedot poistuvat säännösten mukaisesti välittömästi webhookin kautta, mutta rikkomatta Audit-lokien ja AI-ajojen viiteavaimia.

## ---

**🛑 Arkkitehtuurin Ehdottomat Säännöt (2026 Mandates)**

1. **Hybrid Opaque Mandaatti (Identiteettien eristys):**  
   * **Organisaatiot:** Ihmisluettavia (esim. firma-oy) tai juoksevia (Auto-Increment) ID-tunnisteita ei sallita. Kaikki työtilat (Tenants) on pakotettu kryptografiseen Opaque-muotoon: org\_\[a-zA-Z0-9\]{8,}.  
   * **Käyttäjät:** Käyttäjän pääavaimena (id) relaatiokannassa käytetään suoraan Firebasen UID:ta. Pydantic-malleissa tämä validoidaan turvalliseksi aakkosnumeeriseksi merkkijonoksi. Sisäisiä usr\_-mäppäyksiä ei luoda.  
2. **Pydantic Strict Protocol:**  
   Kaikkiin Pydantic-malleihin (mukaan lukien Quorum Local JWT payload) koodataan ehdoton sääntö: model\_config \= ConfigDict(strict=True, extra="forbid"). Tyyppien arvailua (Type Coercion) tai ylimääräisiä kenttiä ei sallita.  
3. **Anemic Routers (Aneemiset Reitittimet):**  
   FastAPI-reitittimet tekevät *vain* Pydantic-validoinnin. Luvitus, roolitarkistukset ja FinOps-rajoitukset delegoidaan tiukasti JWT-injektiolle (Depends(require\_role)). Reitittimet eivät koskaan suorita asynkronisia ORM-kyselyitä luvituksen takia.  
4. **Fail-Fast Error Handling:**  
   Oikeuksien puute, epäkelpo token tai kiintiön (Quota) ylitys nostaa välittömästi deterministisen AppException (esim. ErrorCodes.FORBIDDEN) RFC 7807 \-standardin mukaisesti 0 millisekunnissa.  
5. **Flat 1:1 Identity Mandate:**  
   Käyttäjä on kiinteästi sidottu tasan yhteen organisaatioon. Tietokannan litteä rakenne: User (PK: Firebase UID) $\\rightarrow$ organization\_id (FK: org\_xxx), role. N:M \-liitostauluja ei sallita missään tilanteessa.  
6. **Soft Delete & Audit Integrity:**  
   Kovaa SQL DELETE \-komentoa ei käytetä User tai Organization \-tauluissa liiketoimintadatassa. Poistot hoidetaan aina deleted\_at-aikaleimalla (Soft Delete), jotta Audit-lokien ja aiempien tekoäly-ajojen (Executions) viiteavaimet pysyvät ehjinä.

## ---

**🛡️ 1\. Ovimies, Hovimestari ja Hätäsulku (Token Lifecycle)**

Järjestelmä eristää Firebase-riippuvuuden kokonaan ydinliiketoiminnasta ja pitää API-tietoturvan lokaalissa Python-kontrollissa.

**Vaihe 1: Firebase AuthN & Session Upgrade**

1. Flutter-sovellus (client\_app\_v2) kirjautuu Firebaseen ja palauttaa Googlen ID Tokenin.  
2. Flutter kutsuu Python-backendin /api/v2/iam/auth/exchange \-reittiä.  
3. Python validoi Firebase Tokenin ja etsii litteän User-rivin, jonka PK vastaa saapunutta UID:ta.  
4. Python generoi ja allekirjoittaa (SECRET\_KEY) **Short-Lived Quorum Local JWT** \-tokenin (Elinaika: **15 minuuttia**).  
   JSON  
   {  
     "sub": "aB3x9Q8wE2dF4gH5jK6lM7nO8pQ9", // Firebase UID (PK)  
     "org": "org\_1a2B3c4D5e6F",            // Opaque Org ID (Tenant)  
     "role": "MANAGER",                    // Litteä Enum-rooli  
     "exp": 1716000900                     // 15 minuutin päästä  
   }

5. Riverpod AuthInterceptor kiinnittää tämän lokaalin JWT:n kaikkiin asynkronisiin pyyntöihin.

**Vaihe 2: Silent Refresh & Emergency Kill-Switch**

Koska Quorum JWT elää vain 15 minuuttia, tietoturva on vankka.

* **Silent Refresh:** Flutter hakee taustalla Firebaselta automaattisesti uuden tokenin ja tekee hiljaisen /exchange-kutsun backendille ennen lokaalin tokenin vanhenemista. Käyttäjäkokemus ei katkea.  
* **Kill-Switch (Redis):** Jos ADMIN poistaa käyttäjän tai lakkauttaa oikeudet, backend kirjoittaa kyseisen Firebase UID:n välittömästi **Redis-välimuistin mustalle listalle (Blocklist)**. Luvitusinjektio tarkistaa tämän 1 millisekunnissa ja hylkää voimassa olevankin JWT:n statuksella 401 Unauthorized.

## ---

**👥 2\. Käyttäjäroolit ja Zero-Latency Luvitus (AuthZ)**

Valtuutus perustuu puhtaasti muistissa (RAM) purettavaan litteään UserRole-enumiin.

**Roolimäärittelyt (Strict Enums):**

Python

class UserRole(str, Enum):  
    ROOT \= "ROOT"        \# Platform Admin (Ohittaa Tenant-rajat)  
    ADMIN \= "ADMIN"      \# Organization Admin (Työtilan ja avainten hallinta)  
    MANAGER \= "MANAGER"  \# Workflow Lead (Suunnittelee työnkulkuja)  
    MEMBER \= "MEMBER"    \# Standard User (Ajaa työnkulkuja ja lukee tuloksia)  
    VIEWER \= "VIEWER"    \# Read-Only Stakeholder

**FastAPI Guard Dependency (backend\_v2/core/security.py):**

Tämä on backendin turvamuuri, joka ei salli yhdenkään pyynnön lipsua ohi.

Python

def require\_role(allowed\_roles: list\[UserRole\]):  
    def role\_checker(  
        token: QuorumTokenData \= Depends(get\_quorum\_jwt),  
        x\_org\_id: str \= Header(..., alias="X-Organization-ID"),  
        redis: Redis \= Depends(get\_redis\_client)  
    ):  
        \# 1\. Kill-Switch (O(1) Redis Blocklist check)  
        if redis.exists(f"revoked:usr:{token.sub}"):  
            raise AppException(error\_code=ErrorCodes.UNAUTHORIZED)

        \# 2\. Root ohitus  
        if token.role \== UserRole.ROOT:   
            return token  
              
        \# 3\. Roolitarkistus  
        if token.role not in allowed\_roles:   
            raise AppException(error\_code=ErrorCodes.FORBIDDEN)  
              
        \# 4\. Tenant Isolation (O(1) Memory check)  
        if token.org \!= x\_org\_id:   
            raise AppException(error\_code=ErrorCodes.FORBIDDEN)  
              
        return token  
    return role\_checker

## ---

**🤝 3\. B2B Kutsu-flow ja Törmäyksien Hallinta (Invite Collisions)**

Uuden työntekijän liittäminen B2B-organisaatioon hoidetaan tiukalla kutsumekanismilla (Pending Invite), koska tietokannan PK (Firebase UID) syntyy vasta kun tili luodaan mobiilissa/webissä.

1. **Kutsu:** ADMIN luo kutsun. Backend tallentaa Invitations-tauluun sähköpostin, org\_id:n, roolin ja generoi krypto-satunnaisen invite\_token:in.  
2. **Kirjautuminen:** Työntekijä luo tilin Flutterissa ja saa Firebase UID:n.  
3. **Lunastus:** Flutter kutsuu /api/v2/iam/auth/redeem-invite välittäen Firebase Tokenin ja invite\_token:in.  
4. **Collision Guard (Törmäyksen esto \- 1:1 Mandaatin pakotus):**  
   Jos annetulla sähköpostilla tai Firebase UID:lla on *jo* olemassa litteä User-tietue, joka kuuluu toiseen organisaatioon (esim. hän on aiemmin luonut vahingossa oman ilmaisen testityötilansa), backend **ei** siirrä käyttäjää lennosta.  
   * Se nostaa välittömästi Fail-Fast \-virheen: AppException(ErrorCodes.USER\_ALREADY\_ASSIGNED).  
   * *Miksi:* Tämä estää henkilökohtaisen datan tai aiempien testiajojen luvattoman vuotamisen uuteen organisaatioon. Käyttäjän on joko tuhottava vanha tilinsä täysin tai käytettävä yrityskutsussa toista sähköpostiosoitetta. Tämä pitää 1:1 datamallin eheyden absoluuttisena.  
5. **Yhdistäminen:** Jos törmäystä ei ole, Python luo User-rivin (PK \= Firebase UID, FK \= org\_xxx), mitätöi kutsun ja palauttaa validin Quorum JWT:n.

## ---

**💸 4\. AI FinOps, BYOK ja Naapuruusmelun Esto (Rate Limiting)**

LLM-tekoälykutsut maksavat rahaa ja vaativat massiivisesti laskentatehoa. Järjestelmä suojaa itsensä skriptatulta "Noisy Neighbor" \-spämmiltä suoraan API-tasolla.

1. **Secret Vault:** Tekoälyavaimia ei palauteta DTO-malleissa. Ne tyypitetään Pydanticissa pydantic.SecretStr, joka maskaa ne lokeissa ja virheilmoituksissa automaattisesti (\*\*\*\*\*\*).  
2. **Token-Aware AI Throttling (Redis):** Jokainen tekoälyä kuluttava API-reitti on suojattu Rate Limiter \-injektiolla. Koska org\_xxx on saatavilla heti lokaalista JWT-tokenista (ilman DB-hakua), Redis voi estää spämmin heti API-rajalla:  
   * Esimerkki: *Max 100 AI-ajoa minuutissa per org\_id*.  
   * Ylityksestä palautetaan 0 millisekunnissa 429 Too Many Requests (RFC 7807), eikä raskasta AI-orkestraatiota koskaan käynnistetä.  
3. **Avaimen Resolvointi (Fallback):** LLM-suoritus tarkistaa ensin organisaation omaa BYOK-avainta (Custom Quota). Jos sitä ei löydy, käytetään järjestelmäavainta (org\_system000000). Jos molemmat puuttuvat, nostetaan heti AppException(ErrorCodes.QUOTA\_EXHAUSTED).

## ---

**🏛️ 5\. Datan Eristys: Row-Level Security (Defense-in-Depth)**

Sovellustason suojaukset (API Guards) ovat erinomaisia, mutta järjestelmä vaatii **Defense-in-Depth** \-mekanismit Enterprise-auditointeja varten.

**Tietokantatason Datan Eristys (Row-Level Security \- RLS)**

* Inhimillisten koodivirheiden (esim. ORM Data Leakage) estämiseksi otetaan käyttöön RLS (PostgreSQL).  
* Aina kun backend avaa tietokantayhteyden require\_role-injektion läpäisyn jälkeen, se injektoi kantaan komennon: SET LOCAL quorum.current\_org \= '\<token.org\>'.  
* Tietokantamoottori itse hylkää luku- ja kirjoitusyritykset, jos pyydetty rivi ei kuulu kyseiselle organisaatiolle, vaikka ohjelmoija unohtaisi .filter(org\_id=...) \-ehdon.

## ---

**⚖️ 6\. Tietosuoja ja Synkronointi (GDPR Right to be Forgotten)**

Kun käyttäjä painaa mobiilisovelluksessa Applen/Googlen vaatimaa "Poista tilini" \-painiketta, Firebase tuhoaa tilin välittömästi. Python-backend ei saa jäädä asynkroniseen zombi-tilaan.

1. **Event-Driven Webhook:** Firebase Cloud Function kuuntelee auth.user.deleted \-tapahtumaa. Se kutsuu välittömästi backendin salaista rajapintaa: POST /api/v2/system/webhooks/firebase-delete.  
2. **Pehmeä Poisto (Soft Delete):** Python vastaanottaa poistetun UID:n. Kovaa SQL DELETE \-komentoa **ei suoriteta**. Sen sijaan käyttäjän PII-data (sähköposti ja nimi) anonymisoidaan (esim. email \= "deleted\_user\_X@quorum.local") ja riville asetetaan deleted\_at \= NOW().  
3. **Eheys säilyy:** Tämä takaa, että vanhojen tekoälysuoritusten (Executions), työnkulkujen (Workflows) ja Audit-lokien viiteavaimet (Foreign Keys) osoittavat edelleen validiin (mutta anonymisoituun) käyttäjäriviin, täyttäen GDPR-vaatimukset rikkomatta järjestelmää.

## ---

**⚙️ 7\. The "Root" Bootstrap (Seed Protocol)**

Tietokantaa ei koskaan manipuloida fyysisesti .json-tiedostoa editoimalla.

* **Tier 3 Database Reset:** Kun testikanta tyhjennetään (backend\_v2/seed/run\_seed.py), Seed-skripti generoi automaattisesti litteän juuriorganisaation: "id": "org\_system000000".  
* **Firebase Emulator Hook:** Skripti luo User-rivin tiedetyllä Firebase Local Emulatorin testi-UID:lla.  
* Kun kehittäjä kirjautuu emulaattoriin lokaalissa Flutter-sovelluksessa, /exchange \-reitti mäppää hänet saumattomasti ROOT-rooliin, jolloin kehitystyö on heti valmis alkamaan puhtaalta pöydältä ilman tietokantamanipulaatiota.

## ---

**✅ Laatuportit (Definition of Done)**

Jokaisen arkkitehtuuriin koskevan Pull Requestin (PR) on läpäistävä nämä testit ja katselmoinnit CI/CD-putkessa:

* \[ \] **Dual-Token & Session Upgrade:** Firebase-tokenia käsitellään *vain* IAM-reiteissä (/exchange, /redeem-invite). Kaikki muut rajapinnat vaativat lokaalin, lyhytikäisen Quorum JWT \-tokenin.  
* \[ \] **Hybrid Strictness & Opaque ID:** org\_\[a-zA-Z0-9\]{8,} on pakotettu Pydantic-tasoilla. Käyttäjien PK on Firebasen natiivi UID. Ihmisluettavia tai juoksevia (Auto-Increment) ID:itä ei sallita liiketoimintatauluissa.  
* \[ \] **Pydantic Strictness:** Kaikissa malleissa (mukaan lukien JWT Payload) on ehdoton ConfigDict(strict=True, extra="forbid"). Secret-avaimet ovat tyyppiä SecretStr.  
* \[ \] **Zero-Trust Guard & Kill-Switch:** Yksikkötestit todistavat, että API palauttaa 403 Forbidden / 401 Unauthorized 0 millisekunnissa, jos JWT:n rooli on väärä, työtila (Tenant) ei täsmää, tai UID löytyy Rediksen Blocklistiltä (Revocation).  
* \[ \] **1:1 Flat Integrity & Collisions:** Järjestelmä heittää deterministisen USER\_ALREADY\_ASSIGNED \-poikkeuksen (409 Conflict), jos käyttäjää yritetään kutsua, mutta sähköposti/UID on jo sidottu toiseen organisaatioon. Moniasiakkuuden N:M \-välihuutelutauluja ei sallita.  
* \[ \] **FinOps Rate Limiting:** Rediksen Rate Limiter torjuu liikenteen 429 Too Many Requests \-virheellä per org\_id ennen tekoäly-operaatioiden alkua, estäen Noisy Neighbor \-ilmiön.  
* \[ \] **RLS & Soft Delete Verifioitu:** Testit varmistavat, että poistot päivittävät vain deleted\_at-kentän ja anonymisoivat datan, ja RLS estää cross-tenant vuodot ORM-tasolla.