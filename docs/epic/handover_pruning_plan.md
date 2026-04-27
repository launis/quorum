# Context Pruning & Score Injection Strategy

## 1. Ongelma ja Ratkaisu: Strict Schema-Driven Routing
Reitittäjä (`llm.py`) luo `schema_map` -sanakirjan puutteellisesti. Etsimme ja korjaamme `llm.py`:ssä olevan logiikan, joka rakentaa `schema_map`-sanakirjan. Järjestelmän pitää päätellä suoraan tietokannan DAG-rakenteesta (Blueprint), mitkä askeleet ovat asiantuntijamatriiseja (`"MATRIX"`), ja muut ovat `"TEXT"`. Tämä kytkee "Ruthless Pruning" -karsinnan päälle automaattisesti.

## 2. Arvosanan sisällyttäminen (Option C)
Poistamme raskaat boolean-taulukot `context_builder.py`:stä. Syötämme XAI Reporterille tiiviin paketin:
`{"normalized_score": 70.0, "raw_result": "4.2/6.0", "justification": "..."}`

## 3. Toteutettavat askeleet:
1. **Orchestrator (`llm.py`):** Korjataan `schema_map` rakentumaan oikein DAG-rakenteen perusteella.
2. **Context Builder (`context_builder.py`):** Implementoidaan `raw_result` -murtoluvun rakentaminen muodossa `f"{raw_score} / {len(evaluated_atoms)}"`.
3. **Reporting Hook (`reporting.py` & DTOs):** Varmistetaan, että `MatrixObservabilityDTO` ja `GlobalContextVarsDTO` osaavat poimia `justification`-kentän UI/PDF-tulostusta varten.
4. **Jinja2 / UI-varmistus:** Varmistetaan, että raporttigeneraattorin ja UI:n käyttämä staattinen taulukko tulostaa `justification`-kentän.
5. **CLI-tarkistus (`lue_tulokset.py`):** Varmistetaan ajolla, että massiiviset 100k token-virheet katoavat logeista.
