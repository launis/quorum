# **OSA 1: Alkuperäinen Luonnos ja Nykytilan Kartoitus**

## **Epic 94: Tulostuksen Unifikaatio ja Polymorfinen SDUI-Renderöijä**

### **1. Nykytilan Analyysi (Siiloutunut Tulostuslogiikka)**

Quorumin tulostuskerroksessa on tällä hetkellä arkkitehtuurinen haaste: erilaisten tietorakenteiden esittäminen on siiloutunut omiin erillisiin rutiineihinsa. 
Tämä näkyy vahvasti kolmessa tulostetyypissä:
* **Yksittäisten matriisirivien selitykset (row_explanation):** Renderöidään kovakoodatusti taulukkorakenteen sisään (`report_template.jinja2`).
* **Kokonaisten osioiden tiivistelmät (section_syntheses):** Renderöidään ominaan SDUI-lohkoina omien vihreiden otsikoidensa alle.
* **Esiin nostetut poikkeavuudet (xai_highlights):** Käsittely vaatii täysin oman erillisen logiikkansa ja renderöintikomponenttinsa.

**Nykytilan ongelma:** Koska asettelulogiikka on jakautunut Flutter-käyttöliittymään ja backendin PDF-generaattorin Jinja-templateihin, uuden tulostetyypin lisääminen (esim. "toimenpidesuositukset") vaatii raskasta koodin muuttamista (if/else-rakenteita) molemmissa "päissä" ohjelmistoa.

### **2. DTO-Kannan Rooli ja Refaktorointi**

**DTO (Data Transfer Object)** toimii tulostuksen datalähteenä (`ReportDataDTO`). Tällä hetkellä DTO sisältää vahvasti tyypitettyjä mutta loogisesti toisistaan erotettuja siiloja (kuten erilliset kentät riviselityksille ja synteeseille).

* **Ongelma:** Renderöivä ohjelma joutuu päättelemään, *mistä* kentästä se katsellaan mitäkin tietoa, ja rakentamaan layoutin näiden kenttien ehtojen perusteella (`if row_explanation in cols...`, `if layout.synthesis_blocks...`).

### **3. Tavoitetila: Polymorfinen Renderöinti ja Universaali Tuloste**

Kaikki tulosteet (rivit, synteesit, XAI) yhdenmukaistetaan yhdeksi polymorfiseksi lohkovirraksi (Stream of Blocks) ennen kuin ne tallennetaan lopulliseen muotoonsa.
Järjestelmä siirtyy **puhtaaseen Server-Driven UI (SDUI)** -arkkitehtuuriin. Järjestelmän ainoaksi totuuden lähteeksi tulee staattinen, lopulliseksi käännetty dokumentti (esim. `report_compiled.json` tiedostojärjestelmässä), josta renderöinti tapahtuu yhdellä universaalilla silmukalla.

---

# **Raportti (Lopullinen Synteesi)**

Tässä on tavoitearkkitehtuuri, joka ratkaisee tulostuksen monimutkaisuuden, poistaa esityslogiikan if/else-viidakot (Jumalkoodit) renderöijistä ja noudattaa puhtaan SDUI:n standardeja.

## **Epic 94: Polymorphic SDUI Engine & Unified File Artifacts**

### **1. DTO-Kannan Refaktorointi (The Universal Block Stream)**

Järjestelmän tulostusmalli refaktoroidaan täysin asettelu-vetoiseksi:
* **Abstraktio:** Erilliset konseptit kuten "row_explanation" tai "xai_highlight" lakkaavat olemasta renderöinnin tasolla. Ne kaikki muunnetaan DTO:ssa geneerisiksi SDUI-lohkoiksi (`SduiMarkdownBlock`, `SduiWarningBlock`, `SduiTableBlock`).
* **Järjestyksen Vapaus:** Kun kaikki teksti on lohkoja, backend voi vapaasti sekoittaa yksittäisen kriteerin selityksen ja siihen liittyvän XAI-varoituksen toistensa lomaan, ilman että UI:ta tarvitsee opettaa ymmärtämään tätä uutta rakennetta.

### **2. Yhtenäinen Tiedostotallenne (Single Source of Truth -tiedosto)**

Kun `text_consolidation_hook` ja siihen liittyvät prosessit ovat valmiita, backend kokoaa koko raportin valmiiksi "pureskelluksi" SDUI-puuksi ja tallentaa sen yhtenä lukittuna tiedostona (esim. `report_compiled.json`) `executions/ID/` -hakemistoon.
* **Forensinen Muuttumattomuus:** Tämä tiedosto on immuuni tuleville tietokantamigraatioille ja koodimuutoksille. Raportti renderöityy kymmenen vuoden päästäkin tismalleen samanlaisena.

### **3. Universaali Tulostus (Tyhmät Piirtokoneet)**

Koska meillä on nyt yksi täydellinen, polymorfinen lista lohkoja, PDF-generaattori ja Flutter muuttuvat rakenteellisesti "tyhmiksi piirtokoneiksi":
1. **Flutter-Käyttöliittymä:** Lukee lohkoja yksitellen ja palauttaa oikean natiivikomponentin katsomatta koodin isoa kuvaa (esim. `for block in blocks: buildWidget(block)`).
2. **Staattinen PDF (Jinja2):** Jinja-template yksinkertaistuu massiivisesti. Se vain iteroi saman `blocks`-listan läpi ja tulostaa lohkon tyypin mukaisen HTML-pätkän. Kaikki monimutkainen taulukkologiikka on ratkaistu jo backendissä.

---

# **OSA 2: Arkkitehtuurin Kriittinen Jalostus ja Kooditason Ratkaisut**

