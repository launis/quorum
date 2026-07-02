# EPIC 94: God Code Module Decomposition Workflow

## Tavoite (2026 Best Practices)
Nykyiset suuret "jumalkoodit" (esim. `worker.py`, `blueprint.py`, `execution.py`) rikotaan SRP (Single Responsibility Principle) ja Domain Driven Design -periaatteiden mukaisesti erillisiin alikansioihin. 

Taaksepäinyhteensopivuutta ei vaadita, mutta jokaisen modulaarisen osan tulee sisältää vahvat rajapinnat ja omat eristetyt yksikkötestinsä (Fail-Fast, Pydantic, strict-typing).

## Työnkulku (Workflow)
Moduulien purkaminen suoritetaan systemaattisesti yhden tiedoston kerrallaan noudattaen seuraavaa 5-vaiheista protokollaa:

### Vaihe 1: Mapping & Abstraction (Kartoitus ja Abstraktio)
- Analysoidaan kohdetiedosto (esim. `execution.py`).
- Tunnistetaan itsenäiset vastuut (esim. raportin generointi, SDUI-mäppäys, tietokantapäivitykset).
- Suunnitellaan uusi hakemistorakenne: `backend_v2/services/execution_domain/`.

### Vaihe 2: Baseline Testing (Testauksen Suojamuuri)
- Varmistetaan, että hajotettavalla koodilla on riittävä testikattavuus ennen purkamista.
- Jos testejä puuttuu, luodaan yksinkertaiset "mustalaatikko"-testit varmistamaan, ettei mikään ulkoinen riippuvuus hajoa muutoksen aikana.

### Vaihe 3: Split & Facade Pattern (Purkaminen ja Fasaadi)
- Siirretään erilliset vastuut omiin moduuleihinsa (esim. `execution_domain/report_generator.py`, `execution_domain/state_manager.py`).
- Jätetään alkuperäinen tiedosto (`execution.py`) toistaiseksi olemassa olemaan Facade-kerroksena, joka vain reitittää kutsut uusiin alimoduuleihin. Näin vältetään massiiviset muutosvyöryt muualla koodikannassa.

### Vaihe 4: Quality Gate (Laatuportti)
- Ajetaan uuden arkkitehtuurin läpi tiukat laatutarkastukset (`backend_audit_loop.py --test`).
- Varmistetaan MyPy `strict` -tyypitykset ja Pydantic-mallien eheyden säilyminen.

### Vaihe 5: Coverage Gap Remediation (Testien hajautus)
- Kun koodi on jaettu, myös vanhat "jumalatestit" jaetaan vastaamaan uutta moduulirakennetta (esim. `tests/unit/services/execution_domain/test_report_generator.py`).
- Poistetaan väliaikainen Facade-tiedosto, kun kaikki viittaukset on päivitetty uusiin moduuleihin (valinnainen, jos Facade on hyödyllinen API-rajapintana, se voidaan jättää).
