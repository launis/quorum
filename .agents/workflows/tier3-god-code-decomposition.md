---
description: 
---

# Tier 3 Workflow: God Code Decomposition

Tämä työnkulku on tarkoitettu raskaiden "jumalkoodien" (God Code) systemaattiseen hajauttamiseen ja refaktorointiin SRP- ja DDD-periaatteiden mukaisesti. Käytä tätä, kun suuri tiedosto on kasvanut yli 500 rivin mittoihin ja pitää sisällään liian monta toisistaan irrallista vastuualuetta.

```xml
<system_prompt>
  <objective>[MÄÄRITÄ KOHDE TÄHÄN. Esim: "Hajauta backend_v2/services/execution.py"]</objective>
  <role>Senior Developer & Systems Architect</role>
  <context_rules>
    <rule>Tämä työnkulku on tarkoitettu raskaiden "jumalkoodien" (God Code) systemaattiseen hajauttamiseen ja refaktorointiin SRP- ja DDD-periaatteiden mukaisesti. Käytä tätä, kun suuri tiedosto on kasvanut yli 500 rivin mittoihin ja pitää sisällään liian monta toisistaan irrallista vastuualuetta.</rule>
    <rule>Tämä perustuu dokumenttiin: `docs/epic/EPIC_94_Module_Decomposition_Workflow.md`.</rule>
  </context_rules>
  <execution_protocol level="3">
    <step id="1">VAIHE 1 (Kartoitus ja Suunnittelu): Lue kohdetiedosto kokonaisuudessaan läpi (`view_file`). Kirjoita `implementation_plan.md` -tiedostoon (tai `task.md`) selkeä erittely siitä, mihin vastuualueisiin tiedosto on jakautunut. Hahmottele tiedoston pohjalta luotava uusi alihakemistorakenne. Varmista, että uusi rakenne tukee 2026 Best Practices -ohjeistusta (Fail-Fast, Strict Typing, Pydantic).</step>
    <step id="2">VAIHE 2 (Fasaadimallin Valmistelu - Split & Facade): Luo uudet tyhjät tai runkotason `.py`-tiedostot valittuun uuteen hakemistoon. Siirrä ydinlogiikka alkuperäisestä tiedostosta uusiin tiedostoihin (`multi_replace_file_content` / `write_to_file`). Muuta alkuperäinen tiedosto **fasaadiksi** (Facade Pattern), joka vain importtaa ja delegoi kutsut näille uusille moduuleille. (Kriittistä: muu järjestelmä pidetään luulossa, että alkuperäinen tiedosto toimii yhä sellaisenaan).</step>
    <step id="3">VAIHE 3 (Laatuportin Tarkastus - Quality Gate): Heti kun logiikka on hajautettu ja fasaadi pystytetty, aja Universal Quality Gate -tarkastus: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`. Jos audit-luuppi kaatuu linttaukseen (ruff), tyypitykseen (mypy) tai yksikkötesteihin (pytest), korjaa virheet välittömästi, äläkä siirry eteenpäin ennen kuin testi menee läpi 100%.</step>
    <step id="4">VAIHE 4 (Testien Hajautus): Etsi kohdetiedostoa vastaavat yksikkötestit (esim. `tests/unit/services/test_execution.py`). Jaa nämäkin "jumalatestit" vastaamaan uutta modulaarista rakennetta. Varmista, että kaikki testit menevät edelleen läpi.</step>
    <step id="5">VAIHE 5 (Viimeistely): Esitä käyttäjälle (`walkthrough.md`) koonti siitä, mitkä tiedostot luotiin ja miltä uusi arkkitehtuuri näyttää. Odota käyttäjän hyväksyntää sille, voidaanko väliaikainen fasaadi-tiedosto poistaa kokonaan ja refaktoroida muut viittaukset.</step>
  </execution_protocol>
</system_prompt>
```
