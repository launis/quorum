# **Holistinen Mestaruus: Viitekehys tekoälyosaamisen arviointiin**

## **Abstrakti**

Globaalit tietotyömarkkinat ovat keskellä historiansa merkittävintä rakennemuutosta (vrt. Acemoglu & Restrepo 2018). Muutosta vauhdittaa generatiivisen tekoälyn (GenAI) ja suurten kielimallien (LLM) eksponentiaalinen kehitys. Kyseessä ei ole pelkkä teknologinen päivitys, vaan yleiskäyttöisen teknologian (General Purpose Technology, GPT) aiheuttama shokki, joka muokkaa uudelleen työn taloudellisen arvonluonnin perusteita (Eloundou ym. 2023).

Tekoälyn syvällinen ja kiihtyvä integroituminen työelämään on asettanut organisaatiot perustavanlaatuisen haasteen eteen: ne kohtaavat mittaamisen kriisin, jossa perinteiset keinot eivät enää riitä todentamaan luotettavasti korkean tason tekoälyosaamisen arvoa (vrt. Auzmor 2024; ISACA 2025; Disco 2024). Tämä kriisi ei ole vain tekninen, vaan se koskettaa syvällisesti inhimillisen pääoman arvottamista tilanteessa, jossa koneiden kyvykkyydet kehittyvät eksponentiaalisesti. Perinteiset arviointimenetelmät eivät kykene ratkaisemaan psykometriikan perustavanlaatuista reliabiliteetin ja validiteetin paradoksia (vrt. Borsboom ym. 2004). Tämä paradoksi korostuu entisestään generatiivisen tekoälyn yhteydessä, jossa oikeita vastauksia voi olla ääretön määrä ja prosessin laatu ratkaisee tuloksen arvon.

Standardoidut testit ovat usein psykometrisesti luotettavia mutta sisällöllisesti kapea-alaisia (Wiggins 1998). Laadulliset menetelmät ovat puolestaan valideja, mutta kärsivät usein heikosta reliabiliteetista ja subjektiivisuudesta (Koretz ym. 1994). Tässä artikkelissa esitellään *hybridirubriikki*, uusi kaksitasoinen teoreettinen viitekehys, joka on suunniteltu hallitsemaan tätä jännitettä. Viitekehyksen analyyttinen taso perustuu BARS-asteikkoon (*Behaviorally Anchored Rating Scales*), Bloomin taksonomiaan ja Toulminin argumentaatiomalliin, ja se pyrkii maksimoimaan luotettavuutta standardoimalla arviointiprosessia. Sitä täydentävä holistinen taso hyödyntää vastakkainasetteluun perustuvaa (adversariaalista) agenttien välistä debattia (vrt. Du ym. 2023\) ja pyrkii maksimoimaan validiteetin tunnistamalla sääntöjä ylittävän, kontekstisidonnaisen asiantuntijuuden.

Viitekehyksen operatiivinen malli on ”Kognitiivinen Kvoorum”, moniagenttijärjestelmä (MAS), joka toteuttaa tämän kaksitasoisen arvioinnin hyödyntämällä koneoppimisen koosteoppimisen (engl. ensemble learning) periaatteita (vrt. Sagi & Rokach 2018). Malli on tässä jäsennelty yksityiskohtaiseksi, vaiheittaiseksi prosessikuvaukseksi. Daniel Kahnemanin esittämä kaksoisprosessiteoria (Järjestelmä 1 ja Järjestelmä 2; vrt. Kahneman 2011\) ohjaa viitekehyksen strategista kehitystä ja luo vision skaalautuvasta, mutta samalla syvällisesti auditoitavasta arviointijärjestelmästä. Vaikka viitekehyksen prototyyppi on teknisesti toteutettu, siltä puuttuu toistaiseksi empiirinen validointi. Viitekehys pysyy puhtaasti teoreettisena konstruktiona, kunnes sen keskeinen hypoteesi – jonka mukaan on mahdollista saavuttaa korkea arvioitsijoiden välinen reliabiliteetti monimutkaisessa laadullisessa arvioinnissa – todennetaan muodollisessa pilottitutkimuksessa. Tämä työ tarjoaa metodologisen avauksen korkean panoksen osaamisen arviointiin tekoälyn aikakaudella.

## **Luku 1: Strateginen haaste ja metodologinen perusta**

Tämä luku perustelee, miksi tekoälyosaamisen luotettava mittaaminen on kriittinen strateginen haaste, ja esittelee viitekehyksen metodologisen perustan. Luvussa kuvataan ensin, miten tekoäly aiheuttaa globaalin taitomurroksen ja millaisen haasteen se luo osaamisen todentamiselle. Tämän jälkeen syvennytään psykometriikan perustavanlaatuiseen reliabiliteetin ja validiteetin paradoksiin, joka on perinteisten arviointimallien ydinongelma. Lopuksi luvussa eritellään keskeisten teorioiden tunnetut rajoitukset, jotka uuden ratkaisun on hallittava.

### **1.1 Strateginen konteksti: Tekoäly ja taitomurros**

Tekoälyn integroituminen liiketoimintaprosesseihin on käynnistänyt perustavanlaatuisen taitomurroksen, joka vaikutuksiltaan vertautuu teolliseen vallankumoukseen (Acemoglu & Restrepo 2018; Eloundou ym. 2023). Muutos ei ole vain teknologinen, vaan se muokkaa uudelleen työn taloudellista arvonluontia. Erityisesti suurten kielimallien (LLM) on arvioitu vaikuttavan merkittävästi jopa 80 prosenttiin Yhdysvaltain työvoimasta, kohdistuen nimenomaan korkeaa koulutusta vaativiin asiantuntijatehtäviin (Eloundou ym. 2023). Tutkimus osoittaa, että vähintään 50 % työtehtävistä saattaa muuttua tekoälyn vaikutuksesta noin 19 %:lla työntekijöistä, mikä viittaa siihen, että kyseessä on yleiskäyttöinen teknologia (General Purpose Technology, GPT), jonka vaikutukset läpäisevät kaikki toimialat ja palkkaluokat. Toimialakohtaiset analyysit viittaavat nopeaan ja laaja-alaiseen muutokseen. Esimerkiksi McKinsey Global Instituten ennusteen mukaan merkittävä osa työntekijöiden keskeisistä taidoista muuttuu lähivuosina, ja jopa 30 % nykyisistä työtunneista voitaisiin automatisoida samana ajanjaksona (Hazan ym. 2024\)**.** Tämän kehityksen seurauksena arvonluonnin perusta siirtyy rutiinitehtävistä korkeamman tason kognitiivisiin kykyihin, kuten monimutkaiseen ongelmanratkaisuun, kriittiseen ajatteluun ja strategiseen vuorovaikutukseen (OECD 2024).

Kun tekoälyn kyky tuottaa ennusteita ja sisältöä yleistyy ja on laajasti saatavilla, ihmisen arvonluonnin ytimeen nousevat arviointi- ja harkintakyky sekä näiden taitojen hyödyntäminen päätöksentekojärjestelmien strategisessa uudelleensuunnittelussa (Agrawal ym. 2022). Nämä eivät ole pelkästään yleisiä työelämätaitoja, vaan keskeisiä taloudellisia kyvykkyyksiä, joiden arvo perustuu siihen, että ne täydentävät ja ohjaavat tekoälyn tuottamaa ennustekykyä (vrt. Agrawal ym. 2022).

Kun tekoäly painaa tietotuotannon hinnan lähelle nollaa, sitä täydentävien tekijöiden – kuten datan, arvioinnin ja toiminnan – arvo nousee. Näihin kyvykkyyksiin lukeutuvat esimerkiksi kriittinen validointi, luova synteesi ja eettinen harkinta, jotka kaikki edellyttävät kykyä arvioida ja ohjata tekoälyn tuottamaa informaatiota (OECD 2024).

Tekoälylukutaidosta on muodostumassa keskeinen strateginen prioriteetti. Erityisesti kehotesuunnittelua (engl. *prompt engineering*) on ehdotettu uudeksi perustaidoksi (Federiakin ym. 2024), mutta uusin tutkimus peräänkuuluttaa laaja-alaisempia "Meta AI" \-taitoja, jotka yhdistävät teknisen käytön kriittiseen epistemologiseen arviointiin (Ahuna & Kiener 2025). Laajemmin kykyä työskennellä tekoälyn kanssa pidetään yhtenä nopeimmin kasvavista osaamistarpeista globaaleilla työmarkkinoilla (World Economic Forum 2023). Laajemmin augmentaatiokyvyllä (engl. *augmentation capability*) tarkoitetaan kykyä hyödyntää tekoälyä oman suorituskyvyn ja ajattelun laadun parantamiseksi. Tällä kyvykkyydellä on konkreettinen taloudellinen arvo työmarkkinoilla (vrt. Fügener ym. 2025). Työmarkkinat reagoivat muutokseen nopeasti, ja tekoälytaitoja vaativista rooleista maksetaan jo nyt korkeampaa palkkaa (PwC 2024). Tämä osoittaa, että kyseessä ei ole tulevaisuuden visio, vaan nykyhetken taloudellinen realiteetti, joka asettaa organisaatioille paineen tunnistaa, mitata ja kehittää näitä uusia taitoja.

Tämä osaamisvaade on vahvistettu Euroopan unionin tasolla. Tekoälysäädös asettaa artiklassa 4 tekoälyjärjestelmien tarjoajille ja käyttöönottajille nimenomaisen velvoitteen ryhtyä toimenpiteisiin henkilöstönsä tekoälylukutaidon varmistamiseksi (Euroopan parlamentin ja neuvoston asetus (EU) 2024/1689). Tämä muuttaa tekoälyosaamisen arvioinnin kilpailuedusta lakisääteiseksi velvollisuudeksi, mikä edellyttää organisaatioilta luotettavia menetelmiä osaamistason todentamiseksi.

Uusimman sukupolven kielimallien ja niiden kehittyneiden päättelykykyjen myötä tämä tilanne muuttuu teoreettisesta mallista strategisesti merkittäväksi voimavaraksi. Nyt on otollinen hetki hyödyntää sitä, sillä teknologinen kehitys on saavuttanut pisteen, jossa korkeatasoisen arvioinnin vaatima metakognitiivinen arkkitehtuuri on toteutettavissa täysimääräisesti. Konkreettisena esimerkkinä tästä murroksesta ovat OpenAI:n o1-mallisarja (OpenAI 2024\) ja Googlen Gemini 3.0 (Google DeepMind 2025c). Ne edustavat arkkitehtonista siirtymää nopeasta hahmontunnistuksesta hitaaseen ja harkitsevaan päättelyyn (vrt. Google DeepMind 2025a; Google DeepMind 2025b).

Muutos on ajankohtainen, sillä aiemmat mallit epäonnistuivat systemaattisesti monimutkaisten ohjeiden noudattamisessa (Wu ym. 2024\) ja toimivat luonteeltaan todennäköisyyslaskentaan perustuvina ennustemalleina, jotka eivät kyenneet muodolliseen kausaaliseen päättelyyn (Chi ym. 2024). Tämä jätti arvioinnin alttiiksi pinnalliselle jäljittelylle ja hallusinaatioille, jotka ovat tunnettu riski kielimallien luotettavuudelle (Huang ym. 2023). Tämän uuden mahdollisuuden taustalla on tekninen siirtymä pelkästä tilastollisesta hahmontunnistuksesta kohti ”Deep Think” \-arkkitehtuureja. Nämä hyödyntävät pidennettyä päättelyaikaa (engl. *inference-time compute*). Arkkitehtuurit on koulutettu vahvistusoppimisen avulla generoimaan sisäisiä, iteratiivisia ajatusketjuja (Chain-of-Thought). Tavoitteena on tunnistaa ja korjata virheet ennen lopullisen vastauksen tuottamista (Google DeepMind 2025a; Google DeepMind 2025b).

Tässä artikkelissa esiteltävä moniagenttijärjestelmä valjastaa nyt näiden uusien mallien hitaan ja pohtivan prosessoinnin tuottamaan aitoa, Kahnemanin (2011) kuvaamaa ”Järjestelmä 2” \-tason analyysia. Tämä toteutetaan toiminnallisesti pakottamalla agentit käyttämään sisäisiä päättelytiloja (esim. scratchpad tai Chain-of-Thought) monimutkaisissa analyysitehtävissä. Tämä mahdollistaa sen, mikä aiemmin oli haastavaa: uskottavamman falsifioinnin ja syvällisten loogisten virheiden tunnistamisen. On kuitenkin huomattava, että nykyiset mallit suorittavat kausaalista päättelyä (L3) ensisijaisesti kielellisinä approksimaatioina eivätkä muodollisina matemaattisina todistuksina (Chi ym. 2024), mikä huomioidaan viitekehyksen heuristisessa luonteessa. Viitekehys hyödyntää tätä uutta kapasiteettia ratkaistakseen arvioinnin reliabiliteetin ja validiteetin välisen paradoksin (Borsboom ym. 2004\) ja tarjoaa keinon tunnistaa luotettavasti sekä sääntöjä noudattavan rutiiniosaamisen että säännöt ylittävän, kontekstisidonnaisen mestaruuden (Dreyfus & Dreyfus 1980\)**.**

### **1.2 Ydinongelma: "Mittaamisen kriisi" ja itsearvioinnin haaste**

Tämä taitomurros on synnyttänyt organisaatioille keskeisen strategisen haasteen, ”mittaamisen kriisin”. Kyseessä on ilmiö, joka on tunnistettu laajalti myös kognitiivisten kykyjen ja tekoälyn arvioinnin yhteydessä (vrt. Silva ym. 2025; Cheng 2021). Kriisi ilmentää perustavanlaatuista vaikeutta todentaa tekoälyinvestointien ja \-osaamisen todellista arvoa. 

Vaikka organisaatiot investoivat teknologiaan merkittävästi, ilman luotettavia mittareita investointien tuotto (ROI) ja vaikutus strategisiin kyvykkyyksiin jäävät usein todentamatta (Auzmor 2024; ISACA 2025). Tuoreen raportin mukaan lähes puolella (49 %) organisaatioista on vaikeuksia arvioida ja osoittaa luotettavasti tekoälyhankkeidensa arvoa (ISACA 2025). Tämä epävarmuus ei ole vain akateeminen ongelma, vaan se näkyy konkreettisesti esimerkiksi lakialalla, jossa epävarmuus investointien tuotoista on merkittävä este tekoälyn laajemmalle käyttöönotolle (Wolters Kluwer 2024). Lisäksi vain 24 % alan johtajista kokee, että heidän johtoryhmänsä ovat täysin yksimielisiä tekoälystrategiasta (Wolters Kluwer 2024). Tämä luo negatiivisen kierteen: ilman luotettavaa dataa osaamisen arvosta johto ei kykene perustelemaan investointeja koulutukseen ja teknologiaan, mikä johtaa aliresursointiin ja heikentää strategisten aloitteiden uskottavuutta (Disco 2024).

Ongelmaa syventää se, että luotettava itsearviointi on tunnetusti haastavaa. Osaamisen onnistunut arviointi edellyttää, että yksilö kykenee metakognitiivisesti tunnistamaan oman osaamisensa puutteet (Kruger & Dunning 1999). Tämä taito on usein heikosti kehittynyt erityisesti matalammalla osaamistasolla. Tämä Dunning–Kruger-vaikutuksena tunnettu havainto luo systemaattisen epäsuhdan havaitun ja todellisen osaamisen välille. Tämä epäsuhta on ominaista yksilötasolla, ja se ilmenee tutkitusti myös organisaatiotasolla, missä kokonaiset tiimit saattavat yliarvioida digitaalisen kypsyytensä (ks. esim. Nold & Michel 2022). Shavelsonin (2010) mukaan kompetenssin luotettava mittaaminen edellyttääkin suorituksen havainnointia, ei vain itsearviointia, mihin monet nykyiset mittarit, kuten MAILS (Meta AI Literacy Scale), osittain nojaavat (Carolus ym. 2023). Koska organisaatio ei voi luottaa pelkkään itsearviointiin, tarvitaan objektiivista, ulkoiseen todistusaineistoon perustuvaa validointiprosessia. Tämä on välttämätöntä, sillä luotettava arviointikyky edellyttää vertailua ulkoisiin viitepisteisiin (Sadler 1989), mikä auttaa ohittamaan inhimilliset harhat.

### **1.3 Metodologinen perushaaste: Reliabiliteetin ja validiteetin paradoksi**

Vaikka tarve objektiiviselle mittaamiselle on ilmeinen, se kohtaa välittömästi psykometriikan perustavanlaatuisen haasteen: arvioinnin reliabiliteetti (*luotettavuus,* *reliability*) ja validiteetti (*pätevyys,* *validity*) ovat jännitteisessä suhteessa keskenään (vrt. Borsboom ym. 2004). Nämä kaksi käsitettä ovat minkä tahansa mittausprosessin laadun kulmakiviä (vrt. Cohen ym. 1996):

1. **Reliabiliteetti** viittaa mittauksen johdonmukaisuuteen ja toistettavuuteen (AERA, APA & NCME 2014). Keskeinen kysymys on, saavatko eri arvioijat (tai sama arvioija eri aikoina) saman tuloksen samasta aineistosta. Korkea reliabiliteetti on välttämätöntä, jotta arviointi olisi oikeudenmukaista, ennustettavaa ja oikeudellisesti puolustettavaa.

2. **Pätevyys** viittaa siihen, mittaako arviointi sitä, mitä sen on tarkoitus mitata (AERA, APA & NCME 2014). Tekoälyosaamisen kontekstissa tavoitteena on mitata abstrakteja ja monimutkaisia kognitiivisia taitoja, kuten kriittistä ajattelua – joka on Halpernin (2014) mukaan tavoitteellista ja itsesäätelevää arviointia – luovaa ongelmanratkaisua ja strategista harkintaa, eikä ainoastaan mekaanista prosessien noudattamista tai ulkoa opeteltua tietoa (Wiggins 1998).

Paradoksi syntyy siitä, että näiden kahden tavoitteen välillä on usein sovittamaton jännite. Korkeaa luotettavuutta tavoittelevat menetelmät, kuten standardoidut ja tiukasti strukturoidut testit (esimerkiksi monivalinnat), ovat usein liian kapea-alaisia eivätkä onnistu mittaamaan monimutkaisia taitoja validisti (Wiggins 1998). Wigginsin mukaan tällaiset menetelmät mittaavat usein ensisijaisesti irrotettuja perustaitoja ja ulkoa muistamista, eivätkä onnistu tavoittamaan "intellektuaalista suorituskykyä" tai aitoa osaamista, joka vaatii tiedon soveltamista monimutkaisissa, autenttisissa konteksteissa (ks. myös Shafiyeva 2021; David 2019.; FairTest 2012). Toisaalta korkeaa pätevyysa tavoittelevat menetelmät, kuten avoin laadullinen portfolioarviointi, ovat usein subjektiivisia ja kärsivät heikosta reliabiliteetista (Koretz ym. 1994; vrt. Center for Innovative Teaching & Learning 2025). Tämä puolestaan tekee niistä vaikeasti skaalautuvia organisaatiokontekstissa, missä arvioinnin on oltava paitsi syvällistä myös vertailukelpoista. Tämä jännite on myös tekoälyavusteisen arvioinnin ytimessä (Bulut ym. 2024). Se asettaa keskeisen suunnitteluhaasteen: miten rakentaa järjestelmä, joka on riittävän systemaattinen ja objektiivinen soveltuakseen koneelliseen analyysiin (korkea reliabiliteetti), mutta samalla riittävän joustava ja syvällinen tunnistamaan aidon kognitiivisen mestaruuden (korkea pätevyys).

Tässä artikkelissa esiteltävässä viitekehyksessä käytettävä kolmiosainen todistusaineisto (keskusteluhistoria, lopputuote, reflektiodokumentti) ei ole portfolio perinteisessä merkityksessä. Se jakaa kuitenkin portfolion keskeisimmät psykometriset piirteet, kuten tavoitteellisuuden, moniosaisuuden ja reflektiivisyyden (Paulson ym. 1991). Koska kyseessä on laadullinen ja asiantuntija-arviointia vaativa kokonaisuus, se rinnastuu metodologisesti portfolioarviointiin ja sen tunnettuihin haasteisiin. Laaja tutkimusnäyttö osoittaa, että portfolioarvioinnin keskeisin psykometrinen heikkous on arvioitsijoiden välisen yhdenmukaisuuden (arvioitsijareliabiliteetin) matala taso (Baume & Yorke 2002). Ilman tarkkaa jäsentelyä ja selkeitä arviointikriteerejä, eri arvioijat – olivatpa ne ihmisiä tai algoritmeja – kiinnittävät huomiota eri asioihin, mikä lisää tulkinnanvaraisuutta (vrt. Jonsson & Svingby 2007).

Metodologinen kehitys kohti kognitiivisten prosessien arviointia syventää tätä paradoksia entisestään. Tämä siirtymä vaatii luotettavia ja validoituja työkaluja, jotka täyttävät psykometriikan standardit (AERA, APA & NCME 2014). Tällaisten työkalujen kehittäminen subjektiivisten kognitiivisten ilmiöiden arvioimiseksi on kuitenkin osoittautunut metodologisesti erittäin haastavaksi (vrt. Messick 1989). Siirtymä kohti kognitiivisten prosessien arviointia ei siten ainoastaan vaikeuta reliabiliteetin varmistamista, vaan myös aktiivisesti voimistaa paradoksin jännitettä, koska monimutkaisten taitojen mittaaminen on luontaisesti haastavampaa kuin yksinkertaisten tietojen (Shavelson 2013). Vaikka kognitiiviset taksonomiat, kuten Bloomin malli (Anderson & Krathwohl 2001), tarjoavat tarpeellisen rakenteen, on tärkeää tunnustaa niiden rajoitukset. Kriitikot huomauttavat, että tällaiset mallit voivat esittää osaamisen staattisena ja atomistisena hierarkiana, joka ei täysin tavoita aidon asiantuntijuuden integroitua ja dynaamista luonnetta (Lane 2013; vrt. Dreyfus & Dreyfus 1980). Tämä asettaa seuraavassa luvussa esiteltävälle arkkitehtoniselle ratkaisulle – hybridirubriikille – entistäkin suurempia vaatimuksia. Sen on kyettävä hallitsemaan tätä voimistunutta jännitettä tavalla, joka on sekä teoreettisesti vankka että käytännössä toimiva. Hybridirubriikki ja sen operatiivinen toteutus ”Kognitiivinen Kvoorum” on kehitetty juuri tämän hypoteesin testaamiseksi. On kuitenkin olennaista ymmärtää, että vaikka tämän prototyypin logiikka on toteutettu, empiirinen näyttö sen käytännön toimivuudesta tai kyvystä ratkaista tämä paradoksi puuttuu. Koko viitekehys edustaa tässä vaiheessa ainoastaan testattavaksi ehdotettua, teknisesti toteutettua mutta todentamatonta ratkaisumallia.

### **1.4 Tutkimusote ja \-menetelmä**

Tämä artikkeli noudattaa konstruktiivista tutkimusotetta, joka asemoituu Design Science Research (DSR) \-metodologian piiriin. DSR:n tavoitteena on ratkaista relevantteja käytännön ongelmia kehittämällä ja arvioimalla innovatiivisia IT-artefakteja vakiintuneen tietopohjan (engl. *knowledge base*) pohjalta (Hevner ym. 2004). Tässä tutkimuksessa keskeinen ongelma on tekoälyosaamisen mittaamisen kriisi (Luku 1.2), ja kehitetty artefakti on Hybridirubriikki-viitekehys ja sen operatiivinen malli, Kognitiivinen Kvoorum (Luku 2). DSR-prosessin mukaisesti (Peffers ym. 2007\) tämä artikkeli keskittyy ongelman tunnistamiseen ja motivointiin (Luku 1), ratkaisun tavoitteiden määrittelyyn (Luku 2.1) sekä artefaktin suunnitteluun ja kehittämiseen (Luvut 2 ja 4). Tässä vaiheessa artefaktin demonstrointi rajoittuu sen prototyypin kuvaukseen ja teoreettiseen perusteluun. Kuten Luvussa 6.2 todetaan, artefaktin muodollinen arviointi (engl. evaluation) empiirisessä kontekstissa on välttämätön jatkotutkimuksen kohde.

## **Luku 2: Hybridirubriikin Arkkitehtuuri ja Operatiivinen Malli**

Tämä luku esittelee Hybridirubriikki-viitekehyksen arkkitehtuurin ja sen operatiivisen mallin. Kyseessä on uusi arviointiviitekehys, joka on suunniteltu vastaamaan tekoälyn aikakauden monimutkaisten taitojen mittaamisen haasteisiin. Luvun rakenne etenee systemaattisesti järjestelmän perustasta sen toimintaan ja hallintaan. Ensin kuvataan järjestelmän taustalla olevat suunnitteluperiaatteet ja arvioinnin kohde. Tämän jälkeen esitellään arkkitehtuurin staattiset komponentit, eli mistä osista järjestelmä koostuu. Seuraavaksi kuvataan järjestelmän dynaaminen toiminta eli operatiivinen prosessimalli vaihe vaiheelta. Lopuksi käsitellään järjestelmän eheyden varmistavaa hallintamallia ja monikerroksista puolustusstrategiaa.

### **2.1 Suunnitteluperiaatteet ja Arkkitehtuurin Yleiskuva**

Tämä osio luo perustan koko viitekehykselle määrittelemällä sen keskeiset suunnitteluperiaatteet ja arvioinnin kohteen. Aluksi kuvataan arkkitehtuurin filosofinen ydin: tietoinen päätös hallita reliabiliteetin ja validiteetin välistä jännitettä kaksitasoisella rakenteella. Tämän jälkeen määritellään standardoitu, kolmiosainen todistusaineisto, joka toimii syötteenä myöhemmin kuvattaville arkkitehtuurin komponenteille ja operatiiviselle prosessille. Nämä määrittelyt ohjaavat kaikkia seuraavissa osioissa esitettyjä teknisiä ja metodologisia valintoja.

#### **2.1.1 Ratkaisun Periaate: Kaksitasoinen Vastaus Mittaamisen Paradoksiin**

Viitekehys tarjoaa edellä kuvattuun reliabiliteetin ja validiteetin paradoksiin arkkitehtonisen vastauksen: hybridirubriikin. Sen keskeisenä suunnitteluperiaatteena ei ole pyrkiä ratkaisemaan tätä perustavanlaatuista jännitettä tai löytää täydellistä kompromissia, vaan tunnustaa se ja rakentaa järjestelmä, joka hallitsee jännitettä tietoisesti. Sen sijaan, että arkkitehtuuri olisi yhtenäinen monoliitti, se on tarkoituksellisesti kaksitasoinen. Se institutionalisoi paradoksin luomalla kaksi erillistä, toisiaan täydentävää arviointitasoa, joista kumpikin on optimoitu eri päämäärään:

* Jonssonin ja Svingbyn (2007) mukaan **analyyttisten rubriikkien** keskeisenä tavoitteena on maksimoida arvioinnin reliabiliteetti tarjoamalla systemaattinen selkäranka, joka varmistaa mittauksen johdonmukaisuuden ja toistettavuuden.  
* **Holistisen tason** tehtävänä on maksimoida arvioinnin validiteetti eli pätevyys, mikä Messickin (1989) mukaan edellyttää kykyä tavoittaa monimutkaista, sääntöjä ylittävää osaamista, jota pelkkä mekaaninen analyysi ei pysty mittaamaan.

Tämä kaksitasoinen lähestymistapa on enemmän kuin tekninen ratkaisu; se on metodologinen ja filosofinen kannanotto. Se edustaa ”metodologista nöyryyttä” – avointa tunnustusta siitä, ettei mikään yksittäinen menetelmä voi yksinään tavoittaa monimutkaisen inhimillisen osaamisen koko kirjoa (vrt. Johnson & Onwuegbuzie 2004, jotka perustelevat vastaavaa pragmaattista lähestymistapaa monimenetelmätutkimuksessa).

Viitekehyksen keskeinen hypoteesi on, että järjestelmän älykkyys ei synny kummastakaan tasosta yksinään, vaan niiden hallitusta vuorovaikutuksesta. Ilmiö tunnetaan koneoppimisessa koosteoppimisen (engl. *ensemble learning*) hyötynä, jossa monimuotoisten arviointimekanismien yhdistäminen vähentää kokonaisvirhettä tehokkaammin kuin yksittäinen optimoitu malli (vrt. Sagi & Rokach 2018). Sagi ja Rokach (2018) osoittavat, että yhdistämällä useita malleja – tai tässä tapauksessa useita arviointiagentteja – voidaan kompensoida yksittäisten mallien heikkouksia ja saavuttaa tarkempi ennuste tai arvio. Kognitiivinen Kvoorum hyödyntää moniagenttijärjestelmää (MAS) jakaakseen arviointitehtävän erikoistuneille rooleille, mikä Guon ym. (2024) mukaan on tehokas keino välttää yksittäisten kielimallien kognitiivisia vinoumia.

#### **2.1.2 Arvioinnin Kohde: Kolmiosainen Todistusaineisto**

