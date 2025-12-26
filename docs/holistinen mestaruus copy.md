# Holistinen Mestaruus: Viitekehys tekoälyosaamisen arviointiin

## Abstrakti

Globaalit tietotyömarkkinat ovat keskellä historiansa merkittävintä rakennemuutosta (vrt. [Acemoglu & Restrepo 2018](#acemoglu2018)). Muutosta vauhdittaa generatiivisen tekoälyn (GenAI) ja suurten kielimallien (LLM) eksponentiaalinen kehitys. Kyseessä ei ole pelkkä teknologinen päivitys, vaan yleiskäyttöisen teknologian (General Purpose Technology, GPT) aiheuttama shokki, joka muokkaa uudelleen työn taloudellisen arvonluonnin perusteita ([Eloundou ym. 2023](#eloundou2023)).

Tekoälyn syvällinen ja kiihtyvä integroituminen työelämään on asettanut organisaatiot perustavanlaatuisen haasteen eteen: ne kohtaavat mittaamisen kriisin, jossa perinteiset keinot eivät enää riitä todentamaan luotettavasti korkean tason tekoälyosaamisen arvoa (vrt. [Auzmor 2024](#auzmor2024); [ISACA 2025](#isaca2025); [Disco 2024](#disco2024)). Tämä kriisi ei ole vain tekninen, vaan se koskettaa syvällisesti inhimillisen pääoman arvottamista tilanteessa, jossa koneiden kyvykkyydet kehittyvät eksponentiaalisesti.

Perinteiset arviointimenetelmät eivät kykene ratkaisemaan psykometriikan perustavanlaatuista reliabiliteetin ja validiteetin paradoksia (vrt. [Borsboom ym. 2004](#borsboom2004)). Tämä paradoksi korostuu entisestään generatiivisen tekoälyn yhteydessä, jossa oikeita vastauksia voi olla ääretön määrä ja prosessin laatu ratkaisee tuloksen arvon. Standardoidut testit ovat usein psykometrisesti luotettavia mutta sisällöllisesti kapea-alaisia ([Wiggins 1998](#wiggins1998)). Laadulliset menetelmät ovat puolestaan valideja, mutta kärsivät usein heikosta reliabiliteetista ja subjektiivisuudesta ([Koretz ym. 1994](#koretz1994)).

Tässä artikkelissa esitellään *hybridirubriikki*, uusi kaksitasoinen teoreettinen viitekehys, joka on suunniteltu hallitsemaan tätä jännitettä. Viitekehyksen analyyttinen taso perustuu BARS-asteikkoon (*Behaviorally Anchored Rating Scales*), Bloomin taksonomiaan ja Toulminin argumentaatiomalliin, ja se pyrkii maksimoimaan luotettavuutta standardoimalla arviointiprosessia. Sitä täydentävä holistinen taso hyödyntää vastakkainasetteluun perustuvaa (adversariaalista) agenttien välistä debattia (vrt. [Du ym. 2023](#du2023)) ja pyrkii maksimoimaan validiteetin tunnistamalla sääntöjä ylittävän, kontekstisidonnaisen asiantuntijuuden.

Viitekehyksen operatiivinen malli on ”Kognitiivinen Kvoorum”, moniagenttijärjestelmä (MAS), joka toteuttaa tämän kaksitasoisen arvioinnin hyödyntämällä koneoppimisen koosteoppimisen (engl. *ensemble learning*) periaatteita (vrt. [Sagi & Rokach 2018](#sagi2018)). Malli on tässä jäsennelty yksityiskohtaiseksi, vaiheittaiseksi prosessikuvaukseksi. Daniel Kahnemanin esittämä kaksoisprosessiteoria (Järjestelmä 1 ja Järjestelmä 2; vrt. [Kahneman 2011](#kahneman2011)) ohjaa viitekehyksen strategista kehitystä ja luo vision skaalautuvasta, mutta samalla syvällisesti auditoitavasta arviointijärjestelmästä.

Vaikka viitekehyksen prototyyppi on teknisesti toteutettu, siltä puuttuu toistaiseksi empiirinen validointi. Viitekehys pysyy puhtaasti teoreettisena konstruktiona, kunnes sen keskeinen hypoteesi – jonka mukaan on mahdollista saavuttaa korkea arvioitsijoiden välinen reliabiliteetti monimutkaisessa laadullisessa arvioinnissa – todennetaan muodollisessa pilottitutkimuksessa. Tämä työ tarjoaa metodologisen avauksen korkean panoksen osaamisen arviointiin tekoälyn aikakaudella.

---

## <a id="luku-1"></a>Luku 1: Strateginen haaste ja metodologinen perusta

Tämä luku perustelee, miksi tekoälyosaamisen luotettava mittaaminen on kriittinen strateginen haaste, ja esittelee viitekehyksen metodologisen perustan. Luvussa kuvataan ensin, miten tekoäly aiheuttaa globaalin taitomurroksen ja millaisen haasteen se luo osaamisen todentamiselle. Tämän jälkeen syvennytään psykometriikan perustavanlaatuiseen reliabiliteetin ja validiteetin paradoksiin, joka on perinteisten arviointimallien ydinongelma. Lopuksi luvussa eritellään keskeisten teorioiden tunnetut rajoitukset, jotka uuden ratkaisun on hallittava.

### <a id="luku-1-1"></a>1.1 Strateginen konteksti: Tekoäly ja taitomurros

Tekoälyn integroituminen liiketoimintaprosesseihin on käynnistänyt perustavanlaatuisen taitomurroksen, joka vaikutuksiltaan vertautuu teolliseen vallankumoukseen ([Acemoglu & Restrepo 2018](#acemoglu2018); [Eloundou ym. 2023](#eloundou2023)). Muutos ei ole vain teknologinen, vaan se muokkaa uudelleen työn taloudellista arvonluontia. Erityisesti suurten kielimallien (LLM) on arvioitu vaikuttavan merkittävästi jopa 80 prosenttiin Yhdysvaltain työvoimasta, kohdistuen nimenomaan korkeaa koulutusta vaativiin asiantuntijatehtäviin ([Eloundou ym. 2023](#eloundou2023)). Tutkimus osoittaa, että vähintään 50 % työtehtävistä saattaa muuttua tekoälyn vaikutuksesta noin 19 %:lla työntekijöistä, mikä viittaa siihen, että kyseessä on yleiskäyttöinen teknologia (General Purpose Technology, GPT), jonka vaikutukset läpäisevät kaikki toimialat ja palkkaluokat.

Toimialakohtaiset analyysit viittaavat nopeaan ja laaja-alaiseen muutokseen. Esimerkiksi McKinsey Global Instituten ennusteen mukaan merkittävä osa työntekijöiden keskeisistä taidoista muuttuu lähivuosina, ja jopa 30 % nykyisistä työtunneista voitaisiin automatisoida samana ajanjaksona ([Hazan ym. 2024](#hazan2024)).

Tämän kehityksen seurauksena arvonluonnin perusta siirtyy rutiinitehtävistä korkeamman tason kognitiivisiin kykyihin, kuten monimutkaiseen ongelmanratkaisuun, kriittiseen ajatteluun ja strategiseen vuorovaikutukseen ([OECD 2024](#oecd2024)). Kun tekoälyn kyky tuottaa ennusteita ja sisältöä yleistyy ja on laajasti saatavilla, ihmisen arvonluonnin ytimeen nousevat arviointi- ja harkintakyky sekä näiden taitojen hyödyntäminen päätöksentekojärjestelmien strategisessa uudelleensuunnittelussa ([Agrawal ym. 2022](#agrawal2022)). Nämä eivät ole pelkästään yleisiä työelämätaitoja, vaan keskeisiä taloudellisia kyvykkyyksiä, joiden arvo perustuu siihen, että ne täydentävät ja ohjaavat tekoälyn tuottamaa ennustekykyä (vrt. [Agrawal ym. 2022](#agrawal2022)). Kun tekoäly painaa tietotuotannon hinnan lähelle nollaa, sitä täydentävien tekijöiden – kuten datan, arvioinnin ja toiminnan – arvo nousee.

Näihin kyvykkyyksiin lukeutuvat esimerkiksi kriittinen validointi, luova synteesi ja eettinen harkinta, jotka kaikki edellyttävät kykyä arvioida ja ohjata tekoälyn tuottamaa informaatiota ([OECD 2024](#oecd2024)). Tekoälylukutaidosta on muodostumassa keskeinen strateginen prioriteetti. Erityisesti kehotesuunnittelua (engl. *prompt engineering*) on ehdotettu uudeksi perustaidoksi ([Federiakin ym. 2024](#federiakin2024)), ja laajemmin kykyä työskennellä tekoälyn kanssa pidetään yhtenä nopeimmin kasvavista osaamistarpeista globaaleilla työmarkkinoilla ([World Economic Forum 2023](#wef2023)). Laajemmin augmentaatiokyvyllä (engl. *augmentation capability*) tarkoitetaan kykyä hyödyntää tekoälyä oman suorituskyvyn ja ajattelun laadun parantamiseksi. Tällä kyvykkyydellä on konkreettinen taloudellinen arvo työmarkkinoilla (vrt. [Fügener ym. 2025](#fugener2025)).

Työmarkkinat reagoivat muutokseen nopeasti, ja tekoälytaitoja vaativista rooleista maksetaan jo nyt korkeampaa palkkaa ([PwC 2024](#pwc2024)). Tämä osoittaa, että kyseessä ei ole tulevaisuuden visio, vaan nykyhetken taloudellinen realiteetti, joka asettaa organisaatioille paineen tunnistaa, mitata ja kehittää näitä uusia taitoja. Tämä osaamisvaade on vahvistettu Euroopan unionin tasolla. Tekoälysäädös asettaa artiklassa 4 tekoälyjärjestelmien tarjoajille ja käyttöönottajille nimenomaisen velvoitteen ryhtyä toimenpiteisiin henkilöstönsä tekoälylukutaidon varmistamiseksi ([Euroopan parlamentin ja neuvoston asetus (EU) 2024/1689](#eu2024)). Tämä muuttaa tekoälyosaamisen arvioinnin kilpailuedusta lakisääteiseksi velvollisuudeksi, mikä edellyttää organisaatioilta luotettavia menetelmiä osaamistason todentamiseksi.

Uusimman sukupolven kielimallien ja niiden kehittyneiden päättelykykyjen myötä tämä tilanne muuttuu teoreettisesta mallista strategisesti merkittäväksi voimavaraksi. Nyt on otollinen hetki hyödyntää sitä, sillä teknologinen kehitys on saavuttanut pisteen, jossa korkeatasoisen arvioinnin vaatima metakognitiivinen arkkitehtuuri on toteutettavissa täysimääräisesti. Konkreettisena esimerkkinä tästä murroksesta ovat OpenAI:n o1-mallisarja ([OpenAI 2024](#openai2024)) ja Googlen Gemini 3.0 ([Google DeepMind 2025c](#google2025c)). Ne edustavat arkkitehtonista siirtymää nopeasta hahmontunnistuksesta hitaaseen ja harkitsevaan päättelyyn (vrt. [Google DeepMind 2025a](#google2025a); [Google DeepMind 2025b](#google2025b)). Muutos on ajankohtainen, sillä aiemmat mallit epäonnistuivat systemaattisesti monimutkaisten ohjeiden noudattamisessa ([Wu ym. 2024](#wu2024)) ja toimivat luonteeltaan todennäköisyyslaskentaan perustuvina ennustemalleina, jotka eivät kyenneet muodolliseen kausaaliseen päättelyyn ([Chi ym. 2024](#chi2024)). Tämä jätti arvioinnin alttiiksi pinnalliselle jäljittelylle ja hallusinaatioille, jotka ovat tunnettu riski kielimallien luotettavuudelle ([Huang ym. 2023](#huang2023)).

Tämän uuden mahdollisuuden taustalla on tekninen siirtymä pelkästä tilastollisesta hahmontunnistuksesta kohti ”Deep Think” -arkkitehtuureja. Nämä hyödyntävät pidennettyä päättelyaikaa (engl. *inference-time compute*). Arkkitehtuurit on koulutettu vahvistusoppimisen avulla generoimaan sisäisiä, iteratiivisia ajatusketjuja (Chain-of-Thought). Tavoitteena on tunnistaa ja korjata virheet ennen lopullisen vastauksen tuottamista ([Google DeepMind 2025a](#google2025a); [Google DeepMind 2025b](#google2025b)). Tässä artikkelissa esiteltävä moniagenttijärjestelmä valjastaa nyt näiden uusien mallien hitaan ja pohtivan prosessoinnin tuottamaan aitoa, Kahnemanin (2011) kuvaamaa ”Järjestelmä 2” -tason analyysia. Tämä toteutetaan toiminnallisesti pakottamalla agentit käyttämään sisäisiä päättelytiloja (esim. scratchpad tai Chain-of-Thought) monimutkaisissa analyysitehtävissä. Tämä mahdollistaa sen, mikä aiemmin oli haastavaa: uskottavamman falsifioinnin ja syvällisten loogisten virheiden tunnistamisen. On kuitenkin huomattava, että nykyiset mallit suorittavat kausaalista päättelyä (L3) ensisijaisesti kielellisinä approksimaatioina eivätkä muodollisina matemaattisina todistuksina ([Chi ym. 2024](#chi2024)), mikä huomioidaan viitekehyksen heuristisessa luonteessa.

Viitekehys hyödyntää tätä uutta kapasiteettia ratkaistakseen arvioinnin reliabiliteetin ja validiteetin välisen paradoksin ([Borsboom ym. 2004](#borsboom2004)) ja tarjoaa keinon tunnistaa luotettavasti sekä sääntöjä noudattavan rutiiniosaamisen että säännöt ylittävän, kontekstisidonnaisen mestaruuden ([Dreyfus & Dreyfus 1980](#dreyfus1980)).

### <a id="luku-1-2"></a>1.2 Ydinongelma: "Mittaamisen kriisi" ja itsearvioinnin haaste

Tämä taitomurros on synnyttänyt organisaatioille keskeisen strategisen haasteen, ”mittaamisen kriisin”. Kyseessä on ilmiö, joka on tunnistettu laajalti myös kognitiivisten kykyjen ja tekoälyn arvioinnin yhteydessä (vrt. [Silva ym. 2025](#silva2025); [Cheng 2021](#cheng2021)).

Kriisi ilmentää perustavanlaatuista vaikeutta todentaa tekoälyinvestointien ja -osaamisen todellista arvoa. Vaikka organisaatiot investoivat teknologiaan merkittävästi, ilman luotettavia mittareita investointien tuotto (ROI) ja vaikutus strategisiin kyvykkyyksiin jäävät usein todentamatta ([Auzmor 2024](#auzmor2024); [ISACA 2025](#isaca2025)). Tuoreen raportin mukaan lähes puolella (49 %) organisaatioista on vaikeuksia arvioida ja osoittaa luotettavasti tekoälyhankkeidensa arvoa ([ISACA 2025](#isaca2025)). Tämä epävarmuus ei ole vain akateeminen ongelma, vaan se näkyy konkreettisesti esimerkiksi lakialalla, jossa epävarmuus investointien tuotoista on merkittävä este tekoälyn laajemmalle käyttöönotolle ([Wolters Kluwer 2024](#wolters2024)). Lisäksi vain 24 % alan johtajista kokee, että heidän johtoryhmänsä ovat täysin yksimielisiä tekoälystrategiasta ([Wolters Kluwer 2024](#wolters2024)).

Tämä luo negatiivisen kierteen: ilman luotettavaa dataa osaamisen arvosta johto ei kykene perustelemaan investointeja koulutukseen ja teknologiaan, mikä johtaa aliresursointiin ja heikentää strategisten aloitteiden uskottavuutta ([Disco 2024](#disco2024)).

Ongelmaa syventää se, että luotettava itsearviointi on tunnetusti haastavaa. Osaamisen onnistunut arviointi edellyttää, että yksilö kykenee metakognitiivisesti tunnistamaan oman osaamisensa puutteet ([Kruger & Dunning 1999](#kruger1999)). Tämä taito on usein heikosti kehittynyt erityisesti matalammalla osaamistasolla. Tämä Dunning–Kruger-vaikutuksena tunnettu havainto luo systemaattisen epäsuhdan havaitun ja todellisen osaamisen välille. Tämä epäsuhta on ominaista yksilötasolla, ja se ilmenee tutkitusti myös organisaatiotasolla, missä kokonaiset tiimit saattavat yliarvioida digitaalisen kypsyytensä (ks. esim. [Nold & Michel 2022](#nold2022)).

Koska organisaatio ei voi luottaa pelkkään itsearviointiin, tarvitaan objektiivista, ulkoiseen todistusaineistoon perustuvaa validointiprosessia. Tämä on välttämätöntä, sillä luotettava arviointikyky edellyttää vertailua ulkoisiin viitepisteisiin ([Sadler 1989](#sadler1989)), mikä auttaa ohittamaan inhimilliset harhat.

### <a id="luku-1-3"></a>1.3 Metodologinen perushaaste: Reliabiliteetin ja validiteetin paradoksi

Vaikka tarve objektiiviselle mittaamiselle on ilmeinen, se kohtaa välittömästi psykometriikan perustavanlaatuisen haasteen: arvioinnin reliabiliteetti (luotettavuus, *reliability*) ja validiteetti (pätevyys, *validity*) ovat jännitteisessä suhteessa keskenään (vrt. [Borsboom ym. 2004](#borsboom2004)).

Nämä kaksi käsitettä ovat minkä tahansa mittausprosessin laadun kulmakiviä (vrt. [Cohen ym. 1996](#cohen1996)):
* **Reliabiliteetti** viittaa mittauksen johdonmukaisuuteen ja toistettavuuteen ([AERA, APA & NCME 2014](#aera2014)). Keskeinen kysymys on, saavatko eri arvioijat (tai sama arvioija eri aikoina) saman tuloksen samasta aineistosta. Korkea reliabiliteetti on välttämätöntä, jotta arviointi olisi oikeudenmukaista, ennustettavaa ja oikeudellisesti puolustettavaa.
* **Pätevyys** viittaa siihen, mittaako arviointi sitä, mitä sen on tarkoitus mitata ([AERA, APA & NCME 2014](#aera2014)). Tekoälyosaamisen kontekstissa tavoitteena on mitata abstrakteja ja monimutkaisia kognitiivisia taitoja, kuten kriittistä ajattelua, luovaa ongelmanratkaisua ja strategista harkintaa, eikä ainoastaan mekaanista prosessien noudattamista tai ulkoa opeteltua tietoa ([Wiggins 1998](#wiggins1998)).

Paradoksi syntyy siitä, että näiden kahden tavoitteen välillä on usein sovittamaton jännite.

Korkeaa luotettavuutta tavoittelevat menetelmät, kuten standardoidut ja tiukasti strukturoidut testit (esimerkiksi monivalinnat), ovat usein liian kapea-alaisia eivätkä onnistu mittaamaan monimutkaisia taitoja validisti ([Wiggins 1998](#wiggins1998)). Wigginsin mukaan tällaiset menetelmät mittaavat usein ensisijaisesti irrotettuja perustaitoja ja ulkoa muistamista, eivätkä onnistu tavoittamaan "intellektuaalista suorituskykyä" tai aitoa osaamista, joka vaatii tiedon soveltamista monimutkaisissa, autenttisissa konteksteissa (ks. myös [Shafiyeva 2021](#shafiyeva2021); [David 2019](#david2019).; [FairTest 2012](#fairtest2012)).

Toisaalta korkeaa pätevyysa tavoittelevat menetelmät, kuten avoin laadullinen portfolioarviointi, ovat usein subjektiivisia ja kärsivät heikosta reliabiliteetista ([Koretz ym. 1994](#koretz1994); vrt. [Center for Innovative Teaching & Learning 2025](#citl2025)). Tämä puolestaan tekee niistä vaikeasti skaalautuvia organisaatiokontekstissa, missä arvioinnin on oltava paitsi syvällistä myös vertailukelpoista.

Tämä jännite on myös tekoälyavusteisen arvioinnin ytimessä ([Bulut ym. 2024](#bulut2024)). Se asettaa keskeisen suunnitteluhaasteen: miten rakentaa järjestelmä, joka on riittävän systemaattinen ja objektiivinen soveltuakseen koneelliseen analyysiin (korkea reliabiliteetti), mutta samalla riittävän joustava ja syvällinen tunnistamaan aidon kognitiivisen mestaruuden (korkea pätevyys).

Tässä artikkelissa esiteltävässä viitekehyksessä käytettävä kolmiosainen todistusaineisto (keskusteluhistoria, lopputuote, reflektiodokumentti) ei ole portfolio perinteisessä merkityksessä. Se jakaa kuitenkin portfolion keskeisimmät psykometriset piirteet, kuten tavoitteellisuuden, moniosaisuuden ja reflektiivisyyden ([Paulson ym. 1991](#paulson1991)). Koska kyseessä on laadullinen ja asiantuntija-arviointia vaativa kokonaisuus, se rinnastuu metodologisesti portfolioarviointiin ja sen tunnettuihin haasteisiin. Laaja tutkimusnäyttö osoittaa, että portfolioarvioinnin keskeisin psykometrinen heikkous on arvioitsijoiden välisen yhdenmukaisuuden (arvioitsijareliabiliteetin) matala taso ([Baume & Yorke 2002](#baume2002)). Ilman tarkkaa jäsentelyä ja selkeitä arviointikriteerejä, eri arvioijat – olivatpa ne ihmisiä tai algoritmeja – kiinnittävät huomiota eri asioihin, mikä lisää tulkinnanvaraisuutta (vrt. [Jonsson & Svingby 2007](#jonsson2007)).

Metodologinen kehitys kohti kognitiivisten prosessien arviointia syventää tätä paradoksia entisestään. Tämä siirtymä vaatii luotettavia ja validoituja työkaluja, jotka täyttävät psykometriikan standardit ([AERA, APA & NCME 2014](#aera2014)). Tällaisten työkalujen kehittäminen subjektiivisten kognitiivisten ilmiöiden arvioimiseksi on kuitenkin osoittautunut metodologisesti erittäin haastavaksi (vrt. [Messick 1989](#messick1989)). Siirtymä kohti kognitiivisten prosessien arviointia ei siten ainoastaan vaikeuta reliabiliteetin varmistamista, vaan myös aktiivisesti voimistaa paradoksin jännitettä, koska monimutkaisten taitojen mittaaminen on luontaisesti haastavampaa kuin yksinkertaisten tietojen ([Shavelson 2013](#shavelson2013)).

Vaikka kognitiiviset taksonomiat, kuten Bloomin malli ([Anderson & Krathwohl 2001](#anderson2001)), tarjoavat tarpeellisen rakenteen, on tärkeää tunnustaa niiden rajoitukset. Kriitikot huomauttavat, että tällaiset mallit voivat esittää osaamisen staattisena ja atomistisena hierarkiana, joka ei täysin tavoita aidon asiantuntijuuden integroitua ja dynaamista luonnetta ([Lane 2013](#lane2013); vrt. [Dreyfus & Dreyfus 1980](#dreyfus1980)).

Tämä asettaa seuraavassa luvussa esiteltävälle arkkitehtoniselle ratkaisulle – hybridirubriikille – entistäkin suurempia vaatimuksia. Sen on kyettävä hallitsemaan tätä voimistunutta jännitettä tavalla, joka on sekä teoreettisesti vankka että käytännössä toimiva. Hybridirubriikki ja sen operatiivinen toteutus ”Kognitiivinen Kvoorum” on kehitetty juuri tämän hypoteesin testaamiseksi. On kuitenkin olennaista ymmärtää, että vaikka tämän prototyypin logiikka on toteutettu, empiirinen näyttö sen käytännön toimivuudesta tai kyvystä ratkaista tämä paradoksi puuttuu. Koko viitekehys edustaa tässä vaiheessa ainoastaan testattavaksi ehdotettua, teknisesti toteutettua mutta todentamatonta ratkaisumallia.

### <a id="luku-1-4"></a>1.4 Tutkimusote ja -menetelmä

Tämä artikkeli noudattaa konstruktiivista tutkimusotetta, joka asemoituu Design Science Research (DSR) -metodologian piiriin. DSR:n tavoitteena on ratkaista relevantteja käytännön ongelmia kehittämällä ja arvioimalla innovatiivisia IT-artefakteja vakiintuneen tietopohjan (engl. *knowledge base*) pohjalta ([Hevner ym. 2004](#hevner2004)).

Tässä tutkimuksessa keskeinen ongelma on tekoälyosaamisen mittaamisen kriisi ([Luku 1.2](#luku-1-2)), ja kehitetty artefakti on Hybridirubriikki-viitekehys ja sen operatiivinen malli, Kognitiivinen Kvoorum ([Luku 2](#luku-2)). DSR-prosessin mukaisesti ([Peffers ym. 2007](#peffers2007)) tämä artikkeli keskittyy ongelman tunnistamiseen ja motivointiin ([Luku 1](#luku-1)), ratkaisun tavoitteiden määrittelyyn ([Luku 2.1](#luku-2-1)) sekä artefaktin suunnitteluun ja kehittämiseen ([Luvut 2](#luku-2) ja [4](#luku-4)). Tässä vaiheessa artefaktin demonstrointi rajoittuu sen prototyypin kuvaukseen ja teoreettiseen perusteluun. Kuten [Luvussa 6.2](#luku-6-2) todetaan, artefaktin muodollinen arviointi (engl. evaluation) empiirisessä kontekstissa on välttämätön jatkotutkimuksen kohde.
## <a id="luku-2"></a>Luku 2: Hybridirubriikin Arkkitehtuuri ja Operatiivinen Malli

Tämä luku esittelee Hybridirubriikki-viitekehyksen arkkitehtuurin ja sen operatiivisen mallin. Kyseessä on uusi arviointiviitekehys, joka on suunniteltu vastaamaan tekoälyn aikakauden monimutkaisten taitojen mittaamisen haasteisiin.

Luvun rakenne etenee systemaattisesti järjestelmän perustasta sen toimintaan ja hallintaan. Ensin kuvataan järjestelmän taustalla olevat suunnitteluperiaatteet ja arvioinnin kohde. Tämän jälkeen esitellään arkkitehtuurin staattiset komponentit, eli mistä osista järjestelmä koostuu. Seuraavaksi kuvataan järjestelmän dynaaminen toiminta eli operatiivinen prosessimalli vaihe vaiheelta. Lopuksi käsitellään järjestelmän eheyden varmistavaa hallintamallia ja monikerroksista puolustusstrategiaa.

### <a id="luku-2-1"></a>2.1 Suunnitteluperiaatteet ja Arkkitehtuurin Yleiskuva

Tämä osio luo perustan koko viitekehykselle määrittelemällä sen keskeiset suunnitteluperiaatteet ja arvioinnin kohteen. Aluksi kuvataan arkkitehtuurin filosofinen ydin: tietoinen päätös hallita reliabiliteetin ja validiteetin välistä jännitettä kaksitasoisella rakenteella. Tämän jälkeen määritellään standardoitu, kolmiosainen todistusaineisto, joka toimii syötteenä myöhemmin kuvattaville arkkitehtuurin komponenteille ja operatiiviselle prosessille. Nämä määrittelyt ohjaavat kaikkia seuraavissa osioissa esitettyjä teknisiä ja metodologisia valintoja.

#### <a id="luku-2-1-1"></a>2.1.1 Ratkaisun Periaate: Kaksitasoinen Vastaus Mittaamisen Paradoksiin

Viitekehys tarjoaa edellä kuvattuun reliabiliteetin ja validiteetin paradoksiin arkkitehtonisen vastauksen: hybridirubriikin. Sen keskeisenä suunnitteluperiaatteena ei ole pyrkiä ratkaisemaan tätä perustavanlaatuista jännitettä tai löytää täydellistä kompromissia, vaan tunnustaa se ja rakentaa järjestelmä, joka hallitsee jännitettä tietoisesti. Sen sijaan, että arkkitehtuuri olisi yhtenäinen monoliitti, se on tarkoituksellisesti kaksitasoinen.

Se institutionalisoi paradoksin luomalla kaksi erillistä, toisiaan täydentävää arviointitasoa, joista kumpikin on optimoitu eri päämäärään:

* **Analyyttisen tason** tavoitteena on maksimoida reliabiliteetti. Se luo järjestelmälle systemaattisen, sääntöpohjaisen ja auditoitavan selkärangan, joka varmistaa arvioinnin johdonmukaisuuden ja toistettavuuden. Se toimii "ankkurina", joka estää arvioinnin valumisen täydelliseen subjektiivisuuteen.
* **Holistisen tason** tavoitteena on maksimoida pätevyys. Se on joustava ja dynaaminen mekanismi, jonka tehtävänä on tunnistaa aito, kontekstisidonnainen ja sääntöjä ylittävä osaaminen, jota analyyttinen taso ei kykene tavoittamaan.

Tämä kaksitasoinen lähestymistapa on enemmän kuin tekninen ratkaisu; se on metodologinen ja filosofinen kannanotto. Se edustaa ”metodologista nöyryyttä” – avointa tunnustusta siitä, ettei mikään yksittäinen menetelmä voi yksinään tavoittaa monimutkaisen inhimillisen osaamisen koko kirjoa (vrt. [Johnson & Onwuegbuzie 2004](#johnson2004), jotka perustelevat vastaavaa pragmaattista lähestymistapaa monimenetelmätutkimuksessa).

Viitekehyksen keskeinen hypoteesi on, että järjestelmän älykkyys ei synny kummastakaan tasosta yksinään, vaan niiden hallitusta vuorovaikutuksesta. Ilmiö tunnetaan koneoppimisessa koosteoppimisen (engl. *ensemble learning*) hyötynä, jossa monimuotoisten arviointimekanismien yhdistäminen vähentää kokonaisvirhettä tehokkaammin kuin yksittäinen optimoitu malli (vrt. [Sagi & Rokach 2018](#sagi2018)). [Sagi ja Rokach (2018)](#sagi2018) osoittavat, että yhdistämällä useita malleja – tai tässä tapauksessa useita arviointiagentteja – voidaan kompensoida yksittäisten mallien heikkouksia ja saavuttaa tarkempi ennuste tai arvio. Kognitiivinen Kvoorum soveltaa tätä periaatetta siten, että se jakaa arviointitehtävän erikoistuneille agenteille, jolloin vältetään yksittäisen LLM-mallin vinoumat.

#### <a id="luku-2-1-2"></a>2.1.2 Järjestelmän Episteeminen Nelikenttä (DATA, TULOS, INTENTIO, STANDARDI)

Hybridirubriikki ei arvioi vain lopputulosta, vaan kokonaisvaltaista tietotyöprosessia. Tätä varten se määrittelee neljä erillistä episteemistä ulottuvuutta, jotka muodostavat arvioinnin koordinaatiston:

1.  **DATA (Mitä tehtiin):** Keskusteluhistoria (*History Log*).
    *   *Määritelmä:* Autenttinen, muokkaamaton tallenne käyttäjän ja tekoälyn välisestä vuorovaikutuksesta.
    *   *Funktio:* Toimii empiirisenä todistusaineistona prosessin laadusta. Se paljastaa lahjomattomasti, onko käyttäjä toiminut "Kuljettajana" (aktiivinen ohjaus) vai "Matkustajana" (passiivinen tilaus).
    *   *Agentit:* Vartija, Analyytikko, Loogikko, Falsifioija.

2.  **TULOS (Mitä saatiin aikaan):** Lopputuote (*Product Artifact*).
    *   *Määritelmä:* Prosessin konkreettinen lopputulema (esim. koodi, sopimus, essee).
    *   *Funktio:* Mittaa työn substanssiarvoa ja faktuaalista oikeellisuutta. Ilman laadukasta tulosta hyväkään prosessi ei ole arvokas.
    *   *Agentit:* Analyytikko, Faktuaalinen Valvoja.

3.  **INTENTIO (Mitä yritettiin):** Reflektiodokumentti (*Reflection Document*).
    *   *Määritelmä:* Käyttäjän metakognitiivinen selitys omasta prosessistaan ja tavoitteistaan.
    *   *Funktio:* Paljastaa käyttäjän itsetuntemuksen tason (Dunning-Kruger). Kriittinen kysymys: Onko Intentio linjassa Datan kanssa, vai onko kyseessä jälkikäteen keksitty selitys (Post-Hoc Rationalization)?
    *   *Agentit:* Profiloija, Performatiivisuuden Tunnistaja.

4.  **STANDARDI (Miten asiat pitäisi tehdä):** Tämä dokumentti (*The Standard*).
    *   *Määritelmä:* Normatiivinen säännöstö (esim. Laki, Brand Book, Opetussuunnitelma), jota vasten kolmea edellistä verrataan.
    *   *Funktio:* Toimii "Coachin aivoina". Se määrittelee "hyvän" kriteerit. Kun vaihdat tätä dokumenttia, muutat koko järjestelmän arvomaailman (esim. Lakimiehestä Markkinointijohtajaksi).
    *   *Agentit:* Tuomari, Valmentaja.

Tämä nelikenttä mahdollistaa triangulaation: Totuus ei löydy yhdestäkään tiedostosta yksinään, vaan niiden välisten ristiriitojen ("Deltan") analyysistä.

Kuten [Luvussa 1.3](#luku-1-3) todetaan, tämä kokonaisuus rinnastuu metodologisesti portfolioarviointiin ([Paulson ym. 1991](#paulson1991)).

### <a id="luku-2-2"></a>2.2 Arkkitehtuurin Komponentit

Kun suunnitteluperiaatteet ja arvioinnin kohde on määritelty, tässä osiossa esitellään Hybridirubriikin kaksi pääkomponenttia, jotka muodostavat sen rakenteellisen perustan (staattinen näkymä). Osio kuvaa ensin Analyyttisen Tason, joka konkretisoituu yksityiskohtaiseksi Kognitiiviseksi Arviointimatriisiksi. Tämän jälkeen esitellään Holistinen Taso, joka on toteutettu Kognitiivinen Kvoorum -moniagenttijärjestelmänä. Nämä komponentit ovat ne mekanismit, jotka aktivoidaan seuraavassa osiossa kuvattavassa operatiivisessa mallissa.

#### <a id="luku-2-2-1"></a>2.2.1 Analyyttinen Taso: Kognitiivinen Arviointimatriisi

Hybridirubriikin arkkitehtuurin ensimmäinen taso on sen analyyttinen taso, joka konkretisoituu Kognitiiviseksi Arviointimatriisiksi. Tämä matriisi muodostaa koko arviointiprosessin systemaattisen ja auditoitavan selkärangan. Sen ensisijainen tavoite on varmistaa arvioinnin reliabiliteetti (engl. *reliability*) – mittauksen johdonmukaisuus ja toistettavuus ([AERA, APA & NCME 2014](#aera2014)).

Matriisin suunnittelu perustuu vakiintuneisiin kognitiivisen suorituskyvyn ja argumentaation viitekehyksiin. Se hyödyntää Bloomin taksonomiaa ([Anderson & Krathwohl 2001](#anderson2001)) kognitiivisten taitotasojen (analyysi, arviointi, synteesi) erittelyyn ja Toulminin argumentaatiomallia ([Toulmin 2003](#toulmin2003)) päättelyn laadun systemaattiseen arviointiin. Rakenteellisesti matriisi on BARS-asteikko (engl. *Behaviorally Anchored Rating Scales*), joka sitoo arviointitasot konkreettisiin kuvauksiin ([Smith & Kendall 1963](#smith1963)). Tämä Kognitiivinen Arviointimatriisi muodostaa arvioinnin normatiivisen perustan.

**Metodologiset Rajoitteet:**
Tämä metodologinen valinta sisältää kuitenkin tietoisesti hyväksyttyjä rajoitteita, jotka tekevät hybridimallin toisesta tasosta välttämättömän. BARS-menetelmiä on perinteisesti kehitetty tavoitteena parantaa luotettavuutta siten, että arviointitasot ankkuroidaan konkreettisiin käyttäytymiskuvauksiin ([Moskal 2000](#moskal2000); [Smith & Kendall 1963](#smith1963)). Niiden todellinen psykometrinen ylivoimaisuus muihin menetelmiin nähden on kuitenkin kyseenalaistettu ([Jacobs ym. 1980](#jacobs1980)). Akateemiset arviot ovat todenneet, että BARS-asteikot eivät kvantitatiivisesti arvioituna ole välttämättä parempia kuin muutkaan menetelmät ([Jacobs ym. 1980](#jacobs1980)), ja eräissä vertailuissa ne ovat jopa osoittaneet heikompaa arvioitsijoiden välistä yhdenmukaisuutta kuin perinteiset summatiiviset asteikot ([Kinicki ym. 1985](#kinicki1985)).

Lisäksi niihin liittyy tutkimuskirjallisuudessa laajasti tunnistettuja psykometrisiä ja käytännöllisiä haasteita. Niiden kehittäminen on resurssi-intensiivistä, aikaa vievää ja kallista ([Morgeson ym. 2007](#morgeson2007)). Lisäksi ne voivat olla joustamattomia muuttuvissa työrooleissa, jotka vaativat jatkuvaa päivitystä ([Levine ym. 1988](#levine1988)). Tämä joustamattomuus ja vaatimus määritellä spesifisiä käyttäytymismalleja voivat johtaa siihen, että ne yksinkertaistavat liikaa monimutkaisia, luovia tai strategisia tehtäviä ([Klieger ym. 2018](#klieger2018)), kuten ongelmanratkaisua ja luovuutta, joita on vaikea kuvata spesifisinä, havaittavina käyttäytymisinä.

Juuri tämä BARS-mallien ankkureiden "äärimmäinen spesifisyys" (engl. *extreme specificity*) voi johtaa kognitiivisen vaatimustason latistumiseen, ja se onkin tunnistettu haasteeksi arvioijille, sillä se rajoittaa niiden soveltuvuutta abstraktimpien ominaisuuksien mittaamiseen ([Klieger ym. 2018](#klieger2018)). Lisäksi BARS-asteikkojen luotettavuuden on osoitettu olevan parhaimmillaankin vain kohtalainen tai jopa rajoitettu (engl. *limited reliability*) juuri niissä konteksteissa, jotka vaativat monimutkaisten ei-teknisten taitojen arviointia, kuten vaativissa asiantuntijatehtävissä on todennettu ([Kim ym. 2022](#kim2022)).

Tämän vuoksi analyyttisen tason toteuttaminen BARS-mallina ei ole ratkaisu reliabiliteettiongelmaan, vaan tietoinen kompromissi, joka tuo rakenteen arviointiin mutta jättää merkittävän osan varianssista selittämättä. Juuri nämä menetelmän sisäsyntyiset rajoitukset tekevät holistisen tason välttämättömäksi.

Kuten tämän viitekehyksen "Metodologisen nöyryyden mandaatissa" (ks. [Luku 2.4.3.2, Mandaatti 3](#luku-2-4-3-2)) todetaan, kognitiivisiin prosesseihin (Bloom, Toulmin) perustuva matriisi mittaa tehokkaasti prosessin loogisuutta (Pätevyys), mutta ei välttämättä tunnista aitoa asiantuntijuutta (Mestaruus), joka ilmenee sääntöjen strategisena rikkomisena tai luovana soveltamisena. Nämä taidot ovat usein kontekstisidonnaisia, implisiittisiä ([Polanyi 1966](#polanyi1966)) ja vaikeasti etukäteen määriteltäviä (vrt. [Dreyfus & Dreyfus 1980](#dreyfus1980)).

Kognitiivisen arviointimatriisin rajoitteet eivät ole virheitä, vaan tietoinen suunnitteluvalinta. Matriisin rakenteellinen jäykkyys on välttämätöntä, jotta se voi toimia vakaana ja koneellisesti käsiteltävänä perustana. Tämän metodologisen jännitteen vuoksi viitekehys ei voi nojata pelkkään analyyttiseen tasoon, vaan vaatii toisen, dynaamisemman tason.

Itse analyyttinen matriisi (Taulukko 1) on kuitenkin rakennettu huomattavasti perinteisiä BARS-asteikkoja yksityiskohtaisemmaksi, jotta se tarjoaa riittävän erottelukyvyn. Erityisesti korkeimman tason (Taso 4) kriteerit sisältävät usein vaihtoehtoisia polkuja. Tämä valinta pyrkii lisäämään pätevyyttä, mutta samalla se lisää kognitiivista kuormaa ja tulkinnanvaraisuutta, mikä puolestaan luo tunnetun riskin arvioitsijoiden välisen yhdenmukaisuuden (engl. *Inter-Rater Reliability*, IRR) heikkenemiselle ([Wolf & Stevens 2007](#wolf2007); [Jonsson & Svingby 2007](#jonsson2007)).

Kognitiivisen Kvoorumin arkkitehtuuri on suunniteltu hallitsemaan tätä lisääntynyttä jännitettä. Analyytikko-agentti ankkuroi väitteet todistusaineistoon ([Luku 2.3.3](#luku-2-3-3)), Loogikko-agentti purkaa argumentin rakenteen ([Luku 2.3.4](#luku-2-3-4)) ja Kriitikkoryhmä falsifioi argumentin ([Luku 2.3.5](#luku-2-3-5)). Tämän prosessin tavoitteena on varmistaa, että monimutkaisten kriteerien soveltaminen pysyy ankkuroituna objektiiviseen todistusaineistoon, mikä vähentää subjektiivista tulkintaa ja tukee luotettavuutta.

**Taulukko 1. Kognitiivinen Arviointimatriisi (BARS-asteikko, vrt. `seed_data.json` "BARS_MATRIX")**

| Kriteeri | Taso 4: Arkkitehti (Architect) | Taso 3: Kuski (Driver) | Taso 2: Kartanlukija (Navigator) | Taso 1: Matkustaja (Passenger) |
| :--- | :--- | :--- | :--- | :--- |
| **Strateginen Ohjaus (Agency)** | **Arkkitehti (Suunnittelee):** Käyttäjä on purkanut ongelman osiin (Decomposition) ENNEN ensimmäistä promptia. Prosessi on suunniteltu ketju. | **Kuski (Ohjaa):** Käyttäjä tietää mitä haluaa ja asettaa reunaehdot. Korjaa suuntaa aktiivisesti, jos tekoäly poikkeaa. | **Kartanlukija (Korjaa):** Reaktiivinen toiminta. Epämääräinen aloitus, korjaa vasta jälkikäteen ("Ei noin, vaan näin"). | **Matkustaja (Tilaa):** Passiivinen tilaaja. "Tee essee aiheesta X". Hyväksyy ensimmäisen version. Ulkoistaa ajattelun. |
| **Tekninen Toteutus (Engineering)** | **Insinööri:** Käyttää edistyneitä tekniikoita: Few-Shot, Chain-of-Thought, XML-tagit. Promptit ovat strukturoituja olioita. | **Osaaja:** Käyttää perustekniikoita: Roolitus, selkeät rajoitteet, kontekstin syöttö. Kieli on täsmällistä. | **Keskusteleva:** Käyttää luonnollista puhekieltä ("Voisitko..."). Promptit epätarkkoja. | **Laiska (Lazy):** Kirjoitusvirheitä, "se juttu", pelkkiä avainsanoja. Luottaa tekoälyn "mind reading" -kykyyn. |
| **Kriittinen Iteraatio (Falsification)** | **Adversariaalinen:** Testaa rajoja ("Etsi virheet"). Spottaa faktavirheet ja pakottaa korjaamaan lähteisiin viitaten. | **Korjaava:** Huomaa selkeät virheet ja pyytää korjausta. | **Hyväksyvä:** Kehuu tekoälyä ("Hyvä!") vaikka vastauksessa olisi puutteita. Korjaukset vain tyylillisiä. | **Sokea:** Sokea luottamus. Kopioi hallusinaatiot suoraan lopputuotteeseen. |

#### <a id="luku-2-2-2"></a>2.2.2 Holistinen Taso: Kognitiivinen Kvoorum ja Paneeli (MAS-arkkitehtuuri)

Hybridirubriikin toinen arkkitehtoninen taso on holistinen taso. Se on toteutettu Kognitiivinen Kvoorum -moniagenttijärjestelmänä, joka toimii kahdessa moodissa (`seed_data.json` workflows):

1.  **Sequential Audit (Courtroom 2.0):** Agentit toimivat peräkkäin, syväluodaten jokaisen aspektin erikseen.
2.  **Fused Audit (Courtroom 3.0):** Käyttää `PanelAgent`-komponenttia, joka yhdistää Logiikan, Falsifioinnin ja Kausaalisuuden yhdeksi "Paneeliksi". Tämä on tehokkaampi ja vähentää kognitiivista kuormaa, mutta säilyttää kriittiset näkökulmat.

Kvoorum koostuu erikoistuneista rooleista:
*   **Turvaportti:** Vartija-agentti.
*   **Analyysi:** Analyytikko ja Loogikko.
*   **Kriitikot (tai Paneeli):** Falsifioija, Valvoja, Kausaalinen, Tunnistaja.
*   **Synteesi:** Tuomari ja XAI-Raportoija.
*   **Ohjaus:** Valmentaja.

### <a id="luku-2-3"></a>2.3 Operatiivinen Malli: Sekventiaalinen Auditointiketju

...

**Deterministinen Rangaistusmekanismi ("Passiivisuus-leikkuri")**

Järjestelmän sääntökantaan (`seed_data.json` -> `OP_RULE_4`) on koodattu ehdoton "Passiivisuus-leikkuri". Tämä on kriittinen kontrolli:

*   **Sääntö:** Jos käyttäjä saa mistään kriteeristä tason 1 (Matkustaja), kokonaisarvosana **EI SAA** ylittää tasoa 2/4.
*   **Perustelu:** Hyvä tekoäly ei kompensoi huonoa kuskia. Arvioimme prosessinhallintaa, emme tuuria. Jos käyttäjä nukkuu ratissa, suoritus hylätään, vaikka auto (AI) ajaisi maaliin.

Tämä osio siirtää tarkastelun arkkitehtuurin staattisista komponenteista järjestelmän dynaamiseen toimintaan. Se kuvaa yksityiskohtaisesti "Sekventiaalisen Auditointiketjun" – vaiheittaisen prosessin, jonka mukaisesti arviointi suoritetaan. Osio esittää tiukassa ajallisessa järjestyksessä, miten arkkitehtuurin komponentit (agentit ja matriisi) prosessoivat todistusaineistoa. Prosessi koostuu viidestä peräkkäisestä päävaiheesta (1–5), alkaen syötteen esikäsittelystä, edeten analyysiin ja argumentaatioon, jatkuen kriittiseen falsifiointiin ja päättyen lopulliseen synteesiin.

#### <a id="luku-2-3-1"></a>2.3.1 Prosessimallin Kuvaus ja Auditoitavuus

Nykyisessä prototyyppivaiheessa järjestelmä toteuttaa ”sekventiaalisen auditointiketjun” (engl. *Sequential Audit Chain*), jossa agentit prosessoivat informaatiota peräkkäin kumuloituvassa prosessissa. Tämä arkkitehtuuri on itsessään verrattavissa tieteellisen menetelmän soveltamiseen ([Cheng 2001](#cheng2001)):

1.  **Vaihe 1: Empiirinen havainnointi.** Prosessi alkaa todistusaineiston keräämisestä ja ankkuroinnista (Analyytikko-agentti, ks. [Luku 2.3.3](#luku-2-3-3)).
2.  **Vaihe 2: Hypoteesin luominen.** Jäsennellyn argumentin muodostaminen (Loogikko-agentti, ks. [Luku 2.3.4](#luku-2-3-4)).
3.  **Vaihe 3: Falsifiointi.** Argumentti altistetaan systemaattiselle kumoamisyritykselle (Kriitikkoryhmä, ks. [Luku 2.3.5](#luku-2-3-5)).
4.  **Vaihe 4: Synteesi ja Johtopäätökset.** Tulokset kootaan yhteen (Tuomari-agentti), ja analyysiin liittyvä epävarmuus tuodaan esiin selitettävän tekoälyn (Explainable AI, XAI; vrt. [Adadi & Berrada 2018](#adadi2018)) avulla (XAI-Raportoija-agentti, ks. [Luku 2.3.6](#luku-2-3-6)).

Tämä vaiheittainen malli on tietoinen arkkitehtuurivalinta, joka priorisoi maksimaalista auditoitavuutta ja jäljitettävyyttä tehokkuuden kustannuksella. Vaikka dynaamisemmat debatti-arkkitehtuurit voivat tuottaa syvällisempiä oivalluksia ([Du ym. 2023](#du2023)), tämä tiukasti sekventiaalinen malli valittiin perusarkkitehtuuriksi, jotta arviointiprosessi pysyy vakioituna ja mitattavana. Se pakottaa analyysin noudattamaan tiukasti falsifioinnin ja Toulminin mallin kaltaisia, ennalta määriteltyjä ja vakiintuneita loogisia rakenteita.

Operatiivisesti tämä auditoitavuus toteutuu siten, että jokainen agentti tuottaa standardoidun JSON-välitulosteen. Tämä modulaarinen rakenne edellyttää kaikkien välitulosten välittämistä prosessin loppuun. Vaikka tämä lisää datan määrää, se on strateginen valinta: se varmistaa, että lopullinen päätös perustuu koko päättelyketjuun ja mahdollistaa Tuomari-agentin suorittaman hierarkkisen konfliktinratkaisun. Nämä välitulosteet muodostavat yhdessä "kognitiivisen jäljen" koko päättelyprosessista, joka voidaan tallentaa ja tarkastaa jälkikäteen (vrt. [Luku 4.2](#luku-4-2)).

#### <a id="luku-2-3-2"></a>2.3.2 Vartija-agentti: Esikäsittely ja Turvaportti (Vaihe 1)

Operatiivinen prosessi alkaa syötteen esikäsittelyllä, jonka suorittaa Vartija-agentti. Tämä agentti toteuttaa Teknisen Kontrollikerroksen (ks. [Luku 2.4.2](#luku-2-4-2)) toiminnot: Rakenteellinen Puhdistus, Datan Normalisointi, Datan Anonymisointi ja Aktiivinen Uhkien Luokittelu.

Sen tehtävänä on torjua ulkoisia uhkia, kuten kehotemurtoja ([OWASP Foundation 2025a](#owasp2025a)). Torjunta kohdistuu erityisesti epäsuoriin kehotemurtoihin (engl. *Indirect Prompt Injection*), jotka ovat kasvava uhka kielimalleille ([Yi ym. 2025](#yi2025); [Greshake ym. 2023](#greshake2023); [Liu, X. ym. 2024](#liu2024)).

Viimeisenä valmisteluvaiheena ja ainoastaan jos turvatarkistukset on läpäisty, Vartija-agentti merkitsee datan (engl. *Input Tainting*) kokoamalla kaiken puhdistetun datan yhteen objektiin. Tämä luo perustan järjestelmän keskeiselle turvallisuussäännölle (ks. [Luku 2.4.2.4](#luku-2-4-2-4), Sääntö 1: Luottamuksen Kehä, vain vartijan hyväksymä data on validia), joka perustuu turvallisen tiedonkulun periaatteisiin ([Denning & Denning 1977](#denning1977)).

#### <a id="luku-2-3-3"></a>2.3.3 Analyytikko-agentti: Todistepohjainen Ankkurointi (Vaihe 2)

Arviointiprosessin analyysivaiheen aloittaa Analyytikko-agentti. Sen ainoa tehtävä on luoda ”todistuskartta” ja varmistaa, että kaikki myöhempi analyysi on ankkuroitu toimitettuun todistusaineistoon noudattaen Sääntöä 1 (ks. [Luku 2.4.2.4](#luku-2-4-2-4)). Se toteuttaa tämän soveltamalla RAG-tyyppistä (engl. *Retrieval-Augmented Generation*) tiedonhakustrategiaa konteksti-ikkunan sisällä ([Lewis ym. 2020](#lewis2020)), joka vähentää merkittävästi kielimallien taipumusta hallusinointiin ([Shuster ym. 2021](#shuster2021)).

RAG-arkkitehtuureilla on kuitenkin tunnettuja heikkouksia ([Ahmad ym. 2024](#ahmad2024)). Yksi merkittävä haaste on ”lost in the middle” -ilmiö, jossa mallit eivät kykene hyödyntämään tehokkaasti tietoa pitkän konteksti-ikkunan keskellä ([Liu, N. F. ym. 2024](#liu2024b)). Prototyyppivaiheessa tätä riskiä ei hallita teknisesti (esim. erillisellä uudelleensijoitusmallilla; vrt. [Ma ym. 2024](#ma2024)). Riskiä pyritään kuitenkin lieventämään operatiivisesti. Analyytikko-agentti on ohjeistettu toteuttamaan kaksivaiheisen prosessin: ensin agentti suorittaa laajan haun, minkä jälkeen se optimoi tulokset sijoittamalla tärkeimmät tulokset kontekstin alkuun ja loppuun. Tämä on kehotepohjainen strategia, joka perustuu [Liu, N. F. ym. (2024)](#liu2024b) havaintoihin. Lisäksi agenttia ohjeistetaan kirjaamaan tämä riski XAI-raportointia varten.

#### <a id="luku-2-3-4"></a>2.3.4 Loogikko-agentti: Argumentaation Rakentaminen (Vaihe 3)

Analyytikko-agentin tuottaman todistuskartan pohjalta Loogikko-agentti rakentaa muodollisen argumentin. Sen tehtävänä on muodostaa hypoteesi käyttäjän osaamistasosta soveltamalla Kognitiivista Arviointimatriisia (Taulukko 1), joka perustuu Bloomin taksonomiaan ([Anderson & Krathwohl 2001](#anderson2001)).

Loogikko-agentti jäsentää analyysinsa systemaattisesti käyttäen Toulminin argumentaatiomallia ([Toulmin 2003](#toulmin2003)). Se esittää selkeän väitteen (osaamistaso), perusteet (viittaukset todistusaineistoon) ja oikeutuksen (päättelysäännöt matriisista). Tämä vaihe muuntaa raakadatan jäsennellyksi ja auditoitavaksi argumentiksi, joka on valmis seuraavan vaiheen kriittiseen tarkasteluun.

#### <a id="luku-2-3-5"></a>2.3.5 Kriitikkoryhmä: Systemaattinen Falsifiointi (Vaihe 4)

Neljännessä vaiheessa Loogikko-agentin tuottama argumentti altistetaan systemaattiselle kumoamisyritykselle. Tämän tehtävän suorittaa Kriitikkoryhmä, joka koostuu neljästä erikoistuneesta agentista (Looginen Falsifioija-agentti, Faktuaalinen ja Eettinen Valvoja-agentti, Kausaalinen Analyytikko-agentti, Performatiivisuuden Tunnistaja-agentti).

Ryhmän tehtävä on toimia järjestelmän sisäisenä ”paholaisen asianajajana”, ja sen toiminta perustuu Karl Popperin falsifiointiperiaatteeseen: tieteellinen totuus selvitetään yrittämällä aktiivisesti kumota esitetyt väitteet ([Popper 1934](#popper1934)) (ks. [Luku 2.4.3.2](#luku-2-4-3-2), Periaate 1). Sen sijaan, että ryhmä etsisi vahvistusta Loogikko-agentin havainnoille, sen tehtävä on yrittää aktiivisesti kumota Loogikko-agentin muodostama argumentti. Tämä on kriittinen vaihe, sillä ilman aktiivista haastamista tekoälymallit sortuvat helposti ”myötäilyvinoumaan” (engl. *sycophancy*), jossa ne vain vahvistavat toistensa (mahdollisesti virheelliset) päätelmät ([Perez ym. 2022b](#perez2022b); [Wynn, Satija & Hadfield 2025](#wynn2025)).

Tämä monimutkainen auditointi on jaettu neljään erilliseen kognitiiviseen rooliin.

**2.3.5.1 Looginen Falsifioija-agentti ("Argumentaation Auditoija")**

Tämä agentti iskee argumentaation rakenteeseen. Jotta se ei sortuisi lauman mukana kulkemiseen, sille on annettu erityinen "Erimielisyyden Ylläpidon Mandaatti" (JEM) (ks. [Luku 2.4.3.2](#luku-2-4-3-2), Mandaatti 1).

* **Tehtävä:** Agentin on vastustettava "konsensuksen tyranniaa" ylläpitämällä perusteltua erimielisyyttä ([Wynn, Satija & Hadfield 2025](#wynn2025)). Se ei saa muuttaa analyysiaan vain ollakseen samaa mieltä muiden kanssa. Tätä varten se hyödyntää "punaisen tiimin" (engl. *red teaming*) menetelmiä ([Ganguli ym. 2022](#ganguli2022)).
* **Päättelyn uskollisuus (Faithfulness Audit):** Agentti tarkistaa, onko esitetty päättelyketju aito. Se etsii merkkejä siitä, että käyttäjä (tai tekoäly) on keksinyt perustelut jälkikäteen (post-hoc-rationalisointi) sen sijaan, että ne olisivat aidosti ohjanneet toimintaa ([Turpin ym. 2023](#turpin2023); [Creswell ym. 2024](#creswell2024)).
* **Rajoitteet:** Popperin falsifioinnin soveltaminen "pehmeisiin" ilmiöihin on haastavaa (ks. [Nola & Sankey 2014](#nola2014)) ja kohtaa Duhem-Quine-teesin mukaisen ongelman, jossa yksittäistä väittämää on vaikea eristää kokonaisuudesta ([Duhem 1906](#duhem1906); [Quine 1951](#quine1951)). Lisäksi tekoälyn toiminnan stokastisuus mutkistaa suoraviivaista falsifiointia ([Ganascia 2017](#ganascia2017)). Siksi tässä viitekehyksessä falsifiointia käytetään täsmätyökaluna: etsitään suoria, loogisia ristiriitoja reflektion ja keskusteluhistorian välillä hyödyntämällä argumentaatioskeemojen kriittisiä kysymyksiä ([Walton, Reed & Macagno 2008](#walton2008)).

**2.3.5.2 Faktuaalinen ja Eettinen Valvoja-agentti ("Todisteiden Valvoja")**

Tämä agentti vastaa siitä, että väitteet vastaavat todellisuutta ja noudattavat eettisiä sääntöjä. Se ei luota pelkkään annettuun tietoon, vaan kaivaa syvemmältä.

* **RFI-Protokolla (Tiedonhankinta):** Agentti suorittaa kohdennetun uusintahaun (Request for Information Protocol) (ks. [Luku 2.4.3.1](#luku-2-4-3-1), Protokolla 3). Nykyisessä prototyypissä, jossa ei ole integroitua verkkohakutyökalua, tämä vaihe toteutetaan hyödyntämällä mallin sisäistä tietämystä ja kontekstin ristiintarkistusta (engl. *Simulated Retrieval*).
* **Kyselynlaajennus:** Hakulausekkeiden muokkaaminen uusista näkökulmista ([Jagerman ym. 2023](#jagerman2023)).
* **HyDE (Hypothetical Document Embeddings):** Agentti kuvittelee ideaalin dokumentin, joka kumoaisi väitteen, ja käyttää sitä hakuna ([Gao ym. 2022](#gao2022)).
* **Heterogeenisyyden välttämättömyys:** Järjestelmän luotettavuus paranee merkittävästi, jos tämä vaihe ajetaan eri tekoälymallilla (esim. GPT-4) kuin aiemmat vaiheet (esim. Gemini) ([Ye ym. 2025](#ye2025)) (ks. [Luku 2.4.2.4](#luku-2-4-2-4), Vaatimus 1). Jos kaikki agentit käyttävät samaa mallia, ne saattavat toistaa samat virheet ja hallusinaatiot ("sokeat pisteet") ([Cemri ym. 2025](#cemri2025)). Eri mallien käyttö mahdollistaa aidon ristiinvalidoinnin.
* **Eettinen tarkastus:** Agentti etsii aktiivisesti vakavia eettisiä rikkomuksia, kuten syrjintää tai lähteiden tahallista vääristelyä ([Weidinger ym. 2021](#weidinger2021)).

**2.3.5.3 Faktuaalinen Verifiointiprotokolla (Google Search API)**

Osana Faktuaalisen ja Eettisen Valvoja-agentin toimintaa, järjestelmä toteuttaa automatisoidun "Faktuaalisen Verifiointiprotokollan". Mekanismi on suunniteltu torjumaan kielimallien taipumusta hallusinointiin ([Shuster ym. 2021](#shuster2021)) ankkuroimalla väitteet ulkoiseen, todennettavaan tietoon. Tämä implementaatio hyödyntää reaaliaikaista verkkohakua (Google Custom Search JSON API), mikä mahdollistaa aidon episteemisen validoinnin.

Protokolla etenee kolmivaiheisena prosessina, joka suoritetaan orkestrointikerroksessa ennen varsinaista agenttianalyysiä:

1.  **Väitteiden Ekstraktio (Claim Extraction):** Ensimmäisessä vaiheessa järjestelmä aktivoi kevyen kielimallin (Gemini 2.5 Flash) suorittamaan semanttisen seulonnan. Mallille syötetään Lopputuote ja Reflektiodokumentti, ja sitä ohjeistetaan tunnistamaan kolme (3) keskeisintä faktaväitettä, jotka ovat alttiita virheille. Seulonta priorisoi väitteitä, jotka sisältävät spesifejä vuosilukuja, historiallisia tapahtumia, henkilöitä tai tieteellisiä faktoja, noudattaen periaatetta, jonka mukaan "kovat faktat" ovat tehokkain falsifioinnin kohde ([Popper 1934](#popper1934)).
2.  **Ulkoinen Todistusaineiston Haku (External Evidence Retrieval):** Tunnistetut väitteet syötetään SearchService-komponentille, joka suorittaa kohdennetut haut Google Custom Search API:n kautta. Tämä vaihe on kriittinen "maailmanmallin" laajentamiseksi kielimallin staattisen koulutusdatan ulkopuolelle (vrt. [Lewis ym. 2020](#lewis2020)). Järjestelmä hakee kullekin väitteelle kaksi (2) relevantinta lähdettä ja eristää niistä tiivistelmät (snippet) ja metatiedot (lähde, URL).
3.  **Kontekstuaalinen Injektio (Contextual Injection):** Lopuksi hakutulokset injektoidaan suoraan Faktuaalisen ja Eettisen Valvoja-agentin konteksti-ikkunaan (Prompt Injection). Tämä muuttaa agentin tehtävän pelkästä tekstianalyysistä "todistusaineistoon perustuvaksi vertailuksi" (Evidence-Based Verification). Agentti saa käyttöönsä strukturoidun raportin:
    * Väite X (Dokumentista)
    * Ulkoinen Lähde Y (Google Search)
    * Verifiointitulos: Ristiriita / Vahvistus.

Mikäli ulkoinen haku epäonnistuu (esim. API-avainten puuttuessa), järjestelmä palautuu automaattisesti käyttämään aiemmin kuvattua "simuloitua hakua" (Simulated Retrieval), mutta kirjaa tämän metodologiseksi rajoitteeksi (XAI-raportointi). Tämä hybridimalli varmistaa, että falsifiointiprosessi säilyttää toimintakykynsä kaikissa olosuhteissa, mutta priorisoi aina empiiristä dataa sen ollessa saatavilla (vrt. [Trivedi ym. 2024](#trivedi2024)).

**2.3.5.4 Kausaalinen Analyytikko-agentti ("Temporaalinen Auditoija")**

Tämän agentin tehtävä on auditoida prosessin ajallista johdonmukaisuutta ja kausaalista uskottavuutta soveltamalla seuraavia heuristiikkoja (ks. [Luku 2.4.3.4](#luku-2-4-3-4), Heuristiikat 1–3):

* **Temporaalinen auditointi:** Agentti tarkistaa aikajanan: ilmestyikö oivallus (syy) keskusteluhistoriaan ennen tuloksen paranemista (seuraus)? Syyn on aina edellettävä seurausta ([Hume 1739](#hume1739); [Lagnado & Sloman 2006](#lagnado2006); [Pearl 2009](#pearl2009)).
* **Kontrafaktuaalinen stressitesti (L3-simulaatio):** Agentti kysyy: 'Jos käyttäjä EI olisi tehnyt tätä oivallusta, olisiko tulos silti ollut sama?'. Tämä on yritys simuloida syvällistä syy-seuraus-päättelyä ([Pearl 2009](#pearl2009); [Sgaier ym. 2020](#sgaier2020)).
* **Abduktiivinen Haasto:** Agentti soveltaa Occamin partaveistä (vrt. [Walton ym. 2008](#walton2008)). Se arvioi, onko käyttäjän kuvaama oivallus yksinkertaisin selitys havaitulle muutokselle, vai onko post-hoc rationalisointi todennäköisempi selitys.

**2.3.5.5 Performatiivisuuden Tunnistaja-agentti ("Käyttäytymisanalyytikko")**

Tämä agentti keskittyy tunnistamaan käyttäytymismalleja ja pelistrategioita, jotka viittaavat järjestelmän manipulointiin (Goodhartin laki) ([Strathern 1997](#strathern1997); [Stumborg ym. 2022](#stumborg2022)). Tätä ohjaa mandaatti (ks. [Luku 2.4.3.2](#luku-2-4-3-2), Mandaatti 4). Agentti etsii useita indikaattoreita:

* **Epäuskottava lineaarisuus:** Onko prosessi liian suoraviivainen ja virheetön ollakseen totta? (vrt. [Goffman 1959](#goffman1959)).
* **Pinnallinen vuorovaikutus:** Osoittaako keskusteluhistoria vain vähäistä kognitiivista syvyyttä?
* **Kognitiivinen epäsuhta:** Vastaako reflektiossa kuvattu prosessi keskusteluhistorian todellista kulkua? Tämä analyysi perustuu kognitiivisen dissonanssin tunnistamiseen ([Festinger 1957](#festinger1957)).
* **Keinotekoinen monimutkaisuus:** Onko prosessiin lisätty turhia vaiheita vain näyttävyyden vuoksi? ([Cullen 2020](#cullen2020)).
* **Matriisin optimointi:** Vastaako reflektio epäilyttävän tarkasti arviointikriteereitä, vaikka itse työskentely ei? ([Strathern 1997](#strathern1997); [Stumborg ym. 2022](#stumborg2022)).
* **Kognitiivinen investointi:** Vastaako oivallukseen käytetty kognitiivinen työpanos sen väitettyä merkittävyyttä (vrt. [de Bruin ym. 2023](#debruin2023))?
* **Itsetehostuksen Indikaattorit:** Etsitään merkkejä itsetehostusvinoumasta ([Dufner ym. 2019](#dufner2019)).
* **Pre-Mortem Analyysi:** Agentti kääntää todistustaakan olettamalla reflektion olevan väärennös ja etsimällä tätä tukevia signaaleja ([Klein 2007](#klein2007)).
* **Tilastollinen Anomaliantunnistus ("Epäilyttävä Täydellisyys"):** Viitekehys soveltaa periaatetta, jonka mukaan oppimisprosessi on harvoin lineaarinen ja virheetön (ks. [Luku 2.4.3.2](#luku-2-4-3-2), Sääntö 4). Jos suoritus saa maksimaaliset pisteet kaikilla mittareilla ilman prosessissa näkyvää kitkaa tai iterointia, se liputetaan automaattisesti "Epäilyttävän Täydelliseksi". Tämä perustuu havaintoon, että liiallinen silottelu (engl. *over-smoothing*) on usein merkki tekoälyn generoimasta tai performatiivisesta narratiivista ([Cullen 2020](#cullen2020)).

On kuitenkin huomattava, että ilman ulkoista maailmanmallia kielimalli ei kykene muodolliseen kausaaliseen päättelyyn ([Chi ym. 2024](#chi2024)), joten näiden agenttien (Kausaalinen Analyytikko-agentti ja Performatiivisuuden Tunnistaja-agentti) suorittamat testit mittaavat ensisijaisesti narratiivin loogista eheyttä eivätkä sen empiiristä totuusarvoa. Siksi nämä testit ovat "kielellisiä approksimaatioita" – ne ovat parhaita mahdollisia arvauksia, eivät matemaattisen tarkkoja todisteita. Tämä tekee järjestelmästä haavoittuvan taitavalle manipuloinnille.

#### <a id="luku-2-3-6"></a>2.3.6 Tuomari- ja XAI-Raportoija-agentit: Synteesi ja Raportointi (Vaihe 5)

Viimeisessä vaiheessa, kun "käräjät" on käyty, Tuomari-agentti kokoaa tulokset. Tämä ei ole pelkkä keskiarvo, vaan hierarkkinen konfliktinratkaisu, joka noudattaa tiukkoja sääntöjä:

* **Falsifioinnin etusija:** Faktat voittavat aina tulkinnat ([Popper 1934](#popper1934)) (ks. [Luku 2.4.3.4](#luku-2-4-3-4), Sääntö 6). Jos Faktuaalinen ja Eettinen Valvoja-agentti löytää faktavirheen tai eettisen rikkomuksen, se syrjäyttää Loogikko-agentin positiivisen tulkinnan "mestaruudesta".
* **Jäsennellyn erimielisyyden mandaatti (JEM):** Jos Kriitikkoryhmän agentit ja Loogikko-agentti ovat eri mieltä tulkinnasta, Tuomari-agentti ei saa pakottaa niitä yksimielisyyteen (ks. [Luku 2.4.3.2](#luku-2-4-3-2), Mandaatti 1). Erimielisyys on arvokasta tietoa, joka paljastaa tapauksen monimutkaisuuden ([Wynn, Satija & Hadfield 2025](#wynn2025)).

Lopuksi XAI-Raportoija-agentti laatii raportin, joka noudattaa [Adadi ja Berradan (2018)](#adadi2018) kuvaamia periaatteita (XAI). Se ei vain kerro tulosta, vaan tekee näkyväksi kaiken epävarmuuden erottelemalla sen lähteet ([Der Kiureghian & Ditlevsen 2009](#derkiureghian2009); [Hüllermeier & Waegeman 2021](#hullermeier2021)):

* **Aleatorinen epävarmuus:** Datan epäselvyydestä johtuva epävarmuus.
* **Systeeminen epävarmuus:** Itse järjestelmän rajoituksista (esim. kehotteiden hauraus, kausaalipäättelyn puute) johtuva epävarmuus.
* **Episteeminen epävarmuus:** Agenttien välisestä erimielisyydestä johtuva epävarmuus.

XAI-raportti tiivistää nämä epävarmuustekijät "Luotettavuusasteeksi" (engl. *Reliability Score*). Mikäli järjestelmä ei pysty varmentamaan arkkitehtuurin eheyttä (esim. heterogeenisyyden puute; ks. [Luku 2.4.2.4](#luku-2-4-2-4), Vaatimus 1), luotettavuusaste laskee automaattisesti tasolle "EHDOLLEINEN", mikä signaloi ihmisvalvojalle pakollista tarkistustarvetta noudattaen Protokollaa 4 (ks. [Luku 2.4.3.3](#luku-2-4-3-3)).

Tämä läpinäkyvyys on turvallisuustekijä. Raportti pakottaa ihmisvalvojan (HITL) ottamaan kantaa kriittisiin kysymyksiin (”Kriittiset Auditointikysymykset”) ja varmistaa näin, ettei tekoälyn päätöstä hyväksytä sokeasti (ks. [Luku 2.4.4.1](#luku-2-4-4-1)).

Tämän lisäksi Tuomari-agentin päätöksentekoa ohjaa kooditasolle rakennettu deterministinen rangaistusmekanismi (engl. *Deterministic Penalty Rules*). Tämä mekanismi toimii varovaisuusperiaatteen mukaisena "hätäjarruna", joka ohittaa agentin inhimillisen harkinnan kriittisissä virhetilanteissa (vrt. [Kahneman 2011](#kahneman2011)). JudgeAgent-komponentin logiikka pakottaa arvosanat laskemaan automaattisesti, mikäli edeltävät vaiheet ovat liputtaneet fataaleja virheitä:

* **Turvallisuusuhka (Security Threat):** Mikäli Vartija-agentti havaitsee tietoturvariskin, kaikkien osa-alueiden pisteet leikataan automaattisesti alimpaan mahdolliseen (Arvosana 1), riippumatta sisällön laadusta (vrt. [OWASP Foundation 2025a](#owasp2025a)).
* **Looginen virhe (Logical Fallacy):** Mikäli Falsifioija havaitsee kriittisen "post-hoc-rationalisoinnin" tai muun päättelyvirheen, arvosana katetaan korkeintaan välttävään tasoon (Arvosana 2) (vrt. [Turpin ym. 2023](#turpin2023)).

Tämä varmistaa, että järjestelmä ei koskaan palkitse vaarallista tai loogisesti epärehellistä toimintaa, vaikka se olisi retorisesti vakuuttavaa.

#### <a id="luku-2-3-7"></a>2.3.7 Valmentaja-agentti: Oppimispolun Rikastaminen

Prosessin viimeisenä vaiheena, arvioinnin (summative assessment) valmistuttua, järjestelmä aktivoi Valmentaja-agentin (Coach Agent). Sen tehtävänä on kääntää Tuomari-agentin tuottama arvio formatiiviseksi oppimissuunnitelmaksi (vrt. [Wiggins 1998](#wiggins1998)). Tämä vaihe ei vaikuta enää arvosanaan, vaan tähtää käyttäjän metakognitiivisten taitojen kehittämiseen (vrt. [Flavell 1979](#flavell1979)).

Valmentaja-agentin toiminta perustuu "rikastetun palautteen" periaatteeseen (engl. Enriched Feedback). Agentti hyödyntää sisäistä tietokantaansa (Knowledge Base), joka sisältää kuratoidun kokoelman alan keskeistä kirjallisuutta ja käsitteitä. Agentin `enrich_learning_plan`-metodi suorittaa kaksivaiheisen prosessin:

1.  **Kontekstuaalinen haku:** Agentti skannaa käyttäjän suorituksesta ja Tuomarin arviosta tunnistetut kehityskohteet.
2.  **Viitteiden injektio:** Agentti etsii tietokannastaan (esim. JSON-muotoinen Unified Database) kuhunkin kehityskohteeseen sopivat akateemiset lähteet ja liittää ne suoraan palautteeseen.

Tämä mekanismi varmistaa, että palaute ei ole vain geneeristä kehotusta "parantaa suoritusta", vaan se tarjoaa konkreettiset, tieteellisesti validoidut työkalut (esim. "vrt. Strathern 1997") osaamisen syventämiseen (vrt. [Shavelson 2013](#shavelson2013)). Toiminnallisuus toteuttaa käytännössä Bloom’n taksonomian ylemmän tason tavoitteen tiedon soveltamisesta ja arvioinnista ([Anderson & Krathwohl 2001](#anderson2001)).

### <a id="luku-2-4"></a>2.4 Hallintamalli ja Monikerroksinen Puolustusstrategia (DiD)

Kun arkkitehtuurin rakenne ja operatiivinen prosessi on kuvattu, tämä viimeinen osio keskittyy järjestelmän eheyden, turvallisuuden ja luotettavuuden varmistaviin mekanismeihin. Arkkitehtoniset tasot edellyttävät selkeää hallintamallia, joka muodostaa hierarkkisen kontrollirakenteen. Osio kuvaa hallintamallin, joka on toteutettu monikerroksisena puolustusstrategiana (Defense-in-Depth). Se määrittelee tekniset, behavioraaliset ja hallinnolliset kontrollikerrokset, jotka läpileikkaavat koko arkkitehtuuria ja ohjaavat operatiivista prosessia.

#### <a id="luku-2-4-1"></a>2.4.1 Puolustusstrategian Yleiskuvaus ja Rajoitteet

Järjestelmän eheyden varmistamiseksi hallintamalli toteutetaan monikerroksisena puolustusstrategiana, joka torjuu kielimalleihin liittyviä uhkia ([OWASP Foundation 2025f](#owasp2025f)). Strategia perustuu monikerroksisen puolustuksen (engl. *Defense in Depth*, DiD) -malliin ([CISA 2016](#cisa2016)) ja koostuu kolmesta toisiaan täydentävästä kontrollikerroksesta:

1.  **Tekninen Kontrollikerros** ([Luku 2.4.2](#luku-2-4-2)) suojaa ensisijaisesti ulkoisilta uhilta, kuten kehotemurroilta (LLM01:2025).
2.  **Behavioraalinen Kontrollikerros** ([Luku 2.4.3](#luku-2-4-3)) hallitsee agenttien sisäistä toimintaa ja torjuu toimivallan ylittämistä (LLM06:2025).
3.  **Hallinnollinen Kontrollikerros** ([Luku 2.4.4](#luku-2-4-4)) toimii ylimpänä valvontamekanismina (Ihmisvalvonta, HITL).

Prototyypin nykytilassa järjestelmän turvallisuutta ja luotettavuutta rajoittaa useiden kehittyneiden teknisten toimintojen puuttuminen. Näitä ovat "Semanttinen Anonymisointi", "Upotusten Eheyden Tarkistus" ja "Uudelleensijoitusmalli". Lisäksi on kriittistä tunnustaa, että prototyypissä monet kontrollit (erityisesti Teknisessä ja Behavioraalisessa kerroksessa) on toteutettu kehotepohjaisina simulaatioina, jotka emuloivat tuotantoympäristön teknisiä kontrolleja, mutta eivät korvaa niitä (vrt. [Jia ym. 2025](#jia2025)).

#### <a id="luku-2-4-2"></a>2.4.2 Tekninen Kontrollikerros

Ensimmäinen puolustuslinja suojaa ulkoisilta teknisiltä uhilta. Tämä kerros toteutetaan operatiivisen prosessin Vartija-agentin toimesta (ks. [Luku 2.3.2](#luku-2-3-2)). Vartija-agentti toimii turvaporttina, joka suorittaa syötteiden validoinnin ja puhdistuksen.

**2.4.2.1 Rakenteellinen Puhdistus (Input Sanitization) ja Datan Normalisointi**

Tämä vaihe yhdistää turvallisuuskontrollit ja datan eheyden varmistamisen. Ensimmäisenä puolustuslinjana ([OWASP Foundation s.a](#owaspsa)) Vartija-agentin tehtävä on muuntaa kaikki syötteet (esim. PDF, DOCX) raakatekstiksi. Tämä pienentää hyökkäyspinta-alaa ja varmistaa datan yhdenmukaisuuden ([OWASP Foundation 2025d](#owasp2025d)). Tähän prosessiin kuuluu pakollinen datan normalisointi, joka on kriittistä merkistön eheyden ja interoperabiliteetin varmistamiseksi, erityisesti manuaalisessa orkestroinnissa (vrt. [Luku 5.2.4](#luku-5-2-4); [W3C 2008](#w3c2008)). Normalisointi sisältää pakollisen UTF-8-merkistökoodauksen varmistamisen sekä typografisten merkkien (kuten "älykkäiden lainausmerkkien") muuntamisen standardeiksi ASCII-merkeiksi. Tämän jälkeen se poistaa aktiivisesti kaikki tunnetut haitalliset merkit, skriptit ja ohjausmerkit (engl. *control characters*).

**2.4.2.2 Datan Anonymisointi (OWASP LLM02:2025-torjunta)**

Tämä vaihe torjuu arkaluontoisen tiedon paljastumista. Vartija-agentin tehtävä on hakea ja peittää tunnistettavat henkilötiedot (PII) monikerroksisesti (vrt. [Lison ym. 2021](#lison2021); [Li ym. 2024](#li2024)). Prototyyppivaiheessa ulkoisilla kirjastoilla toteutettu deterministinen anonymisointi puuttuu. Tämä korvataan agenttipohjaisella hybridimallilla, joka yhdistää kohdennetut sääntöpohjaiset (RegEx) menetelmät (esim. HETU, sähköposti) kielimallin suorittamaan laajempaan kontekstuaaliseen PII-analyysiin. Tämä mahdollistaa epätyypillisten henkilötietojen tunnistamisen (vrt. [Li ym. 2024](#li2024)), vaikka menetelmä sisältääkin stokastisen epävarmuuden.

**2.4.2.3 Aktiivinen Uhkien Luokittelu (OWASP LLM01:2025-torjunta)**

Tämä vaihe on suora vastaus epäsuorien kehotemurrosten uhkaan. Viitekehyksen visiona on käyttää erillistä teknistä luokittelijaa. Nykyinen prototyyppitoteutus toteuttaa tämän kontrollin kehotepohjaisena 'semanttisena perustuslakitarkistuksena' (vrt. [Bai ym. 2022](#bai2022)) käyttäen menetelmää:

* **Menetelmä 1 (Adversariaalinen Simulaatio):** Vartija-agentti pakotetaan suorittamaan monivaiheinen uhka-analyysi sisäisessä päättelytilassa (engl. *scratchpad*), omaksumalla ensin "Punaisen Tiimin" (Hyökkääjä) rooli ja simuloimalla hyökkäystä, ja sen jälkeen "Sinisen Tiimin" (Puolustaja) rooli arvioimalla sen onnistumista.
    * **Perustuu:** Syötteen intention syvempi ymmärtäminen, (vrt. [Perez ym. 2022a](#perez2022a)).
    * **Koskee:** Vartija-agentti.

Tämä luo kuitenkin perustavanlaatuisen arkkitehtonisen ristiriidan ja puolustuksellisen paradoksin: järjestelmä pyrkii torjumaan kehotemurtoja (LLM01) käyttämällä menetelmää (kehotepohjainen kontrolli), joka itsessään on haavoittuvin juuri kyseiselle hyökkäykselle. Ilman ulkoista luokittelijaa tämä kontrolli on katsottava 'syvyyspuolustukseksi' eikä täydelliseksi ratkaisuksi. Tämä on tunnistettu merkittävä tekninen rajoite ja haurauden lähde (vrt. [Jia ym. 2025](#jia2025); [Liu, Y. ym. 2023](#liu2023)).

#### <a id="luku-2-4-2-4"></a>2.4.2.4 Lisäkontrollit ja Rajoitteet

* **Upotusten Eheyden Tarkistus (OWASP LLM08:2025-Torjunta):** Viitekehyksen visioon kuuluu Vartija-agentin kyky tunnistaa RAG-arkkitehtuuriin kohdistuvia hyökkäyksiä suorittamalla ajonaikainen poikkeamien havaitseminen upotustilassa (vrt. [Zilliz 2024](#zilliz2024); [OWASP Foundation 2025e](#owasp2025e)). Nykyisessä prototyypissä tämä kontrolli on toteutettu ainoastaan protokollalla:
    * **Protokolla 1 (Negatiivinen Lokikirjaus):** Järjestelmä pakottaa Vartija-agentin kirjaamaan puuttuvan teknisen suojauksen eksplisiittiseksi riskiksi ('LLM08-riski hallitsematon'), mikä tekee haavoittuvuudesta läpinäkyvän (XAI) mutta ei poista sitä teknisesti.
    * **Perustuu:** Läpinäkyvyys ja riskienhallintakäytännöt, ([OWASP Foundation 2025e](#owasp2025e)).
    * **Koskee:** Vartija-agentti.
* **Datan Merkintä (engl. *Input Tainting*):** Puhdistetun datan kokoaminen yhteen objektiin (ks. [Luku 2.3.2](#luku-2-3-2)), joka luo perustan Säännölle 1 (Luottamuksen Kehä).
* **Sääntö 1 (Luottamuksen Kehä / Chain of Trust):** Vain Vartija-agentin hyväksymä ja merkitsemä data on tarkistettua. Tämä on kriittinen kontrolli, sillä järjestelmän behavioraaliset säännöt pakottavat kaikki myöhemmät agentit käsittelemään ainoastaan tätä tarkistettua dataa.
    * **Perustuu:** Turvallisen tiedonkulun perusperiaatteet, ([Denning & Denning 1977](#denning1977)).
    * **Koskee:** Kaikki agentit.
* **Vaatimus 1 (Heterogeenisyyden Välttämättömyys):** Järjestelmän luotettavuus paranee merkittävästi, jos kriittiset vaiheet (erityisesti Falsifiointi) ajetaan eri tekoälymallilla (esim. GPT-4) kuin aiemmat vaiheet (esim. Gemini).
    * **Perustuu:** Mallien sokeiden pisteiden välttäminen, ([Ye ym. 2025](#ye2025); [Cemri ym. 2025](#cemri2025)).
    * **Koskee:** Erityisesti Faktuaalinen ja Eettinen Valvoja-agentti (Järjestelmätason vaatimus).

#### <a id="luku-2-4-3"></a>2.4.3 Behavioraalinen Kontrollikerros (Kognitiivinen Palomuuri)

Järjestelmän toinen puolustuslinja on Behavioraalinen Kontrollikerros, joka toimii *Kognitiivisena Palomuurina*. Se on agentteja ohjaava periaatteellinen rajoituskokonaisuus. Tämän kerroksen ensisijaisena tehtävänä on hallita agenttien sisäistä toimintaa, varmistaa prosessin eheys, lieventää kognitiivisia vinoumia ja ohjata holistista arviointia.

**<a id="luku-2-4-3-1"></a>2.4.3.1 Prosessin Eheys ja Toimivallan Rajaaminen**

Järjestelmän eheyden varmistamiseksi jokaisen agentin on suoritettava pakollinen, standardoitu validointiprotokolla ennen tehtävänsä aloittamista:

* **Protokolla 2 (Kolmivaiheinen Validointi):**
    * **Rakenteellinen eheys ja puhdistus:** Syötteen JSON-muodon validointi ja tarvittaessa virheensietoinen jäsennys (engl. *robust parsing*) eli "aggressiivinen puhdistus". Tämä mekanismi pyrkii pelastamaan JSON-objektin poistamalla tunnettuja formaattivääristymiä (esim. Markdown-jäänteitä).
    * **Semanttinen eheys (Tarkistussumma):** Datan sisällön vertaaminen edellisen vaiheen generoimaan semanttiseen tarkistussummaan (ks. [Luku 5.2.4](#luku-5-2-4)).
    * **Rakenteellinen skeptisyys:** Syötteen rakenteen kriittinen tarkastelu anomaliatunnisteiden havaitsemiseksi, mikä toimii sekundaarisena suojana kehotemurtoja (LLM01) vastaan.
    * **Perustuu:** Syötteen validoinnin parhaat käytännöt, ([OWASP Foundation s.a.](#owaspsa)).
    * **Koskee:** Kaikki agentit.

Lisäksi tiedonhankinnan eheyden varmistamiseksi sovelletaan seuraavaa protokollaa:

* **Protokolla 3 (RFI-Protokolla - Tiedonhankinta):** Agentti suorittaa kohdennetun uusintahaun (Request for Information Protocol). Prototyypissä tämä toteutetaan simuloituna hakuna (Simulated Retrieval) käyttäen mallin sisäistä tietämystä ja kontekstin ristiintarkistusta.
    * **Perustuu:** Iteratiivinen ja dynaaminen tiedonhaku, (vrt. [Trivedi ym. 2024](#trivedi2024)).
    * **Koskee:** Faktuaalinen ja Eettinen Valvoja-agentti.

Puolustusstrategia hyödyntää redundanssia. Kaikkia agentteja velvoitetaan ylläpitämään rakenteellista skeptisyyttä. Lisäksi sovelletaan menetelmää:

* **Menetelmä 2 (Ristiinvalidoiva Päättelyketju / Cross-Validating Chain-of-Thought):** Agentit pakotetaan validoimaan edeltävän agentin päättelyn looginen johdonmukaisuus ja ankkurointi todistusaineistoon ennen oman prosessinsa käynnistämistä.
    * **Perustuu:** Päättelyketjun looginen validointi, ([Ye ym. 2025](#ye2025); [Cemri ym. 2025](#cemri2025)).
    * **Koskee:** Kaikki agentit.

Lisäksi järjestelmä asettaa tiukat rajoitteet estääkseen toimivallan ylittymisen (engl. *excessive agency*) ([OWASP Foundation 2025d](#owasp2025d)).

* **Sääntö 2 (Toimivallan Rajaaminen / Työkalukielto):** Rajoitteet kieltävät agentteja hyödyntämästä määrittelemättömiä ulkoisia työkaluja tai API-rajapintoja.
    * **Perustuu:** Työkaluhavoittuvuuksien torjunta ja vähimmät oikeudet, ([Research AIMultiple 2025](#aimultiple2025); [Saltzer & Schroeder 1975](#saltzer1975)).
    * **Koskee:** Kaikki agentit.

Samalla ehkäistään systeemisiä riskejä, kuten roolivuotoa (engl. *role-bleed*), jossa agentti ylittää sille määritellyn kognitiivisen roolin rajat ([Yeager.ai 2023](#yeager2023)).

**<a id="luku-2-4-3-2"></a>2.4.3.2 Operatiiviset Mandaatit (Perustuslaki)**

Kognitiivista Palomuuria ylläpidetään neljällä peruuttamattomalla mandaatilla (`seed_data.json` -> `HEADER_MANDATES`), jotka on injektoitu jokaisen agentin "sieluun" (System Prompt). Nämä ovat hierarkkisesti kaikkien muiden ohjeiden yläpuolella:

* **Mandaatti 1 (Järjestelmä 2 -Pakko / System 2 Mandatory):** Agentin on käytettävä hidasta, deliberatiivista päättelyä (System 2). Nopea, intuitiivinen vastaaminen (System 1) on kielletty. Agentin on tuotettava 'sisäistä monologia' (reasoning trace) ennen lopputuloksen generointia. Tämä mahdollistaa mm. Jäsennellyn Erimielisyyden (JEM) ylläpidon.
* **Mandaatti 2 (Vinoumien Torjunta / Bias Prevention):** Agentin on aktiivisesti tunnistettava ja kumottava omat kognitiiviset vinoumansa, erityisesti vahvistusvinouma (Confirmation Bias) ja myötäilyvinouma (Sycophancy).
* **Mandaatti 3 (Insinöörimäinen Nöyryys / Engineering Humility):** Agentin on tunnustettava tietonsa rajat. Hallusinaatio on fataali virhe. Jos tietoa ei ole, se on myönnettävä (Unknown Unknowns).
* **Mandaatti 4 (Performatiivisuuden Tunnistus / Anti-Goodhart):** Agentin on tunnistettava yritykset pelata järjestelmää (Goodhartin laki). Pinnallinen muodon matkiminen ei ole mestaruutta.

**<a id="luku-2-4-3-3"></a>2.4.3.3 Säännöt (Rules of Engagement)**

Mandaattien lisäksi järjestelmä noudattaa tarkkaa säännöstöä (`HEADER_RULES`), joka ohjaa agenttien vuorovaikutusta:

* **Sääntö 1 (Luottamuksen Kehä / Trust Circle):** Vain Vartija-agentin (Guard) merkitsemä data on luotettavaa. Agentit eivät saa luottaa syötteeseen, josta puuttuu kryptografinen (tai simuloitu) eheysleima.
* **Sääntö 2 (Toimivalta / Jurisdiction):** Agentti ei saa keksiä faktoja tyhjästä. Kaiken analyysin on ankkuroiduttava syötettyyn dataan (`HISTORY_TEXT`, `PRODUCT_TEXT`, `REFLECTION_TEXT`).
* **Sääntö 3 (Substanssi > Muoto / Substance over Style):** Arvioinnin on perustuttava asiasisältöön, ei kielenhuollolliseen sujuvuuteen tai ulkoasuun (Lievittää esteettistä vinoumaa).
* **Sääntö 4 (Epäilyttävä Täydellisyys / Suspicious Perfection):** Jos prosessi on kitkaton ja virheetön, se on epäilyttävää. Aito oppiminen sisältää virheitä. Täydellisyys liputetaan anomaliana.
* **Sääntö 5 (Hauraus / Epistemic Uncertainty):** XAI-raportin on aina eriteltävä epävarmuuden lähteet. Väärä varmuus on pahempaa kuin tietämättömyys.
* **Sääntö 6 (Falsifiointi / Falsification):** Falsifiointi on ensisijaista verifiointiin nähden. Yksi todistettu virhe kumoaa sata kaunista lausetta ([Popper 1934](#popper1934)).

**<a id="luku-2-4-3-4"></a>2.4.3.4 Behavioraalisen Kerroksen Rajoitteet**

On kriittistä tunnustaa, että nykyisessä implementaatiossa Kognitiivinen Palomuuri toimii ensisijaisesti deklaratiivisena normatiivisena ohjauskerroksena, ei teknisesti läpäisemättömänä esteenä (vrt. [Greshake ym. 2023](#greshake2023)). Koska kehotteet eivät voi teknisesti täysin estää agenttia toimimasta virheellisesti, behavioraalista kerrosta on täydennettävä pakollisilla teknisillä kontrolleilla tuotantoympäristössä.

Prototyypissä tätä haurautta hallitaan läpinäkyvyyden (XAI) ja vastuun siirtämisen (HITL) kautta:

* **Protokolla 4 (Vastuun Siirtäminen, HITL):** Järjestelmä siirtää tietoisesti kriittiset vastuut (kuten heterogeenisyyden varmistamisen; Vaatimus 1) ihmisvalvojalle (HITL).
* **Pakollinen Haurauden Raportointi:** XAI-Raportoija-agentin on pakko kirjata kehotepohjaisen kontrollin hauraus Systeemiseksi Epävarmuudeksi jokaiseen raporttiin (Sääntö 5).

Visio edellyttää siirtymistä teknisiin perustuslaillisiin luokittelijoihin (engl. *Constitutional Classifiers*) ([Anthropic 2025a](#anthropic2025a)), jotka tarjoavat vahvemman suojan ([Sharma ym. 2025](#sharma2025)).

**<a id="luku-2-4-3-4"></a>2.4.3.4 Deduktiiviset ja Loogiset Kontrollit**

Tämä osio kokoaa yhteen järjestelmän käyttämät loogiset ja deduktiiviset kontrollimekanismit, joita sovelletaan analyysi- ja falsifiointivaiheissa.

* **Heuristiikka 1 (Temporaalinen auditointi):** Agentti tarkistaa aikajanan: ilmestyikö oivallus (syy) keskusteluhistoriaan ennen tuloksen paranemista (seuraus)? Syyn on aina edellettävä seurausta.
    * **Perustuu:** Syyn ja seurauksen ajallinen järjestys, ([Hume 1739](#hume1739); [Lagnado & Sloman 2006](#lagnado2006); [Pearl 2009](#pearl2009)).
    * **Koskee:** Kausaalinen Analyytikko-agentti.
* **Heuristiikka 2 (Kontrafaktuaalinen stressitesti, L3-simulaatio):** Agentti kysyy: 'Jos käyttäjä EI olisi tehnyt tätä oivallusta, olisiko tulos silti ollut sama?'. Tämä on yritys simuloida syvällistä syy-seuraus-päättelyä.
    * **Perustuu:** Syvällinen syy-seuraus-päättely (kontrafaktuaalit), ([Pearl 2009](#pearl2009); [Sgaier ym. 2020](#sgaier2020)).
    * **Koskee:** Kausaalinen Analyytikko-agentti.
* **Heuristiikka 3 (Abduktiivinen Haasto):** Agentti soveltaa Occamin partaveistä. Se arvioi, onko käyttäjän kuvaama oivallus yksinkertaisin selitys havaitulle muutokselle, vai onko post-hoc rationalisointi todennäköisempi selitys.
    * **Perustuu:** Päättely parhaaseen selitykseen (Occamin partaveitsi), (vrt. [Walton ym. 2008](#walton2008)).
    * **Koskee:** Kausaalinen Analyytikko-agentti.
* **Sääntö 6 (Falsifioinnin Etusija):** Faktat voittavat aina tulkinnat. Jos Faktuaalinen ja Eettinen Valvoja-agentti löytää faktavirheen tai eettisen rikkomuksen, se syrjäyttää Loogikko-agentin positiivisen tulkinnan "mestaruudesta".
    * **Perustuu:** Faktojen priorisointi tulkintojen yli (Periaate 1), ([Popper 1934](#popper1934)).
    * **Koskee:** Tuomari-agentti.

#### <a id="luku-2-4-4"></a>2.4.4 Hallinnollinen Kontrollikerros (Ihmisvalvonta, HITL)

Viimeinen kontrollitaso auditoi ja valvoo prosessia. Hallintamallin kulmakivi on pakollinen Ihmisvalvonta (engl. *Human-in-the-Loop*, HITL), joka toimii ylimpänä suojana monimutkaisia uhkia vastaan. Sen toiminta perustuu valvontaohjattuun automaatioon ja heijastelee EU:n tekoälysääntelyn periaatteita (AI Act, Art. 14) ([Euroopan komissio 2024a](#eu2024)). EU:n eettiset ohjeet määrittelevät valvonnan kolmitasoiseksi: "Human-in-the-Loop" (suom. ihminen prosessissa mukana), "Human-on-the-Loop" (suom. ihminen valvomassa prosessia) sekä "Human-in-Command" (suom. ihminen ohjaamassa prosessia) ([Euroopan komission korkean tason asiantuntijaryhmä 2019](#eu2019)). Valvonnan tulee ulottua taktisesta väliintulosta strategiseen hallintaan ([Pfeifer 2025](#pfeifer2025)). Ihmisen rooli on toimia järjestelmän strategisena valvojana ja ylimpänä auktoriteettina.

**<a id="luku-2-4-4-1"></a>2.4.4.1 Automaatioharhan Torjunta**

HITL-varmistaja on altis automaatioharhalle ([Luku 5.3.1](#luku-5-3-1)). Tämän torjumiseksi järjestelmä soveltaa menetelmää:

* **Menetelmä 3 (Kysymyksiin ohjaava raportointi):** Raporttipohja ei ole passiivinen tiedonanto, vaan se pakottaa ihmisvalvojan aktiiviseen kognitiiviseen työhön. Tämä mekanismi on toteutettu siten, että XAI-Raportoija-agentti generoi "Kriittisiä Auditointikysymyksiä", joihin ihmisvalvojan on vastattava, erityisesti koskien JEM-erimielisyyksiä (Mandaatti 1).
    * **Perustuu:** Automaatioharhan aktiivinen torjunta ja kognitiivinen pakote ([Parasuraman & Riley 1997](#parasuraman1997)).
    * **Koskee:** XAI-Raportoija-agentti, Ihmisvalvoja (HITL).

XAI-raportti pysäyttää päätöksenteon vaatimalla ihmisvahvistusta ennen lopullista hyväksyntää. Esimerkiksi: "HITL-RATKAISU VAADITAAN: Kriitikko väittää X, Loogikko väittää Y. Kumpi argumentti on paremmin tuettu todisteella Z?" Tämä varmistaa ihmisen aktiivisen osallistumisen. HITL-varmistaja tekee lopullisen, vastuullisen päätöksen.

**2.4.4.2 Muut Hallinnolliset Kontrollit**

Tämä kerros hallitsee myös muita systeemisiä riskejä hallinnollisilla käytännöillä. Turvaton tuotoksen käsittely (LLM05:2025) torjutaan tulosteen koodauksella ([OWASP Foundation 2025c](#owasp2025c)). Toimitusketjun haavoittuvuuksia (LLM03:2025) hallitaan LLMOps-käytännöillä ([Kreuzberger ym. 2023](#kreuzberger2023)). Opetusdatan myrkyttäminen (LLM04:2025) puolestaan estetään käyttämällä vain ihmisen hyväksymää dataa ([D'Angelo 2025](#dangelo2025)).
## <a id="luku-3"></a>Luku 3: Viitekehyksen Asemointi: Vertaileva Analyysi Akateemisiin ja Kaupallisiin Ratkaisuihin

Tämä luku sijoittaa viitekehyksen laajempaan kontekstiin vertaamalla sitä akateemiseen tutkimukseen ja kaupallisiin sovelluksiin. Tavoitteena on tunnistaa viitekehyksen keskeinen innovaatio ja strateginen erottautumistekijä.

### <a id="luku-3-1"></a>3.1 Akateeminen maisema: Olemassa olevien osien uusi synteesi

Vaikka kokonaisarkkitehtuuri on uusi, sen komponentit nojaavat vakiintuneisiin tutkimussuuntauksiin. Kognitiivinen Kvoorum on moniagenttijärjestelmä (MAS) ([Guo ym. 2024](#guo2024)). Olennaisia vertailukohtia ovat vastakkainasetteluun perustuvaa dynamiikkaa hyödyntävät järjestelmät, kuten generatiiviset adversarialliset verkot (GAN) ([Goodfellow ym. 2014](#goodfellow2014)) ja agenttien väliset debatit.

Debattien on osoitettu parantavan päättelyn laatua ([Du ym. 2023](#du2023)), mikä vahvistaa Kriitikko-agentin roolin. Viitekehys sijoittuu koulutusteknologian kentälle ([Luckin ym. 2017](#luckin2017)). Nykyiset sovellukset ovat kuitenkin keskittyneet konkreettisempien tuotosten arviointiin ([Bezanilla ym. 2019](#bezanilla2019)), eivät abstraktin päättelyprosessin analyysiin (vrt. [Li ym. 2025](#li2025)).

Argumentaation laadun analyysille löytyy vastine argumentinlouhinnan (*Argumentation Mining*) alalta, joka keskittyy argumenttirakenteiden automaattiseen tunnistamiseen tekstistä ([Lippi & Torroni 2016](#lippi2016)). Rakenteellisten piirteiden analyysin on osoitettu parantavan automaattista arviointia ([Wachsmuth ym. 2017](#wachsmuth2017)), mikä tukee Loogikko-agentin Toulmin-pohjaista analyysia.

Viitekehyksen ensisijainen innovaatio on näiden erillisten tutkimussuuntien – moniagenttiarkkitehtuurien, portfolioarvioinnin ja argumentinlouhinnan – ainutlaatuinen ja integroitu synteesi. Se soveltaa psykometrista teoriaa modernin tekoälyarkkitehtuurin avulla uudella, synteettisellä tavalla. Esimerkiksi Dreyfus-logiikka on koodattu eksplisiittiseksi säännöksi, ei vain filosofiseksi periaatteeksi.

### <a id="luku-3-2"></a>3.2 Kaupallinen maisema: Markkinarako laadulliselle arvioinnille

Kaupalliset ratkaisut jakautuvat pääosin kahteen kategoriaan. Tämä heijastaa laajempaa suuntausta, jossa tekoälysovellukset eriytyvät kahdentyyppisiin mekanismeihin ([Wisse & Greve 2023](#wisse2023)). Formatiiviset sovellukset tukevat oppimista, kun taas summatiiviset sovellukset keskittyvät osaamisen todentamiseen ja arviointiin:

* **Formatiiviset sovellukset:** Alustat kriittisen ajattelun harjoitteluun. Nämä keskittyvät oppimisprosessiin, mutta eivät tuota auditoitavaa arviota osaamisesta, sillä tekoälyn käyttöä varsinaisessa arvioinnissa pidetään haasteellisena ([Larson ym. 2024](#larson2024)).
* **Summatiiviset sovellukset:** Työkalut jäsenneltyjen arviointien laatimiseen (esim. kysymystenluonti) ([Boussioux 2025](#boussioux2025)). Nämä keskittyvät arviointitehtävien, kuten monivalintojen, laatimiseen ja välttävät monimutkaisen, laadullisen todistusaineiston analysointia ([Displayr 2024](#displayr2024)).

Viimeaikaiset tutkimukset vahvistavat tämän aukon: nykyiset työkalut laiminlyövät systemaattisesti "kriittisen ajattelun ja kehittyneet vuorovaikutuskyvyt" ([Li ym. 2025](#li2025)).

Näiden kategorioiden väliin jää markkinarako. Koska laadullinen arviointi on aikaa vievää ([Suskie 2009](#suskie2009)). Markkinoilta myös puuttuu työkalu, joka kykenisi arvioimaan moniosaista todistusaineistoa automaattisesti ja syvällisesti korkean panoksen tilanteissa.

Tämä viitekehys luo uuden markkinakategorian: "automatisoitu korkean panoksen laadullinen arviointi". Sen todellinen kilpailija ei ole toinen ohjelmisto, vaan ihmisasiantuntijoiden suorittamat manuaaliset prosessit, joita se pyrkii tehostamaan.
## <a id="luku-4"></a>Luku 4: Hybridirubriikin Strateginen Kehitys

Tässä luvussa kuvataan viitekehyksen strategista kehitystä kohti syvällisempää ja auditoitavampaa analyysia. Perinteiset mallit kykenevät usein kertomaan, mitä tapahtui, mutta eivät miksi. Tästä syystä viitekehyksen Toulmin-pohjainen analyysi on suunniteltu tekemään päättelyketjusta läpinäkyvän.

### <a id="luku-4-1"></a>4.1 Kiihtyvyyden ja Haurauden Paradoksi Strategisena Ajurina

Arkkitehtuurin kehityspolku on sarja strategisia valintoja reliabiliteetin ja validiteetin jännitteen hallitsemiseksi. Kehityksen taustalla on kiihtyvyyden ja haurauden paradoksi. Yleiskäyttöisten tekoälymallien nopea kehitys ([Raisch & Krakowski 2021](#raisch2021)) mahdollistaa monimutkaisemmat arkkitehtuurit, mutta lisääntyvä kompleksisuus paljastaa samalla systeemisen haurauden (vrt. [Brooks 1987](#brooks1987)).

Tutkimus osoittaa, että moniagenttijärjestelmien (MAS) epäonnistumiset johtuvat usein koordinaatio-ongelmista, eivät yksittäisten agenttien päättelykyvystä ([Cemri ym. 2025](#cemri2025)). Yksittäisen agentin älykkyyden kasvu ei ratkaise systeemisiä ongelmia ([Cemri ym. 2025](#cemri2025)). Päinvastoin: älykkäämpi agentti voi argumentoida vakuuttavammin virheellisen näkemyksen puolesta (esim. myötäilyvinouman ohjaamana; [Perez ym. 2022b](#perez2022b)) ja johtaa järjestelmän harhaan.

Ratkaisu ei ole vain komponenttien parantaminen, vaan arkkitehtuurin tulee vahvistaa agenttien välisten suhteiden ja kontrollirakenteiden vahvistamiseen. Tulevaisuuden arkkitehtuuri on dynaaminen ekosysteemi, jossa hidas, auditoitava analyysi (korkea pätevyys) ja nopea, tehokas päättely (korkea reliabiliteetti) täydentävät toisiaan.

### <a id="luku-4-2"></a>4.2 Kaksitasoinen Kognitiivinen Arkkitehtuuri: Järjestelmä 1 ja Järjestelmä 2

Viitekehyksen strategisen kehityksen periaatteeksi on valittu Daniel Kahnemanin kaksoisprosessiteoria ([Kahneman 2011](#kahneman2011)). Teorian mukaan ajattelu jakautuu kahteen järjestelmään:

* **Järjestelmä 1**: Nopea, automaattinen, intuitiivinen ja tiedostamaton.
* **Järjestelmä 2**: Hidas, analyyttinen, tietoinen ja vaatii ponnistelua.

Vaikka teoria on osa tieteellistä keskustelua ([Evans & Stanovich 2013](#evans2013)), tässä sitä käytetään strategisena analogiana arkkitehtuurin jäsentämiseen. Tavoitteena on rakentaa kaksi rinnakkaista päättelyjärjestelmää:

* **”Järjestelmä 2” – Hidas, Kallis ja Syvällinen**: Nykyinen Kognitiivinen Kvoorum takaa maksimaalisen auditoitavuuden korkean riskin tapauksissa. Tämä on yhdenmukaista uuden tutkimuksen kanssa (esim. "System-2 Attention"; [Weston & Sukhbaatar 2023](#weston2023)).
* **”Järjestelmä 1” – Nopea, Tehokas ja Automatisoitu**: Pitkän aikavälin visio, tislattu agenttimalli koulutetaan Järjestelmä 2:n datalla rutiininomaisiin arviointeihin.

Arkkitehtuuri muodostaa itseään vahvistavan kehän, jossa hidas päättelyjärjestelmä (Järjestelmä 2) toimii datan tuotantomoottorina. Se luo korkealaatuisia päättelyketjuja, jotka toimivat strategisena pääomana ([Wang ym. 2022](#wang2022)). Tätä aineistoa hyödynnetään nopean järjestelmän (Järjestelmä 1) kehittämisessä, jolloin raskaaseen prosessointiin tehdyt investoinnit mahdollistavat kevyemmän ratkaisun skaalaamisen.

### <a id="luku-4-3"></a>4.3 Kehityspolku: Kaksitasoisen Arkkitehtuurin Rakentaminen

Kehityspolku on kolmivaiheinen. Se etenee reliabiliteetin maksimoinnista (Järjestelmä 2) kohti tehokkuuden optimointia (Järjestelmä 1).

#### <a id="luku-4-3-1"></a>4.3.1 Auditoitavan "Järjestelmä 2:n" Perusta

Nykyinen malli perustuu tiukasti vaiheittaiseen työnkulkuun (”tiukasti sekventiaalinen”). Tämä ”Vaihe 1” edustaa nykyistä prototyyppiä. Sen vahvuus on korkea auditoitavuus ja läpinäkyvyys. Se asettaa luotettavuuden etusijalle. Hinta on korkea viive ja kustannukset. Tämä kustannus on strateginen investointi, joka tuottaa korkealaatuista dataa myöhempiä vaiheita varten.

#### <a id="luku-4-3-2"></a>4.3.2 "Järjestelmä 2:n" Tehokkuuden Optimointi

Tavoitteena on nopeuttaa prosessia ja parantaa sen virheensietokykyä siirtymällä jäykästä sekventiaalisesta ketjusta kohti suunnattua asyklistä verkkoa (engl. *Directed Acyclic Graph*, DAG). Tässä arkkitehtuurissa järjestelmä ei etene vain lineaarisesti vaiheesta toiseen, vaan hyödyntää dynaamisia työnkulkuja, jotka mahdollistavat iteratiiviset palautesilmukat ja agenttien kielellisen itsereflektion ([Shinn ym. 2023](#shinn2023); [Zhang ym. 2024](#zhang2024)).

Tämä malli sallii heikkolaatuiseksi todetun analyysin automaattisen palauttamisen uudelleenkäsittelyyn tietyssä solmukohdassa ilman, että koko prosessia on aloitettava alusta. Jotta auditoitavuus ei vaarantuisi tässä monimutkaisemmassa ja rinnakkaisessa rakenteessa, siirtymä edellyttää teknisesti keskitetyn ja muuttumattoman transaktiolokin toteuttamista, joka tallentaa verkon jokaisen tilasiirtymän.

#### <a id="luku-4-3-3"></a>4.3.3 Skaalautuvan "Järjestelmä 1:n" Luominen

Pitkän aikavälin visiona on hyödyntää **tiedon tiivistämistä** (tislausta) (engl. *knowledge distillation*) (vrt. [Hinton ym. 2015](#hinton2015)). Tämä vaihe merkitsee Järjestelmä 1:n luomista, jossa hybridirubriikin logiikka ”tiivistetään” yhdeksi malliksi. Aiempien vaiheiden tuottamaa dataa käytetään opetusaineistona yksittäisen mallin hienosäätöön. Kevyempi malli oppii jäljittelemään agenttitiimin päättelymalleja. Tislattu malli on kuitenkin vain niin luotettava kuin opetusdata, jolla se on koulutettu.

**Taulukko 2. Moniagenttiarkkitehtuurien strateginen vertailu.**

| Arkkitehtuuri | Vahvuus | Heikkous | Keskeinen kompromissi |
| :--- | :--- | :--- | :--- |
| **Vaiheittainen** | Maksimaalinen auditoitavuus ja reliabiliteetti (Hybridimallin täydellinen jäljitettävyys). | Korkea latenssi ja kustannukset. | Asettaa luotettavuuden ja läpinäkyvyyden etusijalle |
| **Rinnakkainen** | Merkittävästi lyhyempi viive. | Työnkulun ohjauksen kasvanut monimutkaisuus. | Asettaa nopeuden ja tehokkuuden etusijalle. |
| **Tislattu** | Äärimmäisen matala latenssi ja kustannukset (Koko hybridilogiikka yhdessä mallissa). | Joustamattomuus; suorituskyky riippuu datan laadusta. | Asettaa skaalautuvuuden ja käytettävyyden etusijalle. |

### <a id="luku-4-4"></a>4.4 Tulevaisuuden Visio: Systeemisen Resilienssin Vahvistaminen

Järjestelmän pitkän aikavälin menestys edellyttää kehitystä, joka vahvistaa sen kykyä hallita häiriöitä ([Perrow 1984](#perrow1984)). Tämä edellyttää [Luvussa 5.1.1](#luku-5-1-1) tunnistettuihin riskeihin vastaamista. Lisäksi on otettava käyttöön ja validoitava ne kriittiset tekniset kontrollit, jotka on prototyypistä jätetty pois, sekä lisättävä seuraavat välttämättömät tekniset toiminnallisuudet:

* **Semanttinen Anonymisointi**: Siirtyminen nykyisestä RegEx-pohjaisesta suodatuksesta kehittyneempään, NLP/NER-pohjaiseen henkilötietojen (engl. *Personally Identifiable Information*, PII) tunnistukseen.
* **Upotusten Eheyden Tarkistus**: Vartija-agenttiin lisätään anomaliantunnistus, joka perustuu geometrisiin poikkeamiin.
* **Uudelleensijoitusmalli**: Analyytikko-agentin RAG-prosessiin integroidaan erillinen "re-ranker" -malli "lost in the middle" -ilmiön torjumiseksi.

Nämä lisäykset ovat välttämättömiä ennen kuin järjestelmää voidaan pitää tuotantokelpoisena, ja niiden käyttöönotto vaatii huolellista empiiristä testausta. Seuraavat kolme kehityskulkua tähtäävät systeemisen resilienssin lisäämiseen.

#### <a id="luku-4-4-1"></a>4.4.1 "Järjestelmä 2:n" Päättelykyvyn Syventäminen monikierroksisella debatilla

Nykyinen staattinen rakenne voi vahvistaa systeemisiä virheitä. Tulevaisuuden suunta on dynaaminen ”agenttiekologia”, jossa agentit osallistuvat monikierroksiseen väittelyyn (*debate*) ([Liang ym. 2023](#liang2023)). Tämä mahdollistaisi todellisen debatin Kriitikon ja Loogikon välillä. Vuorovaikutus voi tuottaa syvällisempiä oivalluksia, mutta on altis sosiaalisille vinoumille.

Tutkimus osoittaa, että debatit voivat johtaa virheiden vahvistumiseen, kun agentit suosivat yksimielisyyttä ([Wynn ym. 2025](#wynn2025)). Tämän "konsensuksen tyrannian" vuoksi debatin tavoitteen on oltava jäsennelty erimielisyys. Tuomari-agentin rooli muuttuu aktiiviseksi moderaattoriksi, joka varmistaa älyllisen rehellisyyden ja raportoi vähemmistönäkemykset ihmisvalvojalle.

#### <a id="luku-4-4-2"></a>4.4.2 Siirtymä kohti agenttisuunnittelua (engl. *Agent Engineering*)

Järjestelmän strateginen jatkokehitys on edellyttänyt siirtymistä hauraasta kehotesuunnittelusta (engl. *prompt engineering*) kohti vankempaa agenttisuunnittelun toimintamallia. Tässä lähestymistavassa turvallisuus ja logiikka eivät nojaa pelkkiin kielellisiin pyyntöihin, vaan ne koodataan suoraan järjestelmän rakenteisiin ([Anthropic 2025c](#anthropic2025c)).

Tämä rakenteellinen muutos tarkoittaa nykyisen, pelkkään kielimalliin nojaavan behavioraalisen suojauksen korvaamista erillisillä teknisillä luokittelijoilla, kuten Llama Guard -mallilla, jotka on optimoitu tunnistamaan ja estämään haitallinen sisältö ennen sen prosessointia ([Inan ym. 2023](#inan2023); vrt. [Anthropic 2025a](#anthropic2025a)). Arkkitehtuuritasolla tämä vaatii siirtymää jäykästä sekventiaalisesta ketjusta suunnatuksi asykliseksi verkoksi (DAG), mikä mahdollistaa iteratiiviset palautesilmukat ja heikkolaatuiseksi todetun analyysin automaattisen palauttamisen uudelleenkäsittelyyn (vrt. [Zhang ym. 2024](#zhang2024)).

Järjestelmän pätevyyttä vahvistetaan samalla ulkoistamalla kausaalinen päättely simulaatioista todelliseen koodin suorittamiseen eristetyissä hiekkalaatikoissa, mikä vie kohti autonomisten koneälyjen edellyttämiä maailmanmalleja ([LeCun 2022](#lecun2022)) ja tarjoaa deterministisen keinon todentaa väitteiden paikkansapitävyys ([Turpin ym. 2025](#turpin2025)). Myötäilyvinouman (engl. *sycophancy*) torjunnassa hyödynnetään pakotettua rakenteellista erimielisyyttä käyttämällä heterogeenisia yleiskäyttöisiä tekoälymalleja, mikä estää agentteja vahvistamasta toistensa virheellisiä päätelmiä ([Wynn ym. 2025](#wynn2025)). Lopullinen luottamus automaatioon varmistetaan Tuomari-agentin systemaattisella hienosäädöllä (engl. *fine-tuning*), joka perustuu laajaan ihmiskalibrointiin ja tilastollisen arvioijien välisen yhdenmukaisuuden, kuten Cohenin Kappa -kertoimen, jatkuvaan seurantaan ([McHugh 2012](#mchugh2012)).

#### <a id="luku-4-4-3"></a>4.4.3 Hallintamallin Sisäistäminen

Nykyinen kehotepohjainen Kognitiivinen Palomuuri on hauras ([Luku 2.5.1](#luku-2-5-1)). Kestävämpi ratkaisu on siirtyä sisäistettyyn hallintaan hyödyntämällä monikerroksista puolustusstrategiaa ([CISA 2016](#cisa2016)). Tämä yhdistää (1) mallin sisäisen linjauksen perustuslaillisen tekoälyn (CAI) avulla ([Bai ym. 2022](#bai2022)) sekä (2) ulkoisen valvonnan perustuslaillisilla luokittelijoilla ([Anthropic 2025a](#anthropic2025a); [Sharma ym. 2025](#sharma2025)).

CAI-lähestymistavassa periaatteet upotetaan malliin hienosäädön avulla ([Bai ym. 2022](#bai2022)). Tämä kaksitasoinen puolustus on kestävä ratkaisu (vrt. [Sharma ym. 2025](#sharma2025)). Tämä siirtymä on elintärkeä dynaamisen agenttiekologian luotettavuuden kannalta. Autonomisempien agenttien toiminnan on perustuttava sisäistettyyn arvopohjaan.

Nämä kolme kehityskulkua ovat toisistaan riippuvaisia ja muodostavat vision resilientistä järjestelmästä.

**Taulukko 3. Viitekehyksen kehitys kohti systeemistä resilienssiä.**

| Vaihe | Arkkitehtuuri | Hallintamalli | Anomaliantunnistus | Keskeinen haaste |
| :--- | :--- | :--- | :--- | :--- |
| **Nykyinen** | Staattinen Kognitiivinen Kvoorum | Kehotepohjainen Kognitiivinen Palomuuri | Ristiriitojen tunnistus (Faktuaalinen) | Kognitiivisen Arviointimatriisin normatiivisen soveltamisen ja holistisen tason Mestaruus-poikkeamien tunnistamisen välinen jännite |
| **Tuleva** | Dynaaminen Agenttiekologia (Debatti) | Perustuslaillinen tekoäly (CAI) | Prosessin uskottavuusanalyysi | Holistisen tason debatin hallinta ja agenttien välinen epäjohdonmukaisuus |
| **Visio** | Itsesäätelevä Agenttiekologia | Sisäistetty ja jaettu ”perustuslaki” | Kausaalinen auditointi (Maailmanmallit) | Hybridirubriikin täydellinen sisäistäminen ja aidon kausaalisen ymmärryksen saavuttaminen |

### <a id="luku-4-5"></a>4.5 Täydentävät tieteelliset menetelmät: Psykometrinen tarkkuus ja muodollinen todentaminen

Vaikka kaksitasoinen hybridimatriisi tarjoaa arkkitehtonisen ratkaisun reliabiliteetin ja validiteetin paradoksiin ([Borsboom ym. 2004](#borsboom2004)), järjestelmän mittaustarkkuutta on mahdollista parantaa integroimalla siihen vakiintuneita psykometrisia menetelmiä. Nykyinen prototyyppi nojaa arvioitsijoiden väliseen luotettavuuteen (Cohenin kappa) ja BARS-asteikkoon, mutta nämä edustavat klassista testiteoriaa (CTT), joka käsittelee virhettä erittelemättömänä kokonaisuutena.

Tulevaisuuden kehitysvaiheessa (”Järjestelmä 2:n optimointi”) viitekehys ottaa käyttöön yleistettävyysteorian (Generalizability Theory, G-teoria). Toisin kuin perinteinen luotettavuuskerroin, G-teoria mahdollistaa virhelähteiden matemaattisen erittelyn ([Brennan 2001](#brennan2001)). Tämä on kriittistä moniagenttijärjestelmässä, jossa on pystyttävä erottamaan, johtuuko vaihtelu arvioivasta agentista, tehtävätyypistä vai itse opiskelijan suorituksesta. G-teorian avulla voidaan laskea optimaalinen ”kognitiivinen kvoorum” eli se agenttien ja tehtävien määrä, joka vaaditaan luotettavan G-kertoimen (> 0.80) saavuttamiseksi.

Kognitiivisen arviointimatriisin (Taulukko 1) tasojen kalibroinnissa siirrytään hyödyntämään osioivasteoriaa (engl. *Item Response Theory*, IRT) ([Embretson & Reise 2000](#embretson2000)). Nykyinen matriisi olettaa arviointitasojen välimatkat tasaisiksi, mikä on laadullisessa arvioinnissa harvoin totta. IRT-mallinnus asettaa sekä tehtävän vaikeuden että vastaajan kyvykkyyden samalle logit-asteikolle, mikä paljastaa kriteerien todellisen erottelukyvyn ja mahdollistaa adaptiivisen testauksen.

Sisällöllisen analyysin syvyyttä vahvistetaan ottamalla käyttöön SOLO-taksonomia (engl. *Structure of the Observed Learning Outcome*) ([Biggs & Collis 1982](#biggs1982)). Siinä missä nykyinen Bloomin taksonomiaan ([Anderson & Krathwohl 2001](#anderson2001)) perustuva malli luokittelee kognitiivisia prosesseja, SOLO-taksonomia mittaa vastauksen rakenteellista monimutkaisuutta. Tämä tarjoaa Loogikko-agentille välineen erottaa ”monistrukturaalinen” (asiat irrallisina luetteleva) vastaus aidosti ”suhteuttavasta” (asiat kokonaisuudeksi sitovasta) vastauksesta, mikä on keskeinen syvällisen osaamisen osoitus.

Viimeisenä menetelmällisenä lisäyksenä on muodollinen todentaminen. Koska nykyiset kielimallit ovat alttiita hallusinaatiolle ja epäonnistuvat usein monimutkaisessa syysuhteisessa päättelyssä ([Chi ym. 2024](#chi2024)), järjestelmään integroidaan "Logic-to-Code" -moduuli. Tässä lähestymistavassa Loogikko-agentti ei ainoastaan arvioi argumenttia tekstinä, vaan kääntää sen premissit ja johtopäätökset formaaliksi koodiksi (esim. Python tai Prolog). Koodin suorittaminen tarjoaa yksiselitteisen tavan todentaa argumentin looginen eheys (vrt. [Turpin ym. 2025](#turpin2025)), mikä vähentää merkittävästi retorisen uskottavuuden ja totuuden välistä kuilua.

### <a id="luku-4-6"></a>4.6 Siirtymä staattisesta lopputuloksen arvioinnista dynaamiseen kognitiivisen rakenteen analyysiin

Mestaruuden tunnistaminen edellyttää siirtymistä muuttumattomasta lopputuotteen pisteytyksestä dynaamiseen kognitiivisen rakenteen analyysiin. Aiemmin [Luvussa 2.4.5](#luku-2-4-5) kuvattu substanssiosaamisen ja kognitiivisten taitojen erottelu vaatii tuekseen menetelmiä, jotka tekevät oppimisprosessin rakenteen näkyväksi.

Keskeinen menetelmä tämän saavuttamiseksi on episteeminen verkkoanalyysi (engl. *Epistemic Network Analysis*, ENA) ([Shaffer ym. 2016](#shaffer2016)). ENA mallintaa koodien ja käsitteiden välisiä yhteyksiä dynaamisina verkkoina sen sijaan, että se laskisi vain niiden esiintymistiheyksiä. Tämä mahdollistaa ”keskusteluhistorian” ja ”reflektiodokumentin” välisen suhteen visualisoinnin: jos reflektiossa esiintyvät käsitteet eivät muodosta verkkoa varsinaisen toiminnan kanssa, kyseessä on todennäköisesti [Luvussa 5.1.2](#luku-5-1-2) kuvattu näytöksenomainen reflektio.

Koska mestaruus on luonteeltaan usein piilevää ([Polanyi 1966](#polanyi1966)) ja pakenee tarkkoja arviointimatriiseja, kokonaisvaltaista tasoa vahvistetaan adaptiivisella vertailevalla arvioinnilla (engl. *Adaptive Comparative Judgment*, ACJ) ([Pollitt 2012](#pollitt2012)). ACJ-menetelmässä Tuomari-agentti ei vertaa työtä ehdottomaan kriteeriin, vaan suorittaa sarjan parivertailuja (”kumpi näistä osoittaa syvempää ymmärrystä?”). Tämä menetelmä on osoittautunut perinteisiä pisteytysmenetelmiä luotettavammaksi abstraktin osaamisen arvioinnissa ([Pollitt 2012](#pollitt2012)), ja se luo järjestelmälle empiirisesti viritetyn laatuasteikon.

Lopuksi analyysi ulotetaan kielelliseen metatasoon tutkimalla opiskelijan tieto-opillista asemoitumista (engl. *epistemic stance*) ja metadiskurssia ([Hyland 2005](#hyland2005)). Asiantuntijuus ilmenee usein tapana ilmaista varmuutta ja epävarmuutta: mestari tunnistaa tietonsa rajat ja käyttää strategisia varaumia (engl. *hedging*), kun taas noviisi tai tekoälyä kritiikittömästi jäljittelevä toimija sortuu usein perusteettomaan varmuuteen. Tämän metadiskurssin analysointi tarjoaa kognitiiviselle kvoorumille uuden, sisällöstä riippumattoman merkin aidon asiantuntijuuden ja tekoälyn tuottaman tekstin erottamiseksi.

### <a id="luku-4-7"></a>4.7 Hallittu kehitys luotettavuuden varmistamiseksi

Tässä luvussa kuvattu kehityskulku vastaa ”kiihtyvyyden ja haurauden paradoksiin” ([Cemri ym. 2025](#cemri2025)) yhdistämällä arkkitehtonisen varovaisuuden metodologiseen tarkkuuteen. Ratkaisun ytimessä on Kahnemanin (2011) kaksoisprosessiteoriaan perustuva symbioosi, jossa hidas ”Järjestelmä 2” (kognitiivinen kvoorum) tuottaa korkealaatuista dataa nopean ”Järjestelmä 1:n” (tiivistetty malli) kouluttamiseksi.

Tämä strategia edellyttää kuitenkin, että hitaan järjestelmän tuottama analyysi on todistettavasti pätevää. Pelkkä laskentatehon tai ajan lisääminen ei poista virheitä, jos mittaristo on vinoutunut. Siksi luvuissa 4.6 ja 4.7 esitellyt täydentävät tieteelliset menetelmät – kuten G-teoria ([Brennan 2001](#brennan2001)), episteeminen verkkoanalyysi ([Shaffer ym. 2016](#shaffer2016)) ja muodollinen todentaminen – eivät ole vain lisäosia, vaan strategisia välttämättömyyksiä. Ne varmistavat, että ”Järjestelmä 2” tuottaa empiirisesti viritettyä ja rakenteellisesti syvällistä tietoa, jota ilman myöhempi tiedon tiivistäminen (engl. *Knowledge Distillation*) vain monistaisi pinnallisia virheitä (vrt. [Hinton ym. 2015](#hinton2015)).

Tämä kokonaisuus tarjoaa yleistettävän mallin vastuullisen tekoälyjärjestelmän kehittämiselle, joka etenee neljän periaatteen mukaisesti:

1.  **Priorisoi tarkastettavuus ja syvällisyys (Järjestelmä 2):** Aloita aina raskaalla, moniagenttipohjaisella prosessilla, joka maksimoi läpinäkyvyyden tehokkuuden kustannuksella.
2.  **Varmista laatu tieteellisillä menetelmillä:** Ankkuroi arviointi vakiintuneisiin psykometrisiin malleihin (kuten IRT ja G-teoria) ja dynaamiseen rakenneanalyysiin (kuten ENA ja ACJ), jotta järjestelmä mittaa aitoa osaamista eikä vain todennäköisyyksiä.
3.  **Hyödynnä varmennettua dataa skaalautumiseen (Järjestelmä 1):** Käytä tieteellisesti varmennettua prosessidataa kevyempien mallien opettamiseen, jolloin raskas investointi pätevyyteen muuttuu skaalautuvaksi pääomaksi.
4.  **Siirry ulkoisesta pakosta sisäistettyyn eheyteen:** Kehitä järjestelmää kohti tilaa, jossa hallintamekanismit ja arvot on koodattu osaksi agenttien sisäistä toimintalogiikkaa (perustuslaillinen tekoäly, Constitution AI).
## <a id="luku-5"></a>Luku 5: Keskeiset riskit ja niiden hallinta

Tässä luvussa analysoidaan viitekehykseen liittyviä keskeisiä riskejä ja esitellään niiden hallintamekanismeja. Analyysi kattaa metodologiset ydinriskit ([Luku 5.1](#luku-5-1)), arkkitehtoniset riskit ([Luku 5.2](#luku-5-2)) sekä operatiiviset, eettiset ja teknologiset riskit ([Luku 5.3](#luku-5-3)).

### <a id="luku-5-1"></a>5.1 Metodologiset Ydinriskit – Viitekehyksen Tieteellisen Perustan Haasteet

#### <a id="luku-5-1-1"></a>5.1.1 Riski: Empiirisen Validoinnin Puute

**Riskin kuvaus:** Viitekehyksen keskeisin heikkous on empiirisen näytön puuttuminen. Sen uskottavuus nojaa todentamattomaan hypoteesiin korkean arvioijien välisen luotettavuuden (engl. *inter-rater reliability*, IRR) saavuttamisesta. Tämä on merkittävä haaste, sillä laadullisten arviointien heikkous on juuri matala IRR ([Baume & Yorke 2002](#baume2002); [Koretz ym. 1994](#koretz1994)).

Riskiä korostavat prototyypin tekniset puutteet, jotka on yksityiskohtaisesti kirjattu Vartija- ja Analyytikko-agenttien tuottamiin metodologisiin lokeihin. Järjestelmästä puuttuvat edistynyt "Semanttinen Anonymisointi" (OWASP LLM02:2025 -riskin hallinta) ja RAG-prosessin "Uudelleensijoitusmalli" ("lost in the middle" -riski; [Liu, N. F. ym. 2024](#liu2024b)). Lisäksi "Upotusten Eheyden Tarkistus" puuttuu, joten OWASP LLM08:2025 -riski on täysin hallitsematon, koska toiminto "EI OLE KÄYTÖSSÄ".

**Riski: Vektori- ja Upotushyökkäykset (OWASP LLM08:2025).** Koska nykyinen prototyyppi ei sisällä erillistä upotusten eheyden tarkistusta (Embedding Integrity Check), RAG-arkkitehtuuri on altis ”myrkytetyille” hakutuloksille (Poisoned Retrieval) ([Zou ym. 2024](#zou2024)). Tämä puute on tehty näkyväksi pakottamalla Vartija-agentin kirjaamaan metodologiseen lokiin nimenomaisen varoituksen: "RAJOITUS:... LLM08-riski hallitsematon."

Näiden kehittyneiden kontrollien puuttuminen luo validointivelan, jonka vaikutuksia nykyiseen arkkitehtuuriin ei ole empiirisesti testattu. [Luvussa 4.4](#luku-4-4) esitellään näkymiä näiden riskien hallitsemiseksi tulevissa iteraatioissa.

**Hallintamekanismi:** Ainoa ratkaisu on [luvussa 6.2](#luku-6-2) esitetty tutkimusagenda. On käynnistettävä muodollinen pilottitutkimus, joka mittaa psykometriset ominaisuudet:

* **Reliabiliteetti:** Mitataan analyyttisen tason IRR vertaamalla järjestelmän arvioita ihmisasiantuntijoiden arvioimaan ”vertailuaineistoon” (engl. *Gold Standard*).
* **Pätevyys:** Arvioidaan holistisen tason käsitepätevyysa todentamalla, että Mestaruus-poikkeama-merkinnät korreloivat ulkoisten asiantuntija-arvioiden kanssa.

**Jäännösriski:** Riski on merkittävä, kunnes empiirinen tutkimus on suoritettu. Siihen asti viitekehys pysyy puhtaasti teoreettisena konstruktiona.

#### <a id="luku-5-1-2"></a>5.1.2 Riski: Goodhartin Laki ja ”Performatiivinen Reflektio”

**Riskin kuvaus:** Perustavanlaatuinen uhka on Goodhartin laki ([Strathern 1997](#strathern1997)), jonka mukaisesti käyttäjät voivat oppia manipuloimaan järjestelmää ([Stumborg ym. 2022](#stumborg2022)). Tämä ilmenee ”performatiivisena reflektiona”, joka on tässä viitekehyksessä sovellettu termi kuvaamaan tilannetta, jossa käyttäjä tuottaa vakuuttavan, mutta epäaidon narratiivin (vrt. vaikutelmien hallinta; [Cullen 2020](#cullen2020); [Levashina & Morgeson 2007](#levashina2007)). Nykyinen arkkitehtuuri ei todennäköisesti tunnista tätä.

**Juurisyy:** Nykyinen arkkitehtuuri ei kykene aitoon kausaaliseen auditointiin ([Pearl 2009](#pearl2009); [Sgaier ym. 2020](#sgaier2020); [Bareinboim ym. 2022](#bareinboim2022)). Vaikka jotkut tutkijat näkevät kielimalleissa potentiaalia kausaaliseen päättelyyn ([Kiciman ym. 2023](#kiciman2023)), nykyisten kielimallien onkin osoitettu systemaattisesti epäonnistuvan muodollisessa L3-päättelyssä ([Chi ym. 2024](#chi2024)).

**Hallintamekanismit:**

* **Nykyinen (toiminnallinen):** Tuomari-agentin ”Aitous-epäily”-liputus. Toteutus sisältää "Epäilyttävä Täydellisyys" -heuristiikan, joka institutionalisoi epäluulon ”liian täydellisiä” suorituksia kohtaan ja toimii tilastollisena anomaliantunnistuksena. Tämä heuristiikka (joka on konkretisoitu osaksi Tuomari-agentin päätöksentekoa) määrittelee täsmälliset ehdot liputukselle: jos suoritus saa korkeimmat pisteet (Taso 4) kaikissa kriteereissä JA Kriitikko-agentin prosessiauditointi ei löydä poikkeamia, suoritus liputetaan automaattisesti anomaliaksi ja Aitous-epäilyllä. Lisäksi Kriitikko-agentin heuristiikkoja on vahvistettu L3-simulaatioilla. Mekanismien pätevyys on kuitenkin todentamatta.
* **Tulevaisuuden (strateginen):** Siirtymä ”kausaaliseen auditointiin” integroimalla ”maailmanmalleja” ([Luku 4.4.2](#luku-4-4-2)).

**Jäännösriski:** Riski on akuutti. Viitekehys on nykymuodossaan haavoittuvainen taitavalle manipuloinnille.

Tämän riskin torjumiseksi järjestelmä hyödyntää "Performatiivisuuden tunnistuksen", joka on suora vastatoimi Goodhartin laille ("kun mittarista tulee tavoite...") ([Strathern 1997](#strathern1997); [Stumborg ym. 2022](#stumborg2022)) ja "performatiiviselle reflektiolle" ([Cullen 2020](#cullen2020)). Järjestelmä toteuttaa tämän torjunnan Prosessiauditoijaryhmän (Kausaalinen Analyytikko ja Performatiivisuuden Tunnistaja) kautta.

Tämänhetkinen toteutus on kuitenkin rajoittunut heuristiikkoihin, jotka edustavat Pearlin kausaalihierarkian (PCH) alempia tasoja ([Pearl 2009](#pearl2009)). Agentin suorittama "Temporaalinen Auditointi" (syy edeltää seurausta) ja "Kausaalinen Uskottavuus" -heuristiikka (vrt. [Sgaier ym. 2020](#sgaier2020)) toimivat L1-tason (Assosiaatio) ja L2-tason (Interventio) puitteissa (ks. [Luku 2.4.3](#luku-2-4-3)).

Analyysin syvyyttä on parannettu ottamalla käyttöön kehittyneitä päättelyketjutekniikoita, jotka simuloivat L3-päättelyä (ks. [Luku 2.4.3](#luku-2-4-3)). Näitä ovat esimerkiksi "Kontrafaktuaalinen Stressitesti", "Abduktiivinen Haasto" ja "Pre-Mortem Analyysi" (ks. yksityiskohtainen kuvaus [Luvussa 2.4.3](#luku-2-4-3)).

Viitekehyksen suurin yksittäinen metodologinen riski on, että se ei kykene suorittamaan muodollista L3-tason (Kontrafaktuaalit) kausaalista auditointia, jota aidon performatiivisuuden tunnistaminen edellyttäisi. Tämä tarkoittaa, että järjestelmä kykenee tunnistamaan loogiset ristiriidat ja ilmeiset "mahdoton aikajana" -virheet, mutta se on edelleen altis taitavasti laaditulle, loogisesti ehyelle mutta faktuaalisesti keksitylle narratiiville.

Vaikka uudet heuristiikat parantavat L3-simulaatiota, laaja empiirinen tutkimus on osoittanut, että nykyiset kielimallit epäonnistuvat systemaattisesti muodollisessa kausaalisessa ja kontrafaktuaalisessa päättelyssä (L3) ([Chi ym. 2024](#chi2024)). Tämän takia operatiivinen malli nojaa heuristiseen uskottavuuteen (esim. aikajanan tarkistus) aidon matemaattisen kausaalianalyysin sijaan.

Tämä jättää kausaalisen aukon, jota performatiivinen reflektio voi hyödyntää. Tämän vuoksi järjestelmä edellyttää pakollisen metodologisen lokikirjauksen, joka pakottaa Kausaalisen Analyytikko -agentin tunnustamaan tämän rajoitteen: "RAJOITUS: Järjestelmä ei kykene muodolliseen L3-tason kausaaliseen päättelyyn, vaikka L3-simulaatioita käytetään. Riski performatiivisen reflektion tunnistamatta jäämisestä on kohonnut"

Tämä kuilu L3-vision ([Luku 4.4.2](#luku-4-4-2)) ja L1/L2-toteutuksen välillä on keskeisin este viitekehyksen täydelle validiteetille. Nykyiset "Deep Think" -mallitkaan eivät kykene luotettavasti simuloimaan kontrafaktuaaleja ilman ulkoisia kausaalisia malleja tai koodipohjaista suoritusta (vrt. [Turpin ym. 2025](#turpin2025); [Aryan & Liu 2025](#aryan2025)), minkä vuoksi prototyyppi tyytyy heuristiseen uskottavuusarviointiin.

#### <a id="luku-5-1-3"></a>5.1.3 Riski: Hybridirubriikin Sisäinen Jännite

**Riskin kuvaus:** Viitekehys institutionalisoi psykometriikan paradoksin. Jännite syntyy analyyttisen (reliabiliteetti) ja holistisen (pätevyys) tason välille, jotka ovat usein ristiriidassa.

**Hallintamekanismi:** Kaksitasoinen arkkitehtuuri ([Luku 2.1](#luku-2-1)) hallitsee riskiä. Konkreettinen instrumentti on Mestaruus-poikkeama-liputus, joka siirtää tulkintavastuun ihmiselle. Jännitteen hallitsemiseksi on sisäänrakennettu "Popper vs. Dreyfus" -erotteluheuristiikka:

* **Falsifioinnin (Popper) Etusija:** Vakavaa eettistä laiminlyöntiä tai faktuaalista virhettä ei voi tulkita ”mestaruus-poikkeamaksi”.
* **Mestaruuden (Dreyfus) Tunnistaminen:** ”mestaruus-poikkeama” voi ilmetä vain matriisin odotusarvojen tietoisena ja perusteltuna rikkomisena.

**Jäännösriski:** Jännite on pysyvä. Lopullinen tulkintavastuu jää aina ihmiselle, mikä asettaa korkeat vaatimukset ihmisvalvojan asiantuntemukselle.

### <a id="luku-5-2"></a>5.2 Arkkitehtoniset Riskit – Kognitiivisen Kvoorumin Sisäiset Hauraudet

#### <a id="luku-5-2-1"></a>5.2.1 Riski: Päättelyketjujen Epäluotettavuus

**Riskin kuvaus:** Auditoitavuus perustuu oletukseen, että agenttien päättelyketjut ovat uskollisia (engl. *faithful*), eli ne heijastavat tarkasti mallin todellista päättelyprosessia ([Jacovi & Goldberg 2020](#jacovi2020)). Viimeaikainen tutkimus on entisestään vahvistanut epäilyjä tästä ja osoittanut, että jopa edistyneimmät mallit tuottavat säännöllisesti epäuskollisia päättelyketjuja ([Arcuschin ym. 2025](#arcuschin2025)).

Mallit voivat päätyä "implisiittiseen post-hoc -rationalisointiin" ([Creswell ym. 2024](#creswell2024); [Arcuschin ym. 2025](#arcuschin2025)), jolloin ne perustelevat jälkikäteen intuitiivisesti tuotetun vastauksen (vrt. [Turpin ym. 2023](#turpin2023)).

**Hallintamekanismi:** Kaksivaiheinen "teoriaohjattu prosessivalvonta". Hypoteesina on, että rationalisoinnin virheet ilmenevät argumentin rakenteessa. Valvonta toteutetaan seuraavasti:

* **Argumentin Purku (Loogikko):** Loogikko tunnistaa argumentaatioskeeman ([Walton ym. 2008](#walton2008)) ja tuottaa "kriittiset kysymykset".
* **Kohdennettu Stressitesti (Epäuskollisuuden Tunnistus) (Kriitikkoryhmä):** Kriitikko käyttää kysymyslistaa stressitestissä etsiäkseen rationalisointia ja päättelyketjun epäuskollisuutta.

Tämä mekanismi siirtää valvonnan faktantarkistuksesta päättelyn laadun auditointiin.

**Jäännösriski:** Riski on perustavanlaatuinen nykyisille kielimalleille. Lieventämiseksi Kriitikko-agentille on sisällytetty ”Kausaalinen heuristiikka” ([Luku 2.4.3](#luku-2-4-3)), joka pakottaa arvioimaan syy-seuraussuhteen uskottavuutta ([Sgaier ym. 2020](#sgaier2020)).

#### <a id="luku-5-2-2"></a>5.2.2 Riski: Systeeminen Hauraus ja Virheiden Eteneminen

**Riskin kuvaus:** Nykyinen vaiheittainen arkkitehtuuri on hauras. Virhe alkuvaiheessa etenee koko ketjun läpi. Tämä on tunnettu MAS-koordinaatio-ongelma ([Cemri ym. 2025](#cemri2025)).

**Hallintamekanismi:** Riskiä hallitaan kahdella päästrategialla. Ensisijainen suositus on arkkitehtoninen heterogeenisyys. Siirtyminen heterogeenisiin järjestelmiin (eri yleiskäyttöiset tekoälymallit) parantaa suorituskykyä ([Ye ym. 2025](#ye2025)).

Tämän lisäksi arkkitehtuuriin on lisätty redundanssia "Ristiinvalidoiva Ketjutus" (*Cross-Validating CoT*) -mekanismilla ([Luku 2.6.2](#luku-2-6-2)). Tämä pakottaa Loogikon, Kriitikkoryhmän ja Tuomarin varmistamaan edellisen agentin päättelyn sisäisen johdonmukaisuuden ennen oman tehtävänsä aloittamista. Tämä vähentää riskiä, että alkuvaiheen virhe ohjaa koko analyysia.

Koska nykyisessä prototyyppiympäristössä (manuaalinen orkestrointi) agentit eivät pääse käsiksi ajonaikaiseen metadataan (eli ne eivät tiedä, mikä yleiskäyttöinen tekoälymalli niitä suorittaa), heterogeenisyyden automaattinen todentaminen on mahdotonta. Koska orkestraattori ei teknisesti 'näe' mitä mallia API-kutsussa käytettiin (jos se vaihdetaan lennosta UI:ssa), vastuu on protokollatason sääntö.

**Jäännösriski:** Homogeeninen ajo lisää merkittävästi systeemisen virheen riskiä - prototyyppi pysyy hauraana. Ratkaisu on siirtyminen rinnakkaiseen arkkitehtuuriin ([Luku 4.3.2](#luku-4-3-2)). Siihen asti luotettavuus riippuu korostetusti ihmisvalvojasta (HITL). Tämän riskin hallinta on konkretisoitu pakottamalla XAI-Raportoija-agentin raportoimaan ihmisvalvojalle vastuun heterogeenisyyden varmentamisesta. Järjestelmän pätevyys edellyttää heterogeenista arkkitehtuuria, sillä homogeeninen ajo lisää riskiä systeemisten virheiden vahvistumisesta ([Cemri ym. 2025](#cemri2025)) ja mitätöi aidon ristiinvarmentamisen (engl. *cross-verification*) hyödyn ([Ye ym. 2025](#ye2025)).

#### <a id="luku-5-2-3"></a>5.2.3 Riski: Debatin degeneraatio ja konsensuksen tyrannia

**Riskin kuvaus:** Vaikka adversariaalisen debatin on osoitettu parantavan päättelyä ([Du ym. 2023](#du2023)), tuoreempi tutkimus viittaa "konsensuksen tyranniaan" ([Wynn ym. 2025](#wynn2025)). Homogeenisissä ryhmissä agentit saattavat asettaa etusijalle sosiaalista mukautumista totuudenmukaisuuden kustannuksella. Tämä voi johtaa tilanteeseen, jossa virheellinen mutta enemmistön kannattama näkemys syrjäyttää oikean vähemmistönäkemyksen. [Wynn ym. (2025)](#wynn2025) osoittivat, että debatti voi jopa heikentää suoritusta, jos agentit eivät ole riittävän kyvykkäitä tai jos ne ovat taipuvaisia myötäilyvinoumaan.

**Hallintamekanismit:**

* **Vinoumat:** Siirtyminen heterogeeniseen MAS-arkkitehtuuriin (suositeltu).
* **Erimielisyys:** Järjestelmä tekee erimielisyydestä strategista pääomaa. Vastaus on ”Jäsennellyn Erimielisyyden Mandaatti” (JEM), joka on toteutettu kaksitasoisesti. Kriitikko-agentti ohjeistetaan aktiivisesti ylläpitämään erimielisyyttä ([Luku 2.4.3](#luku-2-4-3)), ja Tuomari-agenttia kielletään pakottamasta konsensusta ja ohjeistetaan raportoimaan erimielisyydestä.

**Jäännösriski:** Nykyinen prototyyppi on altis vinoumille. Erimielisyyden tulkintavastuu siirtyy ihmiselle.

#### <a id="luku-5-2-4"></a>5.2.4 Riski: Heterogeenisen Arkkitehtuurin Yhteentoimivuus

**Riskin kuvaus:** Suositeltu heterogeeninen arkkitehtuuri ([Luku 5.2.2](#luku-5-2-2)), jossa eri agentit käyttävät eri yleiskäyttöisiä tekoälymalleja (Malli A ja Malli B), tuo mukanaan teknisen yhteen toimivuuden (engl. *interoperability*) riskin. Kun dataa (JSON) siirretään mallien välillä, on riski datan eheyden vaarantumisesta siirron tai tulkinnan aikana (vrt. [ISO/IEC 25010 2023](#iso2023)).

**Hallintamekanismi:** Riskiä hallitaan teknisillä ja semanttisilla kontrolleilla. Jokaiseen prosessivaiheeseen on sisällytetty pakollinen syötteen eheyden tarkistus. Tämä tarkistus varmistaa rakenteellisen (JSON-kelpoisuus) ja perustason semanttisen eheyden (merkistö).

Datasiirron turvaamiseksi manuaalisessa orkestroinnissa on otettu käyttöön "Container-enkapsulointi" (selkeät alku- ja lopputunnisteet), joka eristää JSON-objektit muusta keskusteluvirrasta. Lisäksi on implementoitu "Semanttiset Tarkistussummat". Lähettävä agentti generoi lyhyen (3–4 virkkeen) yhteenvedon tuottamastaan datasta. Vastaanottava agentti varmistaa, että datan sisältö vastaa tarkistussummaa ennen käsittelyn aloittamista. Tämä tarjoaa vahvemman suojan hienovaraisia merkistövirheitä ja inhimillisiä kopiointivirheitä (esim. osittainen kopiointi) vastaan.

Lisäksi heterogeenisyyden varmentamisen tueksi on otettu käyttöön "Ympäristön Allekirjoitus" (engl. *Environmental Signature*). Kriitikkoryhmän agentit ohjeistetaan lisäämään tuottamaansa JSON-objektiin metadata-kenttä, joka indikoi suorituksen tapahtuneen erillisessä ympäristössä (esim. "Kriitikkoryhma_External"). Vaikka tämä allekirjoitus on vain deklaratiivinen (agentti ei voi teknisesti varmentaa omaa suoritusympäristöään), se toimii auditoitavana signaalina XAI-Raportoijalle pakollisen HITL-varmistuskysymyksen generoimiseksi (vrt. [Luku 5.2.2](#luku-5-2-2)).

**Jäännösriski:** Validointi ja tarkistussummat eivät takaa täydellistä semanttista eheyttä eivätkä tunnista semanttisia tulkintaeroja. Manuaalinen orkestrointi (datan kopiointi ja liittäminen) lisää inhimillisen virheen riskiä ja altistaa datan hienovaraisille merkistö- tai koodausvirheille siirron aikana (vrt. [W3C 2008](#w3c2008)). Nämä virheet voivat muuttaa sisällön merkitystä tunnistamattomasti. Tämän vuoksi Tuomari-agentti ohjeistetaan kirjaamaan tämä riski pysyväksi Systeemiseksi Epävarmuudeksi lopulliseen XAI-raporttiin.

#### <a id="luku-5-2-5"></a>5.2.5 Riski: Agenttien kognitiivinen ylikuormitus ja käyttäytymisen inversio

**Riskin kuvaus:** Pääarviointikehotteen analyysi tunnistaa kriittisen pullonkaulan, joka johtuu tiettyjen agenttien kohtuuttomasta kognitiivisesta kuormasta. Erityisesti Prosessiauditoija ja Tuomari-agentti ovat arkkitehtonisesti ylikuormitettuja. Niiden on koostettava koko dataketju ja sovellettava subjektiivisia holistisia sääntöjä. Tämä kasvattaa käsiteltävän kontekstin laajuuden (engl. *context width*) ja pituuden äärimmilleen.

Tutkimukset osoittavat, että tehtävän monimutkaisuus ([Shen ym. 2023](#shen2023)) sekä monimutkaisuuden ja kontekstin pituuden yhteisvaikutus heikentävät kielimallien suorituskykyä ja ohjeiden noudattamista (*instruction following*) merkittävästi ([Wu ym. 2024](#wu2024)).

Tämän riskin vakavin seuraus ei ole satunnainen virhe, vaan käyttäytymisen inversio. Tutkimuksissa, joissa mallien kognitiivista kuormitusta on kasvatettu monimutkaisilla tehtävillä, mallien on havaittu hylkäävän monimutkaiset, normatiiviset (esim. oikeudenmukaisuus) ohjeet ja siirtyvän yksinkertaisempaan, rationaaliseen maksimointiin ([Kirshner ym. 2025](#kirshner2025)).

"Kognitiiviselle Kvoorumille" tämä tarkoittaa, että ylikuormitettu Tuomari-agentti voi epäonnistua kaltaisten monimutkaisten, subjektiivisten sääntöjen soveltamisessa ja oikaista yksinkertaisempiin, mutta virheellisiin, ratkaisuihin. Tämä uhkaa suoraan koko järjestelmän pätevyyttä.

**Hallintamekanismi:** Lyhyellä aikavälillä riskiä hallitaan pakollisella HITL-valvonnalla ja XAI-raportoinnilla ([Luku 2.5.4](#luku-2-5-4)). Lisäksi järjestelmään on implementoitu aktiivinen huomionhallintamekanismi: "Kontekstin Segmentointi ja Fokusointi". Tämä pakottaa Tuomari-agentin soveltamaan 'System 2 Attention' -periaatetta ([Weston & Sukhbaatar 2023](#weston2023)) luomalla tietoisesti erilliset Fokus- (keskeiset todisteet/konfliktit) ja Kohina-listat (irrelevantti data). Synteesi perustuu ainoastaan Fokus-listaan. Tämä pyrkii vähentämään irrelevantin informaation aiheuttamaa häiriötä ja auttaa agenttia keskittymään kriittisimpiin todisteisiin ja konflikteihin, mikä vähentää käyttäytymisen inversion riskiä.

Pitkällä aikavälillä ratkaisu edellyttää arkkitehtuurin optimointia ([Luku 4.3.2](#luku-4-3-2)) tai tehtävien pilkkomista pienempiin osiin.

**Jäännösriski:** Riski on korkea nykyisessä arkkitehtuurissa ja riippuvainen käytettyjen yleiskäyttöisten tekoälymallien kyvykkyydestä hallita monimutkaisuutta.

### <a id="luku-5-3"></a>5.3 Operatiiviset, Eettiset ja Teknologiset Riskit – Järjestelmä Käytännössä

#### <a id="luku-5-3-1"></a>5.3.1 Riski: Automaatioharha ja Ihmisvalvonnan Taakka

**Riskin kuvaus:** Ihmisvalvoja (HITL) on altis automaatioharhalle – taipumukselle luottaa epäkriittisesti järjestelmän tuotokseen ([Parasuraman & Riley 1997](#parasuraman1997)). Mitä kehittyneempi järjestelmä, sitä suurempi riski on, että ihmisvalvoja alisuoriutuu.

**Hallintamekanismi:** Riskiä torjutaan osallistavalla raportoinnilla ([Luku 2.5.4](#luku-2-5-4)). Raporttipohja ei ole passiivinen tiedonanto, vaan se pakottaa ihmisvalvojan aktiiviseen kognitiiviseen työhön. XAI-Raportoija generoi "Kriittisiä Auditointikysymyksiä", erityisesti koskien agenttien välisiä erimielisyyksiä (JEM), joihin ihmisen on otettava kantaa ("HITL-VASTAUS VAADITAAN"). Tämä vähentää taipumusta hyväksyä raportti kritiikittömästi.

**Jäännösriski:** Automaatioharha on syvälle juurtunut piirre. Kuormittunut varmistaja voi ohittaa varoitussignaalit ja kysymykset. Ihminen on samanaikaisesti järjestelmän tärkein varmistus ja merkittävin haavoittuvuus.

#### <a id="luku-5-3-2"></a>5.3.2 Riski: Strategiset ja Eettiset Uhat

**Riskin kuvaus (Metodologinen vesittyminen):** Organisaatiot saattavat kustannussyistä jättää holistisen tason pois. Tällainen toteutuksen puutteellisuus ([Durlak & DuPre 2008](#durlak2008)) tuhoaisi järjestelmän validiteetin.

**Riskin kuvaus (Käyttötarkoituksen laajentuminen):** Riski on, että työkalu muuttuu valvontainstrumentiksi (engl. *function creep*) ([Koops 2021](#koops2021); [AI Now Institute 2021](#ainow2021)). Järjestelmän tuottama ”kognitiivinen jälki” on arkaluonteista dataa ([Weidinger ym. 2021](#weidinger2021)).

**Hallintamekanismit:** Vaativat hallinnollisia ratkaisuja (governance) ja teknisiä kontrolleja.
* **Eettiset riskit:** Kriitikko-agentti tunnistaa eettiset laiminlyönnit.
* **Vesittyminen:** Sitovat käyttöönottomallit, jotka vaativat täyden hybridiprosessin käyttöä korkean panoksen arvioinneissa.
* **Valvonta:** Eettiset säännöt, kuten kielto käyttää tuloksia ainoana perustana korkean panoksen päätöksille ja arvioitavan oikeus dataansa.

**Jäännösriski:** Teknologia ei estä väärinkäyttöä. Ilman vahvaa hallintamallia organisaatiot voivat käyttää työkalua väärin.

#### <a id="luku-5-3-3"></a>5.3.3 Riski: Teknologiset tietoturvauhat (OWASP Top 10 for LLMs)

**Riskin kuvaus:** Järjestelmä on altis yleisille LLM-tietoturvariskeille ([OWASP Foundation 2025f](#owasp2025f)).

**Hallintamekanismi:** Monikerroksinen puolustusstrategia (DiD) ([Luku 2.6](#luku-2-6)):
1.  **Tekninen Kontrollikerros:** Vartija-agentti (syötteiden puhdistus, anonymisointi) (LLM01:2025, LLM02:2025).
2.  **Behavioraalinen Kontrollikerros:** Kognitiivinen Palomuuri (LLM06:2025).
3.  **Hallinnollinen Kontrollikerros:** HITL (joka torjuu useita riskejä, kuten automaatioharhaa).

Tulevaisuudessa siirrytään perustuslailliseen tekoälyyn (CAI) ([Bai ym. 2022](#bai2022)).

**Jäännösriski:** Nykyinen kehotepohjainen Kognitiivinen Palomuuri on hauras ([Luku 2.5.1](#luku-2-5-1)).

**Taulukko 4. Keskeisimmät OWASP Top 10 for LLMs –riskit ja torjuntamekanismit.**

| OWASP-riski (2025) | Kuvaus viitekehyksen kontekstissa | Ensisijainen torjuntamekanismi |
| :--- | :--- | :--- |
| **LLM01: Prompt Injection** | Käyttäjä upottaa dataan piilotettuja komentoja manipuloidakseen Kvoorumia ([OWASP Foundation 2025a](#owasp2025a)). | Vartija-agentin suorittama syötteiden puhdistus ja aktiivinen luokittelu ([Luku 2.6.1](#luku-2-6-1)). |
| **LLM02: Sensitive Information Disclosure** | Kvoorum paljastaa tahattomasti arkaluonteista tietoa (esim. PII). | Vartija-agentin suorittama automaattinen datan anonymisointi ([Luku 2.6.1](#luku-2-6-1)). |
| **LLM03: Supply Chain Vulnerabilities** | Käytetyt ulkoiset yleiskäyttöiset tekoälymallit sisältävät haavoittuvuuksia tai muuttuvat (malliajautuminen). | "Muodolliset LLMOps-käytännöt, jatkuva regressiotestaus." |
| **LLM04: Data and Model Poisoning** | "Hyökkääjä manipuloi dataa, jota käytetään tislatun mallin (Järjestelmä 1) hienosäädössä." | Opetusdatana käytetään ainoastaan ihmisen validoimaa (HITL) dataa ([Luku 2.6.3](#luku-2-6-3)). |
| **LLM05: Improper Output Handling** | Järjestelmä välittää käsittelemättömän LLM-tuotoksen eteenpäin. | Systemaattinen tulosteen koodaus ja validointi ([Luku 2.6.3](#luku-2-6-3)). |
| **LLM06: Excessive Agency** | Agentit ylittävät niille määritellyt valtuudet. | Kognitiivinen Palomuuri sekä agenttien tekninen eristäminen ([Luku 2.5.1](#luku-2-5-1) ja [Luku 2.6.2](#luku-2-6-2)). |
| **LLM08: Vector and Embedding Weaknesses** | "Hyökkääjä manipuloi RAG-arkkitehtuuria. Kuten [Luvussa 5.1.1](#luku-5-1-1) todetaan, tämän kontrollin puuttuminen on merkittävä tekninen ja metodologinen riski." | "Tunnettu rajoite prototyypissä: Vartija-agentin metodologinen lokikirjaus, joka varoittaa puuttuvasta suojauksesta. (Huom: Visiona on aktiivinen ”Upotusten Eheyden Tarkistus”, mutta nykyinen toteutus ei sisällä geometrista poikkeamien havaitsemista, jättäen riskin teknisesti hallitsemattomaksi) ([OWASP Foundation 2025e](#owasp2025e))." |
| **LLM09: Misinformation** | "Järjestelmä tuottaa virheellistä mutta vakuuttavaa tietoa, johon ihmisvalvoja luottaa (Automaatioharha)." | Ihmisvalvonnan (HITL) prosessi ja Tuomarin XAI-rooli ([Luku 5.3.1](#luku-5-3-1)). |
| **LLM10: Unbounded Consumption** | Hyökkääjä kuormittaa järjestelmää resurssi-intensiivisillä pyynnöillä. | Teknisen tason käytön rajoittaminen (rate limiting) ([OWASP Foundation 2025g](#owasp2025g)). |
## <a id="luku-6"></a>Luku 6: Johtopäätökset ja Tutkimusagenda

Tässä artikkelissa on esitetty uusi teoreettinen viitekehys, hybridirubriikki, ja sen operatiivinen malli, Kognitiivinen Kvoorum. Esitämme hypoteesin, että tämä kaksitasoinen arkkitehtuuri voi tarjota perinteisiä menetelmiä luotettavamman (korkeampi reliabiliteetti) ja pätevämmän (korkeampi pätevyys) tavan arvioida monimutkaista tekoälyosaamista.

Tämä arkkitehtuuri toteutetaan käytännössä moniagenttisena Kognitiivisena kvoorumina ja sen perustana on Kahnemanin kaksoisprosessiteoria, mikä vahvistaa systemaattista ja auditoitavaa arviointiprosessia. Tämän hypoteesin todentaminen edellyttää tulevaa empiiristä tutkimusta. Tämän vuoksi esitämme tutkimusagendan, jonka keskiössä on viitekehyksen ydinlupauksen systemaattinen validointi.

Viitekehyksen arvo syntyy sen filosofiasta: luottamus rakennetaan auditoitavan päättelyprosessin kautta, joka hallitsee ”reliabiliteetin ja validiteetin paradoksia” ([Luku 1.3](#luku-1-3)).

### <a id="luku-6-1"></a>6.1 Hypoteesin validoinnin ja jatkokehityksen edellytykset

Hypoteesin testaaminen ja jatkokehitys edellyttävät siirtymistä kohti monimutkaisemman, kaksitasoisen järjestelmän hallintaa. Kriittisiä tekijöitä ovat:

* **Holistisen tason ohjauksen hallinta:** Kognitiivisen Kvoorumin luotettava käyttö edellyttää kykyä hallita agenttien työnkulkua, minimoida viivettä ja optimoida kustannuksia (vrt. [Anthropic 2025b](#anthropic2025b); [Mesenbrink ym. 2025](#mesenbrink2025)).
* **HITL-valvonnan kehittäminen validoinnin ytimenä:** Validiteetin arviointi nojaa ihmisvalvojan (HITL) kykyyn toimia tehokkaana valvojana ja ratkaista sisäiset jännitteet. Tämä edellyttää koulutusta ja työkaluja automaatioharhan tunnistamiseksi ([Parasuraman & Riley 1997](#parasuraman1997)).
* **Data-strategia ja hybridilogiikan tislauskyky:** Siirtymä (”Järjestelmä 1”) vaiheeseen on kriittistä skaalautuvuuden kannalta. Tämä edellyttää kykyä ”tislata” hybridirubriikin logiikka yhdelle mallille, mikä vaatii korkealaatuisen päättelydatan (”kognitiivisten jälkien”) keräämistä ja datatieteen osaamista.

### <a id="luku-6-2"></a>6.2 Tutkimusagenda: Seuraavat vaiheet

Ennen empiirisen tutkimusagendan toteuttamista on ehdottoman välttämätöntä hankkia eettinen ennakkoarviointi ja hyväksyntä asiaankuuluvalta tutkimuseettiseltä toimikunnalta noudattaen Suomessa ihmistieteiden tutkimusta koskevia kansallisia ohjeistuksia ([Tutkimuseettinen neuvottelukunta TENK 2019](#tenk2019)).

Koska viitekehyksen toiminnallinen malli on toteutettu mutta empiirisesti testaamatta, viitekehykseltä puuttuu toistaiseksi empiirinen näyttö. Kuten [luvussa 5.1.1](#luku-5-1-1) todetaan, sen arvo perustuu todentamattomaan hypoteesiin. Seuraava tutkimusagenda on ehdoton edellytys väitteiden todentamiseksi:

1.  **Viitekehyksen ydinlupauksen todentaminen luotettavuustutkimuksella (kriittinen ja välitön ensisijainen tavoite).** Agenda jakautuu kahteen vaiheeseen:
    * **Ulkoisen validiteetin testaus (arvioijien välinen luotettavuus IRR):** On välittömästi käynnistettävä vertaileva pilottitutkimus (n=50), joka mittaa Kognitiivisen Kvoorumin arvioitsijareliabiliteetin (IRR) suhteessa ihmisasiantuntijoihin.
    * **Tutkimusasetelmassa:**
        * **Aineisto:** Kerätään 50 autenttista tekoälyavusteista opiskelijatyötä (sis. keskusteluhistorian).
        * **Ihmisverrokki:** Kolme riippumatonta, sokoutettua ihmisarvioijaa pisteyttää työt Hybridirubriikilla (Cohenin Kappa).
        * **Kvoorum-ajo:** Sama aineisto syötetään Kognitiiviselle Kvoorumille (heterogeeninen konfiguraatio: GPT-4 & Claude 3.5).
        * **Analyysi:** Mitataan Kvoorumin ja ihmisten välinen vastaavuus sekä Kvoorumin sisäinen konsistenssi toistomittauksilla. Tämä vastaa kritiikkiin AI-arvioinnin stokastisuudesta.
2.  **Holistisen validiteetin testaus (Goodhartin Laki):** On mitattava kestävyyttä ”performatiivista reflektiota” ([Cullen 2020](#cullen2020)) vastaan. On suoritettava koe, jossa testataan ”Epäilyttävä Täydellisyys” -heuristiikan kykyä erottaa aidot suoritukset optimoiduista ([Strathern 1997](#strathern1997)).
3.  **Arkkitehtuurin tehostaminen ja datastrategian priorisointi.** Käynnistetään rinnakkaisen orkestrointimallin pilotointi ja systemaattinen päättelydatan kerääminen. Tämä data mahdollistaa tulevaisuudessa tislatun mallin (”Järjestelmä 1”) kouluttamisen.

---

## <a id="lahdeluettelo"></a>Lähdeluettelo

* <a id="acemoglu2018"></a>**Acemoglu, Daron & Restrepo, Pascual.** 2018: The race between man and machine: Implications of technology for growth, factor shares, and employment. American Economic Review, 108(6), 1488–1542. DOI: <a href="https://doi.org/10.1257/aer.20160696">10.1257/aer.20160696</a>.
* <a id="adadi2018"></a>**Adadi, Amina & Berrada, Mohammed.** 2018: Peeking inside the black-box: A survey on explainable artificial intelligence (XAI). IEEE Access, 6, 52138–52160. DOI: <a href="https://doi.org/10.1109/ACCESS.2018.2870052">10.1109/ACCESS.2018.2870052</a>.
* <a id="aera2014"></a>**AERA, APA & NCME.** 2014: *Standards for educational and psychological testing*. Washington, DC: American Educational Research Association. [Verkkojulkaisu]. Saatavilla: https://www.testingstandards.net/uploads/7/6/6/4/76643089/standards_2014edition.pdf. [Haettu 14.11.2025].
* <a id="agrawal2022"></a>**Agrawal, Ajay; Gans, Joshua & Goldfarb, Avi.** 2022: *Prediction machines: The simple economics of artificial intelligence*. Boston: Harvard Business Review Press.
* <a id="ahmad2024"></a>**Ahmad, Sultan ym.** 2024: A comprehensive review of retrieval-augmented generation (RAG): Key challenges and future directions. arXiv preprint arXiv:2410.12837. DOI: <a href="https://doi.org/10.48550/arXiv.2410.12837">10.48550/arXiv.2410.12837</a>.
* <a id="ahuna2025"></a>**Ahuna, Kelly & Kiener, Michael.** 2025: Beyond digital literacy: Cultivating “meta AI” skills in students and faculty. Faculty Focus. Julkaistu 6.8.2025. [Verkkojulkaisu]. Saatavilla: https://www.facultyfocus.com/articles/teaching-with-technology-articles/beyond-digital-literacy-cultivating-meta-ai-skills-in-students-and-faculty/. [Haettu 14.11.2025].
* <a id="aimultiple2025"></a>**AIMultiple.** 2025: 15 Security Threats to LLM Agents (with Real-World Examples). Research AIMultiple. [Verkkojulkaisu]. Saatavilla: https://research.aimultiple.com/security-of-ai-agents/. [Haettu 16.11.2025].
* <a id="ainow2021"></a>**AI Now Institute.** 2021: *A New AI Lexicon: Function Creep*. New York: AI Now Institute. [Verkkojulkaisu]. Saatavilla: https://ainowinstitute.org/publications/collection/a-new-ai-lexicon-function-creep. [Haettu 14.11.2025].
* <a id="anderson2001"></a>**Anderson, Lorin W. & Krathwohl, David R. (toim.).** 2001: *A taxonomy for learning, teaching, and assessing: A revision of Bloom’s taxonomy of educational objectives*. New York: Longman.
* <a id="anthropic2025a"></a>**Anthropic.** 2025a: Constitutional classifiers. Anthropic Policy & Research. [Verkkojulkaisu]. Saatavilla: https://www.anthropic.com/research/constitutional-classifiers. [Haettu 14.11.2025].
* <a id="anthropic2025b"></a>**Anthropic.** 2025b: How we built our multi-agent research system. Anthropic Engineering Blog. Julkaistu 13.6.2025. [Verkkojulkaisu]. Saatavilla: https://www.anthropic.com/engineering/multi-agent-research-system. [Haettu 14.11.2025].
* <a id="anthropic2025c"></a>**Anthropic.** 2025c: Building effective agents. Anthropic Research. [Verkkojulkaisu]. Saatavilla: https://www.anthropic.com/research/building-effective-agents. [Haettu 14.11.2025].
* <a id="arcuschin2025"></a>**Arcuschin, Iván ym.** 2025: Chain-of-Thought Reasoning In The Wild Is Not Always Faithful. arXiv preprint arXiv:2503.08679. DOI: <a href="https://doi.org/10.48550/arXiv.2503.08679">10.48550/arXiv.2503.08679</a>.
* <a id="aryan2025"></a>**Aryan, Ali & Liu, Zhi.** 2025: Causal Reflection with Language Models. arXiv preprint arXiv:2508.04495. DOI: <a href="https://doi.org/10.48550/ARXIV.2508.04495">10.48550/ARXIV.2508.04495</a>.
* <a id="auzmor2024"></a>**Auzmor.** 2024: How to measure the ROI of AI training programs. Auzmor. [Verkkojulkaisu]. Saatavilla: https://auzmor.com/blog/measure-the-roi-of-ai-training-programs/. [Haettu 14.11.2025].
* <a id="bai2022"></a>**Bai, Yuntao ym.** 2022: Constitutional AI: Harmlessness from AI feedback. arXiv preprint arXiv:2212.08073. DOI: <a href="https://doi.org/10.48550/arXiv.2212.08073">10.48550/arXiv.2212.08073</a>.
* <a id="bareinboim2022"></a>**Bareinboim, Elias ym.** 2022: On Pearl's hierarchy and the foundations of causal inference. Teoksessa H. Geffner, R. Dechter & J. Halpern (toim.), *Probabilistic and causal inference: The works of Judea Pearl*. New York: Association for Computing Machinery, 507–556. DOI: <a href="https://doi.org/10.1145/3501714.3501743">10.1145/3501714.3501743</a>.
* <a id="baume2002"></a>**Baume, David & Yorke, Mantz.** 2002: The reliability of assessment by portfolio on a course to develop and accredit teachers in higher education. Studies in Higher Education, 27(1), 7–25. DOI: <a href="https://doi.org/10.1080/03075070120099340">10.1080/03075070120099340</a>.
* <a id="bezanilla2019"></a>**Bezanilla, María José ym.** 2019: Methodologies for teaching-learning in higher education and their relationship with student competences: A systematic review. Educational Research Review, 27, 83–98. DOI: <a href="https://doi.org/10.1016/j.edurev.2019.01.004">10.1016/j.edurev.2019.01.004</a>.
* <a id="biggs1982"></a>**Biggs, John B. & Collis, Kevin F.** 1982: *Evaluating the quality of learning: The SOLO taxonomy (Structure of the Observed Learning Outcome)*. New York: Academic Press.
* <a id="borsboom2004"></a>**Borsboom, Denny; Mellenbergh, Gideon J. & van Heerden, Jaap.** 2004: The concept of validity. Psychological Review, 111(4), 1061–1071. DOI: <a href="https://doi.org/10.1037/0033-295X.111.4.1061">10.1037/0033-295X.111.4.1061</a>.
* <a id="boussioux2025"></a>**Boussioux, Leonard.** 2025: Revolutionize quality assurance with AI. Mareana. [Verkkojulkaisu]. Saatavilla: https://mareana.com/whitepaper/qa-playbook/. [Haettu 14.11.2025].
* <a id="brennan2001"></a>**Brennan, Robert L.** 2001: *Generalizability theory*. New York: Springer.
* <a id="brooks1987"></a>**Brooks, Frederick P.** 1987: No silver bullet: Essence and accidents of software engineering. Computer, 20(4), 10–19. DOI: <a href="https://doi.org/10.1109/MC.1987.1663532">10.1109/MC.1987.1663532</a>.
* <a id="bulut2024"></a>**Bulut, Okan ym.** 2024: The Rise of Artificial Intelligence in Educational Measurement: Opportunities and Ethical Challenges. Chinese/English Journal of Educational Measurement and Evaluation, 5(3), Artikla 3. DOI: <a href="https://doi.org/10.59863/MIQL7785">10.59863/MIQL7785</a>.
* <a id="carolus2023"></a>**Carolus, Angela ym.** 2023: MAILS - Meta AI literacy scale: Development and testing of an AI literacy questionnaire based on well-founded competency models and psychological change- and meta-competencies. arXiv preprint arXiv:2302.09319. DOI: <a href="https://doi.org/10.48550/arXiv.2302.09319">10.48550/arXiv.2302.09319</a>.
* <a id="cemri2025"></a>**Cemri, M. ym.** 2025: Why do multi-agent LLM systems fail? arXiv preprint arXiv:2503.13657. DOI: <a href="https://doi.org/10.48550/arXiv.2503.13657">10.48550/arXiv.2503.13657</a>.
* <a id="citl2025"></a>**Center for Innovative Teaching & Learning.** 2025: Authentic assessment. Indiana University Bloomington. [Verkkojulkaisu]. Saatavilla: https://citl.indiana.edu/teaching-resources/assessing-student-learning/authentic-assessment/index.html. [Haettu 14.11.2025].
* <a id="cheng2001"></a>**Cheng, Peter C-H.** 2001: Scientific discovery, computational models of. Teoksessa N. J. Smelser & P. B. Baltes (toim.), *International encyclopedia of the social & behavioral sciences*. Amsterdam: Elsevier, 13783–13787. DOI: <a href="https://doi.org/10.1016/B978-0-08-097086-8.43085-0">10.1016/B978-0-08-097086-8.43085-0</a>.
* <a id="cheng2021"></a>**Cheng, Peter.** 2021: Competence assessment by stimulus matching: an application of GOMS to assess chunks in memory. Teoksessa *Proceedings of the 19th International Conference on Cognitive Modelling (ICCM 2021)*. [Verkkojulkaisu]. Saatavilla: https://cidlab.com/files/smp/pb/pb-2021.pdf. [Haettu 14.11.2025].
* <a id="chi2024"></a>**Chi, Hao ym.** 2024: Unveiling causal reasoning in large language models: Reality or mirage? Advances in Neural Information Processing Systems, 37, 96640–96670. DOI: <a href="https://doi.org/10.48550/arXiv.2506.21215">10.48550/arXiv.2506.21215</a>.
* <a id="cisa2016"></a>**CISA.** 2016: *Defense in depth*. Cybersecurity and Infrastructure Security Agency. [Verkkojulkaisu]. Saatavilla: https://www.cisa.gov/sites/default/files/recommended_practices/NCCIC_ICS-CERT_Defense_in_Depth_2016_S508C.pdf. [Haettu 14.11.2025].
* <a id="cohen1996"></a>**Cohen, Ronald Jay; Swerdlik, Mark E. & Phillips, Sturman M.** 1996: *Psychological testing and assessment: An introduction to tests and measurement*. 3. painos. Mountain View: Mayfield Publishing Company.
* <a id="creswell2024"></a>**Creswell, Antonia ym.** 2024: Reducing post-hoc rationalization in large language models. Findings of the Association for Computational Linguistics: ACL 2024, 14757–14771. DOI: <a href="https://doi.org/10.18653/v1/2024.findings-acl.867">10.18653/v1/2024.findings-acl.867</a>.
* <a id="cullen2020"></a>**Cullen, Michael J.** 2020: Faking in high-stakes selection: A call to integrate empirical research and applied practice. International Journal of Selection and Assessment, 28(3), 223–226. DOI: <a href="https://doi.org/10.1111/ijsa.12289">10.1111/ijsa.12289</a>.
* <a id="dangelo2025"></a>**D'Angelo, Matt.** 2025: AI safety vs AI security in LLM applications: What teams must know. promptfoo. [Verkkojulkaisu]. Saatavilla: https://www.promptfoo.dev/blog/ai-safety-vs-security/. [Haettu 14.11.2025].
* <a id="david2019"></a>**David, Jane L.** 2019: 15 reasons why standardized tests are problematic. ASCD Blog. [Verkkojulkaisu]. Saatavilla: https://www.ascd.org/blogs/15-reasons-why-standardized-tests-are-problematic. [Haettu 14.11.2025].
* <a id="debruin2023"></a>**de Bruin, Anique B. H.; van Merriënboer, Jeroen J. G. & van Gog, Tamara.** 2023: The role of cognitive effort in fostering the acquisition of complex cognitive skills. Teoksessa J. Sweller, J. J. G. van Merriënboer & F. Paas (toim.), *Cognitive load theory: A research-based guide to instructional design*. Cambridge: Cambridge University Press, 237–256. DOI: <a href="https://doi.org/10.1017/9781009403718.011">10.1017/9781009403718.011</a>.
* <a id="denning1977"></a>**Denning, Dorothy E. & Denning, Peter J.** 1977: Certification of programs for secure information flow. Communications of the ACM, 20(7), 504–513. DOI: <a href="https://doi.org/10.1145/359636.359712">10.1145/359636.359712</a>.
* <a id="derkiureghian2009"></a>**Der Kiureghian, Armen & Ditlevsen, Ove.** 2009: Aleatory or epistemic? Does it matter? Structural Safety, 31(2), 105–112. DOI: <a href="https://doi.org/10.1016/j.strusafe.2008.06.020">10.1016/j.strusafe.2008.06.020</a>.
* <a id="disco2024"></a>**Disco.** 2024: How to assess the ROI of AI-driven upskilling initiatives. Disco. [Verkkojulkaisu]. Saatavilla: https://www.disco.co/blog/how-to-assess-the-roi-of-ai-driven-upskilling-initiatives. [Haettu 14.11.2025].
* <a id="displayr2024"></a>**Displayr.** 2024: Discover the 5 best AI tools for qualitative data analysis. Displayr. [Verkkojulkaisu]. Saatavilla: https://www.displayr.com/discover-the-5-best-ai-tools-for-qualitative-data-analysis/. [Haettu 14.11.2025].
* <a id="dreyfus1980"></a>**Dreyfus, Stuart E. & Dreyfus, Hubert L.** 1980: *A Five-Stage Model of the Mental Activities Involved in Directed Skill Acquisition*. California Univ Berkeley Operations Research Center. [Verkkojulkaisu]. Saatavilla: https://apps.dtic.mil/sti/pdfs/ADA084551.pdf. [Haettu 18.11.2025].
* <a id="du2023"></a>**Du, Yilun ym.** 2023: Improving factuality and reasoning in language models through multiagent debate. arXiv preprint arXiv:2305.14325. DOI: 10.48550/arXiv.2305.14325.
* <a id="dufner2019"></a>**Dufner, Michael ym.** 2019: Self-enhancement and psychological adjustment: A meta-analytic review. Personality and Social Psychology Review, 23(1), 48–72. DOI: 10.1177/1088868318756467.
* <a id="duhem1906"></a>**Duhem, Pierre.** 1906: *La théorie physique: son objet et sa structure*. Paris: Chevalier & Rivière.
* <a id="durlak2008"></a>**Durlak, Joseph A. & DuPre, Elizabeth P.** 2008: Implementation matters: A review of research on the influence of implementation on program outcomes and the factors affecting implementation. American Journal of Community Psychology, 41(3–4), 327–350. DOI: <a href="https://doi.org/10.1007/s10464-008-9165-0">10.1007/s10464-008-9165-0</a>.
* <a id="eloundou2023"></a>**Eloundou, Tyna; Manning, Sam; Mishkin, Pamela & Rock, Daniel.** 2023: GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models. arXiv preprint arXiv:2303.10130. DOI: <a href="https://doi.org/10.48550/arXiv.2303.10130">10.48550/arXiv.2303.10130</a>.
* <a id="embretson2000"></a>**Embretson, Susan E. & Reise, Steven P.** 2000: *Item response theory for psychologists*. Mahwah: Lawrence Erlbaum Associates.
* <a id="eu2024"></a>**Euroopan parlamentti & Euroopan unionin neuvosto.** 2024: *Euroopan parlamentin ja neuvoston asetus (EU) 2024/1689, annettu 13 päivänä kesäkuuta 2024, tekoälyä koskevista yhdenmukaistetuista säännöistä ja asetusten (EY) N:o 300/2008, (EU) N:o 167/2013, (EU) N:o 168/2013, (EU) 2018/858, (EU) 2018/1139 ja (EU) 2019/2144 sekä direktiivien 2014/90/EU, (EU) 2016/797 ja (EU) 2020/1828 muuttamisesta (tekoälysäädös)*. Euroopan unionin virallinen lehti, L, 2024/1689. https://eur-lex.europa.eu/eli/reg/2024/1689/oj
* <a id="eu2019"></a>**Euroopan komission korkean tason asiantuntijaryhmä.** 2019: *Ethics guidelines for trustworthy AI*. Bryssel: Euroopan komissio. [Verkkojulkaisu]. Saatavilla: https://digital-strategy.ec.europa.eu/en/library/ethics-guidelines-for-trustworthy-ai. [Haettu 14.11.2025].
* <a id="evans2013"></a>**Evans, Jonathan St. B. T. & Stanovich, Keith E.** 2013: Dual-process theories of higher cognition: Advancing the debate. Perspectives on Psychological Science, 8(3), 223–241. DOI: <a href="https://doi.org/10.1177/1745691612460685">10.1177/1745691612460685</a>.
* <a id="fairtest2012"></a>**FairTest.** 2012: The limits of standardized tests for diagnosing and assisting student learning. FairTest: The National Center for Fair & Open Testing. [Verkkojulkaisu]. Saatavilla: https://fairtest.org/limits-standardized-tests-diagnosing-and-assisting/. [Haettu 14.11.2025].
* <a id="federiakin2024"></a>**Federiakin, Denis ym.** 2024: Prompt engineering: A new skill for the future of work. Procedia Computer Science, 231, 401–409. DOI: <a href="https://doi.org/10.1016/j.procs.2023.12.233">10.1016/j.procs.2023.12.233</a>.
* <a id="festinger1957"></a>**Festinger, Leon.** 1957: *A theory of cognitive dissonance*. Stanford: Stanford University Press.
* <a id="flavell1979"></a>**Flavell, John H.** 1979: Metacognition and cognitive monitoring: A new area of cognitive-developmental inquiry. American Psychologist, 34(10), 906–911. DOI: <a href="https://doi.org/10.1037/0003-066X.34.10.906">10.1037/0003-066X.34.10.906</a>.
* <a id="fugener2025"></a>**Fügener, Andreas; Walzner, Daniel D. & Gupta, Alok.** 2025: Roles of Artificial Intelligence in Collaboration with Humans: Automation, Augmentation, and the Future of Work. Management Science. DOI: <a href="https://doi.org/10.1287/mnsc.2024.05684">10.1287/mnsc.2024.05684</a>.
* <a id="ganascia2017"></a>**Ganascia, Jean-Gabriel.** 2017: A Popperian falsification of artificial intelligence - Lighthill. arXiv preprint arXiv:1704.08111. DOI: <a href="https://doi.org/10.48550/arXiv.1704.08111">10.48550/arXiv.1704.08111</a>.
* <a id="ganguli2022"></a>**Ganguli, Deep ym.** 2022: Red teaming language models to reduce harms: Methods, scaling behaviors, and lessons learned. arXiv preprint arXiv:2209.07858. DOI: <a href="https://doi.org/10.48550/arXiv.2209.07858">10.48550/arXiv.2209.07858</a>.
* <a id="gao2022"></a>**Gao, Luyu ym.** 2022: Precise zero-shot dense retrieval without relevance labels. arXiv preprint arXiv:2212.10496. DOI: <a href="https://doi.org/10.48550/arXiv.2212.10496">10.48550/arXiv.2212.10496</a>.
* <a id="goffman1959"></a>**Goffman, Erving.** 1959: *The presentation of self in everyday life*. New York: Doubleday.
* <a id="goodfellow2014"></a>**Goodfellow, Ian J. ym.** 2014: Generative adversarial networks. Advances in Neural Information Processing Systems, 27, 2672–2680. DOI: <a href="https://doi.org/10.48550/arXiv.1406.2661">10.48550/arXiv.1406.2661</a>.
* <a id="google2025a"></a>**Google DeepMind.** 2025a: *Gemini 3 Pro Model Card*. [PDF]. Saatavilla: https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf. [Haettu 14.11.2025].
* <a id="google2025b"></a>**Google DeepMind.** 2025b: *Gemini 3 Pro Model Evaluation*. [PDF]. Saatavilla: https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_model_evaluation.pdf. [Haettu 14.11.2025].
* <a id="google2025c"></a>**Google DeepMind.** 2025c: Gemini 3: A new era of intelligence. Google Blog. Julkaistu 18.11.2025. [Verkkojulkaisu]. Saatavilla: https://blog.google/products/gemini/gemini-3/. [Haettu 14.11.2025].
* <a id="greshake2023"></a>**Greshake, Kai ym.** 2023: Not what you’ve signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection. arXiv preprint arXiv:2302.12173. DOI: <a href="https://doi.org/10.48550/arXiv.2302.12173">10.48550/arXiv.2302.12173</a>.
* <a id="guo2024"></a>**Guo, Taicheng ym.** 2024: Large language model based multi-agents: A survey of progress and challenges. Proceedings of the Thirty-Third International Joint Conference on Artificial Intelligence, 8048–8057. DOI: <a href="https://doi.org/10.24963/ijcai.2024/890">10.24963/ijcai.2024/890</a>.
* <a id="hazan2024"></a>**Hazan, Eric ym.** 2024: A new future of work: The race to deploy AI and raise skills in Europe and beyond. McKinsey Global Institute. [Verkkojulkaisu]. Saatavilla: https://www.mckinsey.com/mgi/our-research/a-new-future-of-work-the-race-to-deploy-ai-and-raise-skills-in-europe-and-beyond. [Haettu 14.11.2025].
* <a id="hevner2004"></a>**Hevner, Alan R.; March, Salvatore T.; Park, Jinsoo & Ram, Sudha.** 2004: Design Science in Information Systems Research. MIS Quarterly, 28(1), 75–105. DOI: <a href="https://doi.org/10.2307/25148625">10.2307/25148625</a>.
* <a id="hinton2015"></a>**Hinton, Geoffrey; Vinyals, Oriol & Dean, Jeffrey.** 2015: Distilling the knowledge in a neural network. arXiv preprint arXiv:1503.02531. DOI: <a href="https://doi.org/10.48550/arXiv.1503.02531">10.48550/arXiv.1503.02531</a>.
* <a id="huang2023"></a>**Huang, Lei ym.** 2023: A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions. ACM Transactions on Information Systems. DOI: <a href="https://doi.org/10.1145/3703155">10.1145/3703155</a>.
* <a id="hullermeier2021"></a>**Hüllermeier, Eyke & Waegeman, Willem.** 2021: Aleatoric and epistemic uncertainty in machine learning: an introduction to concepts and methods. Machine Learning, 110, 457–506. DOI: <a href="https://doi.org/10.1007/s10994-021-05946-3">10.1007/s10994-021-05946-3</a>.
* <a id="hume1739"></a>**Hume, David.** 1739: *A Treatise of Human Nature: Being an Attempt to Introduce the Experimental Method of Reasoning into Moral Subjects*. Lontoo: John Noon. https://archive.org/details/treatiseofhumann01hume
* <a id="hyland2005"></a>**Hyland, Ken.** 2005: *Metadiscourse: Exploring interaction in writing*. Lontoo: Continuum.
* <a id="inan2023"></a>**Inan, Hakan ym.** 2023: Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations. arXiv preprint arXiv:2312.06674. DOI: <a href="https://doi.org/10.48550/arXiv.2312.06674">10.48550/arXiv.2312.06674</a>.
* <a id="isaca2025"></a>**ISACA.** 2025: 2025 Volume 5 How to measure and prove the value of your AI investments. ISACA. [Verkkojulkaisu]. Saatavilla: https://www.isaca.org/resources/news-and-trends/newsletters/atisaca/2025/volume-5/how-to-measure-and-prove-the-value-of-your-ai-investments. [Haettu 14.11.2025].
* <a id="iso2023"></a>**ISO/IEC.** 2023: *Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models (ISO/IEC 25010:2023)*. Geneve: International Organization for Standardization. [Verkkojulkaisu]. Saatavilla: https://www.iso.org/standard/84727.html. [Haettu 14.11.2025].
* <a id="jacobs1980"></a>**Jacobs, Rick; Kafry, Dalia & Zedeck, Sheldon.** 1980: Expectations of behaviorally anchored rating scales. Personnel Psychology, 33(3), 595–640. DOI: <a href="https://doi.org/10.1111/j.1744-6570.1980.tb00486.x">10.1111/j.1744-6570.1980.tb00486.x</a>.
* <a id="jacovi2020"></a>**Jacovi, Alon & Goldberg, Yoav.** 2020: Towards faithfully interpretable NLP systems: How should we define and evaluate faithfulness? Teoksessa *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics*. Association for Computational Linguistics, 4198–4205. DOI: <a href="https://doi.org/10.18653/v1/2020.acl-main.385">10.18653/v1/2020.acl-main.385</a>.
* <a id="jagerman2023"></a>**Jagerman, Rolf ym.** 2023: Query expansion by prompting large language models. arXiv preprint arXiv:2305.03653. DOI: <a href="https://doi.org/10.48550/arXiv.2305.03653">10.48550/arXiv.2305.03653</a>.
* <a id="jia2025"></a>**Jia, Yihao; Shao, Zenghui; Liu, Yanyi; Jia, Jinyuan; Song, Dawn & Gong, Neil Zhenqiang.** 2025: A Critical Evaluation of Defenses against Prompt Injection Attacks. arXiv preprint arXiv:2505.18333. DOI: <a href="https://doi.org/10.48550/arXiv.2505.18333">10.48550/arXiv.2505.18333</a>.
* <a id="johnson2004"></a>**Johnson, R. Burke & Onwuegbuzie, Anthony J.** 2004: Mixed methods research: A research paradigm whose time has come. Educational Researcher, 33(7), 14–26. DOI: <a href="https://doi.org/10.3102/0013189X033007014">10.3102/0013189X033007014</a>.
* <a id="jonsson2007"></a>**Jonsson, Anders & Svingby, Gunilla.** 2007: The use of scoring rubrics: Reliability, validity and educational consequences. Educational Research Review, 2(2), 130–144. DOI: <a href="https://doi.org/10.1016/j.edurev.2007.05.002">10.1016/j.edurev.2007.05.002</a>.
* <a id="kahneman2011"></a>**Kahneman, Daniel.** 2011: *Thinking, fast and slow*. New York: Farrar, Straus and Giroux.
* <a id="kiciman2023"></a>**Kiciman, Emre ym.** 2023: Causal reasoning and large language models: Opening a new frontier for causality. arXiv preprint arXiv:2305.00050. DOI: <a href="https://doi.org/10.48550/arXiv.2305.00050">10.48550/arXiv.2305.00050</a>.
* <a id="kim2022"></a>**Kim, Dong-Gi ym.** 2022: Assessing non-technical skills in medical students: An evaluation of the inter- and intra-rater reliability of the behaviorally anchored rating scale (BARS). Teaching and Learning in Medicine, 35(3), 310–319. DOI: <a href="https://doi.org/10.1080/10872981.2022.2070940">10.1080/10872981.2022.2070940</a>.
* <a id="kinicki1985"></a>**Kinicki, Angelo J. ym.** 1985: Behaviorally anchored rating scales vs. summated rating scales: Psychometric properties and susceptibility to rating bias. Educational and Psychological Measurement, 45(3), 535–549. DOI: <a href="https://doi.org/10.1177/001316448504500310">10.1177/001316448504500310</a>.
* <a id="kirshner2025"></a>**Kirshner, Stuart; Klaben, Ben & Dobbe, Sam.** 2025: Instruction-Following: The Truth Is In There, But Is It In The Loss? arXiv preprint arXiv:2511.07973. DOI: <a href="https://doi.org/10.48550/arXiv.2511.07973">10.48550/arXiv.2511.07973</a>.
* <a id="klein2007"></a>**Klein, Gary.** 2007: Performing a Project Premortem. Harvard Business Review, 85(9), 18–19.
* <a id="klieger2018"></a>**Klieger, David M. ym.** 2018: Development of the Behaviorally Anchored Rating Scales for the Skills Demonstration and Progression Guide. ETS Research Report Series RR-18-24. Educational Testing Service. DOI: <a href="https://doi.org/10.1002/ets2.12210">10.1002/ets2.12210</a>.
* <a id="koops2021"></a>**Koops, Bert-Jaap.** 2021: The concept of function creep. Law, Innovation and Technology, 13(1), 29–56. DOI: <a href="https://doi.org/10.1080/17579961.2021.1898299">10.1080/17579961.2021.1898299</a>.
* <a id="koretz1994"></a>**Koretz, Daniel M. ym.** 1994: The Vermont portfolio assessment program: Findings and implications. Educational Measurement: Issues and Practice, 13(3), 5–16. DOI: <a href="https://doi.org/10.1111/j.1745-3992.1994.tb00854.x">10.1111/j.1745-3992.1994.tb00854.x</a>.
* <a id="kreuzberger2023"></a>**Kreuzberger, Dominik; Kühl, Niklas & Hirschl, Sebastian.** 2023: Machine learning operations (MLOps): Overview, definition, and architecture. IEEE Access, 11, 31866–31879. DOI: <a href="https://doi.org/10.1109/ACCESS.2023.3262138">10.1109/ACCESS.2023.3262138</a>.
* <a id="kruger1999"></a>**Kruger, Justin & Dunning, David.** 1999: Unskilled and unaware of it: How difficulties in recognizing one's own incompetence lead to inflated self-assessments. Journal of Personality and Social Psychology, 77(6), 1121–1134. DOI: <a href="https://doi.org/10.1037/0022-3514.77.6.1121">10.1037/0022-3514.77.6.1121</a>.
* <a id="lagnado2006"></a>**Lagnado, David A. & Sloman, Steven A.** 2006: Time as a guide to cause. Journal of Experimental Psychology: Learning, Memory & Cognition, 32(3), 451–460. DOI: <a href="https://doi.org/10.1037/0278-7393.32.3.451">10.1037/0278-7393.32.3.451</a>.
* <a id="lane2013"></a>**Lane, Suzanne.** 2013: Validity evidence for assessments of higher-order thinking. Journal of Educational Measurement, 50(4), 399–430. DOI: <a href="https://doi.org/10.1111/jedm.12028">10.1111/jedm.12028</a>.
* <a id="larson2024"></a>**Larson, Barbara Z. ym.** 2024: Critical thinking in the age of generative AI. Academy of Management Learning & Education, 23(3). DOI: <a href="https://doi.org/10.5465/amle.2024.0338">10.5465/amle.2024.0338</a>.
* <a id="lecun2022"></a>**LeCun, Yann.** 2022: A path towards autonomous machine intelligence. OpenReview. [Verkkojulkaisu]. Saatavilla: https://openreview.net/forum?id=BZ5a1r-kVsf. [Haettu 14.11.2025].
* <a id="levashina2007"></a>**Levashina, Julia & Morgeson, Frederick P.** 2007: Applicant faking on personality measures: A coping perspective. Academy of Management Review, 32(4), 1118–1136. DOI: <a href="https://doi.org/10.5465/amr.2007.26586083">10.5465/amr.2007.26586083</a>.
* <a id="levine1988"></a>**Levine, Edward L.; Ash, Ronald A. & Bennett, Nathan.** 1988: The "behavioral consistency" approach to job analysis: A critical reappraisal. Human Resource Management Review, 8(3), 273–293. DOI: <a href="https://doi.org/10.1016/S1053-4822(98)90023-6">10.1016/S1053-4822(98)90023-6</a>.
* <a id="lewis2020"></a>**Lewis, Patrick ym.** 2020: Retrieval-augmented generation for knowledge-intensive NLP tasks. Advances in Neural Information Processing Systems, 33, 9459–9474. DOI: <a href="https://doi.org/10.48550/arXiv.2005.11401">10.48550/arXiv.2005.11401</a>.
* <a id="li2025"></a>**Li, Feng ym.** 2025: An assessment of human–AI interaction capability in the generative AI era: The influence of critical thinking. Journal of Intelligence, 13(6), 62. DOI: <a href="https://doi.org/10.3390/jintelligence13060062">10.3390/jintelligence13060062</a>.
* <a id="li2024"></a>**Li, Zhikun ym.** 2024: PII-Bench: A benchmark for personally identifiable information (PII) detection and anonymization. arXiv preprint arXiv:2404.03893. DOI: <a href="https://doi.org/10.48550/arXiv.2404.03893">10.48550/arXiv.2404.03893</a>.
* <a id="liang2023"></a>**Liang, Tian-Shuo ym.** 2023: Encouraging divergent thinking in large language models through multi-agent debate. arXiv preprint arXiv:2305.19118. DOI: <a href="https://doi.org/10.48550/arXiv.2305.19118">10.48550/arXiv.2305.19118</a>.
* <a id="lippi2016"></a>**Lippi, Marco & Torroni, Paolo.** 2016: Argumentation mining: State of the art and emerging trends. ACM Transactions on Internet Technology, 16(2), 1–25. DOI: <a href="https://doi.org/10.1145/2850417">10.1145/2850417</a>.
* <a id="lison2021"></a>**Lison, Pierre ym.** 2021: Anonymisation models for text data: State of the art, challenges and future directions. arXiv preprint arXiv:2106.04631. DOI: <a href="https://doi.org/10.48550/arXiv.2106.04631">10.48550/arXiv.2106.04631</a>.
* <a id="liu2024"></a>**Liu, Nelson F. ym.** 2024: Lost in the middle: How language models use long contexts. Transactions of the Association for Computational Linguistics, 12, 157–173. DOI: <a href="https://doi.org/10.1162/tacl_a_00638">10.1162/tacl_a_00638</a>.
* <a id="liu2024b"></a>**Liu, Xiaogeng ym.** 2024: Automatic and universal prompt injection attacks against large language models. arXiv preprint arXiv:2403.04957. DOI: <a href="https://doi.org/10.48550/arXiv.2403.04957">10.48550/arXiv.2403.04957</a>.
* <a id="liu2023"></a>**Liu, Yi ym.** 2023: Prompt injection attacks and defenses in large language models: A survey. arXiv preprint arXiv:2310.12815. DOI: <a href="https://doi.org/10.48550/arXiv.2310.12815">10.48550/arXiv.2310.12815</a>.
* <a id="luckin2017"></a>**Luckin, Rosemary ym.** 2017: Towards artificial intelligence-based assessment systems. Nature Human Behaviour, 1(3), 0028. DOI: <a href="https://doi.org/10.1038/s41562-016-0028">10.1038/s41562-016-0028</a>.
* <a id="ma2024"></a>**Ma, Yubo ym.** 2024: Mitigating contextual information loss in RAG models through re-ranking. arXiv preprint arXiv:2401.06427. DOI: <a href="https://doi.org/10.48550/arXiv.2401.06427">10.48550/arXiv.2401.06427</a>.
* <a id="mchugh2012"></a>**McHugh, Mary L.** 2012: Interrater reliability: the kappa statistic. Biochemia Medica, 22(3), 276–282. DOI: <a href="https://doi.org/10.11613/BM.2012.031">10.11613/BM.2012.031</a>.
* <a id="mesenbrink2025"></a>**Mesenbrink, Hanna ym.** 2025: Orchestrated multi agents sustain accuracy under clinical-scale workloads compared to a single agent. medRxiv. DOI: 10.1101/2025.08.22.25334049.
* <a id="messick2003"></a>**Messick, Samuel J.** 2003: Substance and structure in assessment arguments. Law, Probability and Risk, 2(4), 237–258. DOI: <a href="https://doi.org/10.1093/lpr/2.4.237">10.1093/lpr/2.4.237</a>.
* <a id="messick1989"></a>**Messick, Samuel J.** 1989: Validity. Teoksessa R. L. Linn (toim.), *Educational measurement*. 3. painos. New York: Macmillan, 13–103.
* <a id="morgeson2007"></a>**Morgeson, Frederick P.; Delaney-Klinger, Kelly & Hemingway, Monica A.** 2007: The importance of job analysis to the legal defensibility of an organization's selection system. Teoksessa L. L. Koppes (toim.), *Historical perspectives in industrial and organizational psychology*. Mahwah: Lawrence Erlbaum Associates, 301–322.
* <a id="moskal2000"></a>**Moskal, Barbara M.** 2000: Scoring rubrics: What, when and how? Practical Assessment, Research, and Evaluation, 7(3). DOI: <a href="https://doi.org/10.7275/a5vq-7q66">10.7275/a5vq-7q66</a>.
* <a id="nola2014"></a>**Nola, Robert & Sankey, Howard.** 2014: *Theories of scientific method: An introduction*. Lontoo: Routledge. DOI: <a href="https://doi.org/10.4324/9781315728666">10.4324/9781315728666</a>.
* <a id="nold2022"></a>**Nold, Herbert & Michel, Lukas.** 2022: The Dunning-Kruger Effect on Organizational Agility. Academy of Management Proceedings, 2022(1). DOI: <a href="https://doi.org/10.5465/AMBPP.2022.10365abstract">10.5465/AMBPP.2022.10365abstract</a>.
* <a id="oecd2024"></a>**OECD.** 2024: *Artificial intelligence and the changing demand for skills in the labour market*. OECD Artificial Intelligence Papers, No. 14. Paris: OECD Publishing. DOI: <a href="https://doi.org/10.1787/88684e36-en">10.1787/88684e36-en</a>.
* <a id="openai2024"></a>**OpenAI.** 2024: *OpenAI o1 System Card*. OpenAI. [Verkkojulkaisu]. Saatavilla: https://openai.com/index/openai-o1-system-card/. (arXiv preprint arXiv:2412.16720).
* <a id="owasp2025a"></a>**OWASP Foundation.** 2025a: LLM01:2025 Prompt Injection. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llmrisk/llm01-prompt-injection/. [Haettu 15.11.2025].
* <a id="owasp2025b"></a>**OWASP Foundation.** 2025b: LLM02:2025 Sensitive Information Disclosure. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llm-top-10/. [Haettu 15.11.2025].
* <a id="owasp2025c"></a>**OWASP Foundation.** 2025c: LLM05:2025 Improper Output Handling. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llm-top-10/. [Haettu 15.11.2025].
* <a id="owasp2025d"></a>**OWASP Foundation.** 2025d: LLM06:2025 Excessive Agency. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llm-top-10/. [Haettu 15.11.2025].
* <a id="owasp2025e"></a>**OWASP Foundation.** 2025e: LLM08:2025 Vector and Embedding Weaknesses. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llmrisk/llm08-vector-and-embedding-weaknesses/. [Haettu 15.11.2025].
* <a id="owasp2025f"></a>**OWASP Foundation.** 2025f: OWASP Top 10 for Gen AI. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llm-top-10/. [Haettu 15.11.2025].
* <a id="owasp2025g"></a>**OWASP Foundation.** 2025g: LLM10:2025 Unbounded Consumption. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llm-top-10/. [Haettu 15.11.2025].
* <a id="owaspsa"></a>**OWASP Foundation.** s.a.: Input Validation Cheat Sheet. OWASP Cheat Sheet Series. [Verkkojulkaisu]. Saatavilla: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html. [Haettu 18.11.2025].
* <a id="parasuraman1997"></a>**Parasuraman, Raja & Riley, Victor.** 1997: Humans and automation: Use, misuse, disuse, abuse. Human Factors, 39(2), 230–253. DOI: 10.1518/001872097778543886.
* <a id="paulson1991"></a>**Paulson, F. Leon; Paulson, Pearl R. & Meyer, Carol A.** 1991: What makes a portfolio a portfolio. Educational Leadership, 48(5), 60–63.
* <a id="pearl2009"></a>**Pearl, Judea.** 2009: *Causality: Models, reasoning, and inference*. 2. painos. Cambridge: Cambridge University Press. DOI: <a href="https://doi.org/10.1017/CBO9780511803161">10.1017/CBO9780511803161</a>.
* <a id="peffers2007"></a>**Peffers, Ken; Tuunanen, Tuure; Rothenberger, Marcus A. & Chatterjee, Samir.** 2007: A Design Science Research Methodology for Information Systems Research. Journal of Management Information Systems, 24(3), 45–77. DOI: <a href="https://doi.org/10.2753/MIS0742-1222240302">10.2753/MIS0742-1222240302</a>.
* <a id="perez2022a"></a>**Perez, Ethan ym.** 2022a: Red Teaming Language Models to Reduce Harms: Methods, Scaling Behaviors, and Lessons Learned. arXiv preprint arXiv:2209.07858. DOI: <a href="https://doi.org/10.48550/arXiv.2209.07858">10.48550/arXiv.2209.07858</a>.
* <a id="perez2022b"></a>**Perez, Ethan ym.** 2022b: Discovering Language Model Behaviors with Model-Written Evaluations. arXiv preprint arXiv:2212.09251. DOI: <a href="https://doi.org/10.48550/arXiv.2212.09251">10.48550/arXiv.2212.09251</a>.
* <a id="perrow1984"></a>**Perrow, Charles.** 1984: *Normal accidents: Living with high-risk technologies*. Princeton: Princeton University Press.
* <a id="pfeifer2025"></a>**Pfeifer, Karen.** 2025: Humanity-in-the-loop: Human AI oversight is an imperative. Medium. Julkaistu 22.10.2025. [Verkkojulkaisu]. Saatavilla: https://medium.com/@karenpfeifer/humanity-in-the-loop-human-ai-oversight-is-an-imperative-50bdcc2688d8. [Haettu 14.11.2025].
* <a id="polanyi1966"></a>**Polanyi, Michael.** 1966: *The tacit dimension*. Chicago: University of Chicago Press.
* <a id="pollitt2012"></a>**Pollitt, Alastair.** 2012: The method of Adaptive Comparative Judgement. Assessment in Education: Principles, Policy & Practice, 19(3), 281–300. DOI: <a href="https://doi.org/10.1080/0969594X.2012.665354">10.1080/0969594X.2012.665354</a>
* <a id="popper1934"></a>**Popper, Karl.** 1934: *Logik der Forschung*. Vienna: Julius Springer.
* <a id="pwc2024"></a>**PwC.** 2024: *AI jobs barometer*. PricewaterhouseCoopers. [Verkkojulkaisu]. Saatavilla: https://www.pwc.com/gx/en/issues/artificial-intelligence/ai-jobs-barometer.html. [Haettu 14.11.2025].
* <a id="quine1951"></a>**Quine, Willard Van Orman.** 1951: Two dogmas of empiricism. The Philosophical Review, 60(1), 20–43. DOI: <a href="https://doi.org/10.2307/2181906">10.2307/2181906</a>.
* <a id="raisch2021"></a>**Raisch, Sebastian & Krakowski, Sebastian.** 2021: Artificial intelligence and management: The automation-augmentation paradox. Academy of Management Review, 46(1), 192–210. DOI: <a href="https://doi.org/10.5465/amr.2018.0072">10.5465/amr.2018.0072</a>.
* <a id="reinecke2014"></a>**Reinecke, Katharina & Gajos, Krzysztof Z.** 2014: Quantifying visual preferences around the world. Proceedings of the SIGCHI Conference on Human Factors in Computing Systems, 717–726. DOI: <a href="https://doi.org/10.1145/2556288.2557076">10.1145/2556288.2557076</a>.
* <a id="sadler1989"></a>**Sadler, D. Royce.** 1989: Formative assessment and the design of instructional systems. Instructional Science, 18(2), 119–144. DOI: <a href="https://doi.org/10.1007/BF00117714">10.1007/BF00117714</a>.
* <a id="sagi2018"></a>**Sagi, Omer & Rokach, Lior.** 2018: Ensemble learning: A survey. Wiley Interdisciplinary Reviews: Data Mining and Knowledge Discovery, 8(4), e1249. DOI: <a href="https://doi.org/10.1002/widm.1249">10.1002/widm.1249</a>.
* <a id="saito2023"></a>**Saito, Keisuke; Wachi, Akifumi & Akimoto, Youhei.** 2023: Verbosity bias in preference labeling by large language models. arXiv preprint arXiv:2310.10864. DOI: <a href="https://doi.org/10.48550/arXiv.2310.10864">10.48550/arXiv.2310.10864</a>.
* <a id="saltzer1975"></a>**Saltzer, Jerome H. & Schroeder, Michael D.** 1975: The protection of information in computer systems. Proceedings of the IEEE, 63(9), 1278–1308. DOI: <a href="https://doi.org/10.1109/PROC.1975.9939">10.1109/PROC.1975.9939</a>.
* <a id="sgaier2020"></a>**Sgaier, Sema K. ym.** 2020: The case for causal AI. Stanford Social Innovation Review, 18(3), 50–55. DOI: <a href="https://doi.org/10.48558/KT81-SN73">10.48558/KT81-SN73</a>.
* <a id="shafiyeva2021"></a>**Shafiyeva, Ulviyya.** 2021: Assessing Students' Minds: Developing Critical Thinking or Fitting into Procrustean Bed. European Journal of Education, 4(2), 78–91. DOI: <a href="https://doi.org/10.26417/452bxv17s">10.26417/452bxv17s</a>.
* <a id="sharma2025"></a>**Sharma, Mrinank ym.** 2025: Constitutional classifiers: Defending against universal jailbreaks across thousands of hours of red teaming. arXiv preprint arXiv:2501.18837. DOI: <a href="https://doi.org/10.48550/arXiv.2501.18837">10.48550/arXiv.2501.18837</a>.
* <a id="shavelson2010"></a>**Shavelson, Richard J.** 2010: On the measurement of competency. Empirical Research in Vocational Education and Training, 2(1), 41–63.
* <a id="shaffer2016"></a>**Shaffer, David Williamson; Collier, Wesley & Ruis, A. R.** 2016: A tutorial on Epistemic Network Analysis: Analyzing the structure of connections in cognitive, social, and interaction data. Journal of Learning Analytics, 3(3), 9–45. DOI: <a href="https://doi.org/10.18608/jla.2016.33.3">10.18608/jla.2016.33.3</a>.
* <a id="shavelson2013"></a>**Shavelson, Richard J.** 2013: On an approach to testing and modeling competence. Educational Psychologist, 48(2), 73–86. DOI: <a href="https://doi.org/10.1080/00461520.2013.779483">10.1080/00461520.2013.779483</a>.
* <a id="shen2023"></a>**Shen, Yongliang ym.** 2023: Large Language Models as Tool Makers. arXiv preprint arXiv:2305.17126. DOI: <a href="https://doi.org/10.48550/arXiv.2305.17126">10.48550/arXiv.2305.17126</a>.
* <a id="shinn2023"></a>**Shinn, Noah ym.** 2023: Reflexion: an autonomous agent with dynamic memory and self-reflection. arXiv preprint arXiv:2303.11366. DOI: <a href="https://doi.org/10.48550/arXiv.2303.11366">10.48550/arXiv.2303.11366</a>.
* <a id="shuster2021"></a>**Shuster, Kurt ym.** 2021: Retrieval augmentation reduces hallucination in conversation. arXiv preprint arXiv:2104.07567. DOI: <a href="https://doi.org/10.48550/arXiv.2104.07567">10.48550/arXiv.2104.07567</a>.
* <a id="silva2025"></a>**Silva, Bruno ym.** 2025: Development of an Adapted Version of the Motor Competence Assessment (MCA) for Older Adults. Journal of Clinical Medicine, 14(21), 7866. DOI: <a href="https://doi.org/10.3390/jcm14217866">10.3390/jcm14217866</a>.
* <a id="smith1963"></a>**Smith, Patricia Cain & Kendall, Lorne M.** 1963: Retranslation of expectations: An approach to the construction of unambiguous anchors for rating scales. Journal of Applied Psychology, 47(2), 149–155. DOI: <a href="https://doi.org/10.1037/h0047060">10.1037/h0047060</a>.
* <a id="strathern1997"></a>**Strathern, Marilyn.** 1997: 'Improving ratings': audit in the British university system. European Review, 5(3), 305–321. DOI: <a href="https://doi.org/10.1002/(SICI)1234-981X(199707)5:3<305::AID-EURO184>3.0.CO;2-4">10.1002/(SICI)1234-981X(199707)5:3<305::AID-EURO184>3.0.CO;2-4</a>.
* <a id="stumborg2022"></a>**Stumborg, Michael F. ym.** 2022: *Goodhart's law: Recognizing and mitigating the manipulation of measures in analysis*. CNA Occasional Paper. [Verkkojulkaisu]. Saatavilla: https://www.cna.org/reports/2022/09/Goodharts-Law-Recognizing-Mitigating-Manipulation-Measures-in-Analysis.pdf. [Haettu 14.11.2025].
* <a id="supianto2023"></a>**Supianto, Arief Andy ym.** 2023: A systematic review of multi-agent systems in educational assessment. Computers & Education: Artificial Intelligence, 4, 100135. DOI: <a href="https://doi.org/10.1016/j.caeai.2023.100135">10.1016/j.caeai.2023.100135</a>.
* <a id="suskie2009"></a>**Suskie, Linda.** 2009: *Assessing student learning: A common sense guide*. 2. painos. San Francisco: Jossey-Bass.
* <a id="talboy2023"></a>**Talboy, Alisha & Fuller, Elizabeth.** 2023: Large language models show humanlike cognitive biases. arXiv preprint arXiv:2308.14343. DOI: <a href="https://doi.org/10.48550/arXiv.2308.14343">10.48550/arXiv.2308.14343</a>.
* <a id="tetard2009"></a>**Tétard, Franck & Collan, Mikael.** 2009: Lazy User Theory: A Dynamic Model to Understand User Selection of Products and Services. Proceedings of the 42nd Hawaii International Conference on System Sciences, 1–10. Waikoloa, HI: IEEE Computer Society. DOI: <a href="https://doi.org/10.1109/HICSS.2009.290">10.1109/HICSS.2009.290</a>
* <a id="toulmin2003"></a>**Toulmin, Stephen E.** 2003: *The uses of argument*. Päivitetty painos. Cambridge: Cambridge University Press. DOI: <a href="https://doi.org/10.1017/CBO9780511802031">10.1017/CBO9780511802031</a>.
* <a id="towardsai2025"></a>**Towards AI.** 2025: AI Sandbox in 2025: How Enterprises and Governments Shape AI's Future. Towards AI. Julkaistu 26.9.2025. [Verkkojulkaisu]. Saatavilla: https://pub.towardsai.net/ai-sandbox-in-2025-how-enterprises-and-governments-shape-ais-future-b41f0d267c4d. [Haettu 14.11.2025].
* <a id="trivedi2024"></a>**Trivedi, Harsh ym.** 2024: Interleaving retrieval with chain-of-thought reasoning for knowledge-intensive multi-step questions. arXiv preprint arXiv:2401.10133. DOI: <a href="https://doi.org/10.48550/arXiv.2401.10133">10.48550/arXiv.2401.10133</a>.
* <a id="turpin2023"></a>**Turpin, Miles ym.** 2023: Language models don't always say what they think: Unfaithful explanations in chain-of-thought prompting. Teoksessa A. Oh, T. Hashimoto & D. Blei (toim.), *Advances in Neural Information Processing Systems 36*. La Jolla: Neural Information Processing Systems Foundation, 21016–21033.
* <a id="turpin2025"></a>**Turpin, Miles ym.** 2025: Executable counterfactuals: Improving LLMs' causal reasoning through code. arXiv preprint arXiv:2510.01539. DOI: <a href="https://doi.org/10.48550/arXiv.2510.01539">10.48550/arXiv.2510.01539</a>.
* <a id="tenk2019"></a>**Tutkimuseettinen neuvottelukunta TENK.** 2019: *Ihmiseen kohdistuvan tutkimuksen eettiset periaatteet ja ihmistieteiden eettinen ennakkoarviointi Suomessa*. Tutkimuseettisen neuvottelukunnan ohje 2019. Tutkimuseettisen neuvottelukunnan julkaisuja 3/2019. Helsinki: TENK. [Verkkojulkaisu]. Saatavilla: https://tenk.fi/sites/default/files/2021-01/Ihmistieteiden_eettisen_ennakkoarvioinnin_ohje_2020.pdf. [Haettu 14.11.2025].
* <a id="tversky1974"></a>**Tversky, Amos & Kahneman, Daniel.** 1974: Judgment under uncertainty: Heuristics and biases. Science, 185(4157), 1124–1131. DOI: <a href="https://doi.org/10.1126/science.185.4157.1124">10.1126/science.185.4157.1124</a>.
* <a id="w3c2008"></a>**W3C.** 2008: Migrating to Unicode. W3C Internationalization (I18n) Activity. [Verkkojulkaisu]. Saatavilla: https://www.w3.org/International/articles/unicode-migration/. [Haettu 14.11.2025].
* <a id="wachsmuth2017"></a>**Wachsmuth, Henning ym.** 2017: Computational argumentation quality assessment in natural language. Proceedings of the 15th Conference of the EACL, 176–187. DOI: <a href="https://doi.org/10.18653/v1/E17-1017">10.18653/v1/E17-1017</a>.
* <a id="walton2008"></a>**Walton, Douglas N.; Reed, Chris & Macagno, Fabrizio.** 2008: *Argumentation schemes*. Cambridge: Cambridge University Press. DOI: <a href="https://doi.org/10.1017/CBO9780511802034">10.1017/CBO9780511802034</a>.
* <a id="wang2023"></a>**Wang, Yuxia ym.** 2023: A survey on an authoritarian bias: The blind spot of large language models. arXiv preprint arXiv:2312.06086. DOI: <a href="https://doi.org/10.48550/arXiv.2312.06086">10.48550/arXiv.2312.06086</a>.
* <a id="wang2022"></a>**Wang, Xuezhi; Wei, Jason; Schuurmans, Dale; Le, Quoc; Chi, Ed; Narang, Sharan; Chowdhery, Aakanksha & Zhou, Denny.** 2022: Self-Consistency Improves Chain of Thought Reasoning in Language Models. arXiv preprint arXiv:2203.11171. DOI: <a href="https://doi.org/10.48550/arXiv.2203.11171">10.48550/arXiv.2203.11171</a>
* <a id="weidinger2021"></a>**Weidinger, Laura ym.** 2021: Ethical and social risks of harm from language models. arXiv preprint arXiv:2112.04359. DOI: <a href="https://doi.org/10.48550/arXiv.2112.04359">10.48550/arXiv.2112.04359</a>.
* <a id="weston2023"></a>**Weston, Jason & Sukhbaatar, Sainbayar.** 2023: System 2 attention (is something you might need too). arXiv preprint arXiv:2311.11829. DOI: <a href="https://doi.org/10.48550/arXiv.2311.11829">10.48550/arXiv.2311.11829</a>.
* <a id="wiggins1998"></a>**Wiggins, Grant.** 1998: *Educative assessment: Designing assessments to inform and improve student performance*. San Francisco: Jossey-Bass.
* <a id="wisse2023"></a>**Wisse, Gerben & Greve, Rutger.** 2023: AI in educational assessment: A systematic review of formative and summative applications. Computers & Education: Artificial Intelligence, 5, 100174. DOI: <a href="https://doi.org/10.1016/j.caeai.2023.100174">10.1016/j.caeai.2023.100174</a>.
* <a id="wolf2007"></a>**Wolf, Kenneth & Stevens, Ellen.** 2007: The role of rubrics in advancing and assessing student learning. The Journal of Effective Teaching, 7(1), 3–14.
* <a id="wolf2023"></a>**Wolf, Yotam ym.** 2023: Fundamental Limitations of Alignment in Large Language Models. arXiv preprint arXiv:2304.11082. DOI: <a href="https://doi.org/10.48550/arXiv.2304.11082">10.48550/arXiv.2304.11082</a>.
* <a id="wolters2024"></a>**Wolters Kluwer.** 2024: *2024 Future ready lawyer survey report*. [Verkkojulkaisu]. Saatavilla: https://www.wolterskluwer.com/en/know/future-ready-lawyer-2024. [Haettu 14.11.2025].
* <a id="wooldridge2009"></a>**Wooldridge, Michael.** 2009: *An introduction to multiagent systems*. 2. painos. Chichester: John Wiley & Sons.
* <a id="wef2023"></a>**World Economic Forum.** 2023: *Future of Jobs Report 2023*. [Verkkojulkaisu]. Saatavilla: https://www.weforum.org/publications/the-future-of-jobs-report-2023/. [Haettu 18.11.2025].
* <a id="wu2024"></a>**Wu, Junjie ym.** 2024: Large Language Models are Challenged by an Abundance of Over-complicated Instructions. arXiv preprint arXiv:2409.07844. DOI: <a href="https://doi.org/10.48550/arXiv.2409.07844">10.48550/arXiv.2409.07844</a>.
* <a id="wynn2025"></a>**Wynn, Alexander; Satija, Harsh & Hadfield, Gillian.** 2025: Talk isn't always cheap: Understanding failure modes in multi-agent debate. Proceedings of the ICML 2025 Workshop on Multi-Agent Systems. arXiv preprint arXiv:2509.05396. DOI: <a href="https://doi.org/10.48550/arXiv.2509.05396">10.48550/arXiv.2509.05396</a>.
* <a id="ye2025"></a>**Ye, Rui ym.** 2025: X-MAS: A comprehensive testbed for evaluating heterogeneous LLM-driven multi-agent systems. arXiv preprint arXiv:2505.16997. DOI: <a href="https://doi.org/10.48550/arXiv.2505.16997">10.48550/arXiv.2505.16997</a>.
* <a id="yeager2023"></a>**Yeager.ai.** 2023: AI Agent Kryptonite - Prompt Saturation and Context Bleeding. Medium. Julkaistu 16.10.2023. [Verkkojulkaisu]. Saatavilla: https://medium.com/yeagerai/ai-agent-kryptonite-prompt-saturation-and-context-bleeding-4db7c4329e4e. [Haettu 16.11.2025].
* <a id="yi2025"></a>**Yi, Zhaoyang ym.** 2025: Benchmarking and defending against indirect prompt injection attacks on large language models. arXiv preprint arXiv:2312.14197. DOI: <a href="https://doi.org/10.48550/arXiv.2312.14197">10.48550/arXiv.2312.14197</a>.
* <a id="zhang2024"></a>**Zhang, Yunhua ym.** 2024: Soar: The Future of AI-Driven Architectures through Directed Acyclic Graph Reasoning. arXiv preprint arXiv:2404.05678. DOI: <a href="https://doi.org/10.48550/arXiv.2404.05678">10.48550/arXiv.2404.05678</a>.
* <a id="zilliz2024"></a>**Zilliz.** 2024: Ensuring Secure and Permission-Aware RAG Deployments. Zilliz Blog. [Verkkojulkaisu]. Saatavilla: https://zilliz.com/blog/ensure-secure-and-permission-aware-rag-deployments. [Haettu 14.11.2025].
* <a id="zou2024"></a>**Zou, Wei; Geng, Runpeng; Wang, Binghui & Jia, Jinyuan.** 2024: PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models. arXiv preprint arXiv:2402.07867. DOI: <a href="https://doi.org/10.48550/arXiv.2402.07867">10.48550/arXiv.2402.07867</a>.