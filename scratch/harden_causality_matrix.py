import json
import os
import secrets
import time

def generate_tda_id():
    return f"tda_{secrets.token_hex(8)}"

def harden_matrix():
    seed_path = "c:/src/quorum/backend_v2/seed/seed_data.json"
    with open(seed_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    target_block_id = "blk_c5804a9143c34cb1"
    target_block = None
    for block in data['prompt_blocks']:
        if block.get('id') == target_block_id:
            target_block = block
            break
            
    if not target_block:
        print(f"Block {target_block_id} not found!")
        return

    # Update block AI description
    target_block['ai_description'] = (
        "<system_directive>\n"
        "<objective>Evaluate the structural integrity of causal claims, distinguishing between Pearl's three rungs of causation: Association, Intervention, and Counterfactuals.</objective>\n"
        "<epistemic_anchor>Pearl, J. 'The Book of Why: The New Science of Cause and Effect'. Evaluates the transition from observation (correlation) to intervention and counterfactual reasoning. Lexical markers include 'causes', 'if we change', 'would have been'.</epistemic_anchor>\n"
        "<rules>\n"
        "<rule>Enforce the Null Hypothesis: Assume all claimed causal links are post hoc fallacies or spurious correlations until an explicit causal mechanism is proven.</rule>\n"
        "<rule>Strict Role Attribution: Never extract evidence from 'user:' prompts.</rule>\n"
        "</rules>\n"
        "</system_directive>"
    )

    # Update claims
    for score_obj in target_block['scales']:
        score = score_obj['score']
        
        if score == 1:
            score_obj['claims'] = [
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Korrelaation ja Kausaalisuuden sekoittaminen", "en": "Confusing Correlation with Causation"}},
                    "ai_description": "CRITICAL DIRECTIVE (FATAL FLAW): Identify if a mere association is falsely presented as a definitive cause without a mechanism.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate 'spurious'. STEP 1 (Lexical Anchor): Find causal words (e.g. 'causes', 'because'). STEP 2 (Bounding Box): Scan the same sentence. If the causal claim is backed ONLY by a statistical correlation or simultaneous occurrence without any physical mechanism -> ACCEPT (flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": True,
                        "aggregation_mode": "EXISTS"
                    }]
                },
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Post hoc ergo propter hoc", "en": "Post Hoc Fallacy"}},
                    "ai_description": "CRITICAL DIRECTIVE (FATAL FLAW): Find instances where chronological order is the sole proof of causation.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate 'logic'. STEP 1 (Lexical Anchor): Find chronological sequence markers (e.g. 'after', 'then'). STEP 2 (Bounding Box): Scan the paragraph. If the text claims A caused B SOLELY because A happened before B -> ACCEPT (flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": True,
                        "aggregation_mode": "EXISTS"
                    }]
                },
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Taikasana-kausaalisuus", "en": "Magic Word Causality"}},
                    "ai_description": "CRITICAL DIRECTIVE (FATAL FLAW): Locate claims where an abstract, unmeasurable entity is presented as a physical cause.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate science. STEP 1: Find a causal claim involving an invisible, unmeasurable entity (e.g. 'universal energy', 'destiny', 'pure willpower'). STEP 2: If this entity is claimed to directly physically cause the outcome without any measurable intermediary -> ACCEPT (flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": True,
                        "aggregation_mode": "EXISTS"
                    }]
                }
            ]
        elif score == 2:
            score_obj['claims'] = [
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Yksittäisen syyn ylikorostaminen", "en": "Oversimplified Single Cause"}},
                    "ai_description": "CRITICAL DIRECTIVE (FATAL FLAW): Find instances attributing a complex outcome to a single, isolated factor.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate nuance. STEP 1 (Lexical Anchor): Find absolute causal words ('only reason', 'entirely due to'). STEP 2 (Bounding Box): Scan the paragraph. If the text attributes a highly complex outcome to a single cause without acknowledging any other potential factors -> ACCEPT (flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": True,
                        "aggregation_mode": "EXISTS"
                    }]
                },
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Kausaalinen suunta", "en": "Direction of Causality"}},
                    "ai_description": "CRITICAL DIRECTIVE: Identify if the text explicitly states the direction of influence between variables.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate accuracy. STEP 1: Find a claim connecting two variables. STEP 2: If the text explicitly states the direction of influence (which variable affects which) -> ACCEPT. If the direction is ambiguous or bi-directional without explanation -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": False,
                        "aggregation_mode": "ALL_MUST_COMPLY"
                    }]
                },
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Anekdoottinen kausaalisuus", "en": "Anecdotal Causation"}},
                    "ai_description": "CRITICAL DIRECTIVE (FATAL FLAW): Locate universal rules derived solely from a single personal anecdote.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate relevance. STEP 1 (Lexical Anchor): Find personal anecdotes ('for example, I', 'one time'). STEP 2: If a universal causal rule is explicitly derived SOLELY from a single personal anecdote -> ACCEPT (flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": True,
                        "aggregation_mode": "EXISTS"
                    }]
                }
            ]
        elif score == 3:
            score_obj['claims'] = [
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Kausaalimekanismin kuvaus", "en": "Description of Causal Mechanism"}},
                    "ai_description": "CRITICAL DIRECTIVE: Find a step-by-step functional mechanism linking the cause to the effect.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate 'robustness'. STEP 1 (Lexical Anchor): Find a causal claim. STEP 2 (Bounding Box): Scan the paragraph. If the text describes a step-by-step functional mechanism linking the cause to the effect (e.g. A causes B which causes C) -> ACCEPT. If it only states A causes C without any middle step -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": False,
                        "aggregation_mode": "ALL_MUST_COMPLY"
                    }]
                },
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Sekoittavien tekijöiden tunnistaminen", "en": "Identification of Confounders"}},
                    "ai_description": "CRITICAL DIRECTIVE: Locate explicit mentions of alternative variables that could explain the outcome.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate completeness. STEP 1 (Lexical Anchor): Find words indicating alternatives ('however', 'other factors', 'confounder'). STEP 2: If the text explicitly names a potential third variable that could also explain the outcome -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": False,
                        "aggregation_mode": "ALL_MUST_COMPLY"
                    }]
                },
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Yleistämisen virhe", "en": "Overgeneralization Fallacy"}},
                    "ai_description": "CRITICAL DIRECTIVE (FATAL FLAW): Identify if a causal mechanism found in one specific context is universally applied without constraints.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate humility. STEP 1 (Lexical Anchor): Find universal terms ('always', 'in every case'). STEP 2: If a causal claim derived from a specific, limited context is applied to all contexts universally without acknowledging boundaries -> ACCEPT (flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": True,
                        "aggregation_mode": "EXISTS"
                    }]
                }
            ]
        elif score == 4:
            score_obj['claims'] = [
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Interventio-logiikka", "en": "Intervention Logic (Pearl's Rung 2)"}},
                    "ai_description": "CRITICAL DIRECTIVE: Find intervention markers that describe what happens if an active change is made.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate effectiveness. STEP 1 (Lexical Anchor): Find intervention markers ('if we change', 'by increasing', 'implementing'). STEP 2: If the text explicitly describes what would happen to the outcome if an active, deliberate intervention is made on the cause (Pearl's Rung 2) -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": False,
                        "aggregation_mode": "ALL_MUST_COMPLY"
                    }]
                },
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Hallittu eristäminen", "en": "Controlled Isolation"}},
                    "ai_description": "CRITICAL DIRECTIVE: Locate statements indicating an external variable was deliberately held constant.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate perfection. STEP 1 (Lexical Anchor): Find control markers ('controlling for', 'holding constant', 'excluding'). STEP 2: If the text explicitly states that an external variable was deliberately held constant or mathematically isolated to prove the cause -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": False,
                        "aggregation_mode": "ALL_MUST_COMPLY"
                    }]
                },
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Yleistyksen rajaus", "en": "Boundary Definition"}},
                    "ai_description": "CRITICAL DIRECTIVE: Find explicit definitions of the population or conditions where the claim is valid.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate 'humility'. STEP 1 (Lexical Anchor): Find boundary markers ('only applies to', 'limited to', 'under these conditions'). STEP 2: If the text explicitly defines the population, environment, or conditions where the causal claim is valid -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": False,
                        "aggregation_mode": "ALL_MUST_COMPLY"
                    }]
                }
            ]
        elif score == 5:
            score_obj['claims'] = [
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Kontrafaktuaalinen testaus", "en": "Counterfactual Testing (Pearl's Rung 3)"}},
                    "ai_description": "CRITICAL DIRECTIVE: Locate active simulations of an alternate timeline to prove necessary causation.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate creativity. STEP 1 (Lexical Anchor): Find counterfactual markers ('if X had not', 'would have been'). STEP 2: If the text actively simulates an alternate timeline (Pearl's Rung 3) to explicitly prove necessary causation -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": False,
                        "aggregation_mode": "ALL_MUST_COMPLY"
                    }]
                },
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Formaali mallintaminen / Do-operaattori", "en": "Formal Modeling / Do-Operator"}},
                    "ai_description": "CRITICAL DIRECTIVE: Find the use of a formal, structural model to map causality.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate 'watertightness'. STEP 1: Find mathematical or structural causal terms ('do-calculus', 'directed acyclic graph', 'structural equation', 'formal model'). STEP 2: If the text explicitly uses a formal model or strict structural logic to map the causality -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": False,
                        "aggregation_mode": "ALL_MUST_COMPLY"
                    }]
                },
                {
                    "label": {"default_locale": "fi", "translations": {"fi": "Lakisidonnainen ankkurointi", "en": "Theoretical Law Anchoring"}},
                    "ai_description": "CRITICAL DIRECTIVE: Identify where the specific causal mechanism is anchored to an established theoretical law.",
                    "tda_assertions": [{
                        "tda_id": generate_tda_id(),
                        "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do not evaluate 'perfect'. STEP 1: Find references to established scientific theories, formal logic principles, or physical laws. STEP 2: If the specific causal mechanism is explicitly anchored to an established theoretical law -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document reasoning_trace first.",
                        "inverse_evidence": False,
                        "aggregation_mode": "ALL_MUST_COMPLY"
                    }]
                }
            ]

    # Create backup
    backup_dir = "c:/src/quorum/backend_v2/seed/backups"
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"seed_data_backup_{int(time.time())}.json")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Created backup at {backup_path}")

    # Save changes
    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Matrix {target_block_id} has been successfully hardened and saved to seed_data.json.")

if __name__ == "__main__":
    harden_matrix()
