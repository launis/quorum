# **🚀 EPIC: B2B SaaS IAM-arkkitehtuuri 2026 - Osa 1 (Valmistelu)**

**Epic ID:** EPIC-IAM-003a

**Tila:** Ready for Implementation / Preparation Phase

**Prioriteetti:** P0 (Kriittinen Core-infrastruktuuri)

**Riippuvuudet:** Ei riippuvuuksia (voidaan toteuttaa nykyisen TinyDB-kehitysympäristön päällä)

**Arkkitehtuuri:** Python 3.14+ (FastAPI), Pydantic V2 (strict), Local JWT (AuthZ), Flutter 3.27+ (Riverpod 3.0), Firebase Local Emulator (AuthN)

---

## **🎯 Tavoite**

Tämän ensimmäisen vaiheen tavoitteena on rakentaa valmiiksi kaikki tietokannasta ja infrastruktuurista riippumattomat IAM-palvelut. Tämä sisältää:
1. **Roolimäärittelyt ja tietomallit** (Pydantic DTOs).
2. **Stateless JWT-signaus ja validointi** (Quorum Local JWT).
3. **FastAPI-reitittimien suojaukset** (require_role guardit) ilman DB-hakuja.
4. **Flutter-sovelluksen tunnistautumisvuo** ja Riverpod-interceptorit.
5. **Firebase-paikallisemulaattorin** kytkeminen lokaaliin testaukseen.

Tämä valmisteleva työ mahdollistaa API-tietoturvan ja käyttöliittymäkontrahtien lukitsemisen ennen PostgreSQL- ja tuotantosiirtoja.

---

## **🛡️ 1. Tokenin Elinkaari & Session Upgrade (Stateless)**

Järjestelmä eristää ulkoisen Firebase-riippuvuuden heti API-rajalla ja vaihtaa sen lyhytikäiseen lokaaliin JWT-tokeniin.

**Vaihe 1: Firebase AuthN & Session Upgrade**
1. Flutter-sovellus kirjautuu Firebaseen ja palauttaa Googlen ID Tokenin.
2. Flutter kutsuu backendin `/api/v2/iam/auth/exchange` -reittiä.
3. Python-backend validoi Firebase Tokenin ja etsii/mäppää saapuneen UID:n käyttäjätietueeksi.
4. Python generoi ja allekirjoittaa lokaalin **Short-Lived Quorum Local JWT** -tokenin (elinaika: **15 minuuttia**):
   ```json
   {
     "sub": "aB3x9Q8wE2dF4gH5jK6lM7nO8pQ9", // Firebase UID
     "org": "org_1a2B3c4D5e6F",            // Opaque Org ID
     "role": "MANAGER",                    // Litteä Enum-rooli
     "exp": 1716000900                     // 15 minuutin päästä
   }
   ```
5. Riverpod `AuthInterceptor` kiinnittää tämän lokaalin JWT:n kaikkiin asynkronisiin API-pyyntöihin.

**Vaihe 2: Silent Refresh (Valmistelu)**
* Flutter hakee taustalla Firebaselta automaattisesti uuden ID Tokenin ja tekee hiljaisen `/exchange`-kutsun backendille ennen lokaalin tokenin vanhenemista. Käyttäjän sessio ei katkea.

---

## **👥 2. Käyttäjäroolit ja Zero-Latency Luvitus (AuthZ)**

Valtuutus perustuu puhtaasti muistissa (RAM) purettavaan litteään `UserRole`-enumiin.

**Roolimäärittelyt (Strict Enums):**
```python
class UserRole(str, Enum):
    ROOT = "ROOT"        # Platform Admin (Ohittaa Tenant-rajat)
    ADMIN = "ADMIN"      # Organization Admin (Työtilan ja avainten hallinta)
    MANAGER = "MANAGER"  # Workflow Lead (Suunnittelee työnkulkuja)
    MEMBER = "MEMBER"    # Standard User (Ajaa työnkulkuja ja lukee tuloksia)
    VIEWER = "VIEWER"    # Read-Only Stakeholder
```

---

## **🔒 3. FastAPI Guard Dependency (Stateless-taso)**

FastAPI-reitittimille luodaan roolitarkistus, joka ei tässä vaiheessa tee asynkronisia ORM-hakuja tietokantaan, vaan luottaa allekirjoitetun tokenin sisältöön (Stateless).

```python
# backend_v2/services/auth.py
class AuthService:
    @staticmethod
    def require_role(allowed_roles: list[UserRole] | UserRole) -> Any:
        """Palauttaa dependency-injektion, joka varmistaa riittävän käyttäjäroolin.
        Osa 1: Purkaa lokaalin JWT-tokenin ja tarkistaa roolin ilman tietokantahakuja.
        """
        from backend_v2.api.dependencies import get_current_user_from_header

        if isinstance(allowed_roles, UserRole):
            allowed_roles = [allowed_roles]

        async def _role_checker(
            user: TokenData = Depends(get_current_user_from_header)
        ) -> TokenData:
            # Root ohittaa kaikki rajat
            if user.role == UserRole.ROOT:
                return user

            # Roolitarkistus
            if user.role not in allowed_roles:
                raise PermissionDeniedError(
                    message=f"Insufficient privileges. Required one of: {[r.value for r in allowed_roles]}",
                    details={"required_roles": [r.value for r in allowed_roles], "current_role": user.role.value},
                )
            return user

        return _role_checker
```

---

## **🚀 4. Transitiovaihe (TinyDB-silta)**

Jotta järjestelmä pysyy 100 % toiminnallisena TinyDB:n päällä ennen PostgreSQL-migraatiota, sovelletaan seuraavia välivaiheen ratkaisuja:

1. **Pääavaimet (PK) TinyDB:ssä:** Vaikka TinyDB käyttää sisäisesti `doc_id`-kokonaislukuja, pakotamme Pydantic-malleihin `id`-kentäksi Firebase UID:n (merkkijono). Repositoriokerros suorittaa haut käyttäen kyselyä `Query().id == "UID"`. Tämä tekee PostgreSQL-migraatiosta myöhemmin täysin yhteensopivan.
2. **App-Level Tenant Eristys:** Koska TinyDB ei tue tietokantatason Row-Level Securitya (RLS), tenant-eristys toteutetaan tässä vaiheessa sovelluskerroksessa (kooditasolla). Kaikkiin repositoriokyselyihin lisätään suodatin `.filter(organization_id=org_xxx)`.
3. **Lokaali Redis-välimuisti (Kehitysympäristö):** Käytetään olemassa olevaa lokaalia Docker Redis -konttia tokenien validointiin ja rate-limit-testaukseen jo tässä vaiheessa.

---

## **✅ Laatuportit (Definition of Done - Osa 1)**

Jokaisen tämän vaiheen PR:n on läpäistävä seuraavat testit:
* [ ] **Pydantic Strictness:** `TokenData`-malli perii `V2CoreBase`-luokan (`ConfigDict(strict=True, extra="forbid")`).
* [ ] **Dual-Token exchange:** Kirjautumistokenit prosessoidaan vain `/exchange`-reitissä, kaikki muut API-haut vaativat lyhytikäisen Quorum JWT -tokenin.
* [ ] **Stateless Role Validation:** Yksikkötestit varmistavat, että API palauttaa `403 Forbidden` 0 millisekunnissa väärällä roolilla ilman, että kantaa kysellään.
* [ ] **Flutter Auth Parity:** Riverpod-interceptorit liittävät JWT:n pyyntöihin ja handlaavat silent refreshin Firebase-emulaattoria vasten.
