"""Audit Status Component."""

import time

import requests
import streamlit as st

from frontend.components.results.renderer import render_dashboard


def render_execution_status(api_client, job_id, workflow_id, workflow_options, backend_url):
    """Renders the progress bar and status text.

    Polls the backend until completion or failure.
    """
    st.divider()
    st.subheader(f"Execution Status: {job_id}")

    dynamic_steps_order = []
    if workflow_id:
        dynamic_steps_order = api_client.get_workflow_steps(workflow_id, workflow_options)

    progress_bar = st.progress(0)
    status_text = st.empty()
    result_container = st.container()

    while True:
        status_data = api_client.get_execution_status(job_id)
        if not status_data:
            time.sleep(2)
            continue

        status = status_data.get("status")
        current_step = status_data.get("current_step")
        pct = status_data.get("progress")

        # Update Progress Bar
        if pct is not None:
            progress_bar.progress(min(pct / 100.0, 1.0))
            if current_step:
                status_text.info(f"{current_step}")
            else:
                status_text.info(f"Status: {status} ({pct}%)")
        elif current_step and dynamic_steps_order and current_step in dynamic_steps_order:
            idx = dynamic_steps_order.index(current_step)
            progress = (idx + 1) / len(dynamic_steps_order)
            progress_bar.progress(min(progress, 0.95))
            status_text.info(f"Vaihe {idx + 1}/{len(dynamic_steps_order)}: {current_step} käynnissä...")
        else:
            progress_bar.progress(0.1)
            if current_step:
                status_text.info(f"{current_step}")
            else:
                status_text.info(f"Status: {status} ...")

        # Handle Terminal States
        if status.upper() == "COMPLETED":
            progress_bar.progress(100)
            status_text.success("Assessment Completed!")
            result = status_data.get("result", {})
            with result_container:
                render_dashboard(result)

            if st.button("Start New Assessment"):
                del st.session_state["active_job_id"]
                st.rerun()
            break

        elif status.upper() == "FAILED":
            status_text.error(f"Job Failed: {status_data.get('error')}")
            render_failure_controls(job_id, backend_url)
            break

        elif status.upper() == "REJECTED":
            status_text.error(f"⚠️ Security Intervention (Rejected): {status_data.get('error')}")
            if "result" in status_data:
                with st.expander("Details"):
                    st.json(status_data["result"])
            if st.button("Acknowledge & Clear"):
                del st.session_state["active_job_id"]
                st.rerun()
            break

        time.sleep(2)


def render_failure_controls(job_id, backend_url):
    """Render controls for handling failed jobs (Retry/Cancel)."""
    col_retry, col_clear = st.columns(2)
    with col_retry:
        if st.button("🔄 Retry / Resume (From last success)"):
            try:
                res = requests.post(f"{backend_url}/workflows/executions/{job_id}/retry")
                if res.status_code == 200:
                    st.success("Resuming...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Retry failed: {res.text}")
            except Exception as e:
                st.error(f"Retry Error: {e}")
    with col_clear:
        if st.button("Cancel & Clear"):
            del st.session_state["active_job_id"]
            st.rerun()
