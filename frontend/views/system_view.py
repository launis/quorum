import pandas as pd
import streamlit as st


def render_system_view(api_client):
    """Renders the System Info / Configuration view.

    Displays technical configuration details and seed data references.

    Args:
        api_client: The API client instance.
    """
    st.header("System Configuration & Seed Data")

    token = st.session_state.get('auth_token')
    # data = api_client.get_seed_data(token=token)
    # Refactored to fetch live data
    workflows_list = api_client.get_workflows(token=token)
    steps_list = api_client.get_steps()
    components_list = api_client.get_components()
    
    if workflows_list and components_list:
        data = True # Dummy flag for indentation preservation if needed, or just flatten.
        # But for minimal diff, we adapt variables.
    else:
        data = False
        
    if data:
        # Get Workflows
        workflows = workflows_list
        workflow_options = {w['id']: w for w in workflows}

        # Workflow Selection
        st.subheader("Valitse Työnkulku (Select Workflow)")
        selected_wf_id = st.selectbox(
            "Workflow",
            options=list(workflow_options.keys()),
            format_func=lambda x: workflow_options[x].get('name', x),
            key="sys_info_wf_selector"
        )

        selected_workflow = workflow_options.get(selected_wf_id)

        if selected_workflow:
            st.info(f"Viewing configuration for: **{selected_workflow.get('name')}**")
            st.markdown(f"_{selected_workflow.get('description')}_")
            st.markdown("---")

            # Gather Dependencies
            workflow_steps_ids = selected_workflow.get('steps', [])
            all_steps = {s['id']: s for s in steps_list if 'id' in s}
            all_components = {c['id']: c for c in components_list if 'id' in c}

            relevant_steps = [all_steps[sid] for sid in workflow_steps_ids if sid in all_steps]

            used_component_ids = set()
            for step in relevant_steps:
                prompts = step.get('execution_config', {}).get('llm_prompts', [])
                for p_id in prompts:
                    used_component_ids.add(p_id)

            used_components = [all_components[cid] for cid in used_component_ids if cid in all_components]

            # Ordering
            type_order = ["header", "mandate", "rule", "operational_rule", "protocol", "method", "instruction", "task"]

            def sort_key(c):
                t = c.get('type', '').lower()
                if t in type_order:
                    return type_order.index(t)
                return 99

            used_components.sort(key=sort_key)

            # Tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📚 Komponenttikirjasto", "Workflow Steps", "Prompt Preview", "Full Chain Export", "📘 Methodology"])

            with tab5:
                st.markdown("""
                ### Methodology & Definitions
                
                **1. Workflow Structure**
                A Workflow is a sequence of **Steps**. Each Step is assigned to an **Agent** (e.g., `AnalystAgent`).
                - **Steps**: The granular execution units (e.g., `step_analyst`).
                - **Agents**: The logic class that executes the step.
                - **Components**: The re-usable building blocks of prompts (Rules, Mandates, Instructions).
                
                **2. Anatomy of a Prompt**
                Each Agent's prompt is dynamically assembled from **Components** in the `seed_data.json`.
                - **System Instruction**: Defines the persona (e.g., "You are an expert logician...").
                - **Context**: The input data (History, Product, Reflection).
                - **Mandates & Rules**: Strict constraints the AI must follow.
                - **Task**: The specific question for this step.
                
                **3. Model Strategies (Fast vs Deep)**
                The system allows mapping specific models to steps based on cognitive load.
                - **⚡ Fast (Global Strategy)**: Uses lighter, faster models (e.g., `Gemini-Flash` or `GPT-3.5`). Best for:
                    - Structural parsing
                    - Formatting
                    - Simple fact-checking
                - **🧠 Deep (Global Strategy)**: Uses reasoning-heavy models (e.g., `Gemini-Pro` or `GPT-4`). Best for:
                    - Complex analysis
                    - Critical judgment (JudgeAgent)
                    - Nuanced feedback (CoachAgent)
                    - "Prompt Fusion" panels
                
                **4. Prompt Fusion**
                An optimization technique where multiple sequential steps are merged into a single LLM call ("Panel") to save time and tokens, while maintaining the logic of individual sub-steps.
                """)

            with tab1:
                st.markdown(f"### Komponenttikirjasto (Library) - {len(used_components)} items")
                st.caption("Components used in this workflow's prompts.")

                # Optional Type Filter
                c_types = sorted(list(set(str(c.get('type') or 'unknown') for c in used_components)))
                if c_types:
                    sel_types = st.multiselect("Filter by Type", c_types, default=c_types)
                    filtered_comps = [c for c in used_components if c.get('type') in sel_types]
                else:
                    filtered_comps = used_components

                for comp in filtered_comps:
                    c_type = comp.get('type', 'unknown').upper()
                    c_id = comp.get('id')
                    c_desc = comp.get('description', '')

                    with st.expander(f"[{c_type}] {c_id} - {c_desc}"):
                        st.text_area("Content", comp.get('content'), height=200, key=f"lib_{c_id}")

            with tab2:
                st.markdown("### Workflow Steps")
                if relevant_steps:
                    # Simplify step data for dataframe
                    step_data_simp = []
                    for s in relevant_steps:
                        step_data_simp.append({
                            "ID": s.get('id'),
                            "Name": s.get('name'),
                            "Component": s.get('component'),
                            "Description": s.get('description')
                        })
                    st.dataframe(pd.DataFrame(step_data_simp))
                else:
                    st.info("No steps found.")

            with tab3:
                st.markdown("### Step Prompt Preview")
                step_ids_ordered = [s['id'] for s in relevant_steps]
                step_to_preview = st.selectbox("Select Step", step_ids_ordered, format_func=lambda x: f"{x} ({all_steps.get(x, {}).get('name')})")

                if step_to_preview:
                    preview_data = api_client.get_prompt_preview(step_to_preview)
                    if preview_data:
                        st.markdown(f"**Agent Class:** `{preview_data.get('agent_class')}`")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("#### System Instruction")
                            st.text_area("System", preview_data.get('system_instruction'), height=500, key="prev_sys")
                        with c2:
                            st.markdown("#### User Prompt")
                            st.text_area("User", preview_data.get('user_prompt'), height=500, key="prev_usr")

            with tab4:
                st.markdown("### Full Execution Chain Export")
                if st.button(f"Generate Chain for {selected_workflow.get('name')}"):
                    with st.spinner("Generating..."):
                        full_text = api_client.get_full_chain_preview(selected_wf_id)
                        if full_text:
                            st.text_area("Full Chain Content", full_text, height=600, key="full_chain_txt")
                            st.download_button("Download .md", full_text, file_name=f"{selected_wf_id}_full_chain.md")
                        else:
                            st.error("Failed to generate chain preview.")

    else:
        st.error("Failed to load seed data.")
