import streamlit as st
import json
from tinydb import TinyDB, Query
import config
from src.database.initialization import initialize_database
from src.engine.orchestrator import Orchestrator
import src.components.hooks # Ensure hooks are registered

# Initialize DB on startup (idempotent)
initialize_database()

st.set_page_config(page_title="Cognitive Quorum v2", layout="wide")

st.title("Cognitive Quorum v2 - Dynamic Workflow Engine")

# Sidebar: Workflow Selection
st.sidebar.header("Configuration")
try:
    db = TinyDB(config.DB_PATH)
    workflows_table = db.table('workflows')
    workflows = workflows_table.all()
    workflow_options = {wf['id']: wf for wf in workflows}
    
    selected_workflow_id = st.sidebar.selectbox(
        "Select Workflow",
        options=list(workflow_options.keys())
    )
    
    if selected_workflow_id:
        st.sidebar.subheader("Model Mapping")
        wf = workflow_options[selected_workflow_id]
        st.sidebar.json(wf.get('default_model_mapping', {}))

except Exception as e:
    st.error(f"Failed to load workflows from DB: {e}")
    selected_workflow_id = None

# Sidebar: System Status
st.sidebar.markdown("---")
st.sidebar.header("System Status")

def status_icon(check):
    return "✅" if check else "❌"

st.sidebar.write(f"Google Gemini API: {status_icon(config.GOOGLE_API_KEY)}")
st.sidebar.write(f"OpenAI API: {status_icon(config.OPENAI_API_KEY)}")
st.sidebar.write(f"Google Search API: {status_icon(config.GOOGLE_SEARCH_API_KEY)}")

# Main Area: Inputs
st.header("1. Upload Evidence")

col1, col2 = st.columns(2)

with col1:
    prompt_text = st.text_area("Prompt Text", height=150, value="Sample Prompt")
    history_text = st.text_area("History Text", height=150, value="Sample History")

with col2:
    product_text = st.text_area("Product Text", height=150, value="Sample Product")
    reflection_text = st.text_area("Reflection Text", height=150, value="Sample Reflection")

if st.button("Run Assessment"):
    if not selected_workflow_id:
        st.error("Please select a workflow.")
    else:
        with st.spinner("Running Workflow..."):
            initial_inputs = {
                "prompt_text": prompt_text,
                "history_text": history_text,
                "product_text": product_text,
                "reflection_text": reflection_text
            }
            
            try:
                # Direct Orchestrator Call
                orchestrator = Orchestrator()
                result = orchestrator.run_workflow(selected_workflow_id, initial_inputs)
                
                st.success("Workflow Completed!")
                
                st.header("2. Results")
                
                # Display Citations if present
                if 'citations' in result and result['citations']:
                    st.subheader("📚 Citations & Sources")
                    for cit in result['citations']:
                        st.info(f"**{cit.get('source', 'Unknown')}**: {cit.get('explanation', '')}")

                # Display XAI Report
                if 'xai_report' in result:
                    st.subheader("📝 XAI Report")
                    st.markdown(result['xai_report'])
                
                # Raw JSON
                with st.expander("View Raw Output JSON"):
                    st.json(result)

            except Exception as e:
                st.error(f"Execution Error: {e}")
