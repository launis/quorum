
import re
import json
import datetime

INPUT_FILE = "c:/src/quorum/backend/debug_verification.log"
OUTPUT_FILE = "c:/src/quorum/backend/debug_summary.md"

def parse_log():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        # Fallback
        with open(INPUT_FILE, 'r', encoding='latin-1', errors='ignore') as f:
            content = f.read()

    md_lines = []
    md_lines.append("# 📊 Debug Log Summary")
    md_lines.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Execution Timeline
    md_lines.append("## ⏱️ Execution Timeline")
    md_lines.append("| Agent | Status | Notes |")
    md_lines.append("|-------|--------|-------|")

    # Find agent starts
    # Pattern: [AgentName] >>> EXECUTION START <<<
    # Or: Starting workflow...
    
    agent_starts = re.findall(r"\[(.*?)\] >>> EXECUTION START <<<", content)
    for agent in agent_starts:
        md_lines.append(f"| **{agent}** | ✅ Started | |")

    md_lines.append("\n")

    # 2. Key Data Points
    md_lines.append("## 🔍 Key Data Points")
    
    # Guard Data
    if "safe_data" in content:
        md_lines.append("- **GuardAgent:** `safe_data` detected.")
        if "keskusteluhistoria" in content:
            md_lines.append("  - ✅ Finnish keys (`keskusteluhistoria`) confirmed.")
    
    # Retrieval Data
    if "RetrievalAgent" in content and "step_context" in content:
         md_lines.append("- **RetrievalAgent:** Execution matched.")
    
    # 3. Final XAI Report
    md_lines.append("## 📝 XAI Report (Final Output)")
    
    # Try to extract the report content printed by debug_full_execution.py
    # Look for "--- XAI REPORT (Sample) ---"
    report_match = re.search(r"--- XAI REPORT \(Sample\) ---\n(.*?)\n(---|\Z)", content, re.DOTALL)
    if report_match:
        report_text = report_match.group(1).strip()
        md_lines.append("```markdown")
        md_lines.append(report_text)
        md_lines.append("```")
    else:
        md_lines.append("> ⚠️ Report content could not be extracted via regex from the log.")

    # 4. Final Keys
    keys_match = re.search(r"Keys: \[(.*?)\]", content)
    if keys_match:
        md_lines.append("\n## 🗝️ Final State Keys")
        md_lines.append(f"`{keys_match.group(1)}`")

    # Write Summary
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))
    print(f"Summary written to {OUTPUT_FILE}")

    # --- LLM CONVERSATION EXTRACTION ---
    conv_lines = []
    conv_lines.append("# 💬 LLM Conversations")
    conv_lines.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Split by "EXECUTION START" to group by agent
    # This is rough because logs are interleaved, but usually sequential in this debug script.
    parts = content.split(">>> EXECUTION START <<<")
    
    # First part is setup, ignore or check for first agent
    for i, part in enumerate(parts):
        if i == 0: continue
        
        # Identify Agent (look backwards in previous part or just assume sequential?)
        # Better: look for [AgentName] in the part (usually logged right after split)
        # Actually, split removes the delimiter. The delimiter had the Agent Name!
        # Re-approach: Regex find iter.
        pass

    # New Approach: Regex scan for blocks
    conv_lines.append("## 📜 Detailed Trace")
    
    # regex for System input
    # ==================== DEBUG: SYSTEM INSTRUCTION ====================
    # (content)
    # ==================================================
    
    # We will identify specific blocks and try to attribute them to the last seen agent.
    
    lines = content.splitlines()
    current_agent = "Unknown"
    
    for idx, line in enumerate(lines):
        if ">>> EXECUTION START <<<" in line:
            # Extract Agent Name: [AgentName] >>> ...
            m = re.search(r"\[(.*?)\] >>>", line)
            if m:
                current_agent = m.group(1)
                conv_lines.append(f"\n### 🤖 {current_agent}")
        
        if "DEBUG: SYSTEM INSTRUCTION" in line:
            conv_lines.append(f"\n**System Instruction:**")
            conv_lines.append("```text")
            # Read until separator
            j = idx + 1
            while j < len(lines) and "======" not in lines[j]:
                conv_lines.append(lines[j])
                j += 1
            conv_lines.append("```")

        if "DEBUG: USER PROMPT" in line:
             conv_lines.append(f"\n**User Prompt:**")
             conv_lines.append("```text")
             j = idx + 1
             while j < len(lines) and "======" not in lines[j]:
                 conv_lines.append(lines[j])
                 j += 1
             conv_lines.append("```")
             
        if "DEBUG: LLM RESPONSE" in line:
             conv_lines.append(f"\n**LLM Response:**")
             conv_lines.append("```json")
             j = idx + 1
             while j < len(lines) and "#######" not in lines[j]:
                 conv_lines.append(lines[j])
                 j += 1
             conv_lines.append("```")

    LLM_FILE = "c:/src/quorum/backend/llm_conversations.md"
    with open(LLM_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(conv_lines))
    print(f"LLM Conversations written to {LLM_FILE}")

if __name__ == "__main__":
    parse_log()
