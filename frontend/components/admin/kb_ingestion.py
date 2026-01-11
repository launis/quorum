"""Knowledge Base Ingestion Component."""
import time

import requests
import streamlit as st


def render_kb_ingestion(backend_url):
    """Renders the KB Ingestion UI."""
    st.subheader("Knowledge Base Ingestion")
    st.markdown("Upload a DOCX file (e.g., `Holistinen Mestaruus.docx`) to ingest it into the Knowledge Base.")

    uploaded_kb = st.file_uploader("Upload Knowledge Base File", type=["docx", "md"])

    reset_db = st.checkbox(
        "Nollaa tietokanta (Reset Knowledge Base)",
        value=False,
        help="Delete all existing references and concepts before ingesting this file.",
    )

    if uploaded_kb:
        if st.button("Ingest Knowledge Base File"):
            with st.spinner("Ingesting file..."):
                try:
                    files = {
                        "file": (
                            uploaded_kb.name,
                            uploaded_kb.getvalue(),
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        )
                    }
                    res = requests.post(
                        f"{backend_url}/admin/knowledge-base/upload", files=files, params={"reset_db": reset_db}
                    )

                    if res.status_code == 200:
                        data = res.json()
                        job_id = data.get("job_id")
                        st.success(f"Ingestion Started! Job ID: {job_id}")

                        # Polling Loop
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        while True:
                            try:
                                status_res = requests.get(f"{backend_url}/admin/knowledge-base/status/{job_id}")
                                if status_res.status_code == 200:
                                    status = status_res.json()
                                    percent = status.get("percent", 0)
                                    stage = status.get("stage", "Processing...")
                                    state = status.get("status", "unknown")

                                    progress_bar.progress(percent)
                                    status_text.info(f"{state.upper()}: {stage}")

                                    if state in ["completed", "failed"]:
                                        if state == "completed":
                                            st.success("Ingestion Completed Successfully!")
                                            st.json(status.get("result"))
                                        else:
                                            st.error(f"Ingestion Failed: {status.get('error')}")
                                        break
                                else:
                                    status_text.warning("Waiting for status...")

                                time.sleep(1)
                            except Exception as e:
                                st.error(f"Polling error: {e}")
                                break
                    else:
                        st.error(f"Ingestion Failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
