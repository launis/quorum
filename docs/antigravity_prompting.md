# 🚀 Antigravity Prompting - Komentokeskus & Työkalupakki (V5.1 / Phase 9 Hardening)

> [!IMPORTANT]
> Tämä dokumentti on **Komentokeskus** ja lakikirja Google Antigravity / Gemini -tekoälyn ohjaamiseen. Koska olemme **Phase 9 Hardening** -vaiheessa, tekoälyn tehtävä ei ole "koodata nopeasti", vaan tuottaa **100 % sääntöjen mukaista, turvallista ja virheetöntä koodia**. 

Tässä dokumentissa kuvataan yhtenäinen **Kolmitasoinen Toimintamalli (3-Tier Protocol)** kaikenkokoisten tehtävien suorittamiseen. Se ohjaa suurien arkkitehtuurimuutosten pilkkomista (Taso 1), niiden suorittamista (Taso 2) sekä päivittäistä yksittäisien ohjelmien työstöä, työn auditointia sekä siemendatan muokkausta (Taso 3). Kaikki toiminta pohjautuu **Universal Mandate** -lopputekstiin.

---

## 🎯 TOIMINTAMALLIN KOLME TASOA (Valitse ja kopioi tarvitsemasi)

Valitse tarpeeseesi sopiva ohjeistuslohko tekstin sisältä ja kopioi se kokonaisuutena tekoälylle. **Lisää aina perään UNIVERSAL MANDATE (löytyy sivun lopusta).**

---

### 🟢 TASO 1: EPIC PLANNER (Ison muutoksen suunnittelu)
*Käyttö: Tällä tasolla tavoite on luoda yhdestä laajasta kokonaisuudesta (useita tiedostoja, uusi agentti) pilkottu `implementation_plan.md` tai sen pohjalta generoida useampi tarkempi suunnitelma ennen koodin kirjoittamista.*

```text
Goal: [KIRJOITA TAVOITE. Esim: "Suunnittele ja toteuta uusi raportointimoduuli ja UI"]

ROLE: Principal Solutions Architect (2026 Context - Phase 9 Hardening).
REFERENCE: `@docs/flutterpromptohje.md` (Read first. Absolute law).

INSTRUCTIONS (LEVEL 1):
1. READ: Do NOT write code yet. Familiarize yourself with the architectural laws.
2. PLAN: Create an `implementation_plan.md` breaking this goal into 4-6 independent Milestones.
3. SEQUENCE: Every milestone MUST strictly follow the V5.1 sequence (Dependencies -> Pydantic Models -> L10n -> Repo -> API -> Frontend Models -> Frontend Controller -> UI).
4. SCOPING: Explicitly map which files are `TARGET (Modify)` and which are `CONTEXT (Read-Only)`.
5. PAUSE: Present the plan and WAIT for explicit approval ("LUPA MYÖNNETTY"). Do not implement anything.
```

---

### 🟡 TASO 2: EXECUTION PLANNER (Suunnitelman järjestelmällinen suoritus)
*Käyttö: Kun Tason 1 `implementation_plan.md` on hyväksytty. Tämä komento asettaa tekoälyn "koodauskone"-tilaan, jossa se ajaa hyväksyttyä listaa vaihe vaiheelta eteenpäin ilman ylimääräisiä sivuaskelia.*

```text
Goal: Execute the approved `implementation_plan.md` step-by-step.

ROLE: Lead Developer (2026 Context - Phase 9 Hardening).
REFERENCE: `@docs/flutterpromptohje.md`.

INSTRUCTIONS (LEVEL 2):
1. ISOLATION: Execute the plan ATOMICALLY. Work on one single Milestone/Step at a time.
2. CONSTRAINTS: For every single step, enforce Strict Typing (`Pydantic` / `Freezed`) and the "Fail-Fast" doctrine (No `try-except pass`, use `AppException`).
3. DUAL-IMPLEMENTATION: If touching backend data, automatically update both TinyDB and Firestore repositories simultaneously.
4. QUALITY LOOP: Write the code and run verification tools (`ruff`, `mypy`, `dart analyze`).
5. CHECKPOINT: Mark the step COMPLETE in the markdown tasklist and explain shortly how the code follows the constraints for this single step. Wait for my permission ("JATKA") before proceeding to the next item on the plan.
```

---

