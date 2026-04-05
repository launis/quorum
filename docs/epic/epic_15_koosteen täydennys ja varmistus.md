# ---

**🚀 EPIC: Antigravity Framework V6.0 "Agentic Shield"**

## **📝 Yhteenveto (Executive Summary)**

Tämä Epic kokoaa kaikki 2026-tason arkkitehtuuripäivitykset. Tavoitteena on siirtää Antigravity passiivisesta ohjeistuksesta **itseään korjaavaksi, deterministiseksi agenttijärjestelmäksi**.

Tässä dokumentissa on käyty läpi **aivan jokainen** alkuperäisessä syötteessä annettu dokumentti ja työnkulku. Jokaiselle on määritetty konkreettiset toimenpiteet ja koodiesimerkit.

## ---

**📍 MILESTONE 1: Työnkulkujen Karkaisu (AI Tiers 1-5)**

*Kohde: Kaikki Tier 1-5 XML-promptit.*

*Tavoite: Poistaa Windows-sidonnaisuus, estää sokea suunnittelu ja asentaa 100% varma "Clean Room" \-kontekstivaihto.*

### **1.1 Polku-sanitaatio ja Rutiinityönkulut (Tiers 2 & 3\)**

Kaikista prompteista (myös Tier 2 Audit ja Tier 3\) vaihdetaan absoluuttinen polku c:\\src\\quorum\\.agents\\rules\\... suhteelliseksi .agents/rules/.... Tämän lisäksi Tier 2:een lisätään maininta uudesta "Circuit Breaker" \-sulakkeesta.

### **1.2 Tier 1 (Epic Planner) & Tier 4 (Bug Hunting) Kognitiiviset Lukot**

Lisää nämä askeleet työnkulkujen \<execution\_protocol\> \-lohkoihin:

XML

