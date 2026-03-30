# **Arkkitehtuurin Auditointiraportti: Cognitive Quorum V2**

**Tavoitetila:** Vuoden 2026 Enterprise SaaS, Explainable AI (xAI) ja AI Act \-yhteensopivuus.

## **1\. Johdanto ja Yleisarvio**

Kokonaisarkkitehtuuri edustaa pilvinatiivin tekoälykehityksen terävintä kärkeä. SDUI-mallin (Server-Driven UI), modulaarisen Flutter-frontendin ja FastAPI:n asynkronisen DAG-moottorin (Directed Acyclic Graph) yhdistelmä on erinomainen valinta monimutkaisten MCP-työkalulooppien ja LLM-agenttien orkestrointiin. Separation of Concerns (huolien erottelu) on toteutettu vahvasti läpi pinon.

Vaikka perusta on poikkeuksellisen kypsä, järjestelmän siirtyminen aitoon skaalautuvaan Enterprise-tuotantoon vaatii integraatiosaumojen defensiivisyyden kiristämistä, hajautetun tilan ja resurssien tarkempaa hallintaa (FinOps) sekä absoluuttisen "Fail-Fast" \-paradigman pakottamista kaikkialle.

## ---

**2\. Järjestelmätason Integriteetti ja xAI-Valmius**

## **2.1 Tietomallien eheys ja Zero-Trust**

Arkkitehtuuri nojaa vahvasti Zero-Trust \-periaatteeseen datan validoinnissa.

* **Strict Data Contracts:** Kaikki backendin V2-mallit perivät V2CoreBase-luokan, jossa on määritelty model\_config \= ConfigDict(strict=True, extra="forbid"). Tämä estää hiljaisen tyyppimuunnoksen ja tuntemattomien/haitallisten kenttien injektoinnin objekteihin.  
* **Defensiivinen Liiketoimintalogiikka:** Pydanticin model\_validator-metodit pakottavat tiukat säännöt (esim. PromptBlock estää allow\_decimals \-asetuksen ei-numeerisilla tyypeillä, ja Workflow tarkistaa mallitasolla, ettei verkossa ole orpoja viittauksia tai syklejä).  
* **Frontendin Tyyppiturvallisuus:** Dart-koodin StrictEnumConverter ja StrictOpaqueIdConverter heittävät armotta AppException.validation \-virheen välittömästi, jos backendin data ei vastaa odotuksia. Tämä pakottaa rajapintasopimukset pitäviksi.

## **2.2 Auditoitavuus ja Event Sourcing (AI Act 2026\)**

Tekoälyn toiminnan selitettävyys (Explainable AI) on ratkaistu oppikirjamaisesti.

* **Jäljitettävyys:** dag\_executor.py ja FrozenContext rakentavat Event Sourcing \-mallia. Tila (ExecutionRecord) päivittyy "Append-Only" \-periaatteella lisäämällä tapahtumia execution\_trace taulukkoon.  
* **Jäädytetty Konteksti:** FrozenContext tallentaa suorituksen aikaiset kehotteet (compiled\_prompts), taustateoriat (injected\_theory) ja ulkoiset työkalukutsut (MCPAuditTrace). Tämän ansiosta jokainen tekoälyn päätös voidaan toistaa ja todistaa täsmälleen sellaisena kuin se tapahtui, mikä on EU:n AI Actin kriittinen vaatimus.

## ---

**3\. Backend-arkkitehtuuri (FastAPI & Python)**

## **3.1 Clean Architecture ja Riippuvuuksien Injektio**

* **Anemic Routers:** FastAPI-reitittimet (esim. executions.py) ovat täysin "aneemisia" portinvartijoita. Ne eivät sisällä tietokantakyselyitä tai liiketoimintalogiikkaa, vaan delegoivat työn puhtaasti Service-kerrokselle (execution\_service). Tämä on puhdas Port & Adapters \-toteutus.  
* **Moderni DI (Dependency Injection):** dependencies.py hyödyntää Python 3.12+ Annotated-tyypitystä (esim. ExecutionServiceDep \= Annotated\[ExecutionService, Depends(...)\]). Tämä takaa staattisen tyyppiturvallisuuden ja tekee koodista erittäin helposti testattavaa.

