# Epic 42: Arvioinnin tiukkuuden toteutusmallit (Evaluation Strictness)

Tässä dokumentissa on avattu yksityiskohtaisesti kolme eri arkkitehtonista tapaa toteuttaa tekoälyn True/False -päätösten tiukkuuden säätö (Strictness). Jokaisessa mallissa käydään läpi sen filosofinen merkitys, tarkka kooditason toteutustapa Quorum-arkkitehtuurissa, sekä lopputulokset järjestelmän ja loppukäyttäjän kannalta.

---

## Malli 1: Prompt-ohjattu tiukkuus (Kielitieteellinen)

**Merkitys:**  
Tämä on perinteinen "ChatGPT-tyyppinen" ratkaisu. Luotamme siihen, että kun sanomme tekoälylle "ole lempeämpi", se ymmärtää mitä tarkoitamme ja muuttaa käytöstään. Ohjelmistoarkkitehtuuri pysyy täysin ennallaan, ainoastaan tekoälylle menevä tekstimuotoinen ohjeistus muuttuu.

**Toteutustapa koodissa:**
1. Otamme käyttöön `prompt_compiler.py` -tiedostossa jo uinuvan `calibrate_strictness(level)` -funktion.
2. Kun `DAGExecutor` rakentaa työnkulkua, se lukee asetuksista (esim. 0-100) tiukkuuden ja lisää LLM:n järjestelmäpromptin alkuun lauseen:
   - *Lempeä (esim. 25):* "STRICTNESS CALIBRATION (25/100): Lenient. Be generally forgiving of minor errors..."
   - *Tiukka (esim. 100):* "STRICTNESS CALIBRATION (100/100): Absolute Strictness. You are an unforgiving auditor..."

**Lopputulokset ja vaikutus:**
- **Käyttäjälle:** Tulokset muuttuvat todennäköisesti hieman pehmeämmiksi lempeällä asetuksella (enemmän True-arvoja).
- **Järjestelmälle:** Erittäin arvaamaton. Pitkissä teksteissä tekoäly saattaa unohtaa promptin alun ("Attention Dilution") ja palata oletustiukkuuteen. Tulos on musta laatikko: emme koskaan voi ohjelmallisesti todistaa, *miksi* LLM päätti antaa True-arvon jossain satunnaisessa matriisissa.

---

## Malli 2: Skeema-ohjattu tiukkuus (Pydantic Fail-Fast & Micro-CoT)

**Merkitys:**  
Quorum-arkkitehtuurin erikoisuus on dynaamiset Pydantic-skeemat. LLM:ää ei ohjata vain sanoilla, vaan sitä ohjataan ohjelmointikielen tietorakenteilla.

**Toteutustapa koodissa (`prompt_compiler.py`):**
Atom-tason evaluaatiossa LLM pakotetaan vastaamaan tarkkaan `AtomResponse`-skeemaan, joka vaatii aina "Chain of Thought" -tyyppisen perustelun ennen Boolean-päätöstä:
```python
quote: str | None = Field(default=None, description="Pakotettu lainaus alkuperäisestä tekstistä Micro-CoT säännöllä. Null if no evidence.")
reasoning: str = Field(..., description="Kognitiivinen kitka ja arvioinnin perustelu.")
boolean: bool = Field(..., description="Puhdas True/False -osumapäätös.")
```
Järjestelmä luottaa "Zero-Trust Auditor" -promptaukseen yhdistettynä pakotettuun boolean-kenttään. LLM:n on itse tehtävä kova True/False -päätös seed-datan sääntöjen pohjalta.

**Lopputulokset ja vaikutus:**
- **Järjestelmälle:** Erittäin korkea determinismi. Emme laske kynnysarvoja ohjelmallisesti, vaan LLM kantaa vastuun kognitiivisesta päätöksestä. `quote` toimii auditoinnin maadoittimena, mutta sallii "Benefit of the doubt" -päätökset (`None`), jos tiukkuutta on laskettu Mallin 1 prompt-kalibroinnilla.

---

## Malli 3 (Hylätty Visio): Numeerinen arvo + Backend-kynnys

*Huom: Tämä malli on Quorum V2 -arkkitehtuurissa hylätty ydinevaluaatiosta (Boolean-osumista), mutta sitä käytetään erillisissä `extension_confidence`-laajennuksissa.*

**Toteutustapa teoriassa:**
LLM olisi palauttanut `confidence_score`-arvon (0-100), ja backendin Transformer olisi tehnyt päätöksen (`atom.is_hit = atom.confidence_score >= threshold`). 

**Miksi tästä luovuttiin ydinarkkitehtuurissa:**
Havaitsimme, että LLM:n kyky arvioida luottamustaan lineaarisella asteikolla on erittäin altis hallusinaatioille (pseudomatiikkaa). Oli huomattavasti luotettavampaa pakottaa LLM tekemään binaarinen (True/False) ratkaisu Pydanticin `boolean`-kentällä (Malli 2) ja hallita "lempeyttä" sanallisella kalibroinnilla (Malli 1).

---

### Loppupäätelmä: Nykytila (V2 Tuotanto)

Tuotantovalmis Quorum V2 -arkkitehtuuri nojaa viime kädessä **Mallin 1 ja Mallin 2 yhdistelmään**. 

Emme siirtäneet kynnysarvojen määrittelyä backendiin (Malli 3), koska se heikensi determinismiä ja etäännytti päätöksenteon alkuperäisestä tekstistä. Sen sijaan "Titanium Standard" on saavutettu antamalla LLM:lle staattinen Pydantic-skeema, joka vaatii puhtaan `boolean: bool` päätöksen ja pakotetun perustelun (`reasoning`). Tiukkuuden tasoa (0-100) säädetään yksinomaan `prompt_compiler.py`:n `calibrate_strictness()` -funktiolla, joka muuttaa asennetta ("Zero-Trust Auditor" vs "Absolute Leniency"), ennen kuin kova Boolean-päätös lukitaan Pydanticiin.
