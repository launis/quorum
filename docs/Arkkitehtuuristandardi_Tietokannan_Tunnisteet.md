# Quorum V2 Arkkitehtuuristandardi: Tietokannan Tunnisteet ja Relaatiot (The Stripe Pattern)

Dokumentin tila: **Luonnos (Phase 2 Hardening)**
Päivitetty: maaliskuu 2026

## 1. Johdanto ja Ydinhaaste
Quorum V2 käyttää dokumenttipohjaista NoSQL-tietokantaa (kehityksessä TinyDB `db_v2.json`, tuotannossa Google Cloud Firestore). 
Dokumenttikantojen suurin vahvuus on luonnollinen ihmisluettavuus (hierarkkinen JSON), mutta suurin riski on **relaatiotietojen pirstoutuminen** hajautetussa B2B SaaS -arkkitehtuurissa.

Jos annamme asiakkaiden muuttaa ihmisluettavia arvoja ("slug"), ja olemme linkittäneet dokumentteja toisiinsa näillä nimillä (References), yhden nimen vaihto pakottaa "Cascading Update" -operaation koko tietokantaan. Samalta nimeltä näyttävä asetus voi sekoittua toisen yrityksen asetukseen (ID-törmäys).

Tämä standardi ohjeistaa, miten Quorumissa käytetään tunnisteita asettamaan järkähtämätön tietoturva, samalla säilyttäen `seed_data.json` siemendatan käsinkoodattavan luettavuuden.

---

## 2. Nomenklatuuri: ID vs. Slug vs. Foreign Key

Jokaiseen Pydantic-malliin ja tietokantadokumenttiin sovelletaan ehdotonta standardia:

1. **`id` (Pääavain / Primary Key):** 
   - Muuttumaton ja yksilöivä tunnus.
   - Käytetään 100% varmuudella **kaikkeen tietokannan sisäiseen tietoturva- ja viitesidontaan** (Foreign Keys). 
   - `id`-arvoa ei oletuksena näytetä loppukäyttäjälle käyttöliittymässä (UI), eikä se saa muuttua olion elinkaaren aikana.

2. **`slug` (Reititys & Ihmisluettavuus):** 
   - URL-ystävällinen, uniikki merkkijono (esim. `oma-yritys-oy` tai `toulmin-matrix-v2`). 
   - Slugia käytetään **yksinomaan Front-endin URL-reitityksissä** (esim. `https://quorum.com/org/oma-yritys-oy/studio`) sekä selkolukuisissa API-kutsuissa. 
   - Asiakas "Tenantin" omistaja ***saa vaihtaa*** oman työnkulkunsa tai organisaationsa `slug` -arvoa asetuksista vapaasti (mikä rikkoo heidän vanhat URL-kirjanmerkkinsä). API- ja kannan taustalla olevat suhteet pysyvät kuitenkin ehjinä, koska The Backend nojaa täysin muuttumattomaan `id` ankkuriin.

3. **Foreign Key (Viiteavain):**
1.  **`id` (Pääavain / Primary Key):** 
    -   Muuttumaton ja yksilöivä tunnus.
    -   Käytetään 100% varmuudella **kaikkeen tietokannan sisäiseen tietoturva- ja viitesidontaan** (Foreign Keys). 
    -   `id`-arvoa ei oletuksena näytetä loppukäyttäjälle käyttöliittymässä (UI), eikä se saa muuttua olion elinkaaren aikana.

2.  **`slug` (Reititys & Ihmisluettavuus):** 
    -   URL-ystävällinen, uniikki merkkijono (esim. `oma-yritys-oy` tai `toulmin-matrix-v2`). 
    -   Slugia käytetään **yksinomaan Front-endin URL-reitityksissä** (esim. `https://quorum.com/org/oma-yritys-oy/studio`) sekä selkolukuisissa API-kutsuissa. 
    -   Asiakas "Tenantin" omistaja ***saa vaihtaa*** oman työnkulkunsa tai organisaationsa `slug` -arvoa asetuksista vapaasti (mikä rikkoo heidän vanhat URL-kirjanmerkkinsä). API- ja kannan taustalla olevat suhteet pysyvät kuitenkin ehjinä, koska The Backend nojaa täysin muuttumattomaan `id` ankkuriin.

