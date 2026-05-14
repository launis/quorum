import json
import secrets
import os

def get_opaque_id():
    return "tda_" + secrets.token_hex(8)

def harden_matrix():
    seed_path = "c:/src/quorum/backend_v2/seed/seed_data.json"
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    target_block = next((b for b in data.get("prompt_blocks", []) if b.get("id") == "blk_fb15f8dcf23f4865"), None)
    if not target_block:
        print("Block not found!")
        return

    # Update macro ai_description
    target_block["ai_description"] = "<system_directive>\n<objective>Evaluate strict adherence to operational guidelines, verifiable provenance, and structural integrity based on established archival frameworks.</objective>\n<epistemic_anchor>ARMA International. 'Generally Accepted Recordkeeping Principles (The Principles).' A framework ensuring organizational Accountability, Transparency, Integrity, Protection, Compliance, Availability, Retention, and Disposition.</epistemic_anchor>\n<rules>\n<rule>Enforce the Null Hypothesis: Assume all actions are ungrounded hallucinations unless explicit compliance and methodological structure are demonstrated.</rule>\n<rule>Bounty Hunter Paradigm: In FATAL FLAW directives, you are not proving consistency. You only need to find ONE sentence that commits the described error to trigger extraction.</rule>\n<rule>Strict Boolean Logic: Evaluate claims as single-pole facts. Ignore complex AND/OR evaluations.</rule>\n</rules>\n</system_directive>"

    scales = target_block["scales"]
    
    # SCORE 1
    s1 = next(s for s in scales if s["score"] == 1)
    s1["claims"][0]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, the quote MUST be in an 'ai:' block. BANNED SOURCES: Never read matches from 'user:' blocks or input fields. STEP 1 (Lexical Anchor): Find explicit rejection markers (e.g., 'Instead of following', 'I will create my own', 'I ignored'). STEP 2 (Bounding Box): Scan the sentence containing the marker. If the author explicitly states they are creating a new rule that contradicts the requested instructions -> ACCEPT. BANNED CONCEPTS: Do not evaluate 'quality' or if the new rule is better. ENFORCEMENT RULE: Document the fabricated constraint in reasoning_trace before extracting the quote.",
        "inverse_evidence": True,
        "aggregation_mode": "EXISTS"
    }]
    s1["claims"][1]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find dogmatic absolute markers (e.g., 'always', '100% guaranteed', 'it is a fact that'). STEP 2 (Bounding Box): Scan the same paragraph. If the absolute claim is made regarding a compliance or archival rule BUT no external framework (ARMA, ISO, law) is cited in that paragraph -> ACCEPT (Flaw proven). BANNED CONCEPTS: Do not accept absolute claims that are mathematically verifiable. ENFORCEMENT RULE: Document the ARMA Integrity violation in reasoning_trace before extracting.",
        "inverse_evidence": True,
        "aggregation_mode": "EXISTS"
    }]
    s1["claims"][2]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find explicit exposure actions (e.g., 'displaying PII', 'sharing password', 'bypassing encryption', 'publicly exposing'). STEP 2 (Bounding Box): Scan the sentence. If a physical action actively exposes sensitive data -> ACCEPT. BANNED CONCEPTS: Do not evaluate theoretical risk, only active exposure actions. ENFORCEMENT RULE: Document the ARMA Protection principle violation in reasoning_trace before extracting.",
        "inverse_evidence": True,
        "aggregation_mode": "EXISTS"
    }]

    # SCORE 2
    s2 = next(s for s in scales if s["score"] == 2)
    s2["claims"][0]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find physical actions of organizing or saving data (e.g., 'stored in', 'saved as', 'archived'). STEP 2 (Bounding Box): Scan the sentence. If an action is taken to store data -> ACCEPT. BANNED CONCEPTS: Do not evaluate if the storage method is 'good' or 'bad'. ENFORCEMENT RULE: Document the mechanical storage action in reasoning_trace before extracting.",
        "inverse_evidence": False,
        "aggregation_mode": "ALL_MUST_COMPLY"
    }]
    s2["claims"][1]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find shortcut markers (e.g., 'to save time', 'we can skip', 'not strictly necessary'). STEP 2 (Bounding Box): Scan the paragraph. If the author explicitly states they are omitting a mandatory step (e.g., ARMA Accountability) for convenience -> ACCEPT. BANNED CONCEPTS: Do not accept justified omissions backed by data. ENFORCEMENT RULE: Document the bypassed rule in reasoning_trace before extracting.",
        "inverse_evidence": True,
        "aggregation_mode": "EXISTS"
    }]
    s2["claims"][2]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find absolute exclusion markers (e.g., 'only focus on', 'ignore everything else'). STEP 2 (Bounding Box): Scan the paragraph. If a single compliance rule is enforced while explicitly stating that another known constraint (e.g., Availability vs Protection) will be ignored -> ACCEPT. BANNED CONCEPTS: Do not accept balanced trade-offs. ENFORCEMENT RULE: Document the explicitly ignored constraint in reasoning_trace before extracting.",
        "inverse_evidence": True,
        "aggregation_mode": "EXISTS"
    }]

    # SCORE 3
    s3 = next(s for s in scales if s["score"] == 3)
    s3["claims"][0]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find procedural compliance markers (e.g., 'step 1 completed', 'followed the checklist'). STEP 2 (Bounding Box): Scan the paragraph. If a process is executed exactly as listed without additional synthesis -> ACCEPT. BANNED CONCEPTS: Do not evaluate 'strategic thinking'. ENFORCEMENT RULE: Document the mechanical step execution in reasoning_trace before extracting.",
        "inverse_evidence": False,
        "aggregation_mode": "ALL_MUST_COMPLY"
    }]
    s3["claims"][1]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find sweeping declarations of success (e.g., 'perfectly secure', 'no issues found', 'fully compliant'). STEP 2 (Bounding Box): Scan the paragraph. If a compliance status is declared flawless WITHOUT mentioning any residual risk or operational trade-off -> ACCEPT (Flaw proven). BANNED CONCEPTS: Do not accept statements that list residual risks. ENFORCEMENT RULE: Document the missing risk acknowledgment in reasoning_trace before extracting.",
        "inverse_evidence": True,
        "aggregation_mode": "EXISTS"
    }]
    s3["claims"][2]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find implicit authority markers (e.g., 'it is common knowledge', 'we always do it this way', 'internally known'). STEP 2 (Bounding Box): Scan the sentence. If a procedural rule is justified solely by internal tradition without citing an external verifiable standard (ARMA Transparency violation) -> ACCEPT. BANNED CONCEPTS: Do not accept explicit external citations. ENFORCEMENT RULE: Document the missing external verifiability in reasoning_trace before extracting.",
        "inverse_evidence": True,
        "aggregation_mode": "EXISTS"
    }]

    # SCORE 4
    s4 = next(s for s in scales if s["score"] == 4)
    s4["claims"][0]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find explicit methodology links (e.g., 'in accordance with', 'following the protocol defined by'). STEP 2 (Bounding Box): Scan the sentence. If an action is explicitly linked to a named guideline or procedure (ARMA Compliance) -> ACCEPT. BANNED CONCEPTS: Do not evaluate the 'quality' of the methodology. ENFORCEMENT RULE: Document the explicit procedural link in reasoning_trace before extracting.",
        "inverse_evidence": False,
        "aggregation_mode": "ALL_MUST_COMPLY"
    }]
    s4["claims"][1]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find boundary definition markers (e.g., 'this applies only to', 'within the scope of', 'excluding'). STEP 2 (Bounding Box): Scan the paragraph. If the operational limits of a compliance rule are explicitly defined -> ACCEPT. BANNED CONCEPTS: Do not accept unbounded absolute rules. ENFORCEMENT RULE: Document the boundary condition in reasoning_trace before extracting.",
        "inverse_evidence": False,
        "aggregation_mode": "ALL_MUST_COMPLY"
    }]
    s4["claims"][2]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find conflict resolution markers (e.g., 'while X requires Y, we must also ensure Z by'). STEP 2 (Bounding Box): Scan the paragraph. If two conflicting operational constraints (e.g., Retention vs Disposition) are mentioned and a specific action is taken to resolve the tension -> ACCEPT. BANNED CONCEPTS: Do not accept rhetorical mentions of conflict without a resolution action. ENFORCEMENT RULE: Document the conflict resolution action in reasoning_trace before extracting.",
        "inverse_evidence": False,
        "aggregation_mode": "ALL_MUST_COMPLY"
    }]

    # SCORE 5
    s5 = next(s for s in scales if s["score"] == 5)
    s5["claims"][0]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find explicit dialectical reasoning ('we evaluated option A, but chose B because'). STEP 2 (Bounding Box): Scan the paragraph. If the author explicitly documents a rejected compliance alternative and provides data-driven reasoning for the final choice -> ACCEPT. BANNED CONCEPTS: Do not accept simple lists of options without rejection reasoning. ENFORCEMENT RULE: Document the rejected alternative in reasoning_trace before extracting.",
        "inverse_evidence": False,
        "aggregation_mode": "ALL_MUST_COMPLY"
    }]
    s5["claims"][1]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find formal citation markers ('according to ARMA principle of', 'ISO standard'). STEP 2 (Bounding Box): Scan the sentence. If a specific external framework is named AND a specific sub-principle or clause is cited to justify a decision -> ACCEPT. BANNED CONCEPTS: Do not accept generic references to 'standards' without naming them. ENFORCEMENT RULE: Document the formal framework name in reasoning_trace before extracting.",
        "inverse_evidence": False,
        "aggregation_mode": "ALL_MUST_COMPLY"
    }]
    s5["claims"][2]["tda_assertions"] = [{
        "tda_id": get_opaque_id(),
        "ai_rule_description": "REQUIRED TARGET: If role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Lexical Anchor): Find integration markers (e.g., 'simultaneously achieving', 'balances X and Y through'). STEP 2 (Bounding Box): Scan the paragraph. If a specific mechanism is described that actively satisfies two typically opposing ARMA principles (e.g., Protection vs Availability) -> ACCEPT. BANNED CONCEPTS: Do not accept claims of balance without describing the physical mechanism. ENFORCEMENT RULE: Document the balancing mechanism in reasoning_trace before extracting.",
        "inverse_evidence": False,
        "aggregation_mode": "ALL_MUST_COMPLY"
    }]

    # Clean up deprecated ai_description from claims to reduce token bloat
    for scale in scales:
        for claim in scale["claims"]:
            if "ai_description" in claim:
                del claim["ai_description"]

    # Save to backups
    import shutil
    import time
    os.makedirs("c:/src/quorum/backend_v2/seed/backups", exist_ok=True)
    backup_path = f"c:/src/quorum/backend_v2/seed/backups/seed_data_backup_{int(time.time())}.json"
    shutil.copy2(seed_path, backup_path)
    print(f"Created backup at {backup_path}")

    # Write back to seed_data.json
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Matrix blk_fb15f8dcf23f4865 has been successfully hardened and saved to seed_data.json.")

if __name__ == "__main__":
    harden_matrix()
