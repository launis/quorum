> **STATUS: PENDING / ODOTTAA TOTEUTUSTA (Tuleva PostgreSQL 17+ & SQLAlchemy 2.0 -migraatiosuunnitelma)**
> **ARKITEHTUURIPERIAATE: "All-in-PostgreSQL" (Single-Engine Sovereign Storage Architecture)**
> **KOLMIVAIHEINEN TIEKARTTA & ARKKITEHTUURISET RIIPPUVUUDET (The Tripartite Roadmap):**
> 1. **Täydellinen poisto (Scrap)**: Tämän suunnitelman toteutus poistaa ja korvaa kokonaan `TinyDBDriver`-ajurin (`backend_v2/database/tinydb_driver.py`), tiedostotietokantakääreen (`backend_v2/database/wrapper.py`), `db_v2.json`-tiedoston ja tiedostolukituksen (`db_v2.json.lock`). Tämän vuoksi in-memory tilasiirtymässä (@[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md]) tai vanhoissa korjauksissa tiedostolukituskoodiin ei tehdä lainkaan rakenteellisia rinnakkaisuus- tai asynkronointikorjauksia (estetään kuolevan koodin ylikorjaus).
> 2. **DTO-mallien ja in-memory tilasiirtymän suora hyödyntäminen (Invest & Re-Use)**: Suunnitelmassa @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] (Vaihe 1) puhdistetut ja tiukasti tyypitetyt Pydantic V2 DTO -mallit (`ExecutionRecord`, `WorkflowInputs`, `ContextVariablesDTO`, `FrozenContext`, `EvaluatedAtomDTO`, `HookDeltaDTO`, `ReportDataDTO`, `TraceEventMetadataDTO`, `StepOutputContentDTO`, `ProgressTracePayloadDTO`, `LightweightMatrixOutput`, `GlobalContextVarsDTO`) siirtyvät **sellaisenaan 1:1** PostgreSQL-migraatioon muodostaen `JSONB`- ja `BYTEA`-tallennuskenttien pysyvän sovellustason validointipohjan.
> 3. **Nollatoleranssi alastomille sanakirjoille (Zero Naked Dicts Ironclad Mandate)**:
>    - **3.1 Ei alastomia sanakirjoja ORM-malleissa**: SQLAlchemy 2.0 -malleissa kielletään ehdottomasti `Mapped[dict[str, Any]]` ja `Mapped[list[dict[str, Any]]]`. Kaikki `JSONB`-sarakkeet tyypitetään ja sidotaan suoraan Pydantic V2 DTO -malleihin käyttämällä `PydanticJSONB`-tyyppikäärettä (`TypeDecorator[T]`) ja Pydantic V2 `TypeAdapter[T]` -moottoria.
>    - **3.2 Ei välisanakirjoja orkestroijassa tai service-kerroksessa**: Suunnitelman @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] ansiosta DAG-orkestroija operoi 100 % puhtailla DTO-olioilla (`TraceEventMetadataDTO`, `StepOutputContentDTO`, `ExecutionInputsDTO`). Tilapäisten päivityssanakirjojen (`updates: dict[str, Any]`, `fc_updates: dict[str, Any]`, `cv_dict: dict[str, Any] | None`, `delta_content_dict: dict[str, Any]`, `step_generated_schemas: dict[str, Any]`) luominen tai `**kwargs`-purku on kielletty. Tilasiirtymät ja tallennukset suoritetaan suoraan vahvasti tyypitettyjen DTO-olioiden ja ORM-attribuuttien kautta.
>    - **3.3 Ei sanakirjamuunnoksia kyselyissä tai repository-rajapinnassa**: Repository-metodit eivät saa koskaan palauttaa sanakirjoja (`dict(row)`, `row._mapping`, `.mappings().all()`) eivätkä vastaanottaa sanakirjoja parametreina (`filter_by(**dict)`). Kaikki haku- ja tallennusoperaatiot toimivat puhtaasti Pydantic-domain-mallien ja DTO-olioiden varassa.
>    - **3.4 Täydellinen 10 taulun suljettu topologia**: Järjestelmän kaikki 10 entiteettityyppiä (`users`, `organizations`, `workflows`, `steps`, `prompt_blocks`, `output_profiles`, `system_configs`, `executions`, `report_artifacts`, `report_binaries`) mallinnetaan erillisinä, vahvasti tyypitettyinä tauluina. Geneeristen "säiliötaulujen" (kuten `components(data: JSONB)`) luominen on kielletty.
>    - **3.5 Litteät FinOps-sarakkeet**: Token- ja kustannustelemetria tallennetaan suoriksi `BigInteger`- ja `Numeric`-sarakkeiksi, ei koskaan JSON-sanakirjoiksi (SSOT).
> 4. **Repositorioiden QGR003-poikkeusten ja ajurirajapinnan sanakirjavuotojen keskittäminen tähän suunnitelmaan (Scope Quarantine & Throwaway Work Ban)**:
>    - Koodikannan AST-auditoinnissa tunnistetut 13 kpl repositorioiden `QGR003` -poikkeusrikkomuksia (laajat `except Exception:` -käsittelijät tiedostoissa `knowledge.py`, `audit.py`, `workflow.py`, `identity.py`, `base.py`), tietokanta-ajurin kantaluokan (`backend_v2/database/driver.py`) 5 alastonta sanakirjaa (`load`, `save`, `query`) sekä seederin (`backend_v2/seed/run_seed.py`) tiedostokäsittelyt **on nimenomaisesti rajattu korjattavaksi VASTA tässä PostgreSQL-migraatiossa**.
>    - **Perustelu**: Quorum käyttää tällä hetkellä poistuvaa `TinyDBDriver`- ja `FirestoreDriver`-kantaa. Jos TinyDB:n tiedostolukitus- ja JSON-poikkeuksia korjattaisiin ennen migraatiota, se olisi hukkatyötä (*throwaway work*), koska vanhat koodirivit heitetään kokonaan roskiin uuden ajurin myötä. Tässä suunnitelmassa repositorioiden virheenkäsittely toteutetaan suoraan puhtailla SQLAlchemy 2.0 / asyncpg -poikkeusluokilla (`IntegrityError`, `NoResultFound`, `OperationalError`) ilman yhtäkään laajaa `except Exception:` -käsittelijää.
> 5. **Pysyvyysentiteettien Pydantic V2 -esivalmistelu (Pre-Flight Schema Sanitization - Scope Absorption)**:
>    - Tietokannan `JSONB`-sarakkeisiin suoraan tallennettavat domain- ja DTO-mallit (`SystemConfigModelRegistry`, `SystemConfigMCPGateways`, `EvaluatedAtomDTO`, `XAIReportEnvelope`), joissa esiintyy 17 kpl alastomia sanakirjoja ja primitive obsession -rakenteita (`system_config.py`, `mcp.py`, `xai.py`, `atom_evaluation.py`, `validation.py`, `studio.py`), siivotaan ja tyypitetään puhtaiksi tämän suunnitelman **Vaiheessa 1.5** ennen ORM-taulujen ja Alembic-migraatioiden ajamista. Tämä takaa, että PostgreSQL 17+:n `JSONB`-sarakkeisiin ei päädy yhtäkään `dict[str, Any]` -avainta.
> 6. **Jatkosuhde Vaiheeseen 3 (LLM-Adapterit & Oheisrajapinnat - @[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_Adapter_Strict_Typing.md])**:
>    - Tämän PostgreSQL-migraation jälkeen jäljelle jäävät ainoastaan ulkoisten tekoäly-SDK:iden adapterisanakirjat (`backend_v2/llm/adapters/`, n. 50 kpl) ja oheiskoukut (`hooks/`, `registry.py`), jotka taklataan omassa itsenäisessä suunnitelmassaan Vaiheessa 3 vaarantamatta tietokantaa tai suoritusputkea. Tämän ansiosta koko backend saavuttaa tasan 0 rikkomuksen tilan.

