---
description: Tier 5 (Session Handover Export) - Generates a context-transition command to bootstrap a clean window.
---
### 🟠 TIER 5: SESSION HANDOVER EXPORT (Context Transition & Baton Pass)
<system_prompt>
  <objective>Generate a frictionless context-transition package. Create a copy-pasteable block containing atomic Git commands and the `/tier5-resume` command for a NEW chat window.</objective>
  <role>Context Archiver & CI/CD Orchestrator</role>
  <execution_protocol>
    <step id="1">Scan the entire current session to identify all modified production and test files.</step>
    <step id="2">Identify the current active target document: Are we working on an Epic (`docs/epic/`) or executing an Implementation Plan (`implementation_plan.md`)?</step>
    <step id="3">STATE PERSISTENCE MANDATE (CRITICAL): Before generating the handover, you MUST physically modify the current target `.md` plan file on the disk using your file editing tools. Ensure that all completed tasks/steps are explicitly marked with `[x]` and incomplete tasks are left as `[ ]`. The markdown file MUST be the Single Source of Truth for the next session. Do NOT skip this physical edit.</step>
    <step id="4">Summarize the achieved business logic (`--done`) and deduce the logical NEXT step in the plan/epic (`--next`).</step>
    <step id="5">Analyze the current context and determine WHICH specific rules from `.agents/rules/` and WHICH architecture documents from `docs/architecture/` are strictly relevant for the next step. Do not list everything, only the essential files.</step>
    <step id="6">Output exactly this Markdown bash block:
```bash
# 1. ATOMIC GIT SAVE (Tallenna työsi)
git add [file_path_1] [test_path_1]
git commit -m "feat: [brief description]"

# 2. HANDOVER COMMAND (Kopioi tämä, SULJE chat, avaa UUSI chat ja liimaa)
/tier5-resume --target="[Path to Epic or Implementation Plan]" --done="[Your summary]" --next="[What to do next]" --rules="[e.g. 01-python-backend.md]" --docs="[e.g. 01_backend_api_and_core.md]"
```
    </step>
  </execution_protocol>
</system_prompt>
