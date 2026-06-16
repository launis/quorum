# Epic: Dynamic Workflow Extensions & Dynamic Lexicon

## 1. Tavoite ja Tausta
Quorum V2:n arkkitehtuuri perustuu dynaamisiin DAG-työnkuluihin. Järjestelmä sisältää tällä hetkellä teknistä velkaa liittyen "Mekaaninen vs Kognitiivinen Tasapaino" (`variance_validation`) -laajennukseen:

1. Laajennus lasketaan tällä hetkellä `blueprint.py`:ssä kovakoodattujen askeleiden ID:iden perusteella. Koska V2-työnkulut ovat dynaamisia, dataa ei löydy, ja arvo putoaa aina turvalliseen nollaan.
2. Sanakirja (`PERFORMATIVE_PATTERNS`), jolla mekaaninen moottori etsii mielistelevää jargonia (sycophancy), on kovakoodattu Python-tiedostoon (`linguistics.py`). Se vaatii täydellisen merkkijono-osuman (ei taivu), eikä sitä voi hallita käyttöliittymästä.

**Tavoitetila:** 
A) Irrotetaan Workflow Extension -laskenta `blueprint.py`:n sisältä ja siirretään se puhtaaseen **Extension Engine** -malliin, joka käyttää semanttisia tageja askeleiden tunnistamiseen. 
B) Siirretään performatiivinen sanakirja tietokantaan ja lisätään perusversio sumeasta logiikasta (`rapidfuzz`), sekä rakennetaan näille hallintakäyttöliittymä Admin Studioon.

## 2. Arkkitehtuurinen Ratkaisu

### Extension Engine ja Semanttiset Tagit

> [!IMPORTANT]
> **Hardening Rule #46 (zero_db_hardcoding_mandate):** Database entity IDs or literal names MUST NEVER be hardcoded or used in conditional logic. When refactoring hardcoded logic, you MUST preserve its functional behavior by translating it into a dynamic check (e.g. comparing against active workflow step IDs or metadata schemas) rather than blindly deleting the bypass.

> [!WARNING]
> **Hardening Rule #82 (preservation_of_inline_comments):** NEVER delete existing inline comments (e.g. `# ...`) as they often document critical architectural exceptions or global states (such as variance validation exceptions). Only modify comments if explicitly upgrading them to PEP 257 docstrings.

Ongelma korjataan irrottamalla sidokset kovakoodattuihin työnkulun askeliin ja luomalla **Workflow Extension Hook**. Askelten tunnistaminen tehdään semanttisten tagien perusteella. `blueprint.py`:n tehtäväksi jää vain valmiin lasketun datan injektointi raporttiin.

Tagi sidotaan työnkulun askeliin ja Extension Hook etsii nämä askeleet dynaamisesti:

```json
// Step-määrityksessä (uusi vapaaehtoinen tags-kenttä)
{ "id": "step_vapaanimi_123", "tags": ["produces_authenticity_score"] }

// Workflow-objektissa (uusi kenttä extension_hooks)
{
  "extension_hooks": [{
    "type": "variance_validation",
    "source_step_tags": {
      "authenticity_score": "produces_authenticity_score",
      "linguistics_result": "produces_linguistics_result"
    }
  }]
}
```

### Dynamic Lexicon ja Sumea Logiikka
- **Tietokantaohjattu (Monikielisyys):** Fraasit siirretään koodista järjestelmän globaaleihin asetuksiin (`SystemConfig` / tietokanta). Rakenne suunnitellaan tukemaan aidosti monikielistä ohjelmistoa (N-määrä kieliä, dynaaminen avainrakenne), ei ainoastaan kovakoodattua kaksikielisyyttä (esim. pelkkä suomi/englanti).
- **RapidFuzz ja Kielikohtainen Konfiguraatio (Perusversio):** Korvataan eksakti `if pattern in text` -logiikka `rapidfuzz`-kirjastolla (`fuzz.ratio` yhdistettynä tekstin sanakohtaiseen tokenisointiin, **EI `fuzz.partial_ratio`**, joka aiheuttaa vääriä osumia alimerkkijonoista). Koska järjestelmä on täysin monikielinen, sumean haun kynnysarvojen (threshold) pitää olla dynaamisia ja sidottu tarkasteltavaan kieleen (suomi vaatii eri joustavuuden taivutuksille kuin englanti). Tässä toteutetaan suoraviivainen perusversio, jossa sanakirjan lisäksi myös kynnysarvot konfiguroidaan `SystemConfig`:in kautta kieli kerrallaan.

