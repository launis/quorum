# CONTEXT & ROLE
Olet kokenut Technical Writer ja Staff-tason ohjelmistoarkkitehti. Olemme juuri saaneet päätökseen laajan koodipohjan refaktoroinnin (FastAPI & Flutter). Koodi noudattaa nyt tiukkaa Clean Architecturea: SSOT (Single Source of Truth), Fail-Fast, Service/Repository -kerrosten sisäinen CRUD API, SDUI, tiukka Pydantic-validointi, RFC 7807 -virheenkäsittely ja No-String I18N.

Seuraava tehtävämme on päivittää projektin `docs/`-hakemiston dokumentaatio vastaamaan tätä uutta, refaktoroitua järjestelmää ja alan parhaita teknisen dokumentaation käytäntöjä.

ÄLÄ ALOITA TIEDOSTOJEN MUOKKAAMISTA VIELÄ. Luo minulle ensin ainoastaan dokumentaation päivityksen tiekartoitus (Execution Plan).

---

# DOCUMENTATION MANDATES & PRINCIPLES

### 1. Parhaat dokumentaatiokäytännöt (Best Practices)
- **DRY (Don't Repeat Yourself):** Samaa asiaa ei selitetä monessa eri tiedostossa. Määrittele konseptit yhdessä päädokumentissa ja käytä Markdownin ristiinlinkitystä muissa tiedostoissa.
- **Yhtenäinen ja selkeä rakenne:** Käytä loogista Markdown-hierarkiaa (H1, H2, H3). Vältä pitkiä sekavia tekstimassoja, suosi listoja, koodiesimerkkejä ja tiivistelmiä.
- **Ajantasaisuus:** Kaikkien koodiesimerkkien, arkkitehtuurikuvausten ja termien on heijastettava UUTTA refaktoroitua tilaa (esim. reitittimissä ei logiikkaa, I18N on ICU-muotoiltu frontendissä, data on tiukasti tyypitetty). Poista säälimättä kaikki vanhentunut (legacy) tieto ja väärät oletukset.
- **Kieli:** Kkaikkien kooditermien, tiedostonimien, funktioiden ja arkkitehtuurikonseptien on vastattava tarkalleen englanninkielistä koodipohjaa.

### 2. Erikoistehtävä: "docs/alku.md" -yhteenveto ens
- Tiedosto `docs/alku.md` on toiminut projektin alussa, kontekstin ensimmäisenä promptina, tärkeän tiedon ja sääntöjen keräilyaltaana. Se sisältää linkit kaikkiin tärkeisiin tiedostoihin ja konsepteihin ja siihen koostetaan napakasti ja yhteenveromaisesti ne asiat jotka ovat tärkeitä kehittämmisen kannalta mutta kuitenkin hallittavissa ja ymmärrettävissä ilman että tarvitsee lukea kaikkia muita dokumentteja.
 
### 3. Yksi tiedosto kerrallaan (Single-File Tasking)
- Suunnitelman askeleet on jaoteltava niin, että yhdessä askeleessa muokataan / päivitetään vain **YHTÄ kohdedokumenttia kerrallaan** 
- Et saa muokata tai uudelleenkirjoittaa useita eri dokumentteja samassa ajossa. Tämä takaa laadun ja sen, ettei konteksti katoa tai hallusinoidu.

---

# EXECUTION PLAN REQUIREMENTS (Suunnitelman rakenne)

Lue ja analysoi `docs/`-hakemiston jokaisen tiedoston nykyinen sisältö. 

TÄRKEÄ: Varmista, että luettavan okumentin sisältö perustuu puhtaasti nykyiseen koodipohjaan, tietokantaan ja sen arkkitehtuuriin.

Laadi minulle suunnitelma, jossa koko `docs/`-hakemiston päivitys on jaettu erittäin pieniin askeliin (Step 1, Step 2, Step 3...).


**Jokaisesta askeleesta on ilmettävä selkeästi:**
1. **Askeleen tunniste ja nimi:** (esim. "Step 2: Päivitetään docs/architecture.md")
2. **Kohdetiedostot:** Mitä *yhtä* dokumenttitiedostoa tässä askeleessa päivitetään.
3. **Tavoitteet ja toimenpiteet:** 
   - Mitä uutta kohdedokumenttiin lisätään tai mitä vanhentunutta sieltä poistetaan, jotta se vastaa uutta koodipohjaa?
   - **Tiedon siirto:** Mitä arvokasta tietoa integroidaan nimenomaan `docs/alku.md` -tiedostostoon.

Luo nyt tämä vaiheistettu Master Plan dokumentaation päivitykselle. Kun olet valmis, jää odottamaan, että annan sinulle erillisen käskyn aloittaa "Step 1" suorittaminen. Älä muokkaa vielä mitään tiedostoja.