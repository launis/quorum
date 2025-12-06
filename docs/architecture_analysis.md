# Tekninen Arkkitehtuuri ja Analyysi: RAG, Kausaalisuus & PII

Tämä dokumentti kuvaa Cognitive Quorum v2 -järjestelmän teknisen arkkitehtuurin ja analysoi sen ydinominaisuuksia. Dokumentti keskittyy toteutettuihin ratkaisuihin ja niiden teknisiin perusteisiin.

---

## 1. Professional RAG (Retrieval-Augmented Generation)

**Arkkitehtuuri:**
Järjestelmä hyödyntää "Semantic Search" -mallia laajojen dokumenttimassojen käsittelyyn. Tämä korvaa aiemman "Context Stuffing" -lähestymistavan, jossa koko dokumentti syötettiin kerralla kielimallille.

*   **Ingestion:** Dokumentit pilkotaan temaattisesti yhtenäisiksi kappaleiksi (chunks) ja muunnetaan numeerisiksi vektoreiksi (embeddings) käyttäen tehokasta embedding-mallia. Nämä vektorit indeksoidaan vektoritietokantaan (ChromaDB), jossa säilytetään myös viittaus alkuperäiseen lähteeseen.
*   **Retrieval:** Käyttäjän kysely muunnetaan vastaavaksi embedding-vektoriksi. Järjestelmä suorittaa vektoritietokantaan semanttisen haun (vector similarity search), joka palauttaa kyselyä lähinnä olevat tekstikappaleet. Vain nämä relevantit kappaleet syötetään LLM:n kontekstiin vastauksen muodostamista varten.

| Ominaisuus | Hyödyt (Pros) | Haitat (Cons) |
| :--- | :--- | :--- |
| **Skaalautuvuus** | Mahdollistaa satojen tai tuhansien sivujen käsittelyn. LLM:n konteksti-ikkuna ei enää rajoita datan määrää. | Lisää järjestelmän monimutkaisuutta (tietokannan ylläpito, indeksointi). |
| **Tarkkuus** | Vähentää hallusinaatioita ("Lost in the Middle" -ilmiö), koska LLM saa vain relevantin tiedon, ei kohinaa. | Haku voi epäonnistua ("Retrieval Failure"), jos kysely ja dokumentti eivät kohtaa semanttisesti. Vaatii laadukkaan embedding-mallin. |
| **Kustannukset** | Pienemmät token-kustannukset per kysely, koska promptiin ei syötetä turhaa dataa. | Aloituskustannus (embeddingien luonti) ja vektoritietokannan infrastruktuurikulut. |
| **Jäljitettävyys** | Voidaan osoittaa tarkasti, mistä tekstikappaleesta vastaus on peräisin (sitaatit). | Vaatii metadatan huolellista hallintaa ingestion-vaiheessa. |

**Suunnitteluperiaate:** RAG-arkkitehtuuri on valittu, koska se on välttämätön laajojen ja useiden dokumenttien tehokkaaseen ja kustannustehokkaaseen analyysiin.

---

## 2. Real Causal Inference (Microsoft DoWhy)

**Arkkitehtuuri:**
Järjestelmä ei ainoastaan tukeudu LLM:n tekstistä tuottamaan intuitioon, vaan hyödyntää formaalia tilastollista päättelyä kausaalisuhteiden validoimiseksi.

*   **Graph Generation:** LLM tunnistaa tekstistä potentiaalisia syy-seuraussuhteita (esim. "A aiheuttaa B:n") ja rakentaa niistä kausaaligraafin (Directed Acyclic Graph, DAG).
*   **Refutation Engine:** Microsoftin DoWhy-kirjasto ottaa LLM:n generoiman graafin ja datan syötteekseen. Se yrittää systemaattisesti *kumota* ehdotetut kausaaliväitteet tilastollisilla testeillä (esim. Placebo Test, Random Cause). Vain testit läpäisseet väitteet raportoidaan luotettavina.

| Ominaisuus | Hyödyt (Pros) | Haitat (Cons) |
| :--- | :--- | :--- |
| **Luotettavuus** | Erottaa korrelaation aidosta kausaatiosta. Estää LLM:ää "keksiä" syy-yhteyksiä, jotka eivät kestä loogista tai tilastollista tarkastelua. | Vaatii strukturoitua dataa toimiakseen täydellisesti. Pelkällä tekstillä tehtävä kausaalianalyysi on aina osittain kvalitatiivista. |
| **XAI (Selitettävyys)** | Tarjoaa matemaattisen perustelun ("refutation score") väitteille, mikä lisää analyysin luotettavuutta ja läpinäkyvyyttä. | Tekninen kynnys on korkea. DoWhy-kirjasto on monimutkainen ja vaatii tilastotieteen perusteiden ymmärrystä. |
| **Bias-tunnistus** | Auttaa tunnistamaan sekoittavat tekijät (Confounders), jotka vääristävät tuloksia. | Laskennallisesti raskasta. Voi hidastaa analyysiprosessia merkittävästi. |

**Suunnitteluperiaate:** Kausaalipäättely on järjestelmän "High-End"-ominaisuus, joka on kriittinen, kun analyysia käytetään tärkeään päätöksentekoon, jossa virheillä on merkittäviä seurauksia.

