# EPIC 88: FastDev-Tila (Kustannus- ja Nopeusoptimointi)

## 1. Yhteenveto & Tavoite (Executive Summary)

**Tavoite:** Mahdollistaa välitön siirtymä maksimaaliseen kehitysnopeuteen (minimikustannukset ja nollaviiveet) aina, kun `.env` -tiedoston `ENVIRONMENT=development`. Tämä tehdään koodin arkkitehtuuria hyödyntäen ilman, että joudumme likaamaan tuotantotietokannan (`seed_data.json`) virallisia konfiguraatioita.

Tämä on elintärkeää, koska ilman näitä rajauksia täysi end-to-end ajo voi kestää tuskastuttavan kauan ja maksaa tarpeettomasti rahaa.

---

## 2. Toteutuksen Vaiheet (Implementation Tiers)

### 2.1 Enum-rajoitteiden dynaaminen ohitus (Module-Load Override)
Pythonin Enums evaluoidaan kerran käynnistyksessä. Tuomme asetukset sisään ja muutamme kovat rajoitteet nopeusoptimoiduiksi kehitystilassa.

*   **Tiedostot:** `backend_v2/models/enums.py`
*   **Toimenpiteet:** 
    *   Lisätään tiedoston alkuun ympäristömuuttujan luku:
        ```python
        from backend_v2.settings import get_settings
        is_dev = get_settings().environment == "development"
        ```
    *   **Päivitetään viiveet ja laajuudet `SystemConcurrency` -luokassa:**
        *   `PACING_DELAY_VERTEX_SECONDS = 0 if is_dev else 12`
        *   `PACING_DELAY_OPENAI_SECONDS = 0 if is_dev else 1`
        *   `LLM_RETRY_MIN_SECONDS = 0 if is_dev else 2`
        *   `LLM_DEFAULT_TIMEOUT_SECONDS = 60 if is_dev else 600`
        *   `MATRIX_SAMPLING_LIMIT = 2 if is_dev else 0` *(Arvioi vain 2 atomia, ohita loput)*
        *   `LLM_MAX_RETRIES = 0 if is_dev else 2` *(Fail-fast)*
        *   `SCHEMA_MAX_LOCALIZED_ANCHORS = 2 if is_dev else 15` *(Minimoi ankkurien poiminta)*
        *   `SCHEMA_MAX_QUOTES_TARGET = 1 if is_dev else 5` *(Lainaa vain 1 kerta per rivi)*
        *   `SCHEMA_MAX_QUOTE_LENGTH = 50 if is_dev else 150` *(Lyhentää lainausten pituutta)*

### 2.2 Mallien lennossa vaihtaminen (Runtime Model Degradation)
Säilytetään `seed_data.json` koskemattomana. Vaihdetaan raskas malli kevyeen juuri ennen API-kutsua kehitystilassa.

*   **Tiedostot:** `backend_v2/llm/client.py`
*   **Toimenpiteet:**
    *   **Muutos `LLMClient.from_strategy()` -metodiin:**
        ```python
        target_model_name = target_strategy.model_name
        from backend_v2.settings import get_settings
        if get_settings().environment == "development":
            # Downgrade Pro models to Flash for extreme speed and low cost
            if "-pro" in target_model_name.lower():
                target_model_name = target_model_name.replace("-pro", "-flash").replace("-PRO", "-FLASH")
                
            # Flash handles much higher RPM, so we can uncap the artificial limits
            if target_strategy.rpm_limit and target_strategy.rpm_limit < 100:
                target_strategy.rpm_limit = 100
        ```
    *   **Muutos `run_structured_task` -metodiin (Global Prompt Override):**
        Jos olemme kehitystilassa, injektoidaan kaikkiin pyyntöihin pakottava sääntö Output Tokenien kuristamiseksi:
        ```python
        if get_settings().environment == "development":
            dev_instruction = "\n\n[SYSTEM: FAST-DEV MODE ACTIVE]\nKeep ALL string fields, explanations, and justifications strictly UNDER 5 WORDS. Speed is the only priority."
            # Lisätään tämä promptin loppuun
        ```

