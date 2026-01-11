"""Audit View Module."""

import streamlit as st

from frontend.api import APIClient
from frontend.components.audit.controls import render_controls
from frontend.components.audit.inputs import render_file_inputs
from frontend.components.audit.status import render_execution_status
from frontend.components.results.renderer import render_dashboard


def render_audit_view(api_client: APIClient, backend_url: str, workflow_options: dict):
    """Renders the main Audit View.

    Handling workflow selection, file inputs, execution controls, and history browsing.

    Args:
        api_client (APIClient): The API client instance.
        backend_url (str): The base URL of the backend.
        workflow_options (dict): Available workflows for selection.
    """
    # 1. Workflow Selection
    st.sidebar.header("Configuration")
    selected_workflow_id = None

    if workflow_options:
        selected_workflow_id = st.sidebar.selectbox(
            "Valitse Työnkulku (Select Workflow)",
            options=list(workflow_options.keys()),
            format_func=lambda x: workflow_options[x].get("name", x),
            key="ui_selected_workflow_id",
        )
        # Show Model Mapping snippet (simplified from original ui.py)
        if selected_workflow_id:
            st.sidebar.subheader("Model Mapping")
            wf = workflow_options[selected_workflow_id]
            mapping = wf.get("default_model_mapping", {})
            if mapping:
                for step, model in mapping.items():
                    st.sidebar.caption(f"**{step}**: `{model}`")
    else:
        st.sidebar.warning("No workflows found.")

    # 2. Inputs
    uploaded_files = render_file_inputs()

    # 3. Controls
    render_controls(api_client, selected_workflow_id, uploaded_files)

    # 4. Progress / Status
    job_id = st.session_state.get("active_job_id")
    if job_id:
        render_execution_status(api_client, job_id, selected_workflow_id, workflow_options, backend_url)

    # 5. History / Recent Runs
    st.subheader("Historia")
    with st.expander("Selaa aiempia ajoja", expanded=False):
        if st.button("Hae viimeiset 5 ajoa"):
            token = st.session_state.get("auth_token")
            runs = api_client.get_recent_runs(token=token)
            if runs:
                st.session_state["recent_runs"] = runs
            else:
                st.warning("Ei ajoja löytynyt tai yhteysvirhe.")

        if "recent_runs" in st.session_state and st.session_state["recent_runs"]:
            runs = st.session_state["recent_runs"]
            # Sort generic dict safely
            run_options = {f"{r.get('start_time', 'N/A')} - {r.get('status')}": r for r in runs}
            selected_label = st.selectbox("Valitse ajo:", options=list(run_options.keys()))

            if st.button("Lataa valittu tulos"):
                selected_run = run_options[selected_label]
                if selected_run.get("status") == "completed":
                    if "result" in selected_run:
                        st.success(f"Ladattu ajo: {selected_run.get('execution_id')}")
                        render_dashboard(selected_run["result"])
                    else:
                        st.warning("Valitussa ajossa ei ole tulosta.")
                else:
                    st.warning(f"Valittu ajo on tilassa: {selected_run.get('status')}")
                    st.json(selected_run)
