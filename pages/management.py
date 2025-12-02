import streamlit as st
import requests
import json

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Management Dashboard", layout="wide")

st.title("🛠️ Management Dashboard")
st.markdown("Edit prompts, rules, and workflows directly in the database.")

# --- Helper Functions ---

def get_components():
    try:
        res = requests.get(f"{API_URL}/config/components")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Error fetching components: {e}")
    return []

def get_workflows():
    try:
        res = requests.get(f"{API_URL}/config/workflows")
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"Error fetching workflows: {res.text}")
    except Exception as e:
        st.error(f"Error fetching workflows: {e}")
    return []

def get_steps():
    try:
        res = requests.get(f"{API_URL}/config/steps")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Error fetching steps: {e}")
    return []

def get_available_models():
    try:
        res = requests.get(f"{API_URL}/llm/models")
        if res.status_code == 200:
            return res.json().get("models", [])
    except Exception as e:
        st.error(f"Error fetching models: {e}")
    return ["gpt-4o", "gemini-1.5-pro", "local-model"] # Fallback

def validate_workflow(workflow, all_steps):
    """
    Validates the workflow sequence by checking schema compatibility.
    """
    sequence = workflow.get('sequence', workflow.get('steps', []))
    if not sequence:
        return ["❌ Workflow has no steps."]
    
    errors = []
    # Initial available schemas (from user input)
    available_schemas = {'RawInput'} 
    
    # Map step IDs to definitions
    step_map = {s['id']: s for s in all_steps}
    
    for i, step_id in enumerate(sequence):
        if step_id not in step_map:
            errors.append(f"❌ Step {i+1}: '{step_id}' not found in database.")
            continue
            
        step_def = step_map[step_id]
        input_schema = step_def.get('input_schema')
        output_schema = step_def.get('output_schema')
        
        # Check if input is satisfied
        if input_schema and input_schema not in available_schemas:
            # Special case: 'RawInput' is always available if we assume standard start
            # But let's be strict.
            # Actually, some agents might accept multiple inputs, but the schema definition is usually single string.
            # Let's check if it's a "soft" dependency or hard.
            # For now, strict check.
            errors.append(f"⚠️ Step {i+1} ({step_id}): Requires '{input_schema}', but available are {available_schemas}.")
        
        # Add output to available
        if output_schema:
            available_schemas.add(output_schema)
            
    if not errors:
        return ["✅ Workflow is valid! Data flow chain is intact."]
    return errors

def create_workflow(wf_id, name, sequence, description, model_mapping):
    try:
        payload = {
            "id": wf_id,
            "name": name,
            "sequence": sequence,
            "description": description,
            "default_model_mapping": model_mapping
        }
        res = requests.post(f"{API_URL}/config/workflows", json=payload)
        if res.status_code == 200:
            st.success(f"Created workflow {wf_id} successfully!")
            return True
        else:
            st.error(f"Failed to create: {res.text}")
    except Exception as e:
        st.error(f"Error creating workflow: {e}")
    return False

def delete_workflow(wf_id):
    try:
        res = requests.delete(f"{API_URL}/config/workflows/{wf_id}")
        if res.status_code == 200:
            st.success(f"Deleted workflow {wf_id} successfully!")
            return True
        else:
            st.error(f"Failed to delete: {res.text}")
    except Exception as e:
        st.error(f"Error deleting workflow: {e}")
    return False

def create_step(step_data):
    try:
        res = requests.post(f"{API_URL}/config/steps", json=step_data)
        if res.status_code == 200:
            st.success(f"Created step {step_data.get('id')} successfully!")
            return True
        else:
            st.error(f"Failed to create step: {res.text}")
    except Exception as e:
        st.error(f"Error creating step: {e}")
    return False

def update_step(step_id, step_data):
    try:
        res = requests.put(f"{API_URL}/config/steps/{step_id}", json=step_data)
        if res.status_code == 200:
            st.success(f"Updated step {step_id} successfully!")
            return True
        else:
            st.error(f"Failed to update step: {res.text}")
    except Exception as e:
        st.error(f"Error updating step: {e}")
    return False

def delete_step(step_id):
    try:
        res = requests.delete(f"{API_URL}/config/steps/{step_id}")
        if res.status_code == 200:
            st.success(f"Deleted step {step_id} successfully!")
            return True
        else:
            st.error(f"Failed to delete step: {res.text}")
    except Exception as e:
        st.error(f"Error deleting step: {e}")
    return False

