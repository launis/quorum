# ** EPIC 91: Quote Evidence Architecture & 2-Stage Opaque Schema**

## ** Tavoite**

Poistaa kaikki nykyiset regex-pohjaiset ja merkkijonosplittauksiin (`|||` tai `<<QRM-SRC...>>`) perustuvat purkkaviritykset LLM-koodista, backendin esityskerroksesta (`blueprint.py`) ja Flutterin käyttöliittymästä. Siirtyä puhtaaseen Pydantic-pohjaiseen `QuoteEvidenceDTO`-rakenteeseen, joka takaa 100% deterministisen ja vikasietoisen esitystavan lainauksille ja niiden lähteille ("Quote Evidence Architecture"). Tällä varmistetaan, että lähde-badget ja itse lainaukset näkyvät käyttöliittymässä aina täydellisesti ilman katkeavia lihavointeja.

## ** ARKKITEHTONINEN VIITEKEHYS JA LAATUPERIAATTEET (Hardening-viitekehys)**

Tämän Epicin toteutuksessa noudatetaan Quorum V2:n tiukkaa laadunvarmistuksen ideologiaa:
1. **Zero-Compromise Pydantic-validointi (Sääntö 10):** Kaikki LLM:n tuotokset ja UI-payloadit hydratoidaan ja validoidaan tiukasti Pydantic-malleilla.
2. **Fail-Fast (Sääntö 3):** Ei fallbackeja rikkoutuneelle datalle. Jos lähdettä ei löydy, ajo epäonnistuu turvallisesti sen sijaan, että UI:hin lähetetään roskaa.
3. **Opaque Stripe ID Mandate (Sääntö 25):** Tietokanta toimii SSOT:na, ja tallentaa relaatiot vain aitojen `doc_...` tyyppisten Opaque ID:iden avulla, ei koskaan ajokohtaisilla "Fake ID":illä.

---

## ** VAIHE 1: Aitojen Relaatioiden Rakentaminen Lainauksiin (The 2-Stage Opaque Schema)**

**Vastuualue:** Backend (Models & LLM Generation)  
**Tavoite:** Pakottaa LLM tuottamaan jäsenneltyä JSON-rakennetta puhtaan tekstin sijaan.

* **Task 1.1: Pydantic-mallin luonti**
  * **Tiedostot:** `backend_v2/models/dtos/lightweight_matrix.py` & `backend_v2/models/v2_core.py`
  * Luo uusi Pydantic-malli `QuoteEvidenceDTO`, joka sisältää kentät `source_id: str` ja `quote_text: str`. 
  * Muuta nykyinen `exact_quotes: list[str]` -> `exact_quotes: list[QuoteEvidenceDTO]`.

* **Task 1.2: 2-Stage Translation Pipeline (LLM-rajoitteiden kiertäminen ja Token-optimointi)**
  * **Vaihe 1 - LLM Output (Token-optimoitu Fake ID):** Koska pitkät Opaque ID:t (esim. `doc_7a8b9c`) tai `<<QRM-SRC-INT-INPUTSPRODUCTTEXT>>` kuluttavat tokeneita ja aiheuttavat tekoälylle kirjoitusvirheitä, `AliasRegistry` muutetaan generoimaan erittäin lyhyitä ja selkeitä viitteitä LLM:lle (esim. `DOC-1`, `DOC-2` tai `SRC-PRODUCTTEXT`).
  * Tekoäly ohjeistetaan palauttamaan Pydantic-rakenteena: `[{"source_id": "DOC-1", "quote_text": "Lainaus tähän"}]`.
  * **Vaihe 2 - Tietokantaan tallennus (SSOT):** `scoring.py`:ssä ennen tietokantaan tallennusta backend katsoo `AliasRegistrystä`, mihin aitoon tietokannan Opaque ID:hen `DOC-1` viittaa. Se tallentaa Pydantic-malliin **vain aidon Opaque ID:n**. Näin tietokannasta tulee puhdas SSOT.

---

## ** VAIHE 2: Tulostuksen rakennus ja Frontend Pariteetti (Display Tier)**

**Vastuualue:** Backend (Presentation) & Frontend (Flutter)  
**Tavoite:** Luoda deterministinen putki tietokannasta Flutterin ruudulle.

* **Task 2.1: Backend Display Payload (`blueprint.py`)**
  * Kun `blueprint.py` rakentaa tulosteen Flutterille, se iteraroi `QuoteEvidenceDTO` -objektit, lukee aidon Opaque ID:n (`doc_7a8b9c`) ja kääntää sen suoraan lokaaliksi käyttöliittymätekstiksi (esim. "Tuotetieto").
  * **Siivous:** Poista nykyiset `scoring.py` ja `blueprint.py` -tiedostojen väliaikaiset Regex-purkkaviritykset kokonaan.

* **Task 2.2: Flutter DTO & UI Rendering**
  * Päivitä `client_app_v2/lib/features/execution/models/scorecard_dto.dart` vastaamaan uutta Pydantic-rakennetta (luo esim. `QuoteEvidenceDto`-luokka).
  * Muokkaa `atom_matrix_table_widget.dart` poistamalla merkkijonon splittaamiset (`contains('|||')`). Renderöi lähdebadge (`sourceName`) ja lainausteksti (`quoteText`) suoraan olion kentistä. Tämä poistaa kaikki lihavointivirheet ja haamulähteet.

---

## ** Hyväksymiskriteerit (Definition of Done)**

1. `exact_quotes` on kaikkialla arkkitehtuurissa lista Pydantic-objekteja, ei merkkijonoja.
2. Tietokantaan ei koskaan tallennu `<<QRM...>>` tai `DOC-1` tyyppisiä ajokohtaisia viitteitä, vaan ainoastaan relaatiotason Opaque ID -viitteitä (`doc_...` tai `prf_...`).
3. Flutterissa `atom_matrix_table_widget.dart` ei tee enää minkäänlaista regex-splittausta stringeille, vaan rakentaa UI:n puhtaasti DTO-kentistä.
4. Python-yksikkötestit (`backend_audit_loop.py`) ja Flutterin koodigenerointi (`flutter_audit_loop.py`) menevät läpi puhtain paperein uuden tiukemman skeeman kanssa.
