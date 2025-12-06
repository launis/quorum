# Tekninen Arkkitehtuuri ja Analyysi: RAG, Kausaalisuus & PII

Tämä dokumentti syventää `implementation_plan_v2.md`:n kuvaamia ratkaisuja analysoimalla niiden hyödyt, haitat ja teknisen arkkitehtuurin Quorum-järjestelmän kontekstissa.

---

## 1. Professional RAG (Retrieval-Augmented Generation)

**Arkkitehtuuri:**
Järjestelmä siirtyy "Context Stuffing" -mallista (kaikki teksti kerralla promptiin) "Semantic Search" -malliin.
*   **Ingestion:** Dokumentit -> Text Splitter (500 token chunks) -> Embedding Model (OpenAI/HuggingFace) -> Vector Store (ChromaDB).
*   **Retrieval:** User Query -> Query Embedding -> Vector Similarity Search (Top-K) -> LLM Context.

| Ominaisuus | Hyödyt (Pros) | Haitat (Cons) |
| :--- | :--- | :--- |
| **Skaalautuvuus** | Mahdollistaa satojen tai tuhansien sivujen käsittelyn. LLM:n konteksti-ikkuna ei enää rajoita datan määrää. | Lisää järjestelmän monimutkaisuutta (tietokannan ylläpito, indeksointi). |
| **Tarkkuus** | Vähentää hallusinaatioita ("Lost in the Middle" -ilmiö), koska LLM saa vain relevantin tiedon, ei kohinaa. | Haku voi epäonnistua ("Retrieval Failure"), jos kysely ja dokumentti eivät kohtaa semanttisesti. Vaatii laadukkaan embedding-mallin. |
| **Kustannukset** | Pienemmät token-kustannukset per kysely, koska promptiin ei syötetä turhaa dataa. | Aloituskustannus (embeddingien luonti) ja vektoritietokannan infrastruktuurikulut. |
| **Jäljitettävyys** | Voidaan osoittaa tarkasti, mistä tekstikappaleesta vastaus on peräisin (sitaatit). | Vaatii metadatan huolellista hallintaa ingestion-vaiheessa. |

**Suositus:** Välttämätön, jos analysoitavien dokumenttien pituus ylittää n. 20-30 sivua tai jos dokumentteja on useita.

---

## 2. Real Causal Inference (Microsoft DoWhy)

**Arkkitehtuuri:**
Siirrytään pelkästä LLM:n "intuitiosta" formaaliin tilastolliseen päättelyyn.
*   **Graph Generation:** LLM louhii tekstistä väitteet (A aiheuttaa B:n) ja luo kausaaligraafin (DAG).
*   **Refutation Engine:** DoWhy-kirjasto ottaa graafin ja datan, ja yrittää *kumota* väitteen matemaattisesti (esim. Placebo Test: "Jos vaihdan syyn satunnaiseen, muuttuuko seuraus?").

| Ominaisuus | Hyödyt (Pros) | Haitat (Cons) |
| :--- | :--- | :--- |
| **Luotettavuus** | Paljastaa korrelaation ja kausaation eron. Estää LLM:ää "keksiä" syy-yhteyksiä, jotka eivät kestä loogista tarkastelua. | Vaatii strukturoitua dataa toimiakseen täydellisesti. Pelkällä tekstillä tehtävä kausaalianalyysi on aina osittain kvalitatiivista. |
| **XAI (Selitettävyys)** | Tarjoaa matemaattisen perustelun ("p-arvo", "refutation score") väitteille, mikä lisää luottamusta raporttiin. | Tekninen kynnys on korkea. Kirjastot (DoWhy) ovat monimutkaisia ja vaativat tilastotieteen ymmärrystä. |
| **Bias-tunnistus** | Auttaa tunnistamaan sekoittavat tekijät (Confounders), jotka vääristävät tuloksia. | Laskennallisesti raskasta. Voi hidastaa analyysiprosessia merkittävästi. |

**Suositus:** "High-End" ominaisuus. Kriittinen, jos järjestelmää käytetään päätöksentekoon, jossa virheillä on suuri hinta (esim. lääketiede, juridiikka). Peruskäytössä voi olla "overkill".

---

## 3. Professional PII (Microsoft Presidio)

**Arkkitehtuuri:**
Siirrytään säännöistä (Regex) kontekstiin (NLP).
*   **Analyzer:** Spacy-kielimalli lukee lauseen rakenteen ("Matti meni kauppaan"). Se ymmärtää, että "Matti" on nimi, koska se on subjektina, vaikka nimi olisi tuntematon.
*   **Anonymizer:** Modulaarinen moottori, joka voi maskata (`*****`), korvata (`<PERSON>`) tai kryptata datan.

| Ominaisuus | Hyödyt (Pros) | Haitat (Cons) |
| :--- | :--- | :--- |
| **Turvallisuus** | Tunnistaa PII-tiedon, jota Regex ei löydä (esim. nimet ilman isoja alkukirjaimia, harvinaiset nimet, kontekstisidonnaiset tiedot). | Raskaampi ajettava. Vaatii NLP-mallin lataamisen muistiin (satoja megatavuja). |
| **Joustavuus** | Tukee kymmeniä eri entiteettityyppejä (sijainti, organisaatio, lääketieteellinen koodi) suoraan paketista. | Vaatii kielikohtaisen mallin. Suomen kielen tuki vaatii erillisen mallin (esim. TurkuNLP) integroinnin, englanti toimii suoraan. |
| **Eheys** | Mahdollistaa "Pseudonymisoinnin" (Matti -> Henkilö A, Matti -> Henkilö A), jolloin tekstin luettavuus ja logiikka säilyy analyysia varten. | Konfigurointi on työläämpää kuin yksinkertainen "etsi ja korvaa". |

**Suositus:** Ehdoton vaatimus GDPR-yhteensopivuudelle tuotantoympäristössä. Regex ei riitä oikeudellisesti pätevään anonymisointiin vapaassa tekstissä.

---

## Yhteenveto Arkkitehtuurista (Target State)

```mermaid
graph TD
    User[Käyttäjä] --> UI[Streamlit UI]
    UI --> Guard[Guard Agent (Presidio)]
    
    subgraph "Data Layer"
        RawDocs[Dokumentit] --> Ingest[Ingestion Pipeline]
        Ingest --> VectorDB[(ChromaDB)]
    end
    
    subgraph "Analysis Layer"
        Guard -->|Sanitized Data| Analyst[Analyst Agent]
        Analyst <-->|Semantic Search| VectorDB
        Analyst --> Causal[Causal Agent (DoWhy)]
        Causal -->|Causal Graph| Refuter[Refutation Engine]
    end
    
    Refuter --> Report[XAI Report]
```
