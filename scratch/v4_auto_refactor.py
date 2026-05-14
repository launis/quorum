import asyncio
import json
import logging
from pathlib import Path
import sys

from dotenv import load_dotenv
import litellm
from pydantic import BaseModel, Field

# Load environment variables (API Keys)
load_dotenv(Path("c:/src/quorum/.env"))

# Import Pydantic models for validation
sys.path.append('c:/src/quorum')
from backend_v2.models.v2_core import PromptBlock

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class V4RuleOutput(BaseModel):
    v4_rule: str = Field(description="The refactored AI rule strictly following V4 mandates.")

async def rewrite_rule(old_rule: str, epic_context: str) -> str:
    system_prompt = f"""
You are the elite Antigravity Prompt Architect.
Your task is to refactor legacy 'AI Rules' to strictly follow the 'Zero-Interpretation Doctrine' (V4 Mandates).

CONTEXT (Epic 51):
{epic_context}

STRICT MANDATES FOR THE NEW RULE:
1. Native English: The rule MUST be written entirely in English.
2. Target Enforcement: Start the rule with exactly: "REQUIRED TARGET: Scan ONLY the Target Data, regardless of format. BANNED SOURCES: Never read matches from user input fields, instructions or reflections."
3. Subjectivity Ban: Remove all subjective adjectives (e.g., 'masterful', 'flawless', 'generic', 'robust'). Replace them with structural or quantitative limits.
4. Banned Logic: Include a "BANNED CONCEPTS:" or "BANNED LOGIC:" section to explicitly forbid LLM interpretation or assumption.
5. Lexical Anchor: Include "STEP 1 (Lexical Anchor):" instructing the LLM to find a specific absolute word or physical structure (e.g., 'Look for absolute terms like...').
6. Bounding Box: Include "STEP 2 (Bounding Box):" instructing the LLM to scan a bounded area (e.g., 'Scan the paragraph') and evaluate a strictly objective condition. "If X is present without Y -> ACCEPT. Otherwise -> REJECT."
7. Keep it under 100 words. It must be highly mechanical.

Output ONLY the validated JSON containing the "v4_rule".
"""
    try:
        response = await litellm.acompletion(
            model="gemini/gemini-2.5-pro", # Can be changed to gpt-4o if preferred
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Old Rule to refactor:\n{old_rule}"}
            ],
            response_format={"type": "json_object", "schema": V4RuleOutput.model_json_schema()}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return data["v4_rule"]
    except Exception as e:
        logger.error(f"Failed to rewrite rule: {e}")
        return old_rule

async def main():
    seed_path = Path("c:/src/quorum/backend_v2/seed/seed_data.json")
    tracker_path = Path("c:/src/quorum/scratch/extracted_rules.json")
    epic_path = Path("c:/src/quorum/docs/epic/epic51_seed_data_tda_refactor.md")
    
    if not tracker_path.exists():
        logger.error("extracted_rules.json not found! Run the extraction script first.")
        return
        
    with open(epic_path, 'r', encoding='utf-8') as f:
        epic_context = f.read()

    with open(tracker_path, 'r', encoding='utf-8') as f:
        atoms_to_fix = json.load(f)

    is_dry_run = "--dry-run" in sys.argv
    if is_dry_run:
        logger.info("DRY RUN MODE ENABLED. Taking a sample of 3 atoms.")
        atoms_to_fix = atoms_to_fix[:3]

    logger.info(f"Loaded {len(atoms_to_fix)} atoms to refactor.")

    # Concurrency control
    semaphore = asyncio.Semaphore(5)
    
    async def process_atom(atom):
        async with semaphore:
            logger.info(f"Refactoring {atom['id']}...")
            new_rule = await rewrite_rule(atom['old_rule'], epic_context)
            return {"tda_id": atom['id'], "new_rule": new_rule}
            
    # Run all requests
    tasks = [process_atom(atom) for atom in atoms_to_fix]
    results = await asyncio.gather(*tasks)
    
    v4_map = {r["tda_id"]: r["new_rule"] for r in results}
    
    # Injection Phase
    with open(seed_path, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)
        
    updated_count = 0
    for block in seed_data.get("prompt_blocks", []):
        for scale in block.get("scales", []):
            for claim in scale.get("claims", []):
                for tda in claim.get("tda_assertions", []):
                    if tda.get("tda_id") in v4_map:
                        tda["ai_rule_description"] = v4_map[tda["tda_id"]]
                        updated_count += 1
                        
    logger.info(f"Injected {updated_count} hardened V4 rules into memory.")
    
    # Pydantic Validation
    logger.info("Running Pydantic Zero-Compromise Validation...")
    try:
        for block in seed_data.get("prompt_blocks", []):
            PromptBlock(**block)
        logger.info("Pydantic validation PASSED. Schema is perfectly intact.")
    except Exception as e:
        logger.error(f"Pydantic validation FAILED! Aborting save. Error: {e}")
        return
        
    if is_dry_run:
        dry_run_output = "c:/src/quorum/scratch/dry_run_output.json"
        with open(dry_run_output, 'w', encoding='utf-8') as f:
            json.dump(v4_map, f, indent=2, ensure_ascii=False)
        logger.info(f"DRY RUN COMPLETE. Check {dry_run_output} to see how the rules were rewritten.")
        logger.info("To run for real on all 43 atoms, execute the script without --dry-run")
    else:
        # Save to disk
        with open(seed_path, 'w', encoding='utf-8') as f:
            json.dump(seed_data, f, indent=2, ensure_ascii=False)
            
        logger.info("Successfully saved seed_data.json. Refactoring complete!")

if __name__ == "__main__":
    asyncio.run(main())