---

## 3. Professional PII (Microsoft Presidio)

**Arkkitehtuuri:**
Järjestelmä käyttää kontekstuaalista NLP-pohjaista tunnistusta henkilötietojen (PII) anonymisointiin, mikä on merkittävästi luotettavampi kuin pelkkiin säännöllisiin lausekkeisiin (Regex) perustuva menetelmä.

*   **Analyzer:** Spacy-pohjainen kielimalli analysoi lauserakenteen ja sanan kontekstin. Se ymmärtää esimerkiksi, että "Matti" on lauseessa "Matti meni kauppaan" henkilön nimi sen kieliopillisen roolin perusteella, vaikka nimi olisi järjestelmälle ennestään tuntematon.
*   **Anonymizer:** Modulaarinen moottori mahdollistaa tunnistetun tiedon joustavan käsittelyn: maskauksen (`*****`), korvaamisen tyypillä (`<PERSON>`) tai pseudonymisoinnin (esim. "Matti" -> "Henkilö A" kaikkialla tekstissä).

| Ominaisuus | Hyödyt (Pros) | Haitat (Cons) |
| :--- | :--- | :--- |
| **Turvallisuus** | Tunnistaa PII-tiedon, jota Regex ei löydä (esim. nimet ilman isoja alkukirjaimia, harvinaiset nimet, kontekstisidonnaiset tiedot). | Raskaampi ajettava. Vaatii NLP-mallin lataamisen muistiin (satoja megatavuja). |
| **Joustavuus** | Tukee kymmeniä eri entiteettityyppejä (sijainti, organisaatio, lääketieteellinen koodi) suoraan paketista. | Vaatii kielikohtaisen mallin. Suomen kielen tuki vaatii erillisen mallin integroinnin, kun taas englanti toimii suoraan. |
| **Eheys** | Mahdollistaa "Pseudonymisoinnin", jolloin tekstin looginen rakenne ja luettavuus säilyvät analyysia varten, vaikka henkilötiedot on poistettu. | Konfigurointi on työläämpää kuin yksinkertainen "etsi ja korvaa". |

**Suunnitteluperiaate:** Kontekstuaalinen PII-käsittely on valittu, koska se on ehdoton vaatimus GDPR-yhteensopivuudelle tuotantoympäristössä käsiteltäessä vapaamuotoista tekstiä.

---

## V2-järjestelmäarkkitehtuuri

Quorum v2 -arkkitehtuuri on modulaarinen ja dataohjattu. Se koostuu erillisistä käyttöliittymä-, taustajärjestelmä- ja ydinlogiikkakerroksista. Järjestelmän toiminta ei ole kovakoodattu, vaan se perustuu tietokantaan tallennettuihin työnkulkumäärityksiin (Workflows).

*   **Frontend (Streamlit):** Selainpohjainen käyttöliittymä, joka vastaa käyttäjäinteraktiosta, kuten dokumenttien lataamisesta, analyysipyyntöjen lähettämisestä ja tulosten visualisoinnista. Se kommunikoi backendin kanssa REST API -kutsuilla.
*   **Backend (FastAPI):** Tarjoaa HTTP-pohjaisen REST API:n, joka ottaa vastaan pyyntöjä frontendiltä. Se vastaa pyyntöjen validoinnista, tilanhallinnasta ja tehtävien orkestroinnista kutsumalla geneeristä työnkulkumoottoria.
*   **Generic Workflow Engine:** Järjestelmän ydin. Moottori ei sisällä itsessään liiketoimintalogiikkaa, vaan se suorittaa tietokannasta ladatun työnkulun mukaisia vaiheita. Työnkulku määrittelee, mitä agentteja (esim. PII, RAG, Causal) ja missä järjestyksessä ajetaan.
*   **Databases:**
    *   **Workflow & Config DB:** Relaatiotietokanta (esim. SQLite/PostgreSQL), joka sisältää työnkulkujen määritykset, agenttien konfiguraatiot ja järjestelmän metadatan.
    *   **Vector DB (ChromaDB):** Vektoritietokanta, johon on tallennettu dokumenttien embedding-vektorit semanttista hakua varten.

### Arkkitehtuurikaavio

```mermaid
graph TD
    User[Käyttäjä] --> FE[Frontend (Streamlit)]

    subgraph "Backend API (FastAPI)"
        FE -- API Call --> API[REST API]
        API --> Engine[Generic Workflow Engine]
    end

    subgraph "Core Services & Data"
        Engine -- "1. Reads Workflow" --> DB[(Workflow & Config DB)]
        Engine -- "2. Invokes Agents" --> PII[PII Agent (Presidio)]
        PII --> RAG[RAG Agent]
        RAG -- "Semantic Search" --> VDB[(Vector DB)]
        RAG --> Causal[Causal Agent (DoWhy)]
        Causal -- "3. Returns Result" --> Engine
    end
    
    Engine -- "4. API Response" --> API
    API --> FE
    
    subgraph "Data Ingestion (Offline)"
        Docs[Lähdedokumentit] --> Ingest[Ingestion Pipeline]
        Ingest --> VDB
    end
```