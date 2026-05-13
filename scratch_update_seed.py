import json
import re

path = 'backend_v2/seed/seed_data.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'<rule>STRUCTURAL RIGIDITY: You MUST adhere to this exact 3-paragraph coaching structure in every output:.*?</rule>'
match = re.search(pattern, content, re.DOTALL)

if match:
    old_rule = match.group(0)
    
    new_rule = (
        "<rule>STRUCTURAL RIGIDITY: You MUST adhere to this exact 4-paragraph coaching structure in every output:\\r\\n"
        "      PARAGRAPH 1 (The Core Competency): Synthesize their main analytical strength based on the overarching data. What did the user practically do well?\\r\\n"
        "      PARAGRAPH 2 (The Interaction Role): You MUST start this paragraph by explicitly highlighting the user's assigned interaction role (e.g., \"**Käyttäjän Rooli: Arkkitehti**\"). Following this, provide a concrete justification for why this specific role (from Passenger to Architect) was assigned based on the control ratio and their cognitive initiative in the current execution. Show exactly which user sentence reflects this role.\\r\\n"
        "      PARAGRAPH 3 (The Cross-Examined Risk): Combine at least two distinct XAI findings (e.g., how the missing context relates to the falsification gap). Highlight the biggest logical blind spot truthfully and concretely.\\r\\n"
        "      PARAGRAPH 4 (The Actionable Path Forward): Provide concrete coaching based on the remediation steps. Empower the user by framing the flaw as a stepping stone to mastery.\\r\\n"
        "    </rule>"
    )
    
    new_content = content.replace(old_rule, new_rule)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Replaced successfully.')
else:
    print('Pattern not found.')
