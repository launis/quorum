### **OSA 2: Kysely micro-milestone \-suunnitelman luomiseksi**

**OHJE ANTIGRAVITYLLE / IMPLEMENTOINTISUUNNITELMA:**

Tavoitteenamme on implementoida kaikki yllä käsitellyt Epic 14 ja Epic 13 ominaisuudet koodikantaamme. Muutos on massiivinen ja koskee järjestelmää tietokannasta käyttöliittymään, joten emme missään nimessä voi koodata tätä yhdessä tai kahdessa suuressa pätkässä, sillä se rikkoisi järjestelmän.

Tee minulle yksityiskohtainen ja hienojakoinen **Micro-Milestone \-implementointisuunnitelma**. Pilko yllä olevat 22 vaatimusta pieniin osiin, joita voimme käydä läpi ja koodata yksi (1) Milestone kerrallaan (esim. yhden Pull Requestin koossa).

**Suunnitelman säännöt:**

1. **Looginen kerrosjärjestys (Bottom-up):**  
   * **Aloita Data-kerroksesta:** DB Schemat (ExecutionRecord), Pydantic DTO:t (SynthesisConfigDTO) ja Seed-datan / tietokannan päivitykset (patch\_epic13.py).  
   * **Siirry Core-logiikkaan:** DAG Workerin eriyttäminen, uuden Render-Workerin pohjustus ja pisteytyksen validointikorjaukset.  
   * **Rakenna Hookit ja Turvallisuus:** Uusi TextConsolidationHook, PII Maskaus (Presidio), I18n purku, Audit Trail \-tallennusmekanismit ja Extension-driven MCP (Step Execution).  
   * **Rakenna API / BFF \-kerros:** Zero-Math graafien pyöristykset, Bleach XSS-sanitointi, DTO pariteetin reititys UI:lle, Headerien asettelu.  
   * **Lopuksi Frontend (Flutter):** OutputRenderer, Riverpod staten kuuntelu (Shimmer), Preamble-perustelut, PDF visuaalinen pariteetti ja varoitusbannerit.  
2. **Jokaisen Milestonen (esim. M1, M2, M3... M10) esitystapa:**  
   * **Nimi ja tavoite:** (esim. "M1: Data-kerros \- SynthesisConfigDTO ja OutputProfile")  
   * **Kohdetiedostot:** Mitä kooditiedostoja tässä nimenomaisessa askeleessa tullaan muokkaamaan.  
   * **Toteutettavat vaatimukset:** (Viittaus ylemmän listan numeroihin, esim. "Toteuttaa kohdat 3 ja 9")  
   * **Definition of Done (DoD) & Testaus:** Miten juuri tämän pienen osan onnistuminen testataan lokaalisti tai todennetaan (esim. testiskriptillä tai mock-datalla tietokannassa) ennen siirtymistä seuraavaan vaiheeseen. Uusi vaihe ei saa rikkoa master-haaraa.

Luo tämä suunnitelma nyt. Kun olet generoinut suunnitelman, kysy minulta: *"Hyväksytkö suunnitelman? Aloitetaanko koodaamaan Milestonea 1?"*

---