\<step id\="1.5"\>DISCOVER (CRITICAL): Actively use your file reading/listing tools to scan the relevant \`TARGET\` directories BEFORE writing the plan. Never hallucinate the current architectural state.\</step\>

\<step id\="1"\>INGEST LOGS: Before modifying anything, actively read \`backend\_debug.log\` or \`client\_debug.log\`, OR ask the user for the stack trace.\</step\>  
\<step id\="2.5"\>PROOF OF FAILURE: PAUSE HERE. Instruct the user to run the test. You MUST WAIT for the user to paste the raw failing test trace output. Do not guess the root cause without seeing the actual error logs.\</step\>

### **1.3 Tier 5 Jakaminen: Sender (Poistuminen) & Receiver (Herätys)**

Korvaa vanha Tier 5 kokonaan näillä kahdella erillisellä työnkululla.

**TIER 5 SENDER (Viestikapulan pakkaus nykyisessä ikkunassa):**

XML

\---  
description: Tier 5 (Session Handover Export) \- Packages the current state into an atomic git commit and a transfer payload for a clean window.  
\---  
\#\#\# 🟠 TIER 5: SESSION HANDOVER EXPORT (Context Transition & Baton Pass)  
\<system\_prompt\>  
  \<objective\>Generate a frictionless context-transition package. Create a copy-pasteable block containing atomic Git commands and the \`/tier5-resume\` command for a NEW chat window.\</objective\>  
  \<role\>Context Archiver & CI/CD Orchestrator\</role\>  
  \<execution\_protocol\>  
    \<step id\="1"\>Scan the entire current session. Identify ALL production files (\`.py\`, \`.dart\`) and test files (\`test\_\*.py\`, \`\*\_test.dart\`) modified.\</step\>  
    \<step id\="2"\>Filter OUT \`.md\` guides, \`.json\` DB files, logs, and scratchpads.\</step\>  
    \<step id\="3"\>Summarize the achieved business logic in one English sentence (\`--done\`). Deduce the logical NEXT step (\`--next\`).\</step\>  
    \<step id\="4"\>Output exactly this Markdown bash block:  
\`\`\`bash  
\# 1\. ATOMIC GIT SAVE (Tallenna työsi)  
git add \[file\_path\_1\] \[test\_path\_1\]  
git commit \-m "feat: \[brief description\]"

\# 2\. HANDOVER COMMAND (Kopioi tämä, SULJE chat, avaa UUSI chat ja liimaa)  
/tier5-resume \[file\_path\_1\] \[test\_path\_1\] \--done="\[Your summary\]" \--next="\[What to do next\]"

\</step\>

\</execution\_protocol\>

\</system\_prompt\>

\*\*TIER 5 RECEIVER (Kontekstin purku uudessa ikkunassa):\*\*  
\`\`\`xml  
\---  
description: Tier 5 (Resume & Audit) \- The receiving end of the handover protocol.  
\---  
\#\#\# 🟠 TIER 5: RESUME & ZERO-SHORTCUT AUDIT  
\<system\_prompt\>  
  \<objective\>Receive the handover payload, rigidly audit the transferred files against architecture constraints, and prepare for \`--next\`.\</objective\>  
  \<role\>Ruthless Code Reviewer & Execution Planner\</role\>  
  \<context\_rules\>ALWAYS read \`.agents/rules/00-antigravity-core.md\`. Dynamically load domain rules based on file extensions.\</context\_rules\>  
  \<execution\_protocol level="5"\>  
    \<step id="1"\>INGEST: Actively use tools to read the files passed. Read \`--done\` context. Acknowledge \`--next\` goal.\</step\>  
    \<step id="2"\>AUDIT (RUTHLESS): Review strictly for: \`try-except pass\` blocks, naked Dicts, silent fallbacks, and missing Freezed/Pydantic strictness.\</step\>  
    \<step id="3"\>TESTING MANDATE CHECK: Verify if handover included unit tests. Fail immediately if core logic lacks tests.\</step\>  
    \<step id="4"\>REPORT: IF FAILS: Refuse handover, propose fixes. IF PASSES: State "Audit läpäisty. Konteksti ladattu." and outline execution of \`--next\`. Wait for PROCEED.\</step\>  
  \</execution\_protocol\>  
\</system\_prompt\>

## ---

**🧠 MILESTONE 2: Pääsäännöt (00-antigravity-core.md)**

*Kohde: .agents/rules/00-antigravity-core.md*

*Tavoite: Agentin psykologian hallinta, ikuisten luuppien esto ja "Shift-Left" testauksen pakottaminen.*

Lisää nämä uudet lohkot asianmukaisiin kohtiin:

XML

\<rule\_block id\="mandatory\_chain\_of\_thought"\>  
    \<banned\_pattern\>Outputting code blocks or executing file-write tools immediately after receiving a user prompt.\</banned\_pattern\>  
    \<mandatory\_pattern\>You MUST wrap your architectural thinking inside \`\<thinking\_process\>\` XML tags BEFORE writing any code. State: 1\) Rules applied, 2\) Root cause, 3\) Execution plan.\</mandatory\_pattern\>  
\</rule\_block\>

\<rule\_block id\="surgical\_precision\_edits"\>  
    \<banned\_pattern\>Using lazy placeholders like \`// ... rest of the file ...\` when outputting code.\</banned\_pattern\>  
    \<mandatory\_pattern\>You MUST be surgical. Truncation is an act of data destruction. Provide the ENTIRE compilable structural block or use precise search-and-replace tools.\</mandatory\_pattern\>  
\</rule\_block\>

\<rule\_block id\="circuit\_breaker\_protocol"\>  
    \<banned\_pattern\>Attempting to autonomously fix the exact same Pytest or Flutter error more than 3 times iteratively.\</banned\_pattern\>  
    \<mandatory\_pattern\>Implement the "Rule of Three". If failing 3 times, you MUST STOP. Output \`\<circuit\_breaker\_tripped\>\`, explain the paradox, and WAIT for human guidance.\</mandatory\_pattern\>  
\</rule\_block\>

\<rule\_block id\="dependency\_hallucination\_firewall"\>  
    \<banned\_pattern\>Autonomously proposing new third-party packages to \`pubspec.yaml\` or \`uv.lock\`.\</banned\_pattern\>  
    \<mandatory\_pattern\>Zero-Trust dependency environment. Solve problems using natively installed tools. If an external library is mathematically necessary, wait for "PERMISSION GRANTED".\</mandatory\_pattern\>  
\</rule\_block\>

\<rule\_block id\="deterministic\_testing\_delegation"\>  
    \<banned\_pattern\>Writing manual JSON dictionary mock data or claiming "Tests are complete" without passing Coverage.\</banned\_pattern\>  
    \<mandatory\_pattern\>You are the worker, Python is the judge. 1\) Use \`polyfactory\` for mock data. 2\) The \`conftest.py\` blocks networks, use MonkeyPatch for external calls. 3\) The \`backend\_audit\_loop.py\` enforces \>90% coverage. Analyze the \`Miss\` column if it fails.\</mandatory\_pattern\>  
\</rule\_block\>

## ---

**🧪 MILESTONE 3: Deterministinen Python-Testausinfrastruktuuri**

*Kohde: Uudet fyysiset tiedostot työtilaan.*

*Tavoite: Ottaa tekoälyltä fyysisesti pois mahdollisuus huijata testauksessa.*

**1\. Verkkolukko (backend\_v2/tests/conftest.py):**

Python

import pytest  
import socket

@pytest.fixture(autouse=True)  
def block\_live\_network\_calls(monkeypatch):  
    """KRIITTINEN ILMARAKO: Estää verkkokutsut yksikkötesteissä."""  
    def guarded\_getaddrinfo(\*args, \*\*kwargs):  
        raise RuntimeError("🛑 FATAL TEST FAILURE: Yritit tehdä oikean verkkokutsun testin aikana\! Käytä mock\_data.py.")  
    monkeypatch.setattr(socket, "getaddrinfo", guarded\_getaddrinfo)

**2\. Polyfactory Mocking (backend\_v2/tests/factories.py):**

Python

from polyfactory.factories.pydantic\_factory import ModelFactory  
from backend\_v2.models.user import UserDTO \# HUOM: Käytä oikeaa malliasi

class UserFactory(ModelFactory\[UserDTO\]):  
    \_\_model\_\_ \= UserDTO

**3\. Arkkitehtuurivalvonta (backend\_v2/tests/architecture/test\_boundaries.py):**

Python

from pytest\_archon import archrule

def test\_routers\_cannot\_import\_database\_directly():  
    (  
        archrule("Anemic Routers Rule: No DB in Routers")  
        .match("backend\_v2.api.routers.\*")  
        .should\_not\_import("backend\_v2.database.\*")  
        .check("backend\_v2")  
    )

**4\. Coverage-lukko (Päivitä olemassa oleva scripts/backend\_audit\_loop.py):**

Python

import subprocess, sys

def run\_tests\_with\_strict\_coverage(target):  
    print("🚀 Verifying Strict TDD Coverage...")  
    cmd \= \["uv", "run", "pytest", f"--cov={target}", "--cov-fail-under=90", "--cov-report=term-missing"\]  
    result \= subprocess.run(cmd, capture\_output=True, text=True)  
    if result.returncode \!= 0:  
        print("❌ AUDIT FAILED: TDD Mandate Violation. Coverage \< 90%.")  
        print("🤖 AI INSTRUCTION: Lue alla oleva raportti (Miss-sarake) ja kirjoita testit puuttuville riveille:\\n", result.stdout)  
        sys.exit(1)

## ---

**🐍 MILESTONE 4: Backend Arkkitehtuuri (01-python-backend.md)**

*Kohde: .agents/rules/01-python-backend.md*

*Tavoite: ORM-vuotojen tukkiminen ja esimerkkien tuominen sääntöihin.*

XML

\<rule\_block id\="zero\_orm\_bleed"\>  
    \<banned\_pattern\>Returning raw DB dictionaries directly from Repository to API routers.\</banned\_pattern\>  
    \<mandatory\_pattern\>The Repository layer is an absolute firewall. Raw records MUST be mapped into strict Pydantic Domain Models (\`ConfigDict(frozen=True)\`).\</mandatory\_pattern\>  
    \<code\_example\>  
        \<anti\_pattern\>return db.table('users').get(doc\_id=1)\</anti\_pattern\>  
        \<pro\_pattern\>return UserDTO.model\_validate(raw\[0\])\</pro\_pattern\>  
    \</code\_example\>  
\</rule\_block\>

\<rule\_block id\="strict\_dependency\_injection"\>  
    \<banned\_pattern\>Instantiating services or databases directly inside FastAPI routers.\</banned\_pattern\>  
    \<mandatory\_pattern\>Dependencies MUST be injected exclusively via FastAPI's \`Depends()\` \+ PEP 593 \`Annotated\`.\</mandatory\_pattern\>  
    \<code\_example\>  
        \<anti\_pattern\>service \= UserService()\</anti\_pattern\>  
        \<pro\_pattern\>  
            DatabaseSession \= Annotated\[Session, Depends(get\_database)\]  
            async def route(db: DatabaseSession): ...  
        \</pro\_pattern\>  
    \</code\_example\>  
\</rule\_block\>

\<rule\_block id\="pydantic\_native\_field\_priority"\>  
    \<banned\_pattern\>Using \`@field\_validator\` for simple bounds checking or regex.\</banned\_pattern\>  
    \<mandatory\_pattern\>ALWAYS prefer native \`Field(ge=0, pattern=...)\`. Native Field is executed in Rust (pydantic-core) at lightning speed.\</mandatory\_pattern\>  
    \<code\_example\>  
        \<anti\_pattern\>@field\_validator('age') ... if v \< 18: raise ValueError()\</anti\_pattern\>  
        \<pro\_pattern\>age: int \= Field(ge=18)\</pro\_pattern\>  
    \</code\_example\>  
\</rule\_block\>

## ---

**📱 MILESTONE 5: Frontend Arkkitehtuuri (02\_flutter\_desktop.md)**

*Kohde: .agents/rules/02\_flutter\_desktop.md*

*Tavoite: Työpöytäkäytettävyys, teeman pakotus ja muistivuotojen esto.*

XML

\<rule\_block id\="riverpod\_read\_vs\_watch\_ban"\>  
    \<banned\_pattern\>Using \`ref.read\` inside \`build()\`, or \`ref.watch\` inside callbacks.\</banned\_pattern\>  
    \<mandatory\_pattern\>Inside \`build()\`, use ONLY \`ref.watch(provider)\`. \`ref.read\` is strictly reserved for one-time execution inside event callbacks (\`onPressed\`).\</mandatory\_pattern\>  
    \<code\_example\>  
        \<anti\_pattern\>Widget build() { final x \= ref.read(prov); onPressed: () \=\> ref.watch(prov); }\</anti\_pattern\>  
        \<pro\_pattern\>Widget build() { final x \= ref.watch(prov); onPressed: () \=\> ref.read(prov); }\</pro\_pattern\>  
    \</code\_example\>  
\</rule\_block\>

\<rule\_block id\="desktop\_pro\_tool\_interaction"\>  
    \<banned\_pattern\>Raw \`GestureDetector\` without hover states, missing \`FocusNode\`, or lacking keyboard shortcuts.\</banned\_pattern\>  
    \<mandatory\_pattern\>This is a Desktop-Class Pro Tool. ALL interactive elements MUST support mouse hover (\`SystemMouseCursors.click\`), keyboard traversal (\`FocusNode\`), and \`Shortcuts\` actions.\</mandatory\_pattern\>  
\</rule\_block\>

\<rule\_block id\="design\_token\_absolute\_rule"\>  
    \<banned\_pattern\>Hardcoding magic numbers (\`EdgeInsets.all(16)\`) or colors (\`Colors.blue\`).\</banned\_pattern\>  
    \<mandatory\_pattern\>Exclusively use global Design Tokens (e.g., \`AppSpacing.p16\`, \`Theme.of(context).textTheme\`).\</mandatory\_pattern\>  
\</rule\_block\>

\<rule\_block id\="freezed\_when\_ban"\>  
    \<banned\_pattern\>Using Freezed \`.when()\`, \`.map()\`, or manual \`if-else\` chains.\</banned\_pattern\>  
    \<mandatory\_pattern\>ALWAYS use Dart 3 native \`switch\` expressions (pattern matching destructuring).\</mandatory\_pattern\>  
    \<code\_example\>  
        \<anti\_pattern\>return state.when(data: (v) \=\> Text(v), loading: () \=\> Spinner());\</anti\_pattern\>  
        \<pro\_pattern\>return switch (state) { AsyncData(:final value) \=\> Text(value), AsyncLoading() \=\> const Spinner() };\</pro\_pattern\>  
    \</code\_example\>  
\</rule\_block\>

## ---

**🤖 MILESTONE 6: LLM Arkkitehtuuri (05\_llm\_architecture.md)**

*Kohde: .agents/rules/05\_llm\_architecture.md*

*Tavoite: Kustannusoptimointi ja Langchain-bloatin estäminen.*

XML

\<rule\_block id\="ai\_bloatware\_ban"\>  
    \<banned\_pattern\>Proposing frameworks like \`langchain\`, \`llamaindex\`, or \`crewai\`.\</banned\_pattern\>  
    \<mandatory\_pattern\>AI logic MUST remain strictly in our native \`LLMClient\` wrapper. Complex orchestrations MUST use Python async patterns and Pydantic.\</mandatory\_pattern\>  
\</rule\_block\>

\<rule\_block id\="ephemeral\_caching\_topology"\>  
    \<banned\_pattern\>Injecting dynamic variables (timestamps, UUIDs) into \`\_SYSTEM\_INSTRUCTION\`.\</banned\_pattern\>  
    \<mandatory\_pattern\>To maximize Context Caching (FinOps), the System Prompt MUST be 100% static. ALL dynamic data MUST be injected exclusively into the \`user\` message at the end.\</mandatory\_pattern\>  
\</rule\_block\>

\<rule\_block id\="role\_segregation\_and\_fencing"\>  
    \<banned\_pattern\>Passing unescaped user inputs directly into prompts.\</banned\_pattern\>  
    \<mandatory\_pattern\>You MUST fence untrusted user payloads inside explicit XML tags (e.g., \`\<user\_payload\>...\</user\_payload\>\`) as a firewall against Prompt Injection.\</mandatory\_pattern\>  
    \<code\_example\>  
        \<anti\_pattern\>{"role": "user", "content": f"Parse this: {user\_text}"}\</anti\_pattern\>  
        \<pro\_pattern\>{"role": "user", "content": f"Data:\\n\<user\_payload\>\\n{user\_text}\\n\</user\_payload\>"}\</pro\_pattern\>  
    \</code\_example\>  
\</rule\_block\>

\<rule\_block id\="llm\_structured\_execution\_mandate"\>  
    \<banned\_pattern\>Asking LLM to "output valid JSON" in text and parsing it with Regex/json.loads.\</banned\_pattern\>  
    \<mandatory\_pattern\>Rely ONLY on \`run\_structured\_task()\` to force execution via API native Structural Constraining (e.g. OpenAI Structured Outputs).\</mandatory\_pattern\>  
    \<code\_example\>  
        \<anti\_pattern\>data \= json.loads(await client.run\_chat(prompt))\</anti\_pattern\>  
        \<pro\_pattern\>result: UserDTO \= await client.run\_structured\_task(messages, response\_model=UserDTO)\</pro\_pattern\>  
    \</code\_example\>  
\</rule\_block\>

\<rule\_block id\="hybrid\_prompting\_mandate"\>  
    \<banned\_pattern\>Writing flat, unstructured strings for system prompts.\</banned\_pattern\>  
    \<mandatory\_pattern\>All system prompts MUST use "Hybrid Prompting" (XML tags inside Markdown) to define semantic boundaries.\</mandatory\_pattern\>  
    \<code\_example\>  
        \<pro\_pattern\>  
            \_SYSTEM \= """\<system\_directive\>  
            \<objective\>Extract data\</objective\>  
            \<rules\>\<rule\>Be exact.\</rule\>\</rules\>  
            \</system\_directive\>"""  
        \</pro\_pattern\>  
    \</code\_example\>  
\</rule\_block\>

## ---

**🗄️ MILESTONE 7: Seed Data Vault Protocol (03\_seed\_vault.md)**

*Kohde: .agents/rules/03\_seed\_vault.md*

*Tavoite: Varmistetaan, että tekoälyllä on selkeät esimerkit siitä, miten Seed-dataa muokataan turvallisesti rikkomatta JSON-syntaksia tai Stripe-ID formaattia.*

Päivitä nykyiset säännöt koodiesimerkeillä:

XML

\<rule\_block id\="inline\_terminal\_scripting"\>  
    \<banned\_pattern\>Using one-liner terminal commands (\`python \-c\`, \`sed\`) or PowerShell variable expansion to modify JSON data.\</banned\_pattern\>  
    \<mandatory\_pattern\>ALWAYS create a dedicated \`modify\_seed.py\` script. You MUST strictly use \`json.load()\` and \`json.dump(..., indent=2)\` to guarantee file structure integrity.\</mandatory\_pattern\>  
    \<code\_example\>  
        \<anti\_pattern\>run\_command("sed \-i 's/old\_id/new\_id/g' backend\_v2/seed/seed\_data.json")\</anti\_pattern\>  
        \<pro\_pattern\>  
            \# modify\_seed.py  
            import json  
            with open('backend\_v2/seed/seed\_data.json', 'r') as f: data \= json.load(f)  
            data\['users'\]\[0\]\['id'\] \= "usr\_abc123"  
            with open('backend\_v2/seed/seed\_data.json', 'w') as f: json.dump(data, f, indent=2)  
        \</pro\_pattern\>  
    \</code\_example\>  
\</rule\_block\>

\<rule\_block id\="hallucinated\_data\_keys"\>  
    \<banned\_pattern\>Inventing extra JSON keys not strictly defined in Pydantic models, or using human-readable IDs like \`id: "new\_user\_1"\`.\</banned\_pattern\>  
    \<mandatory\_pattern\>All generated IDs MUST strictly follow the Opaque Stripe ID pattern (e.g. \`usr\_x8f9a2b1\`). No semantic strings allowed.\</mandatory\_pattern\>  
    \<code\_example\>  
        \<anti\_pattern\>{ "id": "admin\_user", "email": "test@test.com" } \# FATAL: Invalid ID\</anti\_pattern\>  
        \<pro\_pattern\>{ "id": "usr\_x8f9a2b1", "email": "test@test.com" } \# STRICT ALIGNMENT\</pro\_pattern\>  
    \</code\_example\>  
\</rule\_block\>

## ---

**🗺️ MILESTONE 8: Hakemistorakenne (04\_repository\_directory.md)**

*Kohde: Säännöissä olevan hakemistokartan päivitys*

*Tavoite: Hakemistoviitteiden päivitys heijastamaan uutta testausinfrastruktuuria ja poistamaan C:\\src\\... sidonnaisuudet.*

**Päivitykset dokumenttiin:**

1. Varmista, että mikään polku dokumentissa ei ala tekstillä C:\\src\\.... Kaikkien polkujen tulee olla työtilan juuresta alkavia.  
2. Lisää Python-testausinfrastruktuuri dokumentaatioon \<layer id="backend"\> \-osion sisälle:

XML

        \<directory path\="tests/"\>  
            \<description\>Deterministinen Shift-Left testausinfrastruktuuri.\</description\>  
            \<file\_rules\>  
                \<file path\="conftest.py"\>Sisältää verkkolukon (Airgap), joka estää oikeat API-kutsut testeissä.\</file\>  
                \<file path\="factories.py"\>Polyfactory-luokat, jotka generoivat mock-dataa automaattisesti Pydantic-malleista.\</file\>  
            \</file\_rules\>  
            \<directory path\="architecture/"\>Sisältää pytest-archon säännöt, jotka estävät vääriä importteja (esim. Routers \-\> DB).\</directory\>  
        \</directory\>

## ---

**✅ VERIFIOINTI (Kaikki syötteet käsitelty)**

| Alkuperäinen dokumentti / Syöte | Käsitelty Epicissä? | Sijainti |
| :---- | :---- | :---- |
| **00-antigravity-core.md** | Kyllä | Milestone 2 |
| **01-python-backend.md** | Kyllä | Milestone 4 |
| **02\_flutter\_desktop.md** | Kyllä | Milestone 5 |
| **03\_seed\_vault.md** | Kyllä | Milestone 7 *(Lisätty\!)* |
| **Hakemistokartta / 04\_directory** | Kyllä | Milestone 8 *(Lisätty\!)* |
| **05\_llm\_architecture.md** | Kyllä | Milestone 6 |
| **Tiers 1-5 (Agent Workflows)** | Kyllä | Milestone 1 |
| **Uusi Testausinfrastruktuuri** | Kyllä | Milestone 3 |

Nyt järjestelmäsi arkkitehtuuri on **100 % kattava**. Yksikään alun perin antamasi rivi koodia tai sääntöä ei jäänyt ilman laatuporttia. Voit tallentaa tämän suoraan työtilaasi ja käskeä tekoälyä toteuttamaan sen.