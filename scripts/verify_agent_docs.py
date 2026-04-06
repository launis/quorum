import re
import sys
from pathlib import Path

def verify_docs():
    agents_md = Path('AGENTS.md')
    docs_opas = Path('docs/Agent_Workflows_Opas.md')

    if not agents_md.exists() or not docs_opas.exists():
        print("❌ TARKISTUS EPÄONNISTUI: AGENTS.md tai docs/Agent_Workflows_Opas.md puuttuu.")
        sys.exit(1)

    agents_content = agents_md.read_text(encoding='utf-8')
    docs_content = docs_opas.read_text(encoding='utf-8')

    # Haetaan komennot molemmista (muotoa /tier1-planner, /handover jne.)
    pattern = r'/(?:tier[0-9]+-[a-zA-Z0-9_-]+|handover)'
    agents_commands = set(re.findall(pattern, agents_content))
    docs_commands = set(re.findall(pattern, docs_content))

    missing_in_docs = agents_commands - docs_commands
    missing_in_agents = docs_commands - agents_commands

    errors = False

    if missing_in_docs or missing_in_agents:
        print("\n🚨 ARKKITEHTUURIVIRHE: AGENTS.md ja Agent_Workflows_Opas.md EIVÄT OLE SYNKRONISSA!\n")
        if missing_in_docs:
            print(f"-> Nämä on määritelty AGENTS.md:ssä, mutta puuttuvat Oppaasta: {missing_in_docs}")
        if missing_in_agents:
            print(f"-> Nämä on selitetty Oppaassa, mutta puuttuvat AGENTS.md:stä: {missing_in_agents}")
        errors = True

    if "GEMINI.MD" not in agents_content:
        print("-> ❌ GEMINI.MD puuttuu AGENTS.md <required_scanners> -listalta.")
        errors = True

    if errors:
        sys.exit(1)

    print("✅ ARKKITEHTUURI SYNKRONISSA: AGENTS.md -koneohjaus ja Ihmisen Manuaali vastaavat toisiaan täydellisesti.")

if __name__ == '__main__':
    verify_docs()
