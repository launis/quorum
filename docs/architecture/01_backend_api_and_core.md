# 01: API-kerros ja Asynkroninen tapahtumahallinta (Core)

Quorum V2 on rakennettu järeän asynkronisen Python FastAPI -kerroksen ja tilattomien ruutereiden varaan. Koska järjestelmä rakentuu raskaiden tekoäly-DAG:ien ympärille ja nojaa "Fire and Forget" -malliin (palauttaa nopeasti "202 Accepted"), lokaali käyttöliittymä (Flutter) saa tiedon mutaatioista erillisen synkronointimekanismin (WebSocket) ja Push-mutaatioiden avulla.

## Asynkroninen tapahtumahallinta ja Integraatiot (Event-Driven Loop)

### Kaksivaiheinen reaktiivinen luuppi (Reactive UI Loop)
Kun Frontend pakottaa käskyn aloittaa jopa kymmeniä minuutteja kestävän tekoälyajon, tila puretaan ilman blokkaavia API-kyselyitä (HTTP Polling):

1. **Optimistic Start (Riverpod):** Saatuaan API:ltä "202 Accepted" vahvistuksen, Frontend esittää 0 ms latenssilla lokaalin tilan (`PENDING / RUNNING`).
2. **Worker Terminal Write:** Arq Worker suorittaa taustalla verkon loppuun ja tekee tilamuutoksen Master DB:hen yhtenä atomisena mutaationa (`COMPLETED` tai `FAILED`).
3. **Reaktiivinen Push:** Flutterin käyttöliittymä ylläpitää `firestore.collection.snapshots()` -kuuntelijaa. Uusi tila lennähtää muistiin ja uusi XAI-raportti renderöityy reaaliajassa.

### Enterprise Integraatiot (Webhookit)
B2B-järjestelmien "Server-to-Server" (S2S) integraatiot hyödyntävät Webhookkeja (SaaS Integration Layer):
1. **Tenant-Specific Webhookit:** Asiakas tallentaa CRM-järjestelmänsä HTTP-osoitteen.
2. **Webhook Dispatcher:** Kun asynkroninen Node saavuttaa päätetilan, Dispatcher ampuu **HTTP POST** -pyynnön valmiilla JSON:illa kohteeseen.

---

## The Map: Hakemistoryhmien kuvaus (API & Core)

Koodikannassa ("The Modular Async Monolith") ohjaustaso ja käynnistys asuvat omissa vahvasti nimetyissä kansioissaan `backend_v2/` juuressa. Näissä kerroksissa *kognitio ei koskaan vuoda rajapintoihin*.

### `backend_v2/api/` (FastAPI Control Plane)
Ylin REST-rajapintakerros, joka vastaanottaa pyynnöt, ajaa ne Pydantic-turvamuuriin ja siirtää palveluille. 
- **`routers/`**: Eriytetyt HTTP REST V2 -ruuterit. Reititin ei koskaan sisällä liiketoimintalogiikkaa (Anemic pattern).
  - `execution/`: DAG-ajojen hallinta (aloitus, tila) ja `/report` BFF-päätepiste (Backend-For-Frontend).
  - `iam/`: Identiteetin, työtilojen (org) ja Custom Claims -roolien mutaatiot.
  - `studio/`: Graafisen Workflow Studion puhtaat CRUD-tilarajapinnat.

### `backend_v2/core/` (Arkkitehtuurikonfiguraatiot)
Sisältää järjestelmän keskitetyn infrastruktuurin, joka säestää FastAPI:n ruutereita. Varsinainen liiketoiminta puuttuu täältä.
- Sisältää luokat ja moduulit kuten `BaseException`, virheiden serialisoijat RFC 7807 -muotoon sekä Dependency Injection -työkalut.

### Pääkäynnistimet
- **`backend_v2/main.py`**: FastAPI ohjelman päänielu (Entry point). Rekisteröi kaikki ruuterit, konfiguroi CORS-säännöt ja asettaa lokituksen middlewaret. 
- **`backend_v2/settings.py`**: Ainoa paikka missä ympäristömuuttujat (`.env`) ladataan sisään Pydanticin `BaseSettings` -luokan avulla. Suojelee muuta järjestelmää satunnaisilta kovakoodatuilta asetuksilta.