### 🔴 TASO 3: YKSITTÄINEN OPERAATIO (Toteutus, tarkistelu ja ylläpito)
*Käyttö: Tilanteet, joissa muutetaan tai tehdään yksi ainoa feature, refaktoroidaan legacy-tiedosto, metsästetään virheitä ratkaisussa (debugaus) tai suoritetaan auditointeja/konfiguraatiomuutoksia. Taso 3 jakautuu lokeroihin (A, B, C, D) työn laadun perusteella, mutta toimii välittömän suorituksen logiikalla.*

#### 3A. FEATURE & REFACTOR (Yksittäinen toteutus tai siivous)
```text
Goal: [KIRJOITA TAVOITE TÄHÄN. Esim: "Tee uusi välilehti asetuksiin" TAI "Refaktoroi tiedosto X vastaamaan moderneja DTO-sääntöjä"]

OLE: Senior Developer (2026 Context).
INSTRUCTIONS (LEVEL 3A):
1. PLAN: Read related files. Create a quick execution plan containing specific `TARGET (Modify)` and `CONTEXT (Read-Only)` files.
2. FAIL-FAST: State where `AppException` will be raised if data is missing. Do not use fallbacks.
3. UI/UX: Output localized keys only via the API. Do not hardcode frontend strings.
4. EXECUTE & PAUSE: Present the root cause or execution plan, get confirmation ("LUPA MYÖNNETTY"), and write the code adhering strictly to `flutterpromptohje.md`.
>>>>```

#### 3B. BUG HUNTING & ROOT CAUSE ANALYSIS (Virheiden selvitys)
```text
Goal: [KIRJOITA BUGI TÄHÄN. Esim: "API heittää 500 erroria reitillä /profile"]

ROLE: Lead Security & Quality Auditor (2026 Context).
INSTRUCTIONS (LEVEL 3B):
1. IDENTIFY: Trace data flow to its origin. DO NOT patch symptoms. DO NOT add `if x is None: return []` or `try-except pass` just to silence errors.
2. EXPLAIN: Explain the Root Cause of the bug briefly in Finnish.
3. FIX: Propose an atomic code fix that forces the code back into the Pydantic V2 Strict / Fail-Fast paradigm. Wait for "LUPA MYÖNNETTY" before modifying files.
```

#### 3C. ZERO-SHORTCUT AUDIT (Tuomarointi ja koodin laadunvarmistus)
```text
Goal: Audit the newly written files: [KIRJOITA TIEDOSTOT DAAKERILLE, esim. /backend/api/router.py]

ROLE: Ruthless Code Reviewer (2026 Context).
INSTRUCTIONS (LEVEL 3C):
1. Review the provided targets aggressively against `@docs/flutterpromptohje.md` (Part 18).
2. Look strictly for: `try-except pass` blocks, silent `{}` returns masking data errors, naked `ValueError` raises, implicit domain defaults (like `score = 0.0`), and hardcoded localization strings in the backend.
3. REPORT: If ANY critical violation is discovered, refuse to pass the code. Fix them immediately using strict best practices.
```

#### 3D. SEED DATA VAULT PROTOCOL (C-tason konfiguraatiomuutokset)
```text
Goal: [KIRJOITA SIEMENDATAMUUTOS TÄHÄN. Esim: "Muuta mallin strategia 'precise' tilasta 'deep' SSOT-konfiguraatioon"]

ROLE: Registry Administrator (2026 Context).
INSTRUCTIONS (LEVEL 3D):
Modifying `backend/seed/seed_data.json` autonomously is STRICTLY BLOCKED without a safety net. You MUST follow these exact steps to prevent catastrophic ID corruption:
1. PROPOSE: Show me the exact JSON snippet you intend to modify. Wait for "LUPA MYÖNNETTY".
2. BACKUP: Run `cp backend/seed/seed_data.json backend/seed/seed_data.backup.json`.
3. SCRIPT: Create a dedicated Python script file (e.g. `modify_seed.py`) to perform the changes. 
   - 🚫 NEVER use inline terminal commands (like `python -c`) because PowerShell/Bash will silently expand variables like `$c1f...` and destroy the UUIDs.
   - 🚫 NEVER use string replacement or regex on the JSON file. 
   - ✅ ALWAYS use `json.load()` to parse the dict, mutate the Python dictionary intelligently, and `json.dump()` to save it.
   - 🚫 NEVER add undocumented "extra keys" or hallucinated data structures. Only add exactly what the Pydantic domain models define.
4. EXECUTE: Run your script: `python modify_seed.py`.
5. MATH VERIFY: Run a script that recursively counts all objects, lists, and keys in `seed_data.backup.json` vs `seed_data.json` and prints the exact mathematical difference. If the delta is larger than the exact number of keys you explicitly added, STOP. You hallucinated data.
6. DOMAIN VERIFY: You MUST run `pytest backend/tests/unit/test_seed_schema_alignment.py -v`. This test suite is the sovereign architectural guard. If it fails, your mutation corrupted the graph. Fix your script and try again.
7. REPORT: Confirm the mathematical delta matches expectations and tests pass.
8. SEED DATABASE: Aja komento `python backend/seed/run_seed.py local`. Tämä poistaa vanhan lokaalin tietokannan (`data/db.json`) ja rakentaa sen uudestaan juuri muokkaamastasi `seed_data.json` -tiedostosta, varmistaen että uusi arkkitehtuuri on heti käytettävissä kehitysympäristössä.
```

