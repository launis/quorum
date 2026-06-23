# EPIC 84: Hybrid UI Sanitization & Output Profile Refactoring

## 1. Tausta ja Ongelma (Background)

Käyttöliittymässä (SDUI) ja lopullisissa PDF-raporteissa on havaittu visuaalisia ja kognitiivisia lukuongelmia (Wall of text, raakojen `tda_...` sääntö-ID:iden vuotaminen tekstiin, puuttuvat rivinvaihdot listojen välistä, sekä epäjohdonmukainen pituus). Lisäksi `synthesis.py`:n lopussa suoritettava "Row Explanations" -generointi on osoittautunut raskaaksi, vikaherkäksi ja redundantiksi, koska se käyttää raakasitaatteja (`exact_quotes`) kokonaan uuden tiivistelmän kääntämiseen.

Tällä hetkellä luotamme liikaa siihen, että Admin Studion "Tulostusprofiilit" (Output Profiles) ja raskaat LLM-promptit pystyvät 100-prosenttisesti tuottamaan täydellistä ja puhdasta UI/Markdown-dataa. Kokemus kuitenkin osoittaa, että probabilistinen malli tekee aina pieniä muotoiluvirheitä ja vuotaa metadataa.

## 2. Tavoite (Objective)

Siirtyminen **Hybridimalliin ("Sandwich Architecture")**, jossa:
1. **Deterministinen Python-esisiivous** riisuu tekoälyn tuotoksista kaiken teknisen roskan ja hoitaa UI-asettelun rajoitteet.
2. **Kognitiivinen tekoäly (Tulostusprofiilit)** keskittyy yksinomaan tekstin analyyttiseen sisältöön (Senior Executive Coach -ajattelu), eikä sen tarvitse murehtia täydellisestä Markdown-syntaksista tai maksimipituuksista.
3. **Riviselitteiden kognitiivisen tuplatyön poistaminen** täysin. Korvaamme kalliin LLM-generoinnin suoralla Python-kopiolla alkuperäisen arviointivaiheen `semantic_reasoning` -datasta, parantaen objektiivisuutta ja pudottaen token-kulutuksen nollaan.

## 3. Toteutussuunnitelma (Implementation Plan)

### Vaihe 1: Python UI Sanitizer (Robottipölynimuri)
Luodaan uusi apufunktio `backend_v2/utils/ui_sanitizer.py`, joka suorittaa puhtaasti deterministisen jälkikäsittelyn kaikelle UI-leipätekstille:
- **ID-Pesu:** `re.sub(r'tda_[a-f0-9]{32}', '', text)` (Poistaa rumat sääntö-ID:t tekstistä).
- **Whitespace & Markdown -korjaus:** Pakotetaan numeroidut listat (1., 2.) omille riveilleen ja poistetaan tuplatyljät rivit (`\n\n\n` -> `\n\n`).
- **Null-Normalisointi:** Muutetaan "N/A", "None", "Ei huomautettavaa" -> yhtenäinen tyhjä arvo tai UI-ohjaus.
- **Turvaleikkuri:** Pakotetaan maksimipituudet tekstiblokeille (esim. max 3000 merkkiä PDF-taiton pelastamiseksi).

### Vaihe 2: Osittainen Tulostusprofiilien Keventäminen (Promptien päivitys)
Koska Python hoitaa nyt siivouksen, voimme yksinkertaistaa Admin Studion "Tulostusprofiileja" (Output Profiles). 
- Poistamme tulostusprofiilien prompteista epätoivoiset säännöt, kuten *"Älä koskaan tulosta ID-koodeja"* tai *"Muista aina käyttää tarkalleen kahta rivinvaihtoa"*.
- Tekoäly saa keskittyä pelkkään asiantuntijatekstin (Executive Summary) tuottamiseen. Python ottaa kopin lopusta. Se on "osittainen ratkaisu", jossa profiili ohjaa ajatusta, mutta Python ohjaa ulkoasua.

### Vaihe 3: Keskitekstien (Section Syntheses) reititys pesulan läpi
Muokataan `synthesis.py` -tiedostoa (rivit 877-888) siten, että juuri ennen kuin tulokset tallennetaan `state_deltaan`:
- Jokainen `section_syntheses` -kappale (Perustelut, Valmennusvinkki, Paholaisen asianajaja) ajetaan `ui_sanitizer`:in läpi.
- Tämä korjaa lähettämissäsi ruutukaappauksissa näkyneet "Päättelyn rehellisyys" -laatikoiden ID-koodit ja tekstiseinät välittömästi.

### Vaihe 4: Row Explanations -generaattorin murha (Hybridi-refaktorointi)
Refaktoroidaan `synthesis.py`:n rivit 804-876:
1. Poistetaan kokonaan `row_exp_prompt` ja kaikki viittaukset LLMClientin suoritukseen (`exp_client`, `execute_structured_task`).
2. Yksinkertaistetaan logiikka: Kun käymme läpi `available_dtos`, poimimme suoraan `payload.get("semantic_reasoning")`.
3. Ohjelmoidaan Python siivoamaan kyseinen teksti (poistetaan tyhjät jne.) ja mahdollisesti leikkaamaan se ensimmäiseen pisteeseen (`.`) tai maksimipituuteen, jos se on liian pitkä.
4. Sijoitetaan tulos suoraan `row_explanations_dict` -tauluun.
**Perustelu:** Tämä tekee selitteistä analyyttisempiä, säästää kallista LLM-aikaa ja poistaa yhden potentiaalisen vikaantumispisteen järjestelmästä.

## 4. Odotetut Hyödyt (Expected Benefits)
- **Kognitiivinen Ergonomia:** Raporttien UI näyttää ammattimaiselta, objektiiviselta ja täysin vapaalta tietokantaviitteistä tai rikkinäisistä listoista.
- **Järjestelmän Vakaus:** PDF-renderöinti ei enää koskaan kaadu ylipitkiin teksteihin, koska Python-turvaleikkuri takaa taiton eheyden.
- **Suorituskyky ja Kustannukset (Täydellinen voitto):** Riviselitteiden 60 sekunnin LLM-ajo poistuu kokonaan. Järjestelmä on sekunteja nopeampi, maksaa vähemmän Vertex AI tokeneita, ja Schema Validation -riskit poistuvat tältä osin täysin.

---
**Tila:** Ready for Execution (Tier 2)
