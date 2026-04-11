import json
import os

SEED_FILE = "backend_v2/seed/seed_data.json"

ROOT_APPENDIX = " MANDATORY DIRECTIVE: Default all boolean claim evaluations to FALSE. You must never infer, guess, or synthesize compliance. A claim can only be evaluated as TRUE if you can extract direct, undeniable semantic proof from the text. Give absolutely no benefit of the doubt."

ROW_APPENDIX = " CRITICAL MANDATE: The burden of proof is entirely on the user/document. Default missing explicit context to FALSE."

CLAIM_APPENDIX = " ENFORCEMENT: Evaluate as FALSE immediately unless explicit, documented evidence is provided. Implicit adherence or basic logical correctness MUST be rated as FALSE."

def main():
    if not os.path.exists(SEED_FILE):
        print(f"Error: {SEED_FILE} not found.")
        return

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    mutated_count = 0

    for block in data.get("prompt_blocks", []):
        if block.get("category_id") == "matrix":
            # 1. Update Root AI Description
            root_desc = block.get("ai_description", "")
            if "MANDATORY DIRECTIVE: Default all boolean" not in root_desc:
                block["ai_description"] = root_desc + ROOT_APPENDIX
                mutated_count += 1
            
            # 2. Update Rows
            for row in block.get("rows", []):
                row_desc = row.get("ai_description", "")
                if "The burden of proof is entirely" not in row_desc:
                    row["ai_description"] = row_desc + ROW_APPENDIX
                    mutated_count += 1

            # 3. Update Claims
            for scale in block.get("scales", []):
                for claim in scale.get("claims", []):
                    claim_desc = claim.get("ai_description", "")
                    if "Evaluate as FALSE immediately unless explicit" not in claim_desc:
                        claim["ai_description"] = claim_desc + CLAIM_APPENDIX
                        mutated_count += 1

    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Matrix payload tightening complete. Mutated {mutated_count} elements across all matrices (Levels 1-5).")

if __name__ == "__main__":
    main()
