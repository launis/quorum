# P1: Schema Purity Mandate & Clean Slate Retries

## Tavoite
Estää Pydantic-validointivirheet (erityisesti `condition_met` -hallusinaatiot) tiukentamalla Pydantic-skeemoja, kieltämällä keksityt kentät promptissa ja varmistamalla "puhtaan pöydän" uudelleenyritykset.

## Toimenpiteet
1. **Pydantic Strict Mode:** Varmista, että kyseiset mallit (esim. `AtomResponse` ja chunk-vastaukset) sisältävät: `model_config = ConfigDict(strict=True, extra="forbid")`. (Viite: Rule 2, 73).
2. **Schema Purity XML:** Lisää promptin staattiseen osaan (esim. `compile_xml_rubrics()`) eksplisiittinen `<SCHEMA_PURITY_MANDATE>`-lohko, joka kieltää uusien JSON-kenttien luomisen.
   - *Huom: Jos muokkaat `prompt_compiler.py`:tä, huomioi Rule 177. Varmista tarvittaessa käyttäjän hyväksyntä.*
3. **Healing Prompt:** Päivitä `get_schema_healing_prompt()` selittämään tarkasti, *miksi* ylimääräiset kentät hylättiin. (Viite: Rule 20).
4. **Clean Slate Retries:** Varmista `LLMTaskExecutor`:ssa, että kun malli kaatuu validointivirheeseen, sen generoimaa viallista JSON-roskaa ei lisätä keskusteluhistoriaan (`messages` / `history`), vaan uudelleenyritys tehdään puhtaalla state-kutsulla ja uusin healing-ohjein.

## Säännöt ja Rajoitteet
- **Rule 2 (`strict_pydantic_v2_rust`):** `strict=True, extra='forbid'`
- **Rule 20 (`the_self_healing_ban`):** Ei Regex-parsintaa, data validation belongs 100% to Pydantic.
- **Rule 73 (`anti_hallucination_guardrail`):** Älä hallusinoi uusia Pydantic-malleja.
- **Rule 177 (`prompt_compiler_immutability`):** Ole varovainen `prompt_compiler.py`:n muokkaamisessa.