---

### **YHTEENVETO & PÄÄPERIAATE: "All-in-PostgreSQL"**

Tässä suunnitelmassa Quorum ottaa käyttöön **"All-in-PostgreSQL" -periaatteen**:
1. **PostgreSQL 17+ on järjestelmän ainoa totuuden lähde ja ainoa tallennuspaikka (Single Source of Truth & Sole Storage)**.
2. **Nolla ulkoista tiedostovarastoriippuvuutta**: Erilliset ulkoiset pilvitallennukset (Firebase Storage, AWS S3, Google Cloud Storage) ja niihin liittyvät Signed URL -viritykset hylätään tarpeettomina.
3. **Kaksitasoinen tallennusratkaisu PostgreSQL:n sisällä**:
   - **SDUI & Kognitiiviset puut (`JSONB`)**: Server-Driven UI -esitysmalli (`report.sdui.json`), evaluointiverkko (`atom_evaluations`), työnkulut, askeleet, prompt-lohkot ja profiilit tallennetaan natiivisti `JSONB`-muodossa Pydantic-mallien validoimana, jolloin haut ovat millisekuntiluokkaa ja indeksoitavissa.
   - **Valmiit raportit ja binäärit (`BYTEA` erillistaulussa)**: PDF-raportit (`report.pdf`) ja syötedokumentit tallennetaan eristettyyn `report_binaries`-tauluun PostgreSQL:n TOAST-arkkitehtuurin (The Oversized-Attribute Storage Technique) suojaamana. Tällöin päätaulujen kyselyt eivät koskaan kuormita tietokannan välimuistia (`shared_buffers`) raskaalla binaaridatalla.
4. **Täydellinen ACID ja automaattinen siivous**: Viiteavaimet (`ON DELETE CASCADE`) takaavat, että kun ajo poistetaan, kaikki siihen liittyvät raportit, SDUI-puut ja PDF-binaarit tuhoutuvat samassa mikrosekunnin transaktiossa. Orpoja tiedostoja ("Orphaned Files") tai GDPR split-brain -tilanteita ei voi matemaattisesti syntyä.

---

### **IMPLEMENTOINTISUUNNITELMA**

#### **Vaihe 1: Moderni Infra ja Työkalupakki (uv-natiivi)**

PostgreSQL 17+ tuo mukanaan natiivin `uuidv7()`-tuen, tehokkaamman B-Tree-indeksoinnin, edistyneen JSONB-käsittelyn ja optimoidun TOAST-pakkauslogiikan.
Kaikki riippuvuudet hallitaan puhtaasti `uv`-työkalulla:

```powershell
uv add fastapi "sqlalchemy[asyncio]>=2.0" "psycopg[binary]>=3.0" asyncpg alembic pydantic pydantic-settings
```

*(Ulkopuoliset tallennuskirjastot `firebase-admin` ja `google-cloud-storage` on poistettu riippuvuuksista tarpeettomina).*

---

#### **Vaihe 1.5: Pysyvyysentiteettien Pydantic V2 -esivalmistelu (Pre-Flight Schema Sanitization)**

Ennen SQLAlchemy 2.0 ORM -mallien luontia ja ensimmäistä Alembic-migraatiota siivotaan ja tyypitetään ne pysyvät domain- ja DTO-mallit, jotka tallennetaan suoraan PostgreSQL:n `JSONB`-sarakkeisiin (17 kpl `audit_dict_eradication.py` -rikkomusta). Tämä estää skeemavuodot ja takaa, että `PydanticJSONB`-tyyppikääre validoi 100 % puhtaita malleja:

1. **`backend_v2/models/domain/system_config.py` & `backend_v2/models/domain/mcp.py`** (`system_configs` -taulun payload):
   - Korvataan `tools: list[dict[str, Any]] | None` vahvasti tyypitetyllä `list[MCPToolDefinition] | list[dict[str, JsonValue]] | None`.
   - Korvataan `parameters: dict[str, Any] | None` tyypitetyllä `dict[str, JsonValue] | None`.
   - Korvataan `mcp.py`:n `MCPToolCall`, `MCPToolDefinition` ja `MCPServerConfig` -sanakirjat `dict[str, JsonValue]` -rakenteilla.
