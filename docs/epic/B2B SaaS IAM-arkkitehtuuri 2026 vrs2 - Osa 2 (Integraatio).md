# **🚀 EPIC: B2B SaaS IAM-arkkitehtuuri 2026 - Osa 2 (Integraatio)**

**Epic ID:** EPIC-IAM-003b

**Tila:** Draft / Pending Infrastructure

**Prioriteetti:** P0 (Kriittinen Core-infrastruktuuri / SOC2 Compliance)

**Riippuvuudet:** Epic 72 (PostgreSQL Driver) ja Epic 74 (GCP & Redis) on oltava valmiina ja verifioituina.

**Arkkitehtuuri:** Python 3.14+ (FastAPI), PostgreSQL (RLS), Memorystore (Redis), Firebase Auth Webhook (Soft Delete)

---

## **🎯 Tavoite**

Tämän toisen vaiheen tavoitteena on integroida IAM-järjestelmä valmiiseen PostgreSQL-tietokantakerrokseen ja GCP:n tuotantoinfrastruktuuriin. Tämä sisältää:
1. **Tietokantatason row-level security (RLS)** loogiseen asiakaseristykseen (SOC2).
2. **PostgreSQL-taulujen ja indeksien käyttöönoton** (`users`, `organizations`, `invitations`).
3. **Reaaliaikaisen hätäsulun** (Redis Blocklist / Kill-Switch).
4. **B2B-kutsuvuon ja törmäykseneston** (Collision Guard) kannassa.
5. **FinOps Rate Limitingin** (Redis-rajat organisaatioittain).
6. **GDPR-webhookin** ja käyttäjän tietojen anonymisoinnin (Soft Delete).
7. **Tuotantotietokannan alustamisen** (Seed Protocol).

---

## **🏛️ 1. Datan Eristys: Row-Level Security (PostgreSQL RLS)**

Inhimillisten koodivirheiden (esim. unohdettujen `.filter(org_id=...)` -ehtojen) estämiseksi otetaan käyttöön PostgreSQL:n natiivi Row-Level Security.

1. Aina kun backend avaa tietokantayhteyden `require_role`-injektion läpäisyn jälkeen, se injektoi kantaan komennon:
   ```sql
   SET LOCAL quorum.current_org = '<token.org>';
   ```
2. Tietokantamoottori itse hylkää luku- ja kirjoitusyritykset, jos pyydetty rivi ei kuulu kyseiselle organisaatiolle (tenant).
3. Tämä takaa loogisen asiakaseristyksen (Logical Tenant Isolation), mikä on SOC2 Type II -auditoinnin ehdoton vaatimus.

---

## **🛡️ 2. Hätäsulku (Redis Blocklist & Kill-Switch)**

Koska lokaali JWT elää 15 minuuttia, tarvitaan nopea keino evätä poistetun tai rooliltaan muuttuneen käyttäjän pääsy ennen tokenin vanhenemista.

* Kun admin poistaa käyttäjän tai lakkauttaa oikeudet, backend kirjoittaa kyseisen käyttäjän UID:n välittömästi **Redis-välimuistin mustalle listalle (Blocklist)**: `revoked:usr:<uid>`.
* FastAPI:n `require_role` -guard lukee tämän asynkronisesti alle 1 millisekunnissa ja hylkää voimassa olevankin JWT:n välittömästi statuksella `401 Unauthorized`.
* Tämä korvaa hitaan tietokantahaun jokaisen API-kutsun alusta.

```python
# Osa 2: require_role integroitu Redikseen
async def _role_checker(
    user: TokenData = Depends(get_current_user_from_header),
    redis: ArqRedis = Depends(get_arq_pool)
) -> TokenData:
    # 1. Kill-Switch (O(1) Redis Blocklist check)
    if await redis.exists(f"revoked:usr:{user.id}"):
        raise AppException(error_code=ErrorCodes.UNAUTHORIZED)
    
    # 2. Roolitarkistus
    ...
```

---

## **🤝 3. B2B Kutsu-flow ja Törmäyksien Hallinta (Invite Collisions)**

Uuden työntekijän kutsu ja organisaatioon liittäminen hoidetaan tiukoilla kannan eheystarkistuksilla:

1. **Kutsu:** Admin luo kutsun sähköpostilla. Backend tallentaa `invitations`-tauluun `org_id`:n, roolin ja generoi `invite_token`:in.
2. **Törmäyksen esto (1:1 Mandaatin pakotus):**
   Jos sähköpostilla tai Firebase UID:lla on jo olemassa litteä `User`-tietue, joka kuuluu toiseen organisaatioon, backend **ei** siirrä käyttäjää lennosta.
   * Se nostaa välittömästi Fail-Fast -virheen: `AppException(ErrorCodes.USER_ALREADY_ASSIGNED)`.
   * Tämä estää datan ristiinvuotamisen organisaatioiden välillä. Käyttäjän on joko poistettava vanha tilinsä tai käytettävä kutsussa toista sähköpostia.

---

## **💸 4. AI FinOps & Rate Limiting (Redis)**

Estetään spämmi ja "Noisy Neighbor" -ilmiö suoraan API-tasolla.

* Jokainen tekoälyä kuluttava reitti on suojattu Redis-pohjaisella Rate Limiter -injektiolla.
* Koska `org_id` on saatavilla heti lokaalista JWT:stä, Redis voi estää liian tiheät kutsut (esim. *Max 100 AI-ajoa minuutissa per org_id*) heti API-rajalla ilman tietokantahakua.
* Ylityksestä palautetaan 0 ms latenssilla `429 Too Many Requests`.

---

## **⚖️ 5. Soft Delete & GDPR "Right to be Forgotten" Webhook**

Kun käyttäjä poistaa tilinsä mobiilisovelluksesta, Firebase poistaa tilin heti. Backendin asynkroninen synkronointi hoitaa loput:

1. Firebase Cloud Function kuuntelee `auth.user.deleted`-tapahtumaa ja kutsuu backendin webhookia: `POST /api/v2/system/webhooks/firebase-delete`.
2. Backend vastaanottaa poistetun UID:n. Kovaa SQL-deleteä **ei** tehdä.
3. Käyttäjän henkilötiedot (sähköposti ja nimi) anonymisoidaan (esim. `email = "deleted_user_X@quorum.local"`) ja asetetaan `deleted_at = NOW()`.
4. Tämä varmistaa, että aiempien AI-ajojen (`executions`), työnkulkujen (`workflows`) ja audit-lokien viiteavaimet säilyvät ehjinä.

---

## **✅ Laatuportit (Definition of Done - Osa 2)**

Jokaisen tämän vaiheen PR:n on läpäistävä seuraavat testit:
* [ ] **Row-Level Security:** Automaattiset testit varmistavat, että kysely ilman `org_id`-suodatusta ei palauta toisen tenantin tietoja, kun session `quorum.current_org` on asetettu.
* [ ] **Redis Kill-Switch Test:** Kun käyttäjä lisätään Redis Blocklistiin, hänen JWT-tokeninsa lakkaa toimimasta välittömästi (0 ms latenssi, 401 Unauthorized).
* [ ] **Collision prevention:** Kutsun lunastus heittää `409 Conflict`, jos sähköposti on jo sidottu toiseen organisaatioon.
* [ ] **Soft Delete Integrity:** Webhook-kutsun jälkeen sähköpostit ja nimet anonymisoidaan, `deleted_at` on asetettu ja viiteavaimet aikaisempiin suorituksiin säilyvät toiminnassa.