## **3.2 Rinnakkaisuus ja Resurssienhallinta (FinOps)**

* **Structured Concurrency:** Asynkroninen DAG-moottori on rakennettu modernin asyncio.TaskGroup() \-konseptin varaan. Tämä on valtava etu, sillä jos yksi rinnakkainen AI-agentin solmu kaatuu, TaskGroup takaa sisarsolmujen peruutuksen, eliminoiden kalliit "zombisäikeet".  
* **Denial of Wallet \-riski:** Tällä hetkellä dag\_executor.py käyttää lokaalia semaforia (asyncio.Semaphore(SystemConcurrency.MAX\_CONCURRENT\_LLM\_STEPS.value)). Monen instanssin klusterissa (esim. Kubernetes) tämä ei riitä suojaamaan LLM-rajapintoja HTTP 429 \-virheiltä tai kustannusten räjähdykseltä. Rakenne vaatii globaalin Token Bucket \-rajoittimen.

## **3.3 Virheenhallinnan Protokolla**

* **RFC 7807 Parity:** Backend muuttaa kaikki poikkeukset, mukaan lukien Pydanticin validointivirheet (RequestValidationError), yhtenäiseen application/problem+json \-formaattiin.  
* **Vaaralliset Catch-All- ja Nielulohkot:** Järjestelmässä on teknistä velkaa hiljaisten virheiden suhteen. v2\_core.py:n ExecutionRecord.parse\_db\_fields \-metodissa on try... except ValueError: pass \-lohko, joka nielee datan korruptoitumisen. Lisäksi joidenkin taustatehtävien käynnistys asynkronisessa virheenkäsittelyssä (loop.create\_task(self.committer.commit\_trace(...))) ilman taattua *grace periodia* on riski datan menetykselle palvelimen sammuessa.

## ---

**4\. Frontend-arkkitehtuuri (Flutter Desktop-First)**

## **4.1 Tyyppiturvallinen Reititys ja Tilanhallinta**

Koodikanta on Flutter-arkkitehtuurina huippuluokkaa. Koodigeneraation (.g.dart, .freezed.dart) laaja käyttö osoittaa kypsyyttä.

* **Reititys:** router.dart hyödyntää go\_router\_builderia ja vahvasti tyypitettyjä reittejä (@TypedGoRoute, GoRouteData). Tämä on työpöytäsovelluksille elintärkeää, poistaen "magic string" \-virheet syvälinkityksessä ja taaten selaimen/ikkunan back-historian toiminnan.  
* **Tila:** Kontrollerit (BlueprintEditorController) hyödyntävät uutta Riverpod Generatoria (@riverpod) ja Freezed-malleja. Tila on täysin muuttumaton (immutable) ja päivittyy turvallisilla .copyWith()-operaatioilla.

## **4.2 Säikeistys ja UI:n Suorituskyky (Isolates & Jank)**

Raskaana "Pro-Toolina" sovellus käsittelee massiivisia JSON-rakenteita.

* **BackgroundTransformer:** Dio-verkkokirjastoon (api\_client.dart) on rakennettu BackgroundTransformer, joka hyödyntää modernia Isolate.run() \-metodia. Tämä siirtää raskaan deserialisoinnin pois UI-pääsäikeestä, mikä on ehdoton edellytys sille, että kanvaasin animaatiot ja vieritykset pysyvät 120fps nopeudella nykimättöminä (Anti-Jank).

## **4.3 Diagnostinen Virheenhallinta (Error Boundaries)**

* Koodikanta hylkää Flutterin perinteisen "Red Screen of Deathin" ja käyttää AppExceptionBoundarya virheiden lokaaliin eristämiseen.  
* Tämä on vahva ominaisuus, mutta vaatii viemistä askeleen pidemmälle: jotta työkalu olisi täydellinen, virherajojen on oltava rakeisia (granulaarisia). Koko näytön tai reitittimen sijaan yksittäisten DAG-solmujen ja asetusruutujen tulee kääriytyä omiin virhelaatikkoihinsa.

