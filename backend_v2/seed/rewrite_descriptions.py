import asyncio
import json

from dotenv import load_dotenv

load_dotenv(r"c:\src\quorum\backend_v2\.env")

from litellm import acompletion
from pydantic import BaseModel


class DescriptionRewrite(BaseModel):
    fi_descriptive: str
    en_descriptive: str

async def rewrite_block(block, semaphore):
    async with semaphore:
        fi_orig = block.get('description', {}).get('translations', {}).get('fi', '')
        en_orig = block.get('description', {}).get('translations', {}).get('en', '')
        ai_desc = block.get('ai_description', '')

        prompt = f"""
You are rewriting prompt block descriptions for a UI.
Currently, the descriptions were written as commands for an LLM (e.g. "Arvioi argumentti...").
We have now separated the LLM command into `ai_description` which is:
{ai_desc}

Your task is to rewrite the short UI description into a clean, professional, DESCRIPTIVE non-command format. 
For example, instead of "Arvioi argumentin laatua...", write "Analysoi argumentin loogista rakennetta ja kestävyyttä."
Instead of "Evaluate the argument...", write "Analyzes the logical structure and robustness of the argument."

Original FI: {fi_orig}
Original EN: {en_orig}

Provide the descriptive text in both Finnish (fi_descriptive) and English (en_descriptive).
Make them short (1-2 sentences), professional, and neutral.
"""

        try:
            response = await acompletion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format=DescriptionRewrite,
            )
            res = DescriptionRewrite.model_validate_json(response.choices[0].message.content)

            if "description" not in block:
                block["description"] = {"default_locale": "fi", "translations": {}}
            if "translations" not in block["description"]:
                block["description"]["translations"] = {}

            block["description"]["translations"]["fi"] = res.fi_descriptive
            block["description"]["translations"]["en"] = res.en_descriptive
            print(f"Rewrote: {fi_orig[:30]}... -> {res.fi_descriptive[:30]}...")
            return block
        except Exception as e:
            print(f"Error processing block {block.get('id')}: {e}")
            return block

async def main():
    path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    blocks = data.get("prompt_blocks", [])
    semaphore = asyncio.Semaphore(10)

    tasks = [rewrite_block(b, semaphore) for b in blocks if "description" in b]

    await asyncio.gather(*tasks)

    # Save back
    import shutil
    shutil.copy2(path, path + ".bak_rewrite")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Finished rewriting {len(tasks)} blocks.")

if __name__ == "__main__":
    asyncio.run(main())