def update_component(comp_id, content, description, citation=None, citation_full=None):
    try:
        payload = {
            "content": content,
            "description": description,
            "citation": citation,
            "citation_full": citation_full
        }
        res = requests.put(f"{API_URL}/config/components/{comp_id}", json=payload)
        if res.status_code == 200:
            st.success(f"Updated component {comp_id} successfully!")
            return True
        else:
            st.error(f"Failed to update component: {res.text}")
    except Exception as e:
        st.error(f"Error updating component: {e}")
    return False

def update_workflow(wf_id, sequence, description, model_mapping):
    try:
        payload = {
            "sequence": sequence,
            "description": description,
            "default_model_mapping": model_mapping
        }
        res = requests.put(f"{API_URL}/config/workflows/{wf_id}", json=payload)
        if res.status_code == 200:
            st.success(f"Updated workflow {wf_id} successfully!")
            return True
        else:
            st.error(f"Failed to update workflow: {res.text}")
    except Exception as e:
        st.error(f"Error updating workflow: {e}")
    return False


# --- UI Layout ---

tab1, tab2, tab3 = st.tabs(["Prompts & Rules", "Workflows", "Steps"])

with tab1:
    st.header("Prompts & Rules")
    
    # --- Create New Component ---
    with st.expander("➕ Create New Component"):
        new_comp_id = st.text_input("Component ID (Unique)", placeholder="PROMPT_NEW_TASK")
        new_comp_name = st.text_input("Name", placeholder="My Custom Prompt")
        new_comp_type = st.selectbox("Type", ["prompt", "rule", "mandate", "persona", "context", "reference", "other"])
        new_comp_desc = st.text_input("Description", placeholder="What this component does")
        new_comp_content = st.text_area("Content", height=200, placeholder="Enter text or Jinja2 template...")
        new_comp_citation = st.text_input("Citation (Short)", placeholder="(Author Year)")
        
        if st.button("Create Component"):
            if not new_comp_id:
                st.error("Component ID is required.")
            else:
                try:
                    payload = {
                        "id": new_comp_id,
                        "name": new_comp_name,
                        "type": new_comp_type,
                        "description": new_comp_desc,
                        "content": new_comp_content,
                        "citation": new_comp_citation,
                        "module": "config", 
                        "component_class": "ConfigComponent"
                    }
                    res = requests.post(f"{API_URL}/config/components", json=payload)
                    if res.status_code == 200:
                        st.success(f"Created component {new_comp_id} successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to create: {res.text}")
                except Exception as e:
                    st.error(f"Error creating component: {e}")
    st.divider()
    
    components = get_components()
    if components:
        # Filter options
        col_filter, col_select = st.columns([1, 2])
        
        with col_filter:
            # Get unique types
            all_types = sorted(list(set([c.get('type', 'Unknown') for c in components])))
            selected_type_filter = st.multiselect("Filter by Type", all_types, default=all_types)
            
        filtered_components = [c for c in components if c.get('type', 'Unknown') in selected_type_filter]
        
        with col_select:
            comp_names = [c.get('id') for c in filtered_components]
            selected_comp_name = st.selectbox("Select Component to Edit", comp_names, key="select_component_tab1")
        
        # Find selected component data
        selected_comp = next((c for c in components if (c.get('id') == selected_comp_name or c.get('name') == selected_comp_name)), None)
        
        if selected_comp:
            st.info(f"ID: `{selected_comp.get('id')}` | Name: `{selected_comp.get('name')}` | Type: `{selected_comp.get('type')}`")
            
            new_desc = st.text_input("Description", value=selected_comp.get('description', ''), key=f"desc_{selected_comp_name}")
            new_citation = st.text_input("Citation (Short)", value=selected_comp.get('citation', ''), key=f"citation_{selected_comp_name}")
            new_citation_full = st.text_area("Bibliography Entry (Full)", value=selected_comp.get('citation_full', ''), key=f"citation_full_{selected_comp_name}", height=100)
            
            # Content Editor
            content = selected_comp.get('content', '')
            # Try to pretty print if JSON
            try:
                if isinstance(content, str) and (content.startswith('{') or content.startswith('[')):
                     content = json.dumps(json.loads(content), indent=2)
            except:
                pass
                
            new_content = st.text_area("Content (Jinja2 Template or JSON)", value=content, height=400, key=f"comp_content_{selected_comp_name}")
            
            if st.button("Save Changes", key=f"save_comp_{selected_comp_name}"):
                update_component(selected_comp_name, new_content, new_desc, new_citation, new_citation_full)
    else:
        st.warning("No components found.")