3.  **Foreign Key (Viiteavain):**
    -   Relaatioviittaukset toisiin objekteihin nimetään poikkeuksetta koko sanalla ja loppuliitteellä `_id`.
    -   Esim. Viittaus organisaatioon on **`organization_id`**. Viittaus työnkulkuun on **`workflow_id`**.
    -   **KIELLETTYÄ:** Sarakkeeseen `organization_id` ei koskaan tallenneta omistajan `slug`-arvoa (kuten "oma-yritys-oy"), vaan aina omistajan lukkolyöty `id` (kuten "org_9a8b7c").

---

## 1. ID vs. Slug (The Stripe Pattern)

### Pydantic Enforcement Standardi (The Opaque Lock)
Lähtökohtaisesti kantaan asetetun ID-tunnisteen tulee noudattaa "Stripe Pattern" -rakennetta, jossa on alussa datatyypin lyhenne (esim. `org_`, `usr_`, `wf_`, `node_`, `blk_`) ja loppuosa on salattu.

Tuotantolaatuinen Opaque ID vaatii kaksi ehtoa (Fail-Fast Validointi):
1.  **Opaque:** Yksikään järjestelmän sisäinen tunniste ei koskaan saa sisältää ihmisluettavaa nimeä tai avainsanaa (esim. `id: sys_analysis` on laiton). 
2.  **Kryptografinen Pituus:** Alfanumeerisen tunnisteosan on oltava aina **vähintään 8 merkkiä** pitkä (esim. UUIDv4 Hexin lyhenne), jotta turvataan globaali "Collision Resistance".

Standardisoitu Pydantic RegEx -sääntö kaikille malleine (esim. `v2_core.py` ja `auth.py`):
`^([a-z]+)_[a-zA-Z0-9]{8,}$`

### Aliaksen ja Opaque ID:n työnjako

Käytämme etuliitteellä (Prefix) varustettuja merkkijonoja.
- Organisaatio = `org_`
- Käyttäjä = `usr_`
- Työnkulku = `wf_`
- Suoritus = `run_`
- Sääntö/Prompti = `blk_`

### 3.1. System Global Resources (Prefix_OpaqueString)
**Opaque Stripe ID:t koskevat absoluuttisesti kaikkia, myös System Seed-dataa.** Kun resurssi on koko järjestelmän laajuinen ja ohjelmiston mukana The Spinen `seed_data.json` tiedostossa toimitettava (esim. `system`-organisaation julkiset matriisit, työnkulkupohjat):
- **ID Muoto:** Käytetään, aivan kuten kaikessa asiakasdatassa, tyyppietuliitettä ja **satunnaisotettua UUID- tai Opaque Base62 -arvoa** (esim. `id: "blk_L9xX2"`, `id: "wf_K8j2P"`). `sys_slug` -poikkeukset on kokonaan kielletty.
- **Relaatiot:** The Spinen sisäisen `seed_data.json` -tiedoston relaatiot (esim. `$results.step_L9xX2m.matrix_B8z1Pq`) abstrahoidaan pitkälti UI-tasolla (Admin Studio, Blueprint Editor), eikä ihmisen odoteta ratkovan Opaque ID -viittauksia raa'asta JSON-tiedostosta. UI hakee näyttönimet valintalistoille `slug` tai aliaksien kautta, kätkien Opaque-matematiikan alleen.

### 3.2. Dynamic Tenant Resources (Prefix_OpaqueString)
Kun asiat käynnistyvät ja Asiakas-Tenant luo dynaamisen resurssin livenä (esim. Uusi AI-suoritus, Käyttäjätilien luonti tai alkuperäisen matriisin kloonaaminen "Kopioi Omaksi"):
- **ID Muoto:** Identtinen järjestelmäresurssien kanssa: tyyppietuliite ja **satunnainen Stripe-arvo**.
- **Esimerkkejä:** `id: "org_9a8b7c"`, `id: "usr_XjM2p9L"`, `id: "run_Kf39vLx"`
- **Hyöty:** Yksi yhtenäinen "Zero Exceptions" Pydantic-validointi koko The Spinen läpi. Satunnaisuus estää täydellisesti id-törmäykset (Collision) ja tarjoaa **Security by Obscurity** -suojan: Käyttäjä ei voi selaimen arvoja arvailemalla murtautua naapuriyrityksen työnkulkuun.

