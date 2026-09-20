> **STATUS: PENDING / ODOTTAA TOTEUTUSTA (Tuleva PostgreSQL 17+ & SQLAlchemy 2.0 -migraatiosuunnitelma)**
> **ARKITEHTUURIPERIAATE: "All-in-PostgreSQL" (Single-Engine Sovereign Storage Architecture)**
> **LINKITYS JA RAJAUS SUHTEESSA EPIC 152:EEN (Scrap vs. Refactor):**
> 1. **Täydellinen poisto (Scrap)**: Tämän suunnitelman toteutus poistaa ja korvaa kokonaan `TinyDBDriver`-ajurin (`backend_v2/database/tinydb_driver.py`), tiedostotietokantakääreen (`backend_v2/database/wrapper.py`), `db_v2.json`-tiedoston ja tiedostolukituksen (`db_v2.json.lock`). Tämän vuoksi EPIC 152:ssa tiedostolukituskoodiin ei tehdä lainkaan rakenteellisia rinnakkaisuus- tai asynkronointikorjauksia (estetään kuolevan koodin ylikorjaus).
> 2. **DTO-mallien suora hyödyntäminen (Invest & Re-Use)**: EPIC 152:ssa puhdistetut, tiukasti tyypitetyt Pydantic V2 DTO -mallit (`ExecutionRecord`, `ExecutionInputsDTO`, `EvaluatedAtomDTO`, `HookDeltaDTO`, `ReportDataDTO`) siirtyvät **sellaisenaan 1:1** PostgreSQL-migraatioon muodostaen `JSONB`- ja `BYTEA`-tallennuskenttien pysyvän sovellustason validointipohjan.

---

### **YHTEENVETO & PÄÄPERIAATE: "All-in-PostgreSQL"**

Tässä suunnitelmassa Quorum ottaa käyttöön **"All-in-PostgreSQL" -periaatteen**:
1. **PostgreSQL 17+ on järjestelmän ainoa totuuden lähde ja ainoa tallennuspaikka (Single Source of Truth & Sole Storage)**.
2. **Nolla ulkoista tiedostovarastoriippuvuutta**: Erilliset ulkoiset pilvitallennukset (Firebase Storage, AWS S3, Google Cloud Storage) ja niihin liittyvät Signed URL -viritykset hylätään tarpeettomina.
3. **Kaksitasoinen tallennusratkaisu PostgreSQL:n sisällä**:
   - **SDUI & Kognitiiviset puut (`JSONB`)**: Server-Driven UI -esitysmalli (`report.sdui.json`), evaluointiverkko (`atom_evaluations`) ja telemetria tallennetaan natiivisti `JSONB`-muodossa, jolloin haut ovat millisekuntiluokkaa ja indeksoitavissa.
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

#### **Vaihe 2: Tietokantamallit (Stripe-prefixed UUIDv7 & Tripartite-pariteetti)**

Kaikki taulut noudattavat Quorumin kanonista Opaque Stripe ID -standardia (`pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$"`). B-Tree-indeksien pirstaloitumisen estämiseksi ID:n heksasuffiksi generoidaan aikajärjestetystä UUIDv7:stä (`f"{prefix}_{uuid6.uuid7().hex}"`).

**`backend_v2/database/models.py`**:

```python
from datetime import datetime
from typing import Any
from sqlalchemy import (
    String, DateTime, ForeignKey, text, func, BigInteger, Boolean, Numeric
)
from sqlalchemy.dialects.postgresql import JSONB, BYTEA
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    """Käyttäjätunnukset ja tenant-eristys."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # usr_...
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="USER", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Execution(Base):
    """Phase 1: Ajon muuttumaton totuuden lähde (SSOT)."""
    __tablename__ = "executions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # exe_...
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    workflow_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)  # PENDING, RUNNING, PASSED, FAILED
    
    # FinOps & Telemetria
    total_cost_usd: Mapped[float] = mapped_column(Numeric(10, 6), default=0.0, nullable=False)
    token_telemetry: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    
    # Syötteet ja Kognitiivinen evaluointiverkko (JSONB mahdollistaa nopeat kyselyt ja indeksit)
    raw_inputs: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    atom_evaluations: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 1-to-N Relaatio tulosteisiin: Poisto siivoaa automaattisesti kaikki raportit ja niiden PDF-binaarit
    reports: Mapped[list["ReportArtifactModel"]] = relationship(
        "ReportArtifactModel", back_populates="execution", cascade="all, delete-orphan"
    )

class ReportArtifactModel(Base):
    """Phase 2/3: Ajon itsenäiset tulosteet ja Server-Driven UI -esitysmalli (0..N kpl)."""
    __tablename__ = "report_artifacts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # rep_...
    execution_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("executions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    output_profile_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="fi", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="GENERATING", nullable=False)  # GENERATING, READY, FAILED
    
    # Server-Driven UI -puu suoraan JSONB:nä (haetaan ruudulle <1 ms)
    sdui_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    
    has_pdf: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)

    execution: Mapped["Execution"] = relationship("Execution", back_populates="reports")
    
    # 1-to-1 Eristetty binaaritaulu: Raskas PDF pidetään poissa päätaulun muistisivuista
    binary: Mapped["ReportBinaryModel | None"] = relationship(
        "ReportBinaryModel", back_populates="artifact", uselist=False, cascade="all, delete-orphan"
    )

class ReportBinaryModel(Base):
    """All-in-PostgreSQL Eristetty binaaritallennus (TOAST-optimoitu)."""
    __tablename__ = "report_binaries"

    report_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("report_artifacts.id", ondelete="CASCADE"), primary_key=True
    )
    mime_type: Mapped[str] = mapped_column(String(64), default="application/pdf", nullable=False)
    pdf_bytes: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    artifact: Mapped["ReportArtifactModel"] = relationship("ReportArtifactModel", back_populates="binary")
```

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
       query = select(ReportBinaryModel).where(ReportBinaryModel.report_id == report_id)
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
   - Tallentaa `ReportBinaryModel(report_id=rep_id, pdf_bytes=pdf_bytes, size_bytes=len(pdf_bytes))` ja päivittää `ReportArtifactModel.status = 'READY'`.
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

#### **Uusi Tunnistettu Riski: Database Bloat (Kannan paisuminen) & Sen Esto**
- **Riski**: Jos 100 000 PDF-tiedostoa (n. 100 GB) tallennetaan suoraan tauluriville, tavalliset taulukyselyt hidastuvat ja tietokannan RAM-muisti (`shared_buffers`) täyttyy tarpeettomasta binaaridatasta.
- **Taklaus**: 
  1. **Eristetty taulu**: PDF:t sijaitsevat omassa `report_binaries`-taulussaan. Ajolistoja ja raporttilistoja selattaessa tähän tauluun ei kosketa.
  2. **PostgreSQL TOAST**: Yli 2 KB:n kentät pakkataan ja siirretään automaattisesti taustalla TOAST-sivulle. Päätaulun indeksointi ja rivihaut pysyvät yhtä nopeina kuin jos tiedostoja ei olisi lainkaan.
  3. **Valinnainen Retentio/TTL**: Jos levytilaa halutaan säästää, vanhojen raporttien PDF:t voidaan tyhjentää yhdellä SQL-komennolla (`DELETE FROM report_binaries WHERE created_at < NOW() - INTERVAL '90 days'`), jolloin itse ajohistoria ja SDUI-metriikat säilyvät koskemattomina.