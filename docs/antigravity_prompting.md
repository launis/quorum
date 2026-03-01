# 🚀 Antigravity Prompting - Komentokeskus & Työkalupakki (V5.1 / Phase 9 Hardening)

> [!IMPORTANT]
> Tämä dokumentti on **Komentokeskus** ja absoluuttinen lakikirja Google Antigravity / Gemini -tekoälyn ohjaamiseen Cognitive Quorum -projektissa. 
> 
> Koska olemme **Phase 9 Hardening** -vaiheessa, tekoälyn tehtävä ei ole "koodata nopeasti", vaan tuottaa **100 % arkkitehtuurimanifestin mukaista, turvallista ja virheetöntä koodia**. Antigravityn on todistettava jokaisessa tehtävässä, että se ymmärtää rajoitteet ennen työn aloittamista *(Verification Check)*.

---

## 🎯 Käyttöohje: "1-Click" Copy-Paste Promptit

> [!TIP]
> Ohjaamisen pitää olla salamannopeaa ja turvallista. 
> Siksi kaikki projektin säännöt, roolit, tavoitteen laajuudet (Epic/Feature) ja arkkitehtuurin vaatimukset on nyt leivottu **suoraan näihin 5 työkaluun**.
> 
> **Käyttö on yksinkertaista:**
> 1. Valitse tarpeeseesi sopiva Työkalu (1–5) alta.
> 2. Kopioi harmaa koodilohko sellaisenaan.
> 3. Kirjoita `Goal:` -kohtaan tavoitteesi.
> 4. Syötä lohko ja Universal Mandate (liite sivun lopussa) tekoälylle. Valmista!

---

## 🛠️ Työkalupakki

### 🛠️ TYÖKALU 1: EPIC PLANNER *(Laajaan tavoitteeseen: esim. uusi tekoälyagentti, uusi moduuli tai iso arkkitehtuurimuutos)*
> [!NOTE]
> Käytä tätä, kun tavoite on suuri. Tämä estää tekoälyä hallusinoimasta ja pakottaa sen pilkkomaan työn turvallisiin virstanpylväisiin ENNEN koodausta. Tässä tilassa tekoäly **EI SAA** vielä kirjoittaa toteutussuunnitelmaa tai mitään koodia.

```text
Goal: [KIRJOITA LAAJA TAVOITE TÄHÄN. Esim: "Suunnittele ja toteuta uusi asiantuntijaprofiilien raportointimoduuli"]

ROLE: Senior Principal Solutions Architect & Antigravity Specialist (2026 Context - Phase 9 Hardening).
REFERENCE MATERIAL: 
- Primary Source of Truth: `@docs/flutterpromptohje.md` (Read this file first. It is absolute law).
- Map: `@docs/documentation_strategy.md` (Understand the hierarchy).

INSTRUCTIONS (EPIC MODE):
This is a large-scale objective. DO NOT write a code-level implementation plan yet. DO NOT write any code.
1. First, strictly read the architectural law: `@docs/flutterpromptohje.md`.
2. Create a high-level **Master Plan** that breaks this goal into 4-6 completely independent Milestones (Atomic Strikes).
3. Every phase must adhere strictly to the V5.1 architecture sequence (Backend Service/Repo -> Strict Pydantic -> API -> BFF -> Frontend Riverpod -> UI).
4. CRITICAL REQUIREMENT: For EVERY single Atomic Strike/Milestone you define in the Master Plan, you MUST explicitly write out a completely identical, full copy of the "UNIVERSAL MANDATE & CONSTRAINTS (V5.1 - PHASE 9 HARDENING)" block inside that milestone's description. Do not abbreviate it or reference it; print the whole text block exactly as it is attached below.
5. WAIT FOR APPROVAL: Present the Master Plan and wait for my explicit approval. Only after I say "LUPA MYÖNNETTY", you will generate the detailed Implementation Plan for the first step.

VERIFICATION CHECK:
To prove you have read and understood these strict instructions, start your response with the exact phrase: 
"VERIFICATION PASSED: I am in Epic Planning Mode. I will not generate code. I will explicitly embed the full Universal Mandate text into every single defined Atomic Strike."
```

