# Epic 54: Frontend & Backend Opaque ID Hardening (Rule 19 Enforcement)

## 1. Yhteenveto ja Tavoite (Objective)
Tämän Epicin tavoitteena on varmistaa, että Epic 51:ssä määritelty uusi "Sääntö 19: Opaque Stripe ID -Mandaatti" on aukottomasti tuettu ohjelmistotasolla. Tavoitteena on estää ihmiskäyttäjiä (ja rajapintojen kautta tulevia kutsuja) luomasta semanttisia legacy-ID:tä (kuten `tda_ar2_1`). 

Vaikka tietokanta (`seed_data.json`) on nyt puhdistettu, ohjelmiston (Backend V2 ja Client V2) on estettävä virheellisen datan syntyminen "Fail-Fast" -periaatteen mukaisesti.

---

## 2. Toteutuksen Vaiheet (Työnkulku)

### Phase 1: Pydantic V2 -Validointi (Backend)
Pydantic-mallien tehtävänä on toimia järjestelmän viimeisenä puolustuslinjana (Fail-Fast Gatekeeper).
* **Kohdetiedosto:** `c:\src\quorum\backend_v2\models\prompt_block.py` (tai vastaava tiedosto, jossa `TDAAssertion` on määritelty).
* **Toimenpide 1 (Regex):** Lisätään `tda_id` -kenttään säännöllisen lausekkeen validointi: `Field(pattern=r"^tda_[a-f0-9]{16}$")`. Tämä kaataa pyynnön välittömästi, jos sisään yritetään syöttää luettavia lyhenteitä.
* **Toimenpide 2 (Auto-generointi):** Määritetään kentälle oletustehdas (default factory), joka luo uuden satunnaisen heksakoodin, jos kenttä jätetään tyhjäksi: `default_factory=lambda: f"tda_{secrets.token_hex(8)}"`

### Phase 2: Flutter Admin Studio -Käyttöliittymä (Frontend)
Kun ihmiskäyttäjä käyttää Admin Studiota matriisien luontiin, käyttöliittymän on generoita 16-merkkinen heksakoodi automaattisesti taustalla.
* **Kohdetiedosto:** `client_app_v2\lib\features\studio\models\prompt_block.dart` sekä ne Riverpod-providerit/widgetit, joissa "Add Assertion" -toiminnallisuus asuu.
* **Toimenpide:** Päivitetään uuden atomin luontifunktio. Poistetaan mahdollinen käyttöliittymän tekstikenttä (jossa ihminen voisi keksiä ID:n itse) ja korvataan se automaattisella generoijalla.
* **Toteutustapa (Dart):**
  ```dart
  import 'package:uuid/uuid.dart';
  
  String generateOpaqueTdaId() {
    final uuidHex = const Uuid().v4().replaceAll('-', '');
    return 'tda_${uuidHex.substring(0, 16)}';
  }
  ```
  Tämä injektoidaan suoraan uuden `TDAAssertion` -olion luontiin.

### Phase 3: Järjestelmätestaus (E2E Verification)
* Käynnistetään `client_app_v2` ja siirrytään Admin Studioon.
* Luodaan uusi matriisi ja siihen uusi atomi.
* Varmistetaan, että tallennusvaiheessa (POST-pyyntö backendille) payload sisältää oikeaoppisen `tda_[16-hex]` -tunnisteen, ja että backend hyväksyy sen.
* Yritetään simuloida virheellinen POST-pyyntö (esim. `tda_ar1_1`) ja varmistetaan, että Pydantic heittää HTTP 422 Unprocessable Entity -virheen RFC 7807 -standardin mukaisesti.

---

## 3. Definition of Done (DoD)
1. **Backend:** Pydanticin `TDAAssertion` -malli hylkää kaikki ID:t, jotka eivät täsmää `^tda_[a-f0-9]{16}$` Regexiin.
2. **Frontend:** Admin Studion "Add Assertion" -nappi luo uuden `tda_id`:n automaattisesti taustalla. Käyttäjä ei voi syöttää ID:tä itse.
3. **E2E:** Koko ketju käyttöliittymästä tietokantaan tukee yksinomaan Opaque Stripe ID -mandaattia.
