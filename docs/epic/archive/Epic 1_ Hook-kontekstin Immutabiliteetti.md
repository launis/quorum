# **Epic 1: Hook-kontekstin Immutabiliteetti ja Vahva Tyypitys (Strict Pydantic)**

**Epic ID:** QUORUM-EPIC-V2-001

**Tila:** Valmis kehitettäväksi (Ready for Dev)

**Teema:** Core Architecture, Tech Debt, Fail-Fast, Reliability

**Kohdemoduulit:** backend\_v2/core/hook\_registry.py, backend\_v2/services/orchestrator/dag\_executor.py, backend\_v2/utils/dict\_utils.py ja backend\_v2/hooks/\*.py

**Laajuusarvio:** M (1–2 viikon keskitetty refaktorointi)

## **1\. Tausta ja Ongelmakuvaus**

Quorum V2:n työnkulkujen (DAG) suoritusmoottori reitittää dataa lukuisten asiantuntijamoduulien eli koukkujen (Hooks, esim. scoring.py, integrity.py) läpi. Tällä hetkellä näille koukuille välitettävä ajonaikainen tila (HookExecutionContext) on toteutettu standardilla Pythonin @dataclass-rakenteella, joka on todettu tuotannossa merkittäväksi arkkitehtuuriseksi heikkoudeksi.

**Nykyisen arkkitehtuurin kriittiset ongelmat:**

1. **Sivuvaikutukset ja Kilpatilanteet (Mutability):** Nykyinen tila on ajonaikaisesti muokattavissa. Yksittäinen buginen koukku voi vahingossa ylikirjoittaa jaettua dataa. Asynkronisessa suorituksessa tämä johtaa arvaamattomiin kilpatilanteisiin (race conditions).  
2. **SRP-rikkomus ja DI:n puute:** Kontekstiin on injektoitu suoraan tietokantarepositorioita ja muita I/O-objekteja (repository: Any). Kognitiivinen data ja infrastruktuuririippuvuudet on sekoitettu, mikä estää tiukan tyyppivalidoinnin ja puhtaan arkkitehtuurin.  
3. **Shallow Merge \-tuhot:** Datan päivittäminen ajon aikana natiiveilla Pythonin dict-operaatioilla (kuten dict.update()) on altista sisäkkäisten tietorakenteiden ylikirjoittumiselle (esim. numeerinen pisteytys ylikirjoittaa ja tuhoaa aiemmin luodun sanallisen perustelun samassa JSON-puussa).

## **2\. Tavoitteet ja Liiketoiminta-arvo**

Tämän Epicin tavoitteena on rakentaa **Ultimate Fail-Fast** \-perusta ja matemaattinen varmuus koukkujen suoritukselle:

* **100 % Muuttumattomuus (Zero Side-Effects):** Koukuille annettava data jäädytetään (frozen=True). Koukut palauttavat vain muutosobjektin (State Delta), joka liitetään tilaan hallitusti.  
* **Datan ja infrastruktuurin eristäminen (DI Container):** Riippuvuudet välitetään omassa staattisesti tyypitetyssä säiliössään (HookDependencies), täysin erillään Pydantic-datamallista.  
* **Turvallinen tilan päivitys (Deep Merge):** Koukkujen palauttama tila yhdistetään pääsuoritukseen kustomoidulla rekursiivisella syväyhdistämisellä, taaten ettei olemassa olevaa dataa ylikirjoiteta vahingossa.  
* **FinOps:** Pydanticin tiukka validointi varmistaa, että virheellinen data kaataa prosessin välittömästi *ennen* ensimmäistäkään API-kustannuksia kerryttävää LLM-kutsua.

## **3\. Arkkitehtuurilinjaukset (Technical Guidelines)**

Toteutuksessa on noudatettava seuraavia ehdottomia sääntöjä:

