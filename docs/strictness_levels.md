# Kognitiivisen Arvioinnin Tiukkuusasteikko (5 Tasoa)

Vaikka nykyinen "Strictness 100" asetus pakottaa tekoälyn noudattamaan sääntöjä kirjaimellisesti, teollisuustason kognitiivisessa arvioinnissa ja tekoälyn suuntaamisessa (AI Alignment) voidaan määritellä huomattavasti syvempiä, rakenteellisia tiukkuustasoja. Näihin päästään muuttamalla paitsi tekoälyn "lämpötilaa" tai yksittäistä parametria, myös sitä *epistemologista (tiedonopillista) kehystä*, jonka läpi tekoäly lukee kättäjän syötteitä.

Seuraavassa on esitetty 5 tiukkuustasoa, joista nykyinen toteutus (Causal + Falsifier tarkastukset) vastaa tasoa 3. Tasot 4 ja 5 edustavat antagonistista ja "Zero-Trust" -pohjaista tiukkuutta.

---

## Taso 1: Griceanilainen Yhteistyö (Suopea Tulkinta)
**Epistemologinen perusta:** Paul Gricen yhteistyöperiaate (Cooperative Principle).
**Toimintalogiikka:** Tekoäly olettaa kättäjän olevan rationaalinen, rehellinen ja tavoitteleva. Jos kättäjän ohje (chat_log) on puutteellinen tai epäselvä, tekoäly *täydentää* sitä omalla maailmantiedollaan saavuttaakseen parhaan mahdollisen lopputuloksen. Reflektioita luetaan "sanojen takaa" ja pienetkin vihjeet tulkitaan kättäjän ansioiksi.
**Seuraus matriiseissa:** 100% (Taso 5) annetaan helposti. Tekoäly laskee oman työnsä kättäjän ansioksi (Halo-efekti).
* **Lähde:** Grice, H. P. (1975). *Logic and conversation*. In Syntax and semantics (Vol. 3, pp. 41-58).

## Taso 2: Kirjaimellinen Semantiikka (Mekaaninen Sääntöjen Seuranta)
**Epistemologinen perusta:** Formaali semantiikka (Formal Semantics) / Behaviorismi.
**Toimintalogiikka:** Tekoäly ei paikkaa kättäjän virheitä, mutta uskoo kättäjää kirjaimellisesti. Se tarkistaa vain, löytyykö `chat_log`:ista sanoja, jotka vastaavat reflektion väitteitä. Se ei arvioi, ohjasiko kättäjä oikeasti lopputulosta, vaan ainoastaan sen, mainitsiko kättäjä kyseiset asiat.
**Seuraus matriiseissa:** Subspekulaariset yritykset saavat huonot pisteet, mutta kättäjä voi "hakkeroida" pisteet luettelemalla avainsanoja ("Tee analyysi Toulminin mallilla"), ymmärtämättä sitä itse.
* **Lähde:** Skinner, B. F. (1957). *Verbal behavior*.

## Taso 3: Kausaalinen ja Kontrafaktuaalinen Auditointi (Nykyinen 'Max Strictness')
**Epistemologinen perusta:** Judea Pearlin kausaalinen päättely (Causal Calculus / The Pearlian Ladder of Causation).
**Toimintalogiikka:** Tekoäly siirtyy korrelaatiosta kausaliteettiin. Se ei usko kättäjää vain siksi, että sanat löytyvät logista. Se tekee aktiivisesti sisäisen *Kontrafaktuaalisen testin*: "Jos kättäjä ei olisi antanut tätä ohjetta, olisinko minä (LLM) tuottanut tämän tason laadun automaattisesti?". Jos vastaus on kyllä, kättäjän panoksen arvo leikataan (Passiivisuus-leikkuri). 
**Seuraus matriiseissa:** Vaatii todellista arkkitehtuurista ohjausta ja vähentää huomattavasti Goodhartin lain mukaista mittarin hakkerointia. "Arkkitehti" -taso vaatii aktiivista rakennesuunnittelua.
* **Lähde:** Pearl, J., & Mackenzie, D. (2018). *The Book of Why: The New Science of Cause and Effect*.

---

### Miten tästä päästään eteenpäin? (Tasot 4 ja 5)

