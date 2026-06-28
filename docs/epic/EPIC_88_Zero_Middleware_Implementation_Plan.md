# 🚀 Arkkitehtuurin Suoraviivaistaminen (Zero Middleware Mandate)

## Tavoite
Käyttäjän toiveen mukaisesti tuhoamme kaiken V1-taaksepäinyhteensopivuuden ja välikerrosten ("duct tape") logiikan backendin raporttigeneraattorista. 
Tietokannan (execution trace) sisältämä alkuperäinen `AtomEvaluationItemDTO` (joka sisältää `reasoning_steps`, `override_reason` jne.) viedään **sellaisenaan, täysin muokkaamattomana** rajapinnan läpi suoraan Flutter-käyttöliittymään. Kaikki tulevaisuuden laajennukset tehdään vain lisäämällä Pydantic-kenttiä tähän yhteen oppikirjamalliin.

---

## ⚠️ User Review Required
Tämä on massiivinen arkkitehtuurimuutos, joka rikkoo vanhat tallennetut raportit, jos niitä ei ajeta uudelleen (mitä ei ohjeistuksen mukaan tarvitse tukea). 
Hyväksytkö, että poistamme kokonaan `EvidenceQuoteDTO`, `LevelQuotesDTO` ja `RowForensicsDTO` -mallit molemmista päistä (Python & Dart)?

---

## Proposed Changes

### 1. Backend DTO Modernization
**Tiedostot:** `backend_v2/models/v2_core.py` & `backend_v2/models/dtos/report.py`
- [DELETE] Poistetaan `EvidenceQuoteDTO`, `LevelQuotesDTO`, `RowForensicsDTO`.
- [NEW] Luodaan uusi, erittäin yksinkertainen kääre `ScorecardAtomDTO`, joka yhdistää tason tiedot ja suoran tietokantamallin:
```python
class ScorecardAtomDTO(V2CoreBase):
    atom_id: str
    level: int                   # Matriisin taso (esim. 0, 1, 2)
    level_name: str              # Tason nimi ("Taso 0")
    claim_label: str             # Ihmisluettava kriteeri
    evaluation: AtomEvaluationItemDTO | None  # SUORAAN tietokannasta (trace)
```
- [MODIFY] `MatrixScorecardRowDTO`: Korvataan `row_forensics` ja muut V1-kentät suoralla listalla: `evaluated_atoms: list[ScorecardAtomDTO]`.

### 2. Backend Middleware Gutting (Blueprint.py)
**Tiedosto:** `backend_v2/services/blueprint.py`
- [MODIFY] `_generate_v2_scorecard()`: Poistetaan KAIKKI legacy-koodi ja datan litteytys. Funktio vain poimii `evaluations`-lohkosta aidot `AtomEvaluationItemDTO`:t, paketoi ne `ScorecardAtomDTO`:hon (antaakseen niille matriisin kontekstin, eli mille tasolle ne kuuluivat) ja palauttaa ne sellaisenaan.

### 3. Flutter DTO & UI Modernization
**Tiedosto:** `client_app_v2/lib/features/execution/models/scorecard_dto.dart`
- [DELETE] Poistetaan Dartin vastineet vanhoille DTO:ille.
- [NEW] Luodaan Dart-versio `AtomEvaluationItemDto` ja `ScorecardAtomDto`.
- [MODIFY] `MatrixScorecardRowDto` käyttää nyt uutta listaa `evaluatedAtoms`.

**Tiedosto:** Käyttöliittymän renderöinti (todennäköisesti `client_app_v2/lib/features/execution/widgets/scorecard_matrix_row.dart` tai vastaava).
- [MODIFY] Päivitetään UI lukemaan uutta yksinkertaista listaa. Ja mikä parasta: UI:lla on nyt suora pääsy `override_reason`, `semantic_reasoning` yms. kenttiin!

### 4. PDF Parity (Raporttigeneraattorin päivitys & Output Parity)
**Tiedostot:** `backend_v2/services/pdf_generator.py` ja HTML-templacet
- [MODIFY] "PDF Parity and Hardening" -säännön mukaisesti PDF-generaattorin on käytettävä 100% samaa `ScorecardAtomDTO`-rakennetta kuin Flutterin.
- **Output Parity:** Ei riitä, että vain datamalli on sama. Varmistamme, että lopullinen visuaalinen *output* (miten väitteet, pisteet, perustelut ja kognitiiviset ohitukset esitetään) on täysin linjassa Flutter-käyttöliittymän ja PDF-tulosteen välillä. Molempien on esitettävä sama rikkaan datan informaatio käyttäjälle yhdenmukaisella tavalla.
- Varmistetaan, että PDF-renderöinti lukee uutta litteää listaa ja osaa näyttää kognitiivisen ohituksen tiedot täsmälleen samalla logiikalla kuin Flutter.

### 5. Asiantuntijahakujen Klusterointi (Epic 89 Foundation)
**Tiedosto:** `backend_v2/services/blueprint.py` (ja UI:n näyttölogiikka)
- [MODIFY] Vaikka varsinaista Epic 89:n ToolDispatcher-välimuistia ei vielä toteuteta, luomme sille perustan "UI-tasolla". Kun tekoäly tekee samalle matriisiriville useita lähes identtisiä hakuja (esim. eri tasojen arvioinnin yhteydessä), `blueprint.py` tunnistaa nämä ja niputtaa ne yhdeksi ainoaksi esitettäväksi asiantuntijalähteeksi.
- Tämä estää saman asian toistamisen (slopin) lopullisessa Flutter/PDF-raportissa ja takaa selkeän loppukäyttäjäkokemuksen tulevaisuuden dynaamisille MCP-työkaluille.

---

## Verification Plan
1. **Automated Tests**: Ajetaan `uv run python scripts/backend_audit_loop.py` ja korjataan rikkoutuvat testit (blueprint-testit rikkoutuvat, koska ne odottavat vanhoja DTO-malleja).
2. **Flutter Build**: Ajetaan `uv run python scripts/flutter_audit_loop.py client_app_v2` varmistamaan, ettei Flutter-koodi kaadu uusiin malleihin.
3. **Manual Validation**: Avataan Flutter-raporttinäkymä varmistaaksemme, että UI piirtää tiedot onnistuneesti uudesta "oppikirjamallista".
