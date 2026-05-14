import json
import secrets

def generate_opaque_id():
    return f"tda_{secrets.token_hex(8)}"

with open('backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find the specific block
block = next(b for b in data['prompt_blocks'] if b['id'] == 'blk_22e3598e06414409')

# Update Global AI Description with System Directive and Epistemic Anchor
block['ai_description'] = """<system_directive>
<role>EPISTEMIC AUDITOR (ZERO-TRUST)</role>
<task>Evaluate the text for epistemic humility vs. System 1 WYSIATI (What You See Is All There Is) overconfidence.</task>
<mandate>Execute strict lexical scanning. Do not evaluate subjective 'arrogance'. Count data points, locate specific hedging markers, and map exact quotes.</mandate>
<epistemic_anchor>Grounded in Kahneman's Dual Process Theory (System 1 coherence vs. System 2 lazy evaluation) and Floridi's Information Ethics. Absolute claims without immediate empirical data in the same paragraph constitute an epistemic violation.</epistemic_anchor>
</system_directive>"""

# Scale 1
block['scales'][0]['claims'][0]['ai_description'] = "CRITICAL DIRECTIVE: Identify explicitly absolute claims that bypass the WYSIATI limitation without empirical backing."
block['scales'][0]['claims'][0]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the target document. BANNED SOURCES: Reject matches from user inputs or 'user:' prefixes. STEP 1 (Lexical Anchor): Find an absolute certainty marker (e.g., 'undeniably', '100%', 'proven fact'). STEP 2 (Bounding Box): Scan the paragraph containing the marker. STEP 3: If no empirical data is provided within that exact paragraph to justify the claim -> ACCEPT (flaw proven). If empirical data exists -> REJECT. BANNED CONCEPTS: Do not evaluate 'arrogance'.",
    "inverse_evidence": True,
    "aggregation_mode": "EXISTS"
}]

block['scales'][0]['claims'][1]['ai_description'] = "CRITICAL DIRECTIVE: Identify declarations of exhaustive or complete knowledge."
block['scales'][0]['claims'][1]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the target document. BANNED SOURCES: Reject user inputs. STEP 1 (Lexical Anchor): Find declarations of completeness (e.g., 'exhaustive', 'covers everything', 'the only possible'). STEP 2: Document the reasoning. STEP 3: If the text explicitly claims that there are zero unknown variables remaining -> ACCEPT. Otherwise -> REJECT.",
    "inverse_evidence": True,
    "aggregation_mode": "EXISTS"
}]

block['scales'][0]['claims'][2]['ai_description'] = "CRITICAL DIRECTIVE: Identify active dismissal of alternative perspectives without data."
block['scales'][0]['claims'][2]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the target document. BANNED SOURCES: Reject user inputs. STEP 1 (Lexical Anchor): Find dismissive markers towards alternatives (e.g., 'obviously false', 'nonsense', 'irrelevant'). STEP 2 (Bounding Box): Scan the paragraph. STEP 3: If the dismissal occurs without citing an external verifiable source or empirical data -> ACCEPT. Otherwise -> REJECT.",
    "inverse_evidence": True,
    "aggregation_mode": "EXISTS"
}]

# Scale 2
block['scales'][1]['claims'][0]['ai_description'] = "CRITICAL DIRECTIVE: Identify superficial performative hedging."
block['scales'][1]['claims'][0]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the document. BANNED SOURCES: Reject user inputs. STEP 1: Find performative hedging markers (e.g., 'it may be that', 'some might say'). STEP 2: Check the sentence immediately following the hedge. If the following sentence immediately returns to an absolute certainty marker (e.g., 'but ultimately it is a proven fact') -> ACCEPT (performative hedge proven). If it maintains nuance -> REJECT.",
    "inverse_evidence": True,
    "aggregation_mode": "EXISTS"
}]

block['scales'][1]['claims'][1]['ai_description'] = "CRITICAL DIRECTIVE: Identify immediate rationalization of constraints."
block['scales'][1]['claims'][1]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the document. STEP 1: Find a limitation acknowledgment (e.g., 'a limitation is'). STEP 2: Scan the next two sentences. If a dismissive marker (e.g., 'however', 'regardless') immediately rationalizes away the limitation without citing new data -> ACCEPT. Otherwise -> REJECT.",
    "inverse_evidence": True,
    "aggregation_mode": "EXISTS"
}]

block['scales'][1]['claims'][2]['ai_description'] = "CRITICAL DIRECTIVE: Identify failure to explore named alternatives."
block['scales'][1]['claims'][2]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the document. STEP 1: Find a named alternative model or theory. STEP 2 (Bounding Box): Scan the same paragraph. If the alternative is mentioned but the paragraph contains exactly 0 counter-arguments or comparative data points -> ACCEPT. Otherwise -> REJECT. BANNED CONCEPTS: Do not evaluate 'depth', simply count the data points.",
    "inverse_evidence": True,
    "aggregation_mode": "EXISTS"
}]

