# Epic 95: Verification Testing Pyramid & End-to-End Audit

## 1. Yhteenveto ja Tavoite (Objective)
Tämän Epicin tavoitteena on varmistaa järjestelmän vakaus ja arkkitehtuuristen tavoitteiden (Epicit 91.5, 92, 93, 94) täyttyminen kattavalla Testauspyramidilla. Tämä Epic ei luo uusia ominaisuuksia, vaan rakentaa System 2 -tason analyysin ja automatisoidut verifikaatioputket todistaakseen, että aiemmat "Big Bang" -uudistukset ovat tuotantovalmiita, noudattavat arkkitehtuurin ydinperiaatteita (Fail-Fast, SSOT, Strict Pydantic) ja näyttäytyvät loppukäyttäjille virheettömästi.

**TILA: VALMIS (Kaikki vaiheet testattu ja todennettu)**

## 2. Edeltävien Epicien Verifikaatiotavoitteet (System 2 Analysis)

Tämän Epicin puitteissa testataan, että alkuperäiset tavoitteet on saavutettu:

1. **Epic 91.5 (DTO Bridge):** 
   - Varmistetaan, että `ReportDataDto` on absoluuttinen SSOT (Single Source of Truth).
   - Testataan, että O(1) hajautustaulujen (`hydrated_references`) referentiaalinen eheys on aukoton (Zero-Tolerance: yksikään viittaus ei saa osoittaa olemattomaan ID:hen).
   - *Käyttäjäkokemus:* Mahdollistaa välittömän renderöinnin käyttöliittymässä ilman latausviiveitä tai "ikuisia spinnereitä" datan parsimisvaiheessa.

2. **Epic 92 (Enriched Atom Graph):** 
   - Varmistetaan determinististen syklinmurtajien (Cycle Breaker) toiminta.
   - Testataan tilakaskadit (`N_A`, `BLOCKED`) ja oikosulkulogiikka (Short-Circuiting).
   - Testataan `asyncio.TaskGroup`in virheensietokyky (ei deadlockeja backendissä, DLQ-reititys toimii).
   - *Käyttäjäkokemus:* Käyttäjä näkee tarkasti "Miksi" jokin ehto ohitettiin harmaalla (N/A) visuaalisella indikaattorilla, jossa lukee suoraan ohituksen syy.

3. **Epic 93 (SDUI Output Rendering Unification):** 
   - Varmistetaan "Sandwich Architecture" toimivuus (LLM:n tuottaman datan deterministinen sanitointi).
   - Testataan, että lopputulos noudattaa 100% ICU Markdown Pariteettia (Backend ei lähetä värikoodeja tai HTML:ää, vaan ainoastaan merkityssisältöä).
   - *Käyttäjäkokemus:* Raportti näyttää visuaalisesti identtiseltä niin Flutterin mobiilinäkymässä kuin generoidussa PDF-tiedostossakin.

4. **Epic 94 (Frontend SDUI Synchronization):** 
   - Varmistetaan, että Flutter käyttää puhtaasti Freezed-malleja (`disallowUnrecognizedKeys: true`).
   - Testataan Riverpod O(1) cachen suorituskyky ja `Isolate.run()` käyttö JSON-parsimisessa (Main Thread Jankin esto).
   - *Käyttäjäkokemus:* Sovellus ei jäädy (60fps säilyy) edes massiivisia, yli 1000 atomin raportteja avattaessa. Jos data on korruptoitunutta, UI renderöi siistin Error Boundary -kortin (ei Red Screen of Death -kaatumisia).

## 3. Testauspyramidin Vaiheistus (Implementation Phases)

### Vaihe A: Unit Tests (Perustan eheys & Fail-Fast)
* **Tavoite:** Verifioida backendin yksittäiset funktiot ja Pydantic-validaattorit täysin eristetysti.
* **Toteutus:** Polyfactoryn avulla luodaan mock-dataa (ei kovakoodattuja sanakirjoja). Testataan `validate_cognitive_vs_system_state` säännöt, ja referentiaalisen eheyden tarkistus (`enforce_referential_integrity`).
* **Arkkitehtuurisääntö:** Testien on pakko mennä läpi `backend_audit_loop.py` -skriptillä >90% coverage-vaatimuksella.

### Vaihe B: Integration Tests (Moottorin Determinismi)
* **Tavoite:** Varmistaa `TopologicalEvaluator`:n, syklinmurtajien ja `ResultProjector`:n yhteispeli.
* **Toteutus:** Rakennetaan tarkoituksella syklisiä graafeja ja puuttuvia riippuvuuksia, ja varmistetaan, että moottori pakottaa `SYSTEM_ERROR` ja `BLOCKED` tilat täsmälleen oikeille solmuille oikosulkusääntöjen mukaisesti.
* **Arkkitehtuurisääntö:** Strict Mocking Mandate for LLM. Raskaita kielimallikutsuja ei saa tehdä, vaan antureiden tulokset mockataan JSON-fixtureilla `backend_v2/llm/mock.py` -avulla.

### Vaihe C: Golden Master E2E & SDUI Validation
* **Tavoite:** Koestaa koko järjestelmän läpi kulkeva datavirta sisäänsyötöstä Flutter-komponenttien tiloihin asti.
* **Toteutus:** Ajetaan täysi putki staattista Golden Master -dataa vasten ja validoidaan, että tuotettu `ReportDataDto` on tavulleen identtinen odotetun lopputuloksen kanssa (Baseline Parity). Tässä testataan myös, että Frontendin Flutter-widgetit purevat oikein SDUI-payloadin vääntöihin.
* **Arkkitehtuurisääntö:** Zero-Tolerance. Yksikään testi ei saa palauttaa varoituksia (deprecation warnings) tai "lähes oikeita" tuloksia.

## 4. Definition of Done (DoD)
- [x] 1. Jokaiselle neljälle Epicille (91.5, 92, 93, 94) on olemassa automatisoitu testiputki.
- [x] 2. `backend_audit_loop.py` suoritetaan puhtaasti läpi ilman virheitä.
- [x] 3. Golden Master -testit tuottavat vakaan, muuttumattoman SDUI-payloadin (Huom: massiivisten aineistojen 2h LLM-timeout hyväksytään arkkitehtuurin suorituskykyrajana TDA Best-of-Three -mallilla).
- [x] 4. Järjestelmä on matemaattisesti todennettu valmiiksi ja käyttöliittymän SDUI/Freezed-pariteetti auditoitu puhtaaksi.
