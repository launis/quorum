import json
import os

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"

with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

def ensure_en(block, fi_text, en_text):
    if "description" not in block:
        block["description"] = {}
    if "translations" not in block["description"]:
        block["description"]["translations"] = {}
    block["description"]["translations"]["fi"] = fi_text
    block["description"]["translations"]["en"] = en_text
    block["description"]["default_locale"] = "fi"

def repurpose_role(old_id, new_id, fi_text, en_text):
    for block in data.get("prompt_blocks", []):
        if block["id"] == old_id:
            block["id"] = new_id
            block["type"] = "instruction"
            if "scales" in block: del block["scales"]
            if "scale_min" in block: del block["scale_min"]
            if "scale_max" in block: del block["scale_max"]
            ensure_en(block, fi_text, en_text)
            print(f"Repurposed {old_id} -> {new_id}")
            return

repurpose_role("matrix_analyst", "block_role_analyst", 
    "ROOLI: Analyytikko (Analyst).\nTEHTÄVÄ: Käsittele tietoa puolueettomasti, etsi syy-seuraussuhteita ja muodosta selkeä katsaus materiaalista.",
    "ROLE: Analyst.\nTASK: Process information impartially, search for cause-and-effect relationships, and form a clear overview of the material.")

repurpose_role("matrix_coach", "block_role_coach",
    "ROOLI: Valmentaja (Coach).\nTEHTÄVÄ: Anna rakentavaa palautetta, tue kognitiivistä kehitystä ja ohjaa kohti syvällisempiä ratkaisuja.",
    "ROLE: Coach.\nTASK: Provide constructive feedback, support cognitive development, and guide towards deeper solutions.")

repurpose_role("matrix_guard", "block_role_guard",
    "ROOLI: Turva-agentti (Guard).\nTEHTÄVÄ: Valvo syötteitä ja tulosteita eettisten jännitteiden, tietoturvauhkien ja biasin varalta.",
    "ROLE: Guard.\nTASK: Monitor inputs and outputs for ethical tensions, security threats, and bias.")

repurpose_role("matrix_logician", "block_role_logician",
    "ROOLI: Loogikko (Logician).\nTEHTÄVÄ: Pura argumentit niiden loogisiin osiin (Toulminin malli) ja arvioi päättelyn pätevyys.",
    "ROLE: Logician.\nTASK: Break down arguments into their logical components (Toulmin's model) and evaluate the validity of reasoning.")

repurpose_role("matrix_overseer", "block_role_overseer",
    "ROOLI: Valvoja (Overseer).\nTEHTÄVÄ: Koordinoi muita agentteja, valvo työnkulkua ja varmista linjaus alkuperäisen tavoitteen kanssa.",
    "ROLE: Overseer.\nTASK: Coordinate other agents, oversee the workflow, and ensure alignment with the original goal.")

repurpose_role("matrix_profiler", "block_role_profiler",
    "ROOLI: Profiloija (Profiler).\nTEHTÄVÄ: Analysoi tekstin sävyä, piilomerkityksiä, intentioita sekä psykologista profiilia.",
    "ROLE: Profiler.\nTASK: Analyze the tone, hidden meanings, intentions, and psychological profile of the text.")

def update_cognitive_block(block_id, fi_text, en_text):
    for block in data.get("prompt_blocks", []):
        if block["id"] == block_id:
            ensure_en(block, fi_text, en_text)
            print(f"Updated {block_id}")
            return

update_cognitive_block("block_oprule4", 
    "SÄÄNTÖ: Passiivisuus-leikkuri.\nMÄÄRÄYS: Tunnista passiivisuus rehellisesti - älä yritä itse laskea pistesaldoa alas, vaan kirjaa ylös matkustajarooli, jotta Causal Analyst / Judge voi operatiivisesti leikata tulosta.",
    "RULE: Passivity Clipper.\nMANDATE: Identify passivity honestly - do not attempt to calculate the score reduction yourself, but log the passenger role so the Causal Analyst / Judge can operationally cut the result.")

update_cognitive_block("block_protocol1",
    "SÄÄNTÖ: Negatiivinen Loki.\nMÄÄRÄYS: Kirjaa ylös puutteet. Mitä käyttäjä jätti tekemättä? Etsi aktiivisesti asioita, joita ei kysytty tai haastettu.",
    "RULE: Negative Audit.\nMANDATE: Record deficiencies. What did the user fail to do? Actively look for things that were not asked or challenged.")

