# Epic 62: LLM Concurrency Hardening & Universal Provider Decoupling (Monipilven Hallinta, Dynaaminen Jitter-Perääntyminen ja Kontekstin Välimuisti)

> [!IMPORTANT]
> **THE UNIVERSAL PROVIDER DECOUPLING & RESILIENCY MANDATE**: Tämä Epic toteutetaan ilman yhtäkään kovakoodattua tarjoaja- tai sijaintiriippuvuutta Python-koodin ajokerroksessa (No Provider-Hardcoding). Kaikki pilvi- ja konesalispesifit lisäasetukset (kuten GCP:n `vertex_location`, AWS:n `aws_region` tai Azuren `api_version`) siirretään ja ylläpidetään yksinomaan tietokantatasolla (`seed_data.json` / TinyDB) polymorfisen `additional_params` -sanakirjan sisällä. Kooditaso pysyy 100 % geneerisenä ja hyödyntää dynaamista ympäristömuuttujien interpolointia (Dynamic Env Variable Interpolation) sekä jitter-pohjaista eksponentiaalista retry-suojaa.

---

## 1. Yhteenveto ja Tavoite (Objective)

Tämän Epicin tavoitteena on poistaa nykyisen LLM-kutsukerroksen (`LiteLLMProvider`) kiinteä riippuvuus Google Vertex AI -ympäristöstä, tehdä järjestelmästä aidosti monipilviyhteensopiva (Multi-Cloud Ready) ja nostaa suorituskyky uudelle tasolle.

### Tunnistetut Nykytilan Ongelmat:
1. **Vertex-kovakoodaus ja kaatuminen**: `LiteLLMProvider.generate` hakee ja pakottaa `VERTEX_LOCATION`-ympäristömuuttujan olemassaolon ja kaatuu virheeseen (`ValueError`), jos se puuttuu – silloinkin, kun kutsutaan muiden tarjoajien (kuten OpenAI tai Anthropic) malleja.
2. **Jäykkä ja hidas perääntymisaika**: Rate-limit -odotusaika (`RATE_LIMIT_COOLDOWN_SECONDS` = 30) on staattinen vakio. Ensimmäinen API-kooldown odottaa heti 30 sekuntia + jitter, mikä hidastaa toipumista pienistä ja ohimenevistä API-ruuhkista turhaan.
3. **SSOT Caching -integraation puute**: Vaikka Epic 60:ssä erotimme static- ja dynamic-promptlohkot, välimuisti (Context Caching) ei osaa dynaamisesti sopeutua eri tarjoajien välimuististandardeihin (Gemini Native vs Anthropic Ephemeral vs OpenAI Auto).

### Arkkitehtoninen Ratkaisu:
1. **Dynamic Env Variable Interpolation**: Luodaan kooditasolle dynaaminen muuttujaratkaisija. Kaikki `additional_params` -sanakirjaan tallennetut muotoa `"${VAR_NAME}"` olevat merkkijonot korvataan ajonaikana todellisilla ympäristömuuttujilla. Jos muuttujaa ei löydy, laukaistaan välitön virhe (Fail-Fast).
2. **Yleinen parametrikerros (Decoupled Provider)**: Poistetaan `provider.py` -koodista kaikki suorat viittaukset `VERTEX_LOCATION`-muuttujaan. Kutsuparametrit haetaan `additional_params` -kentästä ja puretaan (`**`) suoraan LiteLLM-kutsupakettiin, jolloin LiteLLM reitittää ne itsenäisesti oikeille tarjoajille.
3. **Eksponentiaalinen Jitter-Perääntyminen (Exponential Backoff with Jitter)**: Korvataan kiinteä 30s odotus tenacityn dynaamisella `wait_exponential(multiplier=2, min=2, max=30) + wait_random(1, 5)` -odotuksella. Yritysketju toipuu hetkellisistä 429-virheistä sekunneissa, mutta suojaa pilvikiintiöitä kasvaen asteittain pitkiin odotuksiin.
4. **Universaali Välimuistin Hallinta (Universal Cache Strategy)**: Abstractoidaan promptien välimuistitagit dynaamisesti `caching_strategy`-arvon mukaan (Google Gemini Native, Anthropic Ephemeral, OpenAI Auto).

