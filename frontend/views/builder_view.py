
import time

import streamlit as st

from frontend.components.builder_help import show_help_sidebar


def render_workflow_builder(api_client: APIClient):
    """Renders the Visual Workflow Builder interface.

    Allows users to list, create, edit, copy, and delete workflows.
    Supports both a List Mode (L) and an Editor Mode (E) via session state.

    Args:
        api_client (APIClient): The API client instance.
    """
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

        token = st.session_state.get('auth_token')

        # Fetch Workflows
        wfs = api_client.get_builder_workflows(token=token)

        if wfs:
            # Table Layout
            for wf in wfs:
                with st.container():
                     c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
                     with c1:
                         # Append Visibility Badge
                         vis_icon = "🌍" if wf.get('is_public') else "🔒"
                         st.markdown(f"**{wf.get('name', 'Untitled')}** {vis_icon} (`{wf.get('id')}`)")
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
                                   api_client.delete_builder_workflow(wf['id'], token=token)
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
                                api_client.copy_builder_workflow(wf['id'], new_name, token=token)
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
        token = st.session_state.get('auth_token')

        # Fetch available strategies
        available_strategies = api_client.get_model_strategies()


        # Load Data if editing
        if 'editor_wf_data' not in st.session_state or st.session_state.get('editor_wf_id_ref') != target_id:
             if not is_new:
                 wf = api_client.get_builder_workflow(target_id, token=token)
                 if wf:
                     st.session_state['editor_wf_data'] = wf
                     st.session_state['editor_wf_id_ref'] = target_id
                 else:
                     st.error("Failed to load workflow.")
                     if st.button("Back"):
                         st.session_state['builder_mode'] = 'L'
                         st.rerun()
                     return
             else:
                 # Default New from Backend Template
                 template = api_client.get_workflow_template()
                 if template:
                     st.session_state['editor_wf_data'] = template
                 else:
                     # Emergency Fallback
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
                     chk_key = f"chk_public_{wf_data.get('id', 'new')}"
                     # Use widget state directly if available (handles pre-render update lag)
                     is_public_val = st.session_state.get(chk_key, wf_data.get('is_public', False))

                     payload = {
                         "name": wf_data['name'],
                         "description": wf_data.get('description', ''),
                         "steps": wf_data['steps'],
                         "default_model_mapping": wf_data['default_model_mapping'],
                         "ui_schema": wf_data.get('ui_schema', {}),
                         "is_public": is_public_val
                     }
                     if is_new:
                         res = api_client.create_builder_workflow(payload, token=token)
                         target_id = res['id']
                         st.session_state['builder_wf_id'] = target_id
                         # Update Cache for new WF
                         st.session_state['editor_wf_data'] = res
                         st.session_state['editor_wf_id_ref'] = target_id
                         st.success(f"Created {target_id}!")
                     else:
                         api_client.update_builder_workflow(target_id, payload, token=token)
                         # Update Cache for existing WF to reflect changes immediately
                         st.session_state['editor_wf_data'].update(payload)
                         st.success("Saved!")
                     st.rerun()
                 except Exception as e:
                     st.error(f"Save Failed: {e}")

        # EDITOR LAYOUT
        edit_tab, meta_tab = st.tabs(["Visual Builder", "Metadata"])

        with meta_tab:
            wf_data['name'] = st.text_input("Name", wf_data.get('name', ''))
            wf_data['description'] = st.text_area("Description", wf_data.get('description', ''))

            # Root Only: Public Toggle
            user = st.session_state.get('user', {})
            if user and user.get('role') == "ROOT":
                # Use dynamic key to prevent state bleeding between workflows
                chk_key = f"chk_public_{wf_data.get('id', 'new')}"
                wf_data['is_public'] = st.checkbox("Public (System Template)", value=wf_data.get('is_public', False), key=chk_key)
            else:
                 # Read only view if set
                 if wf_data.get('is_public', False):
                     st.info("🌍 Public System Template")

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

                # VALIDATION (Data Flow)
                validation_res = {"valid": True, "errors": []}
                if steps:
                     validation_res = api_client.validate_flow(steps)

                if not validation_res['valid']:
                     with st.expander("⚠️ Data Flow Issues Detected", expanded=True):
                         for err in validation_res['errors']:
                             st.error(err)

                # Chain Rendering
                for i, step_id in enumerate(steps):
                    # Highlight selected
                    is_selected = st.session_state.get('builder_act_step') == step_id

                    # Check for specific error for this step
                    step_error = None
                    for err in validation_res.get('errors', []):
                         # Naive matching: assumption that error message contains step index or ID
                         # Backend sends "Step X ..."
                         if f"Step {i+1}" in err:
                             step_error = err

                    # Card
                    # Use a different background or emoji if selected
                    prefix = "👉 " if is_selected else ""
                    if step_error: prefix = "❌ " + prefix

                    card_container = st.container(border=True)
                    with card_container:
                        c1, c2, c3, c4 = st.columns([1, 8, 3, 1])
                        with c1:
                            if st.button(f"{i+1}", key=f"sel_{i}_{step_id}", help="Click to Select"):
                                st.session_state['builder_act_step'] = step_id
                                st.rerun()

                        with c2:
                            st.markdown(f"**{prefix}{step_id}**")
                            if step_error:
                                st.caption(f":red[{step_error}]")

                        with c3:
                            # Model Selector
                            current_map = wf_data.get('default_model_mapping', {})
                            current_model = current_map.get(step_id, 'fast')

                            # Calculate index safely
                            try:
                                sel_idx = available_strategies.index(current_model)
                            except ValueError:
                                sel_idx = 0

                            new_model = st.selectbox("Model", available_strategies, index=sel_idx, key=f"model_{i}_{step_id}", label_visibility="collapsed")
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

                    # Dynamic fetching of steps from backend
                    available_steps_config = api_client.get_available_steps_config()
                    if available_steps_config:
                        std_ids = [s['id'] for s in available_steps_config]
                    else:
                        std_ids = []
                        st.error("Could not load standard steps from backend.")

                    step_mode = st.radio("Mode", ["Standard Step", "New Custom Step"])

                    if step_mode == "Standard Step":
                        sel_id = st.selectbox("Standard ID", std_ids)
                        if st.button("Add Standard Step"):
                            steps.append(sel_id)
                            # Ensure default model mapping exists
                            if "default_model_mapping" not in wf_data:
                                wf_data["default_model_mapping"] = {}
                            # Set default to 'fast' if not present
                            if sel_id not in wf_data["default_model_mapping"]:
                                wf_data["default_model_mapping"][sel_id] = "fast"
                            st.rerun()
                    else:
                        st.caption("Backend-Integrated Custom Step (V2)")

                        if st.button("Create & Add Custom Step"):
                            try:
                                # 1. Delegate Logic to Backend
                                new_step = api_client.create_custom_step_v2(sel_agent)
                                cust_id = new_step['id']

                                st.success(f"Created step {cust_id}")

                                # 2. Add to Workflow Sequence
                                steps.append(cust_id)

                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to create step: {e}")


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

                            # Fetch available prompts dynamically
                            all_components = api_client.get_components()
                            allowed_types = api_client.get_prompt_types()

                            # Fallback if no types returned (safety)
                            if not allowed_types:
                                allowed_types = ['prompt', 'mandate', 'rule', 'header', 'instruction']

                            prompt_options = []
                            for c in all_components:
                                if c.get('type') in allowed_types:
                                    prompt_options.append(c.get('id'))

                            # Fallback if fetch fails or empty
                            if not prompt_options:
                                prompt_options = current_prompts # Look only at what we have

                            # Ensure current prompts are in options (in case type is weird)
                            prompt_options = sorted(list(set(prompt_options + current_prompts)))

                            new_prompts = st.multiselect("Edit Prompt Chain", options=prompt_options, default=current_prompts)

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

                # Allow any steps to be fused (Backend validates logic)
                fusion_options = steps

                # UI Selection
                selected_fusion = st.multiselect("Steps to Fuse", fusion_options)


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

                            # Set Composite Step to Deep by default (using ID from response)
                            comp_id = res.get('composite_step_id', 'step_panel')
                            wf_data['default_model_mapping'][comp_id] = 'deep'


                            # Save immediately to persist
                            # Save immediately to persist
                            payload = {
                                "name": wf_data['name'],
                                "description": wf_data.get('description', ''),
                                "steps": wf_data['steps'],
                                "default_model_mapping": wf_data['default_model_mapping'],
                                "ui_schema": wf_data.get('ui_schema', {}),
                                "is_public": wf_data.get('is_public', False)
                            }
                            api_client.update_builder_workflow(target_id, payload, token=token)

                            st.success(f"Fusion Complete! Replaced {len(selected_fusion)} steps with 'step_panel'.")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fusion Failed: {e}")
                else:
                    st.caption("Select at least 2 steps to enable fusion.")

