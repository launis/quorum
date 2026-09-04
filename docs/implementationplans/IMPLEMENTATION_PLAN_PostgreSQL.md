> **STATUS: PENDING / ODOTTAA TOTEUTUSTA (Tuleva PostgreSQL 17+ & SQLAlchemy 2.0 -migraatiosuunnitelma)**

### **IMPLEMENTOINTISUUNNITELMA**

#### **Vaihe 1: Moderni Infra ja Työkalupakki**

PostgreSQL 17 toi jo mukanaan natiivin uuidv7(), ja tulevat 18-19 versiot vain parantavat sen suorituskykyä ja indeksointia. UUIDv7 on ylivoimainen, koska se on **aikajärjestetty** – se ei pirstaloi tietokannan B-Tree-indeksejä, kuten vanha UUIDv4 teki, jolloin miljoonien rivien kanta pysyy salamannopeana.  
Puhdistettu ja täysin asynkroninen Python-pino:

Bash  
pip install fastapi "sqlalchemy\[asyncio\]\>=2.0" "psycopg\[binary\]\>=3.0" alembic pydantic pydantic-settings firebase-admin google-cloud-storage

#### **Vaihe 2: Tietokantamallit (UUIDv7 & SSOT)**

Firebase hallitsee autentikaation ja tiedostot, joten tietokantamme pitää sisällään vain referenssit näihin (SSOT).  
**database/models.py**

Python  
import uuid  
from datetime import datetime  
from sqlalchemy import String, DateTime, ForeignKey, text, func, BigInteger  
from sqlalchemy.dialects.postgresql import UUID  
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped\_column, relationship

class Base(DeclarativeBase):  
    pass

class User(Base):  
    \_\_tablename\_\_ \= "users"

    \# Natiivi UUIDv7. Joissain Postgres-ympäristöissä käytetään uuid\_generate\_v7()  
    id: Mapped\[uuid.UUID\] \= mapped\_column(UUID(as\_uuid=True), primary\_key=True, server\_default=text("uuidv7()"))  
      
    \# SSOT: Yhteys Firebaseen  
    firebase\_uid: Mapped\[str\] \= mapped\_column(String(128), unique=True, index=True, nullable=False)  
    email: Mapped\[str\] \= mapped\_column(String(255), unique=True, nullable=False)  
    role: Mapped\[str\] \= mapped\_column(String(50), default="USER")  
      
    created\_at: Mapped\[datetime\] \= mapped\_column(DateTime(timezone=True), server\_default=func.now())

class FileMetadata(Base):  
    """ Tiedostot tallennetaan Firebase Storageen, kanta pitää vain metadatan SSOT:na """  
    \_\_tablename\_\_ \= "file\_metadata"

    id: Mapped\[uuid.UUID\] \= mapped\_column(UUID(as\_uuid=True), primary\_key=True, server\_default=text("uuidv7()"))  
    user\_id: Mapped\[uuid.UUID\] \= mapped\_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)  
      
    filename: Mapped\[str\] \= mapped\_column(String(255), nullable=False)  
    size\_bytes: Mapped\[int\] \= mapped\_column(BigInteger, nullable=False)  
      
    \# Firebase Storage polku (esim. "users/\<user\_id\>/tiedosto.pdf")  
    storage\_path: Mapped\[str\] \= mapped\_column(String(1024), nullable=False, unique=True)  
    status: Mapped\[str\] \= mapped\_column(String(32), default="pending") \# pending, uploaded  
      
    created\_at: Mapped\[datetime\] \= mapped\_column(DateTime(timezone=True), server\_default=func.now())

#### **Vaihe 3: Uusi Tuotantovalmis Seed-Prosessi**

Vanhat .json-tiedostot hävitetään. Uusi seed-mekanismi rakennetaan **idempotentiksi** Python-skriptiksi (voit ajaa sen turvallisesti 100 kertaa putkeen).  
**scripts/seed\_database.py**