1. **Ei "Escape Hatcheja":** Pydanticin arbitrary\_types\_allowed=True \-asetuksen käyttö on **ehdottomasti kielletty** HookState-mallin yhteydessä.  
2. **Riippuvuuksien Injektio (HookDependencies Container):** Koska FastAPI:n Depends ei toimi työnkulkumoottorin sisäisessä luupissa, kaikki I/O-protokollat kootaan yhteen puhtaaseen @dataclass(frozen=True) \-luokkaan. DAGExecutor saa tämän kontin reitittimeltä/palvelulta ja välittää sen eteenpäin hookeille.  
3. **Tilan syväyhdistäminen (Deep Merge):** Pythonin dict.update() (Shallow Merge) on kielletty tiladeltan yhdistämisessä. Deltat on yhdistettävä rekursiivisella deep\_merge\_dicts \-apufunktiolla.

## **Koodiesimerkki (Tavoitetila)**

Python

from pydantic import BaseModel, ConfigDict, UUID4  
from dataclasses import dataclass  
from typing import Protocol, Any

\# 1\. Riippuvuuksien rajapinnat (Dependency Inversion)  
class IExecutionRepository(Protocol):  
    async def save\_metric(self, execution\_id: UUID4, metric: dict\[str, Any\]) \-\> None: ...

class ISearchClient(Protocol):  
    async def search(self, query: str) \-\> list\[dict\[str, Any\]\]: ...

\# 2\. Dependency Container (Injektoidaan DAGExecutorille, välitetään Hookeille)  
@dataclass(frozen=True)  
class HookDependencies:  
    repository: IExecutionRepository  
    search\_client: ISearchClient | None \= None

\# 3\. Puhdas ja muuttumaton (frozen) datamalli  
class HookState(BaseModel):  
    model\_config \= ConfigDict(frozen=True, extra='forbid', strict=True)  
    execution\_id: UUID4  
    inputs: dict\[str, Any\]

\# 4\. Hookin eksplisiittinen paluuarvo (State Delta)  
class HookResult(BaseModel):  
    success: bool  
    state\_delta: dict\[str, Any\] | None \= None

\# 5\. Hookin puhdas signatuuri  
async def run\_scoring(state: HookState, deps: HookDependencies) \-\> HookResult:  
    \# state.inputs\['score'\] \= 100 \<-- TÄMÄ KAATUU HETI (Frozen=True)\! ✅ Fail-Fast  
      
    calculated\_score \= 100.0  
    await deps.repository.save\_metric(state.execution\_id, {"score": calculated\_score})  
      
    \# Palautetaan State Delta.  
    \# Vaikka inputs sisältäisi ennestään {"matrix\_A": {"justification": "hyvä"}},  
    \# Deep Merge varmistaa, että vain "score" päivittyy, eikä "justification" katoa.  
    return HookResult(success=True, state\_delta={"matrix\_A": {"score": calculated\_score}})

## **4\. Työpaketit (Task Breakdown)**

| Tiketti | Kuvaus | Työmäärä |
| :---- | :---- | :---- |
| **TASK-1** | **Ydinmallien ja DI-Kontin luonti:** Määrittele typing.Protocol-luokat järjestelmän I/O-riippuvuuksille. Luo @dataclass(frozen=True) HookDependencies \-kontti. Luo uudet puhtaat HookState ja HookResult Pydantic-mallit. | 3 h |
| **TASK-2** | **Deep Merge \-työkalu:** Toteuta backend\_v2/utils/dict\_utils.py \-tiedostoon rekursiivinen deep\_merge\_dicts(base: dict, update: dict) \-\> dict funktio. **Kirjoita sille kattavat yksikkötestit**, jotka todistavat, ettei se tuhoa sisäkkäisten sanakirjojen olemassa olevia rinnakkaisia avaimia. | 3 h |
| **TASK-3** | **DAG Executorin päivitys:** Refaktoroi työnkulkumoottori (backend\_v2/services/orchestrator/dag\_executor.py). Injektoi HookDependencies executorin rakentajassa (constructor). Käytä deep\_merge\_dicts \-työkalua HookResult.state\_delta:n yhdistämiseen takaisin pääsuorituksen tilaan. Käsittele Pydanticin ValidationErrorit hallitusti. | 5 h |
| **TASK-4** | **Koukkujen refaktorointi (Osa 1: Core):** Päivitä validointi-, tietoturva- ja eheydenhallintakoukkujen signatuurit ottamaan vastaan HookDependencies ja HookState. Eristä datan mutaatiot HookResult-paluuarvoihin. | 5 h |
| **TASK-5** | **Koukkujen refaktorointi (Osa 2: AI & Data):** Päivitä datakäsittely- ja tekoälykoukut (scoring.py, metrics.py, linguistics.py, llm.py). Poista vanhat puolustavat tyyppitarkistukset, joita Pydantic hoitaa nyt automaattisesti. | 5 h |
| **TASK-6** | **Testien refaktorointi ja Varmentaminen:** Päivitä tests/backend\_v2/hooks/ hakemiston testit luomaan Mock-objektit uuden HookDependencies \-kontin sisälle. **Kirjoita testi, joka varmistaa, että suora mutaatioyritys kaatuu Pydanticin ValidationError / FrozenInstanceError \-poikkeukseen.** | 6 h |

