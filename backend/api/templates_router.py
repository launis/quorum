from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
import os

from backend.config import DATA_DIR, BASE_DIR

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
        template_dir = os.path.join(DATA_DIR, 'templates')
        
        # Fallback to src/components/templates if data/templates doesn't exist (legacy path)
        if not os.path.exists(template_dir):
             root_dir = os.path.dirname(BASE_DIR)
             template_dir = os.path.join(root_dir, 'src', 'components', 'templates')

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
