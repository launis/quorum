import pandas as pd
import requests
import streamlit as st

from frontend.api import APIClient
from frontend.components.admin.kb_ingestion import render_kb_ingestion


def render_admin_view(api_client: APIClient, backend_url: str, workflow_options: dict):
    """Renders the Admin / Tooling dashboard.

    Provides access to Knowledge Base ingestion, Agent Registry, Concept Extractor,
    Citation Lookup, and System Maintenance tools.

    Args:
        api_client (APIClient): The API client instance.
        backend_url (str): The base URL of the backend.
        workflow_options (dict): Available workflows for context selection.
    """
    st.header("Admin / Tooling")

    tabs = st.tabs(["Knowledge Base", "Agent Registry", "Concept Extractor", "Citation Lookup", "Maintenance"])

    # --- Tab 1: Knowledge Base Ingestion ---
    with tabs[0]:
        render_kb_ingestion(backend_url)

    # --- Tab 2: Agent Registry ---
    with tabs[1]:
        st.subheader("Agent Registry")
        st.write("---")

        # Workflow Context Selector logic (recreated from ui.py)
        selected_wf_id = None
        # We need a simplified version of get_workflow_map here or pass it in.
        # workflow_options is passed in.

        # Try to sync with session state if simpler
        def_idx = 0
        if (
            "ui_selected_workflow_id" in st.session_state
            and st.session_state["ui_selected_workflow_id"] in workflow_options
        ):
            def_idx = list(workflow_options.keys()).index(st.session_state["ui_selected_workflow_id"])

        if workflow_options:
            selected_wf_id = st.selectbox(
                "Valitse Työnkulku (Select Workflow)",
                options=list(workflow_options.keys()),
                index=def_idx,
                format_func=lambda x: workflow_options[x].get("name", x),
                key="registry_wf_selector",
            )

        try:
            res = requests.get(
                f"{backend_url}/agents", params={"workflow_id": selected_wf_id} if selected_wf_id else None
            )
            if res.status_code == 200:
                agents = res.json()
                if agents:
                    # Convert to minimal DataFrame for overview
                    df_data = []
                    for a in agents:
                        df_data.append(
                            {
                                "Name": a.get("name"),
                                "Model": a.get("model"),
                                "Description": a.get("description", "").split("\n")[0],  # First line only
                            }
                        )
                    st.dataframe(pd.DataFrame(df_data))

                    # Detailed View
                    st.divider()
                    st.markdown("### Agent Details")
                    # Selectbox for details
                    agent_names = [a["name"] for a in agents]
                    sel_agent = st.selectbox("View Schema for Agent:", agent_names)

                    if sel_agent:
                        agent_data = next((a for a in agents if a["name"] == sel_agent), None)
                        if agent_data:
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown("**Output Schema (Response Structure)**")
                                schema_out = agent_data.get("output_schema")
                                if schema_out:
                                    st.json(schema_out)
                                else:
                                    st.caption("No output schema defined.")

                                schema_in = agent_data.get("input_schema")
                                if schema_in:
                                    st.markdown("**Input Schema**")
                                    st.json(schema_in)

                            with c2:
                                st.markdown("**Full Description**")
                                st.markdown(agent_data.get("description"))
                else:
                    st.info("No agents registered yet.")
            else:
                st.error(f"Failed to fetch agents: {res.status_code}")
        except Exception as e:
            st.error(f"Connection Error: {e}")

    # --- Tab 3: Concept Extractor ---
    with tabs[2]:
        st.subheader("LLM Concept Extractor")
        st.markdown("Test the concept extraction logic without saving to DB.")

        ex_text = st.text_area("Paste Text to Extract Concepts From:", height=200)

        if st.button("Extract Concepts"):
            if not ex_text:
                st.warning("Please enter text.")
            else:
                with st.spinner("Analyzing text with LLM..."):
                    try:
                        form_data = {"text": ex_text}
                        res = requests.post(f"{backend_url}/tools/extract-concepts", data=form_data)

                        if res.status_code == 200:
                            result = res.json()
                            concepts = result.get("concepts", [])
                            st.success(f"Found {len(concepts)} concepts!")
                            st.json(concepts)
                        else:
                            st.error(f"Error: {res.text}")
                    except Exception as e:
                        st.error(f"Request failed: {e}")

    # --- Tab 4: Citation Lookup ---
    with tabs[3]:
        st.subheader("Citation Lookup")
        st.markdown("Check if text contains citations known to the Knowledge Base (Coach Logic).")

        cit_text = st.text_area("Paste Text to Check:", height=200)
        if st.button("Check Citations"):
            with st.spinner("Checking..."):
                try:
                    res = requests.post(f"{backend_url}/tools/citation-lookup", json={"text": cit_text})

                    if res.status_code == 200:
                        data = res.json()
                        citations = data.get("citations", [])
                        if citations:
                            st.success(f"Found {len(citations)} citations!")
                            for c in citations:
                                st.markdown(f"- {c}")
                        else:
                            st.info("No citations found.")
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Failed: {e}")

    # --- Tab 5: Maintenance ---
    with tabs[4]:
        st.subheader("System Maintenance")
        if st.button("Run Self-Test"):
            try:
                res = requests.post(f"{backend_url}/admin/self-test")
                st.json(res.json())
            except Exception as e:
                st.error(e)
