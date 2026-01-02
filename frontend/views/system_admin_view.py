import streamlit as st
import requests
import pandas as pd

def render_system_admin_view(api_url: str):
    """
    Renders the System Admin Dashboard for ROOT users.
    Focus: Organization Management (Multi-Tenancy).
    """
    st.header("🛡️ System Administration")
    
    # 0. Security Guard (Frontend Side)
    # The actual API calls will fail if not ROOT, but we should hide UI too.
    user = st.session_state.get('user', {}) or {}
    current_role = user.get('role', 'VIEWER').upper()
    
    if current_role != 'ROOT':
        st.error(f"⛔ Access Denied: This area is restricted to System Administrators (ROOT). (Current Role: {current_role})")
        return

    tabs = st.tabs(["Organizations", "Global settings", "Audit Logs"])
    
    # --- TAB 1: ORGANIZATION MANAGEMENT ---
    with tabs[0]:
        st.subheader("🏢 Organization Registry")
        
        # 1. Action Bar
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Refresh List"):
                st.rerun()

        # 2. List Organizations
        # 2. List Organizations
        try:
            token = st.session_state.get('auth_token')
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            
            resp = requests.get(f"{api_url}/organizations/", headers=headers)
            
            if resp.status_code == 200:
                orgs = resp.json()
                
                if orgs:
                    # Convert to DataFrame for nice table
                    df = pd.DataFrame(orgs)
                    # Reorder columns if possible
                    cols = ['id', 'name', 'tier', 'contact_email', 'created_at']
                    # Filter only existing cols
                    cols = [c for c in cols if c in df.columns]
                    
                    st.dataframe(
                        df[cols], 
                        use_container_width=True, 
                        hide_index=True,
                        column_config={
                            "id": st.column_config.TextColumn("Org ID", help="Unique system identifier"),
                            "name": st.column_config.TextColumn("Display Name"),
                            "tier": st.column_config.SelectboxColumn("Tier", options=["standard", "premium", "enterprise"]),
                        }
                    )
                else:
                    st.info("No organizations found. System is empty.")
                    
            elif resp.status_code == 403:
                st.error("Unauthorized: You do not have ROOT privileges.")
            else:
                st.error(f"Failed to fetch organizations. Status: {resp.status_code}")
                
        except Exception as e:
            st.error(f"Connection Error: {e}")

        st.divider()
        
        # 3. Create New Organization
        st.write("#### ➕ Create New Tenant")
        with st.form("create_org_form"):
            c1, c2 = st.columns(2)
            new_name = c1.text_input("Display Name", placeholder="e.g. Acme Corporation")
            new_email = c2.text_input("Contact Email", placeholder="admin@acme.com")
            
            new_tier = st.selectbox("Service Tier", ["standard", "premium", "enterprise"])
            
            if st.form_submit_button("Create Organization"):
                if not new_name:
                    st.error("Display Name is required.")
                else:

                    # Backend handles ID generation now.
                    payload = {
                        # "id": auto-generated-in-backend,
                        "name": new_name,
                        "tier": new_tier,
                        "contact_email": new_email
                    }
                    try:
                        token = st.session_state.get('auth_token')
                        headers = {"Authorization": f"Bearer {token}"} if token else {}
                        
                        res = requests.post(f"{api_url}/organizations/", json=payload, headers=headers)
                        if res.status_code == 201:
                            st.success(f"Organization '{new_name}' created successfully!")
                            st.rerun()
                        elif res.status_code == 409:
                            st.error("Organization ID already exists.")
                        else:
                            st.error(f"Error: {res.text}")
                    except Exception as e:
                        st.error(f"Connection Failed: {e}")

    # --- TAB 2: GLOBAL SETTINGS ---
    with tabs[1]:
        st.info("Global System Settings (e.g., Default LLM provider, Global Banned Phrases) will be managed here.")
        
    # --- TAB 3: AUDIT LOGS ---
    with tabs[2]:
        st.info("System-wide Audit Logs (Cross-Tenant) will appear here.")
