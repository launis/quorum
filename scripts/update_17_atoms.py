import json

seed_file = r'c:\src\quorum\backend_v2\seed\seed_data.json'

with open(seed_file, encoding='utf-8') as f:
    data = json.load(f)

global_mandate = "EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. "

updates = {
    'tda_b7dfe23403db4db5b92a29a8bda9957c': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find generic listing conjunctions (e.g., 'and', 'also', 'in addition'). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan the immediate sentence containing the anchor.</step2_bounding_box> "
        "<step3_extraction_condition>Extract the exact quote IF AND ONLY IF two nouns or noun phrases are joined by the conjunction WITHOUT any relational verb describing their interaction in the same sentence.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If ANY verb exists in the sentence that defines a causal or operational relationship between the two nouns, you MUST return JSON null. Verify only syntax, do not judge 'importance'.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_eb266643b83b48bbab94a041b6d12f6d': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find EXACT phrase matches in the document's language (the Target Locale) representing any of the concepts: 'extract directly', 'exact quote', 'do not invent yourself', 'based only on', 'do not hallucinate'. If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan ONLY user prompts.</step2_bounding_box> "
        "<step3_extraction_condition>Extract the exact sentence containing the physical anchor.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>PURE LEXICAL VERIFICATION: Semantic stretching is strictly banned. Synonyms or 'close enough' phrases MUST BE REJECTED. Do not evaluate user intent.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_1473cecaeb4c495c9bd0d28710e602b4': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find an explicit user instruction with at least two specific constraints (e.g., format, length, tone).</step1_lexical_anchors> "
        "<step2_bounding_box>Scan the NEXT user response.</step2_bounding_box> "
        "<step3_extraction_condition>The user MUST explicitly verify those EXACT constraints (e.g., explicitly stating that Constraint A was met, but Constraint B failed).</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the subsequent user response lacks explicit verification of the previous constraints, or is just a generic follow-up, you MUST return JSON null. Implicit verification is BANNED.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_049eb80a94164c519d5a322d55499707': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find friction markers (such as equivalents of 'This is difficult because', 'The risk here is', 'We must balance' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan the chronological sequence.</step2_bounding_box> "
        "<step3_extraction_condition>The friction MUST be physically written BEFORE the action or generation it refers to.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the friction marker is found ONLY in a post-generation reflection or retrospective analysis, you MUST return JSON null. We only accept pre-meditated friction.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_84b7784951c84e948c131c189261f564': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find limitation markers (such as equivalents of 'a limitation is', 'weakness', 'flaw', 'shortcoming' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan the next two sentences.</step2_bounding_box> "
        "<step3_extraction_condition>Extract the quote IF AND ONLY IF a limitation anchor is followed by a dismissive transition word (such as equivalents of 'however', 'regardless', 'anyway' translated into the document's language) that rationalizes away the limitation.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the transition word is missing, or if the text provides new empirical data to solve the limitation instead of dismissing it, you MUST return JSON null.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_19e1957773db4cfd820cb167ae1d8ec3': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find epistemic boundary markers (such as equivalents of 'may not apply', 'exception', 'edge case', 'out of scope', 'limitation' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> "
        "<step3_extraction_condition>The text MUST physically identify a scenario where its OWN logic or model fails or is limited.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the text only describes external problems or general crises, and does not explicitly limit its own analytical scope, you MUST return JSON null. Implicit modesty is BANNED.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_a946688e5f5549e8ac30584d1a02ad26': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Target paragraphs with statistical/factual reporting.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan for first-person markers (such as first-person pronouns, possessive suffixes, or self-reflective verbs translated/adapted into the document's language, e.g., 'I', 'we' in English, or '-mme', '-ni', '-n' in Finnish).</step2_bounding_box> "
        "<step3_extraction_condition>You MUST extract the text IF AND ONLY IF the count of first-person markers is EXACTLY ZERO.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If EVEN ONE first-person pronoun, possessive suffix, or self-reflective verb exists, the count is > 0. In that case, you MUST return JSON null. DO NOT EXTRACT.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_680dc2c703b3425fa0b0d943dbd5af16': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find a structural blueprint ('must contain', 'requirements are'). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Target ONLY 'user:' blocks. Scan the paragraph.</step2_bounding_box> "
        "<step3_extraction_condition>The SAME paragraph MUST ALSO contain constraint vocabulary (such as equivalents of 'conflict', 'trade-off', 'issue', 'balance', 'limitation' translated into the document's language).</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If constraint vocabulary is missing from the paragraph containing the blueprint, you MUST return JSON null. Do not evaluate intent.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_003f932abb9642fc8c3147b04fac95c5': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find absolute completeness markers (such as equivalents of 'exhaustive', 'covers everything', 'the only possible', 'only way' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> "
        "<step3_extraction_condition>Extract the sentence IF AND ONLY IF it explicitly claims there are zero unknown variables or alternatives remaining.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the text is just a selected summary (e.g. 'three key facts') or uses generic rhetorical exaggeration without claiming absolute completeness, return JSON null.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_24bdc98709e84de984aabd67b597239b': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find procedural sequential markers (such as equivalents of 'step 1', 'checklist', 'first', '1.', '2.' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Target ONLY 'ai:' blocks. Scan the paragraph.</step2_bounding_box> "
        "<step3_extraction_condition>Extract the paragraph IF AND ONLY IF it contains these procedural markers AND LACKS any synthesis/deduction verbs (such as equivalents of 'analyzed', 'concluded', 'therefore', 'means' translated into the document's language).</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the paragraph contains BOTH procedural markers AND synthesis verbs, you MUST return JSON null.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_4ba32055738247d28e00a597f505ce9e': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find binary reduction markers (such as equivalents of 'either', 'or', 'simply boils down to', 'only way' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> "
        "<step3_extraction_condition>Extract the quote IF the text uses these markers to force a complex situation into exactly one or two absolute options.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the text acknowledges alternative paths, middle grounds, or nuance, you MUST return JSON null.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_8ecd3f17b3984e4fa1bb6a8cb5576b65': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find absolute causal words (such as equivalents of 'only reason', 'entirely due to', 'only way' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> "
        "<step3_extraction_condition>Extract the quote IF a highly complex outcome is attributed to a SINGLE cause.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the text acknowledges multiple factors or nuances, or if the outcome is simple, return JSON null. Do not evaluate nuance.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_715eb98a6f4a4a1e944db99f5eaaded9': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find epistemic boundary markers (such as equivalents of 'may be inaccurate', 'verify independently', 'limitations', 'hallucination' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> "
        "<step3_extraction_condition>Extract the quote IF the AI explicitly outputs a disclaimer acknowledging its own limitations.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the user writes the reflection/limitation, or if the text just discusses external data errors, you MUST return JSON null. The disclaimer MUST come from the AI itself.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_f29c602444b446a3a6973aa9953a0b01': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find contextual qualifiers (such as equivalents of 'in this specific context', 'under these conditions', 'for this target audience' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan the document.</step2_bounding_box> "
        "<step3_extraction_condition>Extract the quote containing the qualifier.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the text only describes general environments (e.g. 'in modern times') but does not use them to restrict a factual claim, you MUST return JSON null.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_1361cf5ec5b5420c905cd2a1f80893a7': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find explicit retrospective claims of intent (such as equivalents of 'that is what I meant', 'I intended', 'my original goal was' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Target ONLY 'user:' blocks. Read the preceding instructions.</step2_bounding_box> "
        "<step3_extraction_condition>Extract the retrospective claim IF AND ONLY IF the preceding text DOES NOT physically contain the parameters being claimed.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the prior text ALREADY contains the requested parameters (i.e. the user did actually ask for it earlier), you MUST return JSON null. We only extract false post-hoc rationalizations.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_bd85f009b0fb4f7899b40ff0e763dee7': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find tension markers between metrics and goals (such as equivalents of 'this metric is flawed because', 'the metric versus the actual goal' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> "
        "<step3_extraction_condition>Extract the quote IF the user explicitly questions the reliability of a proxy metric in relation to the true qualitative goal.</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the text merely tracks a metric without questioning its validity, you MUST return JSON null.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    ),
    'tda_ac3b078498e048889ad3bc46b634c2ee': (
        "<syntactic_constraint> "
        "<step1_lexical_anchors>Find an academic citation, mathematical theorem, or academic framework. If absent, FAIL FAST and return null.</step1_lexical_anchors> "
        "<step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> "
        "<step3_extraction_condition>Extract the sentence IF AND ONLY IF the logic is explicitly tethered to this source (e.g., actively applying a rule from the source).</step3_extraction_condition> "
        "<step4_fail_fast_protocol>If the source is just named or referenced passively without actively applying its logic, you MUST return JSON null.</step4_fail_fast_protocol> "
        "</syntactic_constraint>"
    )
}

count = 0

def process_node(node):
    global count
    if isinstance(node, dict):
        if 'tda_id' in node and node['tda_id'] in updates:
            node['ai_rule_description'] = global_mandate + updates[node['tda_id']]
            count += 1
        for _k, v in node.items():
            process_node(v)
    elif isinstance(node, list):
        for item in node:
            process_node(item)

process_node(data)

with open(seed_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Successfully updated {count} TDA rules in seed_data.json')
