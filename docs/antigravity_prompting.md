# Kuinka ohjata Antigravity-tekoälyä Manifestin avulla

Tämä dokumentti on ohjeistus siihen, **miten saat tekoälystä (Gemini 3.1) parhaan irti** Quorum-projektissa käyttämällä `docs/flutterpromptohje.md` -manifestia "lakikirjana" pelkän ohjekirjan sijaan.

Koska olemme V8/V9 Hardening-vaiheessa, tekoälyn tehtävä ei ole "kirjoittaa koodia nopeasti", vaan **"kirjoittaa 100% manifestin mukaista, laadukasta koodia"**.

Tässä ovat parhaat taktiikat tekoälyn ohjaamiseen ("Prompting"):

---

## 1. Vaadi "Tuomarointi" ennen toteutusta (Pre-validation)

Kun pyydät tekoälyä rakentamaan uuden ominaisuuden, älä anna sen aloittaa heti koodaamista. Pakota se ensin analysoimaan tilanne Manifestin kautta. Tämä aktivoi sen "Deep Think" -päättelyn.

**✅ Hyvä syöte (Prompt):**
> "Suunnittele uusi Pydantic-malli ja reitti käyttäjän profiilikuvan päivitykselle. **Ennen kuin kirjoitat riviäkään koodia**, lue `docs/flutterpromptohje.md` ja listaa minulle ranskalaisilla viivoilla ne 3 kriittisintä sääntöä, jotka asettavat tiukimmat rajoitteet tälle uudelle reitille."

**Miksi toimii:** Tekoäly joutuu tunnistamaan konseptit (esim. The Zero-Compromise Pledge, Strict Pydantic) ennen kuin se muodostaa ratkaisun. Se ei voi oikaista.

## 2. Vaadi täsmällinen Implementation Plan ennen toteutusta (Planning Mode)

Kun vika on monimutkainen tai vaatii koskemista ydinarkkitehtuuriin, älä salli tekoälyn "sooloilla" ja alkaa suoraan koodaamaan tiedostoja sekaisin. Pakota se laatimaan tiukka `implementation_plan.md` ja hyväksyttämään se sinulla ensin.

**✅ Hyvä syöte (Prompt):**
> "Tavoitteena on implementoida uusi ominaisuus X. Ennen kuin toteutat mitään koodia, lue huolellisesti `docs/`-hakemiston ohjeet, erityisesti `docs/flutterpromptohje.md` sekä `docs/data_management.md`. Laadi tämän jälkeen tiukka `implementation_plan.md` (Käytä Planning modea). Suunnitelman on noudatettava V9 Hardening -arkkitehtuuria ja docs-kansioiden sääntöjä:
> 1. Pydantic-mallit on oltava Strict (ei dict-käyttöä, extra='ignore').
> 2. Fail-Fast: Määrittele missä poikkeukset heitetään (`AppException`).
> 3. Käy jokainen osa `docs/flutterpromptohje.md`, ja kerro kuinka suunnitelmasi noudattaa sitä.
> 4. Zero-Magic: Ei implicit castauksia.
> Pyydä minulta lupa (Review), kun suunnitelma on valmis, jotta voin hyväksyä sen ennen koodaustyön aloittamista (Execution).
"

**Miksi toimii:** Tämä erottaa tekoälyn *suunnitteluvaiheen* ja *suoritusvaiheen*. Saat itse lukea ja torjua huonot arkkitehtuurivalinnat ennakkoon ilman, että joudut perumaan kymmeniä pieleen menneitä koodimuokkauksia.

## 3. Vaadi orjallista toteutusta (Execution Mode)

Kun `implementation_plan.md` on valmis ja olet sen hyväksynyt, anna tekoälylle selkeä ja tiukka käsky toteuttaa se. Älä anna sille lupaa sooloilla suunnitelman ulkopuolelle.

