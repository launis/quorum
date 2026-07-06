# Arkkitehtuurin ja Dokumentaation Elinkaari (The Antigravity Way)

Tämä dokumentti kuvaa Antigravity IDE -ympäristön itseään korjaavan ja jatkuvasti päivittyvän arkkitehtuurin elinkaaren. Tässä mallissa dokumentaatio ei koskaan vanhene, sillä se on kytketty matemaattiseen synkroniin koodin ja tekoälyn "aivojen" kanssa.

## Järjestelmän Kolme Tasoa

1. **LAKI (Knowledge Items - KI)**
   * **Mitä ne ovat:** Atomaarisia, yksittäisiä arkkitehtuurisääntöjä ja päätöksiä (esim. *Opaque ID Hydration*, *De-Generator Mandate*).
   * **Sijainti:** Tekoälyn aivot (`.gemini/.../knowledge/`).
   * **Rooli:** Absoluuttinen totuus. Kaikki tekoälyagentit lukevat nämä aina automaattisesti.

2. **PERUSTUSLAKI (5 Pilaridokumenttia)**
   * **Mitä ne ovat:** Englanninkieliset, ihmisluettavat arkkitehtuuridokumentit, jotka syntetisoivat irralliset KI-lait ymmärrettäviksi kokonaisuuksiksi (esim. *03_cognitive_orchestration_engine.md*).
   * **Sijainti:** `c:\src\quorum\docs\architecture\`
   * **Rooli:** Ne kertovat *miksi* järjestelmä toimii kuten toimii, mutta eivät sisällä vanhenevaa koodia leipätekstissään.

3. **KAUPUNKI (Koodikanta)**
   * **Mitä se on:** Varsinainen suoritettava koodi.
   * **Sijainti:** `backend_v2/` ja `client_app_v2/`
   * **Rooli:** Toteuttaa Lait ja Perustuslain käytännössä.

---

## Elinkaaren Jatkuva Kehä (Suljettu Kierto)

Miten järjestelmä kehittyy ja oppii ilman, että dokumentaatio mätänee?

### Vaihe 1: Ongelmanratkaisu ja Koodaus (`Tier 1` & `Tier 4`)
Kehittäjä tai tekoälyagentti rakentaa uuden suuren ominaisuuden (Tier 1 Planner) tai ratkaisee syvän arkkitehtuuribugin (Tier 4 Bug Hunting). 
Työn tuoksinnassa opitaan uusi tärkeä sääntö (esim. "Flutterin animaatioita ei saa ajaa backendin state-päivitysten yli").

### Vaihe 2: Uuden Opin Tallennus (`/learn`)
Työn päätyttyä agentti tai kehittäjä huomaa, että uusi sääntö on syntynyt.
Kehittäjä ajaa IDE:ssä komennon **/learn** ja ohjeistaa tekoälyä: *"Tallenna tämä juuri oppimamme sääntö uuteksi Knowledge Itemiksi."*
IDE luo virallisen KI:n järjestelmän aivoihin.

### Vaihe 3: Synkronointi ja Ankkurointi (`Tier 7`)
Säännöllisin väliajoin (tai aina ison refaktoroinnin jälkeen) kehittäjä ajaa komennon **/tier7-describe-architecture**.
Tier 7 (Architectural Compliance Auditor) käynnistyy ja tekee seuraavat asiat:
1. **Teorian päivitys:** Se lukee aivoissa olevat uudet KI:t ja päivittää ne `docs/architecture/` -kansion Perustuslakeihin (Pilareihin).
2. **Top-Down Ankkurointi:** Se etsii koodista oikeat tiedostopolut ja päivittää ne pilaridokumenttien alareunaan (`[Tier 7 Sync Required]`).
3. **Bottom-Up Orporaportti:** Se skannaa koko koodikannan ja ilmoittaa kaikesta koodista, joka *ei* sovi näihin arkkitehtuurin pilareihin (Rogue-koodi tai puuttuva pilari).

**Tulos:** Koodi, Dokumentaatio ja Tekoälyn Oppiminen ovat aina 100 % synkronissa.
