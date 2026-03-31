# 05: Datan Pysyvyys, CQRS ja The Seed Vault

Koko orkestraattorin datan pysyvyys on mallinnettu **UnifiedRepository** abstraktion varaan. Luku- ja kirjoitusoperaatiot ovat irti liiketoimintapalveluista, varmistamalla modulaarinen ja moni-driver-yhteensopivuus.

## Tietomalli: Lokaali TinyDB vs Tuotannon Firestore (Master DB)
* **Local Caching:** Backend käyttää turvallista erillistä `db_v2.json` kantaa (Asynkroninen TinyDB) ajojen kehityksessä, minne Opaque Stripe ID -reititys kirjoittaa vapaasti säännöt (`USE_MOCK_DB=true`).
* **Firestore CQRS:** Tuotannossa Quorum nojaa vahvaan Eventual Consistenty -irtaantumiseen Firestore API:llä, miniteisillä "Command and Query" -jaoilla. Kaikki mutaatiot lähetetään REST API:n "Validointimuuriin" (FastAPI), estäen Frontend-kallista kirjoittamista Client SDK:lla. Firestoreen tallentuvat vain Pydantic Opaque ID:n viitteet – itse raskaat DAG-prosessien 10 MT Tracet ajetaan halvempaan **GCP Cloud Storage** (GCS) tilaan Blobiksi. 

## The Seed Vault - DNA:n turvaaminen
Kehityksessä tietokantaa ei koskaan ronkita "konepellin alta". Järjestelmältä löytyy The Seed Vault -määräyksen mukainen tiedosto kansion juuresta, jonne kirjataan Workflow-, Agent-, ja Arviointi-toteumat puhtaana JSON-datana tiukan tyyppijärjestelmän valmiiksi tunnistamina objekteina. Arkkitehtuuri ei poikkea manuaalisilla TinyDB muokkauksilla; kaikki siirtyy seedistä "Ajamalla".

---

## The Map: Hakemistoryhmien kuvaus (Data & Configs)

Nämä kansiot asettavat infrastruktuurin rajat varsinaiselle datan säilytykselle ja ympäristöjen pystytykselle.

### `backend_v2/database/` (The Unified Repository)
Tämä arkkitehtuurialue käsittelee aitoja i/o -mutaatioita rajapinnalle levylle tai pilveen.
- **`repository.py`**: Abstrakti pohja (AbstractWorkflowRepository), johon palvelukerros viittaa. Ei tietokantariippuvuuksia, vain kovia Pythonin Type Hint -protokolloja.
- **`firestore_repo.py`**: Tuotannon toteutus (Firebase Admin SDK:n wrapperi), yhdistää Firestoren ja dynaamisesti luovien Blobs-objektien (GCP Storage) logiikan.
- **`wrapper.py`**: Valvoo virheiden kiinniottoja ja turvamuuria tietokantadriverin (Timeout) ja puhtaan Pydantic Exception -järjestelmän välillä.
- **`db_v2.json`**: Fyysinen lokaali Mock Database, poistetaan `.gitignore`lla, mutta pysyvyyden sydän Zero-Cloud testauksessa.

### `backend_v2/seed/` (The Zero-Deploy Configuration)
The Configuration-As-Code koti asiantuntijoiden konfiguroimille säännöksille.
- **`seed_data.json`**: ITSE DNA. Sisältää valmiit `output_profiles`, `workflows`, ja tekoälyn järjestelmämallien parametrit asynkroniseen injektointiin.
- **`seed_registry.py`**: Ohjelma, joka suorittaa purkutyön Pydantic mallien `model_validate()` funktioilla varmistaen, että tietokanta saa aina stabiilia ja Pydantic Strict luotettavaa dataa.
- **`run_seed.py`**: "The Seed CLI Tool" - Käynnistyskomento.
  - Komento lennosta luo (seeding) lokaalin tietokannan: `uv run python backend_v2/seed/run_seed.py local`.
  - Tuotannon (Firebase) alustus käyttää: `... run_seed.py firestore`.
