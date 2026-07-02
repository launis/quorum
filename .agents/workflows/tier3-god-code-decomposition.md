# Tier 3 Workflow: God Code Decomposition

Tämä työnkulku on tarkoitettu raskaiden "jumalkoodien" (God Code) systemaattiseen hajauttamiseen ja refaktorointiin SRP- ja DDD-periaatteiden mukaisesti. Käytä tätä, kun suuri tiedosto on kasvanut yli 500 rivin mittoihin ja pitää sisällään liian monta toisistaan irrallista vastuualuetta.

Tämä perustuu dokumenttiin: `docs/epic/EPIC_94_Module_Decomposition_Workflow.md`.

## Suoritustapa
Työnkulku suoritetaan yhdelle syötetiedostolle kerrallaan.
**Syöte:** `<target_file>` (esim. `backend_v2/services/execution.py`)

---

## Vaihe 1: Kartoitus ja Suunnittelu
1. Lue kohdetiedosto kokonaisuudessaan läpi (`view_file`).
2. Kirjoita `implementation_plan.md` -tiedostoon (tai `task.md`) selkeä erittely siitä, mihin vastuualueisiin tiedosto on jakautunut.
3. Hahmottele tiedoston pohjalta luotava uusi alihakemistorakenne. *Esimerkiksi jos hajotetaan `execution.py`, luodaan hakemisto `backend_v2/services/execution_domain/` ja siihen osat kuten `report_generator.py` ja `state_manager.py`.*
4. Varmista, että uusi rakenne tukee 2026 Best Practices -ohjeistusta (Fail-Fast, Strict Typing, Pydantic).

## Vaihe 2: Fasaadimallin Valmistelu (Split & Facade)
1. Luo uudet tyhjät tai runkotason `.py`-tiedostot valittuun uuteen hakemistoon.
2. Siirrä ydinlogiikka alkuperäisestä tiedostosta uusiin tiedostoihin (`multi_replace_file_content` / `write_to_file`).
3. Muuta alkuperäinen tiedosto **fasaadiksi** (Facade Pattern), joka vain importtaa ja delegoi kutsut näille uusille moduuleille. 
   - *Tämä on kriittistä laajan rikkoontumisen estämiseksi: muu järjestelmä pidetään luulossa, että alkuperäinen tiedosto toimii yhä sellaisenaan.*

## Vaihe 3: Laatuportin Tarkastus (Quality Gate)
1. Heti kun logiikka on hajautettu ja fasaadi pystytetty, aja Universal Quality Gate -tarkastus, joka sisältyy järjestelmän sääntöihin:
   ```bash
   uv run python scripts/backend_audit_loop.py backend_v2/ --test
   ```
2. Jos audit-luuppi kaatuu linttaukseen (ruff), tyypitykseen (mypy) tai yksikkötesteihin (pytest), korjaa virheet välittömästi, äläkä siirry eteenpäin ennen kuin testi menee läpi 100%.

## Vaihe 4: Testien Hajautus
1. Etsi kohdetiedostoa vastaavat yksikkötestit (esim. `tests/unit/services/test_execution.py`).
2. Jaa nämäkin "jumalatestit" vastaamaan uutta modulaarista rakennetta (esim. `test_report_generator.py`).
3. Varmista, että kaikki testit menevät edelleen läpi.

## Vaihe 5: Viimeistely
1. Esitä käyttäjälle (`walkthrough.md`) koonti siitä, mitkä tiedostot luotiin ja miltä uusi arkkitehtuuri näyttää.
2. Odota käyttäjän hyväksyntää sille, voidaanko väliaikainen fasaadi-tiedosto poistaa kokonaan ja refaktoroida muut viittaukset. 
