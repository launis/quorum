# P3: Dual Negation Hazardin korjaaminen (Code-as-a-Judge)

## Tavoite
Poistaa LLM:ltä käänteisen logiikan (inverse) arviointitaakka ja siirtää looginen flippaus (PASS ↔ FAIL) yksinomaan backendin deterministiseksi tehtäväksi (Code-as-a-Judge).

## Toimenpiteet
1. **Ohjeen poisto promptista:** Muokkaa `localization_compiler.py` (tai vastaava tiedosto). Poista kaikki viittaukset inverse-logiikkaan LLM:n ohjeistuksesta. LLM:n tehtävä on ainoastaan uuttaa, löytyykö piirre tekstistä.
2. **Backendiin Audit-loki:** Vahvista `ChunkWorker.evaluate_extraction` (tai vastaava metodin) logiikkaa lisäämällä selkeä AppException/logger.debug -loki, kun Code-as-a-Judge suorittaa flippauksen (PASS -> FAIL). (Viite: Rule 18).
3. **Immuutti tila (State Immutability):** Kun `ChunkWorker` tekee käännöksen, alkuperäistä objektia EI SAA mutatoida (esim. `obj.status = "FAIL"`). Luo uusi kopio Pydantic-rakenteilla: `obj.model_copy(update={"status": "FAIL"})`. (Viite: Rule 14, 91).

## Säännöt ja Rajoitteet
- **Rule 17 (`the_duct_tape_ban`):** Negaation ohjelmallinen hallinta on ainoa hyväksytty tapa; promptin negaatiot ovat purkkavirityksiä ja kiellettyjä.
- **Rule 22 (`zero_legacy_fallback_hacks`):** Legacy fallback hackit ovat kiellettyjä; data puuttuu -> Fail-Fast crash.
- **Rule 18 (`rfc7807_dual_reporting_strict`):** Flippauksen mahdolliset virheet ja itse lokitus pitää aina hoitaa rakenteellisella Quorum AppException -/ logger.debug -mallilla.
- **Rule 14 (`frozen_state_mutability`) & 91 (`pydantic_mutation_optimization_mandate`):** `ConfigDict(frozen=True)` ja `model_copy(update=...)`.