---

## 2. Arkkitehtuuristen sääntöjen huomiointi (Compliance Matrix)

Kehityksessä on noudatettava tiukasti seuraavia `c:\src\quorum\.agents\rules` -hakemiston sääntöjä:

### 2.1. Ydinjärjestelmä ja laatuportit (00-antigravity-core.md & 01-python-backend.md)
* **The Zero-Compromise Pledge (00)**: Jos jokin dynaaminen ympäristömuuttuja (kuten `VERTEX_LOCATION` Googlelle) puuttuu kokonaan ajonaikana, järjestelmän tulee kaatua välittömästi `ConfigurationError`-virheeseen. Fallback-arvoja ei sallita.
* **System Concurrency SSOT (01 & 05)**: Suorituksen rinnakkaisuusrajat ja retry-määrät ladataan tiukasti `SystemConcurrency`-enumista. `LLM_MAX_RETRIES` on lukittu pysyvästi arvoon 2, jotta vältetään hallitsemattomat API-maksujen vyörytyskierteet.

### 2.2. Kielimallin ja tulostuksen arkkitehtuuri (05_llm_architecture.md)
* **Naked Prompt Injection Ban**: Kaikki välimuistiin (Context Cache) vietävät PromptBlockit ja ohjeistukset pidetään tiukasti static-tilassa ja dynaamiset parametrit eristetään `"user"`-viestin alkuun `<execution_parameters>` -rakenteeseen caching-hyödyn maksimoimiseksi.
* **Universal LLM Wrapper**: Kaikki kutsut kulkevat suojatun `LLMClient` ja `LLMFactory` -arkkitehtuurin läpi. Suoria sdk-kutsuja ei sallita missään backendin apuohjelmassa.

---

## 3. Arkkitehtuurinen Suunnittelu (Proposed Code Changes)

```mermaid
graph TD
    A[Model Registry / seed_data.json] -->|additional_params + caching_strategy| B[LLMClient.from_strategy]
    B -->|Resolve ${ENV_VAR}| C[Dynamic Env Resolver]
    C -->|Unpack params & apply cache tags| D[LiteLLMProvider.generate]
    D -->|wait_exponential + wait_random| E[LiteLLM Router / acompletion]
```

### 3.1. Ympäristömuuttujien Dynaaminen Interpolointi (Dynamic Env Resolver)
Toteutetaan `backend_v2/llm/provider.py` -tiedostoon globaali apufunktio interpoloimaan ympäristömuuttujia:

```python
def resolve_env_variables(params: dict[str, Any]) -> dict[str, Any]:
    """Korvaa parametrien ${ENV_VAR} -viitteet todellisilla ympäristömuuttujilla."""
    resolved = {}
    for k, v in params.items():
        if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
            env_key = v[2:-1]
            resolved_value = os.getenv(env_key)
            if not resolved_value:
                raise ConfigurationError(
                    f"Strict Mode: Vaadittua ympäristömuuttujaa '{env_key}' ei löydy "
                    f"järjestelmästä parametrille '{k}'."
                )
            resolved[k] = resolved_value
        else:
            resolved[k] = v
    return resolved
```

### 3.2. Yleinen parametrikerros (`provider.py`)
Päivitetään `LiteLLMProvider.generate` purkamaan lisäparametrit dynaamisesti ilman Vertex-spesifejä kovakoodauksia:

```python
# 1. Alustetaan geneeriset LiteLLM-kutsuparametrit
call_kwargs = {
    "model": self.model_name,
    "messages": final_messages,
    "temperature": temperature,
    "max_tokens": max_tokens,
    "top_p": top_p,
    "top_k": top_k,
    "timeout": strict_timeout,
}

# 2. Puretaan pilvispesifit parametrit dynaamisesti tietokannan additional_params -lohkosta
if self._config and self._config.additional_params:
    resolved_additional = resolve_env_variables(self._config.additional_params)
    call_kwargs.update(resolved_additional)
```

