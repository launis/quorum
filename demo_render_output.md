# Epic 12: LLM Prompt Context Demo

## 1. Järjestelmän Säännöt ja Matriisit (SYSTEM PROMPT)
Aito PromptCompiler XML tuotos arviointikriteereistä:

---
<EVALUATION_RUBRICS>
  <MATRIX id="matriisi_1" title="">
  </MATRIX>
</EVALUATION_RUBRICS>

## 2. Injektoidut Datalähteet (USER PROMPT)
Aito PromptCompiler XML tuotos asetetuilla The English-Only Mandate injektioilla:

---
CONTEXT DESCRIPTION FOR <TARGET_REFLECTION_DATA>: [STRICT: ENGLISH ONLY] Analyze the structural logic of the user's explicit written reflections.
<TARGET_REFLECTION_DATA>
# Reflektiodokumentin jäsentely (Reflektiodokumentti.pdf)

_Suunnittelu: Miten aloitit ja miksi?_

Aloitin kyselemään yleisesti, mitä ovat megatrendit. Annoin rajoituksia sekä roolin liiketoiminnalle
koska kyse oli johtoryhmän tehtävästä. Esimerkkejä en antanut. Ennakoin, että alkuun en saa hyvää
tulosta.


_Prosessin ohjaaminen: Miten reagoit ja sopeuduit?_


Pyysin supermegatrendejä – tämä oli iso oivallus. Tekoälyn alkuperäinen vastaus oli liian laaja, joten sitä oli
pakko supistaa ja tuottaa ylätason näkemys. Mietin erilaisia sanoja ja termejä, mutta supermegatrendit tuli
ensimmäisenä mieleeni.
Huomasin myös, että lähtötilanteessaa oli virhe, koska yksi raportti oli annettu kahteen kertaan mutta
tehtävän vaatimaa viimeistä raporttia ei ollut annettu


_Lopputuloksen arviointi: Mitä opit ja mikä oli oma panoksesi?_


Lopputuloksessa muuttelin yksityiskohtia ja otin mielestäni asioita pois, jotka eivät kuuluneet
loppuraporttiin ja muutin myös tulosta. Korjasin taulukosta Eurooppaan liittyvän asian, koska näin
alkupeäisen tarpeettomana.



</TARGET_REFLECTION_DATA>

CONTEXT DESCRIPTION FOR <TARGET_CHAT_DATA>: [STRICT: ENGLISH ONLY] Extract and structure the cognitive patterns exhibited by the user during interactive chat.
<TARGET_CHAT_DATA>
**user**: Miten sitra tämän näkee raporttien perusteella

