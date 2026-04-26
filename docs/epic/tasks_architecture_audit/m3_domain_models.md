# Epic 40, Milestone 3: Domain Models

## Tavoite
Päivittää `docs/architecture/02_domain_models.md` vastaamaan koodipohjan nykytilaa, erityisesti Phase 9:n "Zero-Compromise" -muutosten myötä lisättyjen tiukkojen Pydantic-mallien osalta.

## Tarkistettavat tiedostot
- `backend_v2/models/domain/synthesis.py` (SynthesisStepDataDTO, SynthesisMetadataDTO)
- `backend_v2/models/dtos/lightweight_matrix.py` (StrictMatrixPayload, LightweightMatrixOutput, MicroCotDTO)
- `backend_v2/models/domain/scoring.py` (StepGuardDTO, StepFalsifierDTO, StepPanelDTO)
- `backend_v2/models/domain/xai.py` (XAIExtension, Discriminated Unions)

## Löydökset & Puutteet `02_domain_models.md` -dokumentissa

1. **Synthesis DTOs puuttuvat:** `SynthesisConfigDTO` on mainittu dokumentissa, mutta Phase 9:ssä tuodut `SynthesisStepDataDTO` ja `SynthesisMetadataDTO` (strict=True, frozen=True) puuttuvat täysin kuvauksesta. Nämä varmistavat Fail-Fast -injektion `synthesis.py`:n datanpurussa.
2. **Scoring ja Lightweight Matrix -mallit puuttuvat:** Vaikka dokumentti korostaa Zero-Duck-Typingia, sieltä puuttuu kuvaus siitä, miten Matrix-tuloksia validoidaan tiukasti `StrictMatrixPayload` ja `LightweightMatrixOutput` -malleilla (jotka korvasivat "naked dictionary" -arvioinnit scoring-koukussa). Myös arvioinnin validointimallit (`StepGuardDTO`, `StepFalsifierDTO`, `StepPanelDTO`) loistavat poissaolollaan.
3. **XAIExtension puuttuu:** Uudessa XAI-mallissa (`xai.py`) esitelty polymorfinen `XAIExtension` -rakenne (Discriminated Union `extension_type` -kentällä) on avainasemassa Token Shielding- ja Fail-Fast -arkkitehtuurissa, mutta sitä ei ole dokumentoitu.
4. **Mermaid-kaavion päivitys:** Nykyisessä Mermaid-kaaviossa tulisi näyttää, miten `StrictMatrixPayload` / `LightweightMatrixOutput` ja polymorfiset `XAIExtension` -mallit linkittyvät ydinmalleihin.

## Ehdotetut muutokset (Suunnitelma)

1. **Uusi alaluku: "Phase 9: Strict Hook DTOs & Micro-CoT Validation":** Lisätään dokumentin loppuun tai ydinmallien oheen osio, joka kuvaa `models/domain/` ja `models/dtos/` hakemistojen Pydantic V2 -puhtautta (strict, frozen, extra="forbid" / "ignore"). Mainitaan tässä:
   - `SynthesisStepDataDTO` ja `SynthesisMetadataDTO`
   - `StrictMatrixPayload` (RootModel) ja `LightweightMatrixOutput`
   - `StepGuardDTO`, `StepFalsifierDTO`, `StepPanelDTO` scoring-kontekstissa.
2. **Uusi alaluku: "Polymorfinen XAI-injektio (Discriminated Unions)":** Kuvataan `xai.py`:n `XAIExtension` -malli ja sen tärkeys Fail-Fast arkkitehtuurissa (estää väärien laajennustyyppien renderöinnin).
3. **Mermaid-kaavion laajennus:** Lisätään kaavioon `XAIExtension` ja `LightweightMatrixOutput`, ja näytetään miten nämä rikastavat `ReportDataDTO` / `ReportLayoutDTO` -rakenteita.