## **5\. Hyväksymiskriteerit (Definition of Done)**

* \[ \] Vanhasta @dataclass HookExecutionContext:sta on luovuttu koodikannassa kokonaan.  
* \[ \] Uusi HookState on validi Pydantic BaseModel ehtoineen (frozen=True, extra='forbid', strict=True).  
* \[ \] Pydanticin konfiguraatiota arbitrary\_types\_allowed=True **ei ole** käytetty HookState-mallissa.  
* \[ \] Riippuvuudet on eriytetty datasta ja injektoidaan puhtaasti HookDependencies \-kontin (DI) kautta.  
* \[ \] Ajonaikainen tilan päivitys tehdään **yksinomaan rekursiivisella deep merge \-funktiolla**, dict.update() \-metodia ei ole käytetty tiladeltan yhdistämiseen.  
* \[ \] Kaikki koukut palauttavat HookResult \-objektin suoran mutatoinnin sijaan.  
* \[ \] Yksikkötestit todistavat "Fail-Fast" \-käyttäytymisen ja Deep Mergen turvallisuuden.  
* \[ \] Staattinen tyyppianalyysi (mypy \--strict) menee läpi ilman virheitä muokattujen tiedostojen osalta.

## **6\. Riskit ja Mitigaatio**

| Riski | Vaikutus | Hallintakeino (Mitigation) |
| :---- | :---- | :---- |
| **State Deltan yhdistämisen tuhoavuus:** Pythonin oletusmetodit (Shallow Merge) ylikirjoittavat sisäkkäiset sanakirjat kokonaan, tuhoten LLM:n aiemmin tuottamaa dataa. | **Kriittinen** | Ratkaistu **TASK-2**:ssa. Pakotetaan kustomoitu deep\_merge\_dicts \-apufunktio, joka käy dictin läpi rekursiivisesti. Varustetaan se aggressiivisilla yksikkötesteillä skenaarioita varten, joissa päivitetään vain osaa sisäkkäisestä oliosta. |
| **Suuri "Blast Radius":** Signatuurien muuttaminen koskettaa useita tiedostoja ja rikkoo tilapäisesti suoritusmoottorin ja testit. | Korkea | Työ tehdään eristetyssä feature-haarassa (feature/epic-hook-immutability). Tiimi sopii Code Freezestä hooks/-kansioon ja dag\_executor.py:hyn refaktoroinnin ajaksi. |
| **Testien hajoaminen:** Tiukempi Pydantic-validointi (strict=True, extra='forbid') paljastaa piileviä bugeja vanhoissa testeissä (esim. puuttuvia kenttiä mock-datassa). | Keskiverto | Varataan **TASK-6**\-tikettiin riittävästi aikaa testi-fixtureiden siivoamiseen. mypy \--strict auttaa löytämään nämä nopeasti. Tämä on teknisen velan maksua, joka nostaa koodin laatua. |

