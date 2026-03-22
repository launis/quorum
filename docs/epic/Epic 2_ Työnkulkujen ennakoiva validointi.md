# **Epic 2: Työnkulkujen Ennakoiva Validointi (The Pre-Flight Check)**

**Epic ID:** QUORUM-EPIC-V2-002

**Tila:** Valmis kehitettäväksi (Ready for Dev)

**Teema:** Shift-Left, FinOps, Developer Experience (Admin Studio), Reliability

**Kohdemoduulit:** backend\_v2/services/orchestrator/dag\_compiler.py (UUSI), backend\_v2/api/routers/studio/workflows.py

**Riippuvuudet:** Voidaan toteuttaa rinnakkain Epic 1:n kanssa.

**Laajuusarvio:** L (2–3 viikon algoritminen ja rajapintojen kehitys)

## **1\. Tausta ja Ongelmakuvaus**

Quorum V2:n työnkulut (Workflows) perustuvat askeleiden muodostamaan suunnattuun syklittömään verkkoon (DAG \- Directed Acyclic Graph). Tällä hetkellä askeleiden (Steps) välisten riippuvuuksien ja tietorakenteiden reitityksen ($inputs.\*, $steps.\*) oikeellisuus testataan vasta **ajonaikaisesti (Runtime)** DAGExecutorin toimesta.

**Nykyisen arkkitehtuurin kriittiset ongelmat:**

1. **Myöhäinen kaatuminen (Late Failure):** Jos Admin Studiossa tehdään konfiguraatiovirhe – esimerkiksi Askel 3 yrittää lukea muuttujaa $steps.analyst.result, mutta Askel 1 onkin nimetty analyysi – järjestelmä kaatuu vasta tuotannossa. Kallis LLM-API on saattanut jo tuhlata kymmeniä sekunteja ja rahaa aiempien askeleiden suorittamiseen ennen kaatumista (merkittävä FinOps-riski).  
2. **Ikuiset silmukat (Infinite Loops):** Koska verkon syklisyyttä ei tarkisteta tallennushetkellä, käyttäjä voi vahingossa luoda tilanteen, jossa Askel A odottaa Askel B:tä, ja B odottaa A:ta. Tämä johtaa suoritusmoottorin jäätymiseen (Deadlock) ja työntekijäprosessin (Worker) tukehtumiseen.  
3. **Huono virhepalaute (UX):** Kun ajonaikainen virhe tapahtuu, käyttäjä saa kryptisen teknisen poikkeuksen (esim. KeyError). Emme pysty antamaan työnkulun suunnittelijalle Admin Studiossa välitöntä palautetta siitä, mikä reitityksessä on rikki.

## **2\. Tavoitteet ja Liiketoiminta-arvo**

Tämän Epicin tavoitteena on siirtää työnkulkujen eheystarkistus ajonajalta **suunnittelupöydälle (Shift-Left)** rakentamalla "Pre-Flight Check" \-mekanismi.

* **FinOps ja Kustannussäästöt:** Yksikään virheellinen työnkulku ei pääse kuluttamaan LLM-API-krediittejä, koska suoritusta ei edes aloiteta, jos topologia on rikki.  
* **Tietokannan eheys (Zero Trash Policy):** Tietokantaan tallennettu uusi työnkulku on matemaattisesti taattu olevan suoritettavissa (Deadlock-vapaa ja muuttujaviittaukset ehjät).  
* **Erinomainen Developer Experience (UX):** Jos Admin yrittää tallentaa API:n kautta viallisen työnkulun, hän saa välittömästi HTTP 422 \-virheen, joka kertoo ihmisluettavasti: *"Askel 3 yrittää käyttää syötettä '$inputs.user\_id', jota ei ole määritelty työnkulun 'Expected Inputs' \-listassa."*

## **3\. Arkkitehtuurilinjaukset (Technical Guidelines)**

Toteutuksessa on noudatettava seuraavia tiukkoja arkkitehtuurisääntöjä:

1. **Erillinen Kääntäjäpalvelu (DAG Compiler Service):**  
   * **Kriittinen suorituskykyvaatimus:** Graafianalyysiä (syklien etsintä, muuttujapolkujen resoluutio) **EI SAA** toteuttaa Pydanticin @model\_validator \-metodeissa. Tämä tuhoaisi API:n Read-operaatioiden (GET /workflows) suorituskyvyn, koska raskas validointi ajettaisiin jokaisen listahaun yhteydessä.  
   * Siksi semanttinen validointi eriytetään uuteen DAGCompilerService \-luokkaan. Pydantic hoitaa vain perussyntaksin.  
