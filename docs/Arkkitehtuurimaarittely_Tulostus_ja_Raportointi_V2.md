# Arkkitehtuurimäärittely: Yleiskäyttöiset Tulostusprofiilit V2 (Full-Stack CRUD & BFF)

*Tämä dokumentti määrittelee Quorum V2 joustavan tulostus- ja raportointiarkkitehtuurin (Output Profiles & Backend-For-Frontend ViewModel). Arkkitehtuuri on suunniteltu tarjoamaan täydellinen skaalautuvuus, täysi PDF vs. Näyttö -pariteetti ja Domain-Driven eriyttäminen työnkulkujen (Workflows) ja tulosteiden (Reports) välillä.*

## 1. Tavoite ja Best Practice -vertailu

Koko tulostuksen hallinnan (Output Profiles & Renderers) arviointi paljastaa nykytilan ja Enterprise-luokan Best Practice -ratkaisun eron:

| Ominaisuus | Nykytila | Best Practice (Tavoitetila) |
| :--- | :--- | :--- |
| **Arkkitehtuuri** | Tulosteet on upotettu työnkulkujen JSON-puihin. | **Domain-Driven Design (DDD).** Tulostusprofiilit ovat täysin itsenäisiä tietokantaentiteettejä (Uusi `/api/v2/output-profiles/` REST API). |
| **Admin UI (Hallinta)** | Dynaaminen "Blueprint Editor" (JSON-kenttien muokkaus). | **Erikoistunut CRUD-näyttö**, joka estää virhetilat UX-pakotteilla (alasvetovalikot). |
| **Monikielisyys (I18n)** | Vapaamuotoiset sanakirjat ilman sääntöjä. | **Strict I18nText -rakenne:** Englanti on *aina* pakollinen (master kieli). Backend tiputtaa arvon aina englantiin varotoimena. |
| **BFF Keventäminen** | Flutter kantaa logiikkataakkaa ("Muodosta 2D vs 1D"). | **Backend-For-Frontend ViewModel:** Python esilaskee asettelun (ViewModel Nodes). Flutter on sokea ja kevyt piirturi. |
| **PDF vs UI Pariteetti** | PDF-moottori rakentaa asettelun eri logiikalla omassa Jinja2-loopissa. | Täysi logiikkapariteetti. PDF-moottori ja Flutter iteroivat tismalleen saman BFF-lasketun Node-listan. |

## 2. Kieliversiot ja I18nText (Localization Strategy)

Dynaamiset käyttäjätekstit (Analyysin otsikot, asettelujen nimet) käsitellään backendissä tiukalla `I18nText` Pydantic-mallilla.
*   **I18nText Best Practice:** Englanti (`en`) on globaali ja **pakollinen** kenttä. Muut kielet (esim. `fi`) ovat täysin vapaaehtoisia.
*   **Fallback-logiikka:** Kun tulostusmoottori (PDF tai UI) pyytää arvoa esim. kielellä "fi" ja sitä ei löydy, backend palauttaa englannin. DTO ei koskaan palauta `Null`-otsikkoa.

## 3. Uudet REST API:t & End-to-End Pydantic-turva

Irrotamme tulostusprofiilit omaksi resurssikseen uuden API:n alle (`GET /api/v2/output-profiles/` jne.).
1.  **Validointi Heti Alkuun:** Uusi `I18nText` ja laajennettu `OutputProfileLayout` takaavat, ettei tietokantaan voida koskaan tallentaa rikkinäistä layoutia. FastAPI palauttaa 422 Unprocessable Entity -virheen heti tallennuksessa, jos Admin yrittää ohittaa säännöt.
2.  **Kääntäjä (Compiler) & Automaattinen Nimien Generointi:** Työnkulun ajon jälkeen `blueprint.py` yhdistää tulokset ja tulostusprofiilin laatiakseen valmiin raportin. 
    *   **Auto-Naming:** DataGridien/Excelin vaatimat sarakeotsikot generoidaan automaattisesti lukemalla suoraan valittujen blokkien natiivit nimet.
    *   **Collision Avoidance (Törmäysten esto):** Jos raportille on osumassa kaksi täysin samannimistä kenttää, kääntäjä kiipeää automaattisesti työnkulun DAG-puuta ylöspäin! Se eriyttää nimet edellisten tasojen tunnisteilla (esim. "Myynti - Riski" vs "Koneistamo - Riski") varmistaen yksilölliset otsikot tiedostovienneille tismalleen samasta kentän nimestä huolimatta.
    *   **Resilienssi (Graceful Degradation):** Jos tulostusprofiili käskee tekemään *2D Matriisin*, mutta raakadata palauttaakin muuttuneen työnkulun saati tekoälyn toiminnan vuoksi vain 1 arvon, Compiler tekee lennosta geometrisen korjauksen tiputtaen halutun asettelun "1D Info Box" muotoon, suojaten Frontendin kaatumisilta täysin näkymättömästi.