### 🛠️ TYÖKALU 2: FEATURE EXECUTION *(Yksittäiseen muutokseen: esim. uusi asetusvälilehti, selkeä toteutus, tai Epic Plannerin hyväksytty askel 1)*
> [!NOTE]
> Käytä tätä yksittäisiin selkeisiin toteutuksiin tai asetusmuutoksiin. Tässä tilassa luodaan peräkkäinen Implementation Plan ja sen suoritus aloitetaan luvan saamisen jälkeen.

```text
Goal: [KIRJOITA TARKKA TAVOITE TÄHÄN. Esim: "Luo uusi asetusvälilehti asetukset-sivulle"]

ROLE: Lead Backend/Frontend Developer & Antigravity Specialist (2026 Context - Phase 9 Hardening).
REFERENCE MATERIAL: 
- Primary Source of Truth: `@docs/flutterpromptohje.md` (Read this file first. It is absolute law).
- Map: `@docs/documentation_strategy.md` (Understand the hierarchy).

INSTRUCTIONS (EXECUTION MODE):
Create a sequential execution plan (Implementation Plan) to implement this Goal, and then execute it strictly. Do not start coding before the plan is approved.
1. ANTI-HALLUCINATION PROTOCOL: Use your file search/read tools to read existing code BEFORE proposing changes. Never guess a function signature or imports. Every prompt/plan MUST explicitly list files in two strict categories: `TARGET (Modify)` and `CONTEXT (Read-Only)`.
2. EXPLICIT SCOPING: Your response MUST explicitly define which files are `TARGET (Modify)` and which are `CONTEXT (Read-Only)`.
3. FAIL-FAST ENFORCEMENT: Explicitly state where `AppException` (RFC 7807) will be raised if data is missing or invalid.
4. QUALITY LOOP: Before marking this step as done, you MUST verify the code (e.g., mentally trace types, ensure no raw dicts are returned, check Riverpod generators).
5. UX & L10N: Ensure Optimistic UI logic & Fail Fast Retries. Do NOT hardcode strings for UI; use `LocalizationService.translate("KEY")` tied to Pydantic `x-ui-label` defaults and Frontend `app_{lang}.arb` localized responses.

VERIFICATION CHECK:
Before outputting any code, start your response with: 
"VERIFICATION PASSED: I am in Feature Execution Mode. I will adhere strictly to the Universal Mandates and proceed with creating the Implementation Plan." 
Then, list the `TARGET` and `CONTEXT` files explicitly, and write one sentence explaining how your planned code respects the "Fail-Fast" boundary for this specific task.
```

### 🛠️ TYÖKALU 3: BUG HUNTING & ROOT CAUSE ANALYSIS *(Virheiden purkamiseen ja selittämättömien bugien metsästykseen)*
> [!WARNING]
> Käytä tätä bugien korjaamiseen tai UI:n virhetilanteiden selvittämiseen. Estää vaaralliset "purkkakorjaukset".

