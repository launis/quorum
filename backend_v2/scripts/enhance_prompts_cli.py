import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Adjust based on backend architecture
import litellm
from litellm import acompletion

from backend_v2.settings import get_settings

settings = get_settings()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PromptEnhancer")

SEED_DATA_PATH = os.path.join(PROJECT_ROOT, "backend_v2", "seed", "seed_data.json")

# Set up litellm based on the project's Vertex AI / OpenAI settings
import os

litellm.vertex_location = getattr(settings, "vertex_location", os.getenv("VERTEX_LOCATION", "europe-west1"))

async def enhance_prompt_block(sem, pb, model="vertex_ai/gemini-2.5-pro"):
    """Use LLM to rewrite and translate the PromptBlock to highly-critical English."""
    async with sem:
        try:
            # Gather all Finnish texts
            fi_label = pb.get("label", {}).get("translations", {}).get("fi", "")
            fi_desc = pb.get("description", {}).get("translations", {}).get("fi", "")

            fi_scales = []
            for s in pb.get("scales", []):
                fi_score = s.get("score")
                fi_s_name = s.get("name", {}).get("translations", {}).get("fi", "")
                fi_s_claim = s.get("claims", [{}])[0].get("translations", {}).get("fi", "")
                fi_scales.append({
                    "score": fi_score,
                    "name": fi_s_name,
                    "claim": fi_s_claim
                })

            payload = {
                "id": pb.get("id"),
                "label": fi_label,
                "description": fi_desc,
                "scales": fi_scales
            }

            system_instruction = """
            You are an elite AI Alignment Engineer and Prompt Optimizer.
            Your task is to translate and ENHANCE the following Finnish evaluation matrix / instructions into perfectly engineered, uncompromising, and highly critical English.
            
            RULES FOR REWRITING:
            1. Use authoritative, structural keywords in the 'description_en', such as 'ROLE:', 'TASK:', 'RULE:', 'MANDATE:', 'CRITICAL INSTRUCTION:'.
            2. For the grading scales ('scales'), the English translation must reflect extreme strictness (Zero-Trust architecture). 
               - A high score (e.g., 5 or 100) MUST require absolute theoretical and logical perfection. 
               - A low score MUST savagely penalize performative language, logical fallacies, or lack of grounding.
            3. The 'label_en' must be extremely crisp, capitalized, and professional (e.g., 'EPISTEMIC HUMILITY').
            4. Make sure your output is purely valid JSON without any markdown formatting or code blocks.
            
            Example output format EXACTLY:
            {
                "label_en": "EPISTEMIC HUMILTY",
                "description_en": "ROLE: AUDITOR\\nTASK: ...\\nMANDATE: ...",
                "scales_en": [
                    {"score": 1, "name_en": "FAIL", "claim_en": "Absolute failure. No evidence."},
                    {"score": 5, "name_en": "PERFECT", "claim_en": "Flawless theoretical grounding."}
                ]
            }
            """

            user_msg = f"Enhance this block:\n{json.dumps(payload, ensure_ascii=False)}"

            response = await acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_msg}
                ],
                response_format={"type": "json_object"}
            )

            resp_text = response.choices[0].message.content
            if resp_text.startswith("```json"):
                resp_text = resp_text[7:]
            if resp_text.endswith("```"):
                resp_text = resp_text[:-3]

            enhanced = json.loads(resp_text.strip())

            # Update the PromptBlock in place
            if "translations" not in pb["label"]: pb["label"]["translations"] = {}
            if "translations" not in pb["description"]: pb["description"]["translations"] = {}

            pb["label"]["translations"]["en"] = enhanced.get("label_en", "")
            pb["description"]["translations"]["en"] = enhanced.get("description_en", "")

            if pb.get("scales"):
                enhanced_scales = {str(item["score"]): item for item in enhanced.get("scales_en", [])}
                for s in pb["scales"]:
                    sc_val = str(s.get("score"))
                    if sc_val in enhanced_scales:
                        en_name = enhanced_scales[sc_val].get("name_en", "")
                        en_claim = enhanced_scales[sc_val].get("claim_en", "")

                        if "name" not in s or s["name"] is None:
                            s["name"] = {"default_locale": "fi", "translations": {"fi": en_name}} # Placeholder for missing struct
                        if "translations" not in s["name"]: s["name"]["translations"] = {}
                        s["name"]["translations"]["en"] = en_name

                        if "claims" not in s or not s["claims"]:
                            s["claims"] = [{"default_locale": "fi", "translations": {"fi": en_claim}}]
                        if "translations" not in s["claims"][0]: s["claims"][0]["translations"] = {}
                        s["claims"][0]["translations"]["en"] = en_claim

            logger.info(f"Successfully enhanced: {pb.get('id')}")
            return True

        except Exception as e:
            logger.error(f"Failed to enhance {pb.get('id')}: {e}")
            return False

async def main():
    with open(SEED_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    prompt_blocks = data.get("prompt_blocks", [])
    sem = asyncio.Semaphore(15) # Concurrent API calls

    tasks = []
    for pb in prompt_blocks:
        tasks.append(enhance_prompt_block(sem, pb))

    logger.info(f"Starting enhancement for {len(tasks)} PromptBlocks...")
    results = await asyncio.gather(*tasks)

    success_count = sum(1 for r in results if r)
    logger.info(f"Finished. Successfully enhanced {success_count}/{len(tasks)} PromptBlocks.")

    # Save back to seed data
    with open(SEED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')

if __name__ == "__main__":
    asyncio.run(main())
