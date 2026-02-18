import logging
from typing import Any

from backend.exceptions import AppException
from backend.models.view import AssessmentView, StepProgressItem

from .base import BaseTransformer

logger = logging.getLogger(__name__)

class AssessmentTransformer(BaseTransformer):
    def _get_workflow_steps(self, workflow_id: str, current_data: dict, workflow_definition: Any | None = None) -> list[StepProgressItem]:
        """Determines the steps for the workflow and their status dynamically."""
        chain = []
        if workflow_definition:
             # Extract steps from definition
             # Assuming workflow_definition is a dict or Pydantic model with 'steps'
             steps = getattr(workflow_definition, "steps", [])
             if isinstance(steps, list):
                 for s in steps:
                     # Handle Pydantic model or dict
                     sid = getattr(s, "id", None) or s.get("id")
                     if sid:
                         chain.append(sid)

        if not chain:
            # Fallback for legacy/missing definition
            pass

        # 3. Determine Status for each step
        progress_items = []
        for step_id in chain:
            step_status = "pending"
            step_res = current_data.get(step_id)

            if step_res:
                step_status = "completed"
                # Check for specific status flags if available
                if step_res.get("status") == "failed":
                    step_status = "failed"

            label = self._t(f"STEP_{step_id.upper()}", step_id)
            progress_items.append(StepProgressItem(
                id=step_id,
                label=label,
                status=step_status
            ))

        return progress_items

    def transform(
        self,
        raw_data: dict[str, Any],
        workflow_definition: Any | None = None,
        valid_range: tuple[float, float] | None = None,
    ) -> AssessmentView:
        """Transforms raw execution state into a live Monitoring View (AssessmentView)."""
        try:
            # 1. Basic Info
            execution_id = raw_data.get("id") or raw_data.get("execution_id") or "unknown"
            status = raw_data.get("status")
            workflow_id = raw_data.get("workflow_id") or "unknown"

            # 2. UI Variant & Label
            ui_variant = "default"
            status_label = self._t(f"status.{status}", status.title() if status else "Unknown")

            if status in ("completed", "finished"):
                ui_variant = "success"
                status_label = self._t("status.completed", "Valmis")
            elif status in ("failed", "rejected", "error"):
                ui_variant = "error"
                status_label = self._t("status.failed", "Epäonnistui")
            elif status == "cancelled":
                ui_variant = "warning"
                status_label = self._t("status.cancelled", "Peruttu")
            elif status == "running":
                ui_variant = "default"
                status_label = self._t("status.running", "Käynnissä")

            # 3. Status Message & Steps
            status_message = ""

            # Extract steps from results OR trace
            steps_data = raw_data.get("results", {}).get("step_results", {})
            if not steps_data and "execution_trace" in raw_data:
                steps_data = self._reconstruct_state_from_trace(raw_data["execution_trace"])
            elif not steps_data and "results" in raw_data and "execution_trace" in raw_data["results"]:
                steps_data = self._reconstruct_state_from_trace(raw_data["results"]["execution_trace"])

            # GENERATE STEPS LIST
            steps_list = self._get_workflow_steps(str(workflow_id), steps_data, workflow_definition)

            # Filter out pending steps if the execution is completed or failed
            if status in ("completed", "finished", "failed", "rejected"):
                steps_list = [s for s in steps_list if s.status != "pending"]

            if status == "failed":
                error_details = str(raw_data.get("error") or raw_data.get("result", {}).get("error") or "")
                
                # Localize common error codes
                if "AGENT_EXECUTION_CRITICAL" in error_details:
                    if "InstructorRetryException" in error_details:
                        status_message = self._t("error.llm_retry", "Kielimallin vastaus epäonnistui (Yhteys- tai muotoiluvirhe).")
                    else:
                        status_message = self._t("error.agent_critical", "Agentin suoritus keskeytyi kriittiseen virheeseen.")
                elif "Validation Error" in error_details:
                    status_message = self._t("error.validation", "Validointivirhe syötteessä tai tulosteessa.")
                else:
                    status_message = error_details if error_details else self._t("Unknown error", "Tuntematon virhe")
            elif status == "running":
                status_message = self._t("Processing...", "Käsitellään...")
                if steps_data:
                    count = len(steps_data)
                    # Fail safe for empty dict
                    if steps_data:
                        # Safe last step extraction
                        last_key = list(steps_data.keys())[-1]
                        last_step = last_key.replace("step_", "").capitalize()
                        # FIX: Last step is COMPLETED, so label it 'Valmis'
                        status_message = f"{self._t('status.completed', 'Valmis')}: {last_step} ({count})"

                    completed_ids = set(steps_data.keys())
                    for i, item in enumerate(steps_list):
                        if item.id not in completed_ids:
                            # Create new instance as model is frozen
                            steps_list[i] = StepProgressItem(
                                id=item.id,
                                label=item.label,
                                status="running"
                            )
                            # UPDATE: If we know the next step, show THAT as processing
                            running_step = item.id.replace("step_", "").capitalize()
                            status_message = f"{self._t('status.running', 'Käsitellään')}: {running_step}"
                            break

            elif status == "completed":
                status_message = self._t("Assessment ready", "Arviointi valmis")
            else:
                status_message = "..."

            # 4. Warnings
            show_warning = False
            guard = steps_data.get("step_guard", {})
            # Safety: guard might be None if not found
            if guard and guard.get("security_check", {}).get("uhka_havaittu"):
                show_warning = True

            # 5. Final Score
            final_score = None
            judge = steps_data.get("step_judge", {})
            if judge:
                # Try/Except for int conversion only, strict otherwise
                try:
                    if "score_cards" in judge and judge["score_cards"]:
                        final_score = int(float(judge["score_cards"][0].get("total_score", 0)))
                    elif "total_score" in judge:
                        final_score = int(float(judge["total_score"]))
                except (ValueError, TypeError):
                    logger.warning("Failed to parse final score from Judge output", exc_info=True)
                    final_score = None

            return AssessmentView(
                sessionId=str(execution_id),
                statusLabel=str(status_label),
                uiVariant=ui_variant,  # type: ignore # Validated by Literal
                statusMessage=str(status_message),
                showWarningBanner=bool(show_warning),
                steps=steps_list,
                finalScore=final_score,
            )

        except Exception as e:
            error_code = "TRANSFORMATION_FAILED"
            logger.error(f"[{error_code}] Failed to create AssessmentView: {e}", exc_info=True)
            raise AppException(message=f"Transformation failed: {e}", status_code=500, details={"error_code": error_code}) from e