2. **`backend_v2/models/domain/xai.py`** (`report_artifacts`- ja `output_profiles`-taulut):
   - Korvataan `XAIReportEnvelope.flat_report` ja `structured_data` (`dict[str, Any] | None`) tyypitetyllä `Annotated[dict[str, JsonValue] | None, Field(...)]`.
3. **`backend_v2/models/dtos/atom_evaluation.py`** (`executions.atom_evaluations` -sarake):
   - Ratkaistaan Primitive Obsession (`list[dict[str, JsonValue]]`) kapseloimalla `evaluated_matrix_references` ja `raw_xai_extensions` omiin keveisiin Pydantic V2 DTO -luokkiinsa (`EvaluatedMatrixReferenceDTO`, `RawXAIExtensionDTO`).
4. **`backend_v2/models/domain/validation.py` & `backend_v2/models/dtos/studio.py`**:
   - Korvataan `validation.py`:n `root: dict[str, Any]` ja `metadata: dict[str, Any]` muotoon `dict[str, JsonValue]`.
   - Korvataan `studio.py`:n `trace_metadata` ja apusanomat muotoon `dict[str, JsonValue]`.

Ajon jälkeen `uv run python scripts/audit_dict_eradication.py backend_v2/models/domain/system_config.py backend_v2/models/domain/mcp.py backend_v2/models/domain/xai.py backend_v2/models/dtos/atom_evaluation.py backend_v2/models/domain/validation.py backend_v2/models/dtos/studio.py` antaa tasan 0 rikkomusta.

---

#### **Vaihe 2: Tietokantamallit (Stripe-prefixed UUIDv7 & Suljettu 10 Taulun Topologia)**

Kaikki taulut noudattavat Quorumin kanonista Opaque Stripe ID -standardia (`pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$"`). B-Tree-indeksien pirstaloitumisen estämiseksi ID:n heksasuffiksi generoidaan aikajärjestetystä UUIDv7:stä (`f"{prefix}_{uuid6.uuid7().hex}"`).

**`backend_v2/database/models.py`**:

```python
from datetime import datetime
from typing import Any
from pydantic import BaseModel, TypeAdapter
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import BYTEA, JSONB
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionStep, ExecutionStepState, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
from backend_v2.models.domain.step import ExpectedInput, QuestionnaireItem, StepRule
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.dtos.atom_evaluation import EvaluatedAtomDTO
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.render import ReportDataDTO
from backend_v2.models.state import TraceEvent

class Base(DeclarativeBase):
    pass

class PydanticJSONB[T](TypeDecorator[T]):
    """SQLAlchemy 2.0 TypeDecorator providing 100% typed bidirectional Pydantic V2 JSONB mapping via TypeAdapter.
    
    Guarantees absolute eradication of naked dictionaries:
    - Supports single Pydantic models (WorkflowInputs, ContextVariablesDTO, FrozenContext, ReportDataDTO, OutputProfile).
    - Supports polymorphic discriminated unions (AnyPromptBlock, SystemConfigModelRegistry | SystemConfigMCPGateways).
    - Supports collections of models (list[EvaluatedAtomDTO], list[ExecutionStep], list[ExpectedInput], list[StepRule], list[TraceEvent]).
    - Supports typed mapping models (dict[str, ExecutionStepState], dict[str, int]).
    - Directly executes Rust-accelerated dump_python and validate_python without intermediate dict bridges.
    """
    impl = JSONB
    cache_ok = True

    def __init__(self, target_type: type[T] | Any) -> None:
        super().__init__()
        self.target_type = target_type
        self._adapter: TypeAdapter[T] = TypeAdapter(target_type)

    def process_bind_param(self, value: T | None, dialect: Dialect) -> Any:
        if value is None:
            return None
        return self._adapter.dump_python(value, mode="json")

    def process_result_value(self, value: Any, dialect: Dialect) -> T | None:
        if value is None:
            return None
        return self._adapter.validate_python(value)

class User(Base):
    """Käyttäjätunnukset ja tenant-eristys."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # usr_...
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="USER", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Organization(Base):
    """Tenant- ja organisaatioeristys."""
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # org_...
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class WorkflowRecord(Base):
    """Dynamic Directed Acyclic Graph orchestrator blueprint entity."""
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # wor_...
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    name: Mapped[I18nText] = mapped_column(PydanticJSONB(I18nText), nullable=False)
    description: Mapped[I18nText] = mapped_column(PydanticJSONB(I18nText), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)
    version: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    organization_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    default_profile_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mcp_gateway_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model_registry_id: Mapped[str] = mapped_column(String(64), nullable=False)
    default_strictness_level: Mapped[int] = mapped_column(BigInteger, default=50, nullable=False)
    security_penalty: Mapped[float] = mapped_column(Numeric(4, 3), default=0.0, nullable=False)
    post_hoc_penalty: Mapped[float] = mapped_column(Numeric(4, 3), default=0.0, nullable=False)
    passivity_penalty: Mapped[float] = mapped_column(Numeric(4, 3), default=0.0, nullable=False)
    enable_contextual_overrides: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enable_semantic_smoothing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enable_eager_anonymization: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    system_audit_trail: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    historical_context_mode: Mapped[str] = mapped_column(String(32), default="NONE", nullable=False)

    # 100 % tyypitetyt JSONB-sarakkeet ilman alastomia sanakirjoja:
    expected_inputs: Mapped[list[ExpectedInput]] = mapped_column(PydanticJSONB(list[ExpectedInput]), nullable=False, default=list)
    steps: Mapped[list[StepRule]] = mapped_column(PydanticJSONB(list[StepRule]), nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class StepRecord(Base):
    """Isolated, reusable orchestrator cognitive module."""
    __tablename__ = "steps"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # stp_...
    slug: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    organization_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    name: Mapped[I18nText] = mapped_column(PydanticJSONB(I18nText), nullable=False)
    description: Mapped[I18nText | None] = mapped_column(PydanticJSONB(I18nText), nullable=True)
    type: Mapped[str] = mapped_column(String(32), default="llm", nullable=False)
    hook: Mapped[str | None] = mapped_column(String(128), nullable=True)
    role_block_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    extraction_protocol_block_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    execution_persona_block_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # 100 % tyypitetyt JSONB-sarakkeet ilman alastomia sanakirjoja:
    rules: Mapped[list[StepRule]] = mapped_column(PydanticJSONB(list[StepRule]), nullable=False, default=list)
    questionnaire: Mapped[list[QuestionnaireItem]] = mapped_column(PydanticJSONB(list[QuestionnaireItem]), nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class PromptBlockRecord(Base):
    """Polymorphic PromptBlock storage preserving full type discriminated union."""
    __tablename__ = "prompt_blocks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # blk_...
    slug: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    organization_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    category_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    payload: Mapped[AnyPromptBlock] = mapped_column(PydanticJSONB(AnyPromptBlock), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class OutputProfileRecord(Base):
    """Output profile layout and synthesis presentation variant storage."""
    __tablename__ = "output_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # prf_...
    slug: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    workflow_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    organization_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    payload: Mapped[OutputProfile] = mapped_column(PydanticJSONB(OutputProfile), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class SystemConfigRecord(Base):
    """System configuration storage for Model Registries and MCP Gateways."""
    __tablename__ = "system_configs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # sys_...
    type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)  # model_registry or mcp_gateways
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[SystemConfigModelRegistry | SystemConfigMCPGateways] = mapped_column(
        PydanticJSONB(SystemConfigModelRegistry | SystemConfigMCPGateways), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class Execution(Base):
    """Phase 1: Ajon muuttumaton totuuden lähde (SSOT)."""
    __tablename__ = "executions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # exe_...
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    workflow_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    workflow_version: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)  # PENDING, RUNNING, PASSED, FAILED
    target_locale: Mapped[str] = mapped_column(String(10), default="fi", nullable=False)
    active_profile_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_profile_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    
    # FinOps & Telemetria suorina numeerisina sarakkeina (SSOT - Flat FinOps Law):
    prompt_tokens: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    cached_tokens: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    reasoning_tokens: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    cumulative_synthesis_tokens: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    total_cost_usd: Mapped[float] = mapped_column(Numeric(10, 6), default=0.0, nullable=False)
    dag_cost_usd: Mapped[float] = mapped_column(Numeric(10, 6), default=0.0, nullable=False)
    cumulative_synthesis_cost: Mapped[float] = mapped_column(Numeric(10, 6), default=0.0, nullable=False)
    duration_ms: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    
    # Syötteet, blackboard ja kognitiivinen tila 100 % tyypitettyinä Pydantic DTO -malleina (ZERO NAKED DICTS):
    raw_inputs: Mapped[WorkflowInputs] = mapped_column(PydanticJSONB(WorkflowInputs), nullable=False)
    context_variables: Mapped[ContextVariablesDTO] = mapped_column(PydanticJSONB(ContextVariablesDTO), nullable=False)
    frozen_context: Mapped[FrozenContext | None] = mapped_column(PydanticJSONB(FrozenContext), nullable=True)
    atom_evaluations: Mapped[list[EvaluatedAtomDTO]] = mapped_column(PydanticJSONB(list[EvaluatedAtomDTO]), nullable=False, default=list)
    steps: Mapped[list[ExecutionStep]] = mapped_column(PydanticJSONB(list[ExecutionStep]), nullable=False, default=list)
    step_states: Mapped[dict[str, ExecutionStepState]] = mapped_column(PydanticJSONB(dict[str, ExecutionStepState]), nullable=False, default=dict)
    execution_trace: Mapped[list[TraceEvent]] = mapped_column(PydanticJSONB(list[TraceEvent]), nullable=False, default=list)
    models_used: Mapped[dict[str, int]] = mapped_column(PydanticJSONB(dict[str, int]), nullable=False, default=dict)
    source_identity_manifest: Mapped[dict[str, str]] = mapped_column(PydanticJSONB(dict[str, str]), nullable=False, default=dict)
    
    is_resumable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # 1-to-N Relaatio tulosteisiin: Poisto siivoaa automaattisesti kaikki raportit ja niiden PDF-binaarit
    reports: Mapped[list["ReportArtifact"]] = relationship(
        "ReportArtifact", back_populates="execution", cascade="all, delete-orphan"
    )

class ReportArtifact(Base):
    """Phase 2/3: Ajon itsenäiset tulosteet ja Server-Driven UI -esitysmalli (0..N kpl)."""
    __tablename__ = "report_artifacts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # rep_...
    execution_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("executions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    output_profile_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="fi", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="GENERATING", nullable=False)  # GENERATING, READY, FAILED
    
    # Server-Driven UI -puu suoraan 100 % tyypitettynä ReportDataDTO-mallina (ZERO NAKED DICTS):
    sdui_payload: Mapped[ReportDataDTO | None] = mapped_column(PydanticJSONB(ReportDataDTO), nullable=True)
    
    has_pdf: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)

    execution: Mapped["Execution"] = relationship("Execution", back_populates="reports")
    
    # 1-to-1 Eristetty binaaritaulu: Raskas PDF pidetään poissa päätaulun muistisivuista
    binary: Mapped["ReportBinary | None"] = relationship(
        "ReportBinary", back_populates="artifact", uselist=False, cascade="all, delete-orphan"
    )

class ReportBinary(Base):
    """All-in-PostgreSQL Eristetty binaaritallennus (TOAST-optimoitu)."""
    __tablename__ = "report_binaries"

    report_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("report_artifacts.id", ondelete="CASCADE"), primary_key=True
    )
    mime_type: Mapped[str] = mapped_column(String(64), default="application/pdf", nullable=False)
    pdf_bytes: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    artifact: Mapped["ReportArtifact"] = relationship("ReportArtifact", back_populates="binary")
```

#### **Vaihe 2.0.1: Telemetrian tyyppiturvallisuus & TraceEvent-sanakirjojen hävittäminen (TraceEvent & TraceEventMetadataDTO SSOT)**