## 4. Frontend Admin Studio: Uusi CRUD Näyttö & UX

Luovutaan entisestä SDUI tyyppisestä vapaasta formilarakennuksesta tulostusasetusten parissa.
*   **Listanäkymä:** Selkeä lista kaikista järjestelmän Output-profiileista.
*   **Muokkausnäkymä (`output_profile_crud_view.dart`):**
    *   Kun lisätään "Uusi Asettelu", Admin valitsee asettelutyypiksi alasvetovalikosta esim: *Automaattinen, 1D Laatikko, 2D Matriisi, 3D Tutka, tai Riviluettelo (Excel Key/Value)*.
    *   Akselien asetus tehdään alasvetovalikosta (Valitaan olemassa olevan komponentin nimi listasta), jolloin UI tallentaa taustalla järjestelmään oikean `blk_xxx` -tunnisteen suoraan ohjelmallisena arvona. Ihmiset eivät enää kirjoita ID:tä käsin.

## 5. Tulostusmoottorin Vapauttaminen (Backend-for-Frontend "Dumb Client")

Kun suurin vastuu on jo Pythonilla, Flutterista tehdään täysin riisuttu "tyhmä piirtäjä":
*   **Zero-Math Rendering:** Flutter ei tee mitään numeerisia arvioita. Backend lähettää `/api/v2/executions/{id}/report` listan **täysin valmiiksi renderöitäviä UI palikoita (ViewModel Nodes)**.
*   **Map-silmukka:** Flutterin `report_renderer_widget.dart` on enää alle sadan rivin kompakti for-loop. Se lukee tyypit (`info_box`, `matrix_2d`, `key_value_row`) ja liittää ne suoraan vastaaviin visuaalisiin kortteihin tai 3rd party chartteihin. Formatoinnit on paketoitu tekstien sisään Pythonin toimesta.
*   Sama iterointi toteutetaan `report_template.jinja2` puolella PDF-moottoria varten, mahdollistaen 1:1 koodijaon ja taatun ulosannin ulkoasutulostimesta riippumatta.

## 6. Ajojen ja Tulostusprofiilien Risteytys (1:N Suhde)

Kruununa irrotetaan staattinen ajodata sen esitystavasta. Yksittäinen työnkulun ajo ei ole lukittu yhteen oikeaan raporttimuotoon.
*   **Vapaa Generointi:** Uusi ajo tallentuu tietokantaan vain loogisena numeeris-leksikaalisena raakadatana.
*   **Dynaaminen Valinta:** Käyttöliittymä (tai API) pyytää raportin muodostusta haluamallaan tulostusprofiililla parametrilla: `GET /api/v2/executions/{id}/report?profile_id={id}`.
*   Saman yksittäisen ajon (esim. "Auditointi 12.5") voi siis tallentaa ja tulostaa samanaikaisesti kolmena täysin eri raporttina sidosryhmien tarpeista riippuen:
    1.  *Johdon Tiivistelmä* (Vain isot 2D/3D matriisit)
    2.  *Syväluotaava Analyysi* (Kaikki perustelut 1D-laatikoissa)
    3.  *Excel-Rivi* (Vain raa'at Key/Value parit datataulukkoa varten omien järjestelmien syöteluvuilla) 
