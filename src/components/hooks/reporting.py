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
    # print(f"[HOOK] Template Dir: {template_dir}")

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('report_template.jinja2')
    
    # Fetch Disclaimer from DB
    from src.database.client import DatabaseClient
    from tinydb import Query
    
    db = DatabaseClient()
    components = db.get_table('components')
    disclaimer_doc = components.get(Query().id == 'DISCLAIMER')
    disclaimer_text = disclaimer_doc['content'] if disclaimer_doc else "Disclaimer not found."

    # Construct report content from accumulated data
    scores = data.get('pisteet', {})
    
    report_data = {
        "summary": data.get('summary', 'Yhteenveto puuttuu.'),
        "critical_findings": data.get('critical_findings', []),
        "pre_mortem_signals": data.get('pre_mortem_signals'),
        "hitl_required": data.get('hitl_required', False),
        "ethical_issues": data.get('ethical_issues', []),
        "audit_questions": data.get('audit_questions', []),
        "uncertainty": data.get('uncertainty', {
            "aleatoric": "N/A",
            "systemic": [],
            "epistemic": "N/A"
        }),
        "scores": {
            "analysis": {
                "score": scores.get('analyysi_ja_prosessi', {}).get('arvosana', 'N/A'),
                "reasoning": scores.get('analyysi_ja_prosessi', {}).get('perustelu', '')
            },
            "evaluation": {
                "score": scores.get('arviointi_ja_argumentaatio', {}).get('arvosana', 'N/A'),
                "reasoning": scores.get('arviointi_ja_argumentaatio', {}).get('perustelu', '')
            },
            "synthesis": {
                "score": scores.get('synteesi_ja_luovuus', {}).get('arvosana', 'N/A'),
                "reasoning": scores.get('synteesi_ja_luovuus', {}).get('perustelu', '')
            }
        }
    }

    report_content = template.render(
        report_content=report_data,
        final_verdict="KATSO PISTEYTYS", # Legacy field, can be removed from template if unused
        reliability_score="EHDOLLEINEN" if data.get('hitl_required') else "KORKEA",
        disclaimer=disclaimer_text
    )
    
    print("\n--- GENERATED REPORT CONTENT ---\n")
    print(report_content)
    print("\n--------------------------------\n")
    
    return {
        "report_content": report_content,
        "reliability_score": "EHDOLLEINEN" if data.get('hitl_required') else "KORKEA"
    }

HookRegistry.register("generate_jinja2_report", generate_jinja2_report)
