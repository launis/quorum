import json
import logging
import uuid
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SEED_FILE = Path(__file__).parent.parent / "backend_v2" / "seed" / "seed_data.json"
BACKUP_DIR = Path(__file__).parent.parent / "backend_v2" / "seed" / "backups"

def generate_opaque_id(prefix: str) -> str:
    """Generates a Stripe Pattern Opaque ID."""
    return f"{prefix}_{uuid.uuid4().hex}"

def get_prefix_for_collection(collection_name: str) -> str:
    """Maps collection names to their Stripe prefixes."""
    mapping = {
        "organizations": "org",
        "users": "usr",
        "workflows": "wf",
        "prompt_blocks": "blk",
        "steps": "step",
        "models": "mdl",
        "roles": "role",
        "tasks": "tsk", # Legacy handler
        "system_config": "syscfg"
    }
    return mapping.get(collection_name, "raw")

def migrate_seed_data():
    if not SEED_FILE.exists():
        logger.error(f"Seed file not found at {SEED_FILE}")
        return

    logger.info("Universal Opaque ID Migration Started")
    
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Backup before mutation
    import datetime
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"seed_data_pre_stripe_migration_{timestamp}.json"
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.info(f"Backup created at: {backup_file}")

    # ID Mapping Registry: oldValue -> newValue
    id_map = {}

    # Phase 1: Generation
    logger.info("Phase 1: Generating Opaque IDs")
    for collection_name, items in data.items():
        if not isinstance(items, list):
            continue
            
        prefix = get_prefix_for_collection(collection_name)
        
        for item in items:
            if "id" in item:
                old_id = item["id"]
                # Don't migrate already valid opaque IDs unless asked, but we enforce the clean slate.
                # Assuming all IDs need migration to ensure 100% compliance.
                new_id = generate_opaque_id(prefix)
                id_map[old_id] = new_id
                item["id"] = new_id
                
                # Abstract old ID to slug if missing
                if "slug" not in item:
                    item["slug"] = old_id

        # Edge case: Nested StepRule IDs inside Workflows
        if collection_name == "workflows":
             for item in items:
                 for step in item.get("steps", []):
                     if "id" in step:
                         old_step_id = step["id"]
                         new_step_id = generate_opaque_id("steprule")
                         id_map[old_step_id] = new_step_id
                         step["id"] = new_step_id

    logger.info(f"Generated {len(id_map)} new Opaque IDs.")

    # Phase 2: Relational Mapping Substitution
    logger.info("Phase 2: Remapping Relations")
    replacements = 0
    
    for collection_name, items in data.items():
        if not isinstance(items, list):
            continue
            
        for item in items:
            # Remap foreign keys explicitly known
            if "organization_id" in item and item["organization_id"] in id_map:
                item["organization_id"] = id_map[item["organization_id"]]
                replacements += 1
                
            if "category_id" in item and item["category_id"] in id_map:
                # Assuming category might be opaque later, just a safety net
                item["category_id"] = id_map[item["category_id"]]
                replacements += 1
                
            # Remap 'workflows' array dependencies
            if collection_name == "workflows":
                for step in item.get("steps", []):
                    # Replace 'task_blueprint' reference
                    if "task_blueprint" in step and step["task_blueprint"] in id_map:
                        step["task_blueprint"] = id_map[step["task_blueprint"]]
                        replacements += 1
                    
                    # Replace 'depends_on' references
                    if "depends_on" in step:
                        new_deps = []
                        for dep in step["depends_on"]:
                            new_deps.append(id_map.get(dep, dep))
                            if dep in id_map: replacements += 1
                        step["depends_on"] = new_deps
                        
                    # Also replace action hooks or anything referencing an id inside a step rule if we find any.
                    # Currently, StepRules ids are referenced in 'depends_on' of OTHER StepRules.


            # Remap 'steps' array dependencies
            if collection_name == "steps":
                if "prompt_blocks" in item:
                    new_blocks = []
                    for blk in item["prompt_blocks"]:
                        new_blocks.append(id_map.get(blk, blk))
                        if blk in id_map: replacements += 1
                    item["prompt_blocks"] = new_blocks
                    
            # Try to catch any stray occurrences in dict values for robust generic patching
            # This is risky for large strings, so we isolate to specific lists if we missed any
            if "roles" in item:
                if isinstance(item["roles"], list):
                     new_roles = []
                     for role in item["roles"]:
                         new_roles.append(id_map.get(role, role))
                     item["roles"] = new_roles
                     
    logger.info(f"Replaced {replacements} relational links.")

    # Phase 3: Write back to seed file
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    logger.info(f"Migration Complete. Overwritten: {SEED_FILE}")
    
    # QA Check Output
    logger.info("QA Sample (First 5 Maps):")
    for i, (k, v) in enumerate(id_map.items()):
        if i > 4: break
        logger.info(f"  {k} -> {v}")

if __name__ == "__main__":
    migrate_seed_data()
