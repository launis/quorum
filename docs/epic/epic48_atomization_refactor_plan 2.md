## **Epic 48: Atomisaation Purku, Teoreettinen Ankkurointi ja Deterministinen Orkestrointi (SSOT)**

Tämä Epic korvaa V1-aikakauden epädeterministisen ja hallusinaatioalttiin "Deep Atomization" \-mallin 100 % deterministisellä ja akateemisesti ankkuroidulla **Test-Driven Assertion (TDA)** \-arkkitehtuurilla ("Single Source of Truth"). Koko järjestelmä siirtyy sumeasta arvailusta täsmälliseen, matemaattiseen ja todistettavaan validointiin. Kaikki taaksepäin yhteensopivuutta vaativa legacy-koodi tuhotaan armotta.

### **Vaihe 1: Arkkitehtuurin Siivous ja SSOT-Tietokantamalli (Dead Code Removal)**

Järjestelmä puhdistetaan dynaamisista atomisaatio-kutsuista. Infrastruktuuri pystytetään välittömästi ilman LLM-latensseja.

1. **atomization\_cache.json tuhoaminen:**  
   * Tiedosto backend\_v2/seed/atomization\_cache.json poistetaan kokonaan repositoryn historiasta.  
2. **PromptAtomizer-luokan neutralointi (backend\_v2/services/orchestrator/atomizer.py):**  
   * Poistetaan LLM-API-kutsut kokonaan. Logiikka korvataan puhtaalla O(1)-mäppäyksellä, joka lukee asiantuntijoiden tietokantaan asettamat TDA-väitteet ja luo niille efemeraaliset (tilapäiset) ajonaikaiset tunnisteet (esim. tda\_0, tda\_1). V1-aikaiset MD5-tiivisteet ovat kiellettyjä hallusinaatioriskien ja hitauden vuoksi.  
3. **Tietokantaskeeman ja Pydantic-mallien muutos (models/v2\_core.py):**  
   * Tuhotaan vanha micro\_atoms \-kenttä kokonaan kaikista malleista.  
   * Säilytetään matriisikohtainen ai\_description (str), mutta sen rooli on jatkossa pelkkä XML-System Prompt / Agentin Persoona.  
   * Luodaan uusi alimalli TDAAssertion:  
     Python  
     class TDAAssertion(BaseModel):  
         description: str  \# Varsinainen kriteeri (esim. "Teksti esittää numeerisen tavoitteen")  
         inverse\_evidence: bool \= False  \# Kääntää lainauksen vaatimuksen

   * Muutetaan solun Claim-malli muotoon: tda\_assertions: list\[TDAAssertion\] \= Field(min\_length=1). Tämä on järjestelmän uusi SSOT.  
   * **Pakottava sääntö (strict\_pydantic\_v2\_rust):** Malleihin pakotetaan model\_config \= ConfigDict(extra='forbid', strict=True). Ei Optional-purkkapaikkoja tai kikkailuja vanhan datan tukemiseksi.  
4. **run\_seed.py kevennys ja nollaus:**  
   * Poistetaan LLM-clientin ja välimuistin alustukset Seederistä. Seeder lataa kantaan uuden Pydantic-mallin mukaista dataa seed\_data.json \-tiedostosta sekunneissa ilman verkkokutsuja.

### **Vaihe 2: Teoreettinen Ankkurointi ja Prompt Compilerin Äly**

Kaikki kriteerit irrotetaan LLM:n "musta tuntuu" \-logiikasta ja ankkuroidaan suoraan akateemisiin teorioihin.

1. **Uusi seed\_data.json ja Positivity Mandate:**  
   * Teoriat puretaan atomaarisiksi, yksittäisiksi TDA-lauseiksi ja tallennetaan staattisesti seed\_data.json \-tiedostoon listamuodossa.  
2. **Matriisitason PromptBlock.ai\_description (System Prompt):**  
   * Toimii yksinomaan englanninkielisenä System Promptina. Se on täysin staattinen "Prompt Caching" \-hyötyjen maksimoimiseksi. Dynaaminen lähdeteksti injektoidaan User-viestin \<source\_text\>-blokkiin.  
3. **Käänteisen Logiikan Injektio (PromptCompiler):**  
   * PromptCompiler (backend\_v2/services/orchestrator/prompt\_compiler.py) lukee inverse\_evidence-lipun TDA-kohtaisesti.  
   * Jos se on tosi, compiler injektoi suoraan LLM:n promptiin ohjeen säännön tulkitsemiseksi: *"This is an inverse rule. If successful (True \= no issues found), return EMPTY quotes \[\]. If violation found (False), you MUST quote the exact violation."*

