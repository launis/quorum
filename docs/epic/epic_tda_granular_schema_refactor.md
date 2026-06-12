# Epic: TDA Assertion Granular Schema Refactor (STEP & Bounding Box Separation)

## 1. Ongelma ja Nykytila (Problem Statement)
Pydantic V2 -migraation (V1 -> V2) aikana `TDAAssertion`-mallin `concept_description` -kenttään "hakkeroitiin" alun perin luonnollisen kielen sisälle teknisiä prompt-askeleita. Nykytilassa kenttä on vapaamuotoinen `str`, joka sisältää implisiittistä ajo-ohjausta:
* `STEP 1:` (Anchorin etsintä)
* `STEP 2 (Bounding Box):` (Hakualueen rajaus, esim. lause tai kappale)
* `EXTRACTION CONDITION:` (Varsinainen validoinnin ehto)

**Miksi tämä on ongelma?**
Pydanticin "Zero-Fallback" ja "Fail-Fast" -arkkitehtuureissa Pydantic on _sole source of truth_. Nyt `concept_description` on kuitenkin "black box" -möykky, joka sokeuttaa käyttöliittymän (Admin Studio V2 ei ymmärrä kentän sisäistä rakennetta) ja pakottaa prompt_compilerin lukemaan luonnollista kieltä XML-strukturoinnin sijaan.

## 2. Tavoitetila (The Objective)
TDA:n "Pearl's Rung 3" -hakulogiikka jaetaan omiin eksplisiittisiin Pydantic-kenttiinsä. 

### Pydantic-tason muutos (`backend_v2/models/v2_core.py`)
```python
class TDAAssertion(BaseModel):
    # Nykyinen:
    # concept_description: str
    
    # UUSI TAVOITETILA:
    concept_description: str # Vain tiivis kuvaus itse konseptista, ei ajo-ohjeita
    anchor_target: Optional[str] = Field(description="Mitä ankkuria etsitään (ent. STEP 1)")
    bounding_box_scope: Literal["sentence", "paragraph", "document", "adjacent_paragraphs"] = Field(default="paragraph")
    extraction_rule: str = Field(description="Varsinainen sääntö, joka datan on täytettävä (ent. EXTRACTION CONDITION)")
```

### Compiler-tason muutos (`backend_v2/services/orchestrator/localization_compiler.py`)
Prompt compiler kokoaa näistä kentistä dynaamisesti tarkan ja yksiselitteisen XML-hierarkian LLM:lle:
```xml
<tda_validation>
    <anchor_target>{{ anchor_target }}</anchor_target>
    <search_scope>{{ bounding_box_scope }}</search_scope>
    <validation_rule>{{ extraction_rule }}</validation_rule>
</tda_validation>
```

### Frontend-tason muutos (Admin Studio V2)
Model Registry UI ei enää esitä yhtä suurta tekstikenttää, vaan rakentaa dynaamisen Formin:
- **Anchor Target** (Tekstikenttä)
- **Bounding Box** (Dropdown: Sentence / Paragraph / jne.)
- **Extraction Rule** (Tekstikenttä)

## 3. Toteutusvaiheet (Implementation Phases)
1. **Pydantic Skeeman Päivitys:** Muutetaan `TDAAssertion` ja lisätään uudet kentät, sekä päivitetään pydantic testit.
2. **ETL-Migraatio (Seed Data):** Kirjoitetaan skripti, joka parsii Regexillä nykyisistä `concept_description` -teksteistä irti `STEP 1:`, `STEP 2 (Bounding Box):` ja `EXTRACTION CONDITION:` osuudet ja siirtää ne uusiin JSON-kenttiin `seed_data.json`:issa.
3. **Backend Logic & Compiler:** Päivitetään `localization_compiler.py` hyödyntämään uusia kenttiä ja formatoimaan puhdas XML. Poistetaan vanha logiikka, joka luotti `concept_description` -merkkijonon sisältöön.
4. **Frontend / Admin Studio V2:** Päivitetään Flutter-käyttöliittymän List-Editor tukemaan näitä uusia kenttiä Opaque Stripe ID Patternin mukaisesti. 

## 4. Riippuvuudet ja Edellytykset
- **Epic Bilingual Schema Refactor** -tietokantamuutoksen ja puhdistuksen (Zero-Anchors ETL) täytyy olla täysin valmis ja ajettuna kantaan ennen tämän Epicin aloittamista.