2. **Validointi vain Write-operaatioissa:** DAGCompilerService.validate(workflow) ajetaan ainoastaan silloin, kun työnkulku luodaan tai sitä päivitetään (POST/PUT \-rajapinnat Admin Studiossa) tai kun järjestelmä alustetaan (run\_seed.py).  
3. **Graceful Degradation (Taaksepäin yhteensopivuus):** Tietokannassa on jo todennäköisesti historiallisesti rikkinäisiä työnkulkuja. Ne eivät saa kaataa lukuoperaatioita. Ne ladataan muistiin normaalisti, mutta jos niitä yritetään tallentaa uudelleen, kääntäjä pakottaa korjaamaan ne. Ajo (Execution) kuitenkin estetään fail-fast \-periaatteella.

## **Koodiesimerkki (Tavoitearkkitehtuuri)**

**1\. Uusi Kääntäjäpalvelu (dag\_compiler.py):**

Python

from backend\_v2.models.workflow import WorkflowV2  
from backend\_v2.exceptions import WorkflowCompilationError

class DAGCompilerService:  
    @staticmethod  
    def validate\_workflow(workflow: WorkflowV2) \-\> None:  
        """  
        Suorittaa "Pre-Flight Checkin". Nostaa WorkflowCompilationErrorin, jos  
        verkossa on syklejä tai rikkinäisiä muuttujaviittauksia.  
        """  
        \# 1\. Tarkista syklit (esim. Kahnin algoritmi tai DFS)  
        DAGCompilerService.\_ensure\_acyclic(workflow.steps)  
          
        \# 2\. Tarkista muuttujareititykset  
        \# Rakennetaan joukko kaikista avaimista, jotka ovat tiedossa suorituksen alkaessa  
        available\_keys \= set(workflow.expected\_inputs)  
          
        \# Oletetaan, että \_get\_topological\_order palauttaa askeleet suoritusjärjestyksessä  
        ordered\_steps \= DAGCompilerService.\_get\_topological\_order(workflow.steps)  
          
        for step in ordered\_steps:  
            \# Analysoi askeleen config-viittaukset (esim. "$inputs.doc\_id" tai "$steps.analyysi")  
            for ref in step.extract\_variable\_references():  
                if ref.root\_key not in available\_keys:  
                    raise WorkflowCompilationError(  
                        step\_id=step.id,  
                        message=f"Askel '{step.id}' viittaa tuntemattomaan muuttujaan '{ref.root\_key}'. "  
                                f"Tässä vaiheessa saatavilla olevat muuttujat: {available\_keys}"  
                    )  
            \# Askeleen onnistuneen suorituksen jälkeen sen oma tulos on käytettävissä myöhemmille  
            available\_keys.add(f"$steps.{step.id}")

**2\. Käyttö API-reitittimessä (workflows.py):**

Python

@router.post("/", response\_model=WorkflowV2)  
async def create\_workflow(workflow\_in: WorkflowCreateDTO, repo: IWorkflowRepo \= Depends()):  
    \# 1\. Käännä ja semanttisesti validoi työnkulku ENNEN tallennusta  
    try:  
        DAGCompilerService.validate\_workflow(workflow\_in)  
    except WorkflowCompilationError as e:  
        \# Palautetaan ihmisluettava 422-virhe Admin Studion UI:lle  
        raise HTTPException(  
            status\_code=422,   
            detail={"step\_id": e.step\_id, "msg": str(e), "type": "CompilationError"}  
        )   
          
    \# 2\. Tallenna turvallisesti  
    return await repo.save(workflow\_in)

## **4\. Työpaketit (Task Breakdown)**

