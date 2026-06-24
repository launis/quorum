# EPIC 86: Structured BARS Forensic Evidence Quotes (Ryhmitelty Todistusaineisto)

## 1. Yhteenveto & Tavoite (Executive Summary)
EPIC 70 lisäsi mahdollisuuden näyttää matriisien arviointiriveillä alkuperäiset lainaukset (`quotes_list`), jotka johtivat kriteerien täyttymiseen. Tällä hetkellä nämä lainaukset kuitenkin tallennetaan ja välitetään yhtenä tasaisena listana (`list[str]`), jolloin tieto siitä, minkä tason (esim. Taso 4 vs Taso 2) kriteerin kukin sitaatti täytti, menetetään.

**Tämän Epicin tavoite:**
Uudistaa lainausten tallennus- ja esitysrakenne siten, että lainaukset ryhmitellään ja esitetään rakenteellisesti tasoittain (Option C). Tämä säilyttää tarkan todistusaineiston (*Forensic Sovereignty*) ja tekee taulukosta välittömästi luettavan ilman merkkijonojen purkkakoodattuja parsintoja.

---

## 2. Arkkitehtuurinen Konsepti (Structured Design)

Uudistus vaatii datamallien päivittämistä siten, että jokainen lainaus on sidottu tiettyyn tasoon (pisteeseen) ja tason nimeen.

### DTO-tason muutokset (Backend & Frontend)
Nykyinen `list[str]` korvataan rakenteellisella DTO:lla:

```python
# backend_v2/models/dtos/lightweight_matrix.py tai v2_core.py
class LevelQuotesDTO(BaseModel):
    level: int
    level_name: str  # Localized name at evaluation time
    quotes: list[str]
```

Päivitetään `MatrixScorecardRowDTO` (sekä backendillä että frontendin `ScorecardRowDto` Freezed-mallissa):
```python
# Ennen: quotes_list: list[str]
# Jälkeen:
quotes_list: list[LevelQuotesDTO]
```

### Konseptuaalinen Lopputulos (UI Rendering)
Kun lainaukset ryhmitellään, `AtomMatrixTableWidget` renderöi ne sisäkkäisenä listana:

* **Taso 4 - Tunnustava:**
  * *"Muutos 2017:n potentiaalista 2023:n kriisiin on peruuttamaton."*
* **Taso 2 - Heikko:**
  * *"Luonnon kantokyvyn rajat eivät ole vain rajoite..."*
  * *"Tämä syntyy siitä, että Luonnon kantokyky murenee..."*

---

## 3. Toteutuksen Vaiheet (Implementation Tiers)

### Vaihe 1: Backend DTO-määritykset
* Luodaan uusi `LevelQuotesDTO` Python-luokka.
* Päivitetään `MatrixScorecardRowDTO` käyttämään uutta rakennetta.

### Vaihe 2: Scoring Hook (`scoring.py`)
* Muutetaan `matrix_scoring_hook` ryhmittelemään osumat tasoittain.
* Kerätään sitaatit per `s_val` (level) ja haetaan tason lokalisoitu nimi (`scale.name`) arvioinnin aikana.
* Tallennetaan `content_payload["atom_quotes"]` -rakenteeseen lista `LevelQuotesDTO`-objekteja litteän merkkijonolistan sijaan.

### Vaihe 3: Blueprint Transformer (`blueprint.py`)
* Päivitetään `BlueprintTransformer` siirtämään ryhmitelty rakenne sellaisenaan eteenpäin.
* Varmistetaan, että merkkijonojen puhdistus ja pituusrajoitukset (katkaisu) tehdään jokaiselle sitaatille yksitellen ilman, että ryhmittelyrakenne rikkoutuu.

### Vaihe 4: Flutter DTO & Code Generation
* Päivitetään `ScorecardRowDto` (`client_app_v2/lib/features/execution/models/scorecard_dto.dart`) vastaamaan uutta backend-rakennetta.
* Suoritetaan `flutter_audit_loop.py client_app_v2 --build` Freezed-tiedostojen regeneroimiseksi.

### Vaihe 5: Flutter UI Renderöinti (`atom_matrix_table_widget.dart`)
* Päivitetään `AtomMatrixTableWidget` käsittelemään `List<LevelQuotesDto>`.
* Renderöidään kukin tasoryhmä lihavoidulla otsikolla ja sen alla olevat sitaatit sisennetyillä bullet-merkeillä.

---

## 4. Onnistumisen Kriteerit
- [ ] Pydantic-validointi menee läpi sekä scoring- että synthesis-vaiheissa.
- [ ] Flutter-sovellus kääntyy ja parsii JSON-datan virheettömästi ilman tyyppiristiriitoja.
- [ ] Taulukkonäkymä ryhmittelee sitaatit selkeästi tasoittain, luoden suoran visuaalisen linkin *Tasojakauma*-sarakkeen ja *Lainaukset*-sarakkeen välille.