Toteutussuunnitelma @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] (Pre-Migration) hävittää vanhat alastomat sanakirjat (`dict[str, Any]`) `backend_v2/models/state.py`:n `TraceEvent`-mallista:
- `content: StepPayloadValue | TraceEventMetadataEnvelope | dict[str, JsonValue]`, missä `StepPayloadValue` on suljettu polymorfinen unioni (`StepOutputContentDTO | ExecutionInputsDTO | WorkflowInputs | LightweightMatrixOutput | SynthesisStarvationDTO | ProgressTracePayloadDTO`).
- `metadata: TraceEventMetadataDTO` (`ConfigDict(strict=True, extra="forbid", frozen=True)`), joka kapseloi vahvasti tyypitetyt telemetriakentät (`latency_ms`, `chunk_size`, `context_char_length`, `prompt_contexts`, `generated_schema`, `mcp_audit_traces`, `estimated_token_count`, `is_context_update`, `error_code`, `error_message`).

PostgreSQL-migraatiossa vanhaa `TraceEvent`-mallia ei tarvitse korvata rinnakkaisella DTO-luokalla, vaan suoritusputken valmiiksi tyypitetty ja kovetettu `TraceEvent` sidotaan suoraan `PydanticJSONB`-sarakkeeseen:

```python
# Execution.execution_trace hyödyntää suoraan valmiiksi kovetettua TraceEvent-mallia:
execution_trace: Mapped[list[TraceEvent]] = mapped_column(
    PydanticJSONB(list[TraceEvent]), nullable=False, default=list
)
```

Tällöin:
1. `Execution.execution_trace: Mapped[list[TraceEvent]] = mapped_column(PydanticJSONB(list[TraceEvent]), nullable=False, default=list)` takaa, että PostgreSQL:n JSONB-sarakkeeseen ei päädy yhtäkään `dict[str, Any]` -kenttää.
2. Myös Flutter-asiakkaalle suoratoistettava SSE-telemetria noudattaa samaa tiukkaa `TraceEvent`- ja `TraceEventMetadataDTO`-sopimusta.
3. PostgreSQL-suunnitelman sääntö 3.1 ("Ei alastomia sanakirjoja ORM-malleissa") ja sääntö 3.2 ("Ei välisanakirjoja orkestroijassa") toteutuvat 100 %:sesti ilman rinnakkaisia luokkia tai siirtymäkauden purkkapaikkauksia.

---

#### **Vaihe 2.1: Nollatoleranssi Repository- ja DAGExecutor-kerroksissa (Zero Naked Dicts Data Flow)**

Kaikki aiemmat tilapäiset apusanakirjat (`cv_dict`, `delta_content_dict`, `step_generated_schemas`, `updates: dict[str, Any]`, `fc_updates: dict[str, Any]`) poistuvat pysyvästi noudattaen viittä kultaista invarianttia:

1. **Invariantti 1: Ei sanakirjamuotoisia paluuarvoja (Zero Dict Returns)**:
   SQLAlchemy 2.0 palauttaa kyselyistä suoraan `Execution`-entiteetin, jonka attribuutit (`raw_inputs`, `context_variables`, `frozen_context`, `steps`, `step_states`, `atom_evaluations`) ovat valmiiksi validoituja Pydantic V2 DTO -olioita. Repository muuntaa ORM-mallin `ExecutionRecord`-domain-malliksi suoralla kenttäsidonnalla ilman yhtäkään `json.loads`- tai `.get()`-kutsua:
   ```python
   def _to_domain(record: Execution) -> ExecutionRecord:
       return ExecutionRecord(
           id=record.id,
           workflow_id=record.workflow_id,
           workflow_version=record.workflow_version,
           status=ExecutionStatus(record.status),
           target_locale=record.target_locale,
           raw_inputs=record.raw_inputs,
           context_variables=record.context_variables,
           frozen_context=record.frozen_context,
           atom_evaluations=record.atom_evaluations,
           steps=record.steps,
           step_states=record.step_states,
           execution_trace=record.execution_trace,
           models_used=record.models_used,
           source_identity_manifest=record.source_identity_manifest,
           prompt_tokens=record.prompt_tokens,
           completion_tokens=record.completion_tokens,
           cached_tokens=record.cached_tokens,
           reasoning_tokens=record.reasoning_tokens,
           cumulative_synthesis_tokens=record.cumulative_synthesis_tokens,
           dag_cost_usd=float(record.dag_cost_usd),
           cumulative_synthesis_cost=float(record.cumulative_synthesis_cost),
           duration_ms=record.duration_ms,
           is_resumable=record.is_resumable,
           error=record.error,
           created_at=record.created_at,
           updated_at=record.updated_at,
           completed_at=record.completed_at,
           created_by=record.created_by,
       )
   ```

2. **Invariantti 2: Ei sanakirjoja orkestroijassa (Zero Intermediate State Dictionaries)**:
   DAG-orkestroija ei enää kokoa `updates: dict[str, Any] = {}` -sanakirjaa. Päivitykset tehdään joko suoralla ORM-attribuuttiasetuksella tai vahvasti tyypitetyllä `ExecutionUpdateDTO`-mallilla:
   ```python
   # ORM-tason suora asetus:
   execution.context_variables = new_context_variables_dto
   execution.frozen_context = new_frozen_context
   execution.prompt_tokens += delta_tokens.prompt_tokens
   await session.commit()
   ```

3. **Invariantti 3: Ei ORM-vuotoja Service-kerrokseen (Strict Repository Quarantine)**:
   SQLAlchemy `AsyncSession`, `select()`, `update()` ja ORM-mallit (`Execution`, `WorkflowRecord`) on eristetty täysin Repository-kerroksen (`backend_v2/database/repositories/`) sisälle. Service- ja Controller-kerrokset käsittelevät ainoastaan puhtaita Pydantic Domain- ja DTO-malleja.

4. **Invariantti 4: Ei sanakirjapurkua (`**kwargs`)**:
   Päivitykset eivät saa käyttää `**kwargs`- tai `values(**dict)` -syntaksia. Kaikki kentät sijoitetaan eksplisiittisesti ja tyypitetysti.

5. **Invariantti 5: Ei raakakyselyitä (`text(...)`)**:
   Kyselyt rakennetaan tyyppiturvallisilla SQLAlchemy 2.0 -rakenteilla ilman sanakirjoja palauttavia SQL-tekstikomentoja.

