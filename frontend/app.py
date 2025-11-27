import streamlit as st
import requests
import os

# Configuration
API_URL = os.getenv("API_URL", "http://backend:8000")

st.set_page_config(page_title="Cognitive Quorum", layout="wide")

st.title("🧠 Cognitive Quorum")
st.markdown("### Hybrid Rubric Assessment System")

st.info("Upload the required documents to start the assessment process.")

with st.form("upload_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        prompt_file = st.file_uploader("Assessment Prompt (Pääarviointikehote)", type=["pdf"])
        history_file = st.file_uploader("Conversation History (Keskusteluhistoria)", type=["pdf"])
        
    with col2:
        product_file = st.file_uploader("Final Product (Lopputuote)", type=["pdf"])
        reflection_file = st.file_uploader("Reflection (Reflektio)", type=["pdf"])
        
    submitted = st.form_submit_button("Start Assessment")
    
    if submitted:
        if prompt_file and history_file and product_file and reflection_file:
            with st.spinner("Uploading files..."):
                try:
                    files = [
                        ('prompt_file', (prompt_file.name, prompt_file, prompt_file.type)),
                        ('history_file', (history_file.name, history_file, history_file.type)),
                        ('product_file', (product_file.name, product_file, product_file.type)),
                        ('reflection_file', (reflection_file.name, reflection_file, reflection_file.type))
                    ]
                    
                    response = requests.post(f"{API_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Files uploaded successfully!")
                        st.json(data)
                    else:
                        st.error(f"Upload failed: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
        else:
            st.warning("Please upload all 4 required files.")

st.divider()

st.subheader("System Health Check (E2E Hello World)")
with st.expander("Test Database Connection"):
    greeting_input = st.text_input("Enter a greeting:")
    if st.button("Send Greeting"):
        if greeting_input:
            try:
                res = requests.post(f"{API_URL}/greet", json={"message": greeting_input})
                if res.status_code == 200:
                    st.success(f"Sent: {greeting_input}")
                else:
                    st.error(f"Error sending: {res.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

    if st.button("Fetch Latest Greeting"):
        try:
            res = requests.get(f"{API_URL}/greet")
            if res.status_code == 200:
                data = res.json()
                st.info(f"Latest Greeting from DB: {data.get('message')}")
            else:
                st.error(f"Error fetching: {res.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")

st.divider()
st.caption("Cognitive Quorum v0.1.0")
