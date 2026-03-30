# Epic 12: Full System Integration Testing & Resilience Audit (Phase 9 Hardening)

***

## 🎯 1. Epicin Tavoite
Tämän Epicin tavoitteena on saattaa "Phase 9 Hardening" -vaihe päätökseen rakentamalla kattava *"Full System Integration Test"* -automaatioverkko. Tämä varmistaa, että järjestelmän Zero-Typo-, Fail-Fast-, ja Opaque ID -arkkitehtuurilupaukset pitävät aukottomasti paikkansa koko elinkaaren läpi: aina selaimen (Flutter Desktop) Riverpod-tilasta ja `Isolate.run`-parsinnasta FastAPI-ydinreitittimien ja Pydantic-mallien `extra="forbid"` tasolle asti. Tällä estetään regressio Phase 9:n tiukkojen sääntöjen ympärillä.

## 🧱 2. Laajuus (Scope)
Testaus kattaa järjestelmän kriittiset hermokeskukset, keskittyen end-to-end (E2E) -tyyppiseen viestinvälitykseen ja virhetilanteiden toipumiseen (Graceful Degradation & RFC 7807 -virheet).

### 2.1 Backend (Python 3.14 + Pydantic V2)
- **Pydantic Domain & Purity Audit:** Validoidaan SSoT (Single Source of Truth) eli `seed_data.json` automaattisesti siten, että jokainen tietue käy läpi tiukan Fail-Fast-säännöksen. Yksikään ylijäämäavain (extra key) ei saa mennä läpi.
- **API & Middleware E2E-Reitit:** Generoidaan oikeita HTTP asynkronisia testipyyntöjä (`httpx.AsyncClient`) rajapintoihin varmistaaksemme, että vääränlainen domain-kuorma heittää välittömästi `AppException`-virheen (400) ennen Business Logic -kerrosta.

### 2.2 Frontend (Flutter 3.x + Freezed + Riverpod 3.0)
- **Isolate.run Domain Parity Testit:** Ladataan massiivisia JSON-kuormia testivirrassa ja pakotetaan ne Dartin taustasäikeeseen (`Isolate.run()`). C-tason muistin tulee havaita tuntemattomat avaimet ja heittää `CheckedFromJsonException`.
- **Controller-Tier & UI Error Boundary Integration:** Simuloidaan Riverpod-kontrollerin tilanvaihtoja ja varmistetaan, että UI (Desktop-tilassa) käyttää `AppErrorBoundary`-snackbareja näyttämään virheet turvallisesti, eikä Main Thread jäädy (Jank). Asynkronisen `Isolate`-virheen tulee valua sivistyneesti koko widget-puun suojamekanismin syliin.

## 🚦 3. Arkkitehtuuriset Mandaatit Testauksessa
1. **SSoT-Pariteetti:** Testien ydin on aina testata kestävyys todellisella master-tason datalla.
2. **Kielletty "Happy Path" -harha:** Vaikka testin pääsy onnistuneesti läpi on tärkeää, integraation kriittinen kypsyys todistetaan *Negative Testing* -suunnittelulla. On pakollista syöttää vääriä slugeja, viallisia tyyppejä ja puutteellista dataa, jotta näemme järjestelmän kaatuvan kauniisti (Fail-Fast), eikä palauttavan tyhjiä ohitusarvoja (`return {}` tms.).
3. **Zero-Deprecation Mandate:** Kaikki testit pitää mennä läpi ilman ainuttakaan `mypy --strict`, `ruff` tai `dart analyze` varoitusta. 

## 🛠️ 4. Hyväksymiskriteerit (Definition of Done)
1. Python-testien peitto todistaa, että SSoT (`seed_data.json`) on rakenteellisesti matemaattisen puhdas Pydantic V2 -malleille.
2. Backend API-testit tarkistavat `AppException`-välityksen aina rajapintaan asti estäen legacy 500-internal virhevuodot.
3. Flutter-testit validoivat monimutkaisen Freezed-deserialisoinnin Isolaten sisällä.
4. Riverpod-integraatiotesti simuloi rikkinäistä tilasiirtymää todistaen Desktop UI -virheenkäsittelymekanismin `AppErrorBoundary` luotettavuuden.
