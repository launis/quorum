# EPIC 23: Map-Reduce LLM Orchestration & Bounded Contexts

## Tausta (Background)
Gemini 2.5 Pro ja muut modernit mallit pystyvät käsittelemään miljoonia tokeneita syötetietoa (Context Window), mutta niiden infrastruktuuri (ja Pydantic-kirjastojen validointinopeus) kohtaa kriittisen pullonkaulan **Strukturoidun ulostulon (Structured Output) koossa**. 

Tällä hetkellä järjestelmämme pakottaa DAG Executorin tunkemaan koko stepin (sisältäen pahimmillaan jopa 10 arvioitavaa konseptia/matriisia ja satoja `atom_id` kysymyksiä) yhteen ainoaan Pydantic JSON Schemaan. Kun pyydämme LLM:ää generoimaan 300 arviointiobjektia kerralla yhtenä giganttisena taulukkona, malli usein "tukehtuu" JSONin generoimisen raskauteen, katkaisee yhteyden kesken siirron tai ylittää tuotantoinfrastruktuurin oletus-aikakatkaisun (Timeout).

Tämän takia olemme joutuneet laastaroimaan ongelmaa kytkemällä "Matrix Sampling Strategian" rajoittamaan tarkastelua (esim. `STRATIFIED_3` ohittaa satoja atomeja ja tekee valituilla otoksilla arvioita, jotta tulosten määrä pysyy rajallisena).

## Tavoite (Objective)
Rakentaa Backendin DAG (Directed Acyclic Graph) -suorittimeen kyvykkyys dynaamiseen Map-Reduce pirstalointiin. 

Kun `dag_executor.py` tai `llm.py (strategy)` havaitsee askelen (Step) sisältävän valtavan tiheyden datamassoja tai useita rinnakkaisia arviointilohkoja (PromptBlocks), sen tulee atomaarisesti lohkoa nämä itsenäisiksi alatason Pydantic-korikyselyiksi ("Map"). LLM-pyynnöt ammutaan asyncio:lla Vertex AI:hin rinnakkain useana pienenä, nopeasti valmistuvana purskeena. Kun kaikki rinnakkaiset langat valmistuvat, tulokset summataan takaisin yhteen alkuperäisen Step-objektin state-payloadiksi ("Reduce") ja pisteytetään normaalisti `waterfall_scoring_hook`illa.

## Arkkitehtuurivaatimukset
1. **Pirstalointimekanismi (Map)**: DAG-Executorin tai Evaluate-strategian tulee kyetä päättelemään "Painoarvo" (esim. PromptBlockien määrä kerrottuna atomien määrällä). Jos painoarvo ylittää rajan (esim. max 50 atomia per kutsu), syöte leikataan rinnakkaisiksi osapyynnöiksi.
2. **Kokoamismekanismi (Reduce)**: Strict Pydantic -arkkitehtuurin asettamat validointisäännöt on säilytettävä saumattomina lopputuloksen kootessa palasia yhteen. Kokoajafunktion (Aggregator) pitää palauttaa virheettömästi täysi `state_delta` JSON, aivan kuten vanhassa toteutuksessa.
3. **Konkurrenssin suojaelu**: Kun ammutaan 10 rinnakkaista LLM-pyyntöä yhdeltä käyttäjältä, järjestelmän tulee noudattaa uutta `SystemConcurrency` Pydantic Enumia (jotta emme riko Cloud Quotoja ja saa Rate Limit -virheitä 429). Asyncio TaskGroup pitää rajoittaa puristeputkellä (esim. max 3 rinnakkaista requestia).
4. **Resilienssi ja Retry-logiikka**: Jos yksi Map-osa kaatuu, vain se osa yritetään uudelleen pelkän Partial Retry -logiikan kautta (koko 10 minuutin Steppiä ei enää tarvitse nollata ja aloittaa alusta).
5. **No-Limit Seeding**: Kun Epic on valmis, oletuksena oleva `MatrixSamplingStrategy` voidaan asettaa takaisin arvoon `0 (ALL)`, jolloin laatuportti on vapaa auditoimaan absoluuttisesti kaiken saatavilla olevan tiedon.

## Implementointivaiheet (Phases)
- **Phase 1**: Luodaan `ChunkingService` Pydantic-skeema, joka testataan erillisenä irrallisena moduulina.
- **Phase 2**: Laajennetaan `backend_v2/services/orchestrator/strategies/llm.py` hyväksymään modulaarisesti paloitellun prompt-arrayn.
- **Phase 3**: Rinnakkaisuus-Limiter (Semaphore) infrastruktuuri Vertex-kutsun (`litellm`) ympärille estämään tukehtumisen.
- **Phase 4**: Map-Reduce End-to-End yksikkötestaus.
- **Phase 5**: `STRATIFIED_3` poistaminen tuotannosta ja siirtyminen globaaliin `ALL (0)` prosessointiin.