**Tietorakenteen dynaamisuus (Ei staattista Enumia):**
Jotta uusia kieliä voidaan aidosti lisätä Admin Studiosta ilman koodin uudelleenkääntämistä, **kielikoodeja (esim. `fi`, `en`) EI määritellä Enumina**. Pydantic- ja Dart-Enumit ovat staattisia, ja uuden avaimen lisääminen käyttöliittymästä aiheuttaisi välittömän `ValidationError`:in. Sen sijaan kielikoodit tallennetaan avoimina (mutta validoituina, esim. ISO 639-1 -standardin mukaisina 2-kirjaimisina) merkkijonoina `SystemConfig`-rakenteen avaimiksi. Kaikki kielet, kynnysarvot (fuzz threshold) ja sanat säilytetään yksinomaan tietokannassa. Esimerkki dynaamisesta tietokantarakenteesta:

```json
{
  "type": "performative_lexicons",
  "lexicon_configs": {
    "fi": {
      "fuzz_threshold": 80.0,
      "words": ["synergia", "disruptio"]
    },
    "en": {
      "fuzz_threshold": 95.0,
      "words": ["synergy", "disruption"]
    }
  }
}
```
Tämä arkkitehtuuri takaa sen, että kynnysarvoja voidaan hienosäätää suoraan Admin Studiosta ilman koodimuutoksia tai uudelleenkäännöstä.

## 3. Toteutusvaiheet

### Vaihe 1: Datamallien päivitys (Backend)

> [!CAUTION]
> **Hardening Rule #84 (pydantic_schema_freeze_mandate):** NEVER autonomously tighten or alter the structural types, `Optional` bounds (`| None`), or field signatures of any Pydantic models (DTOs, Domain Models, or DB schemas). Modifying a Pydantic model's strictness autonomously breaks downstream validation of the SSOT database.
>
> **POIKKEUS (Taaksepäin yhteensopivuus kielletty):** Tässä epicissä vaaditaan tiukka skeemamuutos. Vanhaa validointia EI tueta oletusarvoilla, vaan vanhan datan pitää kaatua.

- Lisätään `tags: list[str]` Pydantic-malliin `Step` (`v2_core.py`) tiukkana vaatimuksena ilman oletusarvoa (`= []`).
- Lisätään `extension_hooks: list[ExtensionHook]` -kenttä `Workflow`-malliin tiukkana vaatimuksena.
- Päivitetään seed-data sisältämään uudet kentät ja suoritetaan tietokannan tyhjennys/seedaus (Tier 3 - Database Reset), koska vanha data ei enää mene läpi Pydantic-validoinnista.

