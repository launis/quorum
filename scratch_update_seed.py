import json


def update_seed_data():
    file_path = "c:\\src\\quorum\\backend_v2\\seed\\seed_data.json"

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for block in data.get("prompt_blocks", []):
        if block.get("category_id") == "matrix":
            for scale in block.get("scales", []):
                for claim in scale.get("claims", []):
                    for assertion in claim.get("tda_assertions", []):

                        instruction = (assertion.get("extraction_rule", "") + " " + assertion.get("anchor_target", "")).lower()

                        # Generate abstract contrastive examples (X, Y, Z)
                        if "causal" in instruction or "mechanism" in instruction or "connect" in instruction or "link" in instruction:
                            ce = 'ACCEPTABLE: "X affects Y via mechanism Z" (Abstract universal mechanism).\nUNACCEPTABLE: "X is associated with Y" (Lacks explicit mechanism/causality).'
                        elif "empirical" in instruction or "data" in instruction or "evidence" in instruction or "citation" in instruction:
                            ce = 'ACCEPTABLE: "Claim X is supported by explicit data point Y" (Abstract universal example).\nUNACCEPTABLE: "Claim X is true because of common sense" (Lacks empirical data).'
                        elif "counter-argument" in instruction or "rebuttal" in instruction or "dismiss" in instruction or "opposing" in instruction:
                            ce = 'ACCEPTABLE: "X is argued, but Y provides evidence otherwise" (Abstract universal rebuttal).\nUNACCEPTABLE: "X is completely wrong" (Dismissive without counter-data).'
                        elif "certainty" in instruction or "absolute" in instruction or "dogmatic" in instruction:
                            ce = 'ACCEPTABLE: "X is absolutely the only way to achieve Y" (Abstract dogmatic statement).\nUNACCEPTABLE: "X is absolutely the only way to achieve Y, based on Z" (Contains external backing).'
                        elif "qualifier" in instruction or "conditional" in instruction or "probability" in instruction:
                            ce = 'ACCEPTABLE: "X might occur under condition Y" (Abstract qualifier).\nUNACCEPTABLE: "X will definitely occur" (Lacks qualifier).'
                        elif "anecdote" in instruction or "personal" in instruction:
                            ce = 'ACCEPTABLE: "Individual X experienced Y, so society must do Z" (Abstract anecdotal leap).\nUNACCEPTABLE: "Study X shows Y, so society must do Z" (Rigorous backing, not anecdote).'
                        else:
                            ce = 'ACCEPTABLE: "X directly results in Y" (Abstract universal causal link).\nUNACCEPTABLE: "X and Y exist" (Lacks strict linkage).'

                        assertion["contrastive_example"] = ce
                        count += 1

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {count} assertions with abstract X/Y/Z contrastive examples.")

if __name__ == "__main__":
    update_seed_data()
