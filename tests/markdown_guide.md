# Quorum Automaattitestit

Tämä kansio sisältää järjestelmän laadunvarmistustestit.

## Testien Suoritus

Varmista, että olet projektin juurihakemistossa (`quorum/`) ja virtuaaliympäristö on aktiivinen.

```bash
pytest tests
```

Jos haluat ajaa vain tietyt testit:
```bash
pytest tests
```

Jos haluat ajaa vain tietyt testit:
```bash
pytest tests/test_architecture_v2.py
pytest tests/test_adversarial_security.py
```

### Huomautus Palvelimesta
Testit **eivät vaadi** backend-palvelimen (`run_locally.bat` tms.) käynnistämistä.
Testit lataavat backendin koodin suoraan muistiin ajon ajaksi.
Live-testit ottavat itse yhteyden ulkoisiin API-rajapintoihin.

## Testisuitet

### 1. Arkkitehtuuri (`test_architecture_v2.py`)
Testaa backendin ydinlogiikan, erityisesti:
- **Raportointi:** Varmistaa, että Dual Judge -vertailu tuottaa oikean datamatriisin.
- **Builder:** (Tulevaisuudessa) Testaa uusien askelten luonnin logiikkaa.

### 2. Järjestelmän Kestävyys (`test_system_resilience.py`)
Simuloi virhetilanteita ja varmistaa, ettei järjestelmä kaadu hallitsemattomasti:
- **API Failure:** Tietokantavirheet käsitellään oikein (HTTP 500).
- **Graceful Degradation:** Raportointi ei kaada koko työnkulkua, vaikka template puuttuisi.

### 3. Tietoturva ja Adversarial (`test_adversarial_security.py`)
Simuloi hyökkäyksiä järjestelmää vastaan (Red Teaming):
- **Reflection Injection:** Yritetään syöttää "System Override" komentoja reflektiotekstin seassa.
- **History Poisoning:** Väärennetty keskusteluhistoria, jossa käyttäjä esittää adminia.
- *Huom:* Nämä testit varmentavat tällä hetkellä, että syöte päätyy arviointiin (eli järjestelmä näkee sen). Varsinainen torjunta riippuu käytetystä LLM-mallista.

### 4. Live Integraatiotestit (Real LLM)
Testit, jotka käyttävät oikeaa Gemini/OpenAI rajapintaa.

*   **Tiedosto:** `test_live_llm.py`
*   **Tarkoitus:** Varmistaa, että API-avaimet toimivat ja mallit tuottavat validia JSONia.
*   **Varoitus:** Kuluttaa API-krediittejä.

**Ajaminen:**
```bash
# Aja vain live-testit
pytest -m live

# Ohita live-testit (CI-oletus)
pytest -m "not live"
```

### 5. Ympäristötestit (`test_environments.py`)
Varmistaa, että sovellus valitsee oikean tietokantamoottorin (TinyDB Mock, TinyDB Local, Firestore) ympäristömuuttujien perusteella.
Tämä kattaa `run_*.bat` skriptien skenaariot kooditasolla.
### 6. End-to-End API Testit (`test_e2e_api.py`)
Accepance-tason testit, jotka simuloivat koko backendin toimintaa HTTP-rajapinnan kautta:
- **Testaa Mock DB:** Varmistaa lokaalin kehitysympäristön (`run_mock_locally.bat`) API-toimivuuden.
- **Testaa Firestore (Live):** Varmistaa, että API saa yhteyden pilveen. Tämä löytää konfiguraatiovirheet, jotka jäävät yksikkötesteissä huomaamatta.

## Parhaat Käytännöt (Best Practices)
1.  **Unit Tests First:** Testaa logiikka eristettynä (mockit) aina kun mahdollista.
2.  **Fail Gracefully:** Testaa aina myös "unhappy path" (virheet).
3.  **Security Awareness:** Tiedosta, että kaikki käyttäjäsyöte voi olla pahantahtoista.

## Ongelmanratkaisu
Jos saat `ModuleNotFoundError`:
- Varmista, että ajat `pytest`-komennon projektin juuresta, etkä `tests/`-kansion sisältä.
