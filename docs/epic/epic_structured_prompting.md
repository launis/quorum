# Epic: Structured Prompting ja XAI-Läpinäkyvyys (Server-Driven UI)

## 1. Tavoite ja Tausta

Quorum V2:n nollaluottamukseen (Zero-Trust) perustuva arkkitehtuuri edellyttää täydellistä rakenteellista eheyttä (Schema Purity) sekä korkeaa kykyä selittää tekoälyn päätöksiä (Explainable AI, XAI). 

**Nykytilan ongelma (String-pohjainen kääntäjä):**
Tällä hetkellä promptit (esim. `localization_compiler.py`:ssä) rakennetaan raakana tekstinkäsittelynä (f-string). Tämä johtaa kolmeen vakavaan ongelmaan:
1. **Empty Tag Hazard:** Jos tietokannan kenttä on tyhjä, kääntäjä luo LLM:lle tyhjän XML-tagin (esim. `<anchor_target></anchor_target>`), mikä sekoittaa LLM:n huomiomekanismia ja tuhlaa tokeneita.
2. **UI:n Sokeus (Black Box):** Koska prompti on vain massiivinen tekstijono, Flutter-käyttöliittymällä ei ole keinoa näyttää loppukäyttäjälle, *millä konkreettisilla säännöillä* hänet arvioitiin.
3. **Vaikea Testattavuus:** Promptien sisältöjen validointi yksikkötesteissä vaatii hankalaa ja särkyvää Regex-hakemista.

**Tavoitetila (Pydantic-pohjainen Serialisointi):**
Luovutaan promptien rakentamisesta stringeinä. Promptit määritellään Pydantic-datamalleina (DTO). Kun prompt lähetetään, Pydantic pudottaa tyhjät kentät automaattisesti pois (`exclude_none=True`), ja puhdas JSON-rakenne käännetään XML:ksi juuri ennen LLM-kutsua. Sama Pydantic-objekti tarjoillaan REST API:n yli Flutter-käyttöliittymälle XAI-visualisointia varten.

---

## 2. Arkkitehtuuriset Hyödyt (RoI)

1. **Automaattinen Schema Purity:** Pydantic estää tyhjien tagien syntymisen rakenteellisesti. Ei enää purkkavirityksiä (Duct Tape) tai Regex-strippausta.
2. **XAI ja Läpinäkyvyys (SDUI):** Asiakassovellus saa tiedon muodossa: *"Tässä kohdassa testattiin kausaalista väitettä, vaadittu markkeri oli 'always'"*. UI voi renderöidä tämän nätiksi osaksi tulosraporttia, jolloin tekoäly on 100% selitettävissä käyttäjälle.
3. **Deterministinen Caching:** Prompteista tulee ohjelmallisen tarkkoja, mikä maksimoi Prompt Caching -hyödyt ulkoisilla tarjoajilla.

---

## 3. Toteutusvaiheet (Implementation Plan)

### Vaihe A: Infrastruktuuri ja XML-Kääntäjä
- **Tehtävä:** Luodaan `backend_v2/utils/xml_utils.py`, joka sisältää `dict_to_xml` -funktion.
- **Vaatimus:** Funktion on tuotettava siistiä, oikein sisennettyä XML:ää, jotta Prompt Caching toimii tehokkaasti. Sen on tuettava sisäkkäisiä sanakirjoja ja listoja.

### Vaihe B: Prompt-mallien määrittely (Pydantic)
- **Tehtävä:** Luodaan hakemistoon `backend_v2/models/prompts/` omat Pydantic-mallit promptien rakenteille (eivät muokkaa tietokantamalleja).
- **Komponentit:** Esimerkiksi `TdaValidationPrompt`, `MatrixRulePrompt`, `SystemDirectivePrompt`.
- **Vaatimus:** Kaikki kentät, jotka voivat olla tyhjiä, määritellään `Optional` / `| None` tyyppisiksi, jotta `model_dump(exclude_none=True)` aktivoituu.

### Vaihe C: Kääntäjän Refaktorointi (`localization_compiler.py`)
- **Tehtävä:** Korvataan nykyiset f-string -rakenteet Pydantic-mallien instanssoinnilla.
- **Logiikka:** 
  1. Instanssoidaan esim. `TdaValidationPrompt`.
  2. Kutsutaan `model_dump(exclude_none=True)`.
  3. Syötetään sanakirja `dict_to_xml` -funktiolle.
- **Validointi:** Varmistetaan, että tuotettu XML on rakenteellisesti identtinen aiemman kanssa (pl. tyhjien tagien puuttuminen).

### Vaihe D: XAI-Rajapinnan Avaaminen (UI Integration)
- **Tehtävä:** Laajennetaan olemassa olevaa arviointi-endpointia palauttamaan myös `PromptContextDTO`.
- **Logiikka:** Sen sijaan, että generoitu Pydantic-prompt katoaisi LLM-kutsun jälkeen, se palautetaan vastauksessa (tai tallennetaan ajolokiin), josta Flutter Client voi lukea sen suoraan jäsenneltynä JSON-datana.

---

## 4. Riippuvuudet ja Riskit
- **Riski (Regressio):** Jos `dict_to_xml` ei muotoile sisennyksiä täsmälleen kuten aiemmin, Anthropic/OpenAI prompt cache saatetaan menettää lyhyellä aikavälillä (ennen kuin cache uusiutuu).
- **Riippuvuus:** Tämä tulisi toteuttaa vasta *Protocol Routing* -epicin jälkeen (tai itsenäisenä kokonaisuutena), jotta käynnissä olevat refaktoroinnit eivät mene ristiin.

## 5. Menestyskriteerit (Definition of Done)
1. Yhtään tyhjää XML-tagia (kuten `<tag></tag>`) ei lähetetä LLM:lle, tarkistettavissa logfire-treisseistä.
2. Koko prompt voidaan yksikkötestata Python-sanakirjoina.
3. Arkkitehtuuri ei riko voimassa olevia V2 Fail-Fast sääntöjä.