### 3.3. Universal Opaque -mallin Riskit ja Mitigaatio (Risk Analysis)
Dynaamisen datan (Opaque) ja staattisen siemendatan yhdenmukainen Opaque-pakotus luo tiettyjä arkkitehtuuririskejä kehittäjäkokemukselle, jotka The Spine taklaa näin:

1.  **Riski: Luettavuuden Katoaminen (Koodaus JSONissa)**
    -   *Ongelma:* Koska `seed_data.json` käyttää satunnaisia UUID-viitteitä (esim. `{"matrix_id": "blk_L9z"}`), viitteiden lukeminen paljaalla silmällä koodieditorissa on mahdotonta. Kehittäjä voi tehdä kriittisiä virheitä manuaalisessa copy-pastessa puhtaan ihmisluettavuuden (`blk_sys_manager`) puuttuessa.
    -   *Mitigaatio (The De-Generator Mandate):* Kehittäjät eivät ohjelmoi työnkulkuja tai matriiseja käsin JSON-tiedostoon tekstieditorilla. The Spinen "seed" syntyy viemällä data ulos **Admin Studiosta** (UI), jossa järjestelmä hoitaa Opaque-avaimien kytkennät valintalistojen (Dropdowns) ja "Step Aliaksien" (esim. `alias: "step_input_processing"`) kautta. Kone tuottaa JSON-relaatiot erehtymättömästi.

2.  **Riski: UI:n Reitityksen Törmäys (Slug vs ID)**
    -   *Ongelma:* Jos selain yrittää ladata `GET /api/workflow/wf_sys_123`, mistä backend tietää, etsiikö käyttäjä luettavaa sluggia (`slug="wf_sys_123"`) vai oikeaa tietokannan päänavaimen tunnistetta (`id="wf_sys_123"`)? 
    -   *Mitigaatio:* **Tiukasti erotetut API-reitit.** Julkiset haut, jotka nojaavat reititykseen, erotetaan URL:isa (esim. `GET /api/org/by-slug/{slug_name}`). Sisäiset lukuoperaatiot operoivat aina id:llä: `GET /api/org/{id}`. Frontend pakotetaan käyttämään Stripe-patternia ID-hauissa.

3.  **Riski: ID:n Arvaaminen (Insecure Direct Object Reference - IDOR)**
    -   *Ongelma:* Pilvipalvelussa arkkitehtuuri on vaarassa, jos myöntää staattisia/helposti arvattavia ID-tunnisteita.
    -   *Mitigaatio:* Tämä Universal Opaque -arkkitehtuuri on IDOR-hyökkäyksen surma. Kaikki tenant- ja systemdata tallennetaan poikkeuksetta **VAIN** Opaque (satunnainen) Stripellä (`id: usr_XjM2...`). Lisäksi FastAPI tarkistaa JWT-tokenista organisaatiorajat (`organization_id`), joten edes vuotanut UUID ei avaa dataa vieraalle tenantille. Puhdas IDOR on näin estetty.

---

## 4. Hierarkia ja Relaatiot NoSQL-Kannassa (Parent-Child)

Firestore ja TinyDB tukevat sekä lapsiobjektien upottamista (Embedding) että viittaamista (Referencing). Skaalautuvan SaaS-järjestelmän sääntö on selkeä: **Mitä dynaamisempi ja kasvavampi data, sitä tiukemmin se on irrotettava erilliseksi referenssiksi.**

### Kysymys: Organisaatio on "isäntä" käyttäjille (Parent). Miten tallennamme käyttäjätiedot?

**Vastaus: Ehdottomasti erillisenä Document Reference -mallina, EI upotettuna taulukkona.**