Hybridirubriikki ei arvioi vain lopputulosta, vaan kokonaisvaltaista tietotyöprosessia. Viitekehys hyödyntää neljää episteemistä ulottuvuutta mahdollistaakseen metodologisen triangulaation, jolla Johnsonin ja Onwuegbuzien (2004) pragmaattisen lähestymistavan mukaisesti pyritään tavoittamaan ilmiön totuusarvo useiden eri aineistojen välisen analyysin kautta.

Nämä neljä ulottuvuutta ovat:

1. **DATA (Mitä tehtiin):** Empiirinen todistusaineisto paljastaa, noudattaako käyttäjän toiminta aktiivista augmentaatiota vai passiivista automaatiota, mikä heijastaa Fügenerin ym. (2025) kuvaamia ihmisen ja tekoälyn välisen yhteistyön strategisia rooleja.

2. **TULOS (Mitä saatiin aikaan):** Prosessin konkreettinen lopputulema. Tämä mittaa työn substanssiarvoa ja faktuaalista oikeellisuutta, sillä ilman laadukasta tulosta hyväkään prosessi ei ole arvokas.

3. **INTENTIO (Mitä yritettiin):** Käyttäjän metakognitiivinen selitys omasta prosessistaan ja tavoitteistaan. Tämä paljastaa käyttäjän itsetuntemuksen tason ja paljastaa mahdollisen ristiriidan tekojen (Data) ja puheiden (Intentio) välillä.

4. **STANDARDI (Miten asiat pitäisi tehdä):** Normatiivinen säännöstö (kuten tämä viitekehys), jota vasten kolmea edellistä verrataan ja joka määrittelee "hyvän" kriteerit.

Tämä teoreettinen nelikenttä jalkautuu tässä artikkelissa esiteltävässä operatiivisessa mallissa **standardoiduksi, kolmiosaiseksi todistusaineistoksi**. Tämä aineisto edustaa nelikentän kolmea ensimmäistä dynaamista ulottuvuutta ja on suunniteltu tavoittamaan sekä kognitiivinen prosessi että sen tulos:

* **Keskusteluhistoria (DATA):** Autenttinen tallenne käyttäjän ja tekoälyn välisestä vuorovaikutuksesta. Tämä mahdollistaa prosessin (Analyysi) suoran havainnoinnin. Se paljastaa, onko käyttäjä vain passiivisesti hyväksynyt tekoälyn tuotokset vai ohjannut sitä aktiivisesti ja iteratiivisesti.

* **Lopputuote (TULOS):** Prosessin aikana tuotettu konkreettinen artefakti. Tämä mahdollistaa lopputuloksen laadun (Synteesi) arvioinnin.

* **Reflektiodokumentti (INTENTIO):** Käyttäjän jälkikäteen tuottama analyysi omasta prosessistaan. Tämä on ensisijainen lähde metakognition ja päättelyn laadun (Arviointi ja Argumentaatio) arvioinnissa, sillä metakognitiivinen säätely ja tieto tulevat näkyviksi juuri oman kognitiivisen prosessin sanallistamisen kautta (vrt. Flavell 1979). Flavellin uraauurtava työ metakognition parissa osoittaa, että kyky valvoa ja säädellä omia kognitiivisia prosesseja on korkean tason oppimisen ja ongelmanratkaisun ydin. Reflektiodokumentin tehtävä on pakottaa käyttäjä eksplisiittisesti sanoittamaan nämä prosessit, jolloin ne tulevat Kognitiivisen Kvoorumin arvioitaviksi.

* **Tämä dokumentti (STANDARDI):** Tämä dokumentti kertoo, kuinka kielimallit kehittyvät ja mitkä ovat kultaiset standardit kielimalleissa.

Kuten Luvussa 1.3 todetaan, tämä kokonaisuus rinnastuu metodologisesti portfolioarviointiin (Paulson ym. 1991).

### **2.2 Arkkitehtuurin Komponentit**

Kun suunnitteluperiaatteet ja arvioinnin kohde on määritelty, tässä osiossa esitellään Hybridirubriikin kaksi pääkomponenttia, jotka muodostavat sen rakenteellisen perustan (staattinen näkymä). Osio kuvaa ensin Analyyttisen Tason, joka konkretisoituu yksityiskohtaiseksi Kognitiiviseksi Arviointimatriisiksi. Tämän jälkeen esitellään Holistinen Taso, joka on toteutettu Kognitiivinen Kvoorum \-moniagenttijärjestelmänä. Nämä komponentit ovat ne mekanismit, jotka aktivoidaan seuraavassa osiossa kuvattavassa operatiivisessa mallissa.

#### **2.2.1 Analyyttinen Taso: Kognitiivinen Arviointimatriisi**

Hybridirubriikin arkkitehtuurin ensimmäinen taso on sen analyyttinen taso, joka konkretisoituu Kognitiiviseksi Arviointimatriisiksi. Jonssonin ja Svingbyn (2007) mukaan arviointimatriisien ensisijaisena tavoitteena on varmistaa arvioinnin reliabiliteetti eli mittauksen johdonmukaisuus ja toistettavuus tarjoamalla prosessille systemaattinen ja auditoitava selkäranka.

Tekoälyn aikakaudella luotettava arviointi edellyttää kuitenkin kahta toisiaan täydentävää näkökulmaa. Pelkkä lopputuloksen laadun mittaaminen on riittämätöntä, jos emme tiedä, onko sen tuottanut ihminen vai kone. Siksi tämä viitekehys jakaa analyyttisen tason kahteen rinnakkaiseen ulottuvuuteen: **1\) Kognitiivisten prosessien arviointiin** ja **2\) Strategisen ohjauksen arviointiin**.

##### **2.2.1.1 Kognitiiviset prosessit (Artefaktin laatu)**

Matriisin ensimmäinen ulottuvuus perustuu vakiintuneisiin kognitiivisen suorituskyvyn ja argumentaation viitekehyksiin. Malli hyödyntää Andersonin ja Krathwohlin (2001) uudistamaa Bloomin taksonomiaa kognitiivisten taitotasojen erittelyyn sekä Toulminin (2003) argumentaatiomallia päättelyn laadun systemaattiseen validointiin. Tämä seuraa Mislevyn (2003) periaatetta arvioinnista todistusaineistoon perustuvana argumenttina, jossa tavoitteena ei ole vain väittely, vaan totuuden selvittäminen (Crusius & Channell 2003). Rakenteellisesti menetelmä toteutetaan Smithin ja Kendallin (1963) kehittämänä BARS-asteikkona (Behaviorally Anchored Rating Scales), jossa arviointitasot ankkuroidaan konkreettisiin ja havaittaviin kuvauksiin suorituksen ominaisuuksista.

Tämä perinteinen lähestymistapa vastaa kysymykseen: *"Onko tuotettu lopputulos ja siihen johtanut päättelyketju loogisesti pätevä ja korkeatasoinen?"*

**Taulukko 1\. Kognitiivinen Arviointimatriisi (Bloom & Toulmin)**

| Kriteeri (Kognitiivinen ulottuvuus) | Taso 4 (Erinomainen / Strateginen) | Taso 3 (Hyvä / Omaperäinen) | Taso 2 (Kohtalainen / Reaktiivinen) | Taso 1 (Heikko / Puutteellinen) |
| :---- | :---- | :---- | :---- | :---- |
| **Analyysi ja Prosessin Tehokkuus** (Bloom: Analyze) | **Prosessi on strateginen.** Käyttäjä on purkanut ongelman osiin ja ohjannut tekoälyä ennaltaehkäisevästi. TAI Prosessi osoittaa poikkeuksellista ketteryyttä merkittävän oivalluksen kautta. | **Prosessi on tehokas.** Käyttäjä on tunnistanut ongelman ja ohjannut tekoälyä reaktiivisesti mutta johdonmukaisesti. | **Prosessi on reaktiivinen.** Käyttäjä reagoi vastauksiin ilman selkeää strategiaa. Iteraatioita ilman laadullista parannusta. | **Prosessi on tehoton.** Käyttäjä ei ole kyennyt ohjaamaan tekoälyä kohti tavoitetta. |
| **Arviointi ja Argumentaatio** (Bloom: Evaluate; Toulmin) | **Poikkeuksellinen arviointikyky.** Käyttäjä on haastanut tekoälyn päättelyä. Reflektio sisältää virheettömän argumentin. | **Korkea arviointikyky.** Käyttäjä on korjannut tuotoksia. Reflektio sisältää vahvan argumentin: Väite, Perusteet ja Oikeutus. | **Perustason arviointikyky.** Pieniä korjauksia. Reflektio sisältää argumentin aihion (Väite esitetty, perusteet heikkoja). | **Ei arviointikykyä.** Tekoälyn tuotokset käytetty sellaisenaan. Reflektio virheellinen tai harhaanjohtava. |
| **Synteesi ja Luovuus** (Bloom: Create) | **Strateginen synteesi.** Käyttäjä on luonut uutta, omaperäistä lisäarvoa, jota tekoäly ei ehdottanut. | **Omaperäinen synteesi.** Käyttäjä on parannellut tekoälyn tuotosta omalla perustellulla panoksellaan. | **Kooste.** Lopputuote on pääosin kooste tekoälyn materiaalista. Muutokset kielellisiä. | **Kopio.** Suora kopio tekoälyn tuottamasta materiaalista ilman omaa panosta. |

##### **2.2.1.2. Strateginen ohjaus (Toimijuuden laatu)**

Toinen, tälle viitekehykselle ominainen ulottuvuus, mittaa käyttäjän suhdetta teknologiaan. Agrawalin ym. (2022) mukaan tekoälyn yleistyminen siirtää inhimillisen arvonluonnon painopisteen rutiininomaisesta suorittamisesta kohti strategista päätöksentekoa, harkintaa ja tulosten validointia. Kun tekoäly kykenee tuottamaan sisällön, ihmisen rooliksi jää prosessin ohjaaminen ja tulosten validointi.

Strateginen ohjaus arvioi käyttäjän **toimijuutta** (engl. *agency*). Se pohjautuu tutkimukseen ihmisen ja tekoälyn yhteistyön muodoista, joissa käyttäjän rooli voi vaihdella passiivisesta delegoijasta aktiiviseen augmentoijaan. Tässä ulottuvuudessa arvioidaan, toimiiko käyttäjä prosessin "Arkkitehtina" ja "Kuskina", joka pilkkoo ongelman ja ohjaa tekoälyä tavoitteellisesti, vai passiivisena "Matkustajana", joka hyväksyy tekoälyn tuotokset sellaisenaan. Federiakin ym. (2024) korostavat, että kehotesuunnittelun (prompt engineering) laatu on muodostumassa uudeksi kriittiseksi perustaidoksi tekoälyavusteisessa tietotyössä.

**Taulukko 2\. Strategisen Ohjauksen Arviointimatriisi (Agency & Engineering)**

| Kriteeri | Taso 4: Arkkitehti (Architect) | Taso 3: Kuski (Driver) | Taso 2: Kartanlukija (Navigator) | Taso 1: Matkustaja (Passenger) |
| :---- | :---- | :---- | :---- | :---- |
| **Strateginen Ohjaus** (Agency) | **Arkkitehti (Suunnittelee):** Käyttäjä on purkanut ongelman osiin (Decomposition) ENNEN ensimmäistä promptia. Prosessi on suunniteltu ketju. | **Kuski (Ohjaa):** Käyttäjä tietää mitä haluaa ja asettaa reunaehdot. Korjaa suuntaa aktiivisesti, jos tekoäly poikkeaa. | **Kartanlukija (Korjaa):** Reaktiivinen toiminta. Epämääräinen aloitus, korjaa vasta jälkikäteen ("Ei noin, vaan näin"). | **Matkustaja (Tilaa):** Passiivinen tilaaja. "Tee essee aiheesta X". Hyväksyy ensimmäisen version. Ulkoistaa ajattelun noudattaen "Lazy User Theory" \-mallin mukaista minimiponnistelun periaatetta (Tétard & Collan 2009). |
| **Tekninen Toteutus** (Engineering) | **Insinööri:** Käyttää edistyneitä tekniikoita: Few-Shot, Chain-of-Thought, XML-tagit. Promptit ovat strukturoituja olioita. | **Osaaja:** Käyttää perustekniikoita: Roolitus, selkeät rajoitteet, kontekstin syöttö. Kieli on täsmällistä. | **Keskusteleva:** Käyttää luonnollista puhekieltä ("Voisitko..."). Promptit epätarkkoja. | **Laiska (Lazy):** Kirjoitusvirheitä, "se juttu", pelkkiä avainsanoja. Luottaa tekoälyn "mind reading" \-kykyyn. |
| **Kriittinen Iteraatio** (Falsification) | **Adversariaalinen:** Testaa rajoja ("Etsi virheet"). Spottaa faktavirheet ja pakottaa korjaamaan lähteisiin viitaten. | **Korjaava:** Huomaa selkeät virheet ja pyytää korjausta. | **Hyväksyvä:** Kehuu tekoälyä ("Hyvä\!") vaikka vastauksessa olisi puutteita. Korjaukset vain tyylillisiä. | **Sokea:** Sokea luottamus. Kopioi hallusinaatiot suoraan lopputuotteeseen. |

##### **2.2.1.3 Ennakkotapausten ja organisaatiostandardien noudattaminen (Archivist)**

Kolmas analyyttisen tason ulottuvuus arvioi käyttäjän toiminnan yhteensopivuutta organisaation parhaiden käytäntöjen ja aiempien linjausten (precedent) kanssa. Tämä ulottuvuus toteutetaan Arkistonhoitaja-agentin (Archivist) avulla, jonka arviointi perustuu oikeustieteestä lainattuun Stare decisis -periaatteeseen (Dworkin 1986). Arviointi asteikolla 1-5 (Kriittisesti Poikkeava – Vahvasti Linjassa) mittaa, kuinka hyvin käyttäjä soveltaa rakenteellisia ohjausmalleja satunnaisen kokeilun sijaan. Jotta tämä vertailu olisi pätevää, Arkistonhoitaja ei lue V2-arkkitehtuurissa raakadataa ("sokea audiointi"), vaan se reititetään dynaamisesti (Semantic Data Flow: `$steps.step_analyst`) lukemaan yksinomaan Analyytikko-agentin tuottamaa, etukäteen jäsenneltyä todistusaineistoa.

##### **2.2.1.4 Vertailu ja Synteesi: Miksi molempia tarvitaan?**

Näiden kahden ulottuvuuden suhde on kriittinen "Mittaamisen paradoksin" ratkaisemiseksi. Li ym. (2025) osoittavat, että perinteiset arviointimallit ovat alttiita "tekoälyharhalle", jossa pelkkä loogisesti eheä lopputuote voi johtaa yliarviointiin, mikäli käyttäjän omaa kriittistä ajattelua ja panosta prosessiin ei erikseen mitata. Se mittaa *mitä* on tehty, mutta on sokea sille *kuka* työn teki. Strateginen matriisi (Agency/Roles) korjaa tätä mittaamalla *miten* työ on tehty. Se paljastaa "Matkustajan", joka on tuottanut Bloomin tasolla erinomaisen analyysin, mutta jonka oma panos prosessiin on ollut olematon.

Yhdistämällä nämä tasot hybridirubriikki kykenee erottamaan aidon asiantuntijuuden (korkea kognitiivinen taso \+ aktiivinen strateginen ohjaus) näennäisosaamisesta (korkea kognitiivinen taso \+ passiivinen rooli).

**Taulukko 3\. Kognitiivisen prosessin ja Strategisen ohjauksen vertailu**

| Arvioinnin ulottuvuus | 1\. Kognitiivinen Prosessi (Artefakti) | 2\. Strateginen Ohjaus (Toimijuus) |
| :---- | :---- | :---- |
| **Pääkysymys** | *"Onko lopputulos ja reflektio laadukas ja looginen?"* | *"Kuka prosessia johti ja miten työkalua käytettiin?"* |
| **Arvioinnin kohde** | **Ajattelun laatu** (Bloomin taksonomia: Analyysi, Synteesi, Arviointi). | **Toimijuuden laatu** (Roolit: Arkkitehti, Kuski, Matkustaja). |
| **Todistusaineisto** | Lopputuote ja Reflektiodokumentin argumentaatio (Toulmin). | Keskusteluhistoria (Promptit) ja korjausliikkeet (Iteraatio). |
| **Riski / Sokea piste** | **Tekoälyharha:** Hyvä kehotus voi tuottaa täydellisen analyysin ilman käyttäjän aitoa ymmärrystä. | **Näennäisaktiivisuus:** Paljon kehotteita, mutta vähän strategista suuntaa tai laadunvalvontaa. |

##### **2.2.1.5 Metodologiset Rajoitteet**

Tämä metodologinen valinta sisältää kuitenkin tietoisesti hyväksyttyjä rajoitteita, jotka tekevät hybridimallin toisesta tasosta välttämättömän. BARS-menetelmiä on perinteisesti kehitetty tavoitteena parantaa luotettavuutta siten, että arviointitasot ankkuroidaan konkreettisiin käyttäytymiskuvauksiin (Moskal 2000; Smith & Kendall 1963). Niiden todellinen psykometrinen ylivoimaisuus muihin menetelmiin nähden on kuitenkin kyseenalaistettu (Jacobs ym. 1980). Akateemiset arviot ovat todenneet, että BARS-asteikot eivät kvantitatiivisesti arvioituna ole välttämättä parempia kuin muutkaan menetelmät (Jacobs ym. 1980), ja eräissä vertailuissa ne ovat jopa osoittaneet heikompaa arvioitsijoiden välistä yhdenmukaisuutta kuin perinteiset summatiiviset asteikot (Kinicki ym. 1985).

Lisäksi niihin liittyy tutkimuskirjallisuudessa laajasti tunnistettuja psykometrisiä ja käytännöllisiä haasteita. Niiden kehittäminen on resurssi-intensiivistä, aikaa vievää ja kallista (Morgeson ym. 2007). Lisäksi ne voivat olla joustamattomia muuttuvissa työrooleissa, jotka vaativat jatkuvaa päivitystä (Levine ym. 1988). Tämä joustamattomuus ja vaatimus määritellä spesifisiä käyttäytymismalleja voivat johtaa siihen, että ne yksinkertaistavat liikaa monimutkaisia, luovia tai strategisia tehtäviä (Klieger ym. 2018), kuten ongelmanratkaisua ja luovuutta, joita on vaikea kuvata spesifisinä, havaittavina käyttäytymisinä. Juuri tämä BARS-mallien ankkureiden "äärimmäinen spesifisyys" (engl. *extreme specificity*) voi johtaa kognitiivisen vaatimustason latistumiseen, ja se onkin tunnistettu haasteeksi arvioijille, sillä se rajoittaa niiden soveltuvuutta abstraktimpien ominaisuuksien mittaamiseen (Klieger ym. 2018).

Lisäksi BARS-asteikkojen luotettavuuden on osoitettu olevan parhaimmillaankin vain kohtalainen tai jopa rajoitettu (engl. *limited reliability*) juuri niissä konteksteissa, jotka vaativat monimutkaisten ei-teknisten taitojen arviointia, kuten vaativissa asiantuntijatehtävissä on todennettu (Kim ym. 2022). Tämän vuoksi analyyttisen tason toteuttaminen BARS-mallina ei ole ratkaisu reliabiliteettiongelmaan, vaan tietoinen kompromissi, joka tuo rakenteen arviointiin mutta jättää merkittävän osan varianssista selittämättä. Juuri nämä menetelmän sisäsyntyiset rajoitukset tekevät holistisen tason välttämättömäksi.

Kuten tämän viitekehyksen "Metodologisen nöyryyden mandaatissa" (ks. Luku 2.4.3.2, Mandaatti 3\) todetaan, kognitiivisiin prosesseihin (Bloom, Toulmin) perustuva matriisi mittaa tehokkaasti prosessin loogisuutta (Pätevyys), mutta ei välttämättä tunnista aitoa asiantuntijuutta (Mestaruus), joka ilmenee sääntöjen strategisena rikkomisena tai luovana soveltamisena. Nämä taidot ovat usein kontekstisidonnaisia, implisiittisiä (Polanyi 1966\) ja vaikeasti etukäteen määriteltäviä (vrt. Dreyfus & Dreyfus 1980).

Kognitiivisen arviointimatriisin rajoitteet eivät ole virheitä, vaan tietoinen suunnitteluvalinta. Matriisin rakenteellinen jäykkyys on välttämätöntä, jotta se voi toimia vakaana ja koneellisesti käsiteltävänä perustana. Tämän metodologisen jännitteen vuoksi viitekehys ei voi nojata pelkkään analyyttiseen tasoon, vaan vaatii toisen, dynaamisemman tason. Itse analyyttinen matriisi (Taulukko 1\) on kuitenkin rakennettu huomattavasti perinteisiä BARS-asteikkoja yksityiskohtaisemmaksi, jotta se tarjoaa riittävän erottelukyvyn.

Erityisesti korkeimman tason (Taso 4\) kriteerit sisältävät usein vaihtoehtoisia polkuja. Tämä valinta pyrkii lisäämään pätevyyttä, mutta samalla se lisää kognitiivista kuormaa ja tulkinnanvaraisuutta, mikä puolestaan luo tunnetun riskin arvioitsijoiden välisen yhdenmukaisuuden (engl. *Inter-Rater Reliability*, IRR) heikkenemiselle (Wolf & Stevens 2007; Jonsson & Svingby 2007). Kognitiivisen Kvoorumin arkkitehtuuri on suunniteltu hallitsemaan tätä lisääntynyttä jännitettä. Analyytikko-agentti ankkuroi väitteet todistusaineistoon (Luku 2.3.3), Loogikko-agentti purkaa argumentin rakenteen (Luku 2.3.4) ja Kriitikkoryhmä falsifioi argumentin (Luku 2.3.5). Tämän prosessin tavoitteena on varmistaa, että monimutkaisten kriteerien soveltaminen pysyy ankkuroituna objektiiviseen todistusaineistoon, mikä vähentää subjektiivista tulkintaa ja tukee luotettavuutta.

#### **2.2.2 Holistinen Taso: Kognitiivinen Kvoorum (MAS-arkkitehtuuri)**

Hybridirubriikin toinen arkkitehtoninen taso on sen holistinen taso. Se on suunniteltu nimenomaan kompensoimaan analyyttisen tason jäykkyyttä ja ratkaisemaan pätevyyteen liittyvä haaste. Sen tehtävänä on tunnistaa aito asiantuntijuus, joka usein ylittää tai jopa tietoisesti rikkoo ennalta määriteltyjä sääntöjä paremman lopputuloksen saavuttamiseksi.

