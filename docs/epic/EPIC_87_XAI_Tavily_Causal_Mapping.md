# EPIC 87: XAI-Läpinäkyvyys (Tavily-perustelut & Syy-seuraus -mäppäys)

## 1. Yhteenveto & Tavoite (Executive Summary)

**Tavoite:** Rakentaa täydellinen syy-seuraussuhde (Causal Link) ulkoisten hakujen ja tekoälyn antamien pisteiden välille hyödyntäen mahdollisimman paljon puhdasta, determinististä Python-koodia. Datan prosessointi keskitetään `blueprint.py` -tiedostoon (`ReportDataDTO`), jotta mikään esityskerros (PDF, Flutter, REST API) ei joudu laskemaan tai päättelemään mitään itse.

Tämä poistaa LLM:n hallusinaatioriskin viittauksissa ("Python-driven ID Mapping") ja rajoittaa työkalujen perustelujen pituudet ankarasti.

---

## 2. Toteutuksen Vaiheet (Implementation Tiers)

### 2.1 Hakujen "Pakotettu Perustelu" (Python Pydantic)
*   **Tiedostot:** `backend_v2/models/domain/mcp.py` & `v2_core.py`
*   **Toimenpiteet:**
    *   Lisätään `CitationExtractionItemDTO` -luokkaan tiukka pituusrajoitus:
        `reasoning: str = Field(max_length=150, description="Max 1 short sentence. Briefly explain WHY you are verifying this claim.")`
    *   Lisätään `MCPAuditTrace` -luokkaan `reasoning`-kenttä.
    *   Päivitetään `mcp_tool_loop.py`:n prompti pakottamaan max 100 merkin lyhyt lause.

### 2.2 Syy-Seuraussuhteen kerääminen (Python ID-Mapping)
*   **Tiedostot:** `backend_v2/services/mcp/mcp_tool_loop.py` & `backend_v2/models/domain/matrix.py`
*   **Toimenpiteet (Phase 2 injektio):**
    *   Kun Python injektoi Tavily-tulokset takaisin LLM:lle (Phase 2), Python generoi ja syöttää jokaiselle tulokselle yksilöllisen tunnisteen (Trace ID). Esimerkiksi: `<search_result id="tavily_1a2b">`
    *   Lisätään matriisin arviointirivien DTO-malliin uusi kenttä LLM:ää varten:
        `used_evidence_ids: list[str] = Field(default_factory=list, description="List of exact <search_result id> strings you relied upon for this specific row.")`

### 2.3 Datan esipureskelu (Blueprint Transformer / Zero-Math Template)
Kriittinen sääntö: **Esityskerros on tyhmä**. Kaikki ristiinlinkitys lasketaan valmiiksi `ReportDataDTO`:hon (PDF/Flutter DTO), kun työnkulku päättyy.

*   **Tiedostot:** `backend_v2/models/dtos/pdf_report.py` & `backend_v2/services/blueprint.py`
*   **Toimenpiteet:**
    *   Laajennetaan `MCPAuditTraceDTO` uudella kentällä:
        `impacted_axis_names: list[str] = Field(default_factory=list, description="List of axis names this search influenced.")`
    *   Kun `blueprint.py` kokoaa lopullista `ReportDataDTO`:ta matriisien ja audit-lokien pohjalta, se suorittaa **käänteisen haun (Reverse Lookup) Pythonissa**.
    *   Logiikka: Käy läpi jokainen matriisin rivi ja sen `used_evidence_ids`. Etsi vastaava `MCPAuditTrace` raporttiin menevästä lokista. Lisää matriisin rivin nimi (`axis.name`) kyseisen Tracen `impacted_axis_names` -listaan.

### 2.4 Esittäminen ihmiselle (Jinja2 & Flutter)
Koska data on valmiiksi pureskeltu `ReportDataDTO`:ssa, esityskerrokset vain tulostavat valmiit listat.
*   **Tiedostot:** `backend_v2/templates/report_template.jinja2`
*   **Toimenpiteet:**
    *   Tulostetaan audit-lokissa (ja vastaavasti Flutterissa) suoraan uusi valmis lista:
        `Vaikutus arviointiin: {{ trace.impacted_axis_names | join(', ') if trace.impacted_axis_names else 'Haku vahvisti tiedon oikeaksi' }}`

---

## 3. Onnistumisen Kriteerit & Verification Plan
1. **Unit Tests:** Päivitetään mock-oliot sisältämään `reasoning`, `used_evidence_ids` ja `impacted_axis_names`.
2. **Blueprint Transformer Test:** Varmistetaan, että `blueprint.py` osaa onnistuneesti mapata `used_evidence_ids` takaisin traceihin ja populoida `impacted_axis_names` listat oikein `ReportDataDTO`:ssa.
3. **End-to-End Pydantic Test:** Varmistetaan, että kaikki DTO-validoinnit menevät läpi Backend Audit Loopissa (`scripts/backend_audit_loop.py .`).
