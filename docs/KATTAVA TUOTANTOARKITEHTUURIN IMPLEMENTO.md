KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTOINTISUUNNITELMA
Luku 0: Pilvitietokannan ja Ympäristön pystyttäminen verkkoon
Koska sovelluksessasi on jo yhteys Firebaseen, olet kiinni Google Cloud Platform (GCP) -ekosysteemissä. Tietokannan tuotantopystytys tehdään GCP:hen saumattomasti ja tietoturvallisesti:

Google Cloud SQL for PostgreSQL:

Siirry Google Cloud Consoleen samaan projektiin, jossa Firebase-projektisi elää.

Valitse SQL -> Create Instance -> PostgreSQL.

Versio: Valitse vähintään PostgreSQL 18. Se tuo tuen natiiville asynkroniselle I/O:lle (AIO) ja optimoidulle uuidv7():lle, tehden Pythonin asynkronisesta backendistä erittäin nopean.

Tietoturva & Verkkoyhteydet (VPC):

Ei julkista IP:tä: Ota Public IP pois päältä tietokannan asetuksista.

Private IP: Valitse Private IP ja kytke kanta samaan VPC-verkkoon (Virtual Private Cloud), jossa tuotanto-backendisi (esim. Cloud Run) pyörii. Tämä estää täysin ulkomaailman pääsyn kantaan.

Connection Pooling (PgBouncer):

Kytke Cloud SQL:n asetuksista päälle sisäänrakennettu PgBouncer (Transaction pooling mode). Asynkroninen Python osaa avata nopeasti satoja I/O-yhteyksiä, ja ilman allasta kanta kaatuisi nopeasti connection-rajoihin.

AIO-konfiguraatio (PostgreSQL 18+):

Aseta tietokannan lipuista (Database flags) io_method=io_uring (tai worker), jotta asynkroninen AIO-alijärjestelmä on aktiivinen.

Backendin Ympäristömuuttujat:

Sijoita lokaali ja tuotannon DSN-yhteysmerkkijono .env-tiedostoon:
DATABASE_URL=postgresql+psycopg://app_user:salasana@<PRIVATE_IP>:5432/quorum_db

Luku 1: Moderni Infra ja Työkalupakki
Poistamme kaiken teknisen velan ja siirrymme puhtaasti asynkroniseen, tyyppiturvalliseen arkkitehtuuriin. Fallback-logiikkaa demotietokantoihin ei jätetä koodiin.

Poistettavat vanhat riippuvuudet:

Bash
pip uninstall tinydb
Asennettavat tuotantotason kirjastot (backend_v2/requirements.txt):

Plaintext
fastapi
uvicorn[standard]
# psycopg v3 korvaa vanhan psycopg2:n natiivilla async-tuella
psycopg[binary]>=3.0
sqlalchemy[asyncio]>=2.0
alembic
pydantic>=2.0
pydantic-settings
firebase-admin
google-cloud-storage
hashids
Luku 2: Tietokantamallit ja Natiivi UUIDv7 (SSOT)
PostgreSQL on Single Source of Truth (SSOT) kaikelle relaatiodatalle. Tiedostoja ei tallenneta kantaan, vaan kanta pitää ainoastaan Firebase Storagen metadataa yllä.

Käytämme PostgreSQL 18+ natiivia uuidv7():ää. Se on aikajärjestetty, joten se ei pirstaloi tietokannan B-Tree-indeksejä. Huomioituna tietovuotoriskinä UUIDv7 sisältää tarkan luontiajan, joten API-vastauksissa nämä ID:t obfuskoidaan (piilotetaan) hashids-kirjastolla, jottei kilpailija voi päätellä datan luomisvolyymiä.

backend_v2/database/models.py (UUSI):

Python
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, text, func, BigInteger, Computed
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    # PostgreSQL 18 natiivi UUIDv7
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    
    # SSOT: Yhteys Firebase Authiin
    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="USER")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    
    # PG 18 Virtual Generated Column (Lasketaan lennossa, ei vie levytilaa)
    size_mb: Mapped[float] = mapped_column(Computed("size_bytes / 1048576.0", persisted=False))
    
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    
    # Suojaus orpoja tiedostoja vastaan
    status: Mapped[str] = mapped_column(String(32), default="pending") # pending -> uploaded
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
Luku 3: Firebase Storage ja Atomic Get-Or-Create
Löydösten perusteella raskaat binääritiedostot eivät koskaan saa kuormittaa Python-backendin RAM-muistia. Myös Lazy Provisioning (käyttäjien automaattiluonti) altistaa järjestelmän "Race Condition" -virheille. Nämä on korjattu seuraavasti:

