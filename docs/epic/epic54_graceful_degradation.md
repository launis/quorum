# Epic 54: Graceful Degradation & Telemetry Hardening

## 1. Yhteenveto (Executive Summary)
Nykyinen V6-arkkitehtuuri noudattaa äärimmäisen tiukkaa "Fail-Fast" -protokollaa. Vaikka tämä suojelee tietokannan eheyttä täydellisesti, se aiheuttaa työnkulkujen (DAG) kaatumisia tilanteissa, joissa probabilistinen tekoälymalli on yksinkertaisesti kyvytön suorittamaan tiettyä arviointia (esim. Sycophancy-luuppi). Tämä Epic muuntaa järjestelmän vikasietoiseksi (Fault Tolerant) siirtymällä pehmeään epäonnistumiseen (Graceful Degradation) askeleiden sisällä ja korjaamalla telemetrian hälytystasot.

## 2. Vaihe 1: Telemetrian Normalisointi (Alert Fatigue Prevention)
**Kohdetiedosto:** `backend_v2/services/orchestrator/anchor_validation_service.py`

**Ongelma:** Tällä hetkellä Lexical Verifier lokittaa kaikki LLM:n tekemät virheet tasolla `[ERROR]`. Koska järjestelmässä on sisäänrakennettu "Self-Healing" -luuppi, valtaosasta näistä virheistä toivutaan seuraavalla yrityksellä. Error-tason käyttö näissä tapauksissa vääristää lokien luettavuutta ja aiheuttaa hälytysväsymystä (Alert Fatigue).

**Toteutus:**
- Etsitään `AnchorValidationService` -luokasta 4 instances, joissa kutsutaan `logger.error()` poikkeusten (Trace Contradiction, Empty Anchor, Hallucinated Anchor, Quote ei löydy) yhteydessä.
- Vaihdetaan nämä `logger.warning()` -kutsuiksi.
- Pidetään poikkeuksen nostaminen (`raise SemanticEvidenceError`) ennallaan, jotta työnkulkulogiikka ei muutu.

## 3. Vaihe 2: Circuit Breaker & Null Object Pattern
**Kohdetiedosto:** `backend_v2/services/llm_task_executor.py`

**Ongelma:** Kun tekoäly jää jumiin "Self-Healing" -luuppiin ja kuluttaa loppuun maksimiyrityksensä (esim. `current_logical_retries >= max_logical_retries`), järjestelmä kaataa koko työnkulun `WorkflowExecutionError` -poikkeuksella. 

**Toteutus:**
- Rakennetaan "Circuit Breaker" -logiikka kohtaan, jossa maksimiyritykset ylittyvät.
- Poikkeuksen heittämisen sijaan luodaan Pydantic-skemaa (`target_schema`) vasten **neuraali Null Object Fallback**.
- Varmistetaan, että `LLMTaskExecutor` osaa dynaamisesti luoda paluuarvon, jossa on turvalliset "en tiedä" -arvot (esim. `score=0`, `exact_quote=None`, `justification="[SYSTEM ERROR: LLM Unable to verify.]"`).
- Tämä palautetaan onnistuneena tuloksena DAG:lle, jolloin työnkulku jatkuu häiriöttä eteenpäin.

## 4. Vaihe 3: SDUI / Käyttöliittymän valmistautuminen (Future Scope)
- Varmistetaan, että käyttöliittymän (Flutter) SDUI-kerros ja PDF-generaattori on ohjelmoitu ymmärtämään "Null Object" -arvot (esim. `score == 0` tai null-arvoiset lainaukset) ja generoimaan niiden kohdalle kaatumisen sijaan visuaalisesti neutraali "Tietoa ei pystytty varmentamaan" -komponentti.

## 5. Hyväksymiskriteerit (Definition of Done)
1. Lokien seuranta näyttää `[WARNING]` tason ilmoituksia, kun LLM hallusinoi.
2. Kun LLM pakotetaan epäonnistumaan yli 3 kertaa, ajo **ei FAILED** -tilaan, vaan jatkaa matkaa ja kantaan tallentuu neutraali Fallback-objekti.
3. Arkkitehtuurin "Zero-Compromise" -sääntö ei murru: Koodi ei valehtele LLM:n keksineen dataa, vaan myöntää avoimesti tekoälyn epäonnistuneen ja jättää datan puuttumaan.