#### KIELLETTY VÄÄRÄ MALLI (Embedding - Do NOT do this):
```json
// org_9a8b7c
{
  "id": "org_9a8b7c",
  "name": "Oma Yritys Oy",
  "users": [
    {"user_id": "usr_1", "role": "ADMIN", "email": "pekka@yritys.fi"},
    {"user_id": "usr_2", "role": "MEMBER", "email": "matti@yritys.fi"} // TÄMÄ RÄJÄHTÄÄ KUN yrityksellä on 100 000 työntekijää
  ]
}
```
*Miksi kielletty:* Firestoressa jokaisella dokumentilla on 1 Megatavun maksimikoko. Jos upotamme dynaamisesti kasvavia lapsielementtejä (käyttäjiä, ajosuorituksia, lokeja) Isäntädokumentin sisään, isäntädokumentti saavuttaa maksimikokonsa ja koko asiakkaan järjestelmä kaatuu poikkeukseen (DocumentTooLarge OOM). Lisäksi, jos päivitämme organisaation nimeä, meidän pitäisi ladata kaikki 100k käyttäjää samassa paketissa.

#### HYVÄKSYTTY OIKEA MALLI (Flat Referencing):
Käyttäjät ovat fyysisesti täysin omissa Pydantic/Firestore kokoelmissaan (`users` collection). He "ilmoittavat" kuuliaisuutensa Isännälleen viiteavaimella.

**Organisaatio-kokoelma (Isäntä):**
```json
// db.organizations
{
    "id": "org_9a8b7c",
    "slug": "oma-yritys-oy",
    "display_name": "Oma Yritys Oy",
    "tier": "enterprise"
    // Ei mitään mainintaa alaisista täällä.
}
```

**Käyttäjä-kokoelma (Lapsi):**
```json
// db.users
{
    "id": "usr_XjM2p9L",
    "email": "pekka@yritys.fi",
    "firebase_uid": "abCDEfgHIjk...",
    "organization_id": "org_9a8b7c", // TÄMÄ SITOO KÄYTTÄJÄN OMISTAJAAN
    "role": "ADMIN"
}
```

**Miten haut haetaan API:ssa?**
Kun ohjelmisto haluaa listata yrityksen käyttäjät, se tekee tietokantahaun:
`SELECT * FROM users WHERE organization_id = 'org_9a8b7c'`

Tämä arkkitehtuuri kestää sen, että organisaatiossa on 2 käyttäjää tai 2 miljoonaa käyttäjää. Kumpikaan dokumentti ei ylitä Firestonen 1 Mt rajaa.

### Relaatiosääntö Yhteenvetona:
1.  **Upottaminen (Embedding):** Sallittua **vain** silloin, kun alilista on tiukasti rajallinen, harvoin muuttuva, ja loogisesti erottamaton osa dokumenttia. (Esimerkki: Promptin sisäiset `variables` parametrit).
2.  **Viittaaminen (Referencing):** Pakollista **aina**, kun alilista voi kasvaa äärettömästi (Käyttäjät, Työnkulut, Loki-tapahtumat, Suoritukset eli Executions). Yhdistys tehdään sijoittamalla isännän Stripe-ID lapsen `organization_id` kenttään.

---

## 5. API ja Käyttöliittymä (UI) Arkkitehtuuri

Kun UI koodataan noudattamaan tätä Stripe + Foreign Key logiikkaa:

-   **Listauksissa (List Views):** Käyttöliittymä kutsuu backendia: `GET /api/v2/org/{slug}/users`. 
-   **Backendin Resolving:** FastAPI ottaa vastaan reitityksestä URL:in "oma-yritys-oy". Se tekee nopean tarkistuksen: `Hae organisaatio, jonka slug = oma-yritys-oy`. Se löytää dokumentin, jonka `id` on `org_9a8b7c`. Vasta tämän jälkeen backend siirtyy suorittamaan varsinaisen valtuutuksen (AuthZ) ja tietohaun käyttäen oikeaa `org_9a8b7c` avainta tietoturvasäännöissä.
-   **Käyttöliittymän Tilanhallinta (State Management):** Esimerkiksi Flutterin Riverpod-tilassa kokoelmat tallennetaan Map-rakenteena `Map<String, User>`, jossa avaimena (key) toimii aina `usr_XjM2p9L`. Tämä takaa, että jos UI:ssa yritetään päivittää riviä, Dart-koodi ei vahingossa tee tuplauksia vaan osaa aina kohdista oikeaan objektiin Opaque Id:n avulla.