### **Vaihe 3: Hallusinaatiosuoja ja Validointi (Industrial Grade Resilience)**

1. **DTO-rakenteiden päivitys (XAI & Evidence):**  
   * Lisätään LLM:n tulos-DTO-malleihin pakolliset kentät evidence\_quotes: list\[str\] ja reasoning\_trace: str. LLM:n on aina ensin tuotettava reasoning\_trace ennen is\_true-päätöstä (Chain of Thought).  
   * Lisätään extensions: dict\[str, str\] \= Field(default\_factory=dict), jotta dynaamiset valmennuskentät eivät kaada Pydanticin strict-tilaa.  
2. **Käänteiset säännöt (inverse\_evidence) ja Nollasääntö:**  
   * **Normaali hyve (inverse\_evidence \== False):** is\_true \== True vaatii AINA suoran lainauksen (len(quotes) \> 0). is\_true \== False vaatii tyhjän lainauksen \[\].  
   * **Negatiivinen pahe (inverse\_evidence \== True):** is\_true \== True (Hyve \= ei löydy) pakottaa tyhjän listan \[\]. is\_true \== False (Löytyi virhe) pakottaa löytämään tarkan lainauksen todisteeksi.  
3. **RapidFuzz Python-validointi (Fail-Fast):**  
   * Luodaan Pydantic @model\_validator(mode='after') tulosmallille.  
   * **Kadonnut Konteksti:** Ensimmäinen koodirivi on: assert info.context and 'source\_text' in info.context. LLMTaskExecutor pakotetaan injektoimaan tämä: model\_validate(data, context={'source\_text': chunk\_text}).  
   * **Normalisointi (OCR-suoja):** Sekä alkuperäinen source\_text että LLM:n lainaukset normalisoidaan ennen vertailua: .strip().replace('\\n', ' ').lower() ja tuplavälilyönnit poistetaan re.sub(r'\\s+', ' ', text).  
   * **Fuzzy Matching:** Käytetään RapidFuzz-kirjastoa `fuzz.partial_ratio > 95.0`.  
   * **Huijauksen Esto:** Validaattori hylkää alle 4 sanan ja yli 40 sanan lainaukset (ValueError).  
   * **Systeemipromptin lisäys:** *"EXTRACT EXACT QUOTES ONLY. DO NOT PARAPHRASE. DO NOT TRANSLATE."*  
4. **Dynaaminen Virhepalaute (LLM Task Executor):**  
   * Jos Pydantic nostaa ValidationErrorin, LLMTaskExecutor ottaa sen kiinni.  
   * Seuraavaan API-kutsuun injektoidaan vain *tuorein* virhe XML-lohkoon: \<PREVIOUS\_SCHEMA\_ERROR\>Error: Quote not found in source text with 95% ratio.\</PREVIOUS\_SCHEMA\_ERROR\>.  
   * Uudelleenyritysten katto on SystemConcurrency.LLM\_MAX\_RETRIES. Virheitä ei koskaan nielaista except: pass \-lausekkeilla.

### **Vaihe 4: Dead Letter Queue (DLQ) ja Matematiikka**

1. **TDA:n hylkääminen (DLQ):**  
   * Jos LLM\_MAX\_RETRIES ylittyy, kyseinen väite siirretään DLQ-tilaan. Backend Enum-päivitys: ValidationStatus.dlq.  
   * TDA:lle ei anneta 0 pistettä. Se poistetaan nimittäjästä: hit\_rate \= sum(True) / (total\_atoms \- dlq\_count).  
2. **Nollalla Jakamisen Esto (Death by DLQ):**  
   * backend\_v2/utils/scoring/ moottorit päivitetään tukemaan 3-tilalogiikkaa (True, False, DLQ).  
   * Lisätään ehto: if valid\_denominator \<= 0: return ScoringResult(score=None, status="FAILED\_UNSCORABLE").  
3. **Map-Reduce / Chunk-Aggregointi (report\_controller.py):**  
   * Jos dokumentti on pilkottu osiin, tulokset yhdistetään: Positiivisille hyveille (inverse\_evidence=False) käytetään ANY()-logiikkaa. Negatiivisille paheille (inverse\_evidence=True) käytetään ALL()-logiikkaa (yksikin haitallinen löydös kaataa dokumentin puhtauden).  
4. **DAG-tason suojat:**  
   * Jos pisteytysmoottori palauttaa FAILED\_UNSCORABLE, Orkestraattorin on merkittävä koko arvioinnin tila luokkaan FATAL\_SOURCE\_DATA ja lopetettava prosessointi välittömästi.

### **Vaihe 5: Frontend UI \-päivitykset (Tier 2 Hardening)**

