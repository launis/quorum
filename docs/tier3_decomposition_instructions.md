# Ohje: Miten käyttää /tier3-god-code-decomposition -työnkulkua

Tämä dokumentti on ohjenuora sille, miten tekoälyagenttia (Antigravity) ohjeistetaan purkamaan suuria "God Code" -tiedostoja turvallisesti. Tier 3 on nyt **puhdas suunnittelija (God Code Planner)** aivan kuten Tier 1. Se ei kirjoita itse riviäkään koodia, vaan laatii turvallisen, monivaiheisen Strangler Fig -mallin mukaisen suunnitelman ja seurantatiedoston, jota suoritetaan sen jälkeen erillisillä istunnoilla.

Kun käynnistät työnkulun, agentti tulostaa automaattisesti ruudulle ohjeet siitä, mitä se on tekemässä. Varmista aina, että promptistasi löytyvät seuraavat elementit:

## 1. Kohde (Target)
**Tarkka tiedostopolku, jota puretaan.**
Ilman tarkkaa polkua tekoäly saattaa arvailla väärän tiedoston.
*Esimerkki:* `--target="backend_v2/database/repositories/component.py"`

## 2. Älykäs domain-analyysi (Bounded Contexts)
**Mitä asioita tiedostosta halutaan irrottaa.**
Sinun ei tarvitse itse tietää tai luetella domaineita manuaalisesti. Voit antaa tekoälylle vain yhden tiedoston polun ja pyytää sitä *analysoimaan tiedoston* sekä tunnistamaan siitä itsenäiset loogiset kokonaisuudet (Domain-Driven Design). Agentti lukee koodin, tekee kattavan arkkitehtuurikartoituksen ja luo jokaiselle tunnistamalleen domainille oman `phaseX_domain.md` -osasuunnitelman.

## 3. Generoitava Tracker ja Kapulanvaihto (Session Handover)
Koska tekoäly toimii nykyään vain suunnittelijana, se luo aina automaattisesti Markdown-pohjaisen seurantatiedoston (esim. `docs/epic/[tiedostonnimi]_decomposition_tracker.md`). Kun tekoäly ilmoittaa olevansa valmis, se kirjoittaa trackerin loppuun täydellisen `/tier5-resume` -komennon. Tämä komento sisältää parametrit `--achieved`, `--learned` ja `--remaining`, joihin tekoäly on tiivistänyt kaiken oppimansa: mitkä tiedostot puretaan, mitä riippuvuuksia löydettiin, ja mitkä `phaseX_domain.md` -suunnitelmat suoritetaan seuraavaksi. Sinun tarvitsee vain kopioida tämä komento uuteen ikkunaan käynnistääksesi varsinaisen koodauksen (`/tier2-execute` -suorittajalla).

---

### Esimerkki täydellisestä "yhden tiedoston" discovery-promptista:

> `/tier3-god-code-decomposition --target="backend_v2/database/repositories/massive_repo.py". Analysoi tämä God Code -tiedosto huolellisesti ja tunnista siitä itsenäiset loogiset kokonaisuudet (DDD). Toimi God Code Plannerina: laadi jokaiselle tunnistamallesi domainille oma osasuunnitelmansa (purettavaksi siisteihin alihakemistoihin) ja generoi lopuksi docs/epic/massive_repo_decomposition_tracker.md -seurantatiedosto delegointikomennolla.`
