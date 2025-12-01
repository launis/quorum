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

# --- UI Layout ---

tab1, tab2, tab3 = st.tabs(["Prompts & Rules", "Workflows", "Steps"])

with tab1:
    st.header("Prompts & Rules")
    
    components = get_components()
    if components:
        # Filter options
        comp_names = [c.get('id') or c.get('name') for c in components]
        selected_comp_name = st.selectbox("Select Component", comp_names)
        
        # Find selected component data
        selected_comp = next((c for c in components if (c.get('id') == selected_comp_name or c.get('name') == selected_comp_name)), None)
        
        if selected_comp:
            st.info(f"ID: `{selected_comp.get('id')}` | Name: `{selected_comp.get('name')}` | Type: `{selected_comp.get('type')}`")
            
            new_desc = st.text_input("Description", value=selected_comp.get('description', ''))
            
            # Content Editor
            content = selected_comp.get('content', '')
            # Try to pretty print if JSON
            try:
                if isinstance(content, str) and (content.startswith('{') or content.startswith('[')):
                     content = json.dumps(json.loads(content), indent=2)
            except:
                pass
                
            new_content = st.text_area("Content (Jinja2 Template or JSON)", value=content, height=400)
            
            if st.button("Save Changes", key="save_comp"):
                update_component(selected_comp_name, new_content, new_desc)
    else:
        st.warning("No components found.")

with tab2:
    st.header("Workflows")
    
    # --- Create New Workflow ---
    with st.expander("➕ Create New Workflow"):
        with st.form("create_wf_form"):
            new_wf_id = st.text_input("Workflow ID (Unique)", placeholder="WORKFLOW_NEW")
            new_wf_name = st.text_input("Workflow Name", placeholder="My Custom Workflow")
            new_wf_desc = st.text_input("Description")
            new_wf_steps_str = st.text_area("Initial Steps (JSON List of IDs)", value='["STEP_1_GUARD"]')
            new_wf_mapping_str = st.text_area("Model Mapping (JSON)", value='{}')
            
            submitted = st.form_submit_button("Create Workflow")
            if submitted:
                if not new_wf_id:
                    st.error("Workflow ID is required.")
                else:
                    try:
                        new_wf_steps = json.loads(new_wf_steps_str)
                        new_wf_mapping = json.loads(new_wf_mapping_str)
                        if create_workflow(new_wf_id, new_wf_name, new_wf_steps, new_wf_desc, new_wf_mapping):
                            st.rerun()
                    except json.JSONDecodeError:
                        st.error("Invalid JSON in steps or mapping.")

    st.divider()
    
    workflows = get_workflows()
    all_steps = get_steps()
    
    if workflows:
        wf_ids = [w.get('id') for w in workflows]
        selected_wf_id = st.selectbox("Select Workflow", wf_ids)
        
        selected_wf = next((w for w in workflows if w.get('id') == selected_wf_id), None)
        
        if selected_wf:
            st.info(f"ID: `{selected_wf.get('id')}`")
            edit_wf_desc = st.text_input("Description", value=selected_wf.get('description', ''), key="edit_wf_desc")
            
            # Steps Editor (JSON)
            # Note: The DB uses 'sequence' for the list of step IDs.
            steps_json = json.dumps(selected_wf.get('sequence', selected_wf.get('steps', [])), indent=2)
            new_steps_str = st.text_area("Steps Sequence (JSON)", value=steps_json, height=400)
            
            # Model Mapping Editor (JSON)
            mapping_json = json.dumps(selected_wf.get('default_model_mapping', {}), indent=2)
            new_mapping_str = st.text_area("Model Mapping (JSON)", value=mapping_json, height=200)
            
            col_save, col_validate, col_delete = st.columns([1, 1, 1])
            
            with col_save:
                if st.button("Save Workflow", key="save_wf"):
                    try:
                        new_steps = json.loads(new_steps_str)
                        new_mapping = json.loads(new_mapping_str)
                        update_workflow(selected_wf_id, new_steps, edit_wf_desc, new_mapping)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format in Steps or Mapping.")
            
            with col_validate:
                if st.button("Validate Workflow", key="val_wf"):
                    try:
                        # Validate the *current* JSON in the text area, not just what's in DB
                        current_sequence = json.loads(new_steps_str)
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
                                
                    except json.JSONDecodeError:
                        st.error("Cannot validate: Invalid JSON in Steps editor.")
            
            with col_delete:
                if st.button("🗑️ Delete Workflow", key="del_wf", type="primary"):
                    if delete_workflow(selected_wf_id):
                        st.rerun()
    else:
        st.warning("No workflows found.")

with tab3:
    st.header("Steps Definition")
    st.markdown("Define individual steps, their components, and prompts.")
    
    # --- Create New Step ---
    with st.expander("➕ Create New Step"):
        with st.form("create_step_form"):
            new_step_id = st.text_input("Step ID (Unique)", placeholder="STEP_NEW")
            new_step_name = st.text_input("Step Name", placeholder="My Custom Step")
            new_step_comp = st.text_input("Component Class", placeholder="AnalystAgent")
            new_step_json = st.text_area("Full JSON Definition", value='{\n  "input_schema": "RawInput",\n  "output_schema": "AnalysisResult",\n  "execution_config": {\n    "llm_prompts": ["PROMPT_1"],\n    "post_hooks": []\n  }\n}', height=200)
            
            submitted_step = st.form_submit_button("Create Step")
            if submitted_step:
                if not new_step_id:
                    st.error("Step ID is required.")
                else:
                    try:
                        step_data = json.loads(new_step_json)
                        step_data['id'] = new_step_id
                        step_data['name'] = new_step_name
                        step_data['component'] = new_step_comp
                        if create_step(step_data):
                            st.rerun()
                    except json.JSONDecodeError:
                        st.error("Invalid JSON.")

    st.divider()
    
    all_steps = get_steps()
    if all_steps:
        step_ids = [s.get('id') for s in all_steps]
        selected_step_id = st.selectbox("Select Step", step_ids)
        
        selected_step = next((s for s in all_steps if s.get('id') == selected_step_id), None)
        
        if selected_step:
            st.info(f"ID: `{selected_step.get('id')}`")
            
            # Editable JSON
            step_json = json.dumps(selected_step, indent=2)
            new_step_json = st.text_area("Step Definition (JSON)", value=step_json, height=500)
            
            col_save_step, col_del_step = st.columns([1, 1])
            
            with col_save_step:
                if st.button("Save Step", key="save_step"):
                    try:
                        updated_step = json.loads(new_step_json)
                        # Ensure ID matches
                        if updated_step.get('id') != selected_step_id:
                            st.warning("Changing ID is not supported via update. Create a new step instead.")
                        else:
                            update_step(selected_step_id, updated_step)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON.")
            
            with col_del_step:
                if st.button("🗑️ Delete Step", key="del_step", type="primary"):
                    if delete_step(selected_step_id):
                        st.rerun()
    else:
        st.warning("No steps found.")

# --- Sidebar Actions ---
with st.sidebar:
    st.divider()
    st.header("Actions")
    if st.button("📤 Export to Files"):
        trigger_export()
        st.info("This will overwrite the files in `data/templates` and `data/seed_data.json` with the current database state.")