with tab2:
    st.header("Workflows")
    
    all_steps = get_steps()
    available_step_ids = [s.get('id') for s in all_steps] if all_steps else []

    # --- Create New Workflow ---
    with st.expander("➕ Create New Workflow"):
        # Note: We don't use st.form here because we need dynamic updates for Model Mapping based on selected steps.
        new_wf_id = st.text_input("Workflow ID (Unique)", placeholder="WORKFLOW_NEW")
        new_wf_name = st.text_input("Workflow Name", placeholder="My Custom Workflow")
        new_wf_desc = st.text_input("Description", help="Human-readable explanation of the workflow's purpose.")
        
        new_wf_steps = st.multiselect(
            "Initial Steps",
            options=available_step_ids,
            default=["STEP_1_GUARD"] if "STEP_1_GUARD" in available_step_ids else [],
            key="new_wf_steps",
            help="Select the steps for this workflow in order. The order of selection determines the execution order."
        )
        
        # Model Mapping for New Workflow
        st.subheader("Model Mapping")
        new_wf_mapping = {}
        
        AVAILABLE_MODELS = get_available_models()
        
        if new_wf_steps:
            for step_id in new_wf_steps:
                chosen_model = st.selectbox(
                    f"Model for {step_id}",
                    options=AVAILABLE_MODELS,
                    index=0, # Default to first (gpt-4o)
                    key=f"new_model_{step_id}",
                    help=f"Select the AI model to use for the step '{step_id}'."
                )
                new_wf_mapping[step_id] = chosen_model
        else:
            st.info("Select steps to configure model mapping.")

        if st.button("Create Workflow", type="primary"):
            if not new_wf_id:
                st.error("Workflow ID is required.")
            else:
                if create_workflow(new_wf_id, new_wf_name, new_wf_steps, new_wf_desc, new_wf_mapping):
                    st.rerun()

    st.divider()
    
    workflows = get_workflows()
    # all_steps already fetched above
    
    if workflows:
        wf_ids = [w.get('id') for w in workflows]
        selected_wf_id = st.selectbox("Select Workflow", wf_ids)
        
        selected_wf = next((w for w in workflows if w.get('id') == selected_wf_id), None)
        
        if selected_wf:
            st.info(f"ID: `{selected_wf.get('id')}`")
            edit_wf_desc = st.text_input("Description", value=selected_wf.get('description', ''), key=f"edit_wf_desc_{selected_wf_id}", help="Human-readable explanation of the workflow's purpose.")
            
            # Steps Editor (Multiselect)
            # Note: The DB uses 'sequence' for the list of step IDs.
            current_sequence = selected_wf.get('sequence', selected_wf.get('steps', []))
            available_step_ids = [s.get('id') for s in all_steps]
            
            # Ensure current steps are in available list (to avoid errors if a step was deleted)
            valid_current_steps = [s for s in current_sequence if s in available_step_ids]
            
            selected_steps = st.multiselect(
                "Steps Sequence",
                options=available_step_ids,
                default=valid_current_steps,
                key=f"edit_wf_steps_{selected_wf_id}",
                help="Select the steps for this workflow in order. The order of selection determines the execution order."
            )
            
            # Model Mapping Editor (Per-Step Selectbox)
            st.subheader("Model Mapping")
            current_mapping = selected_wf.get('default_model_mapping', {})
            new_mapping = {}
            
            AVAILABLE_MODELS = get_available_models()
            
            if selected_steps:
                for step_id in selected_steps:
                    # Determine current model for this step
                    current_model = current_mapping.get(step_id, "gpt-4o")
                    if current_model not in AVAILABLE_MODELS:
                        AVAILABLE_MODELS.append(current_model)
                        
                    chosen_model = st.selectbox(
                        f"Model for {step_id}",
                        options=AVAILABLE_MODELS,
                        index=AVAILABLE_MODELS.index(current_model),
                        key=f"model_{step_id}_{selected_wf_id}",
                        help=f"Select the AI model to use for the step '{step_id}'."
                    )
                    new_mapping[step_id] = chosen_model
            else:
                st.info("Select steps to configure model mapping.")
            
            col_save, col_validate, col_delete = st.columns([1, 1, 1])
            
            with col_save:
                if st.button("Save Workflow", key=f"save_wf_{selected_wf_id}"):
                    # No need to parse JSON anymore, we have the objects directly
                    update_workflow(selected_wf_id, selected_steps, edit_wf_desc, new_mapping)
            
            with col_validate:
                if st.button("Validate Workflow", key=f"val_wf_{selected_wf_id}"):
                    try:
                        # Validate the *current* selection
                        current_sequence = selected_steps
                        # Create a mock workflow object for validation
                        mock_wf = selected_wf.copy()
                        mock_wf['sequence'] = current_sequence
                        
                        report = validate_workflow(mock_wf, all_steps)
                        for line in report:
                            if "✅" in line:
                                st.success(line)
                            elif "❌" in line:
                                st.error(line)
                            else:
                                st.warning(line)
                                
                    except Exception as e:
                        st.error(f"Validation failed: {e}")
            
            with col_delete:
                if st.button("🗑️ Delete Workflow", key=f"del_wf_{selected_wf_id}", type="primary"):
                    if delete_workflow(selected_wf_id):
                        st.rerun()

