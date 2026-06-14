# P0: Contextual Override -erimielisyyksien siivous Seed Vaultista

## Tavoite
Poistaa tietokannasta (Seed Vault) "Do not evaluate" -meta-säännöt ja tyhjät kysymykset, jotka aiheuttavat Contextual Override -erimielisyyksiä. Arkkitehtuuripäätöksen mukaisesti nämä korjataan datarakennetasolla (`seed_data.json`), jotta prompt-compileria ei tarvitse rasittaa ylimääräisillä ohituksilla.

## Toimenpiteet
1. Etsi `backend_v2/seed/seed_data.json` -tiedostosta kaikki atomit/TDA:t, joiden:
   - `concept_description` alkaa tekstillä *"Do not evaluate"* tai sisältää vastaavan meta-ohjeen.
   - `question` on tyhjä merkkijono `""` tai `None`.
2. Merkitse nämä objektit `disabled: true` -lipulla (tai poista ne, jos arkkitehtuuri näin vaatii), jotta ne eivät vuoda arviointiin.
3. Tarkista tietokannan eheys `backend_v2/seed/run_seed.py local` -skriptillä.

## Säännöt ja Rajoitteet
- **Fail-Fast & Zero-Compromise:** Viallinen data poistetaan alkulähteellä (SSOT), ohjelmallisia ohituksia ei sallita.
- **Duct Tape Ban:** Älä lisää if-else ohituksia prompt-compileriin tätä varten.

## Valmennus Tier 2 -agentille
Kun suoritat tätä taskia, muokkaa ainoastaan `seed_data.json` -tiedostoa ja aja seed-skripti ohjeistetusti. Voit käyttää `/tier3-database-reset` tai vastaavaa työnkulkua.
