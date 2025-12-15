import requests
import json
import logging

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_workflows(self):
        try:
            response = requests.get(f"{self.base_url}/db/workflows", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch workflows: {e}")
            return []

    def get_workflow_steps(self, workflow_id, workflow_options):
        """Helper to get step definitions for a workflow."""
        steps_lookup = {}
        try:
            steps_res = requests.get(f"{self.base_url}/config/steps", timeout=10)
            if steps_res.status_code == 200:
                for s in steps_res.json():
                    steps_lookup[s['id']] = s.get('component')
        except Exception:
            pass

        dynamic_steps_order = []
        current_workflow = workflow_options.get(workflow_id)
        if current_workflow:
            wf_step_ids = current_workflow.get('steps', [])
            for sid in wf_step_ids:
                agent_name = steps_lookup.get(sid)
                if agent_name:
                    dynamic_steps_order.append(agent_name)
        
        if not dynamic_steps_order:
             # Default fallback
            dynamic_steps_order = [
                "GuardAgent", "AnalystAgent", "ProfilerAgent", "LogicianAgent", 
                "LogicalFalsifierAgent", "FactualOverseerAgent", "CausalAnalystAgent", 
                "PerformativityDetectorAgent", "ArchivistAgent", "JudgeAgent", 
                "CoachAgent", "XAIReporterAgent"
            ]
        return dynamic_steps_order

    def start_execution(self, workflow_id, files, metadata=None):
        if metadata is None:
            metadata = {}
            
        form_data = {
            "workflow_id": workflow_id,
            "inputs": json.dumps(metadata) 
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/executions",
                data=form_data,
                files=files,
                timeout=30 # Longer timeout for upload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise e

    def get_execution_status(self, execution_id):
        try:
            response = requests.get(f"{self.base_url}/executions/{execution_id}", timeout=10)
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def get_recent_runs(self, limit=5):
        try:
            res = requests.get(f"{self.base_url}/executions/recent?limit={limit}", timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def get_seed_data(self):
        try:
            response = requests.get(f"{self.base_url}/db/seed_data", timeout=10)
            return response.json() if response.status_code == 200 else {}
        except Exception:
            return {}

    def get_unified_prompts(self):
        try:
            res = requests.get(f"{self.base_url}/config/unified-prompts", timeout=10)
            return res.json().get("content", "") if res.status_code == 200 else ""
        except Exception:
            return ""

    def get_prompt_preview(self, step_id):
        try:
            res = requests.get(f"{self.base_url}/db/preview_prompt/{step_id}", timeout=10)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None

    def get_full_chain_preview(self, workflow_id):
        try:
            res = requests.get(f"{self.base_url}/db/preview_full_chain/{workflow_id}", timeout=10)
            return res.json().get("full_chain_text", "") if res.status_code == 200 else ""
        except Exception:
            return ""