Latauspyyntö ja Signed URLs: Frontend pyytää API:lta latauslupaa. Backend luo FileMetadata-rivin tilaan "pending". Backend generoi Firebase Admin SDK:lla aikarajatun (esim. 15 min) latausosoitteen, johon kryptataan ehdoton sallittu koko ja tiedostotyyppi (estää haittaohjelmat). Frontend lataa suoraan pilveen.

Orpojen tiedostojen siivous: Jos selain kaatuu latauksen aikana, pilveen jää roskatiedosto ("Orphaned file"). Backendiin ajastetaan CronJob, joka etsii yli 24h vanhat "pending"-tilaiset tiedostot, pyytää Firebase Admin SDK:ta tuhoamaan ne Storagesta ja poistaa tietokantarivin.

Käyttäjien poistaminen (Split-Brain vältetty): Relaatiokannan CASCADE DELETE ei riitä. Jos GDPR-poisto iskee, backend hakee ensin tiedostot ja tuhoaa ne Storagesta, tuhoaa tilin Firebase Authista, ja vasta sen jälkeen poistaa rivit PostgreSQL:stä.

Autentikaatio & Race Condition -suojaus (PostgreSQL 19 ominaisuus):
Vältämme haamukäyttäjien syntymisen uuden atomaarisen kyselyn avulla:

Python
# Kun Firebase-token on validoitu:
stmt = text("""
    INSERT INTO users (firebase_uid, email) 
    VALUES (:uid, :email)
    ON CONFLICT (firebase_uid) 
    DO SELECT RETURNING *;  -- PostgreSQL 19 Ominaisuus!
""")
result = await db.execute(stmt, {"uid": firebase_uid, "email": email})
Luku 4: Uusi Tuotantovalmis Seed-Prosessi ja Skeemanhallinta
Vanhat JSON-seed-tiedostot hävitetään kokonaan. Alembic pitää huolen tietokannan rakenteesta, ja seed-skriptistä tehdään idempotentti (se ei luo tuplarivejä, vaikka ajettaisiin CI/CD:ssä useasti putkeen).

Uusi backend_v2/seed/run_seed.py:

Python
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
        # Vain järjestelmän pakolliset perustiedot (System Seed)
        system_admins = [
            {"email": "admin@tuotanto.fi", "firebase_uid": "ADMIN_UID_TÄHÄN", "role": "SUPERADMIN"}
        ]
        
        for admin_data in system_admins:
            # Tarkistetaan Natural Keyllä (email), ettei luoda tuplia
            result = await session.execute(select(User).where(User.email == admin_data["email"]))
            if not result.scalar_one_or_none():
                session.add(User(**admin_data))
                logger.info(f"✅ Luotiin uusi admin: {admin_data['email']}")
        
        await session.commit()

if __name__ == "__main__":
    asyncio.run(run_seed())
Luku 5: Koodikannan Auditointi ja Muutoskartta
Tämä osuus perustuu huolelliseen läpikäyntiin nykyisestä backend_v2-koodikannastasi. Vertaamme nykytilaa suunnitelmaan ja listaamme konkreettiset muutokset kerros kerrokselta.

5.1. Mitä on tehty ja tekemättä
Tehdyt asiat (Olemassaoleva perusta):

API-reitityksen erinomainen jako (backend_v2/api/routers/) ja Clean Architecture -kerrokset (services/, database/repositories/).

Rajapintojen Pydantic-mallit (models/dtos/) ja ydinmallit (models/domain/) ovat selkeästi erillään.

Hook-rekisteri (core/hook_registry.py) tukee laajennettavuutta.

Tekemättömät asiat (Seuraavat askeleet):

Järjestelmä operoi täysin demotasolla. Kaikki kantaan liittyvä kommunikaatio nojaa lokaaliin TinyDB-tiedostojärjestelmään ja Firestoreen.

Oikeat relaatiot, viiteavaimet (Foreign Keys) ja tyyppiturvalliset SQLAlchemy-mallit puuttuvat.

Tietokannan versiohallinta (Alembic) on alustamatta.

Tietoturvallinen transaktio- ja yhteyshallinta on tekemättä.

5.2. seed_data.json Taulut, jotka siirtyvät PostgreSQL:ään
Koodisi rakenteen (database/repositories/) perusteella vanha seed_data.json on sisältänyt seuraavat taulut/kokoelmat:

Komponentit (repositories/components/): agent, execution_persona, extraction_protocol, matrix, output_profile, prompt_block, role, task_blueprint.

Ydintaulut (repositories/): audit, execution, identity (muutetaan tauluksi users), knowledge, system (asetukset), workflow.

Toimenpide: Kaikki vanha json-data heitetään pois. Jokaiselle näistä luodaan backend_v2/database/models.py tiedostoon SQLAlchemy DeclarativeBase -luokat. Vanhat kovakoodatut ID:t hävitetään, ja PostgreSQL 18 generoi rivien syntyessä uudet uuidv7()-avaimet.