---

## 4. Migraatiostrategia (Quorum V2): Clean Slate ja Nolla-Taaksepäinyhteensopivuus

Koska tasalaatuinen Multi-Tenant isolaatio (IDOR-suojaus) ja Deep Copy -arkkitehtuuri nojaavat täysin Opaque ID:hen (The Stripe Pattern), **yksikään** legacy-tunniste (esim. `sys_toulmin` tai `wf_sys_fast`) ei voi koskaan jatkaa elämäänsä tuotantotietokannassa.

Järjestelmä suorittaa **Clean Slate** -migraation (Täysi Uudelleensynty). Vanhoja JSON/TinyDB kantoja ei migroida (Data Mutation), vaan alkuperäinen JSON-pohja rakennetaan kokonaan uusiksi, ja se synkataan pilveen (Firestore).

Tavoitteet ja QA (Laadunvarmistus) -testauskriteeristö on nelivaiheinen:

### Vaihe 1: Pydantic-turvamuurin pystytys (The Fail-Fast Lock)
-   **Tavoite:** Estää ohjelmallisesti minkään vanhan, ihmisluettavan tai liian lyhyen ID:n päätyminen järjestelmään asettamalla koodiin `^([a-z]+)_[a-zA-Z0-9]{8,}$` regex-lukko kohteissa `v2_core.py` ja `auth.py`. 
-   **QA Testaus:**
    -   `Testi A:` Yritettäessä tallentaa luotua dataa ID:llä `"test"`, `AppException` tai Pydantic ValidationError (HTTP 422) heitetään väistämättä The Spine tasolla.
    -   `Testi B:` ID:n yritys koodilla `"blk_a1b"` torjutaan (liian lyhyt), estäen liian heikot hajautusalgoritmit.

### Vaihe 2: Seed Datan Opaque-Generointi (The Blueprint Conversion)
-   **Tavoite:** Noudattaa tiukkaa 'Kaikki uusiksi'-periaatetta varmistaen, että vanhan JSON-kannan satojen kytkösten käsin koodaamisessa ei tapahdu yhtäkään typo-virhettä. Joka ikinen `sys_` ID poistetaan ja korvataan vahvalla Stripe UUID:llä säilyttäen täysi relaatiopuun eheys.
-   **Execution Protocol (Ohje koodaavalle AI-Agentille):**
    1.  Tuleva tekoälyagentti **EI SAA** pyytää käyttäjää naputtamaan uusia ID-koodeja käsin, eikä se saa yrittää luoda Opaque-tunnisteita massakorvaamalla (Find/Replace) raakatekstiä, koska silloin relaatiot katkeavat.
    2.  Agentin on laadittava Python-skripti (esim. `scripts/migrate_seed_to_opaque.py`), joka:
        -   Luku: Lataa nykyisen `backend_v2/seed/seed_data.json` -tiedoston muistiin JSON-puuna.
        -   Iteraatio 1 (ID-Generointi): Käy läpi kaikki kokoelmat (`workflows`, `prompt_blocks`, `steps`, `models`, `roles`). Poimii jokaisen vanhan `id`:n (esim. `"sys_toulmin"`), tallentaa sen entiteetin `"slug"` -kenttään varastoon, ja generoi kohteelle lennosta uuden Stripe-standardin mukaisen Opaque ID:n (esim. `"blk_K92H8z1X"`). Skriptin muistissa pidetään kartoitusta `{"sys_toulmin": "blk_K92H8z1X"}`.
        -   Iteraatio 2 (Relaatioiden Korjaus): Skripti käy läpi kaikki `depends_on`, `task_blueprint`, `models` ja `roles` listat kussakin entiteetissä. Kartoituksen (Map) perusteella skripti korvaa vanhat viitteet ("sys_toulmin") lennosta uusiin ("blk_K92H8z1X").
        -   Kirjoitus: Skripti ylikirjoittaa `seed_data.json` -tiedoston.
