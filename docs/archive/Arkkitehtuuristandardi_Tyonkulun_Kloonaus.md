# ARKKITEHTUURISTANDARDI: Työnkulun Kloonaus ja Riippuvuuksien Hallinta (V2)

Tämä dokumentti määrittelee Quorum V2 -arkkitehtuurin virallisen toimintatavan ja algoritmin työnkulkujen (Workflows) turvalliselle kopioinnille (kloonaukselle). Ohjeistus yhdistää teknisen toteutussuunnitelman, rakenteellisen turvallisuusvaatimuksen sekä riskianalyysin, jotta käyttöliittymäkehitys (Flutter) ja suoritusmoottori (DAG Executor) pysyvät ehdottoman synkroonissa.

## 1. Ydinongelma: Yksilölliset Tunnisteet ja Verkostorakenne

Quorum V2 nojaa täysin Suunnattuun Syklittömään Verkkoon (Directed Acyclic Graph, DAG). Työnkulun sisällä olevat askeleet (StepRules) eivät tunne toisiaan nimeltä, vaan ne on kytketty toisiinsa yksilöllisillä ja kryptografisesti vahvoilla tunnisteilla (esim. `steprule_d90f30d31b894ba2ba12507370eedb46`).

**Kloonauksen haaste:** 
Jos Pääkäyttäjä kopioi "Kokonaisvaltainen Auditointi" -työnkulun tallentaen rakenteen sellaisenaan, molemmissa työnkuluissa on askeleita täysin samoilla tunnisteilla. Koska suoritusmoottori edellyttää askeleilta yksilöllisyyttä (Opaque ID), tämä johtaisi rakenteelliseen umpikujaan. Siksi kloonaus edellyttää prosessia, jossa jokainen solmu (askel) ja siihen johtava suhde (riippuvuus) luodaan ja reititetään uudelleen.

---

## 2. Virallinen Kloonausalgoritmi (Kartoitus ja Reititys)

Kloonaus on kaksi vaiheinen operaatio, joka suoritetaan käyttöliittymän muistissa (Flutter/Riverpod) ennen uuden rakenteen tallentamista tietokantaan.

### Vaihe A: Tunnisteiden Kartoitus (Sanakirjan Luonti)
Kun käyttäjä käynnistää kopioinnin, ohjelma iteroi alkuperäisen työnkulun kaikki askeleet.
1. Ohjelma luo tyhjän väliaikaisen sanakirjan (Key-Value Map).
2. Se generoi jokaiselle askeleelle uuden ja täysin satunnaisen tunnisteen (Opaque ID).
3. Se tallentaa sanakirjaan tiedon: `vanha_tunniste` -> `uusi_tunniste`.
4. Päivittää itse askeleelle uuden tunnisteen säilyttäen muun datan ennallaan.

Tämän vaiheen jälkeen solmut ovat uniikkeja, mutta niiden sisäiset riippuvuudet osoittavat yhä alkuperäisiin, vanhoihin tunnisteisiin.

### Vaihe B: Uudelleenreititys (Riippuvuuksien ja Polkujen Korjaus)
Ohjelma käy uuden askeleen listan läpi uudelleen, ja korjaa askeleiden väliset kytkökset nojaten aiemmin luotuun sanakirjaan.
1. **Riippuvuudet (DAG-reunat):** Askeleen odotuslista (`depends_on`) käydään läpi. Jos listalla on sanakirjasta löytyvä vanha tunniste, se korvataan uudella.
2. **Syötemappaukset (Input Mappings):** Jos ohjelma asettaa tuloksia muiden askeleiden syötteiksi (esim. tiedostaen, mistä edellisen askeleen tuloksesta algoritmi jatkaa), ohjelma purkaa viittauspolun huolellisesti ja korvaa vanhan kohdetunnisteen uudella.
3. **Tulosten Visualisointi (Blueprint Editor):** Lopuksi ohjelma purkaa työnkulun sisäisen tulosnäkymän määrittelyn (`render_blueprint`) ja korvaa kaikki datan piirtämistä ohjaavat tunnisteet uusilla.

Näiden kahden vaiheen jälkeen verkko (DAG) on rakenteellisesti itsenäinen, täydellisesti eristetty alkuperäisestä työnkulusta ja valmis tallennettavaksi tietokantaan.

---

## 3. Riskianalyysi ja Lievennysmekanismit

