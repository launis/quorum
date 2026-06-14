# P2: Seed Vault -auditointi ja Broken Atoms -siivous

## Tavoite
Korjata tai disabloida tyhjät ja puutteelliset `extraction_rule` -säännöt Seed Vaultista. Oletus on, että dataohjatun logiikan tulee tukeutua validiin tietokantasisältöön eikä LLM:n arvaustaitoihin.

## Toimenpiteet
1. Etsi `backend_v2/seed/seed_data.json` -tiedostosta TDA:t/atomit, joiden `extraction_rule` on tyhjä `""` tai erittäin lyhyt (esim. `"found."`, alle 10 merkkiä).
2. Jos sääntö on selkeästi korjattavissa asiayhteydestä, korjaa se. Muussa tapauksessa aseta `disabled: true`.
3. Aja lokaali seedaus uudelleen: `uv run python backend_v2/seed/run_seed.py local`.
4. Varmista tietokannan eheys ja ettei auditointi rikkonut muita SSOT-rakenteita.

## Säännöt ja Rajoitteet
- **Database Schema Hallucination (Rule 76):** Älä muuta tietorakenteita (esim. array-rakenteita) `seed_data.json`:ssa, korjaa ainoastaan vialliset tekstikentät ja ohjausliput.
