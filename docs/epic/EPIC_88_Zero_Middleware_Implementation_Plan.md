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

### 1. Backend DTO Modernization (Zero Middleware & DTO Firewall)
**Tiedostot:** `backend_v2/models/v2_core.py` & `backend_v2/models/dtos/report.py`
- [ ] [DELETE] Poistetaan `EvidenceQuoteDTO`, `LevelQuotesDTO`, `RowForensicsDTO`.
- [ ] [NEW] Luodaan uusi kääre `ScorecardAtomDTO`. **Tietoturva ja Trace Bloat -falsifiointi huomioitu:** Emme upota koko tietokantaobjektia raakana sokeasti rajapintaan, vaan noudatamme Explicit Inclusion (DTO Firewall) -periaatetta. Kopioimme vain presentation-kerrokselle turvalliset kentät:
```python
class ScorecardAtomDTO(V2CoreBase):
    atom_id: str
    level: int                   
    level_name: str              
    claim_label: str             
    # DTO Firewall: Explicit Inclusion of presentation fields only!
    extracted_facts: dict[str, str | None]
    exact_quotes: list[str]
    internal_logic_en: ReasoningStepDTO
    status: str | None
    semantic_reasoning: str
    contextual_override: bool
    structural_location: str
```
- Näin varmistamme, että jos `AtomEvaluationItemDTO`:hon lisätään myöhemmin massiivisia sisäisiä lokeja tai arkaluontoisia prompteja, ne jäävät automaattisesti palomuurin taakse eivätkä kaada mobiililaitteita (OOM) tai vuoda julkiseen verkkoon.
- [ ] [MODIFY] `MatrixScorecardRowDTO`: Korvataan V1-kentät suoralla listalla: `evaluated_atoms: list[ScorecardAtomDTO]`.

### 2. Backend Middleware Gutting & Explicit Skipped States (Blueprint.py)
**Tiedosto:** `backend_v2/services/blueprint.py`
- [ ] [MODIFY] `_generate_v2_scorecard()`: Poistetaan KAIKKI legacy-koodi ja datan litteytys. Funktio vain poimii `evaluations`-lohkosta aidot `AtomEvaluationItemDTO`:t, paketoi ne `ScorecardAtomDTO`:hon.
- [ ] **Explicit Skipped States:** Jos arviointi on short-circuitattu (esim. Taso 0 epäonnistui, jolloin Tasoja 1 ja 2 ei löydy tracesta), `blueprint.py` päättelee matriisin skeemasta puuttuvat tasot ja palauttaa niille `ScorecardAtomDTO`:n, jossa `evaluation = None`. Tämä poistaa kaiken arvailun renderöintimoottoreilta!

### 3. Flutter DTO & UI Modernization
**Tiedosto:** `client_app_v2/lib/features/execution/models/scorecard_dto.dart`
- [ ] [DELETE] Poistetaan Dartin vastineet vanhoille DTO:ille.
- [ ] [NEW] Luodaan Dart-versio `AtomEvaluationItemDto` ja `ScorecardAtomDto`.
- [ ] [MODIFY] `MatrixScorecardRowDto` käyttää nyt uutta litteää listaa `evaluatedAtoms`. 
- [ ] **Smart Getter:** Lisätään DTO:hon apufunktio (esim. `Map<int, List<ScorecardAtomDto>> get atomsByLevel`), joka ryhmittelee litteän siirtoprotokollalistan lennossa UI:n tarvitsemaan hierarkiaan.

**Tiedosto:** Käyttöliittymän renderöinti (todennäköisesti `client_app_v2/lib/features/execution/widgets/scorecard_matrix_row.dart` tai vastaava).
- [ ] [MODIFY] Päivitetään UI piirtämään asiat suoraan uuden litteän listan (tai sen smart getterin) pohjalta. Jos `evaluation == null`, piirretään "Ei arvioitu / Skipped" -tila.

### 4. PDF Parity (Raporttigeneraattorin päivitys & Output Parity)
**Tiedostot:** `backend_v2/services/pdf_generator.py` ja HTML-templacet
- [ ] [MODIFY] "PDF Parity and Hardening" -säännön mukaisesti PDF-generaattorin on käytettävä 100% samaa `ScorecardAtomDTO`-rakennetta kuin Flutterin. 
- [ ] Se käyttää samaa litteää listaa ja ryhmittelee sen Python-päässä identtisellä logiikalla kuin Flutterin smart getter. 
- [ ] **Parity Guarantee:** Koska backend lähettää ohitetuille tasoille eksplisiittisen `evaluation = None`, sekä Flutter että PDF piirtävät "Skipped"-tilat täsmälleen samalla tavalla ilman, että kummankaan renderöijän tarvitsee yrittää arvata dataa. Tämä poistaa Flutter-PDF-ristiriidan täysin.

### 5. Asiantuntijahakujen Klusterointi (Epic 89 Foundation & Purity Paradox Resolution)
**Tiedostot:** `backend_v2/models/dtos/report.py` & `backend_v2/services/blueprint.py`
- **Falsifiointi huomioitu:** Datan suodattaminen tai muokkaaminen itse `AtomEvaluationItemDTO`:n sisällä rikkoisi välittömästi "Zero Middleware" -säännön ja tuhoaisi audit-trailin eheyden.
- [ ] [NEW/MODIFY] Ratkaisemme klusteroinnin nostamalla sen abstraktiotasossa ylemmäs! `MatrixScorecardRowDTO`:hon lisätään uusi kenttä `clustered_row_sources: list[MCPAuditTrace]`.
- [ ] Kun `blueprint.py` kokoaa riviä, se iteroi rivin kaikkien atomien `used_evidence_ids`-viittaukset, hakee niitä vastaavat auditoinnit, ja tallentaa niistä **uniikit** haut tähän uuteen `clustered_row_sources`-listaan.
- [ ] Näin itse `AtomEvaluationItemDTO` pysyy 100 % pyhänä ja koskemattomana (täysin raakana tietokannasta), mutta Flutter/PDF-käyttöliittymä saa siistin, valmiiksi klusteroidun listan asiantuntijahauista suoraan rivitasolla esitettäväksi!

---

## Verification Plan
1. **Automated Tests**: Ajetaan `uv run python scripts/backend_audit_loop.py` ja korjataan rikkoutuvat testit (blueprint-testit rikkoutuvat, koska ne odottavat vanhoja DTO-malleja).
2. **Flutter Build**: Ajetaan `uv run python scripts/flutter_audit_loop.py client_app_v2` varmistamaan, ettei Flutter-koodi kaadu uusiin malleihin.
3. **Manual Validation**: Avataan Flutter-raporttinäkymä varmistaaksemme, että UI piirtää tiedot onnistuneesti uudesta "oppikirjamallista".
