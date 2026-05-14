# V5 Agnostic Hardening Plan (Epic)

## Tavoite
Poistaa loput 11.4 % "haamuvarianssista" TDA (Task/Data Analysis) -putkesta. Tarkoituksena on estää tekoälyä toimimasta "lakimiehenä", joka perustelee miksi irtonaiset asiat liittyvät toisiinsa. Ratkaisun täytyy olla globaali, kieli- ja formaattiriippumaton, jotta sitä voidaan soveltaa yhtä lailla suomenkielisiin Sitra-raportteihin kuin englanninkieliseen koodiin tai lakitekstiin.

## Lähestymistapa: Globaali Asenneviritys (`ai_description`)
Emme muokkaa kaikkia 185 atomia (`ai_rule_description`) yksitellen. Sen sijaan muokkaamme `seed_data.json` -tiedoston `PromptBlock` -tasoisia `ai_description` -kenttiä. Tämä injektoi sokean ja ehdottoman asenteen koko analyysiputkeen jo ylätasolla.

## Uudet Globaalit Säännöt (Injektoitavat)

Nämä kolme sääntöä lisätään jokaisen `PromptBlock`:in `ai_description`-kenttään:

1.  **ANTI-LAWYER MANDATE (No-Argument Rule)**
    *   *Tarkoitus:* Estetään mallia keksimästä post-hoc-rationalisointeja ja asioiden venyttämistä.
    *   *Teksti injektoitavaksi:* "ANTI-LAWYER MANDATE: If your `mechanical_trace` requires explaining *why* or *how* the text matches the rule, you have failed the blind extraction. The match must be structurally self-evident. If you use words like 'implies', 'means', 'functionally', or 'basically' in your trace, you MUST return null."

2.  **HARD BOUNDARY RULE (Rakenteellinen rajaus)**
    *   *Tarkoitus:* Estetään mallia yhdistämästä logiikkaa kappale- tai taulukkorajojen yli, mikä on aiheuttanut vääriä osumia (esim. taulukon sarakkeiden implisiittinen yhdistely).
    *   *Teksti injektoitavaksi:* "HARD BOUNDARY RULE: A logical relationship (causal, conditional, comparative) MUST exist within a single, continuous grammatical sentence. Tables, bullet points, headers, and paragraph breaks are hard boundaries. Bridging logic across hard boundaries is strictly forbidden."

3.  **PRE-COMMITMENT (Leksikaalinen sitoutuminen)**
    *   *Tarkoitus:* Pakotetaan malli tulostamaan kielellisesti käännetyt hakusanat ennen tekstin lukemista, estäen lennosta keksityt "luovat" käännökset.
    *   *Teksti injektoitavaksi:* "PRE-COMMITMENT: Your first step in `mechanical_trace` MUST be to output the exact, literal translated substrings you will search for. You may only extract text that contains one of these exact, pre-declared substrings."

## Toteutusaskeleet (Execution Steps)

1.  **Vaihe 1: Massapäivitys-skripti (`scratch/v5_mass_refactor.py`)**
    *   Kirjoitetaan Python-skripti, joka lukee `backend_v2/seed/seed_data.json`.
    *   Skripti käy läpi kaikki `prompt_blocks` ja lisää yllä olevat kolme sääntöä kunkin lohkon `ai_description` -kentän alkuun.
    *   Säilytetään lohkon alkuperäinen asenne ja ohjeistus (esim. "Olet puolueeton arvioija...").

2.  **Vaihe 2: Ajo ja Varmennus (Sanity Check)**
    *   Ajetaan skripti, joka tallentaa päivitetyn datan.
    *   Suoritetaan tietokannan Hard Reset ja Seeding (`tier3-database-reset` -kulkukaavion mukaisesti, käyttäen olemassa olevaa `run_seed.py` skriptiä), jotta uudet ylätason ohjeistukset latautuvat järjestelmään (SQLite/TinyDB).

3.  **Vaihe 3: Validoiva Ristiinajo (Agnostinen Testi)**
    *   Ajetaan TDA-putki uutta konfiguraatiota vastaan uudella ajolla.
    *   Ajetaan diffaus (`scratch/diff_executions.py`) varmistaaksemme, että varianssi putoaa alle 5 %:iin ja erityisesti implisiittisestä päättelystä johtuvat vanhat "väärien osumien" haamut on eliminoitu.
