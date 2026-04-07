# Epic 15: Deterministic Evaluation & Dynamic Output Orchestration

## Tiivistelmä (Executive Summary)
Cognitive Quorum V2:n skaalautuessa olemme kohdanneet haasteen kognitiivisessa arvioinnissa: **Vääristynyt pistehajonta ("Cliff-Edge Variance")**. Kun raskaasti kuormitettuja ja virheitä antagonistisesti janoavia matriiseja (Toulmin, Bloom, Kahneman) arvioidaan lämpötiloilla T > 0.0 tai niille annetaan pääsy internetiin (MCP Tavily / Grounding), LLM voi satunnaisotannasta riippuen tuomita täysin identtisen syötteen joko "Kriittisesti vaarantuneeksi" (77p) tai "Poikkeuksellisen yhtenäiseksi" (92p).

Tämä Epic (Epic 15) toteuttaa arviointikokonaisuuden massiivisen uudelleenkirjoituksen takaamaan asiantuntijatason determinismin ja tasapuolisen lujuuden. MCP (Agenttien tutkimustaidot) siirretään pois matriisien arvostelunäkymästä puhtaasti tulostuksenhallinnan (`OutputProfile` & `synthesis_md`) apuvälineeksi.

## Ongelman Kartoitus

1. **False Warrants & Hiding Bad Data:** Jos LLM-työkalulle annetaan internetyhteys Toulmin-matriisin arvioinnissa, agentti voi käyttää ulkoista hakua löytääkseen todisteita käyttäjän argumentin taustalle, antaen vahvat Systeemi 2 -pisteet. Tämä on validointivirhe: järjestelmä arvioi hakukoneen älykkyyttä, ei itse perusdatan kestävyyttä.
2. **Kognitiivinen Värinä (Cognitive Jitter):** Pääasiassa LLM-lämpötilasta (Temp > 0) johtuva ilmiö, jossa äärimmäisen monimutkainen päättelyketju johtaa radikaaleihin ääripäihin (cliff-edge fall).

## Vaiheistettu Ratkaisumalli (Phased Approach)

Kyllä, alkuperäiset vaihtoehdot voidaan ja kannattaa nähdä peräkkäisinä vaiheina (Vaihe 1: Taktinen korjaus, Vaihe 2: Strateginen lukitus). Tämä vähentää kertajulkaisun riskiä ja ratkaisee akuutin tuotanto-ongelman heti.

### Vaihe 1: DB-Driven Seeding & Configuration (Taktinen pikakorjaus)
- **Tavoite:** Välitön pisteiden stabilointi ilman kooditason (backend/frontend) tuotantokäännöksiä.
- **Toteutus:** Päivitetään `seed_data.json` siten, että `model_registry` pakottaa malleille `strict` ja `precise` `temperature: 0.0` ja poistaa niiltä luvan internetin käyttöön (`supports_grounding: false`). Suoritetaan ns. Inverse Merge / Seeder-ajo kantaan.
- **Hyödyt:** Ratkaisee kognitiivisen värinän ja 90% False Warrant -ongelmista minuuteissa asetusmuutoksen myötä. Asiakaskokemus paranee välittömästi.

### Vaihe 2: Architectural Enforcement Boundary / Fencing (Strateginen lukkomekanismi)
- **Tavoite:** Eliminoida inhimillisten hallintavirheiden riski ("Human Error / Admin Misconfiguration Risk"). Estää arkkitehtuurisesti arviointien tuhoaminen väärillä asetusmuutoksilla pitkällä aikavälillä, sekä siirtää MCP täysimääräisesti tulostuksenhallintaan (`TextConsolidationHook`).
- **Toteutus:** Koodikerroksen (`prompt_compiler.py` / `executor.py`) päivitys. Backend lukee DAG-solmun tyypin: Jos tyyppi on `evaluation` tai `matrix`, koodi **ohittaa ja poistaa lennosta** asetetut MCP-työkalut sekä **pakottaa** matemaattisesti lämpötilaksi T=0.0. UI:hin päivitetään lukkosymboolit osoittamaan tämän eristyksen aktiivisuudesta.
- **Hyödyt:** Tekee järjestelmästä luodinkestävän. Antigravity V2 "Fail-Fast"-standardien mukainen lopullinen päätepiste.

## Vaiheistettu Suunnitelma (V2 Sequence Priority)

### Milestones 1: Backend Fencing (Arviointien eristäminen)
Varmistetaan, että `DAGExecutor` pystyy identifioimaan, suorittaako se "suljettua viestintää" (Arviointi) vai "avointa viestintää" (Synteesi tai Haku). Odotuksiin kuuluu rakennemuutos `prompt_compiler.py`:n tuottamaan ajonaikaiseen JSON-skemaan, siten että mallin config-rajoitteet (`temperature`, `tools`) yliajetaan kovakoodatuilla Zero-variance määritteillä poikkeuksellisen tärkeiden tiukkuusmittareiden ohjauksessa.

### Milestones 2: The MCP Shift (Synteesin vapauttaminen)
Rakennetaan `text_consolidation_hook.py`:hin (joka laukaistaan asynkronisesta ARQ Workerista) suora yhteys `SystemConfigModelRegistry`:n `mcp_gateways`-objektiin. Kun synteesi (Executive Summary tai Valmennus) laaditaan, agentti lukee *puhdasta ja suljettua matemaattista pistehistoriaa (esim. Bloom Tasolle 2 = matala)*, ja sitten kutsuu MCP-hakuja saadakseen globaaleja ohjeita, miten nämä virheet tyypillisesti korjataan toimialalla (Coaching). 

### Milestones 3: Firestore Data Limitation Rescue
Koska MCP (Internet Retrieval) syöttää raskasta kontekstidataa synteesiin, on välttämätöntä suunnitella samalla, minne nämä `mcpToolAudit` jäljet tallennetaan ilman `ExecutionRecord`-dokumentin 1MB Firestore rajotteen kaatumista. Auditin blob-tallennus offloadina Azureen/GCP Storageen vahvasti suositeltu.

### Milestones 4: Frontend "Trust Boundary" Visualization
Dart/Flutter `dag_builder.dart` ja `ResultDashboard` koodipohjien päivitys. Uusi "Fenced / Unfenced" ikoni kertoo ylläpitäjälle, milloin mallilla on lupa tutkia internetiä ja milloin sitä pidetään "mustassa laatikossa" ankarassa Toulmin-kuulustelussa.

## Hyväksyntä (Verification & Quality Gate)
- Käännettävä uusi yksikkötestaus pyteillä (PyTest) `backend_v2/tests/orchestrator/test_enforced_fencing.py`. Sen on validoitava Pydanticin schema ja varmistettava, ettei `LLMClient.generate` saa sekunnin murto-osaakaan yliajaa nollalämpötilaa.
- Flutterissa on lisättävä visuaalinen regressiotesti varmistamaan Pydantic Freezed -kartan lataus (`ReportDataDTO` vs `SynthesisConfigDTO`).
- Quality Gate reititetään puhtaasti `scripts/backend_audit_loop.py` läpi ennen commitia.
