# P4: Atom-to-Rule Mapping ja Sokea DTO -projisointi

## Tavoite
Ratkaista rakenteellinen Atom-to-Rule Mapping -vuoto hybridimallilla, jossa atomin ja säännön linkitys tehdään promptissa täysin eksplisiittiseksi ilman attention driftiä.

## Toimenpiteet
1. **`FlattenedAtom` -laajennus:** Laajenna skeemaa (`atom_flattening.py`) lisäämällä kentät `extraction_rule`, `anchor_target`, ja `is_inverse`. 
   - *Poikkeus Rule 8 (`duck_typing_token_shield_exception`):* `FlattenedAtom` saa käyttää `extra="ignore"` token-suojauksen varmistamiseksi.
2. **Rubriikin rajaus (`compile_xml_rubrics`):** Varmista, että prompt-compiler luo XML-rubriikkiin ainoastaan kyseisessä chunkissa oikeasti esiintyvien atomien säännöt.
3. **Sokea DTO -projisointi:** Kun atomeja syötetään LLM:lle, luo rajattu DTO (esim. `atom_id`, `rule_anchor`, `question`). Älä syötä koko laajennettua `FlattenedAtom`-objektia, jotta `is_inverse` ja muu backend-logiikka ei vuoda mallille ja kumoa P3-korjausta.
4. **Opaakit Ankkurit:** Käytä `rule_anchor`-kentässä opaakkeja tiivisteitä (esim. `tda_123`), jotta LLM joutuu mekaanisesti lukemaan vastaavan `<rule id="tda_123">` -XML-lohkon eikä arvaa tulosta semantiikan perusteella.

## Säännöt ja Rajoitteet
- **Rule 29 (`high_fidelity_prompting`):** Dynaamiset muuttujat eristetään `<execution_parameters>`-tagiin, ydin pysyy staattisena prompt cachen vuoksi.
- **Rule 51 (`hybrid_prompting_mandate`):** Hybridipromptaus: XML rakenteeseen, Markdown sisältöön.
- **Rule 52 (`ephemeral_caching_topology`):** System prompt 100% staattinen cachen maksimoimiseksi.
- **Rule 8 (`duck_typing_token_shield_exception`):** `FlattenedAtom` on Data Projection Model, eli `extra="ignore"` on sille poikkeuksellisesti sallittu.
- **Opaque Stripe ID Mandate:** Opaakit ankkurit.
