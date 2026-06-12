import json
import re


def process_disambiguation(desc):
    anti_patterns = []

    # Catch REFRAMING
    if "REFRAMING EXCLUSION" in desc:
        anti_patterns.append({
            "pattern": "it is just a stylistic reframing without logical argument",
            "allows_contextual_excuse": False
        })
    # Catch Regulatory
    elif "Regulatory framework references" in desc:
        anti_patterns.append({
            "pattern": "generic regulatory mention without specific sub-clause",
            "allows_contextual_excuse": False
        })
    else:
        anti_patterns.append({
            "pattern": "violates the explicit disambiguation exclusion rule",
            "allows_contextual_excuse": False
        })

    # Remove the block entirely
    new_desc = re.sub(r"<disambiguation>.*?</disambiguation>\.?", "", desc, flags=re.DOTALL).strip()
    return new_desc, anti_patterns

def process_syntactic_constraint(desc):
    syn_regex = re.compile(r"<syntactic_constraint>(.*?)</syntactic_constraint>", re.DOTALL)
    match = syn_regex.search(desc)

    anti_patterns = []

    if match:
        inner = match.group(1)
        # Extract steps
        step1 = re.search(r"<step1_lexical_anchors>(.*?)</step1_lexical_anchors>", inner, flags=re.DOTALL | re.IGNORECASE)
        step2 = re.search(r"<step2_bounding_box>(.*?)</step2_bounding_box>", inner, flags=re.DOTALL | re.IGNORECASE)
        step3 = re.search(r"<step3_extraction_condition>(.*?)</step3_extraction_condition>", inner, flags=re.DOTALL | re.IGNORECASE)
        step4 = re.search(r"<step4_fail_fast_protocol>(.*?)</step4_fail_fast_protocol>", inner, flags=re.DOTALL | re.IGNORECASE)

        replacement = ""
        if step1:
            replacement += f"STEP 1: {step1.group(1).strip()} "
        if step2:
            replacement += f"STEP 2 (Bounding Box): {step2.group(1).strip()} "
        if step3:
            replacement += f"EXTRACTION CONDITION: {step3.group(1).strip()} "

        if step4:
            s4_text = step4.group(1).strip()
            anti_patterns.append({
                "pattern": f"rejection criteria: {s4_text[:100]}...",
                "allows_contextual_excuse": False
            })

        # Strip the EVALUATION MANDATE prefix
        desc = re.sub(r"EVALUATION MANDATE: You are a deterministic.*?null\.\s*", "", desc, flags=re.DOTALL | re.IGNORECASE)
        new_desc = syn_regex.sub(replacement, desc).strip()
        return new_desc, anti_patterns

    return desc, []

try:
    with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', encoding='utf-8') as f:
        data = json.load(f)

    changes_made = 0

    for cat in ['evaluations', 'matrices']:
        for matrix in data.get(cat, []):
            for claim in matrix.get('claims', []):
                for tda in claim.get('tda_assertions', []):
                    desc = tda.get('concept_description', '')

                    original_desc = desc
                    anti_patterns_to_add = []

                    if '<disambiguation>' in desc:
                        desc, ap1 = process_disambiguation(desc)
                        anti_patterns_to_add.extend(ap1)

                    if '<syntactic_constraint>' in desc:
                        desc, ap2 = process_syntactic_constraint(desc)
                        anti_patterns_to_add.extend(ap2)

                    if original_desc != desc:
                        tda['concept_description'] = desc
                        if anti_patterns_to_add:
                            existing_ap = tda.get('anti_patterns', [])
                            existing_patterns = [ap.get('pattern') for ap in existing_ap]
                            for new_ap in anti_patterns_to_add:
                                if new_ap['pattern'] not in existing_patterns:
                                    existing_ap.append(new_ap)
                            tda['anti_patterns'] = existing_ap
                        changes_made += 1

    if changes_made > 0:
        with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Refactored {changes_made} instances successfully.")
    else:
        print("No legacy instances found to refactor.")

except Exception as e:
    print(f"Error: {e}")
