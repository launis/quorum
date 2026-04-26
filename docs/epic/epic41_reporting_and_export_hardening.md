# Epic 41: Unified Reporting and Export Hardening (Zero-Compromise)

## 1. Yhteenveto (Executive Summary)
**Tavoite:** Yhtenäistää raporttien tulostus- ja vientiarkkitehtuuri vastaamaan Phase 9 -sääntöjä (Code is Truth, Fail-Fast). XAI-laajennusten (kuten Valmennusvinkit, Korjaustoimenpiteet ja Sävy, jotka näkyvät onnistuneesti Flutter-käyttöliittymässä) on renderöidyttävä saumattomasti ja yhteneväisesti osana viimeistä tulostettavaa raporttia, ilman tarvetta erillisiin lokaaleihin debug-skripteihin. Samalla korjataan Weasyprintin aiheuttama infrastruktuurin hauraus Windows-ympäristöissä tuomalla natiivi HTML-tuki.

## 2. Ongelman Kuvaus
1. **Datan Integraatio:** Uusi `StrictMatrixPayload` -rakenne, joka sisältää kriittisen syväanalyysin (XAI) tiedot, näkyy jo kauniisti Flutter-asiakasohjelmassa. Tätä dataa ei kuitenkaan tulosteta vastaavalla painoarvolla eikä samassa formaatissa nykyiseen renderöityyn loppuraporttiin. Asiakas toivoo raportin loppuun visuaalisesti samanlaista koontia.
2. **Weasyprint-hauraus (Windows GTK3):** Backendin nykyinen PDF-generointi (`PdfReportService`) on riippuvainen raskaasta Weasyprint-kirjastosta. Tämä kaatuu lokaalisti ajettaessa Windows-ympäristössä GTK3-kirjastojen puuttumiseen, ellet aja palvelua koko ajan Docker-kontissa. Tämä rikkoo Fail-Fast -periaatetta vaikeuttamalla paikallista kehitystä ja auditointia.

## 3. Ratkaisusuunnitelma ja Laajempi Scope

### 3.1 XAI-Datan Täydellinen Pariteetti (Flutter vs. Raportti)
- **Tavoite:** Loppuraportti (PDF/HTML) heijastaa 100% tarkkuudella Flutter-käyttöliittymän SDUI-näyttöä.
- **Toteutus:** Päivitetään Jinja2-mallipohjat (`report_template.jinja2`) purkamaan Phase 9 XAI-metadatan suoraan `ReportDataDTO`:sta. Matriisien perustelut, korjaustoimenpiteet ja emotionaalinen sävy tulostetaan "kauniina raporttina" dokumentin loppuun samalla visuaalisella hierarkialla kuin käyttöliittymän korteissa/komponenteissa.

### 3.2 "HTML First" -Taktinen Varmistus (Zero-Compromise Export)
- **Tavoite:** Taata täydellinen renderöinti ja tulostettavuus paikallisista kehitysympäristöistä ja käyttöjärjestelmistä (Windows) riippumatta.
- **Toteutus:** Tuodaan backendin `/render`-päätepisteeseen suora tuki formaatille `format=html`.
- Backend palauttaa tiukan ja itsenäisen HTML-tiedoston (sisältäen CSS-tyylit), joka voidaan ladata ja avata missä tahansa selaimessa. HTML-dokumentti on itsessään täydellinen raportti, joka voidaan tulostaa PDF:ksi selaimen omalla tulostustoiminnolla.
- Tämä ratkaisee Weasyprintin Windows-ongelman täysin: lokaalisti kehittäjä voi hakea `.html`-raportin yhdellä API-kutsulla ja välttää C-kirjastojen aiheuttamat kaatumiset. PDF pysyy tuettuna Dockerin sisällä.

### 3.3 Ei Erillisiä "Purkka-skriptejä"
- Hylätään tarve erillisille `luo_raportti.py` tai muille lokaaleille CLI-työkaluille loppukäyttäjän raportoinnissa. Kuten linjasit, datan on tultava järjestelmän omista sisäisistä rajapinnoista.
- Raportin generointi säilytetään yksinomaan ydin-API:n ja `PdfReportService`:n / uuden `HtmlReportService`:n vastuulla. 

### 3.4 Kattavan Koontitaulukon (Summary Table) Palautus
- **Tavoite:** Palauttaa `lue_tulokset.py` -skriptin kaltainen kattava matriisikoontitaulukko (Matriisi | Pisteet | Tasot T1-T6 | Lyhyt Perustelu | Skaalattu Arvo) osaksi virallista vakioraporttia.
- **Toteutus:** Vaikka aikaisempi taulukkototeutus on kadonnut Phase 9 migraatiossa, luodaan täysin uusi, oma ja visuaalisesti upea taulukko-komponentti Jinja-malleihin (`report_template.jinja2` ja `dashboard_pdf.html`). Tämä taulukko sijoitetaan raportin ja näyttötulosteen loppuun "Yhteenvetona"-osioon.
- Taulukko noutaa datansa suoraan `ReportDataDTO`:n säännösteltyjen matriisi-avaimien (`StrictMatrixPayload`) kautta, joten se on aina täydellisesti synkronissa muun raportin ja käyttöliittymän kanssa.

## 4. Seuraavat Askeleet (Toteutusvaiheet)
1. **Jinja2-Päivitys:** Refaktoroidaan `backend_v2/templates/report_template.jinja2` tukemaan syvästi sisäkkäistä Phase 9 XAI-dataa.
2. **HTML-reititys:** Lisätään `execution.py`:hin logiikka, joka palauttaa raa'an renderöidyn HTML:n (`format=html`).
3. **Auditointi:** Suoritetaan laatuporttitestaus.