# Scale 3
block['scales'][2]['claims'][0]['ai_description'] = "CRITICAL DIRECTIVE: Verify baseline neutral tone without absolute claims."
block['scales'][2]['claims'][0]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the document. STEP 1: Find a factual claim. STEP 2: Check for qualifying terms (e.g., 'indicates', 'suggests', 'is correlated'). If present AND absolute markers (e.g., 'proves', 'always') are strictly absent in the same sentence -> ACCEPT. Otherwise -> REJECT.",
    "inverse_evidence": False,
    "aggregation_mode": "ALL_MUST_COMPLY"
}]

block['scales'][2]['claims'][1]['ai_description'] = "CRITICAL DIRECTIVE: Identify purely passive informational delivery."
block['scales'][2]['claims'][1]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the document. STEP 1: Find a paragraph containing statistical or factual reporting. STEP 2: Count the first-person pronouns ('I', 'we') or explicit self-reflective verbs ('assume', 'interpret'). If the count is exactly 0 -> ACCEPT (passive delivery proven). If greater than 0 -> REJECT.",
    "inverse_evidence": False,
    "aggregation_mode": "ALL_MUST_COMPLY"
}]

block['scales'][2]['claims'][2]['ai_description'] = "CRITICAL DIRECTIVE: Identify uncritical acceptance of data sources."
block['scales'][2]['claims'][2]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the document. STEP 1: Find a citation or data source introduction (e.g., 'according to', 'data shows'). STEP 2 (Bounding Box): Scan the same paragraph. If terms like 'bias', 'margin of error', or 'limitation' are completely missing -> ACCEPT. Otherwise -> REJECT.",
    "inverse_evidence": False,
    "aggregation_mode": "ALL_MUST_COMPLY"
}]

# Scale 4
block['scales'][3]['claims'][0]['ai_description'] = "CRITICAL DIRECTIVE: Verify explicit recognition of methodological constraints."
block['scales'][3]['claims'][0]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the document. STEP 1: Find explicit boundary setting markers (e.g., 'this does not apply to', 'a key constraint is'). STEP 2: Document the constraint before extracting the exact_quote. If found -> ACCEPT. Otherwise -> REJECT.",
    "inverse_evidence": False,
    "aggregation_mode": "ALL_MUST_COMPLY"
}]

block['scales'][3]['claims'][1]['ai_description'] = "CRITICAL DIRECTIVE: Verify explicit boundary setting."
block['scales'][3]['claims'][1]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the document. STEP 1: Find contextual qualifiers (e.g., 'in this specific context', 'under these conditions'). STEP 2: Extract the exact_quote containing the qualifier. If found -> ACCEPT.",
    "inverse_evidence": False,
    "aggregation_mode": "ALL_MUST_COMPLY"
}]

block['scales'][3]['claims'][2]['ai_description'] = "CRITICAL DIRECTIVE: Verify engagement with alternative perspectives."
block['scales'][3]['claims'][2]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the document. STEP 1: Find a counter-hypothesis (e.g., 'an alternative explanation', 'critics might argue'). STEP 2 (Bounding Box): Scan the same paragraph for external data or citations used to address this counter-hypothesis. If found -> ACCEPT.",
    "inverse_evidence": False,
    "aggregation_mode": "ALL_MUST_COMPLY"
}]

# Scale 5
block['scales'][4]['claims'][0]['ai_description'] = "CRITICAL DIRECTIVE: Verify systemic self-scrutiny."
block['scales'][4]['claims'][0]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the document. STEP 1: Locate a section dedicated to methodology or limitations. STEP 2: Find at least three distinct listed data gaps or foundational assumptions. Document them step-by-step. If 3 or more exist -> ACCEPT. If less than 3 -> REJECT.",
    "inverse_evidence": False,
    "aggregation_mode": "ALL_MUST_COMPLY"
}]

block['scales'][4]['claims'][1]['ai_description'] = "CRITICAL DIRECTIVE: Verify thorough dismantling of counterarguments."
block['scales'][4]['claims'][1]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the document. STEP 1: Locate a risk assessment or 'pre-mortem' structure. STEP 2: Find explicit dismantling of a risk using a verifiable external citation or empirical data. If both the risk and the empirical counter-data are found -> ACCEPT.",
    "inverse_evidence": False,
    "aggregation_mode": "ALL_MUST_COMPLY"
}]

block['scales'][4]['claims'][2]['ai_description'] = "CRITICAL DIRECTIVE: Verify mandatory source anchoring and visible cognitive friction."
block['scales'][4]['claims'][2]['tda_assertions'] = [{
    "tda_id": generate_opaque_id(),
    "ai_rule_description": "REQUIRED TARGET: Scan the document. STEP 1: Find explicit external anchoring for uncertainty (e.g., 'due to X, as noted by [Source]'). STEP 2: Map the cognitive friction. If an external citation is used specifically to justify why a variable remains unknown -> ACCEPT.",
    "inverse_evidence": False,
    "aggregation_mode": "ALL_MUST_COMPLY"
}]

with open('backend_v2/seed/seed_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
