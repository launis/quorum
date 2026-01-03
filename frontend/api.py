import requests
import json
import logging

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_workflows(self, token=None):
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            response = requests.get(f"{self.base_url}/builder/workflows", headers=headers, timeout=10)
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
        
        # No fallback. If empty, it means workflow is empty or API failed.
        # This is strictly correct behavior.
        return dynamic_steps_order

    def get_available_steps_config(self):
        """Fetches all available step configurations from the backend."""
        try:
            res = requests.get(f"{self.base_url}/config/steps", timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Failed to fetch steps config: {e}")
            return []

    def start_execution(self, workflow_id, files, metadata=None, token=None):
        if metadata is None:
            metadata = {}
            
        form_data = {
            "workflow_id": workflow_id,
            "inputs": json.dumps(metadata) 
        }
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            response = requests.post(
                f"{self.base_url}/executions",
                data=form_data,
                files=files,
                headers=headers,
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

    def get_recent_runs(self, limit=5, token=None):
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            res = requests.get(f"{self.base_url}/executions/recent?limit={limit}", headers=headers, timeout=10)
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

    def get_model_strategies(self):
        """Fetches available model strategies (e.g. 'fast', 'deep') from the backend."""
        try:
            res = requests.get(f"{self.base_url}/config/models/strategies", timeout=10)
            return list(res.json().keys()) if res.status_code == 200 else []
        except Exception:
            return []



    # --- Builder API ---
    def get_builder_config_agents(self):
        try:
            res = requests.get(f"{self.base_url}/builder/config/agents", timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Builder Config Error: {e}")
            return []

    def get_builder_workflows(self, token: str):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/builder/workflows", headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Builder List Error: {e}")
            return []

    def get_builder_workflow(self, workflow_id, token: str):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/builder/workflows/{workflow_id}", headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else None
        except Exception as e:
            logger.error(f"Builder Detail Error: {e}")
            return None

    def create_builder_workflow(self, payload, token: str):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{self.base_url}/builder/workflows", json=payload, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
           logger.error(f"Builder Create Error: {e}")
           raise e

    def update_builder_workflow(self, workflow_id, payload, token: str):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.put(f"{self.base_url}/builder/workflows/{workflow_id}", json=payload, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
           logger.error(f"Builder Update Error: {e}")
           raise e

    def delete_builder_workflow(self, workflow_id, token: str):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.delete(f"{self.base_url}/builder/workflows/{workflow_id}", headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
           logger.error(f"Builder Delete Error: {e}")
           raise e
           
    def copy_builder_workflow(self, workflow_id: str, new_name: str, token: str):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{self.base_url}/builder/workflows/{workflow_id}/copy", json={"new_name": new_name}, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Builder Copy Error: {e}")
            raise e

    # --- Authentication (Hybrid) ---

    def login_with_token(self, token: str):
        """
        Exchanges a token (Firebase or Mock) for user details.
        """
        try:
            res = requests.post(f"{self.base_url}/auth/verify", json={"token": token}, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get("token_valid"):
                    return data["user"]
            logger.warning(f"Login failed: {res.text}")
            return None
        except Exception as e:
            logger.error(f"Auth Network Error: {e}")
            return None

    def get_my_profile(self, token: str):
        """Fetches current user profile."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/auth/me", headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None

        except Exception:
            return None

    def list_users(self, token: str):
        """Fetches list of managed users."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/auth/users", headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def create_user(self, token: str, payload: dict):
        """Creates a new user."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{self.base_url}/auth/users", json=payload, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Create User Error: {e}")
            raise e

    # --- V2 ---
    def get_builder_step(self, step_id: str):
        try:
            res = requests.get(f"{self.base_url}/builder/steps/{step_id}", timeout=10)
            return res.json() if res.status_code == 200 else None
        except Exception as e:
            logger.error(f"Failed to get builder step {step_id}: {e}")
            return None

    def update_builder_step(self, step_id: str, payload: dict):
        try:
            res = requests.put(f"{self.base_url}/builder/steps/{step_id}", json=payload, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Failed to update step {step_id}: {e}")
            raise e

    def clone_builder_step(self, source_step_id: str):
        try:
            res = requests.post(f"{self.base_url}/builder/steps/clone", json={"source_step_id": source_step_id}, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Failed to clone step {source_step_id}: {e}")
            raise e

    def compile_fusion(self, workflow_id: str, steps_to_fuse: list):
        try:
            res = requests.post(f"{self.base_url}/builder/compile", json={"workflow_id": workflow_id, "steps": steps_to_fuse}, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Failed to compile fuison: {e}")
            raise e

    def get_workflow_template(self):
        try:
            res = requests.get(f"{self.base_url}/builder/config/template", timeout=10)
            return res.json() if res.status_code == 200 else {}
        except Exception:
            return {}

    def generate_id(self, prefix: str = "custom_step"):
        try:
            res = requests.get(f"{self.base_url}/builder/utils/generate-id?prefix={prefix}", timeout=10)
            return res.json().get('id', '')
        except Exception:
            # Fallback
            import uuid
            return f"{prefix}_{uuid.uuid4().hex[:6]}"

    def create_custom_step_v2(self, component_type: str, name_hint: str = None):
        try:
            payload = {"component_type": component_type}
            if name_hint: payload["name_hint"] = name_hint
            
            res = requests.post(f"{self.base_url}/builder/steps/create-custom", json=payload, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Failed to create custom step v2: {e}")
            raise e

    def create_step(self, payload):
        try:
            res = requests.post(f"{self.base_url}/config/steps", json=payload, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Failed to create step: {e}")
            raise e

    def get_components(self):
        try:
            res = requests.get(f"{self.base_url}/config/components", timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def get_prompt_types(self):
        try:
            res = requests.get(f"{self.base_url}/builder/config/prompt-types", timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []
            
    def validate_flow(self, sequence: list):
        """Calls the backend to validate data flow continuity."""
        try:
            payload = {
                "id": "validation_temp",
                "name": "Validation",
                "sequence": sequence,
                "description": "Temp"
            }
            res = requests.post(f"{self.base_url}/config/validate-flow", json=payload, timeout=10)
            return res.json() if res.status_code == 200 else {"valid": False, "errors": ["Network Error"]}
        except Exception as e:
            return {"valid": False, "errors": [str(e)]}

    def get_available_models(self, providers: list = None, location: str = "us-central1"):
        """Fetches available models from backend with filtering."""
        try:
            params = {"location": location}
            if providers:
                # requests handles list properly as providers=mock&providers=google
                params["providers"] = providers
            
            res = requests.get(f"{self.base_url}/config/models/available", params=params, timeout=15)
            # The backend now returns Dict[str, List]
            return res.json() if res.status_code == 200 else {}
        except Exception as e:
            logger.error(f"Failed to fetch available models: {e}")
            return {}

    def call_llm_adhoc(self, provider: str, mode: str, prompt: str, system_instruction: str = None):
        """Calls the ad-hoc LLM endpoint."""
        try:
            payload = {
                "provider": provider,
                "mode": mode,
                "prompt": prompt,
                "system_instruction": system_instruction
            }
            res = requests.post(f"{self.base_url}/config/models/call", json=payload, timeout=60)
            res.raise_for_status()
            return res.json().get("content", "")
        except Exception as e:
            logger.error(f"Ad-hoc LLM call failed: {e}")
            return f"Error: {str(e)}"