-   **QA Testaus:**
    -   `Testi A:` Koko tuotantokelpoisen `seed_data.json`-filun Regex-hajoaminen: Vapaatekstihaku `"id": "sys_` palauttaa pyöreät **0** tulosta. Koko koodikannasta on operoitu kovat ID:t pois.
    -   `Testi B:` Kuolleiden viittausten testi; jokainen luotu uusi `node_X12...` linkittää vain ja ainoastaan olemassa olevaan, aidosti päivitettyyn Stripe ID:hen toisessa oliossa (Skriptin map on toiminut täydellisesti).

### Vaihe 3: Reitittimen URL-eristys (The Routing Split)
-   **Tavoite:** Koodata FastAPI reitittämään ulospäin näkyvät ihmisurlit (`/by-slug/oma_nimi`) sekä backendin puhtaat UUID-vedot (`/{opaque_id}`).
-   **QA Testaus:**
    -   `Testi A:` Frontend hakee dataa oikean työnkulun perusteella nätillä URL:illa josta The Spine eristää tenantin ja slugin, kääntää sen lennosta täydelliseksi `wf_189H1...` kyselyksi, ja tekee itse tietokantahaut satunnaisilla UUID:illä.

### Vaihe 4: Tuhoaminen ja Uudelleensynty (The Clean Slate Execution)
-   **Tavoite:** Tuhota vanha testikanta fyysisesti poistamalla `data/db_v2.json` ja suorittamalla `backend_v2/seed/run_seed.py local`. Tuotettu kanta palvelee pelastusveneeltä jolta ponnistamme Firestore-pilveen.
-   **QA Testaus:**
    -   `Testi A:` Python-pään alustus kaatuu silmittömästi ValidationError-sumaan jos VAIHE 1:n lukko löytää VAIHE 2:n ohittaneita vanhoja ID:eitä (Koko The Fail-Fast arkkitehtuuri on rakennettu tämän estämiseksi). Kun testaus ei kaadu, Opaque-injektio on virheetön.
    -   `Testi B:` Flutter käynnistyy HUD:it ovat nättejä alias-suomennoksilla, ilman yhtäkään näkyvää rumuutta, mutta tietokannan kaikki sisuskalut on purettu absoluuttiseen Stripe ID-erotteluun.

---

## 5. Pikaohje: Kuinka Opaque ID:t tehdään ja määritellään

Kertauksena kehittäjille ja tekoälyagenteille, näin Universal Opaque ID (The Stripe Pattern) rakennetaan käytännössä:

**1. Sääntö ja Määritelmä:**
- ID on aina muotoa `prefix_satunnainenHash`, esim. `blk_4f2a89b1c7d` tai `org_9a8b7ceX`.
- Pydantic RegEx-lukko: `^([a-z]+)_[a-zA-Z0-9]{8,}$`
- **Ihmisluettavuus on täysin kielletty.** ID:ssä ei saa olla sanoja (kuten `sys_toulmin`). Kaikki ihmisille näkyvä tieto tallennetaan tietokannan `slug` tai `name/label` -kenttiin.

**2. Kuinka tunnisteet tehdään?**
- **Käyttöliittymä (Admin Studio):** Generoi ID:t automaattisesti taustalla, kun uusia asioita (Workflows, Steps) luodaan. Käyttäjä ei koskaan näe niitä.
- **Koodissa ja Migraatioissa (Python):** Tunniste luodaan satunnaisesti uuid-kirjastolla, ei koskaan manuaalisesti keksimällä. Edellytetty Python-koodausmalli on:
  ```python
  import uuid
  def generate_opaque_id(prefix: str) -> str:
      return f"{prefix}_{uuid.uuid4().hex[:12]}"
  ```

**3. Relaatiot ja Viittaaminen:**
- Jos toinen objekti viittaa työnkulkuun, se käyttää kenttää `workflow_id` ja sen arvona säilytetään puhdasta Opaque ID:tä (esim. `wf_A1b2...`), eikä koskaan slugia. Backend ja Frontend huolehtivat "slugin" reitityksestä ihmisen ja koneen välillä muuttaessa URL-polun Opaque ID:ksi tietokantaa varten.
