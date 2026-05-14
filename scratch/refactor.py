import json
import secrets

def gen_tda_id():
    return f"tda_{secrets.token_hex(8)}"

def refactor():
    with open('c:/src/quorum/backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    target_matrix = None
    for b in data['prompt_blocks']:
        if b['id'] == 'blk_ff72c2d79edb4ebf':
            target_matrix = b
            break
            
    if not target_matrix:
        print("Matrix not found.")
        return
        
    target_matrix['ai_description'] = (
        "<system_directive>\n"
        "<objective>Evaluate the user's executive control and process ownership over the AI, distinguishing between a passive 'passenger' and a proactive 'Supreme Adjudicator' (Process Owner).</objective>\n"
        "<epistemic_anchor>W. Edwards Deming (Total Quality Management) & Automation Bias / Human-in-the-Loop (HITL) theory. The human must actively override 'Automation Complacency' and 'Rubber-Stamping'. The user must act as the absolute executive authority, ensuring built-in quality control and continuous active steering (Plan-Do-Check-Act). Abdicating the 'Check' or 'Act' phases to the AI constitutes catastrophic failure. Lexical markers of success include explicit corrective commands, overriding AI choices, and demanding verifiable steps.</epistemic_anchor>\n"
        "<rules>\n"
        "<rule>Enforce the Null Hypothesis: Assume the user is a passive 'passenger' blindly accepting AI output until explicit, authoritative executive commands are demonstrated.</rule>\n"
        "<rule>Bounty Hunter Paradigm: In FATAL FLAW directives (Scores 1-2), you only need to find ONE sentence that commits the described error (e.g. passive acceptance) to trigger extraction.</rule>\n"
        "<rule>Strict Boolean Logic: Evaluate claims as single-pole facts.</rule>\n"
        "</rules>\n"
        "</system_directive>"
    )

    claims_data = {
        1: [
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Sokea hyväksyntä", "en": "Blind acceptance"}},
                "ai_description": "CRITICAL DIRECTIVE: FIND evidence of 'Automation Complacency'. Extract a command where the user blindly accepts the AI's output without asking critical questions.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY the user prompts (prefixes like 'user:'). BANNED SOURCES: Never read AI outputs. BANNED CONCEPTS: Do not look for absence of critique. STEP 1 (Lexical Anchor): Find active acceptance words ('täydellinen', 'näin', 'jatketaan', 'hyvä', 'perfect', 'looks good'). STEP 2 (Bounding Box): Scan the user prompt. If the user accepts the AI output fully in one sentence WITHOUT any modifications or follow-up tasks in the same prompt -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace BEFORE extracting exact_quote.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Päätösvallan ulkoistaminen", "en": "Delegating decision authority"}},
                "ai_description": "CRITICAL DIRECTIVE: FIND evidence of 'Automation Bias'. Extract a user command where the user explicitly asks the AI to make a final decision for them.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. BANNED CONCEPTS: Do not evaluate 'collaboration' or 'politeness'. STEP 1 (Lexical Anchor): Find delegation verbs ('päätä', 'valitse', 'kumpi', 'decide', 'choose'). STEP 2 (Bounding Box): Scan the prompt. If the user explicitly asks the AI to make a final subjective choice or decision on their behalf -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning in reasoning_trace BEFORE extracting.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Virheiden sivuuttaminen", "en": "Ignoring errors"}},
                "ai_description": "CRITICAL DIRECTIVE: FIND evidence of 'Rubber-Stamping'. Extract a user command where the user acknowledges a flaw but commands the AI to proceed anyway.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not evaluate 'forgiveness'. STEP 1 (Lexical Anchor): Find dismissive phrases ('ei haittaa', 'riittää', 'mennään näillä', 'vaikka', 'nevermind', 'good enough'). STEP 2: If the user actively acknowledges an incomplete or erroneous AI response but instructs to move forward anyway -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting exact_quote.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            }
        ],
        2: [
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Pintapuolinen korjailu", "en": "Superficial tweaking"}},
                "ai_description": "CRITICAL DIRECTIVE: FIND evidence of superficial tweaking. Extract a user command where the user only asks for mechanical changes instead of addressing core logic.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. BANNED CONCEPTS: Do not evaluate 'politeness'. STEP 1 (Lexical Anchor): Find formatting terms ('lyhennä', 'muotoile', 'bulletteina', 'shorten', 'format'). STEP 2: If the user's ONLY request is a stylistic or formatting change, completely ignoring substantive logic -> ACCEPT. If they challenge logic -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Reaktiivinen paikkailu", "en": "Reactive patching"}},
                "ai_description": "CRITICAL DIRECTIVE: FIND a reactive prompt where the user adds a constraint only AFTER the AI has already failed.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Lexical Anchor): Find reactive anchors ('unohdit', 'lisää vielä', 'korjaa tuo', 'entä', 'forgot', 'add'). STEP 2 (Bounding Box): Scan the sequence. If the user adds a new critical constraint that they forgot to specify in the previous prompt -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Lähdeaineiston ohittaminen", "en": "Bypassing source material"}},
                "ai_description": "CRITICAL DIRECTIVE: FIND evidence where the user asks the AI to summarize raw data without enforcing any specific extraction rules.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not accept specific extraction commands. STEP 1 (Lexical Anchor): Find broad summary commands ('tiivistä', 'tee yhteenveto', 'mitä tässä lukee', 'summarize'). STEP 2: If the command lacks any specific constraints and allows the AI to freely decide what is important -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            }
        ],
        3: [
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Reunaehtojen asettaminen", "en": "Setting constraints"}},
                "ai_description": "CRITICAL DIRECTIVE: LOCATE a user command where specific, actionable constraints are set for the AI's output generation.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not evaluate 'perfection'. STEP 1 (Lexical Anchor): Find constraint markers ('vähintään', 'korkeintaan', 'rakenne:', 'muodossa', 'at least', 'format:'). STEP 2: If the user provides at least one measurable or structural constraint for the output -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Taustakontekstin määrittely", "en": "Defining background context"}},
                "ai_description": "CRITICAL DIRECTIVE: EXTRACT a user command where explicit background information, role, or target audience is provided.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Lexical Anchor): Find context markers ('toimit', 'kohdeyleisö', 'taustana', 'tavoite', 'audience', 'role', 'context'). STEP 2: If the user defines the situational context or role for the AI before asking for output -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Perusteltu palaute", "en": "Reasoned feedback"}},
                "ai_description": "CRITICAL DIRECTIVE: LOCATE a user response where they correct the AI AND provide a logical reason for the correction.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Lexical Anchor): Find causal feedback markers ('koska', 'sillä', 'tämä ei toimi, koska', 'syynä', 'because', 'due to'). STEP 2: If the user corrects the AI and explicitly states the logical reason for the correction -> ACCEPT. If just a blind correction -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            }
        ],
        4: [
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Analyysimetodin pakottaminen", "en": "Forcing an analysis method"}},
                "ai_description": "CRITICAL DIRECTIVE: FIND evidence where the user explicitly forces the AI to use a specific methodology, framework, or theoretical lens.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. BANNED CONCEPTS: Do not accept generic requests ('analysoi hyvin'). STEP 1 (Lexical Anchor): Find methodology anchors ('käytä menetelmää', 'mallin mukaisesti', 'viitekehys', 'SWOT', 'PESTEL', 'teoria', 'framework'). STEP 2: If the user explicitly names a method or analytical framework the AI MUST follow -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Välitavoitteiden asettaminen", "en": "Setting intermediate milestones"}},
                "ai_description": "CRITICAL DIRECTIVE: EXTRACT a user command that strictly breaks a complex task into discrete steps and prevents the AI from jumping to the conclusion.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Lexical Anchor): Find sequence constraints ('ensin', 'sen jälkeen', 'odota lupaani', 'askel 1', 'first', 'wait for'). STEP 2: If the user explicitly forces the AI to stop and wait for human validation before proceeding to the next step -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Lähteisiin sitominen", "en": "Anchoring to sources"}},
                "ai_description": "CRITICAL DIRECTIVE: LOCATE a user command where the AI is forbidden from generating new information and is forced to extract exact quotes.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Lexical Anchor): Find extraction anchors ('poimi suoraan', 'tarkka lainaus', 'älä keksi itse', 'perustuen vain', 'exact quote', 'do not hallucinate'). STEP 2: If the user explicitly restricts the AI to the provided data and demands exact evidence -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            }
        ],
        5: [
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Episteeminen kumoaminen", "en": "Epistemic overriding"}},
                "ai_description": "CRITICAL DIRECTIVE: EXTRACT an execution where the user explicitly overrides the AI's internal logic with superior, externally verified reasoning.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not accept simple disagreements. STEP 1 (Lexical Anchor): Find override phrases ('olet väärässä', 'tämä logiikka ontuu', 'faktojen vastainen', 'kumottu', 'incorrect', 'you are wrong'). STEP 2 (Bounding Box): Scan the sequence. If the user rejects the AI's reasoning and injects their own superior logical or empirical correction -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Falsifioinnin pakottaminen", "en": "Forcing falsification"}},
                "ai_description": "CRITICAL DIRECTIVE: FIND evidence where the user actively forces the AI to attack, falsify, or critically audit its own generated output.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Lexical Anchor): Find audit anchors ('etsi heikkoudet', 'hyökkää tätä vastaan', 'falsifioi', 'devil\\'s advocate', 'critique'). STEP 2: If the user forces the AI to rigorously critique its own previous output or identify fatal flaws -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Kognitiivisen arkkitehtuurin ohjaus", "en": "Directing cognitive architecture"}},
                "ai_description": "CRITICAL DIRECTIVE: LOCATE an advanced command where the user explicitly programs the AI's internal behavior or cognitive posture for the entire session.",
                "tda_assertions": [{
                    "tda_id": gen_tda_id(),
                    "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Lexical Anchor): Find meta-programming anchors ('sääntö on', 'tästä lähtien', 'järjestelmätason ohje', 'kognitiivinen asento', 'from now on', 'rule is'). STEP 2: If the user sets global architectural constraints or meta-rules that govern the AI's behavior across multiple turns -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning BEFORE extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            }
        ]
    }

    for scale in target_matrix['scales']:
        score = scale['score']
        if score in claims_data:
            scale['claims'] = claims_data[score]

    with open('c:/src/quorum/backend_v2/seed/seed_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("Matrix blk_ff72c2d79edb4ebf refactored successfully.")

if __name__ == '__main__':
    refactor()