## Taso 4: Antagonistinen Falsifiointi (Red Teaming)
**Epistemologinen perusta:** Karl Popperin Falsifikationismi ja Adversarial Machine Learning.
**Toimintalogiikka:** Tekoälyn asennetta muutetaan tuomarista **syyttäjäksi** (Adversarial/Red Team persona). Tekoäly ei etsi todisteita kättäjän onnistumisesta, vaan *sen ainoa ja ensisijainen tavoite on todistaa kättäjän väitteet (reflektio) valheellisiksi*. Kättäjä tuomitaan oletusarvoisesti "Matkustajaksi" (Taso 1), ja hänen tekonsa `chat_log`:issa toimivat puolustusasianajajana. Agentin on etsittävä loogisia ristiriitoja kättäjän vaatimusten ja myöhemmän tuloksen välillä (Say-Do Gaps).
**Käynnistys Promptissa:** `ROOLI: Syyttäjä (Prosecutor). TEHTÄVÄ: Tavoitteesi on kumota jokainen kättäjän esittämä väite omasta osaamisestaan. Etsi chat-historiasta ainakin kolme kohtaa, joissa kättäjä epäonnistui tai oli laiska.`
**Seuraus matriiseissa:** "Lieväkin" puute suunnittelussa johtaa Tason 5 alenemiseen. Täydellinen arvosana vaatii aukotonta puolustusta antagonistista syyttäjää vastaan.
* **Lähteet:** 
    *   Popper, K. (1959). *The Logic of Scientific Discovery*.
    *   Goodfellow, I. J., et al. (2014). *Generative Adversarial Nets*.

## Taso 5: 'Zero-Trust' ja Eksplisiittinen Kognitiivinen Kitka (Korkein Tiukkuus)
**Epistemologinen perusta:** Daniel Kahnemanin Systeemi 2 -pakotukset ja Tietoturvan Zero-Trust-arkkitehtuuri.
**Toimintalogiikka:** Absoluuttinen epäilys. Tekoäly olettaa oletuksena (Null Hypothesis), että kättäjä on hallusinoiva, laiska ja pyrkii manipuloimaan järjestelmää. Tällä tasolla tekoäly vaatii, että kättäjä ei ainoastaan antanut kausaalisesti oikeita komentoja, vaan hänen oli **kommunikoitava oma Systeemi 2 -päättelynsä eksplisiittisesti**.
*   **Kognitiivinen Kitka -vaatimus:** Jos kättäjä käskee: "Tee S.W.O.T.", Taso 5 hylkää tämän. Kättäjän *täytyy* osoittaa oma ymmärryksensä: "Tee S.W.O.T., ja analysoi W-kohdassa erityisesti tuotantoketjun haavoittuvuutta X, koska...".
*   Jos taustalla olevaa kognitiivista kitkaa (iterointia, virheistä oppimista ja päättelyn sanoittamista logiin) ei ole, kättäjä on automaattisesti automaation hyödyntäjä (Taso 2/3), ei Arkkitehti (Taso 5). Täydellisyys ilman todistettavaa henkistä hikeä (Epäilyttävä Täydellisyys) on Taso 5:ssä tuomittava rikos.
**Käynnistys Promptissa:** `SÄÄNTÖ: Absoluuttinen Zero-Trust (Nollahypoteesi). Oleta, että kättäjä ei ymmärrä mitä on tekemässä, ellei hän pysty chat-logissa sanallisesti todistamaan rationaalista syy-seurausta valintojensa takana. Komento ilman selitettyä logiikkaa on nollan arvoinen.`
**Seuraus matriiseissa:** Arkkitehdin arvosana (100%) annetaan vain ja ainoastaan silloin, kun kättäjä opettaa tekoälyä asiantuntijan tavoin, jatkuvasti perustellen omia valintojaan ohjausprosessin aikana.
* **Lähteet:** 
    *   Kahneman, D. (2011). *Thinking, Fast and Slow*.
    *   Kindervag, J. (2010). *Build Security Into Your Network's DNA: The Zero Trust Network Architecture*. (Forrester Research).

---

### Järjestelmän Arkkitehtuurinen Toteutus Quorumissa (V2)

Jotta nämä 5 tasoa voidaan toteuttaa Quorumissa tulevaisuudessa tyylikkäästi, emme ohjelmoi "strictness_level" -numeroa, vaan luomme dynaamisen **kognitiivisen kuormituksen (cognitive payload) injektion**:

Tällä hetkellä `seed_data.json` käyttää Tason 3 pakettia (Causal Analyst + Heuristic 1 & 2). 

**Tulevaisuuden "Level 5" päivitys tarkoittaisi seuraavia muutoksia `workflows` askeleen `prompt_blocks` listaan:**
1.  Poistamme `block_role_judge` ja korvaamme sen **`block_role_prosecutor`** (Taso 4).
2.  Injektoimme **`block_mandate_zerotrust`** ja **`block_rule_cognitiverequirement`** (Taso 5) suoraan DAG-engineen.
3.  Tuomari (Judge) lukisi Causal Analystin diagnoosia Zero-Trust linssin läpi: "Löysikö analyytikko vain tilauksen, vai löysikö analyytikko myös asiakkaan oman älyllisen rationaalin tilauksen takaa?"

