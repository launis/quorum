# Phase 4 Implementation Plan: Isolated Runtime AI (Matrix Evaluation Node)

Tavoite: Toteuttaa täysin sokea, eristetty tekoäly-arviointi (T=0.0). Tekoäly prosessoi `atom_flattening`-pre-hookista tulevan sekoitetun litanian (array) ilman matriisin kontekstivihjeitä ja palauttaa pelkästään Micro-CoT -analysoidut boolean-arvot.

## User Review Required
> [!IMPORTANT]
> - Model Registryyn lisätään `blind` strategia Geminille (T=0.0, Flash tai Pro).
> - Backendin `prompt_compiler.py` saa kaksi uutta metodia, jotta Pydantic-tason Structured Outputs ja sokea System Prompt saadaan täsmäämään 100-prosenttisesti vaatimuksia.

---

## Proposed Changes

### Backend Core & Configuration

#### [MODIFY] [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)
- Add new `blind` model strategy inside the Model Registry (`sys_e26807f3bfa3454d`).
- Configuration: `model_name="vertex_ai/gemini-2.5-flash"`, `temperature=0.0`, `supports_grounding=False`, with standard RPM/TPM limits and `parsing_mode="GEMINI_JSON"`.

#### [MODIFY] [prompt_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/prompt_compiler.py)
- **`build_blind_evaluation_schema()`**: Add a dedicated schema builder for the blind extraction. Returns a dynamic Pydantic model enforcing `{"evaluations": List[AtomResponse]}` where `AtomResponse` includes:
  - `atom_id` (str): Suora yhdiste Flattening-hookin generoimaan hash-avaimeen.
  - `quote` (str | None): Pakotettu lainaus alkuperäisestä tekstistä Micro-CoT säännöllä.
  - `reasoning` (str): Kognitiivinen kitka ja arvioinnin perustelu.
  - `boolean` (bool): Puhdas True/False -osumapäätös.
- **`compile_blind_system_instruction()`**: Luodaan Micro-CoT Prompt-blokki system-rooliin. Tämä ohjeistaa tekoälyä toimimaan mekaanisena, empatiattomana data-erottelijana, pakottaen täyden sokeuden eikä salli matriisisarakkeiden ryhmittelyä. Tässä sovelletaan "Duck-Typing Token Shield" konseptia.

---

## Open Questions
> [!NOTE]
> - Ajatarvitaanko `AtomResponse` Pydantic mallin tyyppimääritykseen laajennusta (esim. poikkeusten käsittely) vai riittääkö puhdas kolmikko (quote, reasoning, boolean)? Nyt määritelty tuolla kolmikolla ja `atom_id`:llä.

---

## Verification Plan

### Automated Tests
- Varmennetaan OpenAPI JSON schema ajamalla:
  `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py --openapi`
- Ajetaan testit (sisältää uudet tai muuttuvat PromptCompiler Pydantic -rutiinit):
  `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py --test`
- Varmennetan, että seed_data on edelleen rakenteellisesti ehyt:
  `uv run pytest backend_v2/tests/unit/test_seed_schema_alignment.py -v`

### Manual Verification
- Tarkastetaan myöhemmin lokidatasta (tai testipenkin kautta), ettei sokea LLM-promptisynteesi "vuoda" vahingossa matriisien tai dimensioiden nimiä LLM-kontekstiin.