Vaikka reititysalgoritmi on teoriassa aukoton, sen ohjelmalliseen toteutukseen käyttöliittymäkerroksessa (Flutter/Dart) kohdistuu ankara laatuvaatimus.

### Riski 1: Kaksinkertainen Korvausvirhe (Iteraatio-Vika)
Jos ohjelma korvaa merkkijonoja huolimattomasti koko tekstimuotoisen datajoukon läpi (ns. globaali replace-toiminto), se altistuu ketjureaktiolle. Jos esimerkiksi tunniste A vaihtuu tunnisteeksi B, ja myöhemmin koodi vaihtaa olemassa olevat B-tunnisteet tunnisteeksi C, alkuperäinen askeleen A tunniste muuttuu vahingossa muotoon C. 

**Pakotettu Ratkaisu:** Quorum V2 käyttää 128-bittisiä askeleiden tunnisteita, jotka eliminoivat yhteentörmäyksen riskin. Tästä huolimatta käyttöliittymän ohjelmoijan on toteutettava uudelleenreititys ehdottoman rakenteellisella JSON-solmujen läpikäymisellä (Node Iteration). Laajoja ja sokkoja merkkijonokorvauksia ei sallita.

### Riski 2: Piilevä Muutettavuus (Jaettu Vastuullisuus)
Kloonaus säilyttää askeleiden viittaukset alkuperäisiin tekoälyn kehotteisiin ja malleihin (`task_blueprint`). Jos Pääkäyttäjä editoi uuden, juuri kopioidun työnkulun sisällä olevaa mallia (esim. askeleen "Profiler" tulkintasääntöjä), tämä muutos vaikuttaa automaattisesti myös alkuperäiseen työnkulkuun josta se kopioitiin, koska ne jakavat saman malliohjauksen.

**Pakotettu Ratkaisu:** Käyttöliittymään on rakennettava Pääkäyttäjälle selkeä visuaalinen varoitusjärjestelmä: *”Huomio: Muokkaat jaettua mallia. Nämä muutokset vaikuttavat kaikkiin työnkulkuihin, jotka käyttävät tätä mallia.”* Tulevaisuudessa arkkitehtuuri voi mahdollistaa edistyneemmän haaroittumisen (Branching), jossa myös taustalla olevat tekoälymallit kopioidaan erillisiksi instansseiksi.

### Riski 3: Katkenneet Viittaukset (Rikkoutunut Rakenne)
Jos alkuperäisessä työnkulussa on inhimillinen tai tekninen vika – esimerkiksi askeleen riippuvuus osoittaa sellaiseen tunnisteeseen, jota ei löydy iteroitavien askeleiden listalta – sanakirja-algoritmi jättää tämän virheellisen viittauksen voimaan uuteen työnkulkuun. Kun suoritusmoottori myöhemmin yrittää ajaa kloonatun työnkulun, suoritus kaatuu heti, koska määritettyä askelta ei löydy.

**Pakotettu Ratkaisu:** Järjestelmä operoi The Fail Fast -standardin mukaisesti. Ennen uuden työnkulun tallennusta tietokantaan, käyttöliittymän (Dart) on validoitava koko juuri kloonattu verkko. Jos yksikään sanakirja-päivitys epäonnistuu kohdeviittauksen puuttumisen vuoksi, koko kopiointioperaatio evätään ja käyttäjälle näytetään punainen virheikkuna, joka estää viallisen datan tallentumisen. 

---

## Yhteenveto

**Toimiiko tämä suoritusten (ajojen) kannalta luotettavasti?** 
Kyllä, täydellisesti. Kun yllä kuvatut "Fail Fast" -validointisäännöt toteutetaan käyttöliittymätasolla, raskaasti työllistetty taustajärjestelmä (Suoritusmoottori) ei huomaa mitään eroa käsin rakennetun tai kopioidun työnkulun välillä. Suoritusmoottori hakee Pydantic-turvalliset ohjeet ja tekoäly-logiikan yhdistetyn jaetun malliston kautta (`task_blueprint`), ja tulos on yhtä laadukas kuin alkuperäisessä suorituksessa. Tämän ratkaisun ansiosta riippuvuudet ovat eheitä, ohjausmalleja voidaan päivittää keskitetysti, ja monimutkaisia työnkulkuja voidaan kokeilla nopeasti uusilla parametreilla pelkän kopiointipainikkeen avulla.