**ai**: Sitran megatrendiraporttien perusteella näkymä tulevaisuuteen on siirtynyt potentiaalista ja nousevista ilmiöistä (2017) kohti kasautuvia, geopoliittisesti latautuneita kriisejä ja systeemisiä murtumia (2023). Sitra näkee tulevaisuuden "postnormaalina aikana", joka on täynnä yllätyksiä, ristiriitaisuuksia ja konflikteja. Keskeiset megatrendit ja niiden evoluutio Sitran näkökulmasta ovat: Megatrendien Evoluutio Sitran Raporteissa (2017 → 2023) 1. Luonto ja Kestävyys (Ympäristö) 🌍 2017: Painopiste oli ymmärryksen kasvamisessa (ymmärrys maapallon kantokyvystä kasvaa ) ja kestävyyskriisin akuutissa luonteessa (Kestävyyskriisi nyt ). 2023: Käsitys on muuttunut systeemiseksi romahdukseksi (Luonnon kantokyky murenee ). Sitra korostaa, että olemme keskellä ekologista kestävyyskriisiä. Suunta eteenpäin: Pakollinen ekologinen jälleenrakennus on ratkaiseva, siirtymä luonnon tilaa ja ihmisten hyvinvointia parantavaan yhteiskuntaan. 2. Valta ja Geopolitiikka (Poliittinen) ⚖️ 2017: Valta-teemaa lähestyttiin monin eri tavoin, kuten verkoston joukkovoiman (haaste ja mahdollisuus) ja globalisaation vastatrendin (nationalismi) kautta. 2023: Valta on kärjistynyt suoraksi konfliktiksi (Demokratian kamppailu kovenee ). Geopoliittinen valtataistelu on tullut "ryminällä takaisin", sääntöpohjainen maailmanjärjestys horjuu, ja luottamus rapautuu informaatiovaikuttamisen takia. Suunta eteenpäin: Vahvistamalla demokratiaa lisäämällä osallisuutta ja vaikuttavuutta, sekä luomalla vahvaa luottamusta. 3. Teknologia ja Digivalta 💻 2017: Teknologia oli ensisijaisesti potentiaalin lähde (Superälykkyys ovella, Data on valtaa ja vaurautta ), joka sulautui kaikkeen. 2023: Teknologia on muuttunut geopoliittiseksi kilpailuasetelmaksi (Kilpailu digivallasta kiihtyy ). Kiistellään digimaailman säännöistä, uusien teknologioiden vaatimista resursseista ja teknologiajättien ylivallasta. Suunta eteenpäin: Edistämällä reilua digimaailmaa luomalla datatalouden pelisäännöt, jossa yksilöiden, yritysten ja yhteiskunnan edut ovat tasapainossa. 4. Talous ja Eriarvoisuus (Taloudellinen) 📈 2017: Keskityttiin työn murrokseen ja siihen, että eriarvoisuus on polttava kysymys. 2023: Kriisit ovat johtaneet siihen, että Talouden perusta rakoilee. Globaali eriarvoisuus kasvaa, ja luonnon palveluiden romahdus murentaa talouden edellytyksiä. Suunta eteenpäin: Uudistetaan talous korjaavaksi ja uusintavaksi taloudeksi, joka noudattaa kestävän ja vastuullisen kehityksen periaatteita. 5. Ihmiset ja Hyvinvointi (Sosiaalinen) 🧑‍🤝‍🧑 2017: Terveys oli valtava trendi ja bisnes. Puhuttiin elinikäisestä pitenemisestä ja eriarvoisuuden korostumisesta terveydessä. 2023: Fokus on siirtynyt terveydestä kasvaviin hyvinvoinnin haasteisiin. Väestön ikääntymisen ja monimuotoistumisen lisäksi korostuu mielenterveysongelmien lisääntyminen tulevaisuutta koskevan epävarmuuden vuoksi. Suunta eteenpäin: Tavoitellaan kokonaisvaltaista hyvinvointia, jossa ihmisten terveys nähdään kytkeytyneenä luonnon terveyteen. Sitran keskeinen viesti on, että vaikka haasteet ovat suuria ja kietoutuvat yhteen, toisenlainen, reilu ja kestävä tulevaisuus on mahdollinen. Tämä edellyttää tulevaisuusajattelua ja muutoskykyä.

**user**: mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila

**ai**: Sitran näkemys suunnasta eteenpäin, sen sijaan että se olisi pelkkä toivetila, korostaa samanaikaista sopeutumista ja uudistumista postnormaalissa, yllätysten täyttämässä ajassa. Sitra näkee tulevaisuuden rakentuvan nykyhetkessä tehdyillä päätöksillä ja valinnoilla kriisien keskellä, mutta korostaa, että paluuta vanhaan normaaliin ei ole. Suunta eteenpäin on Sitran mukaan transformatiivinen ja edellyttää muutoskykyä (resilienssiä) ja tulevaisuusajattelua. 1. Ekologisen Kriisin Edellyttämä Sopeutuminen ja Jälleenrakennus Sitran mukaan Suunta eteenpäin on sopeuduttava maapallon kantokyvyn rajoihin, mikä on kaiken keskiössä. Sopeutuminen: On pakko sopeutua siihen, mikä on jo muuttunut (esim. ilmaston kuumeneminen, luontokato). Uudistuminen: Tulevaisuuteen on satsattava yhteiskunnan ja arjen ekologisella jälleenrakennuksella. Tämä tarkoittaa siirtymistä luonnon tilaa ja ihmisten hyvinvointia parantavaan yhteiskuntaan. Käytäntö: Muutos näkyy kiertotalouden valtavirtaistumisena, kulutuksen vähentämisenä ja siirtymänä kasvipohjaiseen ruokavalioon ja uusiutuvaan energiaan. 2. Systeeminen Uudistuminen Viiden Megatrendin Mukaan Sitran näkemä suunta ei ole ennalta määrätty, mutta se edellyttää määrätietoisia toimia viiden teeman osalta, kääntämällä megatrendien asettamat haasteet mahdollisuuksiksi. Sitra näkee, että tulevaisuus ei vain "vyöry päälle", vaan jokaisella on vastuu ajatella pidempää aikaväliä ja rakentaa parempaa tulevaisuutta.

**user**: koosta näistä vastauksista 1 sivun raportti

**ai**: Analyysi Sitran Megatrendien Evoluutiosta (2017 → 2023)

... [TRUNCATED FOR DEMO] ...
</TARGET_CHAT_DATA>

CRITICAL MANDATE: You must process the input and generate all your output text, reasoning, and source justifications exclusively in the 'fi' language, regardless of the language used in the instructions or source materials.