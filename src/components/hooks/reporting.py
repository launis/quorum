from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
from src.components.hook_registry import HookRegistry
import os

def generate_jinja2_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    HOOK: generate_jinja2_report
    Logic: XAI-Raportoijan raportin generointi Jinja2:lla.
    """
    # Use config for robust path resolution
    import config
    template_dir = os.path.join(config.BASE_DIR, 'src/components/templates')
    print(f"[HOOK] Template Dir: {template_dir}")

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('report_template.jinja2')
    
    # Fetch Disclaimer from DB
    from src.database.client import DatabaseClient
    from tinydb import Query
    
    db = DatabaseClient()
    components = db.get_table('components')
    disclaimer_doc = components.get(Query().id == 'DISCLAIMER')
    disclaimer_text = disclaimer_doc['content'] if disclaimer_doc else "Disclaimer not found."

    report_content = template.render(
        final_verdict=data.get('final_verdict', 'Unknown'),
        reliability_score="CONDITIONAL (Mock)",
        disclaimer=disclaimer_text
    )
    
    return {
        "xai_report": report_content,
        "reliability_score": "CONDITIONAL"
    }

HookRegistry.register("generate_jinja2_report", generate_jinja2_report)
