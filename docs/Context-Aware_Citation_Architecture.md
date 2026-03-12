# Arkkitehtuurimäärittely: Kontekstitietoinen lähdeviittaus (Context-Aware Citation)

Tämä dokumentti määrittelee Quorum V2 -arkkitehtuurin asiantuntija-agenttien lähdeviittausstrategian (Theory Grounding).

## 1. Ydinongelma
Aiemmassa arkkitehtuurissa järjestelmä liitti matriiseihin kytketyt lähdeviitteet (esim. Bloom, Toulmin) graafiseen käyttöliittymään (SDUI) mekaanisesti jokaiselle renderöitävälle elementille. Tämä tapahtui riippumatta siitä, tarvittiinko tai käytettiinkö kyseistä lähdettä todellisuudessa asiantuntijan analyysissä. Seurauksena oli informaatiotulva, joka heikensi tieteellisten ja organisaatiokohtaisten viitteiden arvoa loppukäyttäjälle. 

## 2. Toimintaperiaate & Tavoitteet

**Tavoite on siirtää päätösvalta aktiiviseen lainaamiseen tekoälymallille determinististen Pydantic-rakenteiden kautta, varmistaen samalla viitteiden oikeellisuuden.**

Uusi "Context-Aware Citation" -arkkitehtuuri perustuu seuraaviin periaatteisiin:

1. **Ei pakotettuja lähteitä:** Jos asiantuntija ei hyödynnä lähdettä antamansa perustelun luomisessa, se ei myöskään palauta lähdeviitettä Pydantic-vastauksessaan (`cited_source_id = null`). Tällöin käyttöliittymä (V2 SDUI `WidgetFactory`) ei piirrä lähdelaatikkoa lainkaan ruudulle. Sanat "Ei lähdettä", "Ei viitettä" tai tyhjien laatikoiden renderöinti on ehdottomasti kielletty (Strict No-String Mandate).
2. **Pakotettu ja oikeellinen lainaus:** Jos asiantuntija käyttää lähdettä, sen on palautettava alkuperäinen `source_id` JA senhetkistä perustelua tukeva **suora ja sanatarkka lainaus** alkuperäisestä tekstistä (`cited_text_quote`).
3. **Pääasiallinen lähdemateriaali ja TARKKA muotovaatimus (`docs\Holistinen Mestaruus.md`):** Arviointiasiantuntijoiden ensisijainen tiedonlähde ja viitekehys on Quorumin oma "Holistinen Mestaruus" -dokumentti. Jokaiselle arviointipromptille haetaan lähteet aina ensisijaisesti tästä dokumentista. Esimerkkejä hyödynnettävistä viitekehyksistä: Kahneman (Järjestelmä 1 & 2), Bloom, Toulmin, Goodhartin laki ja Dreyfus & Dreyfus -viitekehykset. Se sitoo agenttien toiminnan vahvasti organisaation omiin tieteellisiin periaatteisiin. 
   > [!IMPORTANT]
   > **Viitteen muodon on oltava absoluuttisen tarkka APA/Harvard -tyylinen auktoriteettivaatimus, täsmälleen samassa muodossa kuin `seed_data.json`:n alkuperäisissä PromptBlockeissa.**
   > **ESIMERKKI (ÄLÄ POIKKEA TÄSTÄ):** `"Anderson, Lorin W. & Krathwohl, David R. (toim.) 2001."` (Tekijät. Vuosi. Mahdollisesti teoksen nimi lyhyenä). Kaikki vapaamuotoiset "Sitra sanoo että..." -viitteet on ehdottomasti kielletty. Viitteen (`cited_source_id` / `citation_reference`) on oltava suoraan kopioitavissa tieteelliseen lähdeluetteloon muodollisessa kirjallisuusformaatissa.
4. **Internet toissijaisena lähteenä (RAG/WebFetcher):** Mikäli sisäinen viitekehys ei tarjoa riittävää pohjaa tai analogiaa spesifille asiantuntijahavainnolle, agentti voi nojata internet-hakuun vastaavia, auktorisoituja lähteitä etsiessään. 
5. **Eheyden ja olemassaolon testaus (Citation Integrity):** Jokainen asiantuntijan generoima uusi tai dynaaminen lähde (erityisesti internetistä haettu) on aktiivisesti testattava faktuaalisen eheyden varmistamiseksi ennen kuin se näytetään loppukäyttäjälle. Lähteen on oltava olemassa ja lainauksen on oltava oikeata, alkuperäisessä tekstissä esiintyvää tekstiä (Fail-Fast: `verify_citation_integrity` -hook).

## 3. Uusi Arkkitehtoninen Malli

Uusi "Context-Aware Citation Architecture" korvaa staattisen käyttöliittymärenderöinnin **Dynaamisella Pydantic-injektiolla** ja **Pakotetulla Faktantarkistuksella**. Se koostuu kolmesta arkkitehtonisesta pilarista:

### 3.1. Dynaaminen Pydantic-Injektio (`PromptCompiler`)
`PromptCompiler` lukee dynaamisesti (esim. matriisien pohjalta tai `Holistinen Mestaruus.md` -dokumentista) sallitut lähteet Enum-listana tai sallii ehdollisen täytön verkkohaulla. Tämä poistaa vapaamuotoisen tekstin hallusinoinnin riskin heti rajapinnassa. Pydantic-skeeman on näytettävä tekoälylle tältä:

```python
class XAIFeedback(BaseModel):
    justification: str = Field(description="Analyysin perustelu tälle havainnolle.")
    
    # Enum-lista sallituista lähteistä tai null
    cited_source_id: str | None = Field(
        description="JOS analyysisi tukeutuu suoraan ennalta määrättyyn teoriaan (Holistinen Mestaruus) tai toissijaiseen, luotettavaan internet-lähteeseen, valitse sen ID tai URL. Muuten palauta aina null."
    )
    
    cited_text_quote: str | None = Field(
        description="JOS valitsit lähteen yllä, liitä tähän tarkka, SUORA ja SANATARKKA lainaus teoriasta/lähteestä, joka tukee äskeistä perusteluasi. Tekoälyn luoma oma teksti on tässä kielletty."
    )
```

### 3.2. Fail-Safe Turvaportti ja Graceful Hook Degradation (`verify_citation_integrity`)
Backend-orkestraattoriin lisätään (tai olemassa olevaa laajennetaan) `verify_citation_integrity` -ohjelmistorutiini. Kun asiantuntija-agentti palauttaa Pydantic-objektin, tämä hook lukee `cited_text_quote` -kentän ja etsii sen absoluuttisena osajonona (substring, sanatarkka haku) ilmoitetusta lähteestä. 

Järjestelmä priorisoi laajan arvioinnin eheyttä, ja torjuu hallusinaatioriskin V2-standardin "Graceful Degradation" & "Dual-Reporting" -yhdistelmästrategialla:

1.  **Vaihtoehto C (Kehittäjän Globaali Ohitus):** Backendin `.env`-konfiguraation `SKIP_CITATION_VERIFICATION=true` asetus ohittaa koko merkkijonoetsinnän tyystin. Tämä sallii "nopean kokeilun" LLM-promptien säädössä.
2.  **Vaihtoehto B (Graceful Nullification):** Tuotannossa, jos lainausta ei löydy täsmälleen asiantuntijan esittämässä muodossa (eli agentti jäi kiinni hallusinaatiosta), suoritus EI kaadu fataaliin `AppException`-virheeseen kaataen koko DAG-ketjua. Sen sijaan hook suorittaa "Graceful Nullification" -siivouksen:
    *   Hook ampuu palvelinlokiin rakenteellisen tason varoituksen: `logger.warning("Citation hallucination detected and stripped: ...")`.
    *   Hook yliajaa asiantuntijan väärentämän Pydantic-datan asettamalla `cited_source_id = null` ja `cited_text_quote = null`.
    *   Pelastettu, ja nyt vain "omaan hyvään analyysiin" perustuva argumentti jatkaa matkaansa eteenpäin.

### 3.3. Graceful Degradation (V2 SDUI)
Käyttöliittymässä "WidgetFactory" vastaanottaa datan. Jos `cited_source_id` on Pydanticin käsittelyn jälkeen yhä `null`, koko viitelohkoa ei piirretä (`SizedBox.shrink()`). Ei "null", ei "tyhjä lähde" -tekstejä.

## 4. Työvaiheet Arkkitehtuurin Saavuttamiseksi (Execution Steps)

Tämän tavoitteen saavuttaminen edellyttää seuraavien spesifien teknisten vaiheiden toteuttamista:

1.  **Rakenteellinen purku (Knowledge Extraction):** Rakenna mekanismi tai koodinpätkä, joka jäsentää ja lukee `Holistinen Mestaruus.md` -dokumentin olennaisimmat viitekehykset (Bloom, Toulmin, Kahneman jne.) koneluettaviksi objekteiksi (esim. `PromptBlock` tai sisäinen tietokanta `seed_data.json` -tasolla).
2.  **Dynaamisen Pydantic-skeeman päivitys:** Muokkaa Pydantic-malleja (esim. `prompt_compiler.py`) vastaanottamaan ja generoimaan edellä kuvatut `cited_source_id` ja `cited_text_quote` vapaan `citation` -tekstikentän sijaan.
3.  **Deterministinen Tarkistus-Hook (`verify_citation_integrity`):** Laajenna nykyinen backendin arkkitehtuuri siten, että `verify_citation_integrity` tutkii Pydantic-vastauksen:
    *   Varmistaen, että `cited_text_quote` todella löytyy väitetystä lähteestä (Holistinen Mestaruus.md tai ulkoinen URL-haku). Estää myötäilyvinouman hallusinaatiot.
4.  **UI:n Graceful Degradation (Varmistettu osittain):** Varmistetaan SDUI-puolella (`WidgetFactory`), että kokonaan tyhjä `cited_source_id` tuottaa pelkän `SizedBox.shrink()` -palautteen, eikä koskaan piirrä placeholder-elementtejä ("Ei lähdettä").