---

#### **Vaihe 2.1.1: Repositorioiden virheenkäsittelyn modernisointi ja QGR003-siivous (Fail-Fast Persistence)**

Kaikki nykyiset `backend_v2/database/repositories/*.py` -tiedostoissa elävät laajat ja tyypittämättömät `except Exception:` -käsittelijät (13 kpl `QGR003`) sekä `driver.py`:n 5 abstraktia sanakirjametodia poistuvat pysyvästi:
1. **SQLAlchemy 2.0 -spesifit poikkeusluokat**: Repositoriot (`knowledge.py`, `audit.py`, `workflow.py`, `identity.py`, `base.py`) nappaavat ainoastaan spesifejä SQLAlchemy-poikkeuksia (`IntegrityError`, `DBAPIError`, `NoResultFound`) ja kääntävät ne deterministisiksi `AppException`-virheiksi RFC 7807 -muodossa (`ErrorCodes.RESOURCE_ALREADY_EXISTS`, `ErrorCodes.RESOURCE_NOT_FOUND`, `ErrorCodes.DATABASE_UNAVAILABLE`).
2. **Nolla `except Exception:` -blokkia ilman re-raisea**: Yksikään tietokantaoperaatio ei enää niele virheitä hiljaa lokittamalla ja palauttamalla `None` tai `[]`. Jos tietokantakirjoitus epäonnistuu, transaktio rullataan takaisin (`await session.rollback()`) ja `AppException` nousee Fail-Fast -periaatteella ylös asti.
3. **`backend_v2/database/driver.py` poisto tai uudelleenkirjoitus**: Vanha `DatabaseDriver`-rajapinta, joka palautti `dict[str, Any]`, poistetaan kokonaan ja korvataan tyypitetyllä asynkronisella sessiotehtaalla (`AsyncSessionLocal`) tai tyypitetyllä `PostgresDriver`-luokalla, joka ei käsittele alastomia sanakirjoja missään elinkaaren vaiheessa.

---

#### **Vaihe 2.2: Staattinen AST-laadunvarmistus (`scripts/audit_orm_strictness.py`)**

PostgreSQL-työmaalle pystytetään automatisoitu AST-auditointi (`audit_orm_strictness.py`), joka estää sanakirjojen palauttamisen ORM-kerrokseen. Skripti tarkastaa:
1. **ORM001**: Mikään sarake ei saa olla `Mapped[dict[str, Any]]` tai `Mapped[list[dict[str, Any]]]`.
2. **ORM002**: Kaikki `JSONB`-sarakkeet on pakotettava käyttämään `PydanticJSONB(TargetType)` -käärettä.
3. **ORM003**: Token- ja kustannusmetriikat on määriteltävä suorina `BigInteger`- tai `Numeric`-sarakkeina.
4. **ORM004**: Kaikki taulut on sidottava suljettuun 10 taulun topologiaan ilman avoimia JSON-säiliötauluja.

---

#### **Vaihe 3: All-in-PostgreSQL Binääri- ja SDUI-tallennusmalli**

Koska käytämme "All-in-PostgreSQL" -periaatetta, emme tarvitse ulkoisia Signed URL -kutsuja tai pilviämpäreitä. Tiedonsiirto on suoraviivaista ja suojattua:

1. **SDUI-esityksen haku ruudulle (Flutter UI)**:
   ```python
   # FastAPI Router: GET /api/v2/reports/{report_id}/sdui
   # Palauttaa suoraan report_artifacts.sdui_payload -kentän.
   # Vasteaika alle 1 ms, koska binaaritauluun ei kosketa lainkaan.
   ```
2. **PDF-raportin lataus ja striimaus**:
   ```python
   # FastAPI Router: GET /api/v2/reports/{report_id}/pdf
   @router.get("/reports/{report_id}/pdf")
   async def download_report_pdf(report_id: str, session: AsyncSession = Depends(get_db)):
       query = select(ReportBinary).where(ReportBinary.report_id == report_id)
       result = await session.execute(query)
       binary_record = result.scalar_one_or_none()
       if not binary_record:
           raise AppException(ErrorCodes.RESOURCE_NOT_FOUND, f"PDF for report {report_id} not found")
       
       return StreamingResponse(
           io.BytesIO(binary_record.pdf_bytes),
           media_type=binary_record.mime_type,
           headers={"Content-Disposition": f'attachment; filename="report_{report_id}.pdf"'}
       )
   ```
3. **Workerin tallennusoperaatio (Phase 3)**:
   - Arq `report_worker` generoi WeasyPrintillä PDF-tavut muistiin (`pdf_bytes: bytes`).
   - Avaa lyhytkestoisen `AsyncSession`-istunnon.
   - Tallentaa `ReportBinary(report_id=rep_id, pdf_bytes=pdf_bytes, size_bytes=len(pdf_bytes))` ja päivittää `ReportArtifact.status = 'READY'`.
   - Tekee `commit()` ja sulkee istunnon.

---

#### **Vaihe 4: Tuotantovalmis Idempotentti Seed-Prosessi**

Alustustyökalu (`scripts/seed_database.py`) varmistaa tietokannan käynnistyksessä pakolliset järjestelmäprofiilit, oletustyönkulut ja järjestelmänvalvojat.

```python
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend_v2.database.session import async_session_maker
from backend_v2.database.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_seed():
    async with async_session_maker() as session:
        logger.info("🌱 Ajetaan All-in-PostgreSQL System Seed...")
        # Idempotentti lisäys: tarkistetaan olemassaolo loogisella avaimella
        admin_email = "admin@quorum.local"
        res = await session.execute(select(User).where(User.email == admin_email))
        if not res.scalar_one_or_none():
            admin = User(id="usr_0191eb00000070008000000000000001", email=admin_email, role="SUPERADMIN")
            session.add(admin)
            logger.info("✅ Luotiin oletusadmin.")
        await session.commit()

if __name__ == "__main__":
    asyncio.run(run_seed())
```

---