| Tiketti | Kuvaus | Työmäärä |
| :---- | :---- | :---- |
| **QUORUM-201** | **DAGCompilerService \- Syklien tunnistus:** Luo uusi palvelu backend\_v2/services/orchestrator/dag\_compiler.py. Toteuta algoritmi (esim. Syvyyssuuntainen haku DFS tai Kahn's algorithm), joka tarkistaa, ettei workflow.steps muodosta ikuisia silmukoita. Rakenna selkeä WorkflowCompilationError-poikkeusluokka. | 6 h |
| **QUORUM-202** | **DAGCompilerService \- Reititysten (Reference) resoluutio:** Toteuta logiikka, joka simuloi työnkulun suoritusjärjestyksen ja tarkistaa, että jokainen muuttujaviittaus ($inputs.\*, $steps.\*) osoittaa dataan, joka on tuotettu aiemmassa askeleessa tai globaaleissa syötteissä. | 8 h |
| **QUORUM-203** | **API-integraatio (Admin Studio):** Päivitä backend\_v2/api/routers/studio/workflows.py (POST ja PUT \-reitit). Lisää kääntäjäpalvelun kutsu ennen tallennusta ja ota kiinni käännösvirheet. Palauta selkokielinen HTTP 422 \-virhe (sisältäen tarkan step\_id:n) takaisin käyttöliittymälle. | 4 h |
| **QUORUM-204** | **Seed-datan migraatio & Siivous:** Päivitä backend\_v2/seed/run\_seed.py ajamaan kääntäjäpalvelu jokaiselle järjestelmän alkuperäiselle työnkululle. **Korjaa manuaalisesti** seed\_data.json:ssa olevat työnkulut, jotka eivät mene uudesta tiukasta kääntäjästä läpi. | 4 h |
| **QUORUM-205** | **Suoritusmoottorin suojamuuri:** Lisää työnkulun käynnistys-endpointtiin tai DAGExecutorin alkuun nopea tarkistus: aja työnkulku kääntäjän läpi (tai tarkista kantaan tallennettu is\_compiled-lippu). Jos ei mene läpi, hylkää ajo välittömästi ilman yhtäkään LLM-kutsua. | 2 h |
| **QUORUM-206** | **Testiautomaatio (Compiler Tests):** Luo kattava testisarja (tests/backend\_v2/services/test\_dag\_compiler.py). Testaa skenaariot: 1\) Validi lineaarinen DAG, 2\) Validi rinnakkainen DAG, 3\) Virhe: Syklinen riippuvuus, 4\) Virhe: Viittaus olemattomaan $inputs \-avaimeen, 5\) Virhe: Viittaus $steps \-avaimeen, jota ei ole vielä topologisesti suoritettu. | 6 h |

## **5\. Hyväksymiskriteerit (Definition of Done)**

* \[ \] DAGCompilerService on toteutettu erillisenä palveluna, **eikä** sitä ole kytketty Pydanticin automaattiseen validointiin (Read-operaatioiden nopeus on turvattu).  
* \[ \] Syklien (ikuiset silmukat) tallentaminen työnkulkuun estetään API-tasolla HTTP 422 \-virheellä.  
* \[ \] Rikkonaisten muuttujaviittausten (Dangling references, Forward references) tallentaminen estetään API-tasolla HTTP 422 \-virheellä.  
* \[ \] API-virheilmoitukset ovat jäsenneltyjä ja ihmisluettavia (kertovat tarkan askeleen ID:n ja puuttuvan avaimen), jotta Admin Studio voi korostaa virheen UI:ssa.  
* \[ \] Kaikki olemassa oleva seed-data menee tiukan kääntäjän läpi virheittä (data on siivottu/korjattu).  
* \[ \] Olemassa olevien, tietokannassa mahdollisesti olevien rikkinäisten työnkulkujen lukeminen (GET) ei kaada APIa (Graceful Degradation).  
* \[ \] Yksikkötestit kattavat algoritmin reunatapaukset.

## **6\. Riskit ja Mitigaatio**

| Riski | Vaikutus | Hallintakeino (Mitigation) |
| :---- | :---- | :---- |
| **Dynaamisten avainten kääntäminen:** Työnkulku saattaa sallia dynaamisten avainten käytön (esim. avain synty LLM:n rakenteettomasta vastauksesta), jolloin staattinen kääntäjä ei pysty täysin todentamaan niiden olemassaoloa ennakkoon. | Keskiverto | **Ratkaisu (QUORUM-202):** Kääntäjä rakennetaan "pragmaattiseksi". Jos se ei pysty staattisesti todistamaan viittausta täysin vääräksi (esim. juuri $steps.analyysi on olemassa, mutta emme ole varmoja onko siellä avainta .dynaaminen\_tulos), se sallii tallennuksen. Estetään vain matemaattisesti varmat virheet (esim. koko juuriaskelta ei ole olemassa). Syvävalidointi jätetään Epic 3:n (Runtime Schema) vastuulle. |
| **API-rajapinnan suorituskyky Write-tilanteessa:** Isojen graafien kääntäminen hidastaa asynkronista API-reititintä. | Matala | Työnkulut ovat tyypillisesti pieniä (alle 50 askelta). Topologisen lajittelun aikakompleksisuus on $O(V+E)$, mikä on Pythonilla sadasosasekuntien luokkaa. Koska Write-operaatiot (Tallennus) ovat harvinaisia, laskentakuorma on täysin mitätön suhteessa saavutettuun turvaan. |
| **Legacy-datan korruptio:** Tuotantotietokannassa on jo työnkulkuja, jotka eivät läpäise uutta tiukkaa kääntäjää. | Kriittinen | **Ratkaisu:** Validointi tapahtuu vain POST/PUT-vaiheessa. Vanhat työnkulut latautuvat Admin Studioon normaalisti. Virhe laukeaa vasta, kun käyttäjä yrittää *suorittaa* niitä tai *tallentaa* niitä muutosten jälkeen, jolloin API pakottaa hänet korjaamaan graafin. |

