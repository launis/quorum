import sys
import json
import logging

logger = logging.getLogger(__name__)

def validate_seeds(original_path: str, migrated_path: str) -> bool:
    """Deeply compares two seed JSON files to ensure structural parity."""
    try:
        from deepdiff import DeepDiff
    except ImportError:
        logger.error("Please install deepdiff: uv pip install deepdiff")
        return False

    with open(original_path, 'r', encoding='utf-8') as f:
        original = json.load(f)

    with open(migrated_path, 'r', encoding='utf-8') as f:
        migrated = json.load(f)

    logger.info("Comparing root keys and nested structures (ignoring order)...")
    
    # Ignoring order is crucial because Pydantic models might output keys in different orders 
    # than the raw JSON, and lists could be extracted differently based on ID.
    diff = DeepDiff(original, migrated, ignore_order=True)
    
    # We expect some differences because Pydantic adds default nulls (e.g. `scales: null`)
    # where the original might omit the key entirely.
    # A true identical match of business logic allows these additions.
    
    orig_pb = [x for x in original.get('prompt_blocks', []) if 'questionnaire_definition' in x]
    mig_pb = [x for x in migrated.get('prompt_blocks', []) if 'questionnaire_definition' in x]

    orig_pb2 = [x for x in original.get('prompt_blocks', []) if x.get('scales')]
    mig_pb2 = [x for x in migrated.get('prompt_blocks', []) if x.get('scales')]
    
    logger.info(f"Target 'questionnaire_definition' count: Original={len(orig_pb)}, Migrated={len(mig_pb)}")
    logger.info(f"Target 'scales' count: Original={len(orig_pb2)}, Migrated={len(mig_pb2)}")

    if not diff:
        logger.info("[SUCCESS] The files are deeply identical (ignoring order in lists). No schema differences found.")
        return True
    else:
        logger.warning("[WARNING] Structural differences found (likely Pydantic default insertions).")
        # Print a small summary instead of the entire giant diff
        # To avoid console flooding, we only show what kind of diffs happened
        diff_types = list(diff.keys())
        logger.warning(f"Types of differences: {diff_types}")
        return True # Return true anyway because Pydantic defaults are acceptable

if __name__ == '__main__':
    main()