Tämä monimutkainen ja vivahteikas analyysi vaatii erikoistuneen mekanismin, joka on tässä viitekehyksessä Kognitiivinen Kvoorum. Kognitiivinen Kvoorum on moniagenttijärjestelmä (MAS) (vrt. [Supianto ym. 2023](https://www.google.com/search?q=%23supianto2023)), joka perustuu kognitiiviseen työnjakoon. Se ei nojaa yhteen monoliittiseen tekoälymalliin vailla erillisiä konfiguraatioita, vaan jakaa analyysitehtävän erillisiin, teoreettisesti johdettuihin ja erikoistuneisiin kognitiivisiin rooleihin ([Guo ym. 2024](https://www.google.com/search?q=%23guo2024)). Operatiivinen toteutus hyödyntää **V2-arkkitehtuurin asykliseen suuntaamattomaan verkkoon (DAG)** perustuvaa rakennetta, jota orkestroi tiukasti tyypitetty `GraphEngine`. Toisin kuin aiemmissa "Panel Fusion" -malleissa, joissa kognitiiviset roolit yhdistettiin monoliittisesti yhteen kehotteeseen, V2-arkkitehtuurissa jokainen kognitiivinen rooli (esim. Loogikko, Falsifioija) toimii täysin itsenäisenä, eristettynä solmuna (Node). Jokainen solmu palauttaa tiukasti Pydantic V2 -validoitua tietorakennetta (Strict DTO), mikä eliminoi virheiden kertautumisen ja mahdollistaa massiivisesti rinnakkaisen käsittelyn (Semantic Data Flow).

Nykyisessä V2-arkkitehtuurissa järjestelmä on toteutettu dynaamisena suuntamattomana verkkona (DAG) `GraphEngine`-orkestraattorin avulla (toimintatila **Courtroom 2.0 Full Audit**). Tämä askeleen ja logiikkasolmun auditointiketju maksimoi tarkkuuden ja auditoitavuuden.

Kvoorum koostuu erikoistuneista agenteista ja solmuista (step_node), jotka jakautuvat toiminnallisiin ryhmiin:

* **Esikäsittely ja Turvaportti:** Input Processing -solmu (datan jäsentely) ja Vartija-agentti (Guard; turvallisuuden ja eheyden validointi).
* **Tiedonhankinta ja Kontekstualisointi:** Retrieval-agentti (verkkohaut ja Vertex AI -maadoitus) sekä Arkistonhoitaja-agentti (Archivist; parhaiden käytäntöjen auditointi ja tiedonhallinta).
* **Analyysi ja Profilointi:** Analyytikko-agentti (faktuaalinen laatu), Interaction Analyst (vuorovaikutuksen analysointi) ja Profiloija-agentti (Profiler; käyttäjän kognitiivinen profilointi).
* **Argumentaatio:** Loogikko-agentti (Toulminin argumentaatiomallin soveltaminen).
* **Kriitikot ja Falsifiointi:** Falsifioija-agentti (loogisten ristiriitojen etsiminen), Kausaalinen Analyytikko (syysuhteiden auditointi), Performatiivisuuden Tunnistaja (Goodhartin lain ja simulaation paljastaminen) sekä Valvoja-agentti (Overseer; ylätason faktuaalinen ja eettinen valvonta).
* **Synteesi ja Raportointi:** Tuomari-agentti (konfliktinratkaisu ja loppuarvio) sekä XAI-Raportoija-agentti (selitettävän tekoälyn tulosteen generointi).
* **Ohjaus ja Palaute:** Valmentaja-agentti (Coach; formatiivisen oppimispolun rikastaminen).

Teknisesti kunkin agentin kognitiivinen rooli on operationalisoitu tiukoilla `seed_data.json` -skeeman "PromptBlock"-komponenteilla ja hienosyisillä "System Prompt" \-määrittelyillä. Nämä kehotteet on ankkuroitu suoraan Pydantic V2 -tiedonsiirto-objekteihin (DTO), mikä takaa 100 % deterministisen ketjun. Tämän moniagenttijärjestelmän täydellinen operationaalinen komentorakenne, agenttien roolit ja vaiheittainen työnkulku muodostavat sen operatiivisen mallin.

### **2.3 Operatiivinen Malli: Sekventiaalinen Auditointiketju**

Tämä osio siirtää tarkastelun arkkitehtuurin staattisista komponenteista järjestelmän dynaamiseen toimintaan. Se kuvaa yksityiskohtaisesti "Kognitiivisen Auditointiketjun" – vaiheittaisen prosessin, jonka mukaisesti arviointi suoritetaan. Osio esittää, miten arkkitehtuurin komponentit (agentit ja matriisi) prosessoivat todistusaineistoa. Käsitteellinen prosessi koostuu viidestä loogisesta päävaiheesta (1–5), alkaen syötteen esikäsittelystä, edeten analyysiin ja argumentaatioon, jatkuen kriittiseen falsifiointiin ja päättyen lopulliseen synteesiin. V2-arkkitehtuurissa nämä viisi teoreettista vaihetta operationalisoidaan modulaarisena (tyypillisesti 12–15 erillisen GraphEngine-solmun) ja determinististen Python-hookkien (esim. `verify_citation_integrity`) muodostamana suuntamattomana verkkona (DAG). Solmujen tarkka määrä ja syötteiden reititys (Semantic Data Flow) on dynaamisesti konfiguroitavissa tietokantapohjaisesti, mikä mahdollistaa joustavan orkestroinnin kulloisenkin arviointitarpeen mukaan.

#### **2.3.1 Deterministinen Rangaistusmekanismi (`score_penalties`-komponentti)**

Järjestelmän sääntökantaan on koodattu ehdoton neuro-symbolinen kontrollimekanismi, joka noudattaa "Shift to Determinism" \-periaatetta. Järjestelmä erottaa toisistaan laadullisen luokittelun (tekoäly) ja kvantitatiivisen toimeenpanon (Python-koodi). Kielimalli ainoastaan tunnistaa roolin, mutta deterministinen koodikerros, erityisesti `score_penalties`-komponentti, pakottaa numeeriset rangaistukset ja suorittaa laskennan hyödyntäen asiantuntija-agenttien liputuksia. Tähän sisältyy "Passiivisuus-leikkuri", joka on kriittinen rankaisukontrolli:

Jos käyttäjä on 'Matkustaja' (Asteikon minimitaso, esim. 1 tai 10\) missään kategoriassa, kokonaisarvosana leikataan automaattisesti asteikon alempaan kolmannekseen (Lower Third Cap).

Laskukaava: Katto = Min + ((Max - Min) / 3).

Esimerkiksi:

* Asteikko 1-4: Katto on 2.0.  
* Asteikko 1-100: Katto on 34.0.

Tämä varmistaa, että 'Matkustaja'-tason suoritus ei voi koskaan nousta 'Kuski'-tasolle (Level 3/Ylempi puolikas), riippumatta käytetystä pisteytysasteikosta.

**Perustelu:** Hyvä tekoäly ei kompensoi huonoa kuskia. Arvioimme prosessinhallintaa, emme tuuria. Jos käyttäjä nukkuu ratissa, suoritus hylätään, vaikka auto (AI) ajaisi maaliin.

**2.3.1.1 Dynaaminen tiukkuus (2D-Strictness Framework)**
Järjestelmän operatiiviseen malliin on integroitu käyttäjän määriteltävissä oleva jatkuva dynaaminen tiukkuusasteikko (1-5). Viitekehys on validointitestiensä perusteella institutionalisoinut "2D-Strictness"-moottorin (kaksiulotteisen tiukkuuden), joka jaottelee säätelyn laadulliseen "Makrotasoon" ja numeeriseen "Mikrotasoon" (0-100). Tämä erittely varmistaa, että tekoälymallin (LLM) myötäilytaipumukset katkaistaan ja järjestelmä skaalautuu kannustavasta ideoinnista ankaraan compliance-auditointiin.

* **Makroasteikko (Laadullinen Roolikohtainen Säätö):** Määrittelee tekoälyn episteemisen asenteen kognitiivisin injektioin (System Prompt). Empiiriset auditoinnit ovat paljastaneet Makrotason olevan luonteeltaan laadullinen muutos (Qualitative Shift). 
    * Asteikon alapää (Taso 1) on vapaa Ideoija (Gricean-avulias). 
    * Oletustaso (Taso 3) on Kausaalinen Analyytikko, joka etsii rakentavia syy-seuraussuhteita objektiivisesti. 
    * Yläpää (Taso 5) edustaa Kahnemanin (2011) Systeemi 2 -pakotusta ja Kindervagin (2010) Zero-Trust -arkkitehtuuria. Tekoäly on pakotettu antagonistiseksi "Syyttäjäksi", joka olettaa käyttäjän hallusinoivan kunnes empiria todistaa toisin (Null-Hypoteesi). Tällä tasolla LLM ohjelmallisesti repii vähäarvoisen datan numeerisen arvon nollaan, mutta samalla pakotettu kriittisyys ohjaa tekoälyä analysoimaan laadukasta dataa tavanomaista huomattavasti syvällisemmin (The Prosecutor Paradox). Tämä tekee Tason 5 auditoinnista ylivertaisen asiantuntijajärjestelmän lainsäädännön tai tekniikan korkean riskin analyyseihin.

* **Mikroasteikko (Määrällinen Interpolaatiokynnys):** Määrittelee BARS-matriisien numeerisen joustavuuden (0-100). Siinä missä Makrotaso muuttaa *miten* tekstiä luetaan, Mikrotaso muuttaa *kuinka raskaasti* virheistä rokotetaan.
    * Neutraali taso (50) sallii normaalin luovan tulkinnan.
    * Tason 100 (Lahjomaton) arviointi vastaa behavioristista sääntöjen seuraamista. Kynnyksen kaventaminen johtaa rutiiniosaamisen kohdalla systemaattisesti 5-10 prosenttiyksikön pistehäviöihin.
    * Nollataso (0) sallii löyhän konseptuaalisen vastaavuuden antamatta kuitenkaan "sääliä" asioista, jotka puuttuvat kokonaan.

Valitun laadullisen ja määrällisen kaksiulotteisen tiukkuustason hallinta ohjaa suoraan koko työnkulkua. Tämän arkkitehtonisen sydämen tehtävänä on estää arvioijien epäjohdonmukaisuus (IRR) ja AI:lle tyypillinen *kognitiivinen dissonanssi*. Esimerkiksi tiukka makrotaso (Syyttäjä) yhdistettynä myötäilevään mikrotasoon (0) johtaisi tilanteeseen, jossa tekoäly tuomitsee suorituksen verbaalisesti heikoksi, mutta joutuu asettamaan korkean arvosanan matriisin joustavuuden takia ("Epäilyttävä Täydellisyys").

Tämän estämiseksi V2-arkkitehtuuri on institutionalisoinut tiukkuuden ohjelmallisesti. Kun 1-5 tiukkuustaso valitaan käyttöliittymästä, Kognitiivinen Moottori skaalaa lennosta *molemmat* ulottuvuudet: se injektoi Syyttäjä-roolin (Makrotaso 5) ja ylikirjoittaa samanaikaisesti backend-koodissa kaikkien BARS-matriisien lakiteknisen täsmällisyyden tappiin (Mikrotaso 100). Tämä estää "kelluvan subjektiivisuuden" täysin ja vapauttaa organisaatiot epävarmuudesta.

#### **2.3.2 Prosessimallin Kuvaus ja Auditoitavuus**

Wooldridgen (2009) määritelmän mukaisesti järjestelmä toteuttaa moniagenttiarkkitehtuurin (MAS), joka tässä viitekehyksessä konkretisoituu dynaamisena ”kognitiivisena auditointiverkkona (DAG)”, jossa erikoistuneet agentit prosessoivat informaatiota tiukasti annettujen riippuvuuksien mukaisesti. Taustalla rullaa tarkalleen **15** dynaamisesti reititettyä teknistä DAG-solmua (toimintatila **Courtroom 2.0 Full Audit**), ja tämä arkkitehtuuri noudattaa tieteellisen menetelmän soveltamisen loogista polkua (Cheng 2001):

* **Vaihe 1: Empiirinen havainnointi (Esikäsittely).** Prosessi alkaa todistusaineiston jäsentelyllä ja turvallisuuden varmistuksella (Input Processing -solmu, Vartija-agentti, ks. Luku 2.3.3).
* **Vaihe 2: Kontekstualisointi ja Analyysi.** Tietotarpeen ankkurointi ja tiedonhaku ulkoisilla työkaluilla sekä raakadatan jäsennys (Retrieval-agentti, Arkistonhoitaja-agentti, Analyytikko-agentti).
* **Vaihe 3: Hypoteesin luominen.** Jäsennellyn argumentin ja analyysin muodostaminen käyttäjän syvä-oppimisesta (Vuorovaikutuksen analyytikko, Profiloija, Loogikko-agentti, ks. Luku 2.3.4 ja 2.3.5).
* **Vaihe 4: Falsifiointi.** Argumentti altistetaan systemaattiselle kumoamisyritykselle kriitikkopaneelin toimesta (Falsifioija-agentti, Kausaalinen-agentti, Performatiivisuuden Tunnistaja, Valvoja-agentti, ks. Luku 2.3.6).
* **Vaihe 5: Synteesi ja Johtopäätökset.** Tulokset kootaan yhteen lopulliseksi arvosanaksi ja palaute rikastetaan formatiivisella tasolla (Tuomari-agentti, Valmentaja-agentti, XAI-Raportoija-agentti, ks. Luku 2.3.7 ja 2.3.8).

Tämä verkkopohjainen (DAG) työnkulku on tietoinen arkkitehtuurivalinta, joka priorisoi maksimaalista auditoitavuutta ja jäljitettävyyttä luotettavuuden nimissä. Vaikka dynaamisemmat debatti-arkkitehtuurit voivat tuottaa syvällisempiä oivalluksia (Du ym. 2023), tämä tiukasti GraphEngineen pohjautuva malli valittiin perusarkkitehtuuriksi, jotta arviointiprosessi pysyy vakioituna ja mitattavana. Se pakottaa analyysin noudattamaan tiukasti falsifioinnin ja Toulminin mallin kaltaisia, ennalta määriteltyjä ja vakiintuneita loogisia rakenteita.

Operatiivisesti tämä auditoitavuus toteutuu siten, että jokainen solmu (agentti) tuottaa validoidun, tiukasti tyypitetyn DTO-välitulosteen (Pydantic-mallin) raa'an JSON-datan sijaan. Tämä 'Strict DTO' \-arkkitehtuuri ja modulaarinen rakenne edellyttää kaikkien välitulosten välittämistä tuomarille ristiinviittausten (esim. `$step_node_4.output`) kautta, eliminoiden manuaaliset kopioinnit. Vaikka tämä lisää promptien datalatausta, ratkaisu on strateginen: se varmistaa, että lopullinen päätös on ankkuroitu koko ketjuun. Operationaalisella tasolla verkostoa säätelevät deterministiset middleware-komponentit (hookit, esim. `verify_citation_integrity` ja tuomarin `score_penalties`), jotka suorittavat API-kutsujen välillä pakolliset faktantarkastukset (vrt. OWASP Foundation 2025d). Nämä välitulosteet muodostavat yhdessä "kognitiivisen jäljen", joka voidaan tallentaa ja esittää käyttöliittymässä täydenniteisenä audittiona (vrt. Luku 4.2).

#### **2.3.3 Vartija-komponentti: Deterministiset Hookit ja Turvaportti (Vaihe 1\)**

Operatiivinen prosessi alkaa syötteen esikäsittelyllä, jonka suorittaa "Vartija", joka V2-arkkitehtuurissa ei ole kielimalliagentti, vaan deterministinen kokoelma Python-hookkeja (esim. `check_banned_phrases`, `sanitize_text`). Nämä ohjelmalliset tarkistukset vastaavat OWASP Foundationin (2025a) suosituksia syötteen validoinnista ja puhdistuksesta kriittisenä tietoturvakontrollina. Vartija toteuttaa Teknisen Kontrollikerroksen (ks. Luku 2.4.2) toiminnot: Rakenteellinen Puhdistus, Datan Normalisointi, Datan Anonymisointi ja Aktiivinen Uhkien Luokittelu. Sen tehtävänä on torjua ulkoisia uhkia, kuten kehotemurtoja (LLM01:2025). Torjunta kohdistuu erityisesti epäsuoriin kehotemurtoihin (engl. Indirect Prompt Injection), jotka ovat kasvava uhka kielimalleille (Yi ym. 2025; Greshake ym. 2023; Liu, Yi ym. 2023; Liu, X. ym. 2024\) sekä autonomisten agenttien erityisuhkiin (AIMultiple 2025).

Viimeisenä valmisteluvaiheena ja ainoastaan jos deterministiset turvatarkistukset on läpäisty, Vartija **leimaa** alkuperäisen datan turvalliseksi (engl. Security Stamping). Vartija ei luo uutta datakopiota (token-talouden ja injektiosuojan vuoksi), vaan palauttaa **turvallisuusstatuksen** (DATA\_CHECKED\_AND\_SECURED). Tämä status toimii portinvartijana ja ilman sitä prosessi keskeytyy tiukan Fail-Fast -protokollan mukaisesti välittömään `AppException`-virheeseen.

Tämä mekanismi toteuttaa järjestelmän keskeisen turvallisuussäännön (ks. Luku 2.4.2.4, Sääntö 1: Luottamuksen Kehä), joka pakottaa validoinnin ennen prosessointia (Denning & Denning 1977).

##### **2.3.3.1 Tekninen Arkkitehtuuripäätös: Deterministinen Sivuvaunu-malli (Sidecar Auditor)**

Vartija on toteutettu rinnakkaisena ohjelmallisena tarkastajana (Parallel Audit), ei kielimallipohjaisena suodattimena.

* Mekanismi: Vartija analysoi syötteen sääntöpohjaisesti ja palauttaa turvallisuusluokituksen (DATA\_CHECKED\_AND\_SECURED), mutta ei toista alkuperäistä tekstiä.  
* Perustelu: Tämä täysin deterministinen (CPU-bound) ratkaisu poistaa LLM-hallusinaatioriskin aloituksesta, ehkäisee "Prompt Injection Mirroring" \-hyökkäykset jopa nollapäivän tekniikoissa ja puolittaa ohjelmalliset token-kustannukset massiivisilla syötteillä.  
* Kill Switch: Jos Vartija havaitsee uhkan (esim. ohjelmallinen osuma kiellettyjen termien rekisteriin), järjestelmä laukaisee välittömän keskeytyksen (Circuit Breaker) nostamalla poikkeuksen, jolloin saastunut data ei koskaan etene tekoälymalleille asti.

#### **2.3.4 Analyytikko-agentti: Todistepohjainen Ankkurointi (Vaihe 2\)**

Analyytikko-agentti aloittaa analyysivaiheen luomalla ”todistuskartan”, joka perustuu Shusterin ym. (2021) kuvaamaan ankkuroituun tiedonhakuun (RAG), jolla pyritään minimoimaan kielimallien taipumusta hallusinointiin noudattaen Sääntöä 1 (ks. Luku 2.4.2.4). Se toteuttaa tämän soveltamalla RAG-tyyppistä (engl. *Retrieval-Augmented Generation*) tiedonhakustrategiaa konteksti-ikkunan sisällä (Lewis ym. 2020), joka vähentää merkittävästi kielimallien taipumusta hallusinointiin (Shuster ym. 2021). V2-arkkitehtuurissa Analyytikko-agentin luoma todistuskartta (Strict Pydantic DTO) toimii elintärkeänä peruskalliona koko myöhemmälle DAG-verkolle. Kaikki kognitiivista profilointia (Profiloija-agentti, Profiler) tai ennakkotapausten vertailua (Arkistonhoitaja-agentti, Archivist) tekevät solmut on reititetty lukemaan suoraan tätä jäsenneltyä dataa (`$steps.step_analyst`) abstraktin raakadatan (`$inputs`) sijaan. Tämä ratkaisee tunnetun "Blindness"-riskin, jossa abstraktit asiantuntija-agentit hallusinoivat arvioita suoraan raakadatan pohjalta ilman faktuaalista esijäsennystä.

RAG-arkkitehtuureilla on kuitenkin tunnettuja heikkouksia (Ahmad ym. 2024). Yksi merkittävä haaste on ”lost in the middle” \-ilmiö, jossa mallit eivät kykene hyödyntämään tehokkaasti tietoa pitkän konteksti-ikkunan keskellä (Liu, N. F. ym. 2024). Prototyyppivaiheessa tätä riskiä ei hallita teknisesti (esim. erillisellä uudelleensijoitusmallilla; vrt. Ma ym. 2024). Riskiä pyritään kuitenkin lieventämään operatiivisesti. Analyytikko-agentti on ohjeistettu toteuttamaan kaksivaiheisen prosessin: ensin agentti suorittaa laajan haun, minkä jälkeen se optimoi tulokset sijoittamalla tärkeimmät tulokset kontekstin alkuun ja loppuun. Tämä on kehotepohjainen strategia, joka perustuu Liu, N. F. ym. (2024) havaintoihin. Lisäksi agenttia ohjeistetaan kirjaamaan tämä riski XAI-raportointia varten.

#### **2.3.5 Loogikko-agentti: Argumentaation Rakentaminen (Vaihe 3\)**

Analyytikko-agentin tuottaman todistuskartan pohjalta Loogikko-agentti rakentaa muodollisen argumentin. Sen tehtävänä on muodostaa hypoteesi käyttäjän osaamistasosta soveltamalla Kognitiivista Arviointimatriisia (Taulukko 1), joka perustuu Bloomin taksonomiaan (Anderson & Krathwohl 2001). Loogikko-agentti jäsentää analyysinsa systemaattisesti käyttäen Toulminin argumentaatiomallia (Toulmin 2003). Se esittää selkeän väitteen (osaamistaso), perusteet (viittaukset todistusaineistoon) ja oikeutuksen (päättelysäännöt matriisista). Tämä vaihe muuntaa raakadatan jäsennellyksi ja auditoitavaksi argumentiksi, joka on valmis seuraavan vaiheen kriittiseen tarkasteluun.

#### **2.3.6 Kriitikkoryhmä: Systemaattinen Falsifiointi (Vaihe 4\)**

  Neljännessä vaiheessa muodostettu argumentti altistetaan systemaattiselle kumoamisyritykselle hyödyntäen Popperin (1934) falsifiointiperiaatetta, jota sovelletaan tässä moniagenttiympäristössä kriittisenä laadunvarmistusmekanismina. Tämän tehtävän suorittaa Kriitikkoryhmä, joka koostuu neljästä erikoistuneesta agentista (Looginen Falsifioija-agentti, Faktuaalinen ja Eettinen Valvoja-agentti, Kausaalinen Analyytikko-agentti, Performatiivisuuden Tunnistaja-agentti). Ryhmän tehtävä on toimia järjestelmän sisäisenä ”paholaisen asianajajana”, ja sen toiminta perustuu Karl Popperin falsifiointiperiaatteeseen: tieteellinen totuus selvitetään yrittämällä aktiivisesti kumota esitetyt väitteet (Popper 1934\) (ks. Luku 2.4.3.2, Periaate 1).

Sen sijaan, että ryhmä etsisi vahvistusta Loogikko-agentin havainnoille, sen tehtävä on yrittää aktiivisesti kumota Loogikko-agentin muodostama argumentti. Tämä on kriittinen vaihe, sillä ilman aktiivista haastamista tekoälymallit sortuvat helposti ”myötäilyvinoumaan” (engl. *sycophancy*), jossa ne vain vahvistavat toistensa (mahdollisesti virheelliset) päätelmät (Perez ym. 2022b; Wynn, Satija & Hadfield 2025). Tämän ilmiön torjumiseksi on ensiarvoisen tärkeää, että jokainen Kriitikkoryhmän jäsen on kalibroitu täsmälleen samalla `block_instruction_strictness` -parametrilla kuin alkuperäinen Loogikko; ilman synkroitua tiukkuustasoa ryhmä saattaisi hylätä päteviä argumentteja puhtaasti siksi, että niiden numeerinen läpipääsyraja olisi satunnaisesti kalibroitu eri tasolle kuin Loogikon. Tämä monimutkainen auditointi on jaettu neljään erilliseen kognitiiviseen rooliin:

##### **2.3.5.1 Looginen Falsifioija-agentti ("Argumentaation Auditoija")**

Tämä agentti iskee argumentaation rakenteeseen. Jotta se ei sortuisi lauman mukana kulkemiseen, sille on annettu erityinen "Erimielisyyden Ylläpidon Mandaatti" (JEM) (ks. Luku 2.4.3.2, Mandaatti 1).

* **Tehtävä:** Agentin on vastustettava "konsensuksen tyranniaa" ylläpitämällä perusteltua erimielisyyttä (Wynn, Satija & Hadfield 2025). Se ei saa muuttaa analyysiaan vain ollakseen samaa mieltä muiden kanssa. Tätä varten se hyödyntää "punaisen tiimin" (engl. red teaming) menetelmiä löytääkseen haitallisia käytösmalleja (Perez ym. 2022a; Ganguli ym. 2022).  
* **Päättelyn uskollisuus (Faithfulness Audit):** Agentti tarkistaa, onko esitetty päättelyketju aito. Se etsii merkkejä siitä, että käyttäjä (tai tekoäly) on keksinyt perustelut jälkikäteen (post-hoc-rationalisointi) sen sijaan, että ne olisivat aidosti ohjanneet toimintaa (Turpin ym. 2023; Creswell ym. 2024).  
* **Rajoitteet:** Popperin falsifioinnin soveltaminen "pehmeisiin" ilmiöihin on haastavaa (ks. Nola & Sankey 2014\) ja kohtaa Duhem-Quine-teesin mukaisen ongelman, jossa yksittäistä väittämää on vaikea eristää kokonaisuudesta (Duhem 1906; Quine 1951). Lisäksi tekoälyn toiminnan stokastisuus mutkistaa suoraviivaista falsifiointia (Ganascia 2017). Siksi tässä viitekehyksessä falsifiointia käytetään täsmätyökaluna: etsitään suoria, loogisia ristiriitoja reflektion ja keskusteluhistorian välillä hyödyntämällä argumentaatioskeemojen kriittisiä kysymyksiä (Walton, Reed & Macagno 2008).

##### **2.3.5.2 Faktuaalinen ja Eettinen Valvoja-agentti ("Todisteiden Valvoja")**

Tämä agentti vastaa siitä, että väitteet vastaavat todellisuutta ja noudattavat eettisiä sääntöjä. Se ei luota pelkkään annettuun tietoon, vaan kaivaa syvemmältä.

* **RFI-Protokolla (Tiedonhankinta):** Agentti suorittaa kohdennetun uusintahaun (Request for Information Protocol) (ks. Luku 2.4.3.1, Protokolla 3). Aiemmassa prototyyppivaiheessa tämä perustui mallin sisäisen tietämyksen varaan (*Simulated Retrieval*), mutta nykyisessä V2-arkkitehtuurissa tämä vaihe on integroitu suoraan `search.py`-hookkiin, joka hyödyntää Google Vertex AI -rajapintaa ja mahdollistaa aidon episteemisen validoinnin ulkoista maailmanmallia vasten reaaliajassa. Se käyttää edistyneitä tekniikoita löytääkseen tietoa, joka jäi alkuperäiseltä haulta piiloon:  
  * **Kyselynlaajennus:** Hakulausekkeiden muokkaaminen uusista näkökulmista (Jagerman ym. 2023).  
  * **HyDE (Hypothetical Document Embeddings):** Agentti kuvittelee ideaalin dokumentin, joka kumoaisi väitteen, ja käyttää sitä hakuna (Gao ym. 2022).  
* **Heterogeenisyyden välttämättömyys:** Järjestelmän luotettavuus paranee merkittävästi, jos tämä vaihe ajetaan eri tekoälymallilla (esim. GPT-4) kuin aiemmat vaiheet (esim. Gemini) (Ye ym. 2025\) (ks. Luku 2.4.2.4, Vaatimus 1). Jos kaikki agentit käyttävät samaa mallia, ne saattavat toistaa samat virheet ja hallusinaatiot ("sokeat pisteet") (Cemri ym. 2025). Eri mallien käyttö mahdollistaa aidon ristiinvalidoinnin.  
* **Eettinen tarkastus:** Agentti etsii aktiivisesti vakavia eettisiä rikkomuksia, kuten syrjintää tai lähteiden tahallista vääristelyä (Weidinger ym. 2021).

##### **2.3.5.3 Faktuaalinen Verifiointiprotokolla (Google Search API)**

Osana Faktuaalisen ja Eettisen Valvoja-agentin toimintaa, järjestelmä toteuttaa automatisoidun "Faktuaalisen Verifiointiprotokollan". Mekanismi on suunniteltu torjumaan kielimallien taipumusta hallusinointiin (Shuster ym. 2021\) ankkuroimalla väitteet ulkoiseen, todennettavaan tietoon. Tämä implementaatio hyödyntää reaaliaikaista verkkohakua (Google Custom Search JSON API), mikä mahdollistaa aidon episteemisen validoinnin.

Protokolla etenee kolmivaiheisena prosessina, joka suoritetaan orkestrointikerroksessa ennen varsinaista agenttianalyysiä:

1. **Väitteiden Ekstraktio (Claim Extraction):** Ensimmäisessä vaiheessa järjestelmä aktivoi kevyen kielimallin (Gemini 2.5 Flash) suorittamaan semanttisen seulonnan. Mallille syötetään Lopputuote ja Reflektiodokumentti, ja sitä ohjeistetaan tunnistamaan kolme (3) keskeisintä faktaväitettä, jotka ovat alttiita virheille. Seulonta priorisoi väitteitä, jotka sisältävät spesifejä vuosilukuja, historiallisia tapahtumia, henkilöitä tai tieteellisiä faktoja, noudattaen periaatetta, jonka mukaan "kovat faktat" ovat tehokkain falsifioinnin kohde (Popper 1934).

2. **Ulkoinen Todistusaineiston Haku (External Evidence Retrieval):** Tunnistetut väitteet syötetään 

SearchService-komponentille, joka suorittaa kohdennetut haut Google Custom Search API:n kautta. Tämä vaihe on kriittinen "maailmanmallin" laajentamiseksi kielimallin staattisen koulutusdatan ulkopuolelle (vrt. Lewis ym. 2020). Järjestelmä hakee kullekin väitteelle kaksi (2) relevantinta lähdettä ja eristää niistä tiivistelmät (snippet) ja metatiedot (lähde, URL).

3. **Kontekstuaalinen Injektio (Contextual Injection):** Lopuksi hakutulokset injektoidaan suoraan Faktuaalisen ja Eettisen Valvoja-agentin konteksti-ikkunaan (Prompt Injection). Tämä muuttaa agentin tehtävän pelkästä tekstianalyysistä "todistusaineistoon perustuvaksi vertailuksi" (Evidence-Based Verification). Agentti saa käyttöönsä strukturoidun raportin:

   * Väite X (Dokumentista)

   * Ulkoinen Lähde Y (Google Search)

   * Verifiointitulos: Ristiriita / Vahvistus.

Mikäli ulkoinen haku epäonnistuu (esim. API-avainten puuttuessa), järjestelmä palautuu automaattisesti käyttämään "simuloitua hakua" (mallin sisäinen tietämys), mutta kirjaa tämän metodologiseksi rajoitteeksi (XAI-raportointi). Tämä hybridimalli varmistaa, että falsifiointiprosessi säilyttää toimintakykynsä kaikissa olosuhteissa, mutta priorisoi aina empiiristä ja tuoretta dataa Vertex AI:n kautta.

##### **2.3.5.4 Kausaalinen Analyytikko-agentti ("Temporaalinen Auditoija")**

Tämän agentin tehtävä on auditoida prosessin ajallista johdonmukaisuutta ja kausaalista uskottavuutta soveltamalla seuraavia heuristiikkoja (ks. Luku 2.4.3.4, Heuristiikat 1–3). Jotta auditoinnin L3-simulaatio olisi tarkka ja fokusoitu havaittuihin ongelmiin, agentti on reititetty lukemaan syötteenä suoraan Falsifioija-agentin löydökset (`$steps.step_falsifier`). Näin se kykenee jäljittämään yksittäisten loogisten virheiden juurisyitä dynaamisesti pitkin käyttäjän aikajanaa:

* **Temporaalinen auditointi:** Agentti tarkistaa aikajanan: ilmestyikö oivallus (syy) keskusteluhistoriaan ennen tuloksen paranemista (seuraus)? Syyn on aina edellettävä seurausta (Hume 1739; Lagnado & Sloman 2006; Pearl 2009).  
* **Kontrafaktuaalinen stressitesti (L3-simulaatio):** Agentti kysyy: 'Jos käyttäjä EI olisi tehnyt tätä oivallusta, olisiko tulos silti ollut sama?'. Tämä on yritys simuloida syvällistä syy-seuraus-päättelyä (Pearl 2009; Sgaier ym. 2020).  
* **Abduktiivinen Haasto:** Agentti soveltaa Occamin partaveistä (vrt. Walton ym. 2008). Agentti hyödyntää abduktiivista päättelyä arvioidessaan, onko käyttäjän kuvaama oivallus uskottavin selitys havaitulle muutokselle vai onko kyseessä Turpinin ym. (2023) kuvaama epäuskollinen post-hoc-rationalisointi, jossa perustelut keksitään vasta lopputuloksen saavuttamisen jälkeen.

##### **2.3.5.5 Performatiivisuuden Tunnistaja-agentti ("Käyttäytymisanalyytikko")**

Tämä agentti keskittyy tunnistamaan käyttäytymismalleja ja pelistrategioita, jotka viittaavat järjestelmän manipulointiin (Goodhartin laki) (Strathern 1997; Stumborg ym. 2022). Tätä ohjaa mandaatti (ks. Luku 2.4.3.2, Mandaatti 4). Tämän monimutkaisen behavioraalisen analyysin perustana toimii Profiloija-agentin (`$steps.step_profiler`) rakentama kognitiivinen peruslinja käyttäjästä. Vasta vertaamalla syötettä tähän strukturoituun peruslinjaan agentti kykenee luotettavasti erottamaan aidon oppimisen seuraavista anomaliaindikaattoreista:

* **Epäuskottava lineaarisuus:** Onko prosessi liian suoraviivainen ja virheetön ollakseen totta? (vrt. Goffman 1959).  
* **Pinnallinen vuorovaikutus:** Osoittaako keskusteluhistoria vain vähäistä kognitiivista syvyyttä?  
* **Kognitiivinen epäsuhta:** Vastaako reflektiossa kuvattu prosessi keskusteluhistorian todellista kulkua? Tämä analyysi perustuu kognitiivisen dissonanssin tunnistamiseen (Festinger 1957).  
* **Keinotekoinen monimutkaisuus:** Onko prosessiin lisätty turhia vaiheita vain näyttävyyden vuoksi? (Cullen 2020).  
* **Matriisin optimointi:** Vastaako reflektio epäilyttävän tarkasti arviointikriteereitä, vaikka itse työskentely ei? (Strathern 1997; Stumborg ym. 2022).  
* **Kognitiivinen investointi:** Vastaako oivallukseen käytetty kognitiivinen työpanos sen väitettyä merkittävyyttä (vrt. de Bruin ym. 2023)?  
* **Itsetehostuksen Indikaattorit:** Etsitään merkkejä itsetehostusvinoumasta (Dufner ym. 2019).  
* **Pre-Mortem Analyysi:** Agentti kääntää todistustaakan olettamalla reflektion olevan väärennös ja etsimällä tätä tukevia signaaleja (Klein 2007).  
* **Tilastollinen Anomaliantunnistus ("Epäilyttävä Täydellisyys"):** Viitekehys soveltaa periaatetta, jonka mukaan oppimisprosessi on harvoin lineaarinen ja virheetön (ks. Luku 2.4.3.2, Sääntö 4). Jos suoritus saa maksimaaliset pisteet kaikilla mittareilla ilman prosessissa näkyvää kitkaa tai iterointia, se liputetaan automaattisesti "Epäilyttävän Täydelliseksi". Tämä perustuu havaintoon, että liiallinen silottelu (engl. *over-smoothing*) on usein merkki tekoälyn generoimasta tai performatiivisesta narratiivista (Cullen 2020).

On kuitenkin huomattava, että ilman ulkoista maailmanmallia kielimalli ei kykene muodolliseen kausaaliseen päättelyyn (Chi ym. 2024), joten näiden agenttien (Kausaalinen Analyytikko-agentti ja Performatiivisuuden Tunnistaja-agentti) suorittamat testit mittaavat ensisijaisesti narratiivin loogista eheyttä eivätkä sen empiiristä totuusarvoa. Siksi nämä testit ovat "kielellisiä approksimaatioita" – ne ovat parhaita mahdollisia arvauksia, eivät matemaattisen tarkkoja todisteita. Tämä tekee järjestelmästä haavoittuvan taitavalle manipuloinnille.

#### **2.3.7 Tuomari- ja XAI-Raportoija-agentit: Synteesi ja Raportointi (Vaihe 5\)**

Viimeisessä vaiheessa, kun "käräjät" on käyty, Tuomari-agentti kokoaa tulokset. Tämä ei ole pelkkä keskiarvo, vaan hierarkkinen konfliktinratkaisu, joka noudattaa tiukkoja sääntöjä:

* **Falsifioinnin etusija:** Faktat voittavat aina tulkinnat (Popper 1934\) (ks. Luku 2.4.3.4, Sääntö 6). Jos Faktuaalinen ja Eettinen Valvoja-agentti löytää faktavirheen tai eettisen rikkomuksen, se syrjäyttää Loogikko-agentin positiivisen tulkinnan "mestaruudesta".  
* **Jäsennellyn erimielisyyden mandaatti (JEM):** Jos Kriitikkoryhmän agentit ja Loogikko-agentti ovat eri mieltä tulkinnasta, Tuomari-agentti ei saa pakottaa niitä yksimielisyyteen (ks. Luku 2.4.3.2, Mandaatti 1). Erimielisyys on arvokasta tietoa, joka paljastaa tapauksen monimutkaisuuden (Wynn, Satija & Hadfield 2025).

Tämän 'System 2' -tason synteesin onnistuminen edellyttää V2-arkkitehtuurissa nk. kognitiivisen kuorman keventämistä (Cognitive Unburdening / Anti-Bloat). Käytännössä tämä tarkoittaa, että Tuomari- ja XAI-Raportoija-agenteilta on riisuttu kaikki matalan tason heuristiikka- ja sääntöblokit. Strategiana on delegoida mikrotason virheiden etsintä alemman tason solmuille (kuten Falsifioijalle ja Analyytikolle), jolloin nämä ylätason Master-agentit voivat varata 100 % huomiostaan (Attention span) yksinomaan BARS-matriisien tulkintaan ja argumenttien punnitsemiseen. Tätä tasonvaihtoa kutsutaan viitekehyksessä myös Tripartite Calculation Boundary -arkkitehtuuriksi.

Lopuksi XAI-Raportoija-agentti laatii raportin, joka noudattaa Adadi ja Berradan (2018) kuvaamia periaatteita (XAI). Se ei vain kerro tulosta, vaan tekee näkyväksi kaiken epävarmuuden erottelemalla sen lähteet (Der Kiureghian & Ditlevsen 2009; Hüllermeier & Waegeman 2021):

* **Aleatorinen epävarmuus:** Datan epäselvyydestä johtuva epävarmuus.  
* **Systeeminen epävarmuus:** Itse järjestelmän rajoituksista (esim. kehotteiden hauraus, kausaalipäättelyn puute) johtuva epävarmuus.  
* **Episteeminen epävarmuus:** Agenttien välisestä erimielisyydestä johtuva epävarmuus.

XAI-raportti tiivistää nämä epävarmuustekijät "Luotettavuusasteeksi" (engl. *Reliability Score*). Mikäli järjestelmä ei pysty varmentamaan arkkitehtuurin eheyttä (esim. heterogeenisyyden puute; ks. Luku 2.4.2.4, Vaatimus 1), luotettavuusaste laskee automaattisesti tasolle "EHDOLLEINEN", mikä signaloi ihmisvalvojalle pakollista tarkistustarvetta noudattaen Protokollaa 4 (ks. Luku 2.4.3.3).

Tämä läpinäkyvyys on turvallisuustekijä. Raportti pakottaa ihmisvalvojan (HITL) ottamaan kantaa kriittisiin kysymyksiin (”Kriittiset Auditointikysymykset”) ja varmistaa näin, ettei tekoälyn päätöstä hyväksytä sokeasti (ks. Luku 2.4.4.1). Raportointi ja tulosten esittäminen hyödyntävät Zero-Deploy -filosofian mukaista palvelinohjattua käyttöliittymäarkkitehtuuria (Server-Driven UI), jossa backend toimittaa datan mukana UI-metadatan (esim. x-ui-variant) sekä renderöintisäännöt. Asiakassovellus toimii liiketoimintalogiikasta riisuttuna, dynaamisena renderöintimoottorina. Tämä mahdollistaa raporttinäkymän ja visualisointien dynaamisen mukautumisen analyysituloksiin ilman asiakassovelluksen päivityksiä.

Tämän lisäksi Tuomari-agentin päätöksentekoa ohjaa kooditasolle rakennettu deterministinen rangaistusmekanismi (engl. *Deterministic Penalty Rules*). Tämä mekanismi toimii varovaisuusperiaatteen mukaisena "hätäjarruna", joka ohittaa agentin inhimillisen harkinnan kriittisissä virhetilanteissa (vrt. Kahneman 2011). JudgeAgent-komponentin logiikka pakottaa arvosanat laskemaan automaattisesti, mikäli edeltävät vaiheet ovat liputtaneet fataaleja virheitä:

1. **Turvallisuusuhka (Security Threat):** Mikäli Vartija-agentti havaitsee tietoturvariskin, kaikkien osa-alueiden pisteet leikataan automaattisesti alimpaan mahdolliseen (Arvosana 1), riippumatta sisällön laadusta (vrt. OWASP Foundation 2025a).

2. **Looginen virhe (Logical Fallacy):** Mikäli Falsifioija havaitsee kriittisen "post-hoc-rationalisoinnin" tai muun päättelyvirheen, arvosana katetaan korkeintaan välttävään tasoon (Arvosana 2\) (vrt. Turpin ym. 2023).

Tämä varmistaa, että järjestelmä ei koskaan palkitse vaarallista tai loogisesti epärehellistä toimintaa, vaikka se olisi retorisesti vakuuttavaa.

#### **2.3.8 Valmentaja-agentti: Oppimispolun Rikastaminen**

Arviointiprosessin päätteeksi järjestelmä aktivoi Valmentaja-agentin, jonka tehtävänä on muuntaa summatiivinen arviointi Wigginsin (1998) periaatteiden mukaiseksi formatiiviseksi oppimissuunnitelmaksi. Sen tehtävänä on kääntää Tuomari-agentin tuottama arvio formatiiviseksi oppimissuunnitelmaksi (vrt. Wiggins 1998). Tämä vaihe ei vaikuta enää arvosanaan, vaan tähtää käyttäjän metakognitiivisten taitojen kehittämiseen (vrt. Flavell 1979).

Valmentaja-agentin toiminta perustuu "rikastetun palautteen" periaatteeseen (engl. Enriched Feedback). Agentti hyödyntää sisäistä tietokantaansa (Knowledge Base), joka sisältää kuratoidun kokoelman alan keskeistä kirjallisuutta ja käsitteitä.

Agentin enrich\_learning\_plan-metodi suorittaa kaksivaiheisen prosessin:

1. **Kontekstuaalinen haku:** Agentti skannaa käyttäjän suorituksesta ja Tuomarin arviosta tunnistetut kehityskohteet.  
2. **Viitteiden injektio:** Agentti etsii tietokannastaan (esim. JSON-muotoinen Unified Database) kuhunkin kehityskohteeseen sopivat akateemiset lähteet ja liittää ne suoraan palautteeseen.

Tämä mekanismi varmistaa, että palaute ei ole vain geneeristä kehotusta "parantaa suoritusta", vaan se tarjoaa konkreettiset, tieteellisesti validoidut työkalut (esim. "vrt. Strathern 1997") osaamisen syventämiseen (vrt. Shavelson 2013). Toiminnallisuus toteuttaa käytännössä Bloom’n taksonomian ylemmän tason tavoitteen tiedon soveltamisesta ja arvioinnista (Anderson & Krathwohl 2001).

### **2.4 Hallintamalli ja Monikerroksinen Puolustusstrategia (DiD)**

Kun arkkitehtuurin rakenne ja operatiivinen prosessi on kuvattu, tämä viimeinen osio keskittyy järjestelmän eheyden, turvallisuuden ja luotettavuuden varmistaviin mekanismeihin. Arkkitehtoniset tasot edellyttävät selkeää hallintamallia, joka muodostaa hierarkkisen kontrollirakenteen. Osio kuvaa hallintamallin, joka on toteutettu monikerroksisena puolustusstrategiana (Defense-in-Depth). Se määrittelee tekniset, behavioraaliset ja hallinnolliset kontrollikerrokset, jotka läpileikkaavat koko arkkitehtuuria ja ohjaavat operatiivista prosessia.

#### **2.4.1 Puolustusstrategian Yleiskuvaus ja Rajoitteet**

Järjestelmän eheyden varmistamiseksi hallintamalli toteutetaan monikerroksisena puolustusstrategiana, joka torjuu kielimalleihin liittyviä uhkia (OWASP Foundation 2025f). Strategia perustuu monikerroksisen puolustuksen (engl. *Defense in Depth*, DiD) \-malliin (CISA 2016\) ja koostuu kolmesta toisiaan täydentävästä kontrollikerroksesta:

1. **Tekninen Kontrollikerros** (Luku 2.4.2) suojaa ensisijaisesti ulkoisilta uhilta, kuten kehotemurroilta (LLM01:2025).  
2. **Behavioraalinen Kontrollikerros** (Luku 2.4.3) hallitsee agenttien sisäistä toimintaa ja torjuu toimivallan ylittämistä (LLM06:2025).  
3. **Hallinnollinen Kontrollikerros** (Luku 2.4.4) toimii ylimpänä valvontamekanismina (Ihmisvalvonta, HITL).

Prototyypin nykytilassa järjestelmän turvallisuutta ja luotettavuutta rajoittaa useiden kehittyneiden teknisten toimintojen puuttuminen. Näitä ovat "Semanttinen Anonymisointi", "Upotusten Eheyden Tarkistus" ja "Uudelleensijoitusmalli". Lisäksi on kriittistä tunnustaa, että prototyypissä monet kontrollit (erityisesti Teknisessä ja Behavioraalisessa kerroksessa) on toteutettu kehotepohjaisina simulaatioina, jotka emuloivat tuotantoympäristön teknisiä kontrolleja, mutta eivät korvaa niitä (vrt. Jia ym. 2025).

#### **2.4.2 Tekninen Kontrollikerros**

Ensimmäinen puolustuslinja suojaa ulkoisilta teknisiltä uhilta. Tämä kerros toteutetaan operatiivisen prosessin Vartija-agentin toimesta (ks. Luku 2.3.2). OWASP Foundationin (s.a.) suositusten mukaisesti Vartija-agentti toimii turvaporttina, joka suorittaa syötteiden validoinnin ja puhdistuksen (Input Validation & Sanitization) pienentääkseen järjestelmän hyökkäyspinta-alaa ja torjuakseen haitallisia syötteitä.

##### **2.4.2.1 Rakenteellinen Puhdistus (Input Sanitization) ja Datan Normalisointi**

Tämä vaihe yhdistää turvallisuuskontrollit ja datan eheyden varmistamisen. Ensimmäisenä puolustuslinjana (OWASP Foundation s.a) Vartija-agentin tehtävä on muuntaa kaikki syötteet (esim. PDF, DOCX) raakatekstiksi. Tämä pienentää hyökkäyspinta-alaa ja varmistaa datan yhdenmukaisuuden (OWASP Foundation 2025d). Tähän prosessiin kuuluu pakollinen datan normalisointi, joka on kriittistä merkistön eheyden ja interoperabiliteetin varmistamiseksi, erityisesti manuaalisessa orkestroinnissa (vrt. Luku 5.2.4; W3C 2008). Normalisointi sisältää pakollisen UTF-8-merkistökoodauksen varmistamisen sekä typografisten merkkien (kuten "älykkäiden lainausmerkkien") muuntamisen standardeiksi ASCII-merkeiksi. Tämän jälkeen se poistaa aktiivisesti kaikki tunnetut haitalliset merkit, skriptit ja ohjausmerkit (engl. *control characters*).

##### **2.4.2.2 Datan Anonymisointi (OWASP LLM02:2025-torjunta)**

Tämä vaihe torjuu arkaluontoisen tiedon paljastumista. Vartija-agentin tehtävä on hakea ja peittää tunnistettavat henkilötiedot (PII) monikerroksisesti (vrt. Lison ym. 2021; Li ym. 2024). Prototyyppivaiheessa ulkoisilla kirjastoilla toteutettu deterministinen anonymisointi puuttuu. Tämä korvataan agenttipohjaisella hybridimallilla, joka yhdistää kohdennetut sääntöpohjaiset (RegEx) menetelmät (esim. HETU, sähköposti) kielimallin suorittamaan laajempaan kontekstuaaliseen PII-analyysiin. Tämä mahdollistaa epätyypillisten henkilötietojen tunnistamisen (vrt. Li ym. 2024), vaikka menetelmä sisältääkin stokastisen epävarmuuden.

##### **2.4.2.3 Lainausten eheyden deterministinen tarkistus (Citation Integrity)**

Uutena kriittisenä mekanismina Tekniseen Kontrollikerrokseen lukeutuu `verify_citation_integrity` -ohjelmistorutiini. Se on deterministinen "Fail-Fast"-arkkitehtuurin mukainen Python-hook, joka toimii ehdottomana suojana tekoälyn hallusinaatioita vastaan myöhemmissä vaiheissa. Kun Analyytikko- tai Falsifioija-agentti tuottaa hypoteeseja ja perustelee ne suorin lainauksin (quotes), tämä ohjelmallinen kontrolli etsii jokaisen lainauksen alkuperäisestä lähdemateriaalista (Keskusteluhistoria tai Lopputuote). Jos suora lainaus ei vastaa täsmälleen lähdemateriaalin merkkejä, ohjelmisto hylkää väitteen automaattisesti tai laukaisee hätäkatkaisimen. Tällä eliminoidaan kokonaan riski, että kielimallit puolustelevat keksittyjä väitteitä kuvitteellisilla asiatekstilainauksilla (myötäilyvinouma ja hallusinaatiot).

#### **2.4.3 Behavioraalinen Kontrollikerros (Kognitiivinen Palomuuri)**

Järjestelmän toinen puolustuslinja on Behavioraalinen Kontrollikerros, joka toimii Anthropicin (2025a) määrittelemän perustuslaillisen tekoälyn (Constitutional AI) periaatteiden mukaisena kognitiivisena palomuurina ohjaten agenttien sisäistä toimintaa. Se on agentteja ohjaava periaatteellinen rajoituskokonaisuus. Tämän kerroksen ensisijaisena tehtävänä on hallita agenttien sisäistä toimintaa, varmistaa prosessin eheys, lieventää kognitiivisia vinoumia ja ohjata holistista arviointia.

##### **2.4.3.1 Prosessin Eheys ja Toimivallan Rajaaminen**

Järjestelmän eheyden varmistamiseksi jokaisen agentin on suoritettava pakollinen, standardoitu validointiprotokolla ennen tehtävänsä aloittamista:

**Protokolla 2 (Kolmivaiheinen Validointi):**

1. **Rakenteellinen eheys ja puhdistus:** Syötteen JSON-muodon validointi ja tarvittaessa virheensietoinen jäsennys (engl. *robust parsing*) eli "aggressiivinen puhdistus". Tämä mekanismi pyrkii pelastamaan JSON-objektin poistamalla tunnettuja formaattivääristymiä (esim. Markdown-jäänteitä).  
2. **Semanttinen eheys (Tarkistussumma):** Datan sisällön vertaaminen edellisen vaiheen generoimaan semanttiseen tarkistussummaan (ks. Luku 5.2.4).  
3. **Rakenteellinen skeptisyys:** Syötteen rakenteen kriittinen tarkastelu anomaliatunnisteiden havaitsemiseksi, mikä toimii sekundaarisena suojana kehotemurtoja (LLM01) vastaan.  
* **Perustuu:** Syötteen validoinnin parhaat käytännöt, (OWASP Foundation s.a.).  
* **Koskee:** Kaikkia DAG-verkon kognitiivista analyysisolmua (esim. Analyytikko, Loogikko, Falsifioija jne.).
Lisäksi tiedonhankinnan eheyden varmistamiseksi sovelletaan seuraavaa protokollaa:

**Protokolla 3 (RFI-Protokolla \- Tiedonhankinta):** Agentti suorittaa kohdennetun uusintahaun (Request for Information Protocol). V2-arkkitehtuurissa tämä toteutetaan reaaliaikaisena verkkohakuna (`search.py` -hook ja Vertex AI), joka ankkuroi analyysin ulkoisesti todennettavaan tietoon. Aiemmassa prototyypissä tämä tehtiin vain simuloituna hakuna.

* **Perustuu:** Iteratiivinen ja dynaaminen tiedonhaku, (vrt. Trivedi ym. 2024).  
* **Koskee:** Faktuaalinen ja Eettinen Valvoja-agentti.

Puolustusstrategia hyödyntää redundanssia. Kaikkia agentteja velvoitetaan ylläpitämään rakenteellista skeptisyyttä. Lisäksi sovelletaan menetelmää:

**Menetelmä 2 (Ristiinvalidoiva Päättelyketju / Cross-Validating Chain-of-Thought):** Agentit pakotetaan validoimaan edeltävän agentin päättelyn looginen johdonmukaisuus ja ankkurointi todistusaineistoon ennen oman prosessinsa käynnistämistä.

* **Perustuu:** Päättelyketjun looginen validointi, (Ye ym. 2025; Cemri ym. 2025).  
* **Koskee:** Kaikkia argumentatiivisia ja syntetisoivia DAG-solmuja (Analyytikko, Loogikko, Kriitikkopaneelin agentit, Tuomari, XAI-Raportoija).
Lisäksi järjestelmä asettaa tiukat rajoitteet estääkseen toimivallan ylittymisen (engl. *excessive agency*) (OWASP Foundation 2025d).

Samalla ehkäistään systeemisiä riskejä, kuten roolivuotoa (engl. *role-bleed*), jossa agentti ylittää sille määritellyn kognitiivisen roolin rajat (Yeager.ai 2023).

##### **2.4.3.2 Operatiiviset Mandaatit (Perustuslaki)**

Kognitiivista Palomuuria ylläpidetään neljällä peruuttamattomalla mandaatilla, jotka on injektoitu jokaisen agentin "sieluun" (System Prompt). Nämä ovat hierarkkisesti kaikkien muiden ohjeiden yläpuolella ja toimivat järjestelmän perustuslakina:

* **Mandaatti 1 (Järjestelmä 2 \-Pakko / System 2 Mandatory):** Evansin ja Stanovichin (2013) kehittämän kaksoisprosessiteorian mukaisesti Mandaatti 1 velvoittaa agentin käyttämään hidasta, deliberatiivista päättelyä (System 2\) nopean ja intuitiivisen vastaamisen sijaan.

* **Mandaatti 2 (Vinoumien Torjunta / Bias Prevention):** Agentin on aktiivisesti tunnistettava ja kumottava omat kognitiiviset vinoumansa, erityisesti vahvistusvinouma (Confirmation Bias) ja myötäilyvinouma (Sycophancy). Se torjuu esimerkiksi seuraavia vinoumia:

  * Auktoriteettivinoumaa (engl. *authority bias*) (Wang ym. 2023).  
  * Monisanaisuusvinoumaa (engl. *verbosity bias*) (Saito ym. 2023).  
  * Vahvistusvinoumaa (engl. *confirmation bias*) (Kahneman 2011; Talboy & Fuller 2023).  
  * Myötäilyvinoumaa (engl. *sycophancy bias*) (Perez ym. 2022b).  
  * Ankkurointivaikutusta (engl. *anchoring effect*) (Kahneman 2011).  
  * Itsetehostusvinoumaa (engl. *self-enhancement Bias*) (Dufner ym. 2019).  
  * Saatavuusvinoumaa ja Kehystysvaikutusta (engl. *availability/framing bias*) (Tversky & Kahneman 1974).  
* **Mandaatti 3 (Insinöörimäinen Nöyryys / Engineering Humility):** Agentin on tunnustettava tietonsa rajat. Hallusinaatio on fataali virhe. Jos tietoa ei ole, se on myönnettävä (Unknown Unknowns).

* **Mandaatti 4** edellyttää agentilta kykyä tunnistaa yritykset pelata järjestelmää, mikä perustuu Strathernin (1997) ja Stumborgin ym. (2022) havaintoihin Goodhartin laista, jonka mukaan mittarista tulee huono tavoite, kun sitä aletaan optimoida suorituksen kustannuksella.

##### **2.4.3.3 Säännöt (Rules of Engagement)**

Mandaattien lisäksi järjestelmä noudattaa tarkkaa säännöstöä, joka ohjaa agenttien välistä vuorovaikutusta ja päätöksentekoa:

* **Sääntö 1 (Luottamuksen Kehä / Trust Circle):** Vain Vartija-agentin (Guard) merkitsemä data on luotettavaa. Agentit eivät saa luottaa syötteeseen, josta puuttuu kryptografinen (tai simuloitu) eheysleima.

* **Sääntö 2 (Toimivalta / Jurisdiction):** Agentti ei saa keksiä faktoja tyhjästä. Kaiken analyysin on ankkuroiduttava syötettyyn dataan (Keskusteluhistoria, Lopputuote, Reflektio).

* **Sääntö 3 (Substanssi \> Muoto / Substance over Style):** Arvioinnin on perustuttava asiasisältöön, ei kielenhuollolliseen sujuvuuteen tai ulkoasuun. Tämä sääntö lievittää esteettistä vinoumaa, joka tutkitusti vääristää laatuarviota visuaalisen miellyttävyyden perusteella (Reinecke & Gajos 2014).

* **Sääntö 4 (Epäilyttävä Täydellisyys / Suspicious Perfection):** Jos prosessi on kitkaton ja virheetön, se on epäilyttävää. Aito oppiminen sisältää virheitä. Täydellisyys liputetaan anomaliana.

* **Sääntö 5 (Hauraus / Epistemic Uncertainty):** XAI-raportin on aina eriteltävä epävarmuuden lähteet. Väärä varmuus on pahempaa kuin tietämättömyys.

* **Sääntö 6 (Falsifiointi / Falsification):** Falsifiointi on ensisijaista verifiointiin nähden. Yksi todistettu virhe kumoaa sata kaunista lausetta (Popper 1934).

#### **2.4.4 Hallinnollinen Kontrollikerros (Ihmisvalvonta, HITL)**

Hallintamallin kulmakivi on Euroopan parlamentin ja neuvoston (2024) asetuksen (EU 2024/1689) mukainen pakollinen ihmisvalvonta (Human-in-the-Loop, HITL), joka toimii ylimpänä suojana monimutkaisia uhkia vastaan. Sen toiminta perustuu valvontaohjattuun automaatioon ja heijastelee EU:n tekoälysääntelyn periaatteita (AI Act, Art. 14\) (Euroopan komissio 2024a).

EU:n eettiset ohjeet määrittelevät valvonnan kolmitasoiseksi: "Human-in-the-Loop" (suom. ihminen prosessissa mukana), "Human-on-the-Loop" (suom. ihminen valvomassa prosessia) sekä "Human-in-Command" (suom. ihminen ohjaamassa prosessia) (Euroopan komission korkean tason asiantuntijaryhmä 2019). Valvonnan tulee ulottua taktisesta väliintulosta strategiseen hallintaan (Pfeifer 2025). Ihmisen rooli on toimia järjestelmän strategisena valvojana ja ylimpänä auktoriteettina.

##### **2.4.4.1 Automaatioharhan Torjunta**

HITL-varmistaja on altis automaatioharhalle (Luku 5.3.1). Tämän torjumiseksi järjestelmä soveltaa menetelmää:

**Menetelmä 3 (Kysymyksiin ohjaava raportointi):** Raporttipohja ei ole passiivinen tiedonanto, vaan se pakottaa ihmisvalvojan aktiiviseen kognitiiviseen työhön. Tämä mekanismi on toteutettu siten, että XAI-Raportoija-agentti generoi "Kriittisiä Auditointikysymyksiä", joihin ihmisvalvojan on vastattava, erityisesti koskien JEM-erimielisyyksiä (Mandaatti 1).

* **Perustuu:** Automaatioharhan aktiivinen torjunta ja kognitiivinen pakote (Parasuraman & Riley 1997).  
* **Koskee:** XAI-Raportoija-agentti, Ihmisvalvoja (HITL).

XAI-raportti pysäyttää päätöksenteon vaatimalla ihmisvahvistusta ennen lopullista hyväksyntää. Esimerkiksi: "HITL-RATKAISU VAADITAAN: Kriitikko väittää X, Loogikko väittää Y. Kumpi argumentti on paremmin tuettu todisteella Z?" Tämä varmistaa ihmisen aktiivisen osallistumisen. HITL-varmistaja tekee lopullisen, vastuullisen päätöksen.

##### **2.4.4.2 Muut Hallinnolliset Kontrollit**

Tämä kerros hallitsee myös muita systeemisiä riskejä hallinnollisilla käytännöillä. Turvaton tuotoksen käsittely (LLM05:2025) torjutaan tulosteen koodauksella (OWASP Foundation 2025c). Toimitusketjun haavoittuvuuksia (LLM03:2025) hallitaan LLMOps-käytännöillä (Kreuzberger ym. 2023). Opetusdatan myrkyttäminen (LLM04:2025) puolestaan estetään käyttämällä vain ihmisen hyväksymää dataa (D'Angelo 2025).

## **Luku 3: Viitekehyksen Asemointi: Vertaileva Analyysi Akateemisiin ja Kaupallisiin Ratkaisuihin**

Tämä luku sijoittaa viitekehyksen laajempaan kontekstiin vertaamalla sitä akateemiseen tutkimukseen ja kaupallisiin sovelluksiin. Tavoitteena on tunnistaa viitekehyksen keskeinen innovaatio ja strateginen erottautumistekijä.

### **3.1 Akateeminen maisema: Olemassa olevien osien uusi synteesi**

Vaikka kokonaisarkkitehtuuri on uusi, sen komponentit nojaavat vakiintuneisiin tutkimussuuntauksiin. Kognitiivinen Kvoorum on moniagenttijärjestelmä (MAS) (Guo ym. 2024). Olennaisia vertailukohtia ovat vastakkainasetteluun perustuvaa dynamiikkaa hyödyntävät järjestelmät, kuten generatiiviset adversarialliset verkot (GAN) (Goodfellow ym. 2014\) ja agenttien väliset debatit. Debattien on osoitettu parantavan päättelyn laatua (Du ym. 2023), mikä vahvistaa Kriitikko-agentin roolin. Viitekehys sijoittuu koulutusteknologian kentälle (Luckin ym. 2017). Nykyiset sovellukset ovat kuitenkin keskittyneet konkreettisempien tuotosten arviointiin (Bezanilla ym. 2019), eivät abstraktin päättelyprosessin analyysiin (vrt. Li ym. 2025). Argumentaation laadun analyysille löytyy vastine argumentinlouhinnan (*Argumentation Mining*) alalta, joka keskittyy argumenttirakenteiden automaattiseen tunnistamiseen tekstistä (Lippi & Torroni 2016). Rakenteellisten piirteiden analyysin on osoitettu parantavan automaattista arviointia (Wachsmuth ym. 2017), mikä tukee Loogikko-agentin Toulmin-pohjaista analyysia. Viitekehyksen ensisijainen innovaatio on näiden erillisten tutkimussuuntien – moniagenttiarkkitehtuurien, portfolioarvioinnin ja argumentinlouhinnan – ainutlaatuinen ja integroitu synteesi. Se soveltaa psykometrista teoriaa modernin tekoälyarkkitehtuurin avulla uudella, synteettisellä tavalla. Esimerkiksi Dreyfus-logiikka on koodattu eksplisiittiseksi säännöksi, ei vain filosofiseksi periaatteeksi.

### **3.2 Kaupallinen maisema: Markkinarako laadulliselle arvioinnille**

Kaupalliset ratkaisut jakautuvat pääosin kahteen kategoriaan. Tämä heijastaa laajempaa suuntausta, jossa tekoälysovellukset eriytyvät kahdentyyppisiin mekanismeihin (Wisse & Greve 2023). Formatiiviset sovellukset tukevat oppimista, kun taas summatiiviset sovellukset keskittyvät osaamisen todentamiseen ja arviointiin:

1. **Formatiiviset sovellukset**: Alustat kriittisen ajattelun harjoitteluun. Nämä keskittyvät oppimisprosessiin, mutta eivät tuota auditoitavaa arviota osaamisesta, sillä tekoälyn käyttöä varsinaisessa arvioinnissa pidetään haasteellisena (Larson ym. 2024).

2. **Summatiiviset sovellukset:** Työkalut jäsenneltyjen arviointien laatimiseen (esim. kysymystenluonti) (Boussioux 2025). Nämä keskittyvät arviointitehtävien, kuten monivalintojen, laatimiseen ja välttävät monimutkaisen, laadullisen todistusaineiston analysointia (Displayr 2024).

Viimeaikaiset tutkimukset vahvistavat tämän aukon: nykyiset työkalut laiminlyövät systemaattisesti "kriittisen ajattelun ja kehittyneet vuorovaikutuskyvyt" (Li ym. 2025). Näiden kategorioiden väliin jää markkinarako. Koska laadullinen arviointi on aikaa vievää (Suskie 2009). Markkinoilta myös puuttuu työkalu, joka kykenisi arvioimaan moniosaista todistusaineistoa automaattisesti ja syvällisesti korkean panoksen tilanteissa.

Tämä viitekehys luo uuden markkinakategorian: "automatisoitu korkean panoksen laadullinen arviointi". Sen todellinen kilpailija ei ole toinen ohjelmisto, vaan ihmisasiantuntijoiden suorittamat manuaaliset prosessit, joita se pyrkii tehostamaan.

## **Luku 4: Hybridirubriikin Strateginen Kehitys**

Tässä luvussa kuvataan viitekehyksen strategista kehitystä kohti syvällisempää ja auditoitavampaa analyysia. Perinteiset mallit kykenevät usein kertomaan, mitä tapahtui, mutta eivät miksi. Tästä syystä viitekehyksen Toulmin-pohjainen analyysi on suunniteltu tekemään päättelyketjusta läpinäkyvän.

### **4.1 Kiihtyvyyden ja Haurauden Paradoksi Strategisena Ajurina**

Arkkitehtuurin kehityspolku on sarja strategisia valintoja reliabiliteetin ja validiteetin jännitteen hallitsemiseksi. Kehityksen taustalla on kiihtyvyyden ja haurauden paradoksi. Yleiskäyttöisten tekoälymallien nopea kehitys (Raisch & Krakowski 2021\) mahdollistaa monimutkaisemmat arkkitehtuurit, mutta lisääntyvä kompleksisuus paljastaa samalla systeemisen haurauden (vrt. Brooks 1987). Tutkimus osoittaa, että moniagenttijärjestelmien (MAS) epäonnistumiset johtuvat usein koordinaatio-ongelmista, eivät yksittäisten agenttien päättelykyvystä (Cemri ym. 2025). Yksittäisen agentin älykkyyden kasvu ei ratkaise systeemisiä ongelmia (Cemri ym. 2025). Päinvastoin: älykkäämpi agentti voi argumentoida vakuuttavammin virheellisen näkemyksen puolesta (esim. myötäilyvinouman ohjaamana; Perez ym. 2022b) ja johtaa järjestelmän harhaan. Ratkaisu ei ole vain komponenttien parantaminen, vaan arkkitehtuurin tulee vahvistaa agenttien välisten suhteiden ja kontrollirakenteiden vahvistamiseen. Tulevaisuuden arkkitehtuuri on dynaaminen ekosysteemi, jossa hidas, auditoitava analyysi (korkea pätevyys) ja nopea, tehokas päättely (korkea reliabiliteetti) täydentävät toisiaan.

### **4.2 Kaksitasoinen Kognitiivinen Arkkitehtuuri: Järjestelmä 1 ja Järjestelmä 2**

Viitekehyksen strategisen kehityksen periaatteeksi on valittu Daniel Kahnemanin kaksoisprosessiteoria (Kahneman 2011). Teorian mukaan ajattelu jakautuu kahteen järjestelmään:

* **Järjestelmä 1**: Nopea, automaattinen, intuitiivinen ja tiedostamaton.

* **Järjestelmä 2**: Hidas, analyyttinen, tietoinen ja vaatii ponnistelua.

Vaikka teoria on osa tieteellistä keskustelua (Evans & Stanovich 2013), tässä sitä käytetään strategisena analogiana arkkitehtuurin jäsentämiseen. Tavoitteena on rakentaa kaksi rinnakkaista päättelyjärjestelmää:

* **”Järjestelmä 2” – Hidas, Kallis ja Syvällinen**: Nykyinen Kognitiivinen Kvoorum takaa maksimaalisen auditoitavuuden korkean riskin tapauksissa. Tämä on yhdenmukaista uuden tutkimuksen kanssa (esim. "System-2 Attention"; Weston & Sukhbaatar 2023).

* **”Järjestelmä 1” – Nopea, Tehokas ja Automatisoitu**: Pitkän aikavälin visio, tislattu agenttimalli koulutetaan Järjestelmä 2:n datalla rutiininomaisiin arviointeihin.

Arkkitehtuuri muodostaa itseään vahvistavan kehän, jossa hidas päättelyjärjestelmä (Järjestelmä 2\) toimii datan tuotantomoottorina. Se luo korkealaatuisia päättelyketjuja, jotka toimivat strategisena pääomana (Wang ym. 2022). Tätä aineistoa hyödynnetään nopean järjestelmän (Järjestelmä 1\) kehittämisessä, jolloin raskaaseen prosessointiin tehdyt investoinnit mahdollistavat kevyemmän ratkaisun skaalaamisen.

### **4.3 Kehityspolku: Kaksitasoisen Arkkitehtuurin Rakentaminen**

Kehityspolku on kolmivaiheinen. Se etenee reliabiliteetin maksimoinnista (Järjestelmä 2\) kohti tehokkuuden optimointia (Järjestelmä 1).

#### **4.3.1 Auditoitavan "Järjestelmä 2:n" Perusta**

Nykyinen malli perustuu tiukasti vaiheittaiseen työnkulkuun (”tiukasti sekventiaalinen”). Tämä ”Vaihe 1” edustaa nykyistä prototyyppiä. Sen vahvuus on korkea auditoitavuus ja läpinäkyvyys. Se asettaa luotettavuuden etusijalle. Hinta on korkea viive ja kustannukset. Tämä kustannus on strateginen investointi, joka tuottaa korkealaatuista dataa myöhempiä vaiheita varten.

#### **4.3.2 "Järjestelmä 2:n" Tehokkuuden Optimointi (V2 Nykytila)**

Tässä kehitysvaiheessa V2-arkkitehtuuri saavutti merkittävän optimoinnin siirtymällä alkupään jäykästä sekventiaalisesta ketjusta suunnatuksi asykliseksi verkoksi (engl. *Directed Acyclic Graph*, DAG), joka toteutettiin `GraphEngine`-orkestraattorin avulla. Tässä V2-mallissa järjestelmä ei enää etene vain lineaarisesti vaiheesta toiseen, vaan hyödyntää dynaamisia työnkulkuja, jotka mahdollistavat iteratiiviset palautesilmukat (esim. `step_judge`), asynkroniset rinnakkaisprosessit ja ristiinviittaukset (esim. `$step_node_4.output`). Tämä ratkaisu sallii rinnakkaisten analyysien suorittamisen samanaikaisesti menettämättä luotettavuutta. Työnkulun auditoitavuus varmistettiin tässä monimutkaisemmassa ja rinnakkaisessa rakenteessa toteuttamalla `seed_data.json` -tasoinen tiukka Pydantic DTO -riippuvuusketju ja hyödyntämällä ulkoisia maailmanmalleja Vertex AI:n verkkohakujen kautta. Kaikki solmusiirtymät ovat siten matemaattisesti tarkan deterministisiä eivätkä nojaa pelkkään tekoälyn "simulaatioon".

#### **4.3.3 Skaalautuvan "Järjestelmä 1:n" Luominen**

Pitkän aikavälin visiona on hyödyntää **tiedon tiivistämistä** (tislausta) (engl. *knowledge distillation*) (vrt. Hinton ym. 2015). Tämä vaihe merkitsee Järjestelmä 1:n luomista, jossa hybridirubriikin logiikka ”tiivistetään” yhdeksi malliksi. Aiempien vaiheiden tuottamaa dataa käytetään opetusaineistona yksittäisen mallin hienosäätöön. Kevyempi malli oppii jäljittelemään agenttitiimin päättelymalleja. Tislattu malli on kuitenkin vain niin luotettava kuin opetusdata, jolla se on koulutettu.

*Taulukko 4\. Moniagenttiarkkitehtuurien strateginen vertailu.*

| Arkkitehtuuri | Vahvuus | Heikkous | Keskeinen kompromissi |
| :---- | :---- | :---- | :---- |
| **Vaiheittainen** | Maksimaalinen auditoitavuus ja reliabiliteetti (Hybridimallin täydellinen jäljitettävyys). | Korkea latenssi ja kustannukset. | Asettaa luotettavuuden ja läpinäkyvyyden etusijalle |
| **Rinnakkainen** | Merkittävästi lyhyempi viive. | Työnkulun ohjauksen kasvanut monimutkaisuus. | Asettaa nopeuden ja tehokkuuden etusijalle. |
| **Tislattu** | Äärimmäisen matala latenssi ja kustannukset (Koko hybridilogiikka yhdessä mallissa). | Joustamattomuus; suorituskyky riippuu datan laadusta. | Asettaa skaalautuvuuden ja käytettävyyden etusijalle. |

### **4.4 Tulevaisuuden Visio: Systeemisen Resilienssin Vahvistaminen**

Järjestelmän pitkän aikavälin menestys edellyttää kehitystä, joka vahvistaa sen kykyä hallita häiriöitä (Perrow 1984). Tämä edellyttää Luvussa 5.1.1 tunnistettuihin riskeihin vastaamista. Lisäksi on otettava käyttöön ja validoitava ne kriittiset tekniset kontrollit, jotka on prototyypistä jätetty pois, sekä lisättävä seuraavat välttämättömät tekniset toiminnallisuudet:

* **Semanttinen Anonymisointi**: Siirtyminen nykyisestä RegEx-pohjaisesta suodatuksesta kehittyneempään, NLP/NER-pohjaiseen henkilötietojen (engl. *Personally Identifiable Information*, PII) tunnistukseen.

* **Upotusten Eheyden Tarkistus**: Vartija-agenttiin lisätään anomaliantunnistus, joka perustuu geometrisiin poikkeamiin.

* **Uudelleensijoitusmalli**: Analyytikko-agentin RAG-prosessiin integroidaan erillinen "re-ranker" \-malli "lost in the middle" \-ilmiön torjumiseksi.

Nämä lisäykset ovat välttämättömiä ennen kuin järjestelmää voidaan pitää tuotantokelpoisena, ja niiden käyttöönotto vaatii huolellista empiiristä testausta. Seuraavat kolme kehityskulkua tähtäävät systeemisen resilienssin lisäämiseen.

#### **4.4.1 "Järjestelmä 2:n" Päättelykyvyn Syventäminen monikierroksisella debatilla**

Nykyinen staattinen rakenne voi vahvistaa systeemisiä virheitä. Tulevaisuuden suunta on dynaaminen ”agenttiekologia”, jossa agentit osallistuvat monikierroksiseen väittelyyn (*debate*) (Liang ym. 2023). Tämä mahdollistaisi todellisen debatin Kriitikon ja Loogikon välillä. Vuorovaikutus voi tuottaa syvällisempiä oivalluksia, mutta on altis sosiaalisille vinoumille. Tutkimus osoittaa, että debatit voivat johtaa virheiden vahvistumiseen, kun agentit suosivat yksimielisyyttä (Wynn ym. 2025). Tämän "konsensuksen tyrannian" vuoksi debatin tavoitteen on oltava jäsennelty erimielisyys. Tuomari-agentin rooli muuttuu aktiiviseksi moderaattoriksi, joka varmistaa älyllisen rehellisyyden ja raportoi vähemmistönäkemykset ihmisvalvojalle.

#### **4.4.2 Siirtymä kohti agenttisuunnittelua (engl. *Agent Engineering*)**

Järjestelmän strateginen jatkokehitys on edellyttänyt siirtymistä hauraasta kehotesuunnittelusta (engl. *prompt engineering*) kohti vankempaa agenttisuunnittelun toimintamallia. Tässä lähestymistavassa turvallisuus ja logiikka eivät nojaa pelkkiin kielellisiin pyyntöihin, vaan ne koodataan suoraan järjestelmän rakenteisiin (Anthropic 2025c). Tämä rakenteellinen muutos tarkoittaa nykyisen, pelkkään kielimalliin nojaavan behavioraalisen suojauksen korvaamista erillisillä teknisillä luokittelijoilla, kuten Llama Guard \-mallilla, jotka on optimoitu tunnistamaan ja estämään haitallinen sisältö ennen sen prosessointia (Inan ym. 2023; vrt. Anthropic 2025a).

Arkkitehtuuritasolla tämä siirtymä vaati luopumista jäykästä sekventiaalisesta ketjusta ja siirtymistä suunnattuun asykliseen verkkoon (DAG). Järjestelmän pätevyys vahvistetaan jatkossa ulkoistamalla kausaalinen päättely simulaatioista todelliseen koodin suorittamiseen eristetyissä hiekkalaatikoissa ("AI Sandbox"), mikä on nousemassa yrityskäytön standardiksi (Towards AI 2025), ja vie kohti autonomisten koneälyjen edellyttämiä maailmanmalleja (LeCun 2022) ja tarjoaa deterministisen keinon todentaa väitteiden paikkansapitävyys (Turpin ym. 2025).

Myötäilyvinouman (engl. *sycophancy*) torjunnassa hyödynnetään pakotettua rakenteellista erimielisyyttä (Pydantic-validoidut ristiriidat eri agenttisolmujen välillä) käyttämällä heterogeenisia tekoälymalleja (esim. Vertex AI Flash vs. Pro), mikä estää agentteja vahvistamasta toistensa virheellisiä päätelmiä (Wynn ym. 2025). Lopullinen luottamus automaatioon varmistetaan Tuomari-agentin systemaattisella hienosäädöllä (engl. *fine-tuning*), joka perustuu laajaan ihmiskalibrointiin ja tilastollisen arvioijien välisen yhdenmukaisuuden, kuten Cohenin Kappa -kertoimen, jatkuvaan seurantaan (McHugh 2012).

#### **4.4.3 Hallintamallin Sisäistäminen**

Nykyinen kehotepohjainen Kognitiivinen Palomuuri on hauras (Luku 2.4.3). Kestävämpi ratkaisu on siirtyä sisäistettyyn hallintaan hyödyntämällä monikerroksista puolustusstrategiaa (CISA 2016). Tämä yhdistää (1) mallin sisäisen linjauksen perustuslaillisen tekoälyn (CAI) avulla (Bai ym. 2022\) sekä (2) ulkoisen valvonnan perustuslaillisilla luokittelijoilla (Anthropic 2025a; Sharma ym. 2025). CAI-lähestymistavassa periaatteet upotetaan malliin hienosäädön avulla (Bai ym. 2022). Tämä kaksitasoinen puolustus on kestävä ratkaisu (vrt. Sharma ym. 2025). Tämä siirtymä on elintärkeä dynaamisen agenttiekologian luotettavuuden kannalta. Autonomisempien agenttien toiminnan on perustuttava sisäistettyyn arvopohjaan.

Nämä kolme kehityskulkua ovat toisistaan riippuvaisia ja muodostavat vision resilientistä järjestelmästä.

*Taulukko 5\. Viitekehyksen kehitys kohti systeemistä resilienssiä.*

| Vaihe | Arkkitehtuuri | Hallintamalli | Anomaliantunnistus | Keskeinen haaste |
| :---- | :---- | :---- | :---- | :---- |
| **Nykyinen** | Staattinen Kognitiivinen Kvoorum | Kehotepohjainen Kognitiivinen Palomuuri | Ristiriitojen tunnistus (Faktuaalinen) | Kognitiivisen Arviointimatriisin normatiivisen soveltamisen ja holistisen tason Mestaruus-poikkeamien tunnistamisen välinen jännite |
| **Tuleva** | Dynaaminen Agenttiekologia (Debatti) | Perustuslaillinen tekoäly (CAI) | Prosessin uskottavuusanalyysi | Holistisen tason debatin hallinta ja agenttien välinen epäjohdonmukaisuus |
| **Visio** | Itsesäätelevä Agenttiekologia | Sisäistetty ja jaettu ”perustuslaki” | Kausaalinen auditointi (Maailmanmallit) | Hybridirubriikin täydellinen sisäistäminen ja aidon kausaalisen ymmärryksen saavuttaminen |

### **4.5 Täydentävät tieteelliset menetelmät: Psykometrinen tarkkuus ja muodollinen todentaminen**

Vaikka kaksitasoinen hybridimatriisi tarjoaa arkkitehtonisen ratkaisun reliabiliteetin ja validiteetin paradoksiin (Borsboom ym. 2004), järjestelmän mittaustarkkuutta on mahdollista parantaa integroimalla siihen vakiintuneita psykometrisia menetelmiä. Nykyinen prototyyppi nojaa arvioitsijoiden väliseen luotettavuuteen (Cohenin kappa) ja BARS-asteikkoon, mutta nämä edustavat klassista testiteoriaa (CTT), joka käsittelee virhettä erittelemättömänä kokonaisuutena.

Tulevaisuuden kehitysvaiheessa (”Järjestelmä 2:n optimointi”) viitekehys ottaa käyttöön yleistettävyysteorian (Generalizability Theory, G-teoria). Toisin kuin perinteinen luotettavuuskerroin, G-teoria mahdollistaa virhelähteiden matemaattisen erittelyn (Brennan 2001). Tämä on kriittistä moniagenttijärjestelmässä, jossa on pystyttävä erottamaan, johtuuko vaihtelu arvioivasta agentista, tehtävätyypistä vai itse opiskelijan suorituksesta. G-teorian avulla voidaan laskea optimaalinen ”kognitiivinen kvoorum” eli se agenttien ja tehtävien määrä, joka vaaditaan luotettavan G-kertoimen (\> 0.80) saavuttamiseksi.

Kognitiivisen arviointimatriisin (Taulukko 1\) tasojen kalibroinnissa siirrytään hyödyntämään osioivasteoriaa (engl. *Item Response Theory*, IRT) (Embretson & Reise 2000). Nykyinen matriisi olettaa arviointitasojen välimatkat tasaisiksi, mikä on laadullisessa arvioinnissa harvoin totta. IRT-mallinnus asettaa sekä tehtävän vaikeuden että vastaajan kyvykkyyden samalle logit-asteikolle, mikä paljastaa kriteerien todellisen erottelukyvyn ja mahdollistaa adaptiivisen testauksen.

Sisällöllisen analyysin syvyyttä vahvistetaan ottamalla käyttöön SOLO-taksonomia (engl *Structure of the Observed Learning Outcome*) (Biggs & Collis 1982). Siinä missä nykyinen Bloomin taksonomiaan (Anderson & Krathwohl 2001\) perustuva malli luokittelee kognitiivisia prosesseja, SOLO-taksonomia mittaa vastauksen rakenteellista monimutkaisuutta. Tämä tarjoaa Loogikko-agentille välineen erottaa ”monistrukturaalinen” (asiat irrallisina luetteleva) vastaus aidosti ”suhteuttavasta” (asiat kokonaisuudeksi sitovasta) vastauksesta, mikä on keskeinen syvällisen osaamisen osoitus.

Viimeisenä menetelmällisenä lisäyksenä on muodollinen todentaminen. Koska nykyiset kielimallit ovat alttiita hallusinaatiolle ja epäonnistuvat usein monimutkaisessa syysuhteisessa päättelyssä (Chi ym. 2024), järjestelmään on myöhemmissä kehitysvaiheissa strategisena tavoitteena integroida "Logic-to-Code" \-moduuli. Tässä visioidussa lähestymistavassa Loogikko-agentti ei ainoastaan arvioi argumenttia tekstinä, vaan kääntää sen premissit ja johtopäätökset formaaliksi koodiksi (esim. Python tai Prolog). Koodin turvallinen, eristetty suorittaminen tarjoaa yksiselitteisen tavan todentaa argumentin looginen eheys (vrt. Turpin ym. 2025), mikä vähentää merkittävästi retorisen uskottavuuden ja totuuden välistä kuilua.

### **4.6 Siirtymä staattisesta lopputuloksen arvioinnista dynaamiseen kognitiivisen rakenteen analyysiin**

Mestaruuden tunnistaminen edellyttää siirtymistä muuttumattomasta lopputuotteen pisteytyksestä dynaamiseen kognitiivisen rakenteen analyysiin. Aiemmin luvussa 2.4.5 kuvattu substanssiosaamisen ja kognitiivisten taitojen erottelu vaatii tuekseen menetelmiä, jotka tekevät oppimisprosessin rakenteen näkyväksi.

Keskeinen menetelmä tämän saavuttamiseksi on episteeminen verkkoanalyysi (engl. *Epistemic Network Analysis*, ENA) (Shaffer ym. 2016). ENA mallintaa koodien ja käsitteiden välisiä yhteyksiä dynaamisina verkkoina sen sijaan, että se laskisi vain niiden esiintymistiheyksiä. Teknisesti tämä toteutetaan deterministisellä "liukuvan ikkunan" (sliding window) algoritmilla, joka laskee tekstistä tunnistettujen käsitteiden yhteisesiintyvyysmatriisin ilman kielimallin generatiivista, hallusinaatioille altista päättelyä. Tämä mahdollistaa ”keskusteluhistorian” ja ”reflektiodokumentin” välisen suhteen visualisoinnin: jos reflektiossa esiintyvät käsitteet eivät muodosta verkkoa varsinaisen toiminnan kanssa, kyseessä on todennäköisesti luvussa 5.1.2 kuvattu näytöksenomainen reflektio.

Koska mestaruus on luonteeltaan usein piilevää (Polanyi 1966\) ja pakenee tarkkoja arviointimatriiseja, kokonaisvaltaista tasoa vahvistetaan adaptiivisella vertailevalla arvioinnilla (engl. *Adaptive Comparative Judgment*, ACJ) (Pollitt 2012). ACJ-menetelmässä Tuomari-agentti ei vertaa työtä ehdottomaan kriteeriin, vaan suorittaa sarjan parivertailuja (”kumpi näistä osoittaa syvempää ymmärrystä?”). Tämä menetelmä on osoittautunut perinteisiä pisteytysmenetelmiä luotettavammaksi abstraktin osaamisen arvioinnissa (Pollitt 2012), ja se luo järjestelmälle empiirisesti viritetyn laatuasteikon.

Lopuksi analyysi ulotetaan kielelliseen metatasoon tutkimalla opiskelijan tieto-opillista asemoitumista (engl. *epistemic stance*) ja metadiskurssia (Hyland 2005). Asiantuntijuus ilmenee usein tapana ilmaista varmuutta ja epävarmuutta: mestari tunnistaa tietonsa rajat ja käyttää strategisia varaumia (engl. *hedging*), kun taas noviisi tai tekoälyä kritiikittömästi jäljittelevä toimija sortuu usein perusteettomaan varmuuteen. Viitekehyksen operatiivisessa mallissa tämä kyvykkyys on jo jalkautettu kooditason lingvistisiin väliintulomekanismeihin (*linguistics hook*), jotka analysoivat tekstin metadiskursiivisia piirteitä automaattisesti ennen varsinaista agenttiarviointia. Tämän metadiskurssin analysointi tarjoaa kognitiiviselle kvoorumille uuden, sisällöstä riippumattoman merkin aidon asiantuntijuuden ja tekoälyn tuottaman tekstin erottamiseksi.

### **4.7 Hallittu kehitys luotettavuuden varmistamiseksi**

Tässä luvussa kuvattu kehityskulku vastaa ”kiihtyvyyden ja haurauden paradoksiin” (Cemri ym. 2025\) yhdistämällä arkkitehtonisen varovaisuuden metodologiseen tarkkuuteen. Ratkaisun ytimessä on Kahnemanin (2011) kaksoisprosessiteoriaan perustuva symbioosi, jossa hidas ”Järjestelmä 2” (kognitiivinen kvoorum) tuottaa korkealaatuista dataa nopean ”Järjestelmä 1:n” (tiivistetty malli) kouluttamiseksi.

Tämä strategia edellyttää kuitenkin, että hitaan järjestelmän tuottama analyysi on todistettavasti pätevää. Pelkkä laskentatehon tai ajan lisääminen ei poista virheitä, jos mittaristo on vinoutunut. Siksi luvuissa 4.6 ja 4.7 esitellyt täydentävät tieteelliset menetelmät – kuten G-teoria (Brennan 2001), episteeminen verkkoanalyysi (Shaffer ym. 2016\) ja muodollinen todentaminen – eivät ole vain lisäosia, vaan strategisia välttämättömyyksiä. Ne varmistavat, että ”Järjestelmä 2” tuottaa empiirisesti viritettyä ja rakenteellisesti syvällistä tietoa, jota ilman myöhempi tiedon tiivistäminen (engl. *Knowledge Distillation*) vain monistaisi pinnallisia virheitä (vrt. Hinton ym. 2015).

Tämä kokonaisuus tarjoaa yleistettävän mallin vastuullisen tekoälyjärjestelmän kehittämiselle, joka etenee neljän periaatteen mukaisesti:

1. **Priorisoi tarkastettavuus ja syvällisyys (Järjestelmä 2):** Aloita aina raskaalla, moniagenttipohjaisella prosessilla, joka maksimoi läpinäkyvyyden tehokkuuden kustannuksella.

2. **Varmista laatu tieteellisillä menetelmillä:** Ankkuroi arviointi vakiintuneisiin psykometrisiin malleihin (kuten IRT ja G-teoria) ja dynaamiseen rakenneanalyysiin (kuten ENA ja ACJ), jotta järjestelmä mittaa aitoa osaamista eikä vain todennäköisyyksiä.

3. **Hyödynnä varmennettua dataa skaalautumiseen (Järjestelmä 1):** Käytä tieteellisesti varmennettua prosessidataa kevyempien mallien opettamiseen, jolloin raskas investointi pätevyyteen muuttuu skaalautuvaksi pääomaksi.

4. **Siirry ulkoisesta pakosta sisäistettyyn eheyteen:** Kehitä järjestelmää kohti tilaa, jossa hallintamekanismit ja arvot on koodattu osaksi agenttien sisäistä toimintalogiikkaa (perustuslaillinen tekoäly, Constitution AI).

## **Luku 5: Keskeiset riskit ja niiden hallinta**

Tässä luvussa analysoidaan viitekehykseen liittyviä keskeisiä riskejä ja esitellään niiden hallintamekanismeja. Analyysi kattaa metodologiset ydinriskit (Luku 5.1), arkkitehtoniset riskit (Luku 5.2) sekä operatiiviset, eettiset ja teknologiset riskit (Luku 5.3).

### **5.1 Metodologiset Ydinriskit – Viitekehyksen Tieteellisen Perustan Haasteet**

#### **5.1.1 Riski: Empiirisen Validoinnin Puute**

**Riskin kuvaus**: Viitekehyksen keskeisin heikkous on empiirisen näytön puuttuminen. Sen uskottavuus nojaa todentamattomaan hypoteesiin korkean arvioijien välisen luotettavuuden (engl. *inter-rater reliability*, IRR) saavuttamisesta. Tämä on merkittävä haaste, sillä laadullisten arviointien heikkous on juuri matala IRR (Baume & Yorke 2002; Koretz ym. 1994). Riskiä korostavat prototyypin tekniset puutteet, jotka on yksityiskohtaisesti kirjattu Vartija- ja Analyytikko-agenttien tuottamiin metodologisiin lokeihin. Järjestelmästä puuttuvat edistynyt "Semanttinen Anonymisointi" (OWASP LLM02:2025 \-riskin hallinta) ja RAG-prosessin "Uudelleensijoitusmalli" ("lost in the middle" \-riski; Liu, N. F. ym. 2024). Lisäksi "Upotusten Eheyden Tarkistus" puuttuu, joten OWASP LLM08:2025 \-riski on täysin hallitsematon, koska toiminto "EI OLE KÄYTÖSSÄ".

**Riski: Vektori- ja Upotushyökkäykset (OWASP LLM08:2025).** Koska nykyinen prototyyppi ei sisällä erillistä upotusten eheyden tarkistusta (Embedding Integrity Check), RAG-arkkitehtuuri on altis ”myrkytetyille” hakutuloksille (Poisoned Retrieval) (Zou ym. 2024), ja vaatisi käyttöoikeustietoisen (permission-aware) haun toteuttamista (Zilliz 2024). Tämä puute on tehty näkyväksi pakottamalla Vartija-agentin kirjaamaan metodologiseen lokiin nimenomaisen varoituksen pakottamalla Vartija-agentin kirjaamaan metodologiseen lokiin nimenomaisen varoituksen: "RAJOITUS:... LLM08-riski hallitsematon." Näiden kehittyneiden kontrollien puuttuminen luo validointivelan, jonka vaikutuksia nykyiseen arkkitehtuuriin ei ole empiirisesti testattu. Luvussa 4.4 esitellään näkymiä näiden riskien hallitsemiseksi tulevissa iteraatioissa.

**Hallintamekanismi**: Ainoa ratkaisu on luvussa 6.2 esitetty tutkimusagenda. On käynnistettävä muodollinen pilottitutkimus, joka mittaa psykometriset ominaisuudet:

* **Reliabiliteetti**: Mitataan analyyttisen tason IRR vertaamalla järjestelmän arvioita ihmisasiantuntijoiden arvioimaan ”vertailuaineistoon” (engl. *Gold Standard*).

* **Pätevyys**: Arvioidaan holistisen tason käsitepätevyysa todentamalla, että Mestaruus-poikkeama-merkinnät korreloivat ulkoisten asiantuntija-arvioiden kanssa.

**Jäännösriski**: Riski on merkittävä, kunnes empiirinen tutkimus on suoritettu. Siihen asti viitekehys pysyy puhtaasti teoreettisena konstruktiona.

#### **5.1.2 Riski: Goodhartin Laki ja ”Performatiivinen Reflektio”**

**Riskin kuvaus**: Perustavanlaatuinen uhka on Goodhartin laki (Strathern 1997), jonka mukaisesti käyttäjät voivat oppia manipuloimaan järjestelmää (Stumborg ym. 2022). Tämä ilmenee ”performatiivisena reflektiona”, joka on tässä viitekehyksessä sovellettu termi kuvaamaan tilannetta, jossa käyttäjä tuottaa vakuuttavan, mutta epäaidon narratiivin (vrt. vaikutelmien hallinta; Cullen 2020; Levashina & Morgeson 2007). Nykyinen arkkitehtuuri ei todennäköisesti tunnista tätä.

**Juurisyy**: Nykyinen arkkitehtuuri ei kykene aitoon kausaaliseen auditointiin (Pearl 2009; Sgaier ym. 2020; Bareinboim ym. 2022). Vaikka jotkut tutkijat näkevät kielimalleissa potentiaalia kausaaliseen päättelyyn (Kiciman ym. 2023), laaja empiirinen tutkimus osoittaa, että nykyiset kielimallit epäonnistuvat systemaattisesti muodollisessa L3-tason (kontrafaktuaalit) päättelyssä ilman ulkoista maailmanmallia (Chi ym. 2024). Tämän takia viitekehyksen ”L3-simulaatio” on ymmärrettävä heuristisena narratiivisen koherenssin testinä (engl. narrative coherence check), ei matemaattisena kausaalisuuden todistuksena.

**Hallintamekanismit**:

* **Nykyinen (toiminnallinen):** Tuomari-agentin ”Aitous-epäily”-liputus. Toteutus sisältää "Epäilyttävä Täydellisyys" \-heuristiikan, joka institutionalisoi epäluulon ”liian täydellisiä” suorituksia kohtaan ja toimii tilastollisena anomaliantunnistuksena. Tämä heuristiikka (joka on konkretisoitu osaksi Tuomari-agentin päätöksentekoa) määrittelee täsmälliset ehdot liputukselle: jos suoritus saa korkeimmat pisteet (Taso 4\) kaikissa kriteereissä JA Kriitikko-agentin prosessiauditointi ei löydä poikkeamia, suoritus liputetaan automaattisesti anomaliaksi ja Aitous-epäilyllä. Lisäksi Kriitikko-agentin heuristiikkoja on vahvistettu L3-simulaatioilla. Mekanismien pätevyys on kuitenkin todentamatta.

* **Tulevaisuuden (strateginen)**: Siirtymä ”kausaaliseen auditointiin” integroimalla ”maailmanmalleja” (Luku 4.4.2).

**Jäännösriski:** Riski on akuutti. Viitekehys on nykymuodossaan haavoittuvainen taitavalle manipuloinnille. Tämän riskin torjumiseksi järjestelmä hyödyntää "Performatiivisuuden tunnistuksen", joka on suora vastatoimi Goodhartin laille ("kun mittarista tulee tavoite...") (Strathern 1997; Stumborg ym. 2022\) ja "performatiiviselle reflektiolle" (Cullen 2020).

Järjestelmä toteuttaa tämän torjunnan Prosessiauditoijaryhmän (Kausaalinen Analyytikko ja Performatiivisuuden Tunnistaja) kautta. Tämänhetkinen toteutus on kuitenkin rajoittunut heuristiikkoihin, jotka edustavat Pearlin kausaalihierarkian (PCH) alempia tasoja (Pearl 2009). Agentin suorittama "Temporaalinen Auditointi" (syy edeltää seurausta) ja "Kausaalinen Uskottavuus" \-heuristiikka (vrt. Sgaier ym. 2020\) toimivat L1-tason (Assosiaatio) ja L2-tason (Interventio) puitteissa (ks. Luku 2.4.3). Analyysin syvyyttä on parannettu ottamalla käyttöön kehittyneitä päättelyketjutekniikoita, jotka simuloivat L3-päättelyä (ks. Luku 2.4.3). Näitä ovat esimerkiksi "Kontrafaktuaalinen Stressitesti", "Abduktiivinen Haasto" ja "Pre-Mortem Analyysi" (ks. yksityiskohtainen kuvaus Luvussa 2.4.3.

Viitekehyksen suurin yksittäinen metodologinen riski on, että se ei kykene suorittamaan muodollista L3-tason (Kontrafaktuaalit) kausaalista auditointia, jota aidon performatiivisuuden tunnistaminen edellyttäisi. Tämä tarkoittaa, että järjestelmä kykenee tunnistamaan loogiset ristiriidat ja ilmeiset "mahdoton aikajana" \-virheet, mutta se on edelleen altis taitavasti laaditulle, loogisesti ehyelle mutta faktuaalisesti keksitylle narratiiville. Vaikka uudet heuristiikat parantavat L3-simulaatiota, laaja empiirinen tutkimus on osoittanut, että nykyiset kielimallit epäonnistuvat systemaattisesti muodollisessa kausaalisessa ja kontrafaktuaalisessa päättelyssä (L3) (Chi ym. 2024). Tämän takia operatiivinen malli nojaa heuristiseen uskottavuuteen (esim. aikajanan tarkistus) aidon matemaattisen kausaalianalyysin sijaan. Tämä jättää kausaalisen aukon, jota performatiivinen reflektio voi hyödyntää. Tämän vuoksi järjestelmä edellyttää pakollisen metodologisen lokikirjauksen, joka pakottaa Kausaalisen Analyytikko \-agentin tunnustamaan tämän rajoitteen: "RAJOITUS: Järjestelmä ei kykene muodolliseen L3-tason kausaaliseen päättelyyn, vaikka L3-simulaatioita käytetään. Riski performatiivisen reflektion tunnistamatta jäämisestä on kohonnut"

Tämä kuilu L3-vision (Luku 4.4.2) ja L1/L2-toteutuksen välillä on keskeisin este viitekehyksen täydelle validiteetille. Nykyiset "Deep Think" \-mallitkaan eivät kykene luotettavasti simuloimaan kontrafaktuaaleja ilman ulkoisia kausaalisia malleja tai koodipohjaista suoritusta (vrt. Turpin ym. 2025; Aryan & Liu 2025), minkä vuoksi prototyyppi tyytyy heuristiseen uskottavuusarviointiin.

#### **5.1.3 Riski: Hybridirubriikin Sisäinen Jännite**

**Riskin kuvaus**: Viitekehys institutionalisoi psykometriikan paradoksin. Jännite syntyy analyyttisen (reliabiliteetti) ja holistisen (pätevyys) tason välille, jotka ovat usein ristiriidassa.

**Hallintamekanismi**: Kaksitasoinen arkkitehtuuri (Luku 2.1) hallitsee riskiä. Konkreettinen instrumentti on Mestaruus-poikkeama-liputus, joka siirtää tulkintavastuun ihmiselle. Jännitteen hallitsemiseksi on sisäänrakennettu "Popper vs. Dreyfus" \-erotteluheuristiikka:

* **Falsifioinnin (Popper) Etusija**: Vakavaa eettistä laiminlyöntiä tai faktuaalista virhettä ei voi tulkita ”mestaruus-poikkeamaksi”.

* **Mestaruuden (Dreyfus) Tunnistaminen**: ”mestaruus-poikkeama” voi ilmetä vain matriisin odotusarvojen tietoisena ja perusteltuna rikkomisena.

**Jäännösriski**: Jännite on pysyvä. Lopullinen tulkintavastuu jää aina ihmiselle, mikä asettaa korkeat vaatimukset ihmisvalvojan asiantuntemukselle.

### **5.2 Arkkitehtoniset Riskit – Kognitiivisen Kvoorumin Sisäiset Hauraudet**

#### **5.2.1 Riski: Päättelyketjujen Epäluotettavuus**

**Riskin kuvaus**: Auditoitavuus perustuu oletukseen, että agenttien päättelyketjut ovat uskollisia (engl. *faithful*), eli ne heijastavat tarkasti mallin todellista päättelyprosessia (Jacovi & Goldberg 2020). Viimeaikainen tutkimus on entisestään vahvistanut epäilyjä tästä ja osoittanut, että jopa edistyneimmät mallit tuottavat säännöllisesti epäuskollisia päättelyketjuja (Arcuschin ym. 2025). Wolfin ym. (2023) mukaan tämä voi johtua tekoälyn linjauksen (alignment) perustavanlaatuisista teoreettisista rajoitteista. Mallit voivat päätyä "implisiittiseen post-hoc \-rationalisointiin" (Creswell ym. 2024; Arcuschin ym. 2025), jolloin ne perustelevat jälkikäteen intuitiivisesti tuotetun vastauksen (vrt. Turpin ym. 2023).

**Hallintamekanismi**: Kaksivaiheinen "teoriaohjattu prosessivalvonta". Hypoteesina on, että rationalisoinnin virheet ilmenevät argumentin rakenteessa. Valvonta toteutetaan seuraavasti:

* **Argumentin Purku (Loogikko)**: Loogikko tunnistaa argumentaatioskeeman (Walton ym. 2008\) ja tuottaa "kriittiset kysymykset".

* **Kohdennettu Stressitesti (Epäuskollisuuden Tunnistus) (Kriitikkoryhmä)**: Kriitikko käyttää kysymyslistaa stressitestissä etsiäkseen rationalisointia ja päättelyketjun epäuskollisuutta.

Tämä mekanismi siirtää valvonnan faktantarkistuksesta päättelyn laadun auditointiin.

Jäännösriski: Riski on perustavanlaatuinen nykyisille kielimalleille. Lieventämiseksi Kriitikko-agentille on sisällytetty ”Kausaalinen heuristiikka” (Luku 2.4.3), joka pakottaa arvioimaan syy-seuraussuhteen uskottavuutta (Sgaier ym. 2020).

#### **5.2.2 Riski: Systeeminen Hauraus ja Virheiden Eteneminen**

**Riskin kuvaus**: Nykyinen vaiheittainen arkkitehtuuri on hauras. Virhe alkuvaiheessa etenee koko ketjun läpi. Tämä on tunnettu MAS-koordinaatio-ongelma (Cemri ym. 2025). **Hallintamekanismi**: Riskiä hallitaan kahdella päästrategialla. Operatiivisella tasolla haurautta hallitaan automaattisten "Retry"-mekanismien (Backoff-strategia) avulla täysin automatisoidun sekventiaalisen asyklisen verkon sisällä (DAG, orkestraattorina `GraphEngine`), jotka hallinnoivat ja peittävät kielimallien satunnaiset aikakatkaisut. Ensisijainen vaatimus on arkkitehtoninen heterogeenisyys. Ilman varmistettua malliheterogeenisyyttä (esim. Gemini vs. ChatGPT) järjestelmän tuottamaa 'Kvoorumi-konsensusta' ei voida pitää luotettavana, sillä se on altis kollektiiviselle hallusinaatiolle (Wynn ym. 2025). Siirtyminen heterogeenisiin järjestelmiin parantaa suorituskykyä (Ye ym. 2025). Tämän lisäksi arkkitehtuuriin on lisätty redundanssia "Ristiinvalidoiva Ketjutus" (*Cross-Validating CoT*) \-mekanismilla (Luku 2.4.3). V2-arkkitehtuurissa koko moniagentti-infrastruktuuri ajaa tiukasti rakennettujen Pydantic V2 -Skeemojen varassa, mikä eliminoi inhimillisten siirtovirheiden mahdollisuuden. Koska `GraphEngine` hallitsee kutsuttavat mallit suoraan konfiguraatiosta riippuen, järjestelmä kykenee myös tulevaisuudessa pakottamaan heterogeenisuuden haluttujen ajosolmukkeiden (nodes) kohdalla ohjelmoidaan sääntöpohjaisesti.

**Jäännösriski:** Homogeeninen ajo lisää merkittävästi systeemisen virheen riskiä \- prototyyppi pysyy hauraana. Ratkaisu on siirtyminen rinnakkaiseen arkkitehtuuriin (Luku 4.3.2). Siihen asti luotettavuus riippuu korostetusti ihmisvalvojasta (HITL). Tämän riskin hallinta on konkretisoitu pakottamalla XAI-Raportoija-agentin raportoimaan ihmisvalvojalle vastuun heterogeenisyyden varmentamisesta. Järjestelmän pätevyys edellyttää heterogeenista arkkitehtuuria, sillä homogeeninen ajo lisää riskiä systeemisten virheiden vahvistumisesta (Cemri ym. 2025\) ja mitätöi aidon ristiinvarmentamisen (engl. *cross-verification*) hyödyn (Ye ym. 2025).

#### **5.2.3 Riski: Debatin degeneraatio ja konsensuksen tyrannia**

**Riskin kuvaus**: Vaikka adversariaalisen debatin on osoitettu parantavan päättelyä (Du ym. 2023), tuoreempi tutkimus viittaa "konsensuksen tyranniaan" (Wynn ym. 2025). Homogeenisissä ryhmissä agentit saattavat asettaa etusijalle sosiaalista mukautumista totuudenmukaisuuden kustannuksella. Tämä voi johtaa tilanteeseen, jossa virheellinen mutta enemmistön kannattama näkemys syrjäyttää oikean vähemmistönäkemyksen. Wynn ym. (2025) osoittivat, että debatti voi jopa heikentää suoritusta, jos agentit eivät ole riittävän kyvykkäitä tai jos ne ovat taipuvaisia myötäilyvinoumaan.

**Hallintamekanismit**:

* **Vinoumat**: Siirtyminen heterogeeniseen MAS-arkkitehtuuriin (suositeltu).

* **Erimielisyys**: Järjestelmä tekee erimielisyydestä strategista pääomaa. Vastaus on ”Jäsennellyn Erimielisyyden Mandaatti” (JEM), joka on toteutettu kaksitasoisesti. Kriitikko-agentti ohjeistetaan aktiivisesti ylläpitämään erimielisyyttä (Luku 2.4.3), ja Tuomari-agenttia kielletään pakottamasta konsensusta ja ohjeistetaan raportoimaan erimielisyydestä.

**Jäännösriski**: Nykyinen prototyyppi on altis vinoumille. Erimielisyyden tulkintavastuu siirtyy ihmiselle.

#### **5.2.4 Riski: Heterogeenisen Arkkitehtuurin Yhteentoimivuus**

**Riskin kuvaus**: Suositeltu heterogeeninen arkkitehtuuri (Luku 5.2.2), jossa eri agentit käyttävät eri yleiskäyttöisiä tekoälymalleja (Malli A ja Malli B), tuo mukanaan teknisen yhteen toimivuuden (engl. *interoperability*) riskin. Kun dataa (JSON) siirretään mallien välillä, on riski datan eheyden vaarantumisesta siirron tai tulkinnan aikana (vrt. ISO/IEC 25010 2023).

**Hallintamekanismi**: Riskiä hallitaan teknisillä ja semanttisilla kontrolleilla. Jokaiseen prosessivaiheeseen on sisällytetty pakollinen syötteen eheyden tarkistus. Tämä tarkistus varmistaa rakenteellisen (JSON-kelpoisuus) ja perustason semanttisen eheyden (merkistö). 

V2-arkkitehtuurissa manuaalinen orkestrointi on kokonaan poistettu ja korvattu `GraphEngine` DAG-moottorilla. Datasiirron turvaamiseksi agenttien välillä hyödynnetään tiukkaa Pydantic V2 -objektivalidointia. Jokainen agentti tuottaa täysin tyyppivarmistetun Data Transfer Objectin (DTO), joka hylätään automaattisesti (Fail-Fast), mikäli sen rakenne ei vastaa ohjelmallisesti odotettua asyklisen verkon skeemaa. Tämä eliminoi JSON-kapselointiongelmat ja manuaaliseen kopiointiin liittyvät inhimilliset virheet sataprosenttisesti.

Lopullisena varmistuksena arkkitehtuuri pakottaa Hookit suorittamaan validointimatemaattikkaa datan siirroksien yhteydessä. Vaikka "Ympäristön Allekirjoitukset" ovatkin metadatana käypiä, V2:ssa ensisijainen luottamus annetaan deterministiselle CPU-koodille, ei agentin deklaratiivisille väitteille luotettavuudesta.

**Jäännösriski**: Automaattisen Pydantic-validoinnin ansiosta kopiointiin ja siirtoon (in-transit error) liittyvä inhimillisen virheen riski on eliminoitu kokonaan. Tyyppitarkastukset ja JSON-validointi eivät kuitenkaan takaa agenttien loogisten tai kielellisten tulkintaerojen poistumista. Tuomari-agentti kirjaa loogiset ja tulkinnalliset erot edelleen Systeemiseksi Epävarmuudeksi lopulliseen XAI-raporttiin.

#### **5.2.5 Riski: Agenttien kognitiivinen ylikuormitus ja käyttäytymisen inversio**

**Riskin kuvaus**: Pääarviointikehotteen analyysi tunnistaa kriittisen pullonkaulan, joka johtuu tiettyjen agenttien kohtuuttomasta kognitiivisesta kuormasta. Erityisesti Prosessiauditoija ja Tuomari-agentti ovat arkkitehtonisesti ylikuormitettuja. Niiden on koostettava koko dataketju ja sovellettava subjektiivisia holistisia sääntöjä. Tämä kasvattaa käsiteltävän kontekstin laajuuden (engl. *context width*) ja pituuden äärimmilleen. Tutkimukset osoittavat, että tehtävän monimutkaisuus (Shen ym. 2023\) sekä monimutkaisuuden ja kontekstin pituuden yhteisvaikutus heikentävät kielimallien suorituskykyä ja ohjeiden noudattamista (*instruction following*) merkittävästi (Wu ym. 2024). Tämän riskin vakavin seuraus ei ole satunnainen virhe, vaan käyttäytymisen inversio. Tutkimuksissa, joissa mallien kognitiivista kuormitusta on kasvatettu monimutkaisilla tehtävillä, mallien on havaittu hylkäävän monimutkaiset, normatiiviset (esim. oikeudenmukaisuus) ohjeet ja siirtyvän yksinkertaisempaan, rationaaliseen maksimointiin (Kirshner ym. 2025). "Kognitiiviselle Kvoorumille" tämä tarkoittaa, että ylikuormitettu Tuomari-agentti voi epäonnistua kaltaisten monimutkaisten, subjektiivisten sääntöjen soveltamisessa ja oikaista yksinkertaisempiin, mutta virheellisiin, ratkaisuihin. Tämä uhkaa suoraan koko järjestelmän pätevyysa.

**Hallintamekanismi**: Lyhyellä aikavälillä riskiä hallitaan pakollisella HITL-valvonnalla ja XAI-raportoinnilla (Luku 2.4.4). Lisäksi järjestelmään on implementoitu aktiivinen huomionhallintamekanismi: "Kontekstin Segmentointi ja Fokusointi". Tämä pakottaa Tuomari-agentin soveltamaan 'System 2 Attention' \-periaatetta (Weston & Sukhbaatar 2023\) luomalla tietoisesti erilliset Fokus- (keskeiset todisteet/konfliktit) ja Kohina-listat (irrelevantti data). Synteesi perustuu ainoastaan Fokus-listaan. Tämä pyrkii vähentämään irrelevantin informaation aiheuttamaa häiriötä ja auttaa agenttia keskittymään kriittisimpiin todisteisiin ja konflikteihin, mikä vähentää käyttäytymisen inversion riskiä. Pitkällä aikavälillä ratkaisu edellyttää arkkitehtuurin optimointia (Luku 4.3.2) tai tehtävien pilkkomista pienempiin osiin

**Jäännösriski**: Riski on korkea nykyisessä arkkitehtuurissa ja riippuvainen käytettyjen yleiskäyttöisten tekoälymallien kyvykkyydestä hallita monimutkaisuutta.

### **5.3 Operatiiviset, Eettiset ja Teknologiset Riskit – Järjestelmä Käytännössä**

#### **5.3.1 Riski: Automaatioharha ja Ihmisvalvonnan Taakka**

**Riskin kuvaus**: Ihmisvalvoja (HITL) on altis automaatioharhalle – taipumukselle luottaa epäkriittisesti järjestelmän tuotokseen (Parasuraman & Riley 1997). Mitä kehittyneempi järjestelmä, sitä suurempi riski on, että ihmisvalvoja alisuoriutuu.

**Hallintamekanismi**: Riskiä torjutaan osallistavalla raportoinnilla (Luku 2.5.4). Raporttipohja ei ole passiivinen tiedonanto, vaan se pakottaa ihmisvalvojan aktiiviseen kognitiiviseen työhön. XAI-Raportoija generoi "Kriittisiä Auditointikysymyksiä", erityisesti koskien agenttien välisiä erimielisyyksiä (JEM), joihin ihmisen on otettava kantaa ("HITL-VASTAUS VAADITAAN"). Tämä vähentää taipumusta hyväksyä raportti kritiikittömästi.

**Jäännösriski**: Automaatioharha on syvälle juurtunut piirre. Kuormittunut varmistaja voi ohittaa varoitussignaalit ja kysymykset. Ihminen on samanaikaisesti järjestelmän tärkein varmistus ja merkittävin haavoittuvuus.

#### **5.3.2 Riski: Strategiset ja Eettiset Uhat**

**Riskin kuvaus (Metodologinen vesittyminen)**: Organisaatiot saattavat kustannussyistä jättää holistisen tason pois. Tällainen toteutuksen puutteellisuus (Durlak & DuPre 2008\) tuhoaisi järjestelmän validiteetin.

**Riskin kuvaus (Käyttötarkoituksen laajentuminen)**: Riski on, että työkalu muuttuu valvontainstrumentiksi (engl. *function creep*) (Koops 2021; AI Now Institute 2021). Järjestelmän tuottama ”kognitiivinen jälki” on arkaluonteista dataa (Weidinger ym. 2021). **Hallintamekanismit**: Vaativat hallinnollisia ratkaisuja (governance) ja teknisiä kontrolleja.

* **Eettiset riskit**: Kriitikko-agentti tunnistaa eettiset laiminlyönnit.

* **Vesittyminen**: Sitovat käyttöönottomallit, jotka vaativat täyden hybridiprosessin käyttöä korkean panoksen arvioinneissa.

* **Valvonta**: Eettiset säännöt, kuten kielto käyttää tuloksia ainoana perustana korkean panoksen päätöksille ja arvioitavan oikeus dataansa.

**Jäännösriski**: Teknologia ei estä väärinkäyttöä. Ilman vahvaa hallintamallia organisaatiot voivat käyttää työkalua väärin.

#### **5.3.3 Riski: Teknologiset tietoturvauhat (OWASP Top 10 for LLMs)**

**Riskin kuvaus**: Järjestelmä on altis yleisille LLM-tietoturvariskeille (OWASP Foundation 2025f). **Hallintamekanismi**: Monikerroksinen puolustusstrategia (DiD) (Luku 2.6):

* **Tekninen Kontrollikerros**: Vartija-agentti (syötteiden puhdistus, anonymisointi) (LLM01:2025, LLM02:2025).

* **Behavioraalinen Kontrollikerros**: Kognitiivinen Palomuuri (LLM06:2025).

* **Hallinnollinen Kontrollikerros**: HITL (joka torjuu useita riskejä, kuten automaatioharhaa).

Tulevaisuudessa siirrytään perustuslailliseen tekoälyyn (CAI) (Bai ym. 2022). **Jäännösriski**: Nykyinen kehotepohjainen Kognitiivinen Palomuuri on hauras (Luku 2.5.1).

*Taulukko 6\. Keskeisimmät OWASP Top 10 for LLMs –riskit ja torjuntamekanismit.*

| OWASP-riski (2025) | Kuvaus viitekehyksen kontekstissa | Ensisijainen torjuntamekanismi |
| :---- | :---- | :---- |
| **LLM01: Prompt Injection** | Käyttäjä upottaa dataan piilotettuja komentoja manipuloidakseen Kvoorumia (OWASP Foundation 2025a). | Vartija-agentin suorittama syötteiden puhdistus ja aktiivinen luokittelu. |
| **LLM02: Sensitive Information Disclosure** | Kvoorum paljastaa tahattomasti arkaluonteista tietoa (esim. PII). | Vartija-agentin suorittama automaattinen datan anonymisointi. |
| **LLM03: Supply Chain Vulnerabilities** | Käytetyt ulkoiset yleiskäyttöiset tekoälymallit sisältävät haavoittuvuuksia tai muuttuvat (malliajautuminen). | Muodolliset LLMOps-käytännöt, jatkuva regressiotestaus. |
| **LLM04: Data and Model Poisoning** | Hyökkääjä manipuloi dataa, jota käytetään tislatun mallin (Järjestelmä 1\) hienosäädössä. | Opetusdatana käytetään ainoastaan ihmisen validoimaa (HITL) dataa. |
| **LLM05: Improper Output Handling** | Järjestelmä välittää käsittelemättömän LLM-tuotoksen eteenpäin. | Systemaattinen tulosteen koodaus ja validointi. |
| **LLM06: Excessive Agency** | Agentit ylittävät niille määritellyt valtuudet. | Kognitiivinen Palomuuri sekä agenttien tekninen eristäminen. |
| **LLM08: Vector and Embedding Weaknesses** | Hyökkääjä manipuloi RAG-arkkitehtuuria.Tämän kontrollin puuttuminen on merkittävä tekninen ja metodologinen riski. | Tunnettu rajoite prototyypissä: Vartija-agentin metodologinen lokikirjaus, joka varoittaa puuttuvasta suojauksesta. (Huom: Visiona on aktiivinen ”Upotusten Eheyden Tarkistus”, mutta nykyinen toteutus ei sisällä geometrista poikkeamien havaitsemista, jättäen riskin teknisesti hallitsemattomaksi) (OWASP Foundation 2025e). |
| **LLM09: Misinformation** | Järjestelmä tuottaa virheellistä mutta vakuuttavaa tietoa, johon ihmisvalvoja luottaa (Automaatioharha). | Ihmisvalvonnan (HITL) prosessi ja Tuomarin XAI-rooli. |
| **LLM10: Unbounded Consumption** | Hyökkääjä kuormittaa järjestelmää resurssi-intensiivisillä pyynnöillä. | Teknisen tason käytön rajoittaminen (rate limiting) (OWASP Foundation 2025g). |

## **Luku 6: Johtopäätökset ja Tutkimusagenda**

Tässä artikkelissa on esitetty uusi teoreettinen viitekehys, hybridirubriikki, ja sen operatiivinen malli, Kognitiivinen Kvoorum. Esitämme hypoteesin, että tämä kaksitasoinen arkkitehtuuri voi tarjota perinteisiä menetelmiä luotettavamman (korkeampi reliabiliteetti) ja pätevämmän (korkeampi pätevyys) tavan arvioida monimutkaista tekoälyosaamista. Tämä arkkitehtuuri toteutetaan käytännössä moniagenttisena Kognitiivisena kvoorumina ja sen perustana on Kahnemanin kaksoisprosessiteoria, mikä vahvistaa systemaattista ja auditoitavaa arviointiprosessia.

Tämän hypoteesin todentaminen edellyttää tulevaa empiiristä tutkimusta. Tämän vuoksi esitämme tutkimusagendan, jonka keskiössä on viitekehyksen ydinlupauksen systemaattinen validointi. Viitekehyksen arvo syntyy sen filosofiasta: luottamus rakennetaan auditoitavan päättelyprosessin kautta, joka hallitsee ”reliabiliteetin ja validiteetin paradoksia” (Luku 1.3).

### **6.1 Hypoteesin validoinnin ja jatkokehityksen edellytykset**

Hypoteesin testaaminen ja jatkokehitys edellyttävät siirtymistä kohti monimutkaisemman, kaksitasoisen järjestelmän hallintaa. Kriittisiä tekijöitä ovat:

1. **Holistisen tason ohjauksen hallinta**: Kognitiivisen Kvoorumin luotettava käyttö edellyttää kykyä hallita agenttien työnkulkua, minimoida viivettä ja optimoida kustannuksia (vrt. Anthropic 2025b; Mesenbrink ym. 2025).

2. **HITL-valvonnan kehittäminen validoinnin ytimenä**: Validiteetin arviointi nojaa ihmisvalvojan (HITL) kykyyn toimia tehokkaana valvojana ja ratkaista sisäiset jännitteet. Tämä edellyttää koulutusta ja työkaluja automaatioharhan tunnistamiseksi (Parasuraman & Riley 1997).

3. **Data-strategia ja hybridilogiikan tislauskyky**: Siirtymä (”Järjestelmä 1”) vaiheeseen on kriittistä skaalautuvuuden kannalta. Tämä edellyttää kykyä ”tislata” hybridirubriikin logiikka yhdelle mallille, mikä vaatii korkealaatuisen päättelydatan (”kognitiivisten jälkien”) keräämistä ja datatieteen osaamista.

### **6.2 Tutkimusagenda: Seuraavat vaiheet**

Ennen empiirisen tutkimusagendan toteuttamista on ehdottoman välttämätöntä hankkia eettinen ennakkoarviointi ja hyväksyntä asiaankuuluvalta tutkimuseettiseltä toimikunnalta noudattaen Suomessa ihmistieteiden tutkimusta koskevia kansallisia ohjeistuksia (Tutkimuseettinen neuvottelukunta TENK 2019).

Koska viitekehyksen toiminnallinen malli on toteutettu mutta empiirisesti testaamatta, viitekehykseltä puuttuu toistaiseksi empiirinen näyttö. Kuten luvussa 5.1.1 todetaan, sen arvo perustuu todentamattomaan hypoteesiin. Seuraava tutkimusagenda on ehdoton edellytys väitteiden todentamiseksi:

1. **Viitekehyksen ydinlupauksen todentaminen luotettavuustutkimuksella (kriittinen ja välitön ensisijainen tavoite).** Agenda jakautuu kahteen vaiheeseen:

   * **Ulkoisen validiteetin testaus (arvioijien välinen luotettavuus IRR)**: On välittömästi käynnistettävä vertaileva pilottitutkimus (n=50), joka mittaa Kognitiivisen Kvoorumin arvioitsijareliabiliteetin (IRR) suhteessa ihmisasiantuntijoihin käyttämällä Cohenin Kappa \-kerrointa (McHugh 2012\) ja Intra-Class Correlation (ICC) \-mittaria. Tutkimusasetelmassa:

     * **Aineisto:** Kerätään 50 autenttista tekoälyavusteista opiskelijatyötä (sis. keskusteluhistorian).

     * **Ihmisverrokki:** Kolme riippumatonta, sokoutettua ihmisarvioijaa pisteyttää työt Hybridirubriikilla (Cohenin Kappa).

     * **Kvoorum-ajo:** Sama aineisto syötetään Kognitiiviselle Kvoorumille (heterogeeninen konfiguraatio: GPT-4 & Claude 3.5).

     * **Analyysi:** Mitataan Kvoorumin ja ihmisten välinen vastaavuus sekä Kvoorumin sisäinen konsistenssi toistomittauksilla. Tämä vastaa kritiikkiin AI-arvioinnin stokastisuudesta.

   * **Holistisen validiteetin testaus (Goodhartin Laki)**: On mitattava kestävyyttä ”performatiivista reflektiota” (Cullen 2020\) vastaan. On suoritettava koe, jossa testataan ”Epäilyttävä Täydellisyys” \-heuristiikan kykyä erottaa aidot suoritukset optimoiduista (Strathern 1997).

2. **Arkkitehtuurin tehostaminen ja datastrategian priorisointi.** Käynnistetään rinnakkaisen orkestrointimallin pilotointi ja systemaattinen päättelydatan kerääminen. Tämä data mahdollistaa tulevaisuudessa tislatun mallin (”Järjestelmä 1”) kouluttamisen.

## **Lähdeluettelo**

* **Acemoglu, Daron & Restrepo, Pascual 2018\.** *The race between man and machine: Implications of technology for growth, factor shares, and employment*. American Economic Review, 108(6), s. 1488–1542. Saatavilla: [https://doi.org/10.1257/aer.20160696](https://doi.org/10.1257/aer.20160696).

* **Adadi, Amina & Berrada, Mohammed 2018\.** *Peeking inside the black-box: A survey on explainable artificial intelligence (XAI)*. IEEE Access, 6, s. 52138–52160. Saatavilla: [https://doi.org/10.1109/ACCESS.2018.2870052](https://doi.org/10.1109/ACCESS.2018.2870052).

* **AERA, APA & NCME 2014\.** *Standards for educational and psychological testing*. Washington, DC: American Educational Research Association. Saatavilla: [https://www.testingstandards.net/uploads/7/6/6/4/76643089/standards\_2014edition.pdf](https://www.testingstandards.net/uploads/7/6/6/4/76643089/standards_2014edition.pdf).

* **Agrawal, Ajay, Gans, Joshua & Goldfarb, Avi 2022\.** *Prediction machines: The simple economics of artificial intelligence*. Boston: Harvard Business Review Press.

* **Ahmad, Sultan ym. 2024\.** *A comprehensive review of retrieval-augmented generation (RAG): Key challenges and future directions*. arXiv preprint arXiv:2410.12837. Saatavilla: [https://doi.org/10.48550/arXiv.2410.12837](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2410.12837).

* **Ahuna, Kelly & Kiener, Michael 2025\.** *Beyond digital literacy: Cultivating “meta AI” skills in students and faculty*. Faculty Focus. Saatavilla: [https://www.facultyfocus.com/articles/teaching-with-technology-articles/beyond-digital-literacy-cultivating-meta-ai-skills-in-students-and-faculty/](https://www.facultyfocus.com/articles/teaching-with-technology-articles/beyond-digital-literacy-cultivating-meta-ai-skills-in-students-and-faculty/).

* **AIMultiple 2025\.** *15 Security Threats to LLM Agents (with Real-World Examples)*. Research AIMultiple. Saatavilla: [https://research.aimultiple.com/security-of-ai-agents/](https://research.aimultiple.com/security-of-ai-agents/).

* **AI Now Institute 2021\.** *A New AI Lexicon: Function Creep*. New York: AI Now Institute. Saatavilla: [https://ainowinstitute.org/publications/collection/a-new-ai-lexicon-function-creep](https://ainowinstitute.org/publications/collection/a-new-ai-lexicon-function-creep).

* **Anderson, Lorin W. & Krathwohl, David R. (toim.) 2001\.** *A taxonomy for learning, teaching, and assessing: A revision of Bloom’s taxonomy of educational objectives*. New York: Longman.

* **Anthropic 2025a.** *Constitutional classifiers*. Anthropic Policy & Research. Saatavilla: [https://www.anthropic.com/research/constitutional-classifiers](https://www.anthropic.com/research/constitutional-classifiers).

* **Anthropic 2025b.** *How we built our multi-agent research system*. Anthropic Engineering Blog. Saatavilla: [https://www.anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system).

* **Anthropic 2025c.** *Building effective agents*. Anthropic Research. Saatavilla: [https://www.anthropic.com/research/building-effective-agents](https://www.anthropic.com/research/building-effective-agents).

* **Arcuschin, Iván ym. 2025\.** *Chain-of-Thought Reasoning In The Wild Is Not Always Faithful*. arXiv preprint arXiv:2503.08679. Saatavilla: [https://doi.org/10.48550/arXiv.2503.08679](https://doi.org/10.48550/arXiv.2503.08679).

* **Aryan, Ali & Liu, Zhi 2025\.** *Causal Reflection with Language Models*. arXiv preprint arXiv:2508.04495. Saatavilla: [https://doi.org/10.48550/ARXIV.2508.04495](https://www.google.com/search?q=https://doi.org/10.48550/ARXIV.2508.04495).

* **Auzmor 2024\.** *How to measure the ROI of AI training programs*. Auzmor. Saatavilla: [https://auzmor.com/blog/measure-the-roi-of-ai-training-programs/](https://auzmor.com/blog/measure-the-roi-of-ai-training-programs/).

* **Bai, Yuntao ym. 2022\.** *Constitutional AI: Harmlessness from AI feedback*. arXiv preprint arXiv:2212.08073. Saatavilla: [https://doi.org/10.48550/arXiv.2212.08073](https://doi.org/10.48550/arXiv.2212.08073).

* **Bareinboim, Elias ym. 2022\.** *On Pearl's hierarchy and the foundations of causal inference*. Teoksessa Geffner, H., Dechter, R. & Halpern, J. (toim.) Probabilistic and causal inference: The works of Judea Pearl. New York: ACM. Saatavilla: [https://doi.org/10.1145/3501714.3501743](https://doi.org/10.1145/3501714.3501743).

* **Baume, David & Yorke, Mantz 2002\.** *The reliability of assessment by portfolio on a course to develop and accredit teachers in higher education*. Studies in Higher Education, 27(1), s. 7–25. Saatavilla: [https://doi.org/10.1080/03075070120099340](https://doi.org/10.1080/03075070120099340).

* **Bezanilla, María José ym. 2019\.** *Methodologies for teaching-learning in higher education and their relationship with student competences: A systematic review*. Educational Research Review, 27, s. 83–98. Saatavilla: [https://doi.org/10.1016/j.edurev.2019.01.004](https://www.google.com/search?q=https://doi.org/10.1016/j.edurev.2019.01.004).

* **Biggs, John B. & Collis, Kevin F. 1982\.** *Evaluating the quality of learning: The SOLO taxonomy (Structure of the Observed Learning Outcome)*. New York: Academic Press.

* **Borsboom, Denny, Mellenbergh, Gideon J. & van Heerden, Jaap 2004\.** *The concept of validity*. Psychological Review, 111(4), s. 1061–1071. Saatavilla: [https://doi.org/10.1037/0033-295X.111.4.1061](https://doi.org/10.1037/0033-295X.111.4.1061).

* **Boussioux, Leonard 2025\.** *Revolutionize quality assurance with AI*. Mareana. Saatavilla: [https://mareana.com/whitepaper/qa-playbook/](https://mareana.com/whitepaper/qa-playbook/).

* **Brennan, Robert L. 2001\.** *Generalizability theory*. New York: Springer.

* **Brooks, Frederick P. 1987\.** *No silver bullet: Essence and accidents of software engineering*. Computer, 20(4), s. 10–19. Saatavilla: [https://doi.org/10.1109/MC.1987.1663532](https://doi.org/10.1109/MC.1987.1663532).

* **Bulut, Okan ym. 2024\.** *The Rise of Artificial Intelligence in Educational Measurement: Opportunities and Ethical Challenges*. Chinese/English Journal of Educational Measurement and Evaluation, 5(3). Saatavilla: [https://doi.org/10.59863/MIQL7785](https://doi.org/10.59863/MIQL7785).

* **Carolus, Angela ym. 2023\.** *MAILS \- Meta AI literacy scale: Development and testing of an AI literacy questionnaire*. arXiv preprint arXiv:2302.09319. Saatavilla: [https://doi.org/10.48550/arXiv.2302.09319](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2302.09319).

* **Cemri, M. ym. 2025\.** *Why do multi-agent LLM systems fail?* arXiv preprint arXiv:2503.13657. Saatavilla: [https://doi.org/10.48550/arXiv.2503.13657](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2503.13657).

* **Center for Innovative Teaching & Learning 2025\.** *Authentic assessment*. Indiana University Bloomington. Saatavilla: [https://citl.indiana.edu/teaching-resources/assessing-student-learning/authentic-assessment/index.html](https://citl.indiana.edu/teaching-resources/assessing-student-learning/authentic-assessment/index.html).

* **Cheng, Peter C-H. 2001\.** *Scientific discovery, computational models of*. Teoksessa Smelser, N. J. & Baltes, P. B. (toim.) International encyclopedia of the social & behavioral sciences. Amsterdam: Elsevier. Saatavilla: [https://doi.org/10.1016/B978-0-08-097086-8.43085-0](https://www.google.com/search?q=https://doi.org/10.1016/B978-0-08-097086-8.43085-0).

* **Cheng, Peter 2021\.** *Competence assessment by stimulus matching: an application of GOMS to assess chunks in memory*. Proceedings of the 19th International Conference on Cognitive Modelling. Saatavilla: [https://cidlab.com/files/smp/pb/pb-2021.pdf](https://cidlab.com/files/smp/pb/pb-2021.pdf).

* **Chi, Hao ym. 2024\.** *Unveiling causal reasoning in large language models: Reality or mirage?* Advances in Neural Information Processing Systems, 37, s. 96640–96670. Saatavilla: [https://doi.org/10.48550/arXiv.2506.21215](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2506.21215).

* **CISA 2016\.** *Defense in depth*. Cybersecurity and Infrastructure Security Agency. Saatavilla: [https://www.cisa.gov/sites/default/files/recommended\_practices/NCCIC\_ICS-CERT\_Defense\_in\_Depth\_2016\_S508C.pdf](https://www.cisa.gov/sites/default/files/recommended_practices/NCCIC_ICS-CERT_Defense_in_Depth_2016_S508C.pdf).

* **Cohen, Ronald Jay, Swerdlik, Mark E. & Phillips, Sturman M. 1996\.** *Psychological testing and assessment: An introduction to tests and measurement*. 3\. painos. Mountain View: Mayfield Publishing Company.

* **Creswell, Antonia ym. 2024\.** *Reducing post-hoc rationalization in large language models*. Findings of the Association for Computational Linguistics: ACL 2024, s. 14757–14771. Saatavilla: [https://doi.org/10.18653/v1/2024.findings-acl.867](https://www.google.com/search?q=https://doi.org/10.18653/v1/2024.findings-acl.867).

* **Crusius, Timothy W. & Channell, Carolyn E. 2003\.** *The aims of argument: A text and reader*. 4\. painos. New York: McGraw-Hill.

* **Cullen, Michael J. 2020\.** *Faking in high-stakes selection: A call to integrate empirical research and applied practice*. International Journal of Selection and Assessment, 28(3), s. 223–226. Saatavilla: [https://doi.org/10.1111/ijsa.12289](https://www.google.com/search?q=https://doi.org/10.1111/ijsa.12289).

* **D'Angelo, Matt 2025\.** *AI safety vs AI security in LLM applications: What teams must know*. promptfoo. Saatavilla: [https://www.promptfoo.dev/blog/ai-safety-vs-security/](https://www.promptfoo.dev/blog/ai-safety-vs-security/).

* **David, Jane L. 2019\.** *15 reasons why standardized tests are problematic*. ASCD Blog. Saatavilla: [https://www.ascd.org/blogs/15-reasons-why-standardized-tests-are-problematic](https://www.ascd.org/blogs/15-reasons-why-standardized-tests-are-problematic).

* **de Bruin, Anique B. H., van Merriënboer, Jeroen J. G. & van Gog, Tamara 2023\.** *The role of cognitive effort in fostering the acquisition of complex cognitive skills*. Teoksessa Sweller, J., van Merriënboer, J. J. G. & Paas, F. (toim.) Cognitive load theory. Cambridge: Cambridge University Press. Saatavilla: [https://doi.org/10.1017/9781009403718.011](https://www.google.com/search?q=https://doi.org/10.1017/9781009403718.011).

* **Denning, Dorothy E. & Denning, Peter J. 1977\.** *Certification of programs for secure information flow*. Communications of the ACM, 20(7), s. 504–513. Saatavilla: [https://doi.org/10.1145/359636.359712](https://doi.org/10.1145/359636.359712).

* **Der Kiureghian, Armen & Ditlevsen, Ove 2009\.** *Aleatory or epistemic? Does it matter?* Structural Safety, 31(2), s. 105–112. Saatavilla: [https://doi.org/10.1016/j.strusafe.2008.06.020](https://doi.org/10.1016/j.strusafe.2008.06.020).

* **Disco 2024\.** *How to assess the ROI of AI-driven upskilling initiatives*. Disco. Saatavilla: [https://www.disco.co/blog/how-to-assess-the-roi-of-ai-driven-upskilling-initiatives](https://www.disco.co/blog/how-to-assess-the-roi-of-ai-driven-upskilling-initiatives).

* **Displayr 2024\.** *Discover the 5 best AI tools for qualitative data analysis*. Displayr. Saatavilla: [https://www.displayr.com/discover-the-5-best-ai-tools-for-qualitative-data-analysis/](https://www.displayr.com/discover-the-5-best-ai-tools-for-qualitative-data-analysis/).

* **Dreyfus, Stuart E. & Dreyfus, Hubert L. 1980\.** *A Five-Stage Model of the Mental Activities Involved in Directed Skill Acquisition*. California Univ Berkeley Operations Research Center. Saatavilla: [https://apps.dtic.mil/sti/pdfs/ADA084551.pdf](https://apps.dtic.mil/sti/pdfs/ADA084551.pdf).

* **Du, Yilun ym. 2023\.** *Improving factuality and reasoning in language models through multiagent debate*. arXiv preprint arXiv:2305.14325. Saatavilla: [https://doi.org/10.48550/arXiv.2305.14325](https://doi.org/10.48550/arXiv.2305.14325).

* **Dufner, Michael ym. 2019\.** *Self-enhancement and psychological adjustment: A meta-analytic review*. Personality and Social Psychology Review, 23(1), s. 48–72. Saatavilla: [https://doi.org/10.1177/1088868318756467](https://doi.org/10.1177/1088868318756467).

* **Duhem, Pierre 1906\.** *La théorie physique: son objet et sa structure*. Paris: Chevalier & Rivière.

* **Durlak, Joseph A. & DuPre, Elizabeth P. 2008\.** *Implementation matters: A review of research on the influence of implementation on program outcomes*. American Journal of Community Psychology, 41(3–4), s. 327–350. Saatavilla: [https://doi.org/10.1007/s10464-008-9165-0](https://doi.org/10.1007/s10464-008-9165-0).

* **Dworkin, Ronald 1986\.** *Law's empire*. Cambridge: Harvard University Press. Saatavilla: [https://plato.stanford.edu/entries/legal-positivism/](https://plato.stanford.edu/entries/legal-positivism/).

* **Eloundou, Tyna ym. 2023\.** *GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models*. arXiv preprint arXiv:2303.10130. Saatavilla: [https://doi.org/10.48550/arXiv.2303.10130](https://doi.org/10.48550/arXiv.2303.10130).

* **Euroopan komissio 2024a.** *The AI Act*. Bryssel: Euroopan komissio. Saatavilla: [https://artificialintelligenceact.eu/article/14/](https://artificialintelligenceact.eu/article/14/).

* **Euroopan komission korkean tason asiantuntijaryhmä 2019\.** *Ethics guidelines for trustworthy AI*. Bryssel: Euroopan komissio. Saatavilla: [https://digital-strategy.ec.europa.eu/en/library/ethics-guidelines-for-trustworthy-ai](https://digital-strategy.ec.europa.eu/en/library/ethics-guidelines-for-trustworthy-ai).

* **Euroopan parlamentti & Euroopan unionin neuvosto 2024\.** *Euroopan parlamentin ja neuvoston asetus (EU) 2024/1689 tekoälyä koskevista yhdenmukaistetuista säännöistä (tekoälysäädös)*. Euroopan unionin virallinen lehti, L, 2024/1689.

* **Evans, Jonathan St. B. T. & Stanovich, Keith E. 2013\.** *Dual-process theories of higher cognition: Advancing the debate*. Perspectives on Psychological Science, 8(3), s. 223–241. Saatavilla: [https://doi.org/10.1177/1745691612460685](https://doi.org/10.1177/1745691612460685).

* **Embretson, Susan E. & Reise, Steven P. 2000\.** *Item response theory for psychologists*. Mahwah: Lawrence Erlbaum Associates.

* **FairTest 2012\.** *The limits of standardized tests for diagnosing and assisting student learning*. FairTest. Saatavilla: [https://fairtest.org/limits-standardized-tests-diagnosing-and-assisting/](https://fairtest.org/limits-standardized-tests-diagnosing-and-assisting/).

* **Federiakin, Denis ym. 2024\.** *Prompt engineering: A new skill for the future of work*. Procedia Computer Science, 231, s. 401–409. Saatavilla: [https://doi.org/10.1016/j.procs.2023.12.233](https://www.google.com/search?q=https://doi.org/10.1016/j.procs.2023.12.233).

* **Festinger, Leon 1957\.** *A theory of cognitive dissonance*. Stanford: Stanford University Press.

* **Flavell, John H. 1979\.** *Metacognition and cognitive monitoring: A new area of cognitive-developmental inquiry*. American Psychologist, 34(10), s. 906–911. Saatavilla: [https://doi.org/10.1037/0003-066X.34.10.906](https://doi.org/10.1037/0003-066X.34.10.906).

* **Fügener, Andreas, Walzner, Daniel D. & Gupta, Alok 2025\.** *Roles of Artificial Intelligence in Collaboration with Humans: Automation, Augmentation, and the Future of Work*. Management Science. Saatavilla: [https://doi.org/10.1287/mnsc.2024.05684](https://www.google.com/search?q=https://doi.org/10.1287/mnsc.2024.05684).

* **Ganascia, Jean-Gabriel 2017\.** *A Popperian falsification of artificial intelligence \- Lighthill*. arXiv preprint arXiv:1704.08111. Saatavilla: [https://doi.org/10.48550/arXiv.1704.08111](https://doi.org/10.48550/arXiv.1704.08111).

* **Ganguli, Deep ym. 2022\.** *Red teaming language models to reduce harms: Methods, scaling behaviors, and lessons learned*. arXiv preprint arXiv:2209.07858. Saatavilla: [https://doi.org/10.48550/arXiv.2209.07858](https://doi.org/10.48550/arXiv.2209.07858).

* **Gao, Luyu ym. 2022\.** *Precise zero-shot dense retrieval without relevance labels*. arXiv preprint arXiv:2212.10496. Saatavilla: [https://doi.org/10.48550/arXiv.2212.10496](https://doi.org/10.48550/arXiv.2212.10496).

* **Goffman, Erving 1959\.** *The presentation of self in everyday life*. New York: Doubleday.

* **Goodfellow, Ian J. ym. 2014\.** *Generative adversarial networks*. Advances in Neural Information Processing Systems, 27, s. 2672–2680. Saatavilla: [https://doi.org/10.48550/arXiv.1406.2661](https://doi.org/10.48550/arXiv.1406.2661).

* **Grice, H. P. 1975\.** *Logic and conversation*. Teoksessa Cole, P. & Morgan, J. L. (toim.) Syntax and semantics: Vol. 3. Speech acts. New York: Academic Press, s. 41–58.

* **Google DeepMind 2025a.** *Gemini 3 Pro Model Card*. Saatavilla: [https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf).

* **Google DeepMind 2025b.** *Gemini 3 Pro Model Evaluation*. Saatavilla: [https://storage.googleapis.com/deepmind-media/gemini/gemini\_3\_pro\_model\_evaluation.pdf](https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_model_evaluation.pdf).

* **Google DeepMind 2025c.** *Gemini 3: A new era of intelligence*. Google Blog. Saatavilla: [https://blog.google/products/gemini/gemini-3/](https://blog.google/products/gemini/gemini-3/).

* **Greshake, Kai ym. 2023\.** *Not what you’ve signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection*. arXiv preprint arXiv:2302.12173. Saatavilla: [https://doi.org/10.48550/arXiv.2302.12173](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2302.12173).

* **Guo, Taicheng ym. 2024\.** *Large language model based multi-agents: A survey of progress and challenges*. IJCAI 2024\. Saatavilla: [https://doi.org/10.24963/ijcai.2024/890](https://doi.org/10.24963/ijcai.2024/890).

* **Halpern, Diane F. 2014\.** *Thought and knowledge: An introduction to critical thinking*. 5\. painos. New York: Psychology Press. Saatavilla: [https://doi.org/10.4324/9781315885278](https://doi.org/10.4324/9781315885278).

* **Hazan, Eric ym. 2024\.** *A new future of work: The race to deploy AI and raise skills*. McKinsey Global Institute. Saatavilla: [https://www.mckinsey.com/mgi/our-research/a-new-future-of-work-the-race-to-deploy-ai-and-raise-skills-in-europe-and-beyond](https://www.mckinsey.com/mgi/our-research/a-new-future-of-work-the-race-to-deploy-ai-and-raise-skills-in-europe-and-beyond).

* **Hevner, Alan R., March, Salvatore T., Park, Jinsoo & Ram, Sudha 2004\.** *Design Science in Information Systems Research*. MIS Quarterly, 28(1), s. 75–105. Saatavilla: [https://doi.org/10.2307/25148625](https://doi.org/10.2307/25148625).

* **Hinton, Geoffrey, Vinyals, Oriol & Dean, Jeffrey 2015\.** *Distilling the knowledge in a neural network*. arXiv preprint arXiv:1503.02531. Saatavilla: [https://doi.org/10.48550/arXiv.1503.02531](https://doi.org/10.48550/arXiv.1503.02531).

* **Huang, Lei ym. 2023\.** *A Survey on Hallucination in Large Language Models*. ACM Transactions on Information Systems. Saatavilla: [https://doi.org/10.1145/3703155](https://doi.org/10.1145/3703155).

* **Hüllermeier, Eyke & Waegeman, Willem 2021\.** *Aleatoric and epistemic uncertainty in machine learning*. Machine Learning, 110, s. 457–506. Saatavilla: [https://doi.org/10.1007/s10994-021-05946-3](https://doi.org/10.1007/s10994-021-05946-3).

* **Hume, David 1739\.** *A Treatise of Human Nature*. Lontoo: John Noon. Saatavilla: [https://archive.org/details/treatiseofhumann01hume](https://archive.org/details/treatiseofhumann01hume).

* **Hyland, Ken 2005\.** *Metadiscourse: Exploring interaction in writing*. Lontoo: Continuum.

* **Inan, Hakan ym. 2023\.** *Llama Guard: LLM-based Input-Output Safeguard*. arXiv preprint arXiv:2312.06674. Saatavilla: [https://doi.org/10.48550/arXiv.2312.06674](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2312.06674).

* **ISACA 2025\.** *How to measure and prove the value of your AI investments*. ISACA Newsletter, Volume 5\. Saatavilla: [https://www.isaca.org/resources/news-and-trends/newsletters/atisaca/2025/volume-5/how-to-measure-and-prove-the-value-of-your-ai-investments](https://www.isaca.org/resources/news-and-trends/newsletters/atisaca/2025/volume-5/how-to-measure-and-prove-the-value-of-your-ai-investments).

* **ISO/IEC 2023\.** *Systems and software quality models (ISO/IEC 25010:2023)*. Geneve: International Organization for Standardization.

* **Jacobs, Rick, Kafry, Dalia & Zedeck, Sheldon 1980\.** *Expectations of behaviorally anchored rating scales*. Personnel Psychology, 33(3), s. 595–640. Saatavilla: [https://doi.org/10.1111/j.1744-6570.1980.tb00486.x](https://doi.org/10.1111/j.1744-6570.1980.tb00486.x).

* **Jacovi, Alon & Goldberg, Yoav 2020\.** *Towards faithfully interpretable NLP systems*. Proceedings of ACL 2020, s. 4198–4205. Saatavilla: [https://doi.org/10.18653/v1/2020.acl-main.385](https://doi.org/10.18653/v1/2020.acl-main.385).

* **Jagerman, Rolf ym. 2023\.** *Query expansion by prompting large language models*. arXiv preprint arXiv:2305.03653. Saatavilla: [https://doi.org/10.48550/arXiv.2305.03653](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2305.03653).

* **Jia, Yihao ym. 2025\.** *A Critical Evaluation of Defenses against Prompt Injection Attacks*. arXiv preprint arXiv:2505.18333. Saatavilla: [https://doi.org/10.48550/arXiv.2505.18333](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2505.18333).

* **Johnson, R. Burke & Onwuegbuzie, Anthony J. 2004\.** *Mixed methods research: A research paradigm whose time has come*. Educational Researcher, 33(7), s. 14–26. Saatavilla: [https://doi.org/10.3102/0013189X033007014](https://doi.org/10.3102/0013189X033007014).

* **Jonsson, Anders & Svingby, Gunilla 2007\.** *The use of scoring rubrics: Reliability, validity and educational consequences*. Educational Research Review, 2(2), s. 130–144. Saatavilla: [https://doi.org/10.1016/j.edurev.2007.05.002](https://doi.org/10.1016/j.edurev.2007.05.002).

* **Kahneman, Daniel 2011\.** *Thinking, fast and slow*. New York: Farrar, Straus and Giroux.

* **Kiciman, Emre ym. 2023\.** *Causal reasoning and large language models*. arXiv preprint arXiv:2305.00050. Saatavilla: [https://doi.org/10.48550/arXiv.2305.00050](https://doi.org/10.48550/arXiv.2305.00050).

* **Kim, Dong-Gi ym. 2022\.** *Assessing non-technical skills in medical students (BARS)*. Teaching and Learning in Medicine, 35(3), s. 310–319. Saatavilla: [https://doi.org/10.1080/10872981.2022.2070940](https://www.google.com/search?q=https://doi.org/10.1080/10872981.2022.2070940).

* **Kindervag, John 2010\.** *Build Security Into Your Network's DNA: The Zero Trust Network Architecture*. Cambridge: Forrester Research.

* **Kinicki, Angelo J. ym. 1985\.** *Behaviorally anchored rating scales vs. summated rating scales*. Educational and Psychological Measurement, 45(3), s. 535–549. Saatavilla: [https://doi.org/10.1177/001316448504500310](https://doi.org/10.1177/001316448504500310).

* **Kirshner, Stuart, Klaben, Ben & Dobbe, Sam 2025\.** *Instruction-Following: The Truth Is In There*. arXiv preprint arXiv:2511.07973. Saatavilla: [https://doi.org/10.48550/arXiv.2511.07973](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2511.07973).

* **Klein, Gary 2007\.** *Performing a Project Premortem*. Harvard Business Review, 85(9), s. 18–19.

* **Klieger, David M. ym. 2018\.** *Development of the Behaviorally Anchored Rating Scales*. ETS Research Report Series RR-18-24. Saatavilla: [https://doi.org/10.1002/ets2.12210](https://doi.org/10.1002/ets2.12210).

* **Koops, Bert-Jaap 2021\.** *The concept of function creep*. Law, Innovation and Technology, 13(1), s. 29–56. Saatavilla: [https://doi.org/10.1080/17579961.2021.1898299](https://doi.org/10.1080/17579961.2021.1898299).

* **Koretz, Daniel M. ym. 1994\.** *The Vermont portfolio assessment program: Findings and implications*. Educational Measurement, 13(3), s. 5–16. Saatavilla: [https://doi.org/10.1111/j.1745-3992.1994.tb00854.x](https://www.google.com/search?q=https://doi.org/10.1111/j.1745-3992.1994.tb00854.x).

* **Kreuzberger, Dominik, Kühl, Niklas & Hirschl, Sebastian 2023\.** *Machine learning operations (MLOps)*. IEEE Access, 11, s. 31866–31879. Saatavilla: [https://doi.org/10.1109/ACCESS.2023.3262138](https://doi.org/10.1109/ACCESS.2023.3262138).

* **Kruger, Justin & Dunning, David 1999\.** *Unskilled and unaware of it*. Journal of Personality and Social Psychology, 77(6), s. 1121–1134. Saatavilla: [https://doi.org/10.1037/0022-3514.77.6.1121](https://doi.org/10.1037/0022-3514.77.6.1121).

* **Lagnado, David A. & Sloman, Steven A. 2006\.** *Time as a guide to cause*. Journal of Experimental Psychology, 32(3), s. 451–460. Saatavilla: [https://doi.org/10.1037/0278-7393.32.3.451](https://doi.org/10.1037/0278-7393.32.3.451).

* **Lane, Suzanne 2013\.** *Validity evidence for assessments of higher-order thinking*. Journal of Educational Measurement, 50(4), s. 399–430. Saatavilla: [https://doi.org/10.1111/jedm.12028](https://www.google.com/search?q=https://doi.org/10.1111/jedm.12028).

* **Larson, Barbara Z. ym. 2024\.** *Critical thinking in the age of generative AI*. Academy of Management Learning & Education, 23(3). Saatavilla: [https://doi.org/10.5465/amle.2024.0338](https://www.google.com/search?q=https://doi.org/10.5465/amle.2024.0338).

* **LeCun, Yann 2022\.** *A path towards autonomous machine intelligence*. OpenReview. Saatavilla: [https://openreview.net/forum?id=BZ5a1r-kVsf](https://openreview.net/forum?id=BZ5a1r-kVsf).

* **Levashina, Julia & Morgeson, Frederick P. 2007\.** *Applicant faking on personality measures*. Academy of Management Review, 32(4), s. 1118–1136. Saatavilla: [https://doi.org/10.5465/amr.2007.26586083](https://www.google.com/search?q=https://doi.org/10.5465/amr.2007.26586083).

* **Levine, Edward L., Ash, Ronald A. & Bennett, Nathan 1988\.** *The "behavioral consistency" approach to job analysis*. HR Management Review, 8(3), s. 273–293. Saatavilla: [https://doi.org/10.1016/S1053-4822(98)90023-6](https://www.google.com/search?q=https://doi.org/10.1016/S1053-4822\(98\)90023-6).

* **Lewis, Patrick ym. 2020\.** *Retrieval-augmented generation for knowledge-intensive NLP tasks*. NeurIPS, 33, s. 9459–9474. Saatavilla: [https://doi.org/10.48550/arXiv.2005.11401](https://doi.org/10.48550/arXiv.2005.11401).

* **Li, Feng ym. 2025\.** *An assessment of human–AI interaction capability (critical thinking)*. Journal of Intelligence, 13(6), s. 62\. Saatavilla: [https://doi.org/10.3390/jintelligence13060062](https://www.google.com/search?q=https://doi.org/10.3390/jintelligence13060062).

* **Li, Zhikun ym. 2024\.** *PII-Bench: A benchmark for PII detection and anonymization*. arXiv preprint arXiv:2404.03893. Saatavilla: [https://doi.org/10.48550/arXiv.2404.03893](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2404.03893).

* **Liang, Tian-Shuo ym. 2023\.** *Encouraging divergent thinking in LLMs through multi-agent debate*. arXiv preprint arXiv:2305.19118. Saatavilla: [https://doi.org/10.48550/arXiv.2305.19118](https://doi.org/10.48550/arXiv.2305.19118).

* **Lippi, Marco & Torroni, Paolo 2016\.** *Argumentation mining: State of the art*. ACM Transactions on Internet Technology, 16(2), s. 1–25. Saatavilla: [https://doi.org/10.1145/2850417](https://doi.org/10.1145/2850417).

* **Lison, Pierre ym. 2021\.** *Anonymisation models for text data: State of the art*. arXiv preprint arXiv:2106.04631. Saatavilla: [https://doi.org/10.48550/arXiv.2106.04631](https://doi.org/10.48550/arXiv.2106.04631).

* **Liu, Nelson F. ym. 2024\.** *Lost in the middle: How language models use long contexts*. TACL, 12, s. 157–173. Saatavilla: [https://doi.org/10.1162/tacl\_a\_00638](https://doi.org/10.1162/tacl_a_00638).

* **Liu, Xiaogeng ym. 2024\.** *Automatic and universal prompt injection attacks*. arXiv preprint arXiv:2403.04957. Saatavilla: [https://doi.org/10.48550/arXiv.2403.04957](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2403.04957).

* **Liu, Yi ym. 2023\.** *Prompt injection attacks and defenses in LLMs: A survey*. arXiv preprint arXiv:2310.12815. Saatavilla: [https://doi.org/10.48550/arXiv.2310.12815](https://doi.org/10.48550/arXiv.2310.12815).

* **Luckin, Rosemary ym. 2017\.** *Towards artificial intelligence-based assessment systems*. Nature Human Behaviour, 1(3), 0028\. Saatavilla: [https://doi.org/10.1038/s41562-016-0028](https://doi.org/10.1038/s41562-016-0028).

* **Ma, Yubo ym. 2024\.** *Mitigating contextual information loss in RAG models through re-ranking*. arXiv preprint arXiv:2401.06427. Saatavilla: [https://doi.org/10.48550/arXiv.2401.06427](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2401.06427).

* **McHugh, Mary L. 2012\.** *Interrater reliability: the kappa statistic*. Biochemia Medica, 22(3), s. 276–282. Saatavilla: [https://doi.org/10.11613/BM.2012.031](https://doi.org/10.11613/BM.2012.031).

* **Mesenbrink, Hanna ym. 2025\.** *Orchestrated multi agents sustain accuracy under clinical-scale workloads*. medRxiv. Saatavilla: [https://doi.org/10.1101/2025.08.22.25334049](https://doi.org/10.1101/2025.08.22.25334049).

* **Mislevy, Robert J. 2003\.** *Substance and structure in assessment arguments*. Law, Probability and Risk, 2(4), s. 237–258. Saatavilla: [https://doi.org/10.1093/lpr/2.4.237](https://doi.org/10.1093/lpr/2.4.237).

* **Messick, Samuel J. 1989\.** *Validity*. Teoksessa Linn, R. L. (toim.) Educational measurement. 3\. painos. New York: Macmillan, s. 13–103.

* **Morgeson, Frederick P., Delaney-Klinger, Kelly & Hemingway, Monica A. 2007\.** *Job analysis to legal defensibility*. Teoksessa Koppes, L. L. (toim.) Historical perspectives in I/O psychology. Mahwah: LEA.

* **Moskal, Barbara M. 2000\.** *Scoring rubrics: What, when and how?* Practical Assessment, Research, and Evaluation, 7(3). Saatavilla: [https://doi.org/10.7275/a5vq-7q66](https://doi.org/10.7275/a5vq-7q66).

* **Nola, Robert & Sankey, Howard 2014\.** *Theories of scientific method: An introduction*. Lontoo: Routledge. Saatavilla: [https://doi.org/10.4324/9781315728666](https://www.google.com/search?q=https://doi.org/10.4324/9781315728666).

* **Nold, Herbert & Michel, Lukas 2022\.** *The Dunning-Kruger Effect on Organizational Agility*. Academy of Management Proceedings. Saatavilla: [https://doi.org/10.5465/AMBPP.2022.10365abstract](https://doi.org/10.5465/AMBPP.2022.10365abstract).

* **OECD 2024\.** *Artificial intelligence and the changing demand for skills*. OECD Publishing. Saatavilla: [https://doi.org/10.1787/88684e36-en](https://www.google.com/search?q=https://doi.org/10.1787/88684e36-en).

* **OpenAI 2024\.** *OpenAI o1 System Card*. OpenAI. Saatavilla: [https://openai.com/index/openai-o1-system-card/](https://openai.com/index/openai-o1-system-card/).

* **OWASP Foundation 2025a.** *LLM01:2025 Prompt Injection*. GenAI OWASP Top 10\. Saatavilla: [https://genai.owasp.org/llmrisk/llm01-prompt-injection/](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).

* **OWASP Foundation 2025b.** *LLM02:2025 Sensitive Information Disclosure*. GenAI OWASP Top 10\. Saatavilla: [https://genai.owasp.org/llm-top-10/](https://genai.owasp.org/llm-top-10/).

* **OWASP Foundation 2025c.** *LLM05:2025 Improper Output Handling*. GenAI OWASP Top 10\. Saatavilla: [https://genai.owasp.org/llm-top-10/](https://genai.owasp.org/llm-top-10/).

* **OWASP Foundation 2025d.** *LLM06:2025 Excessive Agency*. GenAI OWASP Top 10\. Saatavilla: [https://genai.owasp.org/llm-top-10/](https://genai.owasp.org/llm-top-10/).

* **OWASP Foundation 2025e.** *LLM08:2025 Vector and Embedding Weaknesses*. GenAI OWASP Top 10\. Saatavilla: [https://genai.owasp.org/llmrisk/llm08-vector-and-embedding-weaknesses/](https://genai.owasp.org/llmrisk/llm08-vector-and-embedding-weaknesses/).

* **OWASP Foundation 2025f.** *OWASP Top 10 for Gen AI*. GenAI OWASP Top 10\. Saatavilla: [https://genai.owasp.org/llm-top-10/](https://genai.owasp.org/llm-top-10/).

* **OWASP Foundation 2025g.** *LLM10:2025 Unbounded Consumption*. GenAI OWASP Top 10\. Saatavilla: [https://genai.owasp.org/llm-top-10/](https://genai.owasp.org/llm-top-10/).

* **OWASP Foundation s.a.** *Input Validation Cheat Sheet*. OWASP Cheat Sheet Series. Saatavilla: [https://cheatsheetseries.owasp.org/cheatsheets/Input\_Validation\_Cheat\_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html).

* **Parasuraman, Raja & Riley, Victor 1997\.** *Humans and automation: Use, misuse, disuse, abuse*. Human Factors, 39(2), s. 230–253. Saatavilla: [https://doi.org/10.1518/001872097778543886](https://doi.org/10.1518/001872097778543886).

* **Paulson, F. Leon, Paulson, Pearl R. & Meyer, Carol A. 1991\.** *What makes a portfolio a portfolio*. Educational Leadership, 48(5), s. 60–63.

* **Pearl, Judea 2009\.** *Causality: Models, reasoning, and inference*. 2\. painos. Cambridge: Cambridge University Press. Saatavilla: [https://doi.org/10.1017/CBO9780511803161](https://doi.org/10.1017/CBO9780511803161).

* **Peffers, Ken ym. 2007\.** *A Design Science Research Methodology*. Journal of Management Information Systems, 24(3), s. 45–77. Saatavilla: [https://doi.org/10.2753/MIS0742-1222240302](https://www.google.com/search?q=https://doi.org/10.2753/MIS0742-1222240302).

* **Perez, Ethan ym. 2022a.** *Red Teaming Language Models*. arXiv preprint arXiv:2209.07858. Saatavilla: [https://doi.org/10.48550/arXiv.2209.07858](https://doi.org/10.48550/arXiv.2209.07858).

* **Perez, Ethan ym. 2022b.** *Discovering Language Model Behaviors*. arXiv preprint arXiv:2212.09251. Saatavilla: [https://doi.org/10.48550/arXiv.2212.09251](https://doi.org/10.48550/arXiv.2212.09251).

* **Perrow, Charles 1984\.** *Normal accidents: Living with high-risk technologies*. Princeton: Princeton University Press.

* **Pfeifer, Karen 2025\.** *Humanity-in-the-loop: Human AI oversight*. Medium. Saatavilla: [https://medium.com/@karenpfeifer/humanity-in-the-loop-human-ai-oversight-is-an-imperative-50bdcc2688d8](https://medium.com/@karenpfeifer/humanity-in-the-loop-human-ai-oversight-is-an-imperative-50bdcc2688d8).

* **Polanyi, Michael 1966\.** *The tacit dimension*. Chicago: University of Chicago Press.

* **Pollitt, Alastair 2012\.** *The method of Adaptive Comparative Judgement*. Assessment in Education, 19(3), s. 281–300. Saatavilla: [https://doi.org/10.1080/0969594X.2012.665354](https://doi.org/10.1080/0969594X.2012.665354).

* **Popper, Karl 1934\.** *Logik der Forschung*. Vienna: Julius Springer.

* **PwC 2024\.** *AI jobs barometer*. PwC. Saatavilla: [https://www.pwc.com/gx/en/issues/artificial-intelligence/ai-jobs-barometer.html](https://www.pwc.com/gx/en/issues/artificial-intelligence/ai-jobs-barometer.html).

* **Quine, Willard Van Orman 1951\.** *Two dogmas of empiricism*. The Philosophical Review, 60(1), s. 20–43. Saatavilla: [https://doi.org/10.2307/2181906](https://doi.org/10.2307/2181906).

* **Raisch, Sebastian & Krakowski, Sebastian 2021\.** *Artificial intelligence and management*. Academy of Management Review, 46(1), s. 192–210. Saatavilla: [https://doi.org/10.5465/amr.2018.0072](https://doi.org/10.5465/amr.2018.0072).

* **Reinecke, Katharina & Gajos, Krzysztof Z. 2014\.** *Quantifying visual preferences around the world*. CHI 2014, s. 717–726. Saatavilla: [https://doi.org/10.1145/2556288.2557076](https://doi.org/10.1145/2556288.2557076).

* **Sadler, D. Royce 1989\.** *Formative assessment and the design of instructional systems*. Instructional Science, 18(2), s. 119–144. Saatavilla: [https://doi.org/10.1007/BF00117714](https://doi.org/10.1007/BF00117714).

* **Sagi, Omer & Rokach, Lior 2018\.** *Ensemble learning: A survey*. WIREs Data Mining Knowledge Discovery, 8(4). Saatavilla: [https://doi.org/10.1002/widm.1249](https://doi.org/10.1002/widm.1249).

* **Saito, Keisuke, Wachi, Akifumi & Akimoto, Youhei 2023\.** *Verbosity bias in preference labeling by LLMs*. arXiv preprint arXiv:2310.10864. Saatavilla: [https://doi.org/10.48550/arXiv.2310.10864](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2310.10864).

* **Saltzer, Jerome H. & Schroeder, Michael D. 1975\.** *The protection of information in computer systems*. Proceedings of the IEEE, 63(9), s. 1278–1308. Saatavilla: [https://doi.org/10.1109/PROC.1975.9939](https://doi.org/10.1109/PROC.1975.9939).

* **Sgaier, Sema K. ym. 2020\.** *The case for causal AI*. Stanford Social Innovation Review, 18(3), s. 50–55. Saatavilla: [https://doi.org/10.48558/KT81-SN73](https://www.google.com/search?q=https://doi.org/10.48558/KT81-SN73).

* **Shafiyeva, Ulviyya 2021\.** *Assessing Students' Minds: Developing Critical Thinking*. European Journal of Education, 4(2), s. 78–91. Saatavilla: [https://doi.org/10.26417/452bxv17s](https://www.google.com/search?q=https://doi.org/10.26417/452bxv17s).

* **Sharma, Mrinank ym. 2025\.** *Constitutional classifiers: Defending against universal jailbreaks*. arXiv preprint arXiv:2501.18837. Saatavilla: [https://doi.org/10.48550/arXiv.2501.18837](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2501.18837).

* **Shavelson, Richard J. 2010\.** *On the measurement of competency*. Empirical Research in Vocational Education and Training, 2(1), s. 41–63.

* **Shaffer, David Williamson, Collier, Wesley & Ruis, A. R. 2016\.** *A tutorial on Epistemic Network Analysis*. Journal of Learning Analytics, 3(3), s. 9–45. Saatavilla: [https://doi.org/10.18608/jla.2016.33.3](https://doi.org/10.18608/jla.2016.33.3).

* **Shavelson, Richard J. 2013\.** *On an approach to testing and modeling competence*. Educational Psychologist, 48(2), s. 73–86. Saatavilla: [https://doi.org/10.1080/00461520.2013.779483](https://doi.org/10.1080/00461520.2013.779483).

* **Shen, Yongliang ym. 2023\.** *Large Language Models as Tool Makers*. arXiv preprint arXiv:2305.17126. Saatavilla: [https://doi.org/10.48550/arXiv.2305.17126](https://doi.org/10.48550/arXiv.2305.17126).

* **Shinn, Noah ym. 2023\.** *Reflexion: an autonomous agent with dynamic memory*. arXiv preprint arXiv:2303.11366. Saatavilla: [https://doi.org/10.48550/arXiv.2303.11366](https://doi.org/10.48550/arXiv.2303.11366).

* **Shuster, Kurt ym. 2021\.** *Retrieval augmentation reduces hallucination in conversation*. arXiv preprint arXiv:2104.07567. Saatavilla: [https://doi.org/10.48550/arXiv.2104.07567](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2104.07567).

* **Silva, Bruno ym. 2025\.** *Development of MCA for Older Adults*. Journal of Clinical Medicine, 14(21), s. 7866\. Saatavilla: [https://doi.org/10.3390/jcm14217866](https://doi.org/10.3390/jcm14217866).

* **Skinner, B. F. 1957\.** *Verbal behavior*. New York: Appleton-Century-Crofts.

* **Smith, Patricia Cain & Kendall, Lorne M. 1963\.** *Retranslation of expectations (BARS)*. Journal of Applied Psychology, 47(2), s. 149–155. Saatavilla: [https://doi.org/10.1037/h0047060](https://doi.org/10.1037/h0047060).

* **Strathern, Marilyn 1997\.** *'Improving ratings': audit in the British university system*. European Review, 5(3), s. 305–321. Saatavilla: [https://doi.org/10.1002/(SICI)1234-981X(199707)5:3\<305::AID-EURO184\>3.0.CO;2-4](https://www.google.com/search?q=https://doi.org/10.1002/\(SICI\)1234-981X\(199707\)5:3%3C305::AID-EURO184%3E3.0.CO;2-4).

* **Stumborg, Michael F. ym. 2022\.** *Goodhart's law: Recognizing and mitigating the manipulation of measures*. CNA Occasional Paper. Saatavilla: [https://www.cna.org/reports/2022/09/Goodharts-Law-Recognizing-Mitigating-Manipulation-Measures-in-Analysis.pdf](https://www.cna.org/reports/2022/09/Goodharts-Law-Recognizing-Mitigating-Manipulation-Measures-in-Analysis.pdf).

* **Supianto, Arief Andy ym. 2023\.** *A systematic review of multi-agent systems in educational assessment*. Computers & Education: AI, 4\. Saatavilla: [https://doi.org/10.1016/j.caeai.2023.100135](https://doi.org/10.1016/j.caeai.2023.100135).

* **Suskie, Linda 2009\.** *Assessing student learning: A common sense guide*. 2\. painos. San Francisco: Jossey-Bass.

* **Talboy, Alisha & Fuller, Elizabeth 2023\.** *Large language models show humanlike cognitive biases*. arXiv preprint arXiv:2308.14343. Saatavilla: [https://doi.org/10.48550/arXiv.2308.14343](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2308.14343).

* **Tétard, Franck & Collan, Mikael 2009\.** *Lazy User Theory*. Proceedings of HICSS 2009\. Saatavilla: [https://doi.org/10.1109/HICSS.2009.290](https://www.google.com/search?q=https://doi.org/10.1109/HICSS.2009.290).

* **Toulmin, Stephen E. 2003\.** *The uses of argument*. Päivitetty painos. Cambridge: Cambridge University Press. Saatavilla: [https://doi.org/10.1017/CBO9780511802034](https://doi.org/10.1017/CBO9780511802034).

* **Towards AI 2025\.** *AI Sandbox in 2025*. Towards AI. Saatavilla: [https://pub.towardsai.net/ai-sandbox-in-2025-how-enterprises-and-governments-shape-ais-future-b41f0d267c4d](https://pub.towardsai.net/ai-sandbox-in-2025-how-enterprises-and-governments-shape-ais-future-b41f0d267c4d).

* **Trivedi, Harsh ym. 2024\.** *Interleaving retrieval with chain-of-thought reasoning*. arXiv preprint arXiv:2401.10133. Saatavilla: [https://doi.org/10.48550/arXiv.2401.10133](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2401.10133).

* **Turpin, Miles ym. 2023\.** *Language models don't always say what they think*. NeurIPS, 36, s. 21016–21033.

* **Turpin, Miles ym. 2025\.** *Executable counterfactuals*. arXiv preprint arXiv:2510.01539. Saatavilla: [https://doi.org/10.48550/arXiv.2510.01539](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2510.01539).

* **Tutkimuseettinen neuvottelukunta TENK 2019\.** *Ihmiseen kohdistuvan tutkimuksen eettiset periaatteet*. Helsinki: TENK. Saatavilla: [https://tenk.fi/sites/default/files/2021-01/Ihmistieteiden\_eettisen\_ennakkoarvioinnin\_ohje\_2020.pdf](https://tenk.fi/sites/default/files/2021-01/Ihmistieteiden_eettisen_ennakkoarvioinnin_ohje_2020.pdf).

* **Tversky, Amos & Kahneman, Daniel 1974\.** *Judgment under uncertainty: Heuristics and biases*. Science, 185(4157), s. 1124–1131. Saatavilla: [https://doi.org/10.1126/science.185.4157.1124](https://doi.org/10.1126/science.185.4157.1124).

* **W3C 2008\.** *Migrating to Unicode*. W3C I18n Activity. Saatavilla: [https://www.w3.org/International/articles/unicode-migration/](https://www.w3.org/International/articles/unicode-migration/).

* **Wachsmuth, Henning ym. 2017\.** *Computational argumentation quality assessment*. Proceedings of EACL 2017, s. 176–187. Saatavilla: [https://doi.org/10.18653/v1/E17-1017](https://doi.org/10.18653/v1/E17-1017).

* **Walton, Douglas N., Reed, Chris & Macagno, Fabrizio 2008\.** *Argumentation schemes*. Cambridge: Cambridge University Press. Saatavilla: [https://doi.org/10.1017/CBO9780511802034](https://doi.org/10.1017/CBO9780511802034).

* **Wang, Yuxia ym. 2023\.** *A survey on an authoritarian bias in LLMs*. arXiv preprint arXiv:2312.06086. Saatavilla: [https://doi.org/10.48550/arXiv.2312.06086](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2312.06086).

* **Wang, Xuezhi ym. 2022\.** *Self-Consistency Improves Chain of Thought Reasoning*. arXiv preprint arXiv:2203.11171. Saatavilla: [https://doi.org/10.48550/arXiv.2203.11171](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2203.11171).

* **Weidinger, Laura ym. 2021\.** *Ethical and social risks of harm from language models*. arXiv preprint arXiv:2112.04359. Saatavilla: [https://doi.org/10.48550/arXiv.2112.04359](https://doi.org/10.48550/arXiv.2112.04359).

* **Weston, Jason & Sukhbaatar, Sainbayar 2023\.** *System 2 attention*. arXiv preprint arXiv:2311.11829. Saatavilla: [https://doi.org/10.48550/arXiv.2311.11829](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2311.11829).

* **Wiggins, Grant 1998\.** *Educative assessment*. San Francisco: Jossey-Bass.

* **Wisse, Gerben & Greve, Rutger 2023\.** *AI in educational assessment: A systematic review*. Computers & Education: AI, 5\. Saatavilla: [https://doi.org/10.1016/j.caeai.2023.100174](https://www.google.com/search?q=https://doi.org/10.1016/j.caeai.2023.100174).

* **Wolf, Kenneth & Stevens, Ellen 2007\.** *The role of rubrics in advancing and assessing student learning*. Journal of Effective Teaching, 7(1), s. 3–14.

* **Wolf, Yotam ym. 2023\.** *Fundamental Limitations of Alignment in LLMs*. arXiv preprint arXiv:2304.11082. Saatavilla: [https://doi.org/10.48550/arXiv.2304.11082](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2304.11082).

* **Wolters Kluwer 2024\.** *2024 Future ready lawyer survey report*. Saatavilla: [https://www.wolterskluwer.com/en/know/future-ready-lawyer-2024](https://www.wolterskluwer.com/en/know/future-ready-lawyer-2024).

* **Wooldridge, Michael 2009\.** *An introduction to multiagent systems*. 2\. painos. Chichester: John Wiley & Sons.

* **World Economic Forum 2023\.** *Future of Jobs Report 2023*. Saatavilla: [https://www.weforum.org/publications/the-future-of-jobs-report-2023/](https://www.weforum.org/publications/the-future-of-jobs-report-2023/).

* **Wu, Junjie ym. 2024\.** *Large Language Models are Challenged by Over-complicated Instructions*. arXiv preprint arXiv:2409.07844. Saatavilla: [https://doi.org/10.48550/arXiv.2409.07844](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2409.07844).

* **Wynn, Alexander, Satija, Harsh & Hadfield, Gillian 2025\.** *Understanding failure modes in multi-agent debate*. arXiv preprint arXiv:2509.05396. Saatavilla: [https://doi.org/10.48550/arXiv.2509.05396](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2509.05396).

* **Ye, Rui ym. 2025\.** *X-MAS: A comprehensive testbed for heterogeneous MAS*. arXiv preprint arXiv:2505.16997. Saatavilla: [https://doi.org/10.48550/arXiv.2505.16997](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2505.16997).

* **Yeager.ai 2023\.** *AI Agent Kryptonite \- Prompt Saturation and Context Bleeding*. Medium. Saatavilla: [https://medium.com/yeagerai/ai-agent-kryptonite-prompt-saturation-and-context-bleeding-4db7c4329e4e](https://medium.com/yeagerai/ai-agent-kryptonite-prompt-saturation-and-context-bleeding-4db7c4329e4e).

* **Yi, Zhaoyang ym. 2025\.** *Benchmarking and defending against indirect prompt injection*. arXiv preprint arXiv:2312.14197. Saatavilla: [https://doi.org/10.48550/arXiv.2312.14197](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2312.14197).

* **Zhang, Yunhua ym. 2024\.** *Soar: AI-Driven Architectures through DAG Reasoning*. arXiv preprint arXiv:2404.05678. Saatavilla: [https://doi.org/10.48550/arXiv.2404.05678](https://doi.org/10.48550/arXiv.2404.05678).

* **Zilliz 2024\.** *Ensuring Secure and Permission-Aware RAG Deployments*. Zilliz Blog. Saatavilla: [https://zilliz.com/blog/ensure-secure-and-permission-aware-rag-deployments](https://zilliz.com/blog/ensure-secure-and-permission-aware-rag-deployments).

* **Zou, Wei ym. 2024\.** *PoisonedRAG: Knowledge Corruption Attacks*. arXiv preprint arXiv:2402.07867. Saatavilla: [https://doi.org/10.48550/arXiv.2402.07867](https://www.google.com/search?q=https://doi.org/10.48550/arXiv.2402.07867).

