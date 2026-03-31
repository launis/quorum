# 04: Tekoälyn Hooks, Polyglot Context & LLM Päätepisteet

Quorum abstrahoi hallusinoivat LLM-moottorit ja luo ympärilleen säännöstön ("Zero-Math", The Tool Loop), joilla varmistetaan, etteivät mallit ajaudu poikkeustilaan omatoimisesti.

## Kognitiivinen Tiedonkäsittely (Polyglot Context Engineering)

Promptien ja datan kognitiivinen pakotus tapahtuu "Polyglot"-muodossa – yhdistämällä useita semanttisia lajityyppejä turvallisesti keskenään:
1. **Ohjeistus (Markdown):** Agentin luonne on pakotettua The Markdown:ia. Otsikoilla ja ranskalaisilla viivoilla sidostetaan tiukat Pydantic säännöt vahvaan koneoppimisavaruuteen.
2. **Kontekstin Injektio (XML-Tägit):** Asiakkaan data on laatikossa. Prompt Injection / Hyökkäykset on neutralisoitu semanttisesti estämällä tietovuodot XML-lohkojen (`<document_1>`) ulkopuolelle.
3. **Paluudata (Strict JSON):** The Zero-Math Mandate -säännöllä mallin palauttama subjektiivinen CoT/Reasoning on jäsennelty ennakolta.

## Serverless MCP Integraatio (The Tool Loop)
Kun tekoäly aistii "Episteemisen Epävarmuuden", se nojaa dynaamisiin REST-päätepisteisiin (Cloud Run/Tavily HTTP Hookit) ja kutsuu apuvälineitä. Verkko estää epävarmat valinnat tallentamalla haun empiiriset faktat globaaliksi varmenteeksi, mikä passitetaan suorana listana (`Message Pass-Through`) eteenpäin ohittaen hallusinaationarriit.

---

## The Map: Hakemistoryhmien kuvaus (Hooks & LLM)

Koodikannassa on kaksi erityistä hakemistoa LLM-keskustelun putkistohallintaan: The Hooks ja The Drivers.

### `backend_v2/hooks/` (Deterministic CPU Logic)
Tässä kansiossa asuu tiukka sääntöperäinen, ei-kognitiivinen purkuloogiikka (Fallback-vapaa alue). 
- **`scoring.py`**: Soveltaa **The Zero-Math & Micro-CoT Flattening Mandateä**. Mallin tuottamat erilliset JSON-sirpaleet (Score Float, Alaluvut ja Perustelut) parsitaan, litistetään ja muonnetaan turvallisesti yhdeksi Pydantic-turvalliseksi vastineeksi (The Justification). Tällä estetään Flutter UI:ta koskaan laskemasta keskiarvoja ajonaikana.
- **`integrity.py`**: "The Citation Integrity". Vertaa The Tool Loop/Faktojen Lähdeviitteitä säännöllisillä lausekkeilla tai tiukoilla tarkisteilla (Hallusinaatioiden tuhoaja).
- **`security.py`**: Ohjelmallinen suodatin (Banned Phrases) PII (Personal Identifiable Information) vuotoihin, heittäen luonnollisesti `AppException`in säännön rikkoutuessa.
- **`reporting.py`**: Backend-For-Frontend (BFF), Hook, joka muokkaa ja injektoi MarkDown säännöistä PDF-tason turvalliset dokumentit erilleen UI:n omista näyttöongelmista.
- **`search.py`**: Suoranaiset Vertex / Google Search -integraatio-koodistot erillaan puhtaasta tekoälymallista.

### `backend_v2/llm/` (The Drivers)
Tämä kansio kokoaa ulospäin lähtevät "Soittimet".
- LiteLLM / GenAI natiivi-yhteydet ja mallinkohtaiset serialisoijat konfiguroidaan täällä ilman, että ohjelmalogiikan askeleet ("Steps") likaantuvat spesifeillä Anthropic/OpenAI JSON -kääröillä.