---

### 2.3 Tietoturvallinen Mock Login (Dev Tools -paneeli)
Tällä hetkellä "Mock Login" -toiminnot on kovakoodattu Flutterin `login_screen.dart` -tiedostoon, ja pahempana ongelmana **backend sallii mock-tokenit (`mock-token:*`) tuotannossa**, mikäli sellainen API:in lähetetään! Tämä on kriittinen tietoturvariski. Mock Login tulee sulkea tiukasti vain "FastDev"-tilan ja lokaalin debug-tilan taakse.

*   **Backend-toteutus (`backend_v2/services/auth.py`):**
    *   Korjataan `verify_token`-metodin logiikka. Mock-tokenit sallitaan **vain**, kun ympäristönä on `development`.
    *   ```python
        from backend_v2.settings import get_settings
        
        is_dev = get_settings().environment == "development"
        is_mock_token = token.startswith("mock-token:")
        
        # 1. Torjutaan mock-tokenit tuotannossa heti (Fail-Fast)
        if is_mock_token and not is_dev:
            raise AuthenticationError(
                message="Mock tokens are strictly forbidden in production.", 
                details={"error_code": "FORBIDDEN_TOKEN"}
            )
            
        # 2. Sallitaan mock/paikallinen dev-kirjautuminen
        if not self.use_firebase or (is_mock_token and is_dev):
            # ... nykyinen mock-logiikka ...
        ```
*   **Frontend-toteutus (`client_app_v2/lib/features/auth/presentation/login_screen.dart` & `env.dart`):**
    *   Lisätään `env.dart` -tiedostoon tuki `ENVIRONMENT` -muuttujan lukemiselle `.env` -tiedostosta (täysi symmetria backendin kanssa).
    *   Siirretään "Development Tools" -osio täysin erilliseen widgettiin, esim. `MockLoginPanel`.
    *   Renderöidään tämä paneeli `login_screen.dart`:ssa **vain** jos sovellusta ajetaan kehitystilassa `.env` -määrityksen mukaisesti. Näin tuotanto-buildiin (`ENVIRONMENT=production`) ei koskaan vahingossakaan renderöidä nappeja tai niiden kovakoodattuja tekstejä.
    *   ```dart
        import 'package:client_app/core/environment/env.dart';
        
        // Renderöidään vain jos .env tiedostossa lukee development
        if (Env.environment == 'development') ...[
          const SizedBox(height: 24),
          const MockLoginPanel(),
        ],
        ```

---

## 3. Miksi tämä on Best Practice?
1. **Kokonaisvaltainen Nopeus:** Mallit on downgradettu salamannopeaan Flash-malliin, prosessoitavien kriteerien määrä on kuristettu 2:een, tekstin poimintamäärät on pudotettu murto-osaan ja tekstiin on pakotettu max 5 sanan rajoitus. Täysimittainen ajo muuttuu nopeaksi End-to-End "Traceriksi".
2. **Zero-Pollution (Nollasaastuminen):** Tuotantotietokanta (`seed_data.json`) pysyy alkuperäisessä Pro-tilassaan. `.env` tiedosto kontrolloi suoraan sitä, ajetaanko putki Tracer-tilassa vai raskaassa laadunvarmistustilassa.

---

## 4. Verification Plan
1. Ajetaan `backend_audit_loop.py` varmistamaan, että Pydantic-säännöt eivät mene rikki ohituksesta (Esim. mahdolliset minimipituusvaatimukset, jotka voivat konfliktata dynaamisten arvojen kanssa).
2. Asetetaan `ENVIRONMENT=development` ja ajetaan työnkulku: katsotaan lokista, että LLM:n palauttamat tekstit ovat vain muutaman sanan mittaisia ja suoritusaika putoaa sekunteihin.
