# Phase 1: Arkkitehtuuritason Luotettavuus (Falsification & Fuzzy Match)
Source: Epic System 2 Reliability Fixes, Phase 1

## Tavoite
Poistaa False Negative -virheet (turvallinen Fuzzy Match) ja tappaa "Yes Man" -bias logit-tasolla (Falsification Attempt), tavoitteena Kappa 0.70-0.75 ilman Pydantic DLQ -virheitä.

## Invariantit
- **00-antigravity-core.md**: Fail-Fast Pydantic V2 definitions.
- **01-python-backend.md**: Strict typing, no silent error swallowing.

## Tiedostot
- **TARGET (Modify)**: `c:\src\quorum\backend_v2\models\dtos\evaluation_steps.py`
- **TARGET (Modify)**: `c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py`
- **TARGET (Modify)**: `c:\src\quorum\backend_v2\services\orchestrator\strategies\llm_execution\chunk_worker.py`

## Tehtävät

### 1. Paholaisen Asianajaja (Falsification)
Tiedosto: `evaluation_steps.py`
- Lisää `falsification_argument: str` uutena kenttänä aivan juuri **ennen** `decision` -booleania sekä `StepDTOStrict` että `StepDTOSemantic` -luokkiin.
- Description: "Pakollinen vastaväite: Miksi tämä todiste EI ehkä täytä säännön tiukkaa kausaalivaatimusta. Keksi ainakin yksi argumentti ennen päätöstä."
- Tarkoitus: Pakottaa LLM generoimaan negatiivista autoregressiivistä kontekstia ennen `decision` -tokenia, tuhoten "Yes Man" -biasin.

### 2. Deterministinen Fuzzy Match & Entropiaportti
Tiedosto: `anchor_validation_service.py`
- Muuta `validate_evidence` parametrit ottamaan vastaan `strictness_level: int = 50`.
- Implementoi Entropiaportti: Jos `len(exact_quote) < 20`, vaadi 100% osuma (ei RapidFuzzia) hallusinaatioiden estämiseksi.
- Implementoi Discrete Tiers (Porraskaava) pituuden ollessa >= 20:
  - 100 -> 100.0%
  - 85 -> 95.0%
  - 50 -> get_lexical_fuzz_threshold(locale) (yleensä 80.0%)
  - 30 -> 65.0%
- Vertaile `fuzz.partial_ratio(quote, text) >= tier_kynnys`. Jos kyllä, hyväksy.

### 3. Parametrin Välitys
Tiedosto: `chunk_worker.py`
- Varmista että `strictness_level` siirtyy kutsussa `AnchorValidationService.validate_evidence` asti.

## Testing & Quality Gate Plan
1. **Yksikkötestit:** Laajenna `test_anchor_validation.py` kattamaan < 20 merkin vaatimus (Entropiaportti) ja 85/50/30 strictness-portaiden toiminta.
2. **Quality Gate:** Aja `uv run python scripts/backend_audit_loop.py c:\src\quorum\backend_v2 --test`
3. Varmista Pytest, Ruff ja MyPy läpimeno ilman varoituksia.

---
## Session Handover
Valmis! Siirry Master Trackerin pariin jatkaaksesi prosessia.