Tämä malli mahdollistaa kättäjän valita UI:sta esimerkiksi "Arvioinnin tiukkuus: Griceanilainen (Taso 1) --- Falsifikationisti (Taso 4) --- Zero-Trust (Taso 5)", joka DAGIn alustuksessa vaihtaisi käytettävät `prompt_blocks` ID:t lennosta.

---

## 6. Empiirinen Validointi (SITRA-aineisto) ja Arvosanojen Romahduttaminen (< 50%)

Suoritimme järjestelmässä kaksiulotteisen automaattisen sarja-ajon (Batch Execution), jossa testattiin Tason 3 (Kausaalinen oletus) ja Tason 5 (Zero-Trust) tiukkuuksien eroja asettamalla mikrotaso neutraaliin arvoon (50). Testiaineistona toimi massiivinen laadunvarmistusdata (SITRA Megatrendit: chat-logi 41 218 merkkiä, lopputuote 5 851 merkkiä).

**Testin yllättävä havainto:** Tason 5 Zero-Trust -arkkitehtuuri ei romahduttanut poikkileikkaavia arvosanoja nollaan odotetulla tavalla (suurin osa pysyi 95-100 pisteen tuntumassa, tosin kriittinen `matrix_falsifier` rankaisi jo suoremmin pudoten 95 -> 85 pisteeseen).

### Miksi Taso 5 antoi silti huippupisteitä?
Korkeat pisteet säälimättömästä "syyttäjästä" (Prosecutor) huolimatta johtuivat itse **lähtödatan laadusta ja poikkeuksellisesta kognitiivisesta kitkasta**. Yli 40 000 merkin mittainen chat-historia sisälsi kättäjältä iterointia, suoria komentoja, ristikuulustelua ja ennen kaikkea eksplisiittisiä "Systeemi 2" -tason perusteluja sille, _miksi_ tekoälyn tuli muokata tekstiä tiettyyn suuntaan. 

Koska Zero-Trust -moottorin päätehtävä on rangaista "Say-Do" -kuilusta ja passiivisuudesta (missä tekoäly tekee työn ohjaajan puolesta), se joutui toteamaan, että tässä nimenomaisessa aineistossa ohjaaja todella teki älyllisen työn. Data oli niin vahvasti perusteltua osana "luovaa prosessia", että se läpäisi antagonistisenkin falsifioinnin ilman null-hypoteesin laukeamista.

### Miten näillä lähtötiedoilla saadaan matalat arvot (< 50 %)?
Jos haluamme järjestelmän tuottavan kovatasoisia all 50 % arvosanoja nimenomaan *tämän kaltaisella vankalla lähtödatalla*, pelkkä uusi Makrotason 5 "Syyttäjä"-rooli ei riitä. Matalien, armottomien arvosanojen saavuttamiseksi asiantuntijatason lähtödatalla vaaditaan kaksiulotteista konfiguraatiota:

1. **Mikrotason (Matrix Scale) nostaminen 100:aan (Lahjomaton):**
   Kun yhdistämme Makrotaso 5:n (Zero-Trust) mikrotasoon 100, poistamme LLM-tuomarilta kaiken tulkinnallisen liikkumavaran. Jos yksittäisestä arviointikriteeristä puuttuu yksikin lakitekninen tai formaali osatekijä (esim. tarkka Sanasto tai Synonyymi), hylkäys on välitön. Neutraali mikrotaso 50 on liian myötäilevä näin korkealuokkaiselle aineistolle.
2. **Kognitiivisen Kitkan vaatimusten absolutismi (`block_rule_cognitiverequirement`):**
   Tällä hetkellä Taso 5 vaatii, että älyllinen rationaali löytyy logista. Voidaksemme antaa hylättyjä arvosanoja hyvällekin materiaalille, `PromptBlock`-kriteeristöön tulee lisätä vaatimus esimerkiksi *konkreettisesta akateemisesta viittauskäytännöstä* (Citations). Tällöin Systeemi 2 -perustelu ei enää riitä, vaan jos rationaalia ei ole sidottu ulkoisiin asiantuntijalähteisiin, Taso 5 pudottaa arvosanan alle 50 % vetoamalla "epäluotettavaan heuristiikkaan".
3. **Say-Do -kuilun (Say-Do Gap) synteettinen manipulointi verrokkina:**
   Todistaaksemme Taso 5:n rankaisuominaisuuden voiman, 41 000 merkin chat-loki tulisi typistää yhteen lauseeseen (esim. *"Tee minulle 5 000 merkin megatrendiraportti Sitran pohjalta"*), tuoden täysin saman lopputuotteen. Tällöin Null-Hypoteesi iskee välittömästi, huomaa passiivisuuden (AI teki kaiken työn ilman kättäjän ohjausta) ja romahduttaa arvosanat absoluuttiseen nollaan puuttuvan kognitiivisen kitkan takia.