### 3.3. Jitter-perääntymisen päivitys (`provider.py`)
Korvataan nykyinen kiinteä tenacityn `wait_fixed`-odotus dynaamisella eksponentiaalisella backoffilla ja jitterillä:

```python
async for attempt in AsyncRetrying(
    stop=stop_after_attempt(max_rate_limit_retries + 1),
    wait=wait_combine(
        wait_exponential(multiplier=2, min=2, max=30),
        wait_random(1, 5),
    ),
    retry=retry_if_exception(_is_transient_llm_error),
    reraise=True,
    before_sleep=lambda rs: logger.warning(
        "[LiteLLMProvider] Transient Error or Quota Exhausted (Attempt %s/%s). "
        "Initiating dynamic exponential backoff... | Error: %s",
        rs.attempt_number,
        max_rate_limit_retries,
        type(rs.outcome.exception()).__name__ if rs.outcome and rs.outcome.failed else "Unknown",
    ),
):
    with attempt:
        _timeout = call_kwargs["timeout"]
        response = await asyncio.wait_for(self.router.acompletion(**call_kwargs), timeout=float(_timeout))
```

---

## 4. Toteutusvaiheet (Implementation Phases)

### Phase 1: Tietokannan ja Seeding-rakenteen Päivitys (Database Refactoring)
* **Toimenpide**: Päivitetään siementiedosto `backend_v2/seed/seed_data.json` poistamalla kovakoodatut sijainnit ja ottamalla käyttöön dynaamiset parametrit:
  ```json
  "additional_params": {
    "vertex_location": "${VERTEX_LOCATION}"
  }
  ```
* **Seeding-ajo**: Ajetaan seederi TinyDB-kehitystietokannan päivittämiseksi:
  ```powershell
  uv run python backend_v2/seed/run_seed.py
  ```

### Phase 2: Dynaamisen Ympäristöresoluution Toteutus (Provider Decoupling)
* **Toimenpide**: Kirjoitetaan `resolve_env_variables` -apufunktio `provider.py` -tiedostoon.
* **Puhdistus**: Poistetaan kaikki kiinteät `VERTEX_LOCATION` -tarkistukset ja mahdollistetaan `additional_params` -sanakirjan täysi purku `call_kwargs`-rakenteeseen.

### Phase 3: Jitter-perääntymisen Integrointi (Retry Resiliency)
* **Toimenpide**: Päivitetään tenacity-retry-loop `LiteLLMProvider.generate` -metodissa käyttämään eksponentiaalista backoffia ja satunnaista jitteriä.
* **Varmistus**: Testataan, että perättäiset transientit virheet (kuten 429) korjaantuvat hallitusti.

### Phase 4: Universaalin Välimuistin Hallinnan Päivitys (Context Caching)
* **Toimenpide**: Päivitetään `client.py` dynaamisesti soveltamaan cache_control-tageja viesteille riippuen `self._config.caching_strategy` -arvosta (esim. `anthropic_ephemeral`, `gemini_native`).

### Phase 5: Laadunvarmistus & Laatuportti (Verification Loop)
* **Yksikkötestit**: Ajetaan kaikki LLM-yksikkötestit ja kirjoitetaan uusi testi `test_adaptive_retry.py` varmistamaan dynaamisen perääntymisen toiminta.

---

## 5. Definition of Done (DoD)

1. **Zero Provider Hardcoding**: Kooditasolla ei ole yhtäkään kovakoodattua tarkistusta tai viittausta muuttujiin kuten `VERTEX_LOCATION`.
2. **Dynamic Interpolation**: Kaikki `"${VAR_NAME}"` -rakenteet tietokannan `additional_params`-lohkossa ratkaistaan dynaamisesti ympäristömuuttujista, ja puuttuvat muuttujat laukaisevat `ConfigurationError`-virheen.
3. **Resilient Jitter Backoff**: Kooldown ei odota heti 30 sekuntia, vaan aloittaa noin 2–4 sekunnista ja nousee eksponentiaalisesti maksimissaan 30 sekuntiin, satunnaisella viiveellä varustettuna.
4. **All Tests Green**: Kaikki yksikkö- ja integrointitestit menevät puhtaasti läpi laatuportissa:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/ --test
   ```
