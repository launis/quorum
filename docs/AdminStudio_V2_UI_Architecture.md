# Admin Studio V2: Adaptive UI & Navigation Architecture

**PROJECT**: Cognitive Quorum V2 Platform
**STATUS**: Mandatory Architecture Law for Web/Desktop/Mobile clients.
**REFERENCE**: Based on Flutter `Adaptive-Responsive` best practices (https://docs.flutter.dev/ui/adaptive-responsive/best-practices).

---

## 1. THE PROBLEM: FRAGMENTATION & DEEP SILOS
Käyttöliittymä (Admin Studio / Suoritusten Hallintapaneeli) on historiansa aikana siiloutunut ja rakentunut orgaanisesti vailla keskitettyä navigaatiostandardia:
* Joillakin sivuilla käytetään yläpalkkia (`TabBar`: Työnkulut, PromptBlockit).
* Toisilla sivuilla käytetään vasenta sivupalkkia (`NavigationRail`: Etusivu, Uusi analyysi).
* Globaaliin konfiguraatioon liittyvät raskaat työkalut, kuten **Blueprint Editor**, on haudattu liian syvälle yksittäisten alasivujen taakse (liian syvällinen arkkitehtuuri).
* Tuleva **Organisaatiot**-moduuli (Tenant Isolation) vaatii jatkuvasti näkyvän tilan, ja sen varjelu vanhassa sekavassa reitityksessä olisi mahdotonta.

Tämä säännöstö **tuhoaa** tämän sekavan, monitasoisen navigaation ja pakottaa modernin, litteän `Adaptive-Responsive` -standardin koko projektiin.

---

## 2. THE OMNI-NAVIGATION MANDATE (FLAT HIERARCHY)
Päänavigaatio ei saa koskaan jakautua useaan paikkaan (Sekä AppBar/TabBar että Sidebar). Kaikki järjestelmän ylätason Pääkomponentit on nostettava kertaheitolla **yhdelle tasaiselle hierarkiatasolle (Flat Hierarchy)**.

* **BANNED**: Yläpalkin välilehdet (`TabBar` tai `AppBar` title-menut) **globaalissa navigaatiossa**.
* **MANDATORY**: Koko sovellusta ohjaa tasan yksi käyttöliittymäkomponentti, joka mukautuu näytön kokoon (Omni-Navigation).

### 2.1 Uusi Päänavigaatiorakenne (1-Click Pääsy)
Navigaatiopalkin elementit, ylhäältä alas:
1. **Hallintapaneeli** (Suoritukset, Etusivu)
2. **Työnkulut** (Workflow DAG -hallinta)
3. **Blueprint Editori** (Nostettu ylätasolle! Blueprinttejä luodaan itsenäisesti ylätasolla, ja vasta myöhemmin liitetään Työnkulkuihin valintalistasta)
4. **Rakennuspalikat** (PromptBlockit, Mallirekisteri, Steps - *Nämä voidaan tarvittaessa ryhmitellä yhden avattavan menun alle NavigationRailissa jos pystytila loppuu*)
5. **Organisaatiot** (Uusi moduuli: Käyttäjien, roolien ja lisensoinnin hallinta)
6. **Asetukset** (Sovellustason ja ylläpidon konfiguraatiot)

---

## 3. ADAPTIVE BREAKPOINTS & ROUTING RULES
Noudatamme täsmällisiä Flutter-suosituksia näytön fyysisen leveyden suhteen (`LayoutBuilder`, `MediaQuery`):

* **< 600dp (Mobile View):** 
  * Käytetään yksinomaan `NavigationBar` (Bottom nav). 
  * Yläpalkissa (`AppBar`) on vain nykyisen näkymän tekstiotsikko ja spesifisesti kyseisen näkymän konteksti-toiminnot (esim. Tallenna/Julkaise -napit).
* **>= 600dp (Tablet/Desktop View):** 
  * Käytetään yksinomaan `NavigationRail` (Left nav). 
  * Näytön ollessa erittäin leveä (>1200dp), Rail voi vaihtua `extended = true` tilaan, jolloin ikonien vieressä näkyvät tekstit.

**Routing Mandaatti (`StatefulShellRoute`):**
Jotta päävälilehtien välillä siirtyminen (esim. Hallintapaneelista Blueprintteihin ja takaisin) ei hävitä keskeneräistä työtä, GoRouter on **pakotettu** rakentamaan tilaan perustuva `StatefulShellRoute`. Tämä säilyttää jokaisen välilehden oman navigointipinon ja ramin (Scroll position, syotetyt kentät).

---

## 4. THE WORKSPACE CONTEXT (ORGANISAATIOT)
Organisaatiot-päivityksen myötä lähes kaikki backendin työnkulut, promptblockit ja blueprintit on luvitettu (`tenant_id`). Käyttäjän on siksi pystyttävä hetkessä hahmottamaan, missä tilassa hän on.

* **Sijainti:** Ylänavigaatiossa tai vasemman `NavigationRail`:n ehdottomassa huipussa tulee olla **Workspace Switcher** (esim. "Aktiivinen: Sitra").
* **Mutaatio:** Kun Workspacea vaihdetaan pudotusvalikosta, päivittyy globaali Riverpod-tila (`selectedOrganizationProvider`), joka automaattisesti invalidoi (`ref.invalidate()`) kaikki tilatut listaukset. Järjestelmä hakee vain kyseisen organisaation sisällön lennosta muistiin eristäen tenant-tiedot dynaamisesti toisistaan.

---

## 5. TABBAR SALLITUT KÄYTTÖTAPAUKSET
Jos `TabBar` on kielletty ylätasolla, saako sitä yhä käyttää? Kyllä, mutta **vain yksittäisen entiteetin sisäisessä asioinnissa**.

**Esimerkki sallitusta käytöstä:**
Käyttäjä klikkaa "Työnkulut" (joka näkyy listana). Hän avaa Työnkulun "Riskianalyysi V2" editoitavaksi. Avautuvassa koko ruudun editorissa **saa** olla `TabBar`:
* Välilehti 1: Yleiset (Nimi, Kuvaus, Tagit)
* Välilehti 2: Vaiheet (Graafinen DAG, Noodit)
* Välilehti 3: Käyttöoikeudet

Välilehdet rajoittuvat puhtaasti "Riskianalyysi V2" olion skooppiin. Ne eivät koskaan navigoi pois kyseisestä entiteetistä muihin järjestelmän pääosiin.

## 6. RELATIONAL INTEGRITY (NO FREE-TEXT KEYS)

Kaikki käyttöliittymän syötteet (Inputs), jotka määrittelevät **relaation, riippuvuuden tai järjestelmätason tunnisteen** kahden entiteetin välillä, on EHDOTTOMASTI toteutettava pudotusvalikoilla (Dropdown/Select, Autocomplete tai Checkbox). Vapaa tekstinsyöttö (TextField) on kielletty näissä yhteyksissä. Tämä estää inhimilliset kirjoitusvirheet ja datan pirstaloitumisen.

### 6.1 Esimerkki: Odotetut Syötteet (Globaalit Roolit)
Kuvitellaan näkymä, jossa vapaalla tekstillä määritellään työnkulun "Odotetut Syötteet" (esim. `product_text` tai `analysis_target`). 
* **BANNED (Nykyinen huono UX):** Käyttäjä voi vapaasti kirjoittaa tekstikenttään omien muistikuvien mukaan sanan `product_text`. Yksi käyttäjä kirjoittaa `product_text`, toinen `product-text`, kolmas `ProductText`. Työnkulku hajoaa backendissä riippuvuuksien katketessa. Tämä virhe ei ole staattisesti kiinniotettavissa.
* **MANDATORY (V2 UX):** Kenttä on pudotusvalikko (Dropdown), joka latautuu suoraan backendin ohjastetusta sanastosta (Controlled Vocabulary / Enum). Käyttäjä voi ainoastaan **valita** listalta valmiin ja tuetun arvon `product_text`.

### 6.2 Laajennettu Soveltamisala
Tämä sääntö laajentaa Opaque ID -suunnitelman (`Arkkitehtuurimäärittely_Opaque_ID_Sijoittelu_UX.md`) abstraktiovaatimuksen **kaikkiin ihmisluettaviin semanttisiin avaimiin**, jotka sitovat taustajärjestelmän osia toisiinsa UX-kerroksessa:
1. **Globaalit Syöteroolit / Avaimet** (esim. kytkökset työnkulun lähteisiin ja PromptBlock-syötteisiin)
2. **Kategoriat ja Tyyppimäärittelyt** (Hoidetaan tiukasti kooditason Enum-listojen läpi, ei string-teksteinä)
3. **Graafiset Kytkökset ja Mappausavaimet**

**Sanastokirjasto (Vocabulary Control):** Jos järjestelmään tarvitaan uusi syöterooli (esim. `custom_payload`), se on rekisteröitävä keskitetysti järjestelmän sanastokirjastoon (Asetuksissa tai Admin-työkalujen juurikansiossa) erillisenä, validona entiteettinä. Sen jälkeen arvo on automaattisesti pudotusvalikoissa ehyenä, valittavana avaimena kaikkialla askeleita mallinnettaessa. Vapaata kenttää ei salita järjestelmälogiikan rakentamisessa missään tilanteessa.
