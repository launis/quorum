# Arkkitehtuuripäivitys V3: SDUI:n Kevyt Eriyttäminen ja UX-Parannukset

Tämän suunnitelman tavoitteena on **säilyttää Server-Driven UI (SDUI) -arkkitehtuurin valtava dynaaminen voima**, mutta poistaa sen manuaaliseen koodaamiseen liittyvä tuskastuttava monimutkaisuus. 

Emme pura SDUI-moottoria kokonaan (MVC-malliin), vaan teemme "kirurgisia" yksinkertaistuksia, jotta `seed_data.json` on ihmisen luettavissa ja asettelut (Layouts) ovat uudelleenkäytettäviä.

---

## Vaihe 1: Ihmisluettavat Nodi-ID:t (Developer UX)
SDUI:n suurin tuska tällä hetkellä on `steprule_ec0bbf02...` -tyyppisten kryptografisten koodien jäljittäminen `data_paths` -viittauksissa.

### Steppi 1.1: Opaque ID -säännön keventäminen
* **Tavoite:** Mahdollistaa loogiset nimet solmuille säilyttäen Pydantic-turvallisuus.
* **Toimenpide:** Pydanticin `StepRule.id` -kentän nykyinen sääntö (`^([a-z]+)_[a-zA-Z0-9]{8,}$`) sallii jo nyt ihmisluettavat sanat (kunhan niissä ei ole toista alaviivaa ja pituus on yli 8). Hyödynnämme tätä välittömästi.
* **Toteutus:** Päivitämme `seed_data.json`:n työnkulut käyttämään selkokielisiä tunnisteita:
  - `steprule_ec0bbf...` -> `steprule_xaireport1`
  - `steprule_8b245c...` -> `steprule_judge1`
* **Haluttu Output:** SDUI-komponenttien reititykset (`data_paths: ["$results.steprule_xaireport1.evaluation_notes"]`) muuttuvat silmäyksellä luettaviksi, ilman että yksikään rivi Python-koodia rikkoutuu.

---

## Vaihe 2: Asettelujen (Render Blueprints) Eriyttäminen
Jotta `seed_data.json` -tiedoston `workflows`-taulu ei olisi kymmeniä tuhansia rivejä pitkä, siirrämme SDUI-määritykset asumaan omaan "kirjastoonsa".

### Steppi 2.1: Globaali `ReportLayout` -malli
* **Tavoite:** Irrottaa layoutit työnkuluista uuteen tietokantatauluun säilyttäen SDUI:n.
* **Toimenpide:** 
  1. Poistetaan `render_blueprints` `Workflow`-luokasta.
  2. Luodaan `v2_core.py`-tiedostoon uusi juuriluokka `ReportLayout`, joka sisältää saman `components`-listan, jota `render_blueprints` käytti.
* **Haluttu Output:** Pydantic-mallit tukevat "Teemakirjastoa", jota useat eri työnkulut voivat hyödyntää.

### Steppi 2.2: Tietokannan (seed_data.json) Rakennemuutos
* **Tavoite:** Työnkulkujen ja Ulkoasujen erottaminen datatasolla.
* **Toimenpide:** Leikataan `render_blueprints` rakenteet pois ` workflows`-objektien sisältä ja sijoitetaan ne tiedoston juureen uuteen listaan: `"report_layouts": [ ... ]`.
* **Haluttu Output:** Dev-tiimi voi koodata backendin työnkulkuja (steps) yhdessä osassa tiedostoa ja UI-tiimi voi tuunata SDUI-näkymiä omassa osassaan tiedostoa.

---

## Vaihe 3: Moottorin ja Rajapinnan Päivitys
Kun data on eriytetty, päivitämme olemassa olevan SDUI-moottorin lukemaan uutta rakennetta.

### Steppi 3.1: Python SDUI-reitittimen (`blueprint.py`) päivitys
* **Tavoite:** Opettaa vanha moottori hakemaan layoutit uudesta paikasta.
* **Toimenpide:** Muutetaan `BlueprintTransformer` -logiikkaa. Se ei enää kysy: *"Mikä on tämän työnkulun sisäänrakennettu layout?"*. Se kysyy globaalilta tietokannalta: *"Anna minulle layout ID:llä X"*. 
* **Haluttu Output:** Vanha ja tehokas `resolve_component()` -rekursio jatkaa toimintaansa täysin muuttumattomana. Jinja2 PDF-templatet tai Flutterin WidgetFactory eivät vaadi RIVIÄKÄÄN koodimuutosta!

## Yhteenveto
Tällä minimaalisella purkamisella:
1. **Säilytämme Nollakoodi-Flutterin:** Mobiilisovellus rakentaa yhä itsensä dynaamisesti serverin JSON-käskyistä.
2. **Tuhoamme Koodilukutaidottomuuden:** Ihmisluettavat `steprule_`-nimet tekevät manuaalisen debuggauksen helpoksi.
3. **Saavutamme Separation of Concerns:** Työnkulut ja PDF-pohjat asuvat eri kansioissa.

## Vaadittavat Dokumentaatiopäivitykset
Tämän tehtävän päätteeksi on päivitettävä `c:\src\quorum\docs\`:
1. `Arkkitehtuurimäärittely_ AI-orkestraattori V2.md`
2. `v2_sdui_and_de_generator_mandate.md`
3. Erityisesti `Arkkitehtuuristandardi_Tietokannan_Tunnisteet.md` - jotta Opaque ID -sääntö heijastaa uutta "Ihmisluettava Opaque ID" -linjaustamme (`steprule_xaireporter`).