with tab3:
    st.header("Steps")

    # --- Fetch Dynamic Options ---
    try:
        res = requests.get(f"{API_URL}/config/introspection")
        if res.status_code == 200:
            introspection_data = res.json()
            AVAILABLE_SCHEMAS = introspection_data.get('schemas', [])
            AVAILABLE_HOOKS = introspection_data.get('hooks', [])
            AVAILABLE_AGENTS = introspection_data.get('agents', [])
        else:
            st.error(f"Failed to fetch introspection data: {res.text}")
            AVAILABLE_SCHEMAS = []
            AVAILABLE_HOOKS = []
            AVAILABLE_AGENTS = []
    except Exception as e:
        st.error(f"Error fetching introspection data: {e}")
        AVAILABLE_SCHEMAS = []
        AVAILABLE_HOOKS = []
        AVAILABLE_AGENTS = []

    # Fetch available text components (Prompts, Rules, etc.)
    all_components = get_components()
    # Allow all text-based component types. Check case-insensitively.
    TEXT_COMPONENT_TYPES = ["prompt", "rule", "mandate", "persona", "context", "reference"]
    available_prompts = [
        c.get('id') for c in all_components 
        if c.get('type', '').lower() in TEXT_COMPONENT_TYPES
    ] if all_components else []

    # --- Create New Step ---
    with st.expander("➕ Create New Step"):
        with st.form("create_step_form"):
            col_meta, col_config = st.columns([1, 1])
            
            with col_meta:
                new_step_id = st.text_input(
                    "Step ID (Unique)", 
                    placeholder="STEP_NEW",
                    help="Unique identifier for this step (e.g., 'STEP_1_GUARD'). Used when defining Workflows."
                )
                new_step_desc = st.text_input(
                    "Description", 
                    placeholder="What this step does",
                    help="Human-readable explanation of the step's purpose.",
                    key="new_step_desc"
                )
                new_step_comp = st.selectbox(
                    "Component Class", 
                    [""] + AVAILABLE_AGENTS,
                    help="The Python class (Agent) that executes the logic for this step. Determines the 'brain' of the step.",
                    key="new_step_comp"
                )
                
                # Structured Inputs
                new_input_schema = st.selectbox(
                    "Input Schema", 
                    [""] + AVAILABLE_SCHEMAS,
                    help="Pydantic model defining the expected structure of the input data."
                )
                new_output_schema = st.selectbox(
                    "Output Schema", 
                    [""] + AVAILABLE_SCHEMAS,
                    help="Pydantic model defining the expected structure of the output data."
                )
            
            with col_config:
                new_pre_hooks = st.multiselect(
                    "Pre-Hooks", 
                    AVAILABLE_HOOKS,
                    help="Functions executed BEFORE the agent runs. Useful for data sanitization or preparation."
                )
                new_llm_prompts = st.multiselect(
                    "LLM Prompts & Components", 
                    available_prompts,
                    help="System instructions (prompts, rules, mandates) passed to the LLM. You can select multiple components to be concatenated."
                )
                new_post_hooks = st.multiselect(
                    "Post-Hooks", 
                    AVAILABLE_HOOKS,
                    help="Functions executed AFTER the agent runs. Useful for scoring, formatting, or saving results."
                )
                
                # Custom Instructions (Ad-Hoc)
                new_custom_instr = st.text_area(
                    "Custom Instructions (Ad-Hoc)",
                    help="Write specific instructions for this step here. These will be appended to the selected prompts.",
                    height=150
                )
                new_step_citation = st.text_input("Citation (Short)", help="In-text citation for custom instructions.")
                new_step_citation_full = st.text_area("Bibliography Entry (Full)", help="Full reference for bibliography.", height=100)

            # Live Preview of JSON (Visual Only)
            preview_data_display = {
                "id": new_step_id,
                "description": new_step_desc,
                "component": new_step_comp,
                "input_schema": new_input_schema,
                "output_schema": new_output_schema,
                "execution_config": {
                    "pre_hooks": new_pre_hooks,
                    "llm_prompts": new_llm_prompts,
                    "post_hooks": new_post_hooks,
                    "custom_instruction": new_custom_instr,
                    "citation": new_step_citation,
                    "citation_full": new_step_citation_full
                }
            }
            st.caption("JSON Preview (Generated)")
            st.code(json.dumps(preview_data_display, indent=2), language="json")
            
            submitted_step = st.form_submit_button("Create Step")
            if submitted_step:
                if not new_step_id:
                    st.error("Step ID is required.")
                else:
                    # Include component in the actual payload
                    payload = preview_data_display.copy()
                    payload['component'] = new_step_comp
                    if create_step(payload):
                        st.rerun()

    st.divider()
    
    all_steps = get_steps()
    if all_steps:
        step_ids = [s.get('id') for s in all_steps]
        selected_step_id = st.selectbox("Select Step", step_ids)
        
        selected_step = next((s for s in all_steps if s.get('id') == selected_step_id), None)
        
        if selected_step:
            st.info(f"ID: `{selected_step.get('id')}`")
            
            # Editable Fields
            edit_step_desc = st.text_input(
                "Description", 
                value=selected_step.get('description', ''),
                help="Human-readable explanation of the step's purpose.",
                key=f"edit_step_desc_{selected_step_id}"
            )
            
            current_comp = selected_step.get('component', '')
            if current_comp not in AVAILABLE_AGENTS and current_comp:
                AVAILABLE_AGENTS.append(current_comp)
                
            edit_step_comp = st.selectbox(
                "Component Class", 
                [""] + AVAILABLE_AGENTS, 
                index=(AVAILABLE_AGENTS.index(current_comp) + 1) if current_comp in AVAILABLE_AGENTS else 0,
                help="The Python class (Agent) that executes the logic for this step. Determines the 'brain' of the step.",
                key=f"edit_step_comp_{selected_step_id}"
            )
            
            current_input_schema = selected_step.get('input_schema', '')
            if current_input_schema not in AVAILABLE_SCHEMAS and current_input_schema:
                 AVAILABLE_SCHEMAS.append(current_input_schema)
            
            current_output_schema = selected_step.get('output_schema', '')
            if current_output_schema not in AVAILABLE_SCHEMAS and current_output_schema:
                 AVAILABLE_SCHEMAS.append(current_output_schema)

            edit_input_schema = st.selectbox(
                "Input Schema", 
                [""] + AVAILABLE_SCHEMAS, 
                index=(AVAILABLE_SCHEMAS.index(current_input_schema) + 1) if current_input_schema in AVAILABLE_SCHEMAS else 0,
                help="Pydantic model defining the expected structure of the input data.",
                key=f"edit_input_schema_{selected_step_id}"
            )
            edit_output_schema = st.selectbox(
                "Output Schema", 
                [""] + AVAILABLE_SCHEMAS, 
                index=(AVAILABLE_SCHEMAS.index(current_output_schema) + 1) if current_output_schema in AVAILABLE_SCHEMAS else 0,
                help="Pydantic model defining the expected structure of the output data.",
                key=f"edit_output_schema_{selected_step_id}"
            )
            
            exec_config = selected_step.get('execution_config', {})
            
            edit_pre_hooks = st.multiselect(
                "Pre-Hooks", 
                AVAILABLE_HOOKS, 
                default=[h for h in exec_config.get('pre_hooks', []) if h in AVAILABLE_HOOKS],
                help="Functions executed BEFORE the agent runs. Useful for data sanitization or preparation.",
                key=f"edit_pre_hooks_{selected_step_id}"
            )
            edit_llm_prompts = st.multiselect(
                "LLM Prompts & Components", 
                available_prompts, 
                default=[p for p in exec_config.get('llm_prompts', []) if p in available_prompts],
                help="System instructions (prompts, rules, mandates) passed to the LLM. You can select multiple components to be concatenated.",
                key=f"edit_llm_prompts_{selected_step_id}"
            )
            
            edit_post_hooks = st.multiselect(
                "Post-Hooks", 
                AVAILABLE_HOOKS, 
                default=[h for h in exec_config.get('post_hooks', []) if h in AVAILABLE_HOOKS],
                help="Functions executed AFTER the agent runs. Useful for scoring, formatting, or saving results.",
                key=f"edit_post_hooks_{selected_step_id}"
            )
            
            # Custom Instructions (Ad-Hoc)
            current_custom_instr = exec_config.get('custom_instruction', '')
            edit_custom_instr = st.text_area(
                "Custom Instructions (Ad-Hoc)",
                value=current_custom_instr,
                help="Write specific instructions for this step here. These will be appended to the selected prompts.",
                height=150,
                key=f"edit_custom_instr_{selected_step_id}"
            )
            
            edit_step_citation = st.text_input("Citation (Short)", value=exec_config.get('citation', ''), key=f"edit_step_citation_{selected_step_id}")
            edit_step_citation_full = st.text_area("Bibliography Entry (Full)", value=exec_config.get('citation_full', ''), key=f"edit_step_citation_full_{selected_step_id}", height=100)
            
            # Live Preview of JSON (Visual Only)
            updated_step_preview_display = {
                "id": selected_step_id,
                "description": edit_step_desc,
                "component": edit_step_comp,
                "input_schema": edit_input_schema,
                "output_schema": edit_output_schema,
                "execution_config": {
                    "pre_hooks": edit_pre_hooks,
                    "llm_prompts": edit_llm_prompts,
                    "post_hooks": edit_post_hooks,
                    "custom_instruction": edit_custom_instr,
                    "citation": edit_step_citation,
                    "citation_full": edit_step_citation_full
                }
            }
            st.caption("JSON Preview (Live)")
            st.code(json.dumps(updated_step_preview_display, indent=2), language="json")
            
            col_save_step, col_del_step = st.columns([1, 1])
            with col_save_step:
                if st.button("Save Changes", key=f"save_step_{selected_step_id}"):
                    # Include component in the actual payload
                    payload = updated_step_preview_display.copy()
                    payload['component'] = edit_step_comp
                    if update_step(selected_step_id, payload):
                        st.rerun()
            
            with col_del_step:
                if st.button("🗑️ Delete Step", key=f"del_step_{selected_step_id}", type="primary"):
                     if delete_step(selected_step_id):
                         st.rerun()

