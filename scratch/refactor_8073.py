import json
import secrets

def get_opaque_id():
    return 'tda_' + secrets.token_hex(8)

def refactor_block():
    file_path = 'backend_v2/seed/seed_data.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    target_block = None
    for block in data.get('prompt_blocks', []):
        if block.get('id') == 'blk_80732a33fe1947ee':
            target_block = block
            break
            
    if not target_block:
        print("Block blk_80732a33fe1947ee not found!")
        return

    # Rules map: (scale_idx, claim_idx) -> (ai_rule_description, inverse_evidence, aggregation_mode)
    rules_map = {
        (0, 0): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes or `reflection_text`. BANNED LOGIC: Do not evaluate 'blind trust' or 'naivety'. STEP 1 (Lexical Anchor): Find an absolute acceptance phrase (e.g. 'the system output proves', 'we can rely on'). STEP 2 (Bounding Box): Scan the paragraph. If the acceptance is presented without an explicit verification step mentioned -> ACCEPT (flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace BEFORE extracting exact_quote.",
            True, "EXISTS"
        ),
        (0, 1): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED CONCEPTS: Do not accept generic errors; must be an absolute fabrication (LLM09 Overreliance). STEP 1 (Lexical Anchor): Find a factual claim (dates, names, specific data points). STEP 2 (Search Verification): Verify the claim's logic. If the claim is demonstrably false or fabricated but presented with absolute certainty -> ACCEPT (flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document the falsification reasoning in reasoning_trace BEFORE extracting exact_quote.",
            True, "EXISTS"
        ),
        (0, 2): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED CONCEPTS: Do not evaluate 'ignorance' subjectively. STEP 1 (Lexical Anchor): Find dismissive transition words (e.g. 'regardless', 'not an issue', 'ignore'). STEP 2 (Bounding Box): Scan the preceding sentence. If a security risk (like injection or leakage) was mentioned but immediately dismissed without physical mitigation steps -> ACCEPT (flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document the missing mitigation in reasoning_trace BEFORE extracting exact_quote.",
            True, "EXISTS"
        ),
        (1, 0): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not evaluate 'proactivity' subjectively. STEP 1 (Lexical Anchor): Find temporal reactive markers (e.g. 'after the failure', 'once identified', 'we fixed'). STEP 2 (Bounding Box): Scan the paragraph. If security measures are ONLY described as post-incident responses without any pre-incident checks -> ACCEPT (flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document the reactive timeline in reasoning_trace BEFORE extracting exact_quote.",
            True, "EXISTS"
        ),
        (1, 1): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED CONCEPTS: Do not evaluate 'superficial' subjectively. STEP 1 (Lexical Anchor): Find terms indicating a manual or ad-hoc check (e.g. 'glanced at', 'looks okay', 'basic check'). STEP 2 (Bounding Box): Scan the paragraph. If the verification relies entirely on human intuition rather than a systemic protocol (like OWASP) -> ACCEPT (flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document the absence of systemic protocol in reasoning_trace BEFORE extracting exact_quote.",
            True, "EXISTS"
        ),
        (1, 2): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept subjective assessments of risk severity. STEP 1 (Lexical Anchor): Find risk identification markers (e.g. 'potential risk', 'hazard', 'vulnerability'). STEP 2 (Bounding Box): Scan the paragraph downwards. If the risk is identified but no physical action verb (e.g. 'encrypted', 'blocked', 'sanitized') follows to mitigate it -> ACCEPT (flaw proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document the unmitigated hazard in reasoning_trace BEFORE extracting exact_quote.",
            True, "EXISTS"
        ),
        (2, 0): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept vague assertions like 'it is secure'. STEP 1 (Lexical Anchor): Find explicit physical validation actions (e.g. 'validated', 'filtered', 'sanitized', 'checked against'). STEP 2 (Bounding Box): Scan the sentence. If it describes a concrete data validation rule being applied to input or output -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the exact validation action in reasoning_trace BEFORE extracting exact_quote.",
            False, "ALL_MUST_COMPLY"
        ),
        (2, 1): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Do not accept implicit assumptions. BANNED LOGIC: Do not evaluate internal mental states. STEP 1 (Lexical Anchor): Find epistemic boundary markers (e.g. 'may be inaccurate', 'verify independently', 'limitations', 'hallucination'). STEP 2 (Bounding Box): Scan the paragraph. If there is a physical, explicit statement acknowledging the AI's limitations or a disclaimer -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the explicit boundary in reasoning_trace BEFORE extracting exact_quote.",
            False, "ALL_MUST_COMPLY"
        ),
        (2, 2): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prompts alone. BANNED CONCEPTS: Do not accept generic terms like 'safe'. STEP 1 (Lexical Anchor): Find explicit references to standard security protocols (e.g. 'policy', 'standard', 'guideline', 'OWASP'). STEP 2 (Bounding Box): Scan the paragraph. If the text physically demonstrates adherence to a named standard -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the specific protocol followed in reasoning_trace BEFORE extracting exact_quote.",
            False, "ALL_MUST_COMPLY"
        ),
        (3, 0): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not evaluate 'secure by design' subjectively. STEP 1 (Lexical Anchor): Find proactive structural markers (e.g. 'automatically blocks', 'default deny', 'pre-processed'). STEP 2 (Bounding Box): Scan the sentence. If a security constraint is described as a structural, automatic mechanism rather than a manual check -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the structural mechanism in reasoning_trace BEFORE extracting exact_quote.",
            False, "ALL_MUST_COMPLY"
        ),
        (3, 1): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept theoretical resilience. STEP 1 (Lexical Anchor): Find error handling markers (e.g. 'rejected', 'fallback', 'graceful degradation', 'safely ignored'). STEP 2 (Bounding Box): Scan the paragraph. If it describes physically rejecting invalid input or defaulting to a safe state without crashing -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the fail-safe vector in reasoning_trace BEFORE extracting exact_quote.",
            False, "ALL_MUST_COMPLY"
        ),
        (3, 2): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED CONCEPTS: Do not evaluate 'deliberation' without a physical pause. STEP 1 (Lexical Anchor): Find friction markers (e.g. 'requires confirmation', 'are you sure', 'second approval'). STEP 2 (Bounding Box): Scan the paragraph. If an explicit multi-step confirmation or manual override is required before a risky execution -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the physical friction step in reasoning_trace BEFORE extracting exact_quote.",
            False, "ALL_MUST_COMPLY"
        ),
        (4, 0): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept general 'secure' statements. STEP 1 (Lexical Anchor): Find zero-trust markers (e.g. 'zero implicit trust', 'independent verification', 'cryptographic', 'strict boundary'). STEP 2 (Bounding Box): Scan the paragraph. If the processing demonstrates explicit zero-trust architecture where every input/output is treated as potentially hostile -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the zero-trust boundary in reasoning_trace BEFORE extracting exact_quote.",
            False, "ALL_MUST_COMPLY"
        ),
        (4, 1): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept 'fully justified' without a traced reasoning path. STEP 1 (Lexical Anchor): Find causal justification markers (e.g. 'because of risk X', 'to prevent Y', 'therefore blocked'). STEP 2 (Bounding Box): Scan the paragraph. If a security action is paired with an explicit, documented risk assessment -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the exact risk assessment linkage in reasoning_trace BEFORE extracting exact_quote.",
            False, "ALL_MUST_COMPLY"
        ),
        (4, 2): (
            "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED CONCEPTS: Reject superficial mentions of frameworks. STEP 1 (Lexical Anchor): Find exact framework citations (e.g. 'OWASP LLM01', 'NIST', 'ISO 27001'). STEP 2 (Bounding Box): Scan the paragraph. If the specific framework clause is directly linked to the physical security action taken -> ACCEPT. Otherwise -> REJECT. ENFORCEMENT RULE: Document the exact framework clause mapping in reasoning_trace BEFORE extracting exact_quote.",
            False, "ALL_MUST_COMPLY"
        )
    }

    # Iterate over scales and claims
    for s_idx, scale in enumerate(target_block.get('scales', [])):
        for c_idx, claim in enumerate(scale.get('claims', [])):
            if (s_idx, c_idx) in rules_map:
                desc, inv_ev, agg_mode = rules_map[(s_idx, c_idx)]
                # Ensure 1 TDA assertion
                if len(claim['tda_assertions']) > 0:
                    claim['tda_assertions'][0]['tda_id'] = get_opaque_id()
                    claim['tda_assertions'][0]['ai_rule_description'] = desc
                    claim['tda_assertions'][0]['inverse_evidence'] = inv_ev
                    claim['tda_assertions'][0]['aggregation_mode'] = agg_mode

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Successfully refactored blk_80732a33fe1947ee in seed_data.json")

if __name__ == '__main__':
    refactor_block()