## ---

**5\. Teknisen Velan Roadmap ja Toimenpiteet (Vuosi 2026\)**

Kokonaisarkkitehtuurin eheyttämiseksi ja teknisen velan korjaamiseksi toteutetaan seuraavat 6 päätoimenpidettä:

1. **Opaque Types (Branded Types) ID-kenttiin:**  
   * *Ongelma:* Primitiivisten merkkijonojen (str/String) käyttö ID-kentissä vaarantaa relaatioiden eheyden.  
   * *Ratkaisu:* Luo backendiin tyyppiluokka (esim. WorkflowId \= NewType('WorkflowId', str)) ja frontendiin Dartin extension type WorkflowId(String). Salli primitiivien käyttö vain uloimmassa URL-reitityksessä.  
2. **Hajautettu Rate Limiting ja Tenacity (Backend):**  
   * *Ongelma:* Lokaalit semaforit eivät riitä pilviklusterissa estämään "Denial of Wallet" \-ilmiötä.  
   * *Ratkaisu:* Korvaa asyncio.Semaphore Redis-pohjaisella "Token Bucket" \-limitterillä, joka seuraa klusteritasolla yhteyksiä ja token-kulutusta. Integroi LLM-klientteihin tenacity-kirjasto (Exponential Backoff \+ Jitter) ja globaali Circuit Breaker estämään turhat API-kutsut vikatilanteissa.  
3. **Client-vetoinen SSE State Reconciliation (Full-Stack):**  
   * *Ongelma:* Nykyinen SSE-striimi (stream\_execution\_status) pollaa kantaa 2 sekunnin välein ja lähettää koko tilan, mikä ei skaalaudu ja on altis verkkokatkoksille.  
   * *Ratkaisu:* Siirry aitoon Event-Driven \-arkkitehtuuriin (Redis Pub/Sub tai PG NOTIFY). Päivitä frontend tallentamaan Last-Event-ID. Yhteyden pätkiessä frontend hakee REST API:lla puuttuvan tilan (Hydration) tai jatkaa SSE-striimiä spesifistä offsetista.  
4. **Täydellinen Event Sourcing Projisointi (Backend):**  
   * *Ongelma:* ExecutionRecord sisältää mutatoituvaa tilaa (step\_states), mikä on ristiriidassa puhtaan Event Sourcingin kanssa.  
   * *Ratkaisu:* Poista mutatoituva tila tietokantamallista. Luota yksinomaan execution\_trace \-taulukkoon ja käytä olemassa olevaa StateProjector \-luokkaa askeleiden nykytilan reaaliaikaiseen projisointiin lukuvaiheessa.  
5. **Granulaariset Error Boundaryt ja DAG-Konteksti (Frontend):**  
   * *Ongelma:* Yhden solmun kaatuminen saattaa invalidoida koko DAG-kankaan tai esitysnäkymän.  
   * *Ratkaisu:* Kääri yksittäiset paneelit ja solmut (esim. dag\_canvas\_view.dart) omiin lokaaleihin AppExceptionBoundary-laatikkoihinsa. Pakota backend sisällyttämään kaatuneen solmun node\_id heitettävän RFC 7807 \-virheen payloadin extensions-kenttään, jotta frontend osaa visuaalisesti korostaa täsmälleen sen kohdan, mihin tekoälyn suoritus pysähtyi.  
6. **Canvas-Renderöinnin Optimointi ja Isolate-Kynnysarvot (Frontend):**  
   * *Toimenpiteet:* Varmista, että DAG-editorin solmut kuuntelevat Riverpod-tilaa vain puhtailla ref.watch(blueprintProvider.select(...)) \-metodeilla yli-renderöinnin estämiseksi. Kääri staattiset taustagridit RepaintBoundary-widgeteihin. Lisää BackgroundTransformeriin kynnysarvo (esim. \> 10 kt data), jotta aivan pienimmät JSON-vastaukset puretaan ilman Isolaten käynnistämisestä johtuvaa viivettä.