Python  
import asyncio  
import logging  
from sqlalchemy.ext.asyncio import AsyncSession  
from sqlalchemy import select  
from database.session import async\_session\_maker  
from database.models import User

logging.basicConfig(level=logging.INFO)  
logger \= logging.getLogger(\_\_name\_\_)

async def run\_seed():  
    async with async\_session\_maker() as session:  
        \# Tuotannon pakolliset alustusdatatietueet  
        system\_admins \= \[  
            {"email": "admin@tuotanto.fi", "firebase\_uid": "ASETETTU\_FIREBASE\_CONSOLESTA", "role": "SUPERADMIN"}  
        \]

        logger.info("🌱 Ajetaan System Seed...")  
          
        for admin\_data in system\_admins:  
            \# Idempotenssi: tarkista onko data jo kannassa (sähköposti on looginen avain)  
            result \= await session.execute(select(User).where(User.email \== admin\_data\["email"\]))  
            if not result.scalar\_one\_or\_none():  
                new\_admin \= User(\*\*admin\_data)  
                session.add(new\_admin)  
                logger.info(f"✅ Luotiin uusi admin: {admin\_data\['email'\]}")  
            else:  
                logger.info(f"⏭️ Admin {admin\_data\['email'\]} on jo olemassa, ohitetaan.")  
          
        await session.commit()

if \_\_name\_\_ \== "\_\_main\_\_":  
    asyncio.run(run\_seed())

#### **Vaihe 4: Firebase Storage Integration (Signed URLs)**

Sinun ei pidä reitittää suuria binääritiedostoja Backend-palvelimesi tai tietokantasi läpi, sillä se syö RAM-muistia ja kaistanleveyttä.

> 1. **Client pyytää lupaa:** Frontend kutsuu APIa POST /api/files/upload-url.  
> 2. **Backend luo varauksen:** Backend tekee tietokantaan FileMetadata-rivin tilaan "pending".  
> 3. **URL-generointi:** Backend käyttää Firebase Admin SDK:ta luodakseen **Signed URLin** (aikarajoitettu PUT-osoite, validi esim. 15 minuuttia).  
> 4. **Client lataa suoraan pilveen:** Frontend lähettää tiedoston suoraan Google Cloudiin / Firebase Storageen ohittaen backendisi täysin.  
> 5. **Kuittaus:** Frontend kutsuu POST /api/files/{id}/confirm, jolloin backend muuttaa tilaksi "uploaded".

#### **Vaihe 5: Tuotantoputki (CI/CD ja Alembic)**

Nyt kun arkkitehtuuri on uusi, et voi enää koodista ajaa Base.metadata.create\_all(). Tarvitset tietokannan versiohallinnan.

> 1. Aja alembic init \-t async alembic.  
> 2. Luo ensimmäinen tyhjä rakenne (baseline): alembic revision \--autogenerate \-m "Initial schema".  
> 3. Aina kun koodi menee livenä tuotantoon, CI/CD-putkesi ajaa ensin alembic upgrade head (päivittää taulut) ja sitten python scripts/seed\_database.py (varmistaa että asetukset ovat kunnossa).

### **🔴 Red Team Audit: Suunnitelman Kriittinen Haasto & Sudenkuopat**

Vaikka yllä oleva on ehdoton tuotantostandardi, siihen liittyy sudenkuoppia, jotka arkkitehdin on taklattava.  
**1\. "Orphaned Files" (Orvot tiedostot pilvessä)**