```text
Goal: [KIRJOITA ONGELMA TAI LOKI TÄHÄN. Esim: "Backend-reitti /api/profile heittää 500 Internal Server Erroria tallennettaessa, tutki ja korjaa juurisyyt"]

ROLE: Lead Security & Quality Auditor (2026 Context - Phase 9 Hardening).
REFERENCE MATERIAL: 
- Primary Source of Truth: `@docs/flutterpromptohje.md` (Read this file first. It is absolute law).

INSTRUCTIONS (AUDIT MODE):
Act as an aggressive auditor. Your goal is to find the ROOT CAUSE of the issue.
1. DO NOT patch symptoms. You are STRICTLY FORBIDDEN from adding `if x is None: return []`, `.get('field', default)`, or `try-except pass` just to silence the error in Core Logic.
2. Trace the data flow back to its origin. Find where the data contract was broken (e.g., LLM hallucination, missing validation).
3. Explain the Root Cause to me briefly in Finnish before proposing the code fix.
4. Propose a fix that forces the system to comply with strict typing (Pydantic V2) and Fail-Fast error handling (`AppException`).

VERIFICATION CHECK:
Start your response exactly with: 
"VERIFICATION PASSED: I am in Bug Hunting Mode. I swear I will not use try-except pass or defensive null-returns to hide this error. I will trace the data back to its origin."
```

### 🛠️ TYÖKALU 4: THE SEED DATA VAULT *(Tietokannan siemendatan suojattu muokkaus)*
> [!CAUTION]
> **KRIITTINEN TURVATYÖKALU.** Käytä tätä VAIN JA AINOASTAAN silloin, kun on pakko muokata `backend/seed/seed_data.json` -tiedostoa.

```text
Goal: [KIRJOITA SEED-DATAN MUUTOS TÄHÄN. Esim: "Lisää uusi tekoälyagentti 'step_optimizer' steps-listaan ja kytke se 'main_workflow' -ketjuun"]

ROLE: Database Administrator & Registry Guardian (2026 Context - Phase 9 Hardening).

INSTRUCTIONS (VAULT PROTOCOL):
The file `backend/seed/seed_data.json` is the Single Source of Truth (SSOT). Modifying it autonomously without a safety net is STRICTLY BLOCKED.
You MUST follow this exact 5-step sequence using your terminal/bash tools:
1. PROPOSE & PAUSE: Show me the exact JSON snippet you intend to add/modify. Wait for my reply: "LUPA MYÖNNETTY". Do not touch the file yet.
2. BACKUP: (Once approved) Run a bash command to copy the file: `cp backend/seed/seed_data.json backend/seed/seed_data.backup.json`.
3. MODIFY: Use python/bash to inject the approved changes carefully into the original file.
4. VERIFY: Run `diff backend/seed/seed_data.backup.json backend/seed/seed_data.json`.
5. REPORT: Show me the output of the diff. Explicitly confirm that NO other workflows, translations, or system IDs were accidentally deleted, overwritten, or hallucinated.

VERIFICATION CHECK:
Before doing anything, start your response with: 
"VERIFICATION PASSED: I am in Vault Protocol Mode." 
Then explicitly write out the exact bash `cp` and `diff` commands you plan to use in Steps 2 and 4.
```

### 🛠️ TYÖKALU 5: ZERO-SHORTCUT AUDIT *(Koodin tuomarointi Session lopuksi)*
> [!IMPORTANT]
> Käytä tätä laajan koodaussession päätteeksi ennen koodin lukitsemista. Pakottaa tekoälyn auditoimaan oman työnsä laadun.

```text
Goal: [KIRJOITA TARKASTETTAVAT TIEDOSTOT TÄHÄN. Esim: "Auditoi äsken muokatut tiedostot: backend/services/auth.py ja client_app/lib/ui/auth_view.dart"]

ROLE: Ruthless Code Reviewer & Architecture Dictator (2026 Context - Phase 9 Hardening).
REFERENCE MATERIAL: 
- Primary Source of Truth: `@docs/flutterpromptohje.md` (Specifically Part 18: The Zero-Compromise Pledge).

INSTRUCTIONS (POST-EXECUTION AUDIT):
1. Step out of the "developer" role and become a strict Code Auditor. Audit the specified files exclusively against the rules in `@docs/flutterpromptohje.md`.
2. Search aggressively for these CRITICAL VIOLATIONS:
   - Any `try-except pass` blocks or silent `None` / `{}` returns meant to suppress errors.
   - Naked `ValueError` or `Exception` raises (Must be structured `AppException` / RFC 7807).
   - Implicit defaults in Domain models (e.g. `score = 0.0`).
   - Hardcoded raw strings in Python instead of returning Enum Keys (e.g. `STATUS_ACTIVE`).
   - Missing Optimistic UI updates or raw text strings in Flutter instead of `.arb` localizations.
3. If you find ANY violations, DO NOT just warn me. Refactor them immediately to meet the Phase 9 Hardening standards and explain what you fixed.

VERIFICATION CHECK:
Start your response with: 
"VERIFICATION PASSED: I am in Ruthless Auditor Mode." 
Then explicitly list the 5 CRITICAL VIOLATIONS mentioned above to prove you are actively scanning for them.
```