5.3. Poistettavat Ohjelmat ja Luokat (Teknisen velan poisto)
Seuraavat tiedostot poistetaan kokonaan, jotta tuotantokoodiin ei jää kytköksiä demovaiheeseen:

backend_v2/seed/seed_data.json & data/db_v2.json & app.db: Kaikki vanha demodata tuhotaan.

backend_v2/database/tinydb_driver.py: Paikallinen tiedostotietokanta poistetaan tuotantokelvottomana.

backend_v2/database/firestore_driver.py: Relaatiodata kuuluu vain PostgreSQL:ään (SSOT).

backend_v2/services/drivers/local_file_driver.py: Lokaalia levytallennusta ei käytetä pilviympäristössä.

backend_v2/services/drivers/gcs_file_driver.py: Vanha toteutus poistetaan, koska tiedostojen bitit ohjataan suoraan asiakkaalta pilveen.

5.4. Muutettavat Ohjelmat, Aliohjelmat ja Luokat (Refaktorointi)
A. Tietokantaydin ja Yhteydenhallinta (backend_v2/database/)

Muuttuvat tiedostot: wrapper.py, driver.py, factory.py, interfaces.py, repository.py.

Miksi ja Miten: Nykyinen abstraktiokerros (joka tukee TinyDB:tä ja palauttaa sanakirjoja) puretaan. Yhteydenhallinta yksinkertaistetaan käyttämään asynkronista SQLAlchemy async_sessionmaker:ia. API-reitteihin tietokantasessio injektoidaan suoraan Depends(get_db) -tyylillä. interfaces.py ohjelmoidaan uudelleen vaatimaan tyyppiturvallisia SQLAlchemy-malleja.

B. Data Access Layer (backend_v2/database/repositories/ ja components/)

Muuttuvat tiedostot: Kaikki repositoriot (esim. audit.py, execution.py, workflow.py ja components/agent.py).

Miksi ja Miten: Koodi käyttää nyt TinyDB-spesifiä logiikkaa (esim. Query().id == id). Nämä kaikki refaktoroidaan käyttämään SQLAlchemyn asynkronisia select(), insert(), update() ja delete() -operaatioita.

C. Autentikaatio ja API:t (backend_v2/api/routers/iam/auth.py, users.py & backend_v2/services/auth.py)

Muuttuvat tiedostot: Kirjautumisen, rekisteröitymisen ja salasanojen käsittely.

Miksi ja Miten: Oma logiikka salasanojen tai lokaalien tokenien pyörittämiseen poistetaan tietoturvariskinä ja SSOT-periaatteen vastaisena. Tilalle luodaan Depends-injektio (get_current_user), joka validoi Firebase JWT-tokenin firebase_admin-kirjastolla ja suorittaa "Lazy Provisioningin" (kuten Luku 3).

D. DTO:t ja Domain-mallit (backend_v2/models/dtos/ & domain/)

Muuttuvat tiedostot: Kaikki Pydantic-mallit.

Miksi ja Miten: Löyhät tyypitykset (esim. id: int | str) kiristetään muotoon id: uuid.UUID. Luokkiin lisätään model_config = ConfigDict(from_attributes=True), mikä mahdollistaa saumattoman sillan: FastAPI voi hakea koodissasi SQLAlchemyn objektin ja muuntaa sen suoraan JSON:iksi ilman manuaalista mappauskoodia.

E. Tiedostopalvelut (backend_v2/services/storage.py, file_driver.py)

Muuttuvat tiedostot: Kaikki funktiot, jotka operoivat fyysisillä tavuilla.

Miksi ja Miten: Binäärien luku (.read()) ja kirjoitus (.write()) poistetaan backendistä RAM-muistin suojelemiseksi. Luokat refaktoroidaan URL-generaattoreiksi, jotka tallentavat Postgresiin FileMetadata-rivin ja kutsuvat Firebase Admin SDK:n Signed URL -metodeja.

F. Seed-skriptit ja Skeemanhallinta (backend_v2/seed/run_seed.py, wipe_user_data.py, seed_registry.py)

Muuttuvat tiedostot: Seedaustyökalut.

Miksi ja Miten:

run_seed.py refaktoroidaan luomaan "System Seed" -data suoraan SQLAlchemyn objektien avulla idempotentisti (kuten Luku 4).

wipe_user_data.py muutetaan ajamaan puhtaita Postgres SQL-komentoja (TRUNCATE TABLE users CASCADE).

seed_registry.py voidaan todennäköisesti poistaa.

Alembic: Koodikannasta puuttuu skeeman versiohallinta. Ajamalla alembic init -t async alembic otetaan käyttöön tietokannan versionhallinta, jonka CI/CD-putki ajaa tuotantoon mennessä.