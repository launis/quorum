# 02: Pydantic-tietomalli ja Fail-Fast 

> [!CAUTION]
> Backendin arkkitehtuuri ei tunne käsitettä "fallback". Tieto on joko täydellisesti Pydantic V2 -muotoista, tai API kaatuu 422 -virheeseen The Zero-Compromise Pledgen mukaisesti.

## Data Parity ja The Zero-Compromise Pledge

Säännöstö (Blueprintit), Työnkulut (DAG) ja järjestelmän dynaaminen tilataulu (TraceEvents) perustuvat sataprosenttisesti "Strict Pydantic 2026 Mandateen". Tämä ratkaisee vanhat monoliitti-ja hallusinaatiohaasteet kieltämällä raakojen sanakirjojen (`dict`) purkamisen sokeasti.

- Vaikka kanta (Firestore) olisi korruptoitunut tai täynnä vanhaa V1 roska-dataa, API estää haittojen valumisen ohjelmalliseen logiikkaan puhtaan Rust-kuoren ansiosta.
- `model_config = ConfigDict(strict=True, extra='forbid')` -mandaatti estää laiskoja integraatioita sijoittamasta odottamattomia avaimia hyötykuormiin.

---

## The Map: Hakemistoryhmien kuvaus (Domain Models)

Kaikki järjestelmän tiedot elävät ns. "Single Source of Truth" -tilassa. Ei ole olemassa itsenäisiä DTO:ita ruutereiden pohjalla yksittäisten tiedostojen sisällä.

### `backend_v2/models/` (SSOT Datamallit)
Tämä kansio on "Pydantic V2 Strict Mode" -maailma. Määrittelee, miten Quorum näkee maailman.
- **`v2_core.py`**: Arkkitehtuurin sydän. Määrittää muun muassa `Workflow`, `PromptBlock` (agenttisolmun asetus), `Role` ja `OutputProfile` -luokat. Malleissa ei saa ikinä näkyä oletusarvoina `None` kenttiä pelkän joustavuuden vuoksi, vaan status, tyyppi ja versiot on pakotettu eksplisiittisiksi.
- **`domain/`**: Erittäin puhtaat liiketoimintamallit, joilla operoidaan järjestelmän logiikassa eristyksissä kanta-ajureista (Firestore/TinyDB).
- **`dtos/`**: Datansiirtomallit (Data Transfer Objects), joita käytetään suoraan `routers/` tason funktioiden sisään/ulostuloina sekä HTTP API-rajapinnoissa estämään over-fetching vuotoja.
- **`enums.py`**: Kielivapaat Status-, Rooli-, ja Moodi-Enumeraatiot (esim. `AUTH_ORGANIC`, `COMPLETED`).
- **`workflow.py`**: Työnkulkujen (Directed Acyclic Graph) loogiset rakennemallit ja niiden sisäiset assosiaatiot.
- **`state.py`**: DAG-Moottorin ja The Tool Loopin ajonaikainen asynkroninen tila. Ohjaa sitä, miten `TraceEvent` objektit jäädytetään ("FrozenContext").
- **`auth.py`**: Pääsyoikeuksien keskus – sisältää mm. `TokenData` sekä `User` ja `Organization` JWT-dekodauksen skeemat (Custom Claims).