* **Hyökkäys / Riski:** Frontend pyytää backendiltä Signed URLin. Backend luo tietokantaan "pending"-rivin. Käyttäjä lataa 5 GB videon Firebase Storageen, mutta sulkee selaimen juuri ennen /confirm \-kutsua. Sinä maksat Googlelle tallennustilasta, mutta järjestelmässäsi tiedosto jää ikuisesti "pending"-tilaan, eikä kukaan näe sitä.  
* **Red Team Ratkaisu:** Tarvitset taustaprosessin (CronJob / Celery / GCP Cloud Scheduler), joka herää kerran yössä. Se etsii kannasta kaikki rivit, joilla status \== "pending" ja created\_at on yli 24h vanha. Skripti poistaa fyysisen tiedoston Firebase Storagesta Admin SDK:lla ja tuhoaa roskarivin tietokannasta.

**2\. Tietovuoto UUIDv7 \-aikaleimoista**

* **Hyökkäys / Riski:** Koska UUIDv7 sisältää aina generointihetken UNIX-aikaleiman millisekunnilleen (ensimmäiset 48 bittiä), julkisesti näkyvät ID:t (esim. GET /api/users/01H...) kertovat tarkalleen, milloin mikäkin entiteetti on luotu. Nokkela kilpailija voi seurata APIasi ja laskea suoraan, kuinka monta asiakasta tai dokumenttia järjestelmääsi luodaan päivässä (Business Intelligence \-vuoto).  
* **Red Team Ratkaisu:** Jos tämä on liiketoimintariski, säilytä UUIDv7 **vain tietokannan sisäisenä Primary Keynä**. Kun palautat ID:itä ulos Frontendiin, koodaa (obfuskoi) ne lyhyiksi hasheiksi käyttäen esimerkiksi [Hashids](https://www.google.com/search?q=https://hashids.org/python/)\-kirjastoa. Näin tietokantasi toimii salamannopeasti, mutta ulospäin asiat näyttävät satunnaisilta YouTube-tyylisiltä tunnisteilta (esim. x8B2oP).

**3\. Split-Brain: Käyttäjien poistaminen**

* **Hyökkäys / Riski:** Kun käyttäjä pyytää tilinsä poistoa (GDPR), poistat hänet PostgreSQL:stä. SQLAlchemy Cascade tuhoaa hänen metadata-rivinsä. **Mutta**, käyttäjä ja hänen 100 gigatavua tiedostojaan ovat edelleen Firebase Authissa ja Storagessa. Olet juuri luonut massiivisen rikkomuksen.  
* **Red Team Ratkaisu:** Delete-toimenpide pitää toteuttaa transaktionaalisesti ohjelmiston tasolla.  
  1. Hae käyttäjän kaikkien tiedostojen storage\_path Postgresista.  
  2. Kutsu Firebase SDK:ta poistamaan nämä tiedostot Cloudista.  
  3. Kutsu Firebase Auth SDK:ta poistamaan tili (auth.delete\_user(uid)).  
  4. Vasta KUN nämä onnistuivat, poista rivi PostgreSQL:stä.

**4\. Signed URL Abuse (Avoimet portit Storageen)**

* **Hyökkäys / Riski:** Koska backend antaa clientille luvan uploadaa tiedoston, hyökkääjä voi käyttää Signed URLia ladatakseen pilveesi haittaohjelman (esim. .exe PDF:n sijaan) tai massiivisen määrän roskaa ennen kuin URL vanhenee.  
* **Red Team Ratkaisu:** Kun generoitat Signed URLin backendissä, pakota parametreihin ehdoton sallittu koko (Content-Length-Range) sekä Content-Type.  
  Python  
  url \= blob.generate\_signed\_url(  
      expiration=timedelta(minutes=10),  
      method="PUT",  
      content\_type=file\_metadata.mime\_type, \# Pakota tyyppi (esim. application/pdf)  
  )

**Yhteenveto:** Uusi suuntasi on 5/5. Olet irtautunut kehitysvaiheen teknisestä velasta ja siirryt suoraan Cloud-Native / Enterprise \-tasolle. Rakenna Red Team \-huomiot backendisi taustalogiikkaan (kuten orpojen tiedostojen siivous), niin järjestelmäsi rullaa huoltovapaasti vuosikausia.