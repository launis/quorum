# EPIC: V3 LLM Concurrency Limiter & Rate Throttle

**STATUS:** Draft / Planning Phase  
**TIER:** Tier 1 (Epic Planner)  
**CONTEXT:** Quorum V3 Architecture (Python Backend V2 + Model Registry API)  
**LAST UPDATED:** 2026-03-25

## 📌 1. Objective

V3 `DAGExecutor` paralleloi kaikki riippumattomat nodet (`asyncio.gather`). Suurissa matriiseissa (Toulmin, BARS, Bloom) moottori laukaisee 10-20 samanaikaista LLM-kutsua.

**europe-north1** kiintiöt (todistettu 2026-03-24):

| Malli | RPM | TPM |
|-------|-----|-----|
| `gemini-2.5-flash` | **5** | 4 000 000 |
| `gemini-2.5-pro` | **5** | 4 000 000 |

5 RPM:n rajoituksella 10 rinnakkaista kutsua → 5 saa `429 RESOURCE_EXHAUSTED` → retry 10s → ylimääräistä viivettä ja kustannusta.

---

## 💰 2. Kustannusanalyysi

### Vertex AI Hinnoittelu (per 1M tokenia)

| Malli | Input | Output | Reasoning |
|-------|-------|--------|-----------|
| **Flash** | $0.30 | $2.50 | ~$0.30* |
| **Pro** | $1.25 | $10.00 | ~$1.25* |

*Reasoning-tokenit hinnoitellaan input-tasolla.

### Tänäinen ajo (exe_69b1..., 2026-03-24)

| Mittari | Arvo |
|---------|------|
| Prompt tokens | 238 467 |
| Completion tokens | 70 631 |
| Reasoning tokens | 45 807 |
| **Kokonaishinta** | **$0.7209** |
| 429-retryja | 1 kpl (flash step, ~40K prompt tokenia) |

**Retry-hukkakustannus:** ~40K prompt + ~8K completion uudestaan ≈ **$0.03 per retry**

Yhdessä ajossa 1 retry → ~4% hukkaa. Mutta pahimmillaan (kaikki 10 stepiä bouncevat) → **~$0.30 hukkaa per ajo** (42% kokonais).

### Kuukausitason projisointi

| Skenaario | Ajoja/kk | Retryjä/ajo | Hukkakustannus/kk |
|-----------|----------|-------------|-------------------|
| Normaali (1 retry) | 100 | 1 | **$3** |
| Ruuhka (5 retryä) | 100 | 5 | **$15** |
| Worst case (10 retryä) | 100 | 10 | **$30** |

---

## 🔀 3. Vaihtoehtojen vertailu

| Vaihtoehto | Kustannus | Vaikutus RPM:ään | Dev-työ | Vaikutus hintaan |
|------------|-----------|------------------|---------|------------------|
| **A. Quota Increase** (GCP Console) | Ilmainen | 5 → 30+ RPM | 0h | Eliminoi retryjen hukkakustannus ($3-30/kk) |
| **B. Region-vaihto** (`europe-west4`) | Ilmainen | Mahdollisesti korkeampi RPM | 0.5h (env muutos) | Sama kuin A |
| **C. Concurrency Limiter** (tämä EPIC) | Ilmainen | Ei muuta RPM:ää, mutta eliminoi retryt | 4-8h dev | Eliminoi hukkakustannus + puhtaammat logit |
| **D. A + C yhdessä** | Ilmainen | 30+ RPM + älykäs jonottaminen | 4-8h dev | **Paras**: nopeampi + ei hukkaa |

### Suositus

> [!IMPORTANT]
> **Edullisin ratkaisu: A (Quota Increase)**. Se on ilmainen, välitön, ja eliminoi 429-retryjen hukkakustannuksen.
>
> **Rakenteellisesti paras: D (A + C)**. Quota increase antaa enemmän tilaa, ja Concurrency Limiter varmistaa ettei mitään kiintiötä koskaan ylitetä — myös tuotannossa monella käyttäjällä.

**Hinnan kannalta suurin säästö** ei tule retryjen eliminoinnista vaan **mallistrategian optimoinnista**: jos yksi Pro-step ($1.25/M) voitaisiin korvata Flash:illä ($0.30/M), se säästäisi **4x enemmän** per kutsu kuin minkään retryn eliminointi.

---

## 🏗️ 4. Architectural Design

1. **Semaphore:** Rajoita samanaikaiset kutsut per malli. Jos `rpm_limit: 5`, max 5 inflight-kutsua.
2. **Token Bucket:** Seuraa ajallista kulutusta (`requests_sent_in_last_60s`). Jos `>= rpm_limit` → `asyncio.sleep()` kunnes ikkuna vapautuu.
3. **Model Registry Awareness:** Rajat luetaan dynaamisesti Model Registrystä — ei hardcoodattuja arvoja.

---

## 🗺️ 5. Execution Milestones

### Phase 1: Core Limiter
- [ ] **Create:** `backend_v2/utils/rate_limiter.py`
- [ ] **Implement:** `GlobalRateLimiter` singleton (rolling window of timestamps)
- [ ] **Expose:** `async with throttled(model_name=...)` context manager

### Phase 2: Integration
- [ ] **Inject:** Integroi `provider.py`:hin ennen `litellm.acompletion()`
- [ ] **Dynamic:** Lue `tpm_limit`/`rpm_limit` executionin Model Configista
- [ ] **Verify:** `asyncio.sleep(retry_after)` kun ikkuna täynnä

### Phase 3: Validation
- [ ] **Benchmark:** 30 rinnakkaista evaluation-nodea
- [ ] **Log:** Tasainen stagger (2 kutsua/12s) eikä burst + 429-punaisia
- [ ] **Frontend:** SSE-stream ei timeoutaa hitaan jonon aikana

---

## 🚨 6. Banned Patterns
- **Ei hardcoodattuja rajoja:** `RATE_LIMIT = 5` → KIELLETTY. Rajat Model Registrystä.
- **Ei blocking sleep:** `time.sleep()` → KIELLETTY. Vain `await asyncio.sleep()`.
- **Ei virheiden piilottelua:** 429 piirtää silti läpi → LiteLLM retry turvaverkkona.
