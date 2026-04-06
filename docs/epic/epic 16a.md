### **OSA 1: Kyllä/Ei \-vaatimuslista**

**OHJE ANTIGRAVITYLLE:**

Olet järjestelmäarkkitehti ja koodari. Olemme toteuttamassa kahta suurta epic-kokonaisuutta: **Epic 14 (Dynaaminen Tulostusmoottori)** ja **Epic 13 (Output Management V3)**.

Käy läpi alla oleva vaatimuslista kohta kohdalta. Sinun on vastattava JOKAISEEN kohtaan tiukasti tällä täsmällisellä formaatilla (älä poikkea tästä):

* **Toteutettu:** \[Kyllä / Ei / Osittain\]  
* **Selite miten:** \[Jos Kyllä/Osittain: Kerro tarkasti tekninen toteutus, mitä tiedostoja/funktioita muokattiin ja miten. Jos Ei: Kerro mitä tiedostoja pitää muokata ja miten tämä tullaan ratkaisemaan.\]

**VAATIMUSLISTA:**

**Epic 14: Dynaaminen Tulostusmoottori & Eriyttäminen**

1. Onko DAG-moottori (tiedon keruu) ja kielellinen paketointi (tulostusmoottori) eriytetty rakenteellisesti toisistaan?  
2. Onko text\_consolidation\_hook irrotettu DAG-orkestraattorista (worker.py), ja ohjeistaako pää-Worker jatkossa työnsä päätöksestä kutsumalla asynkronisesti enqueue\_job("render\_profile\_job", default\_profile\_id)?  
3. Onko ExecutionRecord päivitetty tukemaan profiilikohtaista välimuistia (profile\_syntheses: dict\[str, RenderedSynthesisCache\]) globaalin teksti-ylikirjoittamisen sijaan?  
4. Reagoiko GET /render?profile\_id=X tyhjiin synteeseihin käynnistämällä taustalla uuden Tulostus-Workerin ajon ja palauttamalla UI:lle SSE/odotusindikoinnin?  
5. Mapataanko globaali synthesized\_markdown ja osiokohtaiset synthesis\_md aidosti läpi koko arkkitehtuurin (Pydantic \-\> BlueprintTransformer \-\> Frontendin Dart-mallit) bittiavaruuteen katoamisen sijaan?  
6. Pakotetaanko UI:n ja PDF:n dynaaminen Header-koontivaihe kunnioittamaan Output Profilen visible\_metadata \-asetuksia riippumatta järjestelmän oletuksista?  
7. Kuunteleeko Flutter Riverpod is\_synthesis\_pending \-tilaa ja renderöikö se Shimmer/Loading-laatikon niihin osioihin, joita tekoäly vasta generoi?  
8. Onko prompt\_compiler.py:n step\_1\_evidence\_quote \-validointia pehmennetty sallimaan vahva semanttinen perustelu (ja poistettu epävakaa "or lower the score immediately" \-oikoreitti)?

**Epic 13: Tulostuksen Hallinta V3**

9\. Onko OutputProfile \-malliin upotettu uusi SynthesisConfigDTO (joka hallinnoi pituusrajoitteita, monikielistä preamble\_textiä, maskausta, vientiformaatit ja tyhjien osioiden hallinnan)?

10\. Suodatetaanko tyhjät arvosteluosiot (omit\_empty\_sections) kokonaan pois kooditasolla ENNEN Synteesi-LLM:n kutsua token-hukan ja hallusinaatioiden estämiseksi?

11\. Anonymisoidaanko arkaluontoinen data (enable\_pii\_masking) lokaalisti algoritmisesti (esim. Microsoft Presidio) ENNEN tekstin lähettämistä Synteesi-LLM:lle?

12\. Puretaanko I18n-tekstit (kuten Preamble) ohjelmallisesti \_resolve\_i18n\_str() \-funktiolla lokaaliksi stringiksi, ja pakotetaanko järjestelmä englannin Fallback-kieleen ENNEN promptiin injektointia?

13\. Pakotetaanko Synteesi-LLM tuottamaan Structured Output \-formaattia (JSON schema: synthesized\_markdown, cited\_sources) XAI-inline-viitteitä varten?

14\. Laukaisevatko Output-laajennukset dynaamisesti tasan yhden (1) MCP-haun automaattisen työkaluinjektion avulla jo Step Execution \-vaiheessa EIKÄ vasta synteesissä (MAX\_TOOL\_CALLS\_PER\_STEP=1)?

15\. Tallentuuko EU AI Act \-auditoitava muistijälki (käytetty prompti, lähteet, vastaus) erilliseen alikokoelmaan tai GCS-bucketiin, jotta 1MB tietokantaraja (Firestore) ei ylity?

16\. Zero-Math UI: Pyöristääkö BFF-kerros (esim. Blueprint) numeeriset matriisigraafit pakotetusti absoluuttisiksi kokonaisluvuiksi (int(round(value, 0))) ennen Dartille siirtoa?

17\. XSS Sanitointi: Suorittaako BFF-kerros tiukan HTML/Markdown-sanitaation (esim. bleach-kirjastolla) ennen synteesin sijoittamista SDUI-pakettiin?

18\. Tukeeko PDF-generoija (pdf\_generator.py ja asynkroninen worker) Markdown-to-HTML \-muunnosta (Jinja2) siten, että saavutetaan täysi visuaalinen pariteetti UI:n kanssa?

19\. Tukevatko Flutterin OutputRenderer ja MarkdownStyleSheet rikkaan Markdownin (luettelot, taulukot) piirtämistä, ja yhdistyvätkö inline-viitteet saumattomasti lähdeluetteloon?

20\. Graceful Degradation: Jos Synteesi-LLM kaatuu API-virheeseen, palauttaako järjestelmä raakadatan \+ has\_warning: true \-lipun, jolloin Flutter piirtää automaattisesti \_buildWarningBannerin?

21\. Raporttipohjien vakiointi: Onko vanhat sekavat profiilit poistettu tietokannasta, seedattu tasan 5 vakioitua raporttipohjaa (patch/migraatioskriptillä), ja näkyvätkö näiden liiketoimintaperustelut UI:ssa?

22\. Arkkitehtuurisäännöt: Käytetäänkö LLM-operaatioissa kaikkialla deterministisesti LLMClient.from\_strategy() \-luokkaa (ei suoria SDK-kutsuja) ja noudatetaanko PII-raakadatassa täyttä lokituskieltoa virhetilanteissa?

### ---

**OSA 2: Kysely micro-milestone \-suunnitelman luomiseksi (Kopioi tämä Antigravitylle)**

Kun tekoäly on lukenut vaatimukset ja kartoittanut ohjelmiston tilanteen, syötä sille tämä prompti, jotta se laatii turvallisen toteutussuunnitelman: