import json


def harden_causal_matrix():
    seed_path = "backend_v2/seed/seed_data.json"

    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    for block in data.get("prompt_blocks", []):
        if block.get("id") == "blk_c5804a9143c34cb1":
            # Score 1 claims
            for claim in block["scales"][0]["claims"]:
                claim["ai_description"] = claim["ai_description"].replace("CRITICAL DIRECTIVE:", "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE.")
                for tda in claim["tda_assertions"]:
                    tda["ai_rule_description"] = tda["ai_rule_description"].replace("CRITICAL DIRECTIVE:", "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE.")

            # Score 2 claims
            for claim in block["scales"][1]["claims"]:
                claim["ai_description"] = claim["ai_description"].replace("CRITICAL DIRECTIVE:", "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE.")
                for tda in claim["tda_assertions"]:
                    tda["ai_rule_description"] = tda["ai_rule_description"].replace("CRITICAL DIRECTIVE:", "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE.")

            # Score 5 claims
            # Claim 1: Isolation
            c0 = block["scales"][4]["claims"][0]
            c0["ai_description"] = c0["ai_description"].replace("CRITICAL DIRECTIVE:", "ENFORCEMENT RULE: SYSTEM 2 REQUIREMENT.")
            c0["tda_assertions"][0]["ai_rule_description"] = c0["tda_assertions"][0]["ai_rule_description"].replace("CRITICAL DIRECTIVE:", "ENFORCEMENT RULE: SYSTEM 2 REQUIREMENT.")

            # Claim 2: Counterfactual (already mentions System 2)
            c1 = block["scales"][4]["claims"][1]
            c1["ai_description"] = c1["ai_description"].replace("CRITICAL DIRECTIVE:", "ENFORCEMENT RULE: SYSTEM 2 REQUIREMENT.")
            c1["tda_assertions"][0]["ai_rule_description"] = c1["tda_assertions"][0]["ai_rule_description"].replace("CRITICAL DIRECTIVE:", "ENFORCEMENT RULE: SYSTEM 2 REQUIREMENT.")

            # Claim 3: Causal chain anchored
            c2 = block["scales"][4]["claims"][2]
            c2["ai_description"] = c2["ai_description"].replace("CRITICAL DIRECTIVE:", "ENFORCEMENT RULE: MANDATORY SOURCE ANCHORING.")
            c2["tda_assertions"][0]["ai_rule_description"] = c2["tda_assertions"][0]["ai_rule_description"].replace("CRITICAL DIRECTIVE:", "ENFORCEMENT RULE: MANDATORY SOURCE ANCHORING.")
            break

    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("Successfully hardened blk_c5804a9143c34cb1")

if __name__ == "__main__":
    harden_causal_matrix()