**✅ Hyvä syöte (Prompt):**
> "Olen lukenut ja hyväksynyt `implementation_plan.md` -dokumentin. Siirry Execution-tilaan ja aloita toteutus. 
> Säännöt suoritukselle:
> 1. Noudata suunnitelmaa orjallisesti. Jos törmäät esteeseen, jota suunnitelma ei huomioinut, keskeytä suoritus ja kysy minulta neuvoa (Notify User).
> 2. Koodin on oltava täysin linjassa `docs/flutterpromptohje.md` -manifestin kanssa (Strict Pydantic, Fail-Fast, Zero-Magic). 
> 3. Tee uudet testit tai tutki onko vanhoissa jo olemassa valmiita testejä. Varmista, että mikään vanha testi ei hajoa muutosten myötä. Aja testit paikallisesti ennen koodin lukitsemista.
> 4. Käy jokainen osa `docs/flutterpromptohje.md`, ja kerro kuinka suunnitelmasi noudattaa sitä.
> 5. Kun valmista, tee `walkthrough.md` -dokumentti todisteeksi muutoksista."

**Miksi toimii:** Tämä asettaa agentin puhtaasti "koodari"-tilaan, viilaa pois tarpeettoman suunnittelun ja asettaa tiukat rajat (Fail-Fast myös tekoälyn työskentelylle).

## 4. Käytä Manifestia "Kiistojen ratkaisijana" (Tie-breaker)

Kun huomaat, että koodissa on virhe tai tekoäly on alkanut laiskistua pitkän istunnon aikana (esim. alkanut ehdottaa `dict`-palautuksia tai `try-except pass` -purkkapurkkavirityksiä), pysäytä se käyttämällä Manifestia absoluuttisena auktoriteettina.

**✅ Hyvä syöte (Prompt):**
> "Tämä koodinpätkä tiedostossa `backend/routes/auth.py` rivillä 50 palauttaa `dict`:n. Vertaa tätä valintaa `docs/flutterpromptohje.md` Osan 2 (Data Passing Mandate) sääntöihin. Mikä tässä on pielessä, miksi, ja miten Manifesti ckäskisi sen korjata?"

**Miksi toimii:** Tämä herättää tekoälyn huomaamaan oman (tai vanhan koodin) rikkomuksen. Se ymmärtää, että kyseessä on *kielletty anti-pattern*, joka täytyy armottomasti refaktoroida, eikä vain "vähän korjailla".

## 3. Vaadi "Zero-Shortcut" Auditointi sessioiden lopuksi (Review)

Jokaisen monimutkaisemman tiketin tai koodaussession päätteeksi, ennen kuin koodi kommitoidaan, laita tekoäly auditoimaan oma työnsä. "Koodisokeus" iskee tekoälyynkin pitkissä ketjuissa.

**✅ Hyvä syöte (Prompt):**
> "Ominaisuus vaikuttaa nyt toimivan lokaalisti. Aja vielä virtuaalinen koodikatselmointi (Code Review) näille kolmelle tiedostolle, joita juuri muokkasimme. Etsi **erityisen aggressiivisesti rikkomuksia `docs/flutterpromptohje.md` -tiedoston Osa 18 (The Zero-Compromise Pledge)** sääntöjä vastaan. Jos löydät ainuttakaan `try-except pass` tai hiljaista `None` -palautusta, poista ne välittömästi ja korjaa ne Fail Fast -periaatteen mukaisiksi."

**Miksi toimii:** Tämä komento pakottaa tekoälyn astumaan ulos "ongelmanratkaisijan" roolista ja siirtymään "kriittisen auditoijan" rooliin. Se huomaa usein omat laiskat ratkaisunsa ja pakottaa laadun Manifestin tasolle.

---

### Tiivistelmä (Muistilista)
1. **Älä koskaan sano vain "Tee tämä".** Sano: *"Tee tämä noudattaen Manifestin sääntöjä X ja Y."*
2. **Kudo Manifesti osaksi refaktorointia.** *"Tämä on vanhaa koodia, refaktoroi se vastaamaan Manifestin Part 4 (Riverpod) standardia."*
3. **Käytä tekoälyn analyysikykyä.** *"Rikkooko ehdottamasi arkkitehtuuri jotain Manifestin sääntöä? Mieti tarkkaan."*
