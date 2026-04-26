# Phase 2: Jinja Templates & XAI Summary Table

## Tavoite
Saattaa visuaaliset Jinja2-mallit (`report_template.jinja2` ja tarvittaessa `dashboard_pdf.html`) täydellisesti synkroniin Phase 9 -infrastruktuurin ja käyttöliittymän kanssa. Tämä tarkoittaa XAI-metadatan (Valmennusvinkit, Sävy, Korjaustoimenpiteet) näyttämistä suoraan raporteissa ja `lue_tulokset.py`:stä inspiraationsa saaneen kattavan Matriisikoontitaulukon (Summary Table) palauttamista.

## Architectural Invariants (Must Follow)
- **Rule 1: No Naked Dicts:** Jinja-templaateissa tulee käyttää vain `ReportDataDTO`-mallien tiukkoja Pydantic-attribuutteja, EI sokeaa dict-navigaatiota (ei `.get("extensions", {})` ilman takuutyyppiä).
- **Rule 2: Surgical Precision Edits:** Templaatteja muokatessa älä riko nykyistä 3D-visuaaliratkaisua. Pidä CSS yhtenäisenä ja skaalautuvana (PDF/HTML parity).

## Target Files (Modify)
1. `c:\src\quorum\backend_v2\templates\report_template.jinja2`
   - **XAI Laajennukset:** Renderöi `ReportDataDTO.grouped_extensions` vastaamaan visuaalisesti Flutterin UI-korteja (Accordion-tyyppiset osiot Valmennusvinkeille, Korjaustoimenpiteille, Sävy-analyysille).
   - **Summary Table (Koontitaulukko):** Luo raportin viimeiseksi osioksi "Yhteenveto / Matrix Summary" -kohta. Sen tulee sisältää puhdas ja selkeä HTML-taulukko, joka iteroi kaikki matriisitulokset (vastaavasti kuin `lue_tulokset.py` terminalissa: Matriisi, Pisteet, T1-T6 skaalat, Perustelut ja Skaalattu %-arvo).

## Context Files (Read-Only)
- `c:\src\quorum\backend_v2\models\v2_core.py` (ReportDataDTO:n kenttien varmentaminen)
- `c:\src\quorum\lue_tulokset.py` (Inspiraatio matriisien purkamisesta ja taulukoinnista)

## Verification & Quality Gate Plan
- Generoi testi-HTML `/render?format=html` -rajapinnan kautta postmanilla tai API:n testiskriptillä `backend_audit_loop.py` jälkeen.
- Varmista selaimella, että XAI-tiedot renderöityvät kauniisti (visuaaliset varoitusvärit/reunukset, samankaltaiset kuin UI:ssa).
- Varmista, että "Summary Table" tulostuu koko sivun leveydellä, sarakkeet tasattuina ja selkeällä tipografialla raportin lopussa.
