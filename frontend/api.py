import json
import logging

import requests

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str):
        """Initializes the APIClient.

        Args:
            base_url (str): The base URL of the backend API (e.g., http://localhost:8000).
        """
        self.base_url = base_url

    def get_workflows(self, token=None):
        """Fetches all workflows from the backend.

        Args:
            token (str, optional): Authentication token. Defaults to None.

        Returns:
            list: A list of workflow dictionaries. Returns empty list on failure.
        """
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

    def get_system_workflows(self, token=None):
        """Fetches raw workflow definitions from DB (Root View).

        Args:
            token (str, optional): Authentication token. Defaults to None.

        Returns:
            list: A list of system workflow dictionaries. Returns empty list on failure.
        """
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            response = requests.get(f"{self.base_url}/db/workflows", headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch system workflows: {e}")
            return []

    def get_workflow_steps(self, workflow_id, workflow_options):
        """Helper to get step definitions for a workflow.

        Args:
            workflow_id (str): The ID of the workflow.
            workflow_options (dict): A dictionary of available workflows.

        Returns:
            list: A list of agent names corresponding to the steps in the workflow.
        """
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
        """Fetches all available step configurations from the backend.

        Returns:
            list: A list of step configuration dictionaries. Returns empty list on failure.
        """
        try:
            res = requests.get(f"{self.base_url}/config/steps", timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Failed to fetch steps config: {e}")
            return []

    def start_execution(self, workflow_id, files, metadata=None, token=None):
        """Starts a new workflow execution with uploaded files.

        Args:
            workflow_id (str): The ID of the workflow to execute.
            files (dict): Dictionary of file objects to upload.
            metadata (dict, optional): Additional metadata/inputs. Defaults to None.
            token (str, optional): Authentication token. Defaults to None.

        Returns:
            dict: The API response containing execution details.

        Raises:
            Exception: If the API call fails.
        """
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
        """Retrieves the status of a specific execution.

        Args:
            execution_id (str): The ID of the execution.

        Returns:
            dict | None: The execution status dictionary, or None if failed.
        """
        try:
            response = requests.get(f"{self.base_url}/executions/{execution_id}", timeout=10)
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def get_recent_runs(self, limit=5, token=None):
        """Fetches a list of recent executions.

        Args:
            limit (int, optional): Number of runs to fetch. Defaults to 5.
            token (str, optional): Authentication token. Defaults to None.

        Returns:
            list: A list of recent execution dictionaries.
        """
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            res = requests.get(f"{self.base_url}/executions/recent?limit={limit}", headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    # get_seed_data removed (Refactor Step 3418)
    # System View now uses get_workflows/get_steps/get_components directly.

    def get_unified_prompts(self):
        """Fetches the unified prompt content.

        Returns:
            str: The unified prompt text.
        """
        try:
            res = requests.get(f"{self.base_url}/config/unified-prompts", timeout=10)
            return res.json().get("content", "") if res.status_code == 200 else ""
        except Exception:
            return ""

    def get_prompt_preview(self, step_id):
        """Fetches a preview of the prompt for a specific step.

        Args:
            step_id (str): The ID of the step.

        Returns:
            dict | None: The prompt preview data, or None on failure.
        """
        try:
            res = requests.get(f"{self.base_url}/db/preview_prompt/{step_id}", timeout=10)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None

    def get_full_chain_preview(self, workflow_id):
        """Fetches a preview of the full prompt chain for a specific workflow.

        Args:
            workflow_id (str): The ID of the workflow.

        Returns:
            str: The full chain prompt text.
        """
        try:
            res = requests.get(f"{self.base_url}/db/preview_full_chain/{workflow_id}", timeout=10)
            return res.json().get("full_chain_text", "") if res.status_code == 200 else ""
        except Exception:
            return ""

    def list_organizations(self, token: str):
        """Fetches list of all organizations (ROOT only).

        Args:
            token (str): Authentication token.

        Returns:
            list: List of organization dictionaries.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/organizations/", headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def get_model_strategies(self):

        """Fetches available model strategies (e.g. 'fast', 'deep') from the backend.

        Returns:
            list: A list of strategy names.
        """
        try:
            res = requests.get(f"{self.base_url}/config/models/strategies", timeout=10)
            return list(res.json().keys()) if res.status_code == 200 else []
        except Exception:
            return []



    def get_components(self):
        """Fetches all configuration components.

        Returns:
            list: A list of component dictionaries.
        """
        try:
            res = requests.get(f"{self.base_url}/config/components", timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Failed to fetch components: {e}")
            return []

    def get_steps(self):
        """Fetches all workflow steps.

        Returns:
            list: A list of step definition dictionaries.
        """
        try:
            res = requests.get(f"{self.base_url}/builder/steps", timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Failed to fetch steps: {e}")
            return []

    def get_prompt_types(self):
        """Fetches allowed prompt component types.

        Returns:
            list: A list of type strings (e.g. 'prompt', 'mandate').
        """
        # Currently no backend endpoint, return empty to trigger view fallback
        return []

    # --- Builder API ---
    def get_builder_config_agents(self):
        """Fetches available agent classes for the Builder.

        Returns:
            list: A list of agent configuration dictionaries.
        """
        try:
            res = requests.get(f"{self.base_url}/builder/config/agents", timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Builder Config Error: {e}")
            return []

    def get_builder_workflows(self, token: str):
        """Fetches workflows specifically for the Builder view.

        Args:
            token (str): Authentication token.

        Returns:
            list: A list of workflow dictionaries.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/builder/workflows", headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Builder List Error: {e}")
            return []

    def get_builder_workflow(self, workflow_id, token: str):
        """Fetches a specific workflow for the Builder.

        Args:
            workflow_id (str): The ID of the workflow.
            token (str): Authentication token.

        Returns:
            dict | None: The workflow dictionary, or None if failed.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/builder/workflows/{workflow_id}", headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else None
        except Exception as e:
            logger.error(f"Builder Detail Error: {e}")
            return None

    def create_builder_workflow(self, payload, token: str):
        """Creates a new workflow via the Builder API.

        Args:
            payload (dict): The workflow data.
            token (str): Authentication token.

        Returns:
            dict: The created workflow data.

        Raises:
            Exception: If creation fails.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{self.base_url}/builder/workflows", json=payload, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Builder Create Error: {e}")
            raise e

    def update_builder_workflow(self, workflow_id, payload, token: str):
        """Updates an existing workflow via the Builder API.

        Args:
            workflow_id (str): The ID of the workflow.
            payload (dict): The update data.
            token (str): Authentication token.

        Returns:
            dict: The updated workflow data.

        Raises:
            Exception: If update fails.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.put(f"{self.base_url}/builder/workflows/{workflow_id}", json=payload, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Builder Update Error: {e}")
            raise e

    def delete_builder_workflow(self, workflow_id, token: str):
        """Deletes a workflow via the Builder API.

        Args:
            workflow_id (str): The ID of the workflow.
            token (str): Authentication token.

        Returns:
            dict: The API response.

        Raises:
            Exception: If deletion fails.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.delete(f"{self.base_url}/builder/workflows/{workflow_id}", headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Builder Delete Error: {e}")
            raise e

    def copy_builder_workflow(self, workflow_id: str, new_name: str, token: str):
        """Copies an existing workflow to a new one.

        Args:
            workflow_id (str): The source workflow ID.
            new_name (str): The name for the new workflow.
            token (str): Authentication token.

        Returns:
            dict: The new workflow data.

        Raises:
            Exception: If copy fails.
        """
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
        """Exchanges a token (Firebase or Mock) for user details.

        Args:
            token (str): The authentication token.

        Returns:
            dict | None: The user dictionary if valid, None otherwise.
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
        """Fetches current user profile.

        Args:
            token (str): Authentication token.

        Returns:
            dict | None: The user profile, or None if failed.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/auth/me", headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None

    def fetch_system_audit_logs(self, token: str, filters: dict = None):
        """Fetches system audit logs.

        Args:
            token (str): Authentication token.
            filters (dict, optional): Filtering parameters (limit, org_id, etc).

        Returns:
            list: List of audit log entries.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/audit/logs", params=filters, headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Audit Log Fetch Error: {e}")
            return []

    def get_global_settings(self, token: str):
        """Fetches global system settings.
        
        Args:
            token (str): Authentication token.
        
        Returns:
            dict: Settings dictionary.
        """
        try:
             headers = {"Authorization": f"Bearer {token}"}
             res = requests.get(f"{self.base_url}/settings", headers=headers, timeout=5)
             return res.json() if res.status_code == 200 else {}
        except Exception:
             return {}

    def update_global_settings(self, payload: dict, token: str):
        """Updates global system settings.
        
        Args:
            payload (dict): Settings to update.
            token (str): Authentication token.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.patch(f"{self.base_url}/settings", json=payload, headers=headers, timeout=5)
            return res.status_code == 200
        except Exception:
            return False

    def list_users(self, token: str):
        """Fetches list of managed users.

        Args:
            token (str): Authentication token.

        Returns:
            list: A list of users.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/auth/users", headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def create_user(self, token: str, payload: dict):
        """Creates a new user.

        Args:
            token (str): Authentication token.
            payload (dict): The user data.

        Returns:
            dict: The created user data.

        Raises:
            Exception: If creation fails.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{self.base_url}/auth/users", json=payload, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Create User Error: {e}")
            raise e

    def update_user(self, token: str, uid: str, payload: dict):
        """Updates a user.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.patch(f"{self.base_url}/auth/users/{uid}", json=payload, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Update User Error: {e}")
            raise e

    def delete_user(self, token: str, uid: str):
        """Deletes a user.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.delete(f"{self.base_url}/auth/users/{uid}", headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Delete User Error: {e}")
            raise e

    def impersonate_user(self, token: str, target_uid: str):
        """Generates an impersonation token.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            payload = {"target_uid": target_uid}
            res = requests.post(f"{self.base_url}/auth/impersonate", json=payload, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json().get("access_token")
        except Exception as e:
            logger.error(f"Impersonate Error: {e}")
            raise e

            logger.error(f"Impersonate Error: {e}")
            raise e

    def get_available_roles(self):
        """Fetches list of available roles from backend.
        
        Returns:
            list[str]: e.g. ['admin', 'member', 'viewer']
        """
        try:
            res = requests.get(f"{self.base_url}/auth/roles", timeout=5)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    # --- Organization User Management (V2.5) ---
    def get_organization_users(self, org_id: str, token: str):
        """Fetches users for a specific organization.
        
        Args:
            org_id (str): Organization ID.
            token (str): Auth token.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/organizations/{org_id}/users", headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"List Org Users Error: {e}")
            return []

    def create_organization_user(self, org_id: str, payload: dict, token: str):
        """Creates a user in an organization.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{self.base_url}/organizations/{org_id}/users", json=payload, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Create Org User Error: {e}")
            raise e

    def delete_organization_user(self, org_id: str, target_uid: str, token: str):
        """Deletes a user from an organization.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.delete(f"{self.base_url}/organizations/{org_id}/users/{target_uid}", headers=headers, timeout=10)
            res.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Delete Org User Error: {e}")
            raise e

    # --- Audit Logs ---
    def get_audit_logs(self, token: str, organization_id: str = None, actor_uid: str = None, action: str = None, limit: int = 100):
        """Fetches audit logs with optional filters.
        """
        try:
            params = {"limit": limit}
            if organization_id: params["organization_id"] = organization_id
            if actor_uid: params["actor_uid"] = actor_uid
            if action: params["action"] = action
            
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{self.base_url}/audit/logs", params=params, headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception as e:
            logger.error(f"Audit Log Error: {e}")
            return []

    def get_builder_step(self, step_id: str):
        """Fetches a specific step for the Builder.

        Args:
            step_id (str): The ID of the step.

        Returns:
            dict | None: The step dictionary, or None if failed.
        """
        try:
            res = requests.get(f"{self.base_url}/builder/steps/{step_id}", timeout=10)
            return res.json() if res.status_code == 200 else None
        except Exception as e:
            logger.error(f"Failed to get builder step {step_id}: {e}")
            return None

    def update_builder_step(self, step_id: str, payload: dict):
        """Updates a step via the Builder API.

        Args:
            step_id (str): The ID of the step.
            payload (dict): The update data.

        Returns:
            dict: The updated step data.

        Raises:
            Exception: If update fails.
        """
        try:
            res = requests.put(f"{self.base_url}/builder/steps/{step_id}", json=payload, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Failed to update step {step_id}: {e}")
            raise e

    def clone_builder_step(self, source_step_id: str):
        """Clones an existing step.

        Args:
            source_step_id (str): The ID of the step to clone.

        Returns:
            dict: The cloned step data.

        Raises:
            Exception: If cloning fails.
        """
        try:
            res = requests.post(f"{self.base_url}/builder/steps/clone", json={"source_step_id": source_step_id}, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Failed to clone step {source_step_id}: {e}")
            raise e

    def compile_fusion(self, workflow_id: str, steps_to_fuse: list):
        """Compiles selected steps into a fused workflow.

        Args:
            workflow_id (str): The ID of the workflow.
            steps_to_fuse (list): List of step IDs to fuse.

        Returns:
            dict: The fused workflow data.

        Raises:
            Exception: If compilation fails.
        """
        try:
            res = requests.post(f"{self.base_url}/builder/compile", json={"workflow_id": workflow_id, "steps": steps_to_fuse}, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Failed to compile fuison: {e}")
            raise e

    def get_workflow_template(self):
        """Fetches the standard workflow template.

        Returns:
            dict: The workflow template.
        """
        try:
            res = requests.get(f"{self.base_url}/builder/config/template", timeout=10)
            return res.json() if res.status_code == 200 else {}
        except Exception:
            return {}

    def generate_id(self, prefix: str = "custom_step"):
        """Generates a unique ID from the backend.

        Args:
            prefix (str, optional): The ID prefix. Defaults to "custom_step".

        Returns:
            str: The generated unique ID.
        """
        try:
            res = requests.get(f"{self.base_url}/builder/utils/generate-id?prefix={prefix}", timeout=10)
            return res.json().get('id', '')
        except Exception:
            # Fallback
            import uuid
            return f"{prefix}_{uuid.uuid4().hex[:6]}"

    def create_custom_step_v2(self, component_type: str, name_hint: str = None):
        """Creates a customized step (V2) based on a component type.

        Args:
            component_type (str): The type of component (e.g., 'AnalystAgent').
            name_hint (str, optional): Hint for the step name. Defaults to None.

        Returns:
            dict: The created step data.

        Raises:
            Exception: If creation fails.
        """
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
        """Creates a basic step via the Config API.

        Args:
            payload (dict): The step configuration.

        Returns:
            dict: The created step data.

        Raises:
            Exception: If creation fails.
        """
        try:
            res = requests.post(f"{self.base_url}/config/steps", json=payload, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Failed to create step: {e}")
            raise e

    def get_components(self):
        """Fetches all configuration components.

        Returns:
            list: A list of component dictionaries.
        """
        try:
            res = requests.get(f"{self.base_url}/config/components", timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def get_prompt_types(self):
        """Fetches available prompt types for the Builder.

        Returns:
            list: A list of prompt types.
        """
        try:
            res = requests.get(f"{self.base_url}/builder/config/prompt-types", timeout=10)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def validate_flow(self, sequence: list):
        """Calls the backend to validate data flow continuity.

        Args:
            sequence (list): List of step IDs in the workflow.

        Returns:
            dict: Validation result with keys 'valid' and 'errors'.
        """
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

    def get_available_models(self, providers: list = None, location: str = None):
        """Fetches available models from backend with filtering.

        Args:
            providers (list, optional): List of providers to filter by (e.g., ['google', 'openai']).
            location (str, optional): Cloud region/location filter.

        Returns:
            dict: Dictionary mapping providers to lists of model names.
        """
        try:
            params = {}
            if location:
                params["location"] = location

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
        """Calls the ad-hoc LLM endpoint.

        Args:
            provider (str): The LLM provider (e.g., 'google').
            mode (str): The strategy mode ('fast' or 'deep').
            prompt (str): The user prompt.
            system_instruction (str, optional): System instruction override.

        Returns:
            str: The LLM response content, or error message.
        """
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