Edellisen mallin refaktoroinnin suurin tekninen haaste on erottaa liiketoimintalogiikka (kuka saa nähdä minkäkin rivin) puhtaasta esityslogiikasta. Ratkaisu on "BFF Adapter" -kerros (Backend-For-Frontend), joka muuttaa semanttisen tiedon polymorfiseksi esitystiedoksi.

### **1. SDUI-Lohkojen Standardisointi ja Mapping**

**Kritiikki (Falsifikaatio):** Jos LLM generoima `row_explanation` on vain pelkkää tekstiä, PDF haluaa piirtää sen taulukkoon, kun taas SDUI voisi haluta sen korttina. Miten taataan, että sama polymorfinen lohko taipuu molempiin?
**Ratkaisu (Koodi):** Luodaan semanttinen `SduiEntityBlock`, joka sisältää avain-arvo-pareja (esim. Nimi, Tulos, Selite). Kumpikin renderöijä (Flutter ja PDF) osaa piirtää EntityBlockin omien kykyjensä mukaan (PDF tekee siitä taulukkorivin, Flutter saattaa tehdä laajennettavan kortin).

```python
class SduiEntityBlock(SduiBaseBlock):
    type: Literal["entity_row"] = "entity_row"
    title: str
    value_badge: Optional[str]
    description: str
    warnings: List[str] # XAI-huomiot integroituna suoraan entiteettiin!
```

### **2. Yhden Silmukan Renderöinti (The Master Loop)**

**Kritiikki (Falsifikaatio):** Jinja-template paisuu ylläpitokelvottomaksi, jos siinä yritetään käsitellä jokainen SDUI-tyyppi valtavassa `if-elif-else` -hässäkässä.
**Ratkaisu (Koodi):** Makrot (Macros) ja dynaaminen inkluusio. Jokaiselle SduiBlock-tyypille luodaan oma pieni template-palanen, ja Master Loop vain kutsuu oikeaa palasta.

```jinja2
<!-- PDF Master Render Loop -->
<div class="report-content">
  {% for block in report_compiled.blocks %}
      {% if block.type == "markdown" %}
          {{ render_markdown(block.text) }}
      {% elif block.type == "entity_row" %}
          {{ render_entity_row(block) }}
      {% elif block.type == "warning_card" %}
          {{ render_warning(block) }}
      {% else %}
          <!-- Tuntematon lohko sivuutetaan turvallisesti -->
      {% endif %}
  {% endfor %}
</div>
```

**Johtopäätös:** Siirtyminen erillisistä datariveistä polymorfiseen "Block Streamiin" ja tiedostopohjaiseen tallenteeseen eliminoi renderöintipään Jumalkoodin. Kun backend pakkaa `row_explanations`, `section_syntheses` ja `xai_highlights` samaan listaan lohkoina, UI-päivitykset (kuten uusien osioiden lisäys) tapahtuvat ilman koodimuutoksia frontendissä tai PDF-generaattorissa.

---

# **OSA 3: LLM-Irrotus ja Deterministinen BFF-Arkkitehtuuri**

*Lisätty heinäkuun 2026 Tier 4 Bug Hunting -istunnon perusteella.*

SDUI:n polymorfinen rakenne (esim. `AnySduiBlock`) on todettu erittäin vaaralliseksi, jos sitä pyydetään suoraan kielimallilta (LLM). 

### **1. Miksi LLM ja SDUI pitää erottaa? (Pydantic extra="forbid" -kaatumiset)**
Quorumin V2CoreBase käyttää tiukkaa `extra="forbid"` -sääntöä. Kun LLM yritti tuottaa SDUI-komponentteja suoraan:
* Se unohti pakollisia kenttiä (esim. `AlertBlock`in `severity`).
* Se keksi loogisilta tuntuvia mutta kiellettyjä kenttiä (esim. yritti laittaa `text`-kentän `HeroInsightBlock`:iin, josta se puuttui, tai käytti `citations`-kenttää `QuoteCardissa` ohjeiden ohjaamana).
* Tuloksena oli välitön Pydantic-validointivirhe, joka kaatoi koko ajon. Vaikka ohituskaistoja ja fallback-kenttiä lisättiin "laastareina" (Heinakuu 2026), arkkitehtuurinen juurisyy on se, että **LLM pakotetaan tekemään UI-esityslogiikan päätöksiä**.

### **2. Ratkaisu: Semantic Data Contracts (LLM) -> SduiMapperService (BFF)**
Lopullinen ja 100 % deterministinen ratkaisu SDUI-hallusinaatioihin on ottaa SDUI-mallit kokonaan pois LLM:n näkyviltä.

1. **LLM tuottaa vain semanttista "tyhmää" dataa:**
   Orchestratorin Pydantic-schemat (kuten `SynthesisSectionDTO`) refaktoroidaan litteiksi. LLM ei palauta SDUI-lohkoja, vaan esimerkiksi:
   ```python
   class LLMSectionData(BaseModel):
       summary_text: str
       bullet_points: list[str]
       quotes: list[QuoteEvidenceDTO]
   ```
2. **Backend-For-Frontend (BFF) hoitaa renderöinnin:**
   Quorumin sisäinen Python-palvelu (`SduiMapperService`) ottaa LLM:n puhtaan datan vastaan ja kääntää sen deterministisellä koodilla polymorfisiksi `AnySduiBlock`-lohkoiksi (esim. pakkaa stringit turvallisesti `BulletListItem`-objekteiksi). 
   *Näin koodi ei ikinä unohda `severity`-kenttää tai laita vääriä attribuutteja, ja Pydantic-kaatumiset katoavat kokonaan.*
