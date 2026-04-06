# Epic: Nykyaikainen Testikattavuus 38 % -> 70 % (Backend V2)

Tämä Epic sitoo V2-arkkitehtuurin asettamat fail-fast-periaatteet oikeaoppisesti testauksen piiriin, painottaen ydinliiketoimintalogiikkaa. Työ on jaettu mahdollisimman pieniin mikrovaiheisiin väsymisen ja koodin monimutkaistumisen estämiseksi.

## 1. Liiketoimintalogiikka & Hookit (Kriittisin Arvo)
*Täällä asuu Antigravity-laskennan ydin. Aloitamme täältä, koska logiikan hajoaminen on kaikkein kalleinta.*

* **Milestone 1.1: Pisteytysmoottori (Scoring) [TEHTY ✅]**
  * **Tiedosto:** `backend_v2/hooks/scoring.py` (Saavutettu: 90%+ API-tason kattavuus)
  * **Sisältö:** Toulminin matriisin ja Kahneman-skaalojen arviointitulosten determinismin ja Pydantic validation bypassien eston testaus.
* **Milestone 1.2: Synteesi- ja Raportointimoottorit**
  * **Tiedosto:** `backend_v2/hooks/reporting.py` & `synthesis.py` (Tavoite: +340 riviä testien piiriin)
  * **Sisältö:** `AppException`-virhemerkinnät, Dual-Reporting heitot, ja Opaque ID referenssien eheyden testaus raporteissa.
* **Milestone 1.3: Mittaristot ja Eheys (Metrics & Integrity)**
  * **Tiedostot:** `backend_v2/hooks/integrity.py` & `metrics.py` (Tavoite: +250 riviä testien piiriin)
  * **Sisältö:** Tietoturvallisen putken keskeyttävät Guardrails-tarkistukset.

## 2. Abstraktiokerrokset (LLM)
*Moottori on testattu, seuraavaksi ulkopuolisten riippuvuuksien kestävyys.*

* **Milestone 2.1: Palveluntarjoajat & Clientit**
  * **Tiedostot:** `backend_v2/llm/provider.py` & `client.py`
  * **Sisältö:** Circuit Breaker -laukaisimet, token-veron mittaukset (FinOps). Error-handlaus ulkoisten rajapintojen (OpenAI, Gemini) simulaatioilla.
* **Milestone 2.2: Käsittelijät (Handlers)**
  * **Tiedosto:** `backend_v2/llm/handler.py`
  * **Sisältö:** Tenacityn retry-luuppien ja 'Semantic Self-Healing' -operaatioiden simulaatio.

## 3. Core-palvelut & Orchestrators
*Tämä alue orkestroi tietovirtauksen. Testit painottavat tilakonetta.*

* **Milestone 3.1: Cognitive Studio Config Management**
  * **Tiedosto:** `backend_v2/services/studio.py`
  * **Sisältö:** Registry routing bypassien testaus, Blueprint generation.
* **Milestone 3.2: Suoritus & Työntekijä (Execution & Worker)**
  * **Tiedostot:** `backend_v2/services/execution.py` & `worker.py`
  * **Sisältö:** ARQ-taustajonon ajon flow-testit. Workflow DAG graph validation (cycles, missing variables).

## 4. Pysyvyys & Turva (Tietokanta / IAM)
*Suurimmat tiedostot, joissa on jo käsin tehtyjä tarkistuksia. Valitsemme strategisen mockauksen tason.*

* **Milestone 4.1: Tietokantakuluttajien API**
  * **Tiedosto:** `backend_v2/database/repository.py` (~645 testaamatonta riviä)
  * **Sisältö:** Optimistic Concurrency lukkojen simuloiminen ja V2 JSON parser virhetilat.
* **Milestone 4.2: Tietoturva & Sessiot (Auth)**
  * **Tiedosto:** `backend_v2/services/auth.py`
  * **Sisältö:** Pydantic strict Attribute-based access (getattr vs get), ja Red Screen-tilat organisaatiorooli puutteissa.
