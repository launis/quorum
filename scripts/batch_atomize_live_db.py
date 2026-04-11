import asyncio
import logging
import sys
import os

# Adjust python path if run from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.atomizer import PromptAtomizer
from backend_v2.exceptions import AppException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BatchAtomizer")

async def main() -> None:
    logger.info("Starting batch atomization of active DB...")
    repo = UnifiedWorkflowRepository()
    
    all_blocks = await repo.get_all("prompt_blocks")
    logger.info(f"Found {len(all_blocks)} total prompt blocks in db.")
    
    modified_count = 0
    for block_data in all_blocks:
        block = PromptBlock.model_validate(block_data)
        if block.scales:
            logger.info(f"Processing block: {block.id} ('{block.slug}')")
            try:
                updated_block = await PromptAtomizer.atomize_prompt_block(block, repository=repo, is_test=False)
                
                # Bypass StudioService permissions by using repo directly for this batch migration
                dump = updated_block.model_dump(mode="json")
                if "id" not in dump:
                    dump["id"] = updated_block.id
                    
                await repo.create_raw("prompt_blocks", dump)
                modified_count += 1
                logger.info(f"-> Successfully atomized and saved {block.id}")
            except Exception as e:
                logger.error(f"-> Failed to atomize {block.id}: {e}")
                
    logger.info(f"Batch atomization complete. Modified {modified_count} blocks.")

if __name__ == "__main__":
    asyncio.run(main())
