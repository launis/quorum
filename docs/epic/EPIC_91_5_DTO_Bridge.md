# Epic 91.5: The Universal DTO Bridge (Vaihe 1/3)

> [!IMPORTANT]
> Tämä on ensimmäinen osa kolmivaiheisesta arkkitehtuurimigraatiosta (Epic 91.5 -> Epic 92 -> Epic 93). 
> Tämän Epicin ainoa tavoite on luoda uusi datakontrakti (Pydantic DTO) ja pakottaa nykyinen ohjelmisto käyttämään sitä. Vasta tämän jälkeen aletaan rakentamaan uutta AI-moottoria (Epic 92) tai käyttöliittymän renderöintiä (Epic 93).

## 1. Yhteenveto ja Tavoite (Objective)

Quorumin järjestelmä kärsii tällä hetkellä epäyhtenäisistä tietorakenteista (Nested Trees, raw Markdown payloadit). Jotta voimme myöhemmin rakentaa asynkronisen DAG-moottorin ja Server-Driven UI:n (SDUI), meidän on ensin lukittava **yksi absoluuttinen datamuoto**.

Epic 91.5 luo **Flat Adjacency List** -muotoisen DTO-kannan. Se erottaa dynaamisen suoritustilan (`results`) staattisesta tekstidatasta (`hydrated_references`), minimoiden payloadin koon ja maksimoiden Pydantic V2:n suorituskyvyn.

---

## 2. Pydantic V2 DTO -Määrittely (01-python-backend.md Compliance)

Nämä mallit muodostavat uuden sillan Backendin ja Frontendin/PDF-generaattorin välille. Mallit on jäädytetty (`frozen=True`) mutaatioiden estämiseksi.

Tiedosto: `backend_v2/models/dtos/report.py`

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Literal

StatusType = Literal['PASSED', 'FAILED', 'N_A', 'SYSTEM_ERROR', 'BLOCKED', 'PENDING']

class HydratedAtomDTO(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)
    resolved_claim: str = Field(description="Puhdistettu väite ihmiskielellä")
    source_quote: str = Field(description="Sanatarkka alkuperäinen lainaus dokumentista")

class AtomResultDTO(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)
    tda_id: str = Field(description="Opaque ID, joka viittaa hydrated_references -avaimeen")
    status: StatusType
    depends_on_tda_ids: List[str] = Field(default_factory=list)
    short_circuit_reason_tda_ids: List[str] = Field(default_factory=list)
    evaluation_reasoning: str | None = Field(default=None)

class ExecutionMetricsDTO(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)
    total_atoms: int
    evaluated: int
    short_circuited_na: int
    final_score_percentage: float | None = Field(default=None)
    completeness_ratio: float = Field(description="Zero-Compromise -mittari")

class ReportDataDto(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)
    execution_id: str
    global_metrics: ExecutionMetricsDTO
    results: List[AtomResultDTO]
    hydrated_references: Dict[str, HydratedAtomDTO] = Field(
        description="O(1) Sanakirja: tda_id -> Staattinen teksti. SDUI hakee näyttötekstit täältä."
    )
```

---

## 3. Pakotettu Migraatio ja No Fallback -politiikka

Järjestelmä on siirrettävä käyttämään tätä uutta DTO:ta välittömästi. Koska emme ole vielä rakentaneet Epic 92:n moottoria, teemme muutoksen nykyiseen järjestelmään:

1. **Tilapäinen Adapteri (Backend):** Nykyisen ("vanhan") moottorin tulosteet mapataan ohjelmallisesti tähän uuteen `ReportDataDto` -muotoon juuri ennen API-palautusta. Vaikka taustalla ei vielä ole oikeaa DAG-moottoria, API näyttää ulospäin täsmälleen samalta kuin tuleva tavoitetila.
2. **Käyttöliittymä ja PDF:** Flutter ja Jinja2 PDF-pohjat refaktoroidaan lukemaan **vain** tätä uutta litteää JSON-muotoa ja sen `hydrated_references` -sanakirjaa.
3. **No Fallback:** Kun tämä silta on rakennettu, kaikki vanhat DTO:t, vanhat API-endpointit ja vanhat käyttöliittymäkomponentit poistetaan koodikannasta. Emme ylläpidä rinnakkaisajoja. Vanhan mallin käyttäminen uuden rinnalla on ankarasti kielletty (Fail-Fast).

## 4. Definition of Done (DoD)
* Uudet Pydantic-mallit on koodattu ja testattu.
* API palauttaa yksinomaan `ReportDataDto` -objekteja.
* Käyttöliittymä ja PDF-generaattori eivät hajoa, vaan osaavat hakea tekstinsä O(1)-hakuna `hydrated_references` -sanakirjasta.
* Vanhat DTO-mallit on tuhottu koodikannasta.

Tämän Epicin suorittamisen jälkeen järjestelmä toimii 100%, ja on valmis Epic 92:n (DAG Moottorin) käyttöönottoon.
