append_text = """
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
"""

with open('c:/src/quorum/docs/AdminStudio_V2_UI_Architecture.md', 'a', encoding='utf-8') as f:
    f.write(append_text)