---

## 🚨 UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (Liitä AINA jokaiseen)

*(Kopioi tämä aina kaikkien Tason 1, 2 ja 3 promptien perään.)*

```text
*** UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (V5.1 - PHASE 9 HARDENING) ***

1. ANTI-HALLUCINATION & FILE SCOPING PROTOCOL:
   - Read-Before-Write: NEVER guess the contents of a file. Use your tools to read the current context before proposing modifications.
   - Explicit Scope: Only modify `TARGET` files. Treat `CONTEXT` files as Read-Only.

2. ARCHITECTURAL BANS (Non-Negotiable - Enforced by Strict Mandates):
   - You MUST adhere to `docs/STRICT MANDATES & ARCHITECTURE PRINCIPLES.md` and `docs/STRICT FRONTEND MANDATES & ARCHITECTURE PRINCIPLES.md`.
   - Backend: NO `try-except pass`. NO raw `dict` returns (Strict Pydantic V2 only). NO legacy `Depends` (Use `Annotated`). NO business logic in Routers. NO `HTTPException` (Use `AppException` & RFC 7807). No default values in domain models unless logically strictly necessary.
   - Frontend: NO `ChangeNotifier` or manual `Provider` (Riverpod 3.0 Generator ONLY). Routing MUST use `GoRouteData`. NO manual `if(isLoading)` checks (Use `.when()`). NO `Future.wait` monoliths for State.
   - L10N (No-String Policy): Backend MUST return Enum Keys (e.g., `AUTH_ORGANIC`). Raw UI strings are BANNED in Python APIs. Translations live exclusively in Frontend `.arb` files executing ICU formats. No manual string concatenation.

3. THE ZERO-COMPROMISE PLEDGE (Fail Fast & Root Cause):
   - If data is invalid or missing, crash immediately at the Service boundary. Do not return `None` or `{}` to silently bypass errors. Fix the root cause.
   - Exception: The BFF (Backend-For-Frontend) mapping layer MUST use graceful degradation (e.g., returning `{}` or `SizedBox.shrink()` on UI) for missing specialist data to prevent total UI crashes, but must log an explicit warning (`logger.warning(...)` / `debugPrint(...)`).
   - Dual-Reporting Python: Always log errors structurally (`logger.error`) BEFORE raising `AppException`.

4. EDITING SAFETY (Anti-Duplication Protocol):
   - When modifying a file, explicitly DELETE or OVERWRITE the old version. NEVER append the new version to the end of the file while leaving the old one intact.

5. DATA PARITY & OPTIMISTIC UI:
   - Backend: Any database repository change MUST be implemented in BOTH `repository.py` (TinyDB) and `firestore_repo.py` (Cloud) to maintain strict dual-backend parity.
   - Frontend: Implement Optimistic Updates for all mutations (update cache before network call, rollback if error).
   
6. OUTPUT FORMAT REQUIREMENTS:
   - Language Strategy: Antigravity Prompts / Code Blocks MUST be in English. Explanations/Context MUST be in Finnish.
   - Internal Comments (The "Why" Mandate): Only comment WHY business logic exists. Never explain WHAT the code mechanically does. Use Imperative Mood for docstrings.

7. QUALITY LOOP & TOOL USAGE (MANDATORY VERIFICATION):
   - Python: Run `ruff check <files> --fix` -> `mypy <files> --strict` -> `pytest`.
   - Flutter: Run `dart format` -> `dart analyze` -> `flutter test`.
   - Resolve ALL syntax and typing errors before declaring the step or ticket complete.
```