update_cognitive_block("block_oprule3",
    "SÄÄNTÖ: Todisteet vs Väitteet.\nMÄÄRÄYS: Erota toisistaan se, mitä käyttäjä todistettavasti teki (empiirinen aineisto), ja mitä hän vain väittää tehneensä (reflektio).",
    "RULE: Evidence vs Claims.\nMANDATE: Differentiate between what the user provably did (empirical material/logs) and what they only claim to have done (reflection).")

update_cognitive_block("block_heuristic1",
    "SÄÄNTÖ: Temporaalinen tarkistus.\nMÄÄRÄYS: Tarkista aikajana. Tuliko oivallus ENNEN tuloksen paranemista (Syy) vai vasta sen jälkeen (Rationalisointi)?",
    "RULE: Temporal Check.\nMANDATE: Check the timeline. Did the insight come BEFORE the result improved (Cause) or only after (Rationalization)?")

update_cognitive_block("block_heuristic2",
    "SÄÄNTÖ: Kontrafaktuaalinen tarkistus.\nMÄÄRÄYS: Kysy: 'Jos käyttäjä ei olisi tehnyt mitään, olisiko tekoäly ratkaissut tämän silti?'. Jos kyllä, aktiivinen prosessiarvo on matala.",
    "RULE: Counterfactual Check.\nMANDATE: Ask: 'If the user had done nothing, would the AI have solved this anyway?'. If yes, the active process value is low.")

update_cognitive_block("block_rule4",
    "SÄÄNTÖ: Epäilyttävä Täydellisyys.\nMÄÄRÄYS: Jos prosessissa ei ole kitkaa tai iteraatiota, se on epäilyttävä. Täydellisyys ilman työtä on harhaista.",
    "RULE: Suspicious Perfection.\nMANDATE: If there is no friction or iteration in the process, it is suspicious. Perfection without work is illusionary.")

# Dynamic Language block
for block in data.get("prompt_blocks", []):
    if block["id"] == "block_instructionlanguagefi":
        block["id"] = "block_instructionlanguage_dynamic"
        fi_desc = "SÄÄNTÖ: Dynaaminen Kielivalinta.\nMÄÄRÄYS: Sinun ON tuotettava tekstiä sillä kielellä, joka on asetettu järjestelmän tai käyttäjän pääkieleksi. Älä vaihda kieltä vahingossa kesken vastauksen."
        en_desc = "RULE: Dynamic Language Selection.\nMANDATE: You MUST produce text in the language set as the system or user's primary language. Do not accidentally switch languages mid-response."
        ensure_en(block, fi_desc, en_desc)
        print("Updated language block to dynamic")

# Instruction Hardening
def harden_task(block_id, fi_add, en_add):
    for block in data.get("prompt_blocks", []):
        if block["id"] == block_id:
            fi_old = block.get("description", {}).get("translations", {}).get("fi", "")
            en_old = block.get("description", {}).get("translations", {}).get("en", "")
            
            fi_new = fi_old + "\n\n" + fi_add
            en_new = en_old + "\n\n" + en_add
            ensure_en(block, fi_new, en_new)
            print(f"Hardened task {block_id}")

harden_task("block_taskcausal", 
    "KONTEKSTI: Syötteiden dynaaminen tunnistus.\nKIELTO: Älä oleta että tiedosto 'REFLECTION_TEXT' on olemassa. Lue 'ai_description' kenttä tunnistaaksesi tiedostot.\nKÄSKE: Etsi syötteistä 'is_chat_history: true'. Tämä on ainoa todellinen kommunikaatio koonnos. Jos reflektio on olemassa muissa tiedostoissa, vertaa sitä chat-historiaan (Etsi Say-Do kuiluja). Älä rankaise jos reflektio puuttuu kokonaan.",
    "CONTEXT: Dynamic input recognition.\nPROHIBITION: Do NOT assume a file 'REFLECTION_TEXT' exists. Read the 'ai_description' field to identify files.\nMANDATE: Look for inputs flagged with 'is_chat_history: true'. This is the only real communication log. If a reflection exists in other files, compare it to the chat history (Look for Say-Do Gaps). Do not penalize if the reflection is entirely missing.")

harden_task("block_taskfalsifier",
    "KONTEKSTI: Goodhartin laki ja performatiivisuus.\nKÄSKE: Etsi ohjaus-syötteistä (is_chat_history: true) asioita, joita käyttäjä väittää tehneensä mutta ei oikeasti tehnyt. Sovella tarvittaessa 'Epäilyttävä täydellisyys' -sääntöä.",
    "CONTEXT: Goodhart's law and performativity.\nMANDATE: Search the communication inputs (is_chat_history: true) for things the user claims to have done but didn't actually do. Apply the 'Suspicious Perfection' rule if necessary.")

