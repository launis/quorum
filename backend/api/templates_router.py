from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
import os

router = APIRouter(prefix="/templates", tags=["Templates"])

@router.post("/render")
async def render_template(
    template_name: str = Body(..., embed=True),
    context: Dict[str, Any] = Body(..., embed=True)
):
    """
    Renders a Jinja2 template with the provided context.
    """
    try:
        # Locate templates directory
        # Assuming we are in backend/api/templates_router.py -> ../../src/components/templates
        # Or more robustly relative to project root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        template_dir = os.path.join(base_dir, 'data', 'templates')
        
        # Fallback to src/components/templates if data/templates doesn't exist (legacy path?)
        if not os.path.exists(template_dir):
             template_dir = os.path.join(base_dir, 'src', 'components', 'templates')

        if not os.path.exists(template_dir):
            raise HTTPException(status_code=500, detail=f"Template directory not found: {template_dir}")

        env = Environment(loader=FileSystemLoader(template_dir))
        
        try:
            template = env.get_template(template_name)
        except Exception:
             # Try adding .j2 if missing
             if not template_name.endswith('.j2'):
                 try:
                     template = env.get_template(template_name + '.j2')
                 except Exception:
                     raise HTTPException(status_code=404, detail=f"Template not found: {template_name}")
             else:
                 raise HTTPException(status_code=404, detail=f"Template not found: {template_name}")

        rendered_text = template.render(**context)
        return {"template": template_name, "rendered_text": rendered_text}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
