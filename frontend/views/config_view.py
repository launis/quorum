"""Global Configuration View."""

import pandas as pd
import requests
import streamlit as st


def render_config_view(api_client, backend_url: str):
    """Renders the Configuration Manager (Components, Steps, Workflows, Models).

    Args:
        api_client: The API client instance.
        backend_url (str): The base URL of the backend.
    """
    st.header("⚙️ Configuration Manager")
    st.markdown("Global settings for Components, Steps, Workflows, and Model Strategies.")

    tabs = st.tabs(["🧩 Components", "👣 Steps", "🛠️ Workflows", "🧠 Model Registry"])

    # --- Component Manager ---
    with tabs[0]:
        st.subheader("Component Library")
        # Fetch all, but separate by type
        all_items = api_client.get_components()

        # Filter: "Real" Components (Editable) vs System Agents (Code)
        config_components = [c for c in all_items if c.get("type") not in ["agent", "critic", "processor"]]
        system_agents = [c for c in all_items if c.get("type") in ["agent", "critic", "processor"]]

        # Filter & Search (Config Components Only)
        # Filter & Search (Config Components Only)
        c_col_search, c_col_filter = st.columns([2, 1])
        with c_col_search:
            search = st.text_input("Search Components", "")
        with c_col_filter:
            # Dynamic Filter options
            all_av_types = sorted(list({c.get("type") for c in config_components if c.get("type")}))
            type_filter = st.multiselect("Filter by Type", all_av_types)

        if search:
            config_components = [c for c in config_components if search.lower() in str(c).lower()]

        if type_filter:
            config_components = [c for c in config_components if c.get("type") in type_filter]

        target_cid = None

        # List (Config Only)
        with st.expander("Component List", expanded=True):
            df = pd.DataFrame(config_components)
            if not df.empty:
                # Ensure useful columns exist
                cols = ["id", "type", "description"]
                for col in cols:
                    if col not in df.columns:
                        df[col] = ""

                # Enable selection
                event = st.dataframe(
                    df[cols], width="stretch", on_select="rerun", selection_mode="single-row", key="comp_list_selection"
                )

                if len(event.selection.rows) > 0:
                    selected_index = event.selection.rows[0]
                    # Map visual index back to the valid list
                    # (df maps 1:1 to config_components because we built df from it)
                    if selected_index < len(config_components):
                        target_cid = config_components[selected_index]["id"]

        # Editor
        st.divider()
        st.subheader("Editor")

        c_mode = st.radio("Action", ["Edit Existing", "Create New", "Delete"], horizontal=True)

        if c_mode in ["Edit Existing", "Delete"]:
            if not target_cid:
                st.info("👆 **Please select a component from the list above to proceed.**")
            else:
                st.write(f"selected: **{target_cid}**")

        if c_mode == "Delete" and target_cid:
            # Check type before allowing delete
            comp_to_del = next((c for c in config_components if c["id"] == target_cid), {})
            if comp_to_del.get("type") in ["agent", "critic", "processor"]:
                st.error(f"⛔ Cannot delete System Component '{target_cid}'. It is part of the codebase.")
            elif st.button(f"Confirm Delete '{target_cid}'", type="primary"):
                try:
                    requests.delete(f"{backend_url}/config/components/{target_cid}").raise_for_status()
                    st.success("Deleted!")
                    st.rerun()
                except Exception as e:
                    # Backend returns the logic for why it failed (e.g. used in steps)
                    st.error(f"Delete failed: {e}")

        elif target_cid or c_mode == "Create New":
            # Load Data
            if c_mode == "Edit Existing" and target_cid:
                comp_data = next((c for c in config_components if c["id"] == target_cid), {})
            else:
                comp_data = {"id": "", "type": "prompt", "content": ""}

            # PROTECT SYSTEM COMPONENTS
            if comp_data.get("type") in ["agent", "critic", "processor"]:
                st.info(
                    f"🔒 **System Component ({comp_data.get('type')})**: "
                    f"This component is defined in Python code and cannot be edited in the UI."
                )
                st.json(comp_data)
            else:
                with st.form("comp_form"):
                    # Form Content Indented
                    c_col1, c_col2 = st.columns(2)
                    with c_col1:
                        new_id = st.text_input("ID", comp_data.get("id"), disabled=(c_mode == "Edit Existing"))
                    with c_col2:
                        # 1. Fetch Standard Types from DB Registry (User Requirement)
                        try:
                            # Use a try-except block in case api_client isn't updated or component missing
                            import json

                            reg_comp = next((c for c in all_items if c["id"] == "SYSTEM_COMPONENT_TYPES"), None)
                            if reg_comp and reg_comp.get("content"):
                                standard_types = set(json.loads(reg_comp.get("content")))
                            else:
                                # Fallback if registry missing (e.g. before migration)
                                standard_types = set()
                        except Exception as e:
                            st.warning(f"Could not load type registry: {e}")
                            standard_types = set()

                        # 2. Add any other types found in actual components (Robustness)
                        existing_types = {c.get("type") for c in config_components if c.get("type")}

                        # 3. Combine
                        available_types = sorted(list(standard_types.union(existing_types)))

                        # Determine index safely
                        current_type = comp_data.get("type")
                        type_index = available_types.index(current_type) if current_type in available_types else 0

                        new_type = st.selectbox("Type", available_types, index=type_index)

                    new_desc = st.text_input("Description", comp_data.get("description", ""))
                    new_content = st.text_area("Content", comp_data.get("content", ""), height=300)

                    submitted = st.form_submit_button("Save Component")
                    if submitted:
                        payload = {"id": new_id, "type": new_type, "description": new_desc, "content": new_content}
                        try:
                            if c_mode == "Create New":
                                requests.post(f"{backend_url}/config/components", json=payload).raise_for_status()
                                st.success("Created!")
                            else:
                                requests.put(
                                    f"{backend_url}/config/components/{new_id}", json=payload
                                ).raise_for_status()
                                st.success("Updated!")

                            st.rerun()
                        except Exception as e:
                            st.error(f"Save failed: {e}")

        # System Agents (Filtered Out)
        if system_agents:
            st.divider()
            with st.expander("🔌 System Agents (Codebase components - Read Only)", expanded=False):
                st.info(
                    "These agents are registered in the system but defined in Python code. They cannot be edited here."
                )
                s_df = pd.DataFrame(system_agents)
                # Ensure useful columns exist
                s_cols = ["id", "class_name", "module"]
                for col in s_cols:
                    if col not in s_df.columns:
                        s_df[col] = ""
                st.dataframe(s_df[s_cols], width="stretch")

    # --- Step Manager (GUI) ---
    with tabs[1]:
        st.subheader("Step Configuration Manager")
        st.info("""
        **Info:** A "Step" is a configured instance of an **Agent Class**.
        - You CAN create new steps here (e.g., `step_analyst_v2`) by re-using existing logic (e.g., `AnalystAgent`) with different prompts.
        - You CANNOT create new Python logic (Classes) here. That requires backend coding in `backend/agents/`.
        """)

        steps = requests.get(f"{backend_url}/config/steps").json()
        all_components = api_client.get_components()
        available_agents = api_client.get_builder_config_agents()
        agent_options = [a["name"] for a in available_agents]

        # Filter for prompt-like components
        prompt_options = [
            c["id"]
            for c in all_components
            if c.get("type")
            in [
                "header",
                "mandate",
                "rule",
                "operational_rule",
                "protocol",
                "method",
                "instruction",
                "task",
                "context",
                "heuristic",
            ]
        ]
        prompt_options.sort()

        s_mode = st.radio("Step Action", ["Edit Existing", "Create New"], horizontal=True, key="s_mode")

        target_sid = None
        if steps and s_mode == "Edit Existing":
            target_sid = st.selectbox("Select Step to Edit", [s["id"] for s in steps], key="step_sel")

        if target_sid or s_mode == "Create New":
            step_data = {}
            if s_mode == "Edit Existing" and target_sid:
                step_data = next((s for s in steps if s["id"] == target_sid), {})
            else:
                step_data = {
                    "id": "step_new",
                    "name": "New Step",
                    "component": agent_options[0] if agent_options else "AnalystAgent",
                    "execution_config": {"llm_prompts": []},
                }

            with st.form("step_gui_form"):
                c1, c2 = st.columns(2)
                with c1:
                    s_id = st.text_input("Step ID", step_data.get("id"), disabled=(s_mode != "Create New"))
                    s_name = st.text_input("Step Name", step_data.get("name", ""))
                with c2:
                    # Agent Component Selector
                    curr_agent = step_data.get("component", "AnalystAgent")
                    if curr_agent not in agent_options:
                        agent_options.append(curr_agent)
                    s_agent = st.selectbox("Agent Logic", agent_options, index=agent_options.index(curr_agent))

                    s_desc = st.text_input("Description", step_data.get("description", ""))

                st.markdown("**Prompt Assembly (Execution Config)**")
                st.caption("Select the prompt components that this step will use.")

                curr_prompts = step_data.get("execution_config", {}).get("llm_prompts", [])
                # Ensure all current are in options
                for p in curr_prompts:
                    if p not in prompt_options:
                        prompt_options.append(p)

                s_prompts = st.multiselect("Prompts", prompt_options, default=curr_prompts)

                # Matrix Selection (Specific to JudgeAgent)
                selected_matrix_id = None
                if s_agent == "JudgeAgent":
                    st.divider()
                    st.markdown("**Judge Configuration**")
                    matrices = [c for c in all_components if c.get("type") == "evaluation_matrix"]
                    matrix_opts = [m["id"] for m in matrices]

                    curr_matrix = step_data.get("execution_config", {}).get("matrix_id")
                    try:
                        idx = matrix_opts.index(curr_matrix) if curr_matrix in matrix_opts else 0
                    except ValueError:
                        idx = 0

                    selected_matrix_id = st.selectbox("Evaluation Matrix", matrix_opts, index=idx)

                if st.form_submit_button("Save Step Configuration"):
                    # Construct Payload
                    payload = step_data.copy()
                    if s_mode == "Create New":
                        payload["id"] = s_id
                    payload["name"] = s_name
                    payload["component"] = s_agent
                    payload["description"] = s_desc
                    if "execution_config" not in payload:
                        payload["execution_config"] = {}
                    payload["execution_config"]["llm_prompts"] = s_prompts

                    if selected_matrix_id:
                        payload["execution_config"]["matrix_id"] = selected_matrix_id

                    try:
                        if s_mode == "Create New":
                            requests.post(f"{backend_url}/config/steps", json=payload).raise_for_status()
                            st.success("Step Created!")
                        else:
                            requests.put(f"{backend_url}/config/steps/{s_id}", json=payload).raise_for_status()
                            st.success("Step Updated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # --- Workflow Manager (GUI) ---
    with tabs[2]:
        st.subheader("Workflow Configuration Manager")
        st.info("""
        **Difference to Workflow Builder:**
        - **This View (Manager):** modify the **low-level configuration** of workflows.
          (ID, Name, Default Model Strategies). Use this for system administration.
        - **Workflow Builder:** Use the visual **Builder** (in main menu) for designing flow logic, adding steps,
          and Prompt Fusion.
        """)

        token = st.session_state.get("auth_token")
        workflows = api_client.get_system_workflows(token=token)
        # Refresh steps for the list
        all_steps = requests.get(f"{backend_url}/config/steps").json()
        [s["id"] for s in all_steps]

        wf_mode = st.radio("Workflow Action", ["Edit Existing", "Create New"], horizontal=True, key="wf_gui_mode")

        target_wfid = None
        if workflows and wf_mode == "Edit Existing":
            target_wfid = st.selectbox("Select Workflow", [w["id"] for w in workflows], key="wf_gui_sel")

        if target_wfid or wf_mode == "Create New":
            wf_data = {}
            if wf_mode == "Edit Existing" and target_wfid:
                wf_data = next((w for w in workflows if w["id"] == target_wfid), {})
            else:
                wf_data = {"id": "new_workflow", "name": "New Workflow", "steps": [], "default_model_mapping": {}}

            # Main Config
            c1, c2 = st.columns(2)
            w_id_input = c1.text_input(
                "Workflow ID", wf_data.get("id"), disabled=(wf_mode != "Create New"), key="w_id_in"
            )
            w_name_input = c2.text_input("Workflow Name", wf_data.get("name"), key="w_name_in")
            w_desc_input = st.text_area("Description", wf_data.get("description", ""), key="w_desc_in")

            st.markdown("### Step Sequence")
            curr_steps = wf_data.get("steps", [])

            # Reordering UI - A simple text area is mostly robust for reordering IDs
            st.caption("Edit the sequence of Step IDs (one per line).")
            steps_text = st.text_area("Steps Sequence", value="\n".join(curr_steps), height=150, key="w_steps_txt")

            st.markdown("### Model Mapping")
            st.caption("Define Fast/Deep strategy for each step.")

            # Parse steps from text area to show mapping options
            # Parse steps from text area to show mapping options
            parsed_steps = [line.strip() for line in steps_text.split("\n") if line.strip()]

            curr_mapping = wf_data.get("default_model_mapping", {})
            new_mapping = curr_mapping.copy()

            # Grid for mapping
            with st.container(border=True):
                for step_id in parsed_steps:
                    c_s, c_m = st.columns([3, 1])
                    c_s.text(step_id)
                    val = curr_mapping.get(step_id, "fast")
                    new_val = c_m.selectbox(
                        "Strategy",
                        ["fast", "deep"],
                        index=0 if val == "fast" else 1,
                        key=f"map_{step_id}",
                        label_visibility="collapsed",
                    )
                    new_mapping[step_id] = new_val

            if st.button("Save Workflow Configuration"):
                # Save
                payload = {
                    "id": w_id_input,
                    "name": w_name_input,
                    "description": w_desc_input,
                    "steps": parsed_steps,
                    "default_model_mapping": new_mapping,
                }
                try:
                    if wf_mode == "Create New":
                        requests.post(f"{backend_url}/config/workflows", json=payload).raise_for_status()
                        st.success("Workflow Created!")
                    else:
                        requests.put(f"{backend_url}/config/workflows/{w_id_input}", json=payload).raise_for_status()
                        st.success("Workflow Updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- Model Registry ---
    with tabs[3]:
        st.subheader("Model Strategies (Fast vs Deep)")
        st.markdown("Define which physical models correspond to the logical 'Fast' and 'Deep' strategies.")

        # Fetch current
        strategies = api_client.get_model_strategies()  # Use client method if available, else requests
        if not strategies:
            # Fallback
            try:
                strategies = requests.get(f"{backend_url}/config/models/strategies").json()
            except Exception:
                pass

        registry = {}
        try:
            registry = requests.get(f"{backend_url}/config/models/registry").json()
        except Exception:
            pass

        if not registry:
            st.warning("No DB registry found. Using system defaults (read-only).")

        # 1. Config Controls
        # Only Provider selector now (Location via ENV)
        provider = st.selectbox("Provider", ["google", "openai", "mock"])

        # 2. Live Discovery
        avail_models_dict = {}
        avail_models = []
        try:
            # Call new API (Location handled by backend env)
            st.caption(f"Searching for {provider} models...")
            avail_models_dict = api_client.get_available_models(providers=[provider])
            # Extract list for current provider
            avail_models = avail_models_dict.get(provider, [])
            # Also check for error keys
            if f"{provider}_error" in avail_models_dict:
                st.error(f"Discovery Error: {avail_models_dict[f'{provider}_error']}")
        except Exception as e:
            st.warning(f"Discovery Failed: {e}")

        if provider:
            current_prov_config = registry.get(provider, {})

            st.markdown(f"#### {provider.upper()} Configuration")
            if avail_models:
                st.success(f"Discovered {len(avail_models)} models.")
            else:
                st.info("No models discovered automatically. You can type manual names.")

            col_f, col_d = st.columns(2)

            def model_selector(label, curr, key_suffix):
                if not avail_models:
                    return st.text_input(label, curr, key=f"txt_{key_suffix}")

                # Smart options
                options = list(avail_models)
                if curr and curr not in options:
                    options.insert(0, curr)

                # Safely determine index
                idx = 0
                if curr in options:
                    idx = options.index(curr)

                return st.selectbox(label, options, index=idx, key=f"sel_{key_suffix}")

            # Fast
            with col_f:
                st.markdown("⚡ **FAST Strategy**")
                f_conf = current_prov_config.get("fast", {})
                strict_def = avail_models[0] if avail_models else ""
                f_name = model_selector("Model Name", f_conf.get("model_name", strict_def), "fast")
                f_temp = st.number_input("Temperature", 0.0, 1.0, f_conf.get("temperature", 0.5), 0.1, key="f_temp")
                f_tokens = st.number_input(
                    "Max Tokens", 1024, 32000, int(f_conf.get("max_tokens", 8192)), 1024, key="f_tok"
                )

            # Deep
            with col_d:
                st.markdown("🧠 **DEEP Strategy**")
                d_conf = current_prov_config.get("deep", {})
                d_name = model_selector("Model Name", d_conf.get("model_name", strict_def), "deep")
                d_temp = st.number_input("Temperature", 0.0, 1.0, d_conf.get("temperature", 0.2), 0.05, key="d_temp")
                d_tokens = st.number_input(
                    "Max Tokens", 1, 1000000, int(d_conf.get("max_tokens", 16384)), 1024, key="d_tokens"
                )

            if st.button("Save Model Strategy"):
                # Construct updates
                new_reg = registry.copy()
                if provider not in new_reg:
                    new_reg[provider] = {}

                new_reg[provider]["fast"] = {"model_name": f_name, "temperature": f_temp, "max_tokens": f_tokens}
                new_reg[provider]["deep"] = {"model_name": d_name, "temperature": d_temp, "max_tokens": d_tokens}

                payload = {"registry": new_reg}
                try:
                    requests.post(f"{backend_url}/config/models/registry", json=payload).raise_for_status()
                    st.success("Model Registry Updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update registry: {e}")

        # 3. Test Ad-Hoc (Requested Feature)
        st.divider()
        with st.expander("🧪 Test Strategy (Ad-Hoc)", expanded=False):
            st.markdown("Test the configured strategy directly via `handler.call_llm` API.")

            t_col1, t_col2 = st.columns(2)
            with t_col1:
                t_mode = st.radio("Strategy Mode", ["fast", "deep"], horizontal=True)
            with t_col2:
                # Reuse provider from selection above
                st.info(f"Using Provider: **{provider}**")

            t_sys = st.text_area("System Instruction (Optional)", "", height=70)
            t_prompt = st.text_area("User Prompt", "Hello, who are you?", height=100)

            if st.button("Run Test Generation", type="primary"):
                with st.spinner("Generating..."):
                    result = api_client.call_llm_adhoc(
                        provider=provider,
                        mode=t_mode,
                        prompt=t_prompt,
                        system_instruction=t_sys if t_sys.strip() else None,
                    )

                    if "Error:" in result:
                        st.error(result)
                    else:
                        st.success("Generation Complete")
                        st.markdown(result)
