# Epic: Template Copier & Validator (UI Layout Cloning Validation)

## Osa-alue: Admin Studio V2 - Arkkitehtuurin Koventaminen (Phase 9)

---

## 1. Tavoite ja Ongelman Kuvaus
V2-työnkulkujen näyttö (SDUI eli Server-Driven UI) rakennetaan ja renderöidään dynaamisesti backendin puolella, jolloin käyttöliittymä on täysin "Zero-Math". 

Jos tulostustemplaatti (UI Layout) sokeasti kopioitaisiin sellaisenaan toiseen työnkulkuun (Workflow B), joka ei edes sisällä kyseisen templaatin vaatimia askeleita tai matriiseja (esim. *Toulminin Argumentaatiomalli*), järjestelmä tuottaisi rikkinäisen tai "tyhjän" raportin. Pahemmassa tapauksessa puuttuva tietorakenne aiheuttaisi ajonaikaisia `Index out of bounds` tai `KeyError` -kaatumisia (vrt. "Tuntematon virhe").

Tämän Epicin tavoitteena on rakentaa Admin Studioon ja taustajärjestelmään **Template Copier & Validator** -algoritmi. Se suojelee Zero-Math Frontendia ehdottomasti: järjestelmä ei koskaan salli käyttäjän tallentaa epäyhteensopivaa ja puutteellista templaattia uuteen työnkulkuun.

---

## 2. Tiukka 3-Vaiheinen Kopiointilogiikka (The Fail-Fast Algorithm)

Tuleva kopiointi-API (esim. `/api/v2/studio/workflows/{id}/copy-layout`) toimii seuraavalla varmistetulla logiikalla:

### Vaihe 1: Kohdetyönkulun "Kapasiteetin" kartoitus (Target Capability Resolution)
Python-skripti käy läpi **Kohde-työnkulun** (johon yritetään kopioida) koko DAG-verkon (Dependency Graph, eli kaikki solmut). Se lukee tietokannasta, mitä Steppejä (askeleita) solmut ajavat, ja kokoaa Set-tietorakenteeseen (esim. `target_capabilities`) kaikki ne `prompt_block`-ID:t ja slugit, joita Kohde-työnkulku kykenee tuottamaan. Se tietää siis etukäteen 100 % varmuudella, mitä dataa tuleva ajo pystyy teoriassa puskemaan ulos.

### Vaihe 2: Lähdetemplaatin "Vaatimusten" purkaminen (Source Requirement Parsing)
Seuraavaksi algoritmi lukee **Lähde-työnkulun** (josta kopioidaan) UI-layoutit (esim. 3D-matriisit, tekstilaatikot ja piirakat). Se muodostaa toisen Set-rakenteen (esim. `source_requirements`), johon listataan kaikki ne matriisien ja laatikoiden ID:t, joita layout ehdottomasti vaatii pystyäkseen piirtymään onnistuneesti ruudulle (esim. vaatimus: `matrix_toulmin` ja `matrix_bloom`).

### Vaihe 3: Matemaattinen Ristikkäistarkistus (Subset Validation & Fail-Fast)
Lopuksi suoritetaan puhdas matemaattinen joukko-opillinen tarkistus Pythonilla:
`missing_blocks = source_requirements - target_capabilities`

* **✓ Jos `missing_blocks` on tyhjä:** Operaatio on 100 % turvallinen. Kaikki matriisit ja promptit, joita tulostustemplaatti haluaa piirtää, löytyvät varmasti uudenkin työnkulun aivoista. Templaatti kopioidaan ja tallennetaan onnistuneesti tietokantaan.
* **❌ Jos `missing_blocks` palauttaa yksikään listauksen:** Algoritmi noudattaa välitöntä Fail-Fast -sääntöä. Se hylkää kopioinnin pysyvästi (Status 400 Bad Request) ja palauttaa Admin Studioon selkokielisen inhimillisen virheilmoituksen: 
  > *"Kopiointi estetty. Kohdetyönkulusta puuttuu tekoälyn askeleita, joita templaatti vaatii: [Toulminin Argumentaatiomalli]. Lisää nämä askeleet DAGiin ennen kopiointia tai poista ne lähdetemplaatista."*

---

## 3. Tarkka Rajapintamäärittely (API Definition)

Ominaisuus rakennetaan täysin API-vetoisesti (API-First). Itse validointilogiikka elää pelkästään Python-taustajärjestelmässä, ja Admin Studio on täysin "tyhmä" käyttöliittymä, joka ainoastaan esittää FastAPI:n palauttaman tiedon.

### Päätepiste (Endpoint)
`POST /api/v2/studio/workflows/{target_workflow_id}/copy-layout`

### Pyyntö (Request Payload)
```json
{
  "source_workflow_id": "wfl_xyz12345"
}
```

### Onnistunut Vastaus (200 OK)
Jos Fail-Fast -tarkistus (Vaihe 3) läpäistään:
```json
{
  "status": "success",
  "message": "Layouts copied successfully to the target workflow."
}
```

### Virhetilanne (400 Bad Request - RFC 7807 Fail-Fast)
Jos työnkulusta puuttuu vaadittuja Prompt-lohkoja, järjestelmä hylkää tallennuksen ja palauttaa rikkaan virheilmoituksen, jonka Admin Studion `AppErrorBoundary` näyttää käyttäjälle:
```json
{
  "type": "https://quorum.ai/errors/layout-capability-mismatch",
  "title": "Template Capability Mismatch",
  "status": 400,
  "detail": "Kopiointi estetty. Kohdetyönkulusta puuttuu askeleita, joita templaatti vaatii.",
  "extensions": {
    "error_code": "LAYOUT_DEPENDENCY_ERROR",
    "missing_blocks": [
      "blk_371c7724eeba40218409b5a3697ac1d3", 
      "matrix_bloom"
    ]
  }
}
```

---

## 4. Toteutuksen Virstanpylväät (Milestones)

### Milestone 1: Backend API & Service Layer (Python)
* [ ] Koodaa yllä määritelty `/copy-layout` rajapinta FastAPI-reitittimeen (`backend_v2/api/studio.py`).
* [ ] Rakenna 3-vaiheinen DAG Subset Validation -algoritmi Business-kerrokseen (esim. `TemplateValidationService`).
* [ ] Toteuta tarkat RFC 7807 -yhteensopivat Error-luokat puuttuvien slugien kiinniotolle.

### Milestone 2: Admin Studion Käyttöliittymä (Flutter)
* [ ] Luo Admin Studioon yksinkertainen kutsu (`executionClient.copyLayout(...)`).
* [ ] Ota kiinni taustajärjestelmän palauttama 400 Bad Request ja pura `extensions.missing_blocks` lista.
* [ ] Tuota punainen Modali / Snackbar Admin Studioon, jossa käyttäjälle luetellaan puuttuvat askeleet selkokielisenä jotta hän tietää, mitä lohkoja DAGivaatiikin toimiakseen.