#### **Vaihe 5: Tuotantoputki (CI/CD, Alembic & Sessioeristys)**

1. **Alembic-migraatiot**:
   ```powershell
   uv run alembic init -t async alembic
   uv run alembic revision --autogenerate -m "Initial Tripartite Schema"
   uv run alembic upgrade head
   ```
2. **Arq Worker Sessioeristys (Unit-of-Work)**:
   - Pitkät LLM DAG -evaluoinnit (15–60 s) **eivät saa pitää auki PostgreSQL-istuntoa tai transaktiota**.
   - Työntekijä noutaa tiedot lyhyellä istunnolla $\rightarrow$ vapauttaa yhteyden pooliin $\rightarrow$ ajaa rinnakkaiset LLM-kutsut $\rightarrow$ avaa uuden istunnon lopputuloksen tallentamiseksi.
3. **Asynkroninen Rinnakkaisuus & Tapahtumasilmukan Lukkiutumisen Esto (Event Loop Starvation)**:
   - **Natiivi `asyncpg` / `asyncio`-ajuri ja transaktiotason rivilukitus (`SELECT ... FOR UPDATE`)**: PostgreSQL-ajuri on 100 % asynkroninen verkkoajuri. TinyDB:n vaatimat synkroniset OS-tiedostolukitukset (`msvcrt.locking`, `fcntl.flock`), `time.sleep(0.02)` -odotussilmukat ja globaalit tiedostokirjoituslukot (`db_v2.json.lock`) poistuvat lopullisesti. Rinnakkaiset DAG-työnkulut eivät enää kilpaile samasta tiedostolukosta, mikä eliminoi `TimeoutError`- ja `PermissionError`-kaatumiset sekä `RUNNING`-tilaan jumiutuvat orvot ajot. Transaktioissa käytetään rivitason lukitusta (`SELECT ... FOR UPDATE`), jolloin vain muokattava ajotietue lukitaan lyhytaikaisesti ilman koko tietokannan tai muiden ajojen blokkaamista.
   - **Korutiinien `asyncio.to_thread` -kielto**: Orkestroijan (`dag_executor.py`) asynkronisia korutiineja (`commit_trace`) **EI KOSKAAN** kääritä `asyncio.to_thread`-kutsuihin (tämä aiheuttaa `RuntimeError: no running event loop` tai jättää korutiinin ajamatta). Transaktiot ja tallennukset ajetaan puhtaasti natiiveina `async/await`-kutsuina tapahtumasilmukalla `_commit_lock = asyncio.Lock()` suojaamana.
   - **CPU-sidonnaisen reduktion eristys**: Jos suoritetaan raskasta CPU-laskentaa (kuten `MatrixReducer.reduce_matrix` sadoille atomeille ennen synteesiä), vain tämä puhtaasti synkroninen laskentalogiikka eristetään ajettavaksi taustasäikeessä muuttumattoman tilavedoksen (`snapshot = exec_record.model_copy()`) yli: `await asyncio.to_thread(MatrixReducer.reduce_matrix, snapshot)`.

---

### **🔴 Red Team Audit: All-in-PostgreSQL -mallin Vahvistus & Haasteet**

