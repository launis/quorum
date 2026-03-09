"""Service for generating detailed PDF reports using WeasyPrint and Jinja2.

Adheres to V2 Architecture (De-Generator Policy / SDUI Block Building):
- Completely dynamic: Iterates over frozen_context.ui_hints_snapshot to render blocks.
- No static domain models.
- Resolves XAI citations and justifications automatically.
"""

import logging
from pathlib import Path

import weasyprint
from jinja2 import Environment, FileSystemLoader

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

class PdfReportService:
    """Service to generate PDF reports dynamically from V2 execution data."""

    def __init__(self, repository: AbstractWorkflowRepository):
        """Initialize the service.

        Args:
            repository: Workflow repository.
        """
        self.repository = repository

        # Suppress verbose fontTools logs (used by WeasyPrint)
        logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
        logging.getLogger("fontTools.ttLib").setLevel(logging.WARNING)

        # Setup Jinja2 env
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

    async def generate_execution_pdf(self, execution_id: str) -> bytes:
        """Generates a dynamic PDF for the given execution ID using SDUI block constraints.

        Args:
            execution_id: The execution UUID.

        Returns:
            bytes: The generated PDF data.
        """
        try:
            # 1. Fetch Data
            execution = await self.repository.get_execution(execution_id)
            if not execution:
                raise AppException(
                    message=f"Execution {execution_id} not found",
                    status_code=404,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                )

            # Fetch Workflow Name for Header
            workflow_id = execution.workflow_id
            workflow_name = "Dynamic Workflow Execution"
            if workflow_id:
                workflow_dict = await self.repository.get_workflow_by_id(workflow_id)
                if workflow_dict and "name" in workflow_dict:
                    name_obj = workflow_dict["name"]
                    # Assuming I18nText dict or just string
                    if isinstance(name_obj, dict):
                        workflow_name = name_obj.get("default_locale", workflow_name)
                    else:
                        workflow_name = str(name_obj)

            # 2. Extract context and results
            frozen_context = execution.frozen_context.model_dump() if execution.frozen_context else {}
            results = execution.results or {}

            # 3. Render Template
            template = self.env.get_template("report_template.jinja2")

            from datetime import datetime
            printed_at = datetime.now().astimezone().strftime("%d.%m.%Y %H:%M")

            html_content = template.render(
                execution_id=execution_id,
                workflow_name=workflow_name,
                frozen_context=frozen_context,
                results=results,
                printed_at=printed_at
            )

            # 4. Generate PDF
            import asyncio
            loop = asyncio.get_running_loop()

            def _render_pdf() -> bytes:
                # Type safe cast since write_pdf returns bytes
                pdf_data = weasyprint.HTML(string=html_content).write_pdf()
                return bytes(pdf_data) if pdf_data else b""

            pdf_bytes = await loop.run_in_executor(None, _render_pdf)

            return pdf_bytes

        except AppException:
             # Re-raise known AppExceptions (e.g. 404) as-is
             raise

        except Exception as e:
             logger.error(f"INTERNAL_SERVER_ERROR: PDF generation failed for {execution_id}: {e}", exc_info=True)
             raise AppException(
                 message=f"PDF generation failed: {e}",
                 status_code=500,
                 details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "original_error": str(e)},
             ) from e
