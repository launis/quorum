
import streamlit as st
import pandas as pd
import json
import uuid
import time
from frontend.components.builder_help import show_help_sidebar

def render_workflow_builder(api_client):
    st.header("Visual Workflow Builder")
    show_help_sidebar()

    # Initialize Session State for Builder
    if 'builder_mode' not in st.session_state:
        st.session_state['builder_mode'] = 'L' # L=List, E=Editor
    if 'builder_wf_id' not in st.session_state:
        st.session_state['builder_wf_id'] = None

    # --- LIST MODE (Dashboard) ---
    if st.session_state['builder_mode'] == 'L':
        st.subheader("Manage Workflows")

        # Create New Button
        if st.button("+ New Workflow"):
            st.session_state['builder_wf_id'] = None # New
            st.session_state['builder_mode'] = 'E'
            st.rerun()

        # Fetch Workflows
        wfs = api_client.get_builder_workflows()
        
        if wfs:
            # Table Layout
            for wf in wfs:
                with st.container():
                     c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
                     with c1:
                         st.markdown(f"**{wf.get('name', 'Untitled')}** (`{wf.get('id')}`)")
                         st.caption(f"{len(wf.get('steps', []))} steps")
                     with c2:
                         if st.button("Edit", key=f"edit_{wf['id']}"):
                             st.session_state['builder_wf_id'] = wf['id']
                             st.session_state['builder_mode'] = 'E'
                             st.rerun()
                     with c3:
                         if st.button("Copy", key=f"copy_{wf['id']}"):
                             st.session_state[f'show_copy_{wf["id"]}'] = True
                             
                     with c4:
                          if st.button("Delete", key=f"del_{wf['id']}"):
                               try:
                                   api_client.delete_builder_workflow(wf['id'])
                                   st.success("Deleted!")
                                   st.rerun()
                               except Exception as e:
                                   st.error(str(e))
                
                # Copy Dialog (inline)
                if st.session_state.get(f'show_copy_{wf["id"]}'):
                    with st.expander(f"Copy '{wf.get('name')}'", expanded=True):
                        new_name = st.text_input("New Name", value=f"{wf.get('name')} Copy", key=f"copy_name_{wf['id']}")
                        col_conf, col_cancel = st.columns(2)
                        if col_conf.button("Confirm Copy", key=f"conf_copy_{wf['id']}"):
                            try:
                                api_client.copy_builder_workflow(wf['id'], new_name)
                                st.success("Copied!")
                                st.session_state[f'show_copy_{wf["id"]}'] = False
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
                        if col_cancel.button("Cancel", key=f"cancel_copy_{wf['id']}"):
                             st.session_state[f'show_copy_{wf["id"]}'] = False
                             st.rerun()
                st.divider()
        else:
            st.info("No workflows found.")

    # --- EDITOR MODE ---
    elif st.session_state['builder_mode'] == 'E':
        target_id = st.session_state.get('builder_wf_id')
        is_new = target_id is None
        
        # Load Data if editing
        if 'editor_wf_data' not in st.session_state or st.session_state.get('editor_wf_id_ref') != target_id:
             if not is_new:
                 wf = api_client.get_builder_workflow(target_id)
                 if wf:
                     st.session_state['editor_wf_data'] = wf
                     st.session_state['editor_wf_id_ref'] = target_id
                 else:
                     st.error("Failed to load workflow.")
                     if st.button("Back"): st.session_state['builder_mode'] = 'L'; st.rerun()
                     return
             else:
                 # Default New
                 st.session_state['editor_wf_data'] = {
                     "name": "New Workflow",
                     "description": "",
                     "steps": [],
                     "default_model_mapping": {},
                     "ui_schema": {"nodes": []}
                 }
                 st.session_state['editor_wf_id_ref'] = None
        
        wf_data = st.session_state['editor_wf_data']

        # HEADER & CONTROLS
        c_head_1, c_head_2 = st.columns([3, 1])
        with c_head_1:
            if st.button("← Back to List"):
                st.session_state['builder_mode'] = 'L'
                del st.session_state['editor_wf_data'] # Clear cache
                st.rerun()
            st.header(f"Editing: {wf_data.get('name')}")
        
        with c_head_2:
             if st.button("Save Changes", type="primary"):
                 try:
                     payload = {
                         "name": wf_data['name'],
                         "description": wf_data.get('description', ''),
                         "steps": wf_data['steps'],
                         "default_model_mapping": wf_data['default_model_mapping'],
                         "ui_schema": wf_data.get('ui_schema', {})
                     }
                     if is_new:
                         res = api_client.create_builder_workflow(payload)
                         target_id = res['id']
                         st.session_state['builder_wf_id'] = target_id
                         st.success(f"Created {target_id}!")
                     else:
                         api_client.update_builder_workflow(target_id, payload)
                         st.success("Saved!")
                     st.rerun()
                 except Exception as e:
                     st.error(f"Save Failed: {e}")

        # EDITOR LAYOUT
        edit_tab, meta_tab = st.tabs(["Visual Builder", "Metadata"])
        
        with meta_tab:
            wf_data['name'] = st.text_input("Name", wf_data.get('name', ''))
            wf_data['description'] = st.text_area("Description", wf_data.get('description', ''))

        with edit_tab:
            # Fetch Available Agents
            available_agents = api_client.get_builder_config_agents()
            agent_names = [a['name'] for a in available_agents]

            col_canvas, col_props = st.columns([2, 1])
            
            with col_canvas:
                st.subheader("Workflow Chain")
                
                # Visualize Chain
                steps = wf_data.get('steps', [])
                
                if not steps:
                    st.info("Chain is empty. Add steps below.")
                
                # Chain Rendering
                for i, step_id in enumerate(steps):
                    # Highlight selected
                    is_selected = st.session_state.get('builder_act_step') == step_id
                    border_color = "red" if is_selected else None # Streamlit doesn't support border color param yet directly in container, but visuals help.
                    
                    # Card
                    # Use a different background or emoji if selected
                    prefix = "👉 " if is_selected else ""
                    
                    card_container = st.container(border=True)
                    with card_container:
                        c1, c2, c3, c4 = st.columns([1, 8, 3, 1])
                        with c1:
                            if st.button(f"{i+1}", key=f"sel_{i}_{step_id}", help="Click to Select"):
                                st.session_state['builder_act_step'] = step_id
                                st.rerun()
                                
                        with c2:
                            st.markdown(f"**{prefix}{step_id}**")
                            
                        with c3:
                            # Model Selector
                            current_map = wf_data.get('default_model_mapping', {})
                            current_model = current_map.get(step_id, 'fast')
                            new_model = st.selectbox("Model", ["fast", "deep"], index=0 if current_model=='fast' else 1, key=f"model_{i}_{step_id}", label_visibility="collapsed")
                            if new_model != current_model:
                                wf_data['default_model_mapping'][step_id] = new_model
                        with c4:
                            if st.button("🗑️", key=f"rm_{i}_{step_id}"):
                                steps.pop(i)
                                if st.session_state.get('builder_act_step') == step_id:
                                    st.session_state['builder_act_step'] = None
                                st.rerun() # Refresh immediately
                    
                    if i < len(steps) - 1:
                        st.markdown("⬇️") # Arrow

                st.divider()
                
                # Add Step UI
                with st.expander("Add Step Settings", expanded=True):
                    # Simplify: Add by Agent Type, auto-generate ID
                    sel_agent = st.selectbox("Select Agent to Add", agent_names)
                    
                    # Hack: Offer standard IDs for demo compatibility
                    std_ids = ["step_guard", "step_analyst", "step_judge", "step_coach", "step_xai"]
                    step_mode = st.radio("Mode", ["Standard Step", "New Custom Step"])
                    
                    if step_mode == "Standard Step":
                        sel_id = st.selectbox("Standard ID", std_ids)
                        if st.button("Add Standard Step"):
                            steps.append(sel_id)
                            st.rerun()
                    else:
                        st.caption("Custom Step Creation - Backend Support Pending")
                        cust_id = f"custom_step_{uuid.uuid4().hex[:6]}"
                        if st.button("Add Custom (Stub)"):
                            steps.append(cust_id)
                            st.rerun()

            with col_props:
                st.subheader("Properties")
                
                active_step = st.session_state.get('builder_act_step')
                if active_step:
                    st.info(f"Selected: `{active_step}`")
                    
                    # FETCH FULL STEP DETAILS (V2)
                    step_detail = api_client.get_builder_step(active_step)
                    
                    if not step_detail:
                        st.error("Could not load step details.")
                    else:
                        st.markdown(f"**Name:** {step_detail.get('name')}")
                        st.markdown(f"**Component:** `{step_detail.get('component')}`")
                        
                        # Model (Redundant but useful)
                        cur_model = wf_data.get('default_model_mapping', {}).get(active_step, 'fast')
                        st.markdown(f"**Current Model:** `{cur_model}`")
                        
                        st.divider()
                        st.markdown("### Hooks & Config (V2)")
                        
                        # Check if Custom
                        is_custom = "_custom_" in active_step
                        
                        if not is_custom:
                            st.warning("This is a SHARED Standard Step. Editing directly is restricted.")
                            if st.button("✨ Customize (Fork Step)"):
                                try:
                                    new_step = api_client.clone_builder_step(active_step)
                                    new_id = new_step['id']
                                    # Replace in Workflow
                                    idx = steps.index(active_step)
                                    steps[idx] = new_id
                                    # Update model mapping key
                                    if active_step in wf_data['default_model_mapping']:
                                        wf_data['default_model_mapping'][new_id] = wf_data['default_model_mapping'][active_step]
                                        del wf_data['default_model_mapping'][active_step]
                                    
                                    st.session_state['builder_act_step'] = new_id
                                    st.success(f"Forked to {new_id}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Fork failed: {e}")
                        else:
                            st.success("✅ Custom Step - Fully Editable")
                            
                            # PROMPT EDITOR
                            exec_config = step_detail.get('execution_config', {})
                            current_prompts = exec_config.get('llm_prompts', [])
                            
                            st.markdown("**Active Prompts (Hooks):**")
                            # We need list of ALL available prompts to add new ones. 
                            # For now, just simple string list editing or fetch from seed if possible.
                            # Let's assume user knows IDs or we just re-order/remove existing.
                            # V2+: Fetch all available hooks from backend.
                            
                            # Simple Re-order / Remove
                            new_prompts = st.multiselect("Edit Prompt Chain", options=current_prompts + ["HEADER_MANDATES", "MANDATE_1", "RULE_1"], default=current_prompts)
                            
                            if new_prompts != current_prompts:
                                if st.button("Save Prompt Configuration"):
                                    exec_config['llm_prompts'] = new_prompts
                                    try:
                                        api_client.update_builder_step(active_step, {"execution_config": exec_config})
                                        st.success("Prompts Updated!")
                                        time.sleep(0.5)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Update failed: {e}")

                    if st.button("Close Selection"):
                        st.session_state['builder_act_step'] = None
                        st.rerun()
                        
                else:
                    st.info("Select a step in the chain to view details.")
                    
                st.divider()
                st.markdown("### Prompt Fusion (V2)")
                st.caption("Select multiple *consecutive* steps to merge into a Panel.")
                
                # Filter strictly standard steps eligible for fusion to avoid mess
                fusion_candidates = ["step_logician", "step_falsifier", "step_causal", "step_detector", "step_overseer"]
                
                # UI Selection
                selected_fusion = st.multiselect("Steps to Fuse", [s for s in steps if s in fusion_candidates], default=[s for s in steps if s in fusion_candidates])
                
                if len(selected_fusion) > 1:
                    if st.button("🔥 Compile Fused Prompt (Replace with Panel)"):
                        try:
                            # Call API to perform the structural change
                            # We send the list of IDs to be replaced.
                            # The backend will return a NEW list of steps for the workflow.
                            
                            res = api_client.compile_fusion(target_id, selected_fusion)
                            
                            # Update local state
                            wf_data['steps'] = res['new_steps']
                            
                            # Clean up model mapping
                            for s in selected_fusion:
                                if s in wf_data['default_model_mapping']:
                                    del wf_data['default_model_mapping'][s]
                            
                            # Set Panel to Deep by default
                            wf_data['default_model_mapping']['step_panel'] = 'deep'
                            
                            # Save immediately to persist
                            payload = {
                                "name": wf_data['name'],
                                "description": wf_data.get('description', ''),
                                "steps": wf_data['steps'],
                                "default_model_mapping": wf_data['default_model_mapping'],
                                "ui_schema": wf_data.get('ui_schema', {})
                            }
                            api_client.update_builder_workflow(target_id, payload)
                            
                            st.success(f"Fusion Complete! Replaced {len(selected_fusion)} steps with 'step_panel'.")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fusion Failed: {e}")
                else:
                    st.caption("Select at least 2 steps to enable fusion.")