harden_task("block_taskjudge",
    "KONTEKSTI: Suuri yhdistäminen ja tuomio.\nKÄSKE: Painota Causal Analystin ja Falsifierin tuloksia. Jos nämä asiantuntijat löytävät 'Performatiivisen reflektion' tai 'Say-Do' kuilun, sinun on rangaistava prosessipisteitä ankarasti skaaloissa, vaikka tuotettu laatu olisi korkea.",
    "CONTEXT: Grand unification and verdict.\nMANDATE: Heavily weigh the results of the Causal Analyst and Falsifier. If these experts find a 'Performative reflection' or a 'Say-Do gap', you must penalize the process scores severely in your scales, even if the final generated quality is high.")


# Matrix Tightening
def tighten_matrix(block_id, score, name_fi, name_en, claims_fi, claims_en):
    for block in data.get("prompt_blocks", []):
        if block["id"] == block_id and "scales" in block:
            for scale in block["scales"]:
                if scale.get("score") == score:
                    if "name" not in scale: scale["name"] = {"translations": {}}
                    scale["name"]["translations"]["fi"] = name_fi
                    scale["name"]["translations"]["en"] = name_en
                    scale["name"]["default_locale"] = "fi"
                    
                    new_claims = []
                    for c_fi, c_en in zip(claims_fi, claims_en):
                        new_claims.append({
                            "default_locale": "fi",
                            "translations": {
                                "fi": c_fi,
                                "en": c_en
                            }
                        })
                    scale["claims"] = new_claims
                    print(f"Tightened {block_id} score {score}")

tighten_matrix("matrix_judge", 5, "Arkkitehti (Erinomainen)", "Architect (Excellent)", 
    [
        "Täydellinen hallinta ja läpinäkyvyys. Käyttäjä ei jättänyt mitään tekoälyn arvattavaksi, ja ohjaus on todistettavasti nähtävissä ekspliittisessä chat-historiassa (is_chat_history: true) tai toimitetussa RAG-kontekstissa.",
        "Korkeimman tason asiantuntijuus. Ei hallusinaatioita, absoluuttinen prosessin integriteetti ilman merkkiäkään 'Goodhartin laista' tai jälkikäteisestä rationalisoinnista."
    ],
    [
        "Perfect control and transparency. The user left nothing for the AI to guess, and the guidance is provably visible in the explicit chat history (is_chat_history: true) or provided RAG context.",
        "Highest level of expertise. No hallucinations, absolute process integrity without a hint of 'Goodhart's Law' or post-hoc rationalization."
    ])

tighten_matrix("matrix_causal_analyst", 5, "Aito (Genuine)", "Genuine",
    [
        "Suora ja kiistaton syy-seuraussuhde (Causal Link). Työn laatu on suoraa seurausta ekspliittisestä ohjauksesta (is_chat_history: true) tai tarjotusta datasta, ei pelkästään tekoälyn taidoista.",
        "Vastafaktuaalinen testi osoittaa: ilman käyttäjän tarkkaa ohjausta tulos olisi jäänyt selvästi heikommaksi tai saavuttamatta."
    ],
    [
        "Direct and indisputable cause-and-effect relationship (Causal Link). The quality of the work is a direct result of explicit guidance (is_chat_history: true) or provided data, not just the AI's skills.",
        "The counterfactual test shows: without the user's precise guidance, the result would have been clearly weaker or unachieved."
    ])


# Update step references
for step in data.get("steps", []):
    pb_list = step.get("prompt_blocks", [])
    
    # 1. Replace the dynamic language block
    new_pb_list = []
    for pb in pb_list:
        if pb == "block_instructionlanguagefi":
            new_pb_list.append("block_instructionlanguage_dynamic")
        elif pb in ["matrix_analyst", "matrix_coach", "matrix_guard", "matrix_logician", "matrix_overseer", "matrix_profiler"]:
            # If any step referenced the old orphan mistakenly, convert it dynamically
            new_id = pb.replace("matrix_", "block_role_")
            new_pb_list.append(new_id)
        else:
            new_pb_list.append(pb)
            
    # 2. Inject heuristics and roles appropriately
    def inject(block_id, index=0):
        if block_id not in new_pb_list:
            new_pb_list.insert(index, block_id)

    if step["id"] == "step_analyst":
        inject("block_role_analyst", index=0)
        
    if step["id"] == "step_causal_analyst":
        inject("block_heuristic1")
        inject("block_heuristic2")

    if step["id"] == "step_falsifier":
        inject("block_protocol1")
        inject("block_rule4")

    if step["id"] == "step_judge":
        inject("block_oprule3")
        inject("block_oprule4")

    # Save
    step["prompt_blocks"] = new_pb_list

with open(SEED_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("SUCCESS: seed_data_modified.json written.")