### Vaihe 2: Extension Hookin Luonti ja DAG-ajoitus (Backend)
- Luodaan `backend_v2/hooks/extensions.py`.
- Kirjoitetaan funktio `calculate_workflow_extensions`, joka iteroi työnkulun askeleet ja etsii vaaditut tulokset tagien perusteella.
- **DAG Race Condition ja Tilan Varmistus -korjaus:** Koska V2 ajaa DAG-askeleita rinnakkain, laajennukset on ajettava nimenomaan **Post-Execution Phase -vaiheessa** (koko työnkulun suorituksen päätteeksi, kun DAG on ratkaistu). Moottorin on lisäksi ehdottomasti tarkistettava lähdeaskeleen tila: jos yksikään vaadittu lähdeaskel ei ole valmis (esim. `if step.status != "COMPLETED"`), laajennuksen laskenta keskeytetään turvallisesti (palauttaa `0.0` tai `null`), jotta korruptoitunutta dataa ei käytetä.
- Kutsutaan `variance_engine.py`:tä tulosten pohjalta. Tulos tallennetaan **erilliseen `extensions`-sanakirjaan** `HookState`-objektissa. Se **EI SAA** olla "virtuaalinen askel" `steps`-taulukossa, jotta se ei riko Pydantic-mallin tiukkaa validointia (Hardening Rule #84) tai kaada Frontendin DAG-aikajanaa (NullReference).

### Vaihe 3: `blueprint.py`:n siivous (Backend)
- Poistetaan kovakoodattu if/else -logiikka (`if wf_ext == "variance_validation"...`) `blueprint.py`:stä.
- Päivitetään koodi lukemaan valmis arvo `HookState`:n `extensions`-sanakirjasta.

### Vaihe 4: Sanakirjan Siirto ja RapidFuzz (Backend)
- **Polymorfisen Unionin Päivitys (SystemConfig):** Koska `SystemConfig` on tiukka Discriminated Union (`extra="forbid"`), uutta dataa ei voi vain tallentaa olemassa olevaan rakenteeseen. Luodaan uusi Pydantic-malli `LexiconConfigPayload` ja rekisteröidään se `SystemConfig` Union-tyyppiin omalla `type="performative_lexicons"` erottimellaan. Vasta tämän jälkeen `PERFORMATIVE_PATTERNS` voidaan siirtää tietokantaan.
- **Zero-Legacy Boot ja Muna-Kana -korjaus:** Kun tietokanta tyhjennetään (Hard Reset), sanakirjaa ei ole. `linguistics.py`:n **TÄYTYY** sisältää turvallinen Graceful Degradation -tarkistus (esim. `if not lexicon_config: return 0.0`), jotta prosessi ei kaadu `NoneType`-virheeseen. Lisäksi perussanakirja (baseline) on injektoitava tietokantaan suoraan `seed_data.json` -tiedoston kautta, jotta Admin Studiolla on oletusdataa heti tyhjän koodikannan käynnistyessä.
- Tuodaan `rapidfuzz` osaksi `detect_performative_patterns` -hookkia (`backend_v2/hooks/linguistics.py`).
- Määritetään `rapidfuzz`-kynnysarvot dynaamisesti kielen perusteella `SystemConfig`:sta (ei kiinteää `fuzz.ratio > 85.0` koodissa). **Huom:** Teksti on ehdottomasti tokenisoitava (esim. `text.split()`) ja vertailtava sanakohtaisesti `fuzz.ratio`:lla väärien osittaisten osumien (kuten "näin" sanassa "päivänäinä") välttämiseksi.

### Vaihe 5: Admin Studio UI (Frontend Flutter)
- Luodaan Admin Studioon uusi näkymä sanakirjan hallintaan (Performative Lexicon Manager).
- Mahdollistetaan sanojen lisääminen, muokkaaminen ja poistaminen. Toteutuksen on tuettava täyttä monikielisyyttä, jolloin uusia kieliä voidaan lisätä ja hallita dynaamisesti ilman, että käyttöliittymä rajoittuu tiettyihin ennalta määriteltyihin kieliin.
- Tallennetaan muutokset takaisin Backendin `SystemConfig`-rajapintaan.

## 4. Menestyskriteerit
1. `Step`-malli tukee semanttisia tageja ja `Workflow` määrittelee tarvittavat hookit.
2. `blueprint.py` ei sisällä kovakoodattua logiikkaa työnkulkujen laajennuksille.
3. Koodissa (`linguistics.py`) ei ole enää kovakoodattua sanakirjaa, vaan se haetaan tietokannasta.
4. Suomen kielen taivutusmuodot tarttuvat haaviin mekaanisesti (`rapidfuzz`).
5. Admin voi hallita sanakirjoja Admin Studion kautta.