# --- Sidebar Actions ---
with st.sidebar:
    st.divider()
    st.header("System Maintenance")
    
    if st.button("💾 Save State to Seed"):
        try:
            res = requests.post(f"{API_URL}/config/export-seed")
            if res.status_code == 200:
                st.success("System state saved to seed_data.json!")
            else:
                st.error(f"Failed to save state: {res.text}")
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("⚠️ Reset DB from Seed"):
        try:
            res = requests.post(f"{API_URL}/config/reset-from-seed")
            if res.status_code == 200:
                st.success("Database reset from seed data!")
                st.rerun()
            else:
                st.error(f"Failed to reset: {res.text}")
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("🚀 Deploy Mock to Production"):
        st.warning("This will overwrite the PRODUCTION database with the current Mock configuration (via seed_data.json).")
        if st.checkbox("Confirm Deployment"):
            try:
                res = requests.post(f"{API_URL}/config/deploy-mock-to-prod")
                if res.status_code == 200:
                    st.success("Mock environment deployed to Production DB!")
                else:
                    st.error(f"Failed to deploy: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")

    if st.button("⬅️ Deploy Production to Mock"):
        st.warning("This will overwrite the MOCK database with the current Production configuration (via seed_data.json).")
        if st.checkbox("Confirm Prod to Mock Deployment"):
            try:
                res = requests.post(f"{API_URL}/config/deploy-prod-to-mock")
                if res.status_code == 200:
                    st.success("Production environment deployed to Mock DB!")
                else:
                    st.error(f"Failed to deploy: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