| Aiempi Riski (Ulkoinen Storage / TinyDB) | Miten "All-in-PostgreSQL" ratkaisee tämän? | Tila |
| :--- | :--- | :--- |
| **1. "Orphaned Files" (Orvot tiedostot)** | Ulkoista varastoa ei ole. `executions` poistaminen ajaa tietokantatasolla `ON DELETE CASCADE`:n `report_artifacts`- ja `report_binaries`-tauluihin. Kaikki binaarit tuhoutuvat mikrosekunnissa ilman erillisiä siivous-croneja. | **100 % TAKLATTU** |
| **2. Split-Brain GDPR -poistot** | Yksi SQL-komento (`DELETE FROM users WHERE id = ...` tai `DELETE FROM executions WHERE id = ...`) poistaa käyttäjän koko datan transaktionaalisesti. Ei riskiä siitä, että kanta tyhjenee mutta tiedostot jäävät pilveen. | **100 % TAKLATTU** |
| **3. Signed URL Abuse & Turvallisuus** | Tiedostoja ei jaeta julkisten Signed URL -osoitteiden kautta. Kaikki liikenne kulkee FastAPI:n autentikoidun `/api/v2/reports/{id}/pdf` -reitin läpi, jolloin tenant-eristys ja RBAC pätevät aina. | **100 % TAKLATTU** |
| **4. UUIDv7 -tietovuoto & ID-sopimukset** | Säilytetään Quorumin viralliset Opaque Stripe ID:t (`exe_...`, `rep_...`). UUIDv7 upotetaan heksasuffiksiksi, jolloin B-Tree-indeksihyöty säilyy täysin ilman, että API-sopimuksia rikotaan. | **100 % TAKLATTU** |
| **5. Tapahtumasilmukan lukkiutuminen & Tiedostolukituskilpa (Lock Starvation & Race Condition)** | TinyDB:n synkroniset levynkirjoitukset, `time.sleep(0.02)` -odotussilmukat ja `msvcrt`-tiedostolukitukset poistuvat. PostgreSQL käyttää täysin asynkronista yhteysallasta (`asyncpg` / `asyncio`), MVCC:tä ja rivitason lukitusta (`SELECT ... FOR UPDATE`). Samanaikaiset DAG-ajot eivät enää kilpaile tiedostolukosta eivätkä aiheuta `TimeoutError`/`PermissionError`-kaatumisia, I/O ei estä `asyncio.TaskGroup`-ajoja eikä SSE-telemetriaa, eivätkä ajot jää orpoina `RUNNING`-tilaan ilman DLQ-reititystä. | **100 % TAKLATTU** |
| **6. Kuolevan tiedostokoodin ylikorjaus & Hukkatyö (Sunk Cost Engineering)** | EPIC 152:ssa ei yritetä refaktoroida `TinyDBDriverin` tai `wrapper.py`:n tiedostolukituksia, vaan ne on karsittu (Scrap). EPIC 152 korjaa ajurista ainoastaan puhtaan `isinstance(data, BaseModel)` -tyyppiturvallisuuden, ja keskittää paukut DTO-malleihin (`models/dtos/`), jotka siirtyvät sellaisenaan PostgreSQL-malliin. | **100 % TAKLATTU** |
| **7. Alastomat sanakirjat ja skeemavuodot (`dict[str, Any]` in JSONB)** | JSONB-sarakkeiden typistäminen `dict[str, Any]` -muotoon on ehdottomasti kielletty. Kaikki JSONB-kentät sidotaan `PydanticJSONB`-kääreellä ja Pydantic V2 `TypeAdapter`-moottorilla suoraan vahvoihin DTO-malleihin (`WorkflowInputs`, `ContextVariablesDTO`, `FrozenContext`, `ReportDataDTO`, `EvaluatedAtomDTO`, `TraceEvent`, `TraceEventMetadataDTO`, `StepOutputContentDTO`, `ProgressTracePayloadDTO`, `LightweightMatrixOutput`, `GlobalContextVarsDTO`, `AnyPromptBlock`, `OutputProfile`, `SystemConfigModelRegistry`, `list[ExecutionStep]`, `dict[str, ExecutionStepState]`, `list[TraceEvent]`), joiden in-memory tyyppiturvallisuus on taklattu suunnitelmassa @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md]. SQLAlchemy ja TypeAdapter sarjallistavat ja validoivat datan automaattisesti ilman käsin koodattuja sanakirjamuunnoksia. | **100 % TAKLATTU** |
| **8. Orkestroijan ja Repositoryn apusanakirjat (`updates: dict`, `cv_dict`)** | Orkestroijan ja tietokantakerroksen väliset tilapäiset päivityssanakirjat on kielletty. Suunnitelman @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] mukaisesti orkestroija operoi 100 % tyypitetyillä DTO-instansseilla (`StepOutputContentDTO`, `TraceEventMetadataDTO`, `ExecutionInputsDTO`). SQLAlchemy 2.0 async session päivittää tilan suoraan tyypitettyjen DTO-instanssien kautta (`execution.context_variables = new_dto`), ja repository rekonstituoi suoraan Pydantic domain-mallit ilman väliaikaisia sanakirjoja. | **100 % TAKLATTU** |
| **9. Staattinen laadunvarmistus & AST-valvonta** | Uusi `audit_orm_strictness.py` estää CI/CD-tasolla minkäänlaisten `dict[str, Any]`- tai `mapped_column(JSONB)`-rakenteiden pääsyn SQLAlchemy-malleihin ilman `PydanticJSONB`-sidosta. | **100 % TAKLATTU** |
| **10. Repositorioiden QGR003-poikkeukset & driver.py:n sanakirjavuodot** | Vanhoja TinyDB-poikkeuskäsittelijöitä ei ylikorjata vanhassa kannassa (throwaway work ban). Uudet SQLAlchemy 2.0 -repositoriot (`knowledge.py`, `audit.py`, `workflow.py`, `identity.py`, `base.py`) kääntävät spesifit virheet (`IntegrityError`, `NoResultFound`, `DBAPIError`) suoraan tyypitetyiksi `AppException`-virheiksi ilman laajoja `except Exception:` -lohkoja. `driver.py`:n alastomat `dict[str, Any]` -metodit poistuvat kokonaan. | **100 % TAKLATTU** |
| **11. Tekoälyparin (Antigravity) kehityssuvereniteetti & Agentic Drift -esto** | Löysä `dict[str, Any]` -pohjainen tietokantatallennus altistaa tekoälyn hallusinoimaan sarakenimiä ja avaimia. Vahva `PydanticJSONB`-sidonta yhdessä `audit_orm_strictness.py`- ja `audit_dict_eradication.py`-porttien kanssa poistaa *Agentic Driftin* ja pakottaa matemaattisen 100 % tyyppiturvallisuuden koko ketjulle suoritusputkesta PostgreSQL-talletukseen saakka. | **100 % TAKLATTU** |
| **12. Kolmivaiheinen tiekartta ja vastuiden jako (The Tripartite Roadmap)** | Työnjako on aukoton: Vaihe 1 (@[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md]) taklaa suoritusputken in-memory -tilan. Tämä suunnitelma (Vaihe 2) esisiivoaa pysyvät domain-mallit (Vaihe 1.5) ja taklaa pysyvyyskerroksen (SQLAlchemy 2.0 ORM, `PydanticJSONB`, `SELECT ... FOR UPDATE`, `driver.py`:n poisto ja repositorioiden QGR003-poikkeukset). Vaihe 3 (@[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_Adapter_Strict_Typing.md]) siivoaa ulkoiset LLM SDK -adapterit ja oheiskoukut saavuttaen koko koodikannan tasan 0 virheen tilan. Työvaiheet eivät risteä eivätkä aiheuta hukkatyötä. | **100 % TAKLATTU** |

#### **Uusi Tunnistettu Riski: Database Bloat (Kannan paisuminen) & Sen Esto**
- **Riski**: Jos 100 000 PDF-tiedostoa (n. 100 GB) tallennetaan suoraan tauluriville, tavalliset taulukyselyt hidastuvat ja tietokannan RAM-muisti (`shared_buffers`) täyttyy tarpeettomasta binaaridatasta.
- **Taklaus**: 
  1. **Eristetty taulu**: PDF:t sijaitsevat omassa `report_binaries`-taulussaan. Ajolistoja ja raporttilistoja selattaessa tähän tauluun ei kosketa.
  2. **PostgreSQL TOAST**: Yli 2 KB:n kentät pakkataan ja siirretään automaattisesti taustalla TOAST-sivulle. Päätaulun indeksointi ja rivihaut pysyvät yhtä nopeina kuin jos tiedostoja ei olisi lainkaan.
  3. **Valinnainen Retentio/TTL**: Jos levytilaa halutaan säästää, vanhojen raporttien PDF:t voidaan tyhjentää yhdellä SQL-komennolla (`DELETE FROM report_binaries WHERE created_at < NOW() - INTERVAL '90 days'`), jolloin itse ajohistoria ja SDUI-metriikat säilyvät koskemattomina.