---

## 🚨 UNIVERSAL MANDATE & CONSTRAINTS (Liitä AINA jokaisen promptin loppuun)

*(Tämä on tekoälyn "perustuslaki". Kopioi tämä tekstilohko AINA kokoelmana valitsemasi työkalun perään samaan viestiin. Jos annoit ohjeeksi Epic Planner (Työkalu 1), tekoäly joutuu itse myös ylläpitämään ja liittämään tämän tekstin jokaisen virstanpylväänsä ja atomic strikesi -lokeron alle).*

```text
*** UNIVERSAL MANDATE & CONSTRAINTS (V5.1 - PHASE 9 HARDENING) ***

1. ANTI-HALLUCINATION & FILE SCOPING PROTOCOL:
   - Read-Before-Write: NEVER guess the contents of a file. Use your tools to read the current context before proposing modifications.
   - Explicit Scope: Only modify `TARGET` files. Treat `CONTEXT` files as Read-Only. If you need to see a file not in context, ask to read it first.

2. THE SEED DATA VAULT PROTOCOL (CRITICAL SAFETY):
   - Modifying `backend/seed/seed_data.json` autonomously is STRICTLY BLOCKED.
   - Requires explicit Backup (`cp`) -> Modify -> Verify (`diff`) loop.

3. ARCHITECTURAL BANS (Non-Negotiable):
   - Backend: NO `try-except pass`. NO raw `dict` returns (Strict Pydantic V2 only). NO legacy `Depends` (Use `Annotated`). NO business logic in Routers. NO `HTTPException` (Use `AppException` & RFC 7807).
   - Frontend: NO `ChangeNotifier` or manual `Provider` (Riverpod 3.0 Generator ONLY). Routing MUST use `GoRouteData`.
   - L10N (No-String Policy): Backend MUST return Enum Keys (e.g., `AUTH_ORGANIC`). Raw UI strings are BANNED in Python APIs. Translations live exclusively in Frontend `.arb` files using ICU formats.

4. THE ZERO-COMPROMISE PLEDGE (Fail Fast):
   - If data is invalid or missing, crash immediately at the Service boundary. Do not return `None` or `{}` to silently bypass errors. Fix the root cause. No implicit default values in domain models.

5. EDITING SAFETY (Anti-Duplication Protocol):
   - When modifying a function/class, explicitly DELETE or OVERWRITE the old version. NEVER append the new version to the end of the file while leaving the old one intact. Ensure strict string replacement.

6. DATA PARITY:
   - Any database repository change MUST be implemented in BOTH `repository.py` (TinyDB) and `firestore_repo.py` (Cloud) to maintain strict dual-backend parity.
   
7. OUTPUT FORMAT REQUIREMENTS:
   - Language Strategy: Antigravity Prompts (Code Blocks) MUST be in English. Your Explanations/Context MUST be in Finnish (Suomi).
   - Granularity (Atomic Strikes): Break the task into small, isolated prompts (approx. 5-10 mins of AI work each). Standard Sequence: Backend Dependencies -> Backend Core/Models -> Backend L10n -> Backend Repositories -> Backend API/Router -> Frontend Models -> Frontend Controller -> Frontend UI.
```