1. **Dart Freezed-mallit:**  
   * Päivitetään mallit tukemaan uutta TDAAssertion \-oliota ja sen listoja (tdaAssertions: List\<TDAAssertion\>).  
   * Lisätään Enum ValidationStatus.dlq.  
   * **Zero Compromise:** Null-coalescing-operaattoreiden (?? \[\]) käyttö legacy-datan pelastamiseksi on EHDOTTOMASTI KIELLETTY. UI:n on kaaduttava äänekkäästi ("Red Screen of Death" kehitystilassa), jos backend lähettää vanhentunutta dataa.  
2. **Matriisieditori:**  
   * Käyttöliittymä (prompt\_block\_builder\_view.dart) päivitetään sellaiseksi, että käyttäjä voi syöttää jokaiselle Claimille rajattoman määrän TDAAssertion \-kriteerejä dynaamiseen listaan ja valita checkboxilla onko kyseessä inverse\_evidence.  
3. **N/A (DLQ) renderöinti:**  
   * Raporttinäkymiin (result\_dashboard.dart yms.) lisätään tuki dlq \-tuloksille. Jos kriteeri on DLQ-tilassa, se näytetään harmaana ("Ei arvioitavissa lähteen laadun vuoksi").

### **6\. Definition of Done (Laatuportit)**

* **Tier 3 Nollaus:** Kehitystietokannat on tyhjennetty ja siemennetty uudella, deterministisellä datalla.  
* **Yksikkötestit (\>90%):** Pydantic RapidFuzz @model\_validator on testattu onnistumisilla, OCR-roskalla, liian pitkillä/lyhyillä lainauksilla sekä kadonneella info.context:lla. Nollalla jakaminen ja DLQ-vähennys on testattu moottoreissa. Chunk-reducer (ANY/ALL) on testattu.  
* **Verkottomuus (Strict Mocking):** Yksikään testi ei tee eläviä LLM-verkkokutsuja. Mock-LLM on viritetty palauttamaan kahdesti vääränlainen lainaus ja todistamaan, että \<PREVIOUS\_SCHEMA\_ERROR\> välitetään oikein ja kolmannella kerralla TDA ohjataan DLQ-tilaan kaatumatta.

### ---

**Yleinen vaikutus ajoihin ja niiden tuloksiin**

Kun tämä Epic on viety tuotantoon, järjestelmä kokee merkittävän paradigman muutoksen:

1. **Vauhti (Nopeus):** Ajot nopeutuvat huomattavasti. LLM:ää ei enää käytetä kriteerien keksimiseen lennosta (atomisointi), mikä säästää jopa 10–20 sekuntia ja ison pinon tokeneita per ajo. Järjestelmä hyppää suoraan O(1)-mäppäyksen kautta varsinaiseen työhön: PDF-tekstin deterministiseen validointiin.  
2. **Luotettavuus ja Hinta:** Kustannukset putoavat. Raskaat atomisointi-promptit jäävät pois. Koska matriisien System-promptit pysyvät nyt täysin staattisina, LLM API pystyy hyödyntämään **Prompt Caching** \-ominaisuutta lähes 100-prosenttisesti (vain ladattu PDF-data vaihtelee), mikä säästää satojatuhansia tokeneita raskaissa ajoissa.  
3. **Tulosten Laatu (Scoring):** "Harmaa alue" poistuu. Asiakas ei enää saa tuloksia, joissa hänellä on "80 % oikein" satunnaisten LLM-mikro-atomien takia. Tulos on raaka, läpinäkyvä ja perustuu puhtaasti asiantuntijoiden asettamaan akateemiseen kriteeristöön (SSOT). Solujen keskiarvot saattavat tippua, mutta laatu on kiistatonta ja 100 % auditoitavissa.  
4. **Ei Keksittyjä Lainauksia:** RapidFuzz-validaattorin myötä joka ikinen vihreäksi tai punaiseksi merkitty kohta on matemaattisesti sidottu PDF-tiedostossa olevaan tekstiin. Järjestelmä on auditoinnin kestävä; "AI Black Box" \-ongelma on ratkaistu lopullisesti.  
5. **Reiluus Huonolla Datalla:** Aiemmin lukukelvottomat sivut (esim. pelkät skannatut kuvat) saattoivat aiheuttaa nollapisteitä ja outoja arvioita. Jatkossa ne menevät turvallisesti DLQ (N/A) \-tilaan. Asiakasta ei rangaista teknisestä lukuvirheestä, vaan ohitetut kohdat renderöidään raporttiin harmaana. Jos sivu on täysin roskaa, ajo keskeytyy ennen kuin se polttaa rahaa (Fail-Fast: FATAL\_SOURCE\_DATA).