import requests
import streamlit as st


def render_org_admin_view(api_url: str):
    """Renders the Organization Admin Dashboard.

    Audience: Organization ADMINs (and ROOT users viewing a specific org).
    Functionality: Manage Tenant Settings, Users, and Billing.

    Args:
        api_url (str): The base URL of the backend API.
    """
    st.header("🏢 Organization Settings")

    # 1. Access Control Logic
    # We verify the role. If not ADMIN/ROOT, we block.
    user = st.session_state.get('user', {}) or {}
    role = user.get('role', 'VIEWER').upper()
    org_id = user.get('organization_id')

    if role not in ['ADMIN', 'ROOT']:
        st.error(f"⛔ Access Denied: You must be an Organization Administrator or Root. (Current Role: {role})")
        return

    if not org_id and role != 'ROOT':
        st.error("Error: No Organization Context found.")
        return

    # Handle ROOT without personal Org
    if role == 'ROOT' and not org_id:
        st.warning("⚠️ You are logged in as ROOT without a bound Organization.")
        st.markdown("To manage organizations globally, use the **🛡️ System Admin** view.")

        st.divider()
        st.markdown("#### 🕵️ Debug: Impersonate Organization")
        target_override = st.text_input("Enter Organization ID to View/Edit manually:")
        if not target_override:
            st.info("Enter an ID above to load that organization's context.")
            return
        else:
            org_id = target_override # Override for subsequent logic

    # For user context, we fetch 'My Organization'
    # If ROOT is here, they usually are viewing their OWN system org, or impersonating.
    # For now, we use the '/organizations/me' endpoint to get the context of the logged in user.

    try:
        # Fetch current org details
        token = st.session_state.get('auth_token')
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        res = requests.get(f"{api_url}/organizations/me", headers=headers)

        # Fallback logic if /me doesn't return (e.g. ROOT viewing specific org)
        if res.status_code != 200 and org_id:
             res = requests.get(f"{api_url}/organizations/{org_id}", headers=headers)

        if res.status_code == 200:
            org_data = res.json()
        else:
            if role == 'ROOT':
                 st.warning(f"⚠️ Could not load organization data for ID: '{org_id}'. (Status: {res.status_code})")
                 st.markdown("The organization might not exist in the database yet.")

                 st.markdown("#### 🕵️ Try Another ID")
                 new_target = st.text_input("New Target Org ID", key="retry_org_id_input")
                 if st.button("Load New Target"):
                      # We can't easily update the outer variable and rerun in one pass without session state logic,
                      # but typical Streamlit flow allows user to hit enter.
                      # Ideally we'd update session_state user but that's risky.
                      # Let's just ask them to use the System Admin view.
                      pass

                 st.info("💡 Tip: Use **System Admin** view to create organizations first.")
                 return
            else:
                 st.error(f"Could not load organization data. Status: {res.status_code}")
                 return

    except Exception as e:
        st.error(f"Connection Error: {e}")
        return

    # --- UI LAYOUT ---

    # Header Info
    c1, c2, c3 = st.columns([2, 1, 1])
    c1.metric("Organization", org_data.get('name', 'Unknown'))
    c2.metric("Tier", org_data.get('tier', 'Standard').upper())
    c3.metric("ID", org_data.get('id'))

    tabs = st.tabs(["⚙️ General Settings", "👥 User Management", "💳 Billing & Usage"])

    # TAB 1: General Settings
    with tabs[0]:
        st.subheader("General Configuration")

        with st.form("edit_org_form"):
            new_name = st.text_input("Display Name", value=org_data.get('name', ''))
            new_email = st.text_input("Contact Email", value=org_data.get('contact_email', ''))

            # Read-only fields
            st.text_input("Organization ID", value=org_data.get('id'), disabled=True, help="Cannot be changed.")
            # Tier selection with fallback
            available_tiers = ["standard", "premium", "enterprise"]
            current_tier = org_data.get('tier', 'standard').lower()

            try:
                tier_index = available_tiers.index(current_tier)
            except ValueError:
                tier_index = 0 # Default to standard if unknown value

            st.selectbox("Tier", available_tiers, index=tier_index, disabled=True, help="Contact Sales to upgrade.")

            if st.form_submit_button("Save Changes"):
                update_payload = {
                    "name": new_name,
                    "contact_email": new_email
                }
                try:
                    # Update endpoint
                    upd_res = requests.put(f"{api_url}/organizations/{org_data['id']}", json=update_payload, headers=headers)
                    if upd_res.status_code == 200:
                        st.success("✅ Settings updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"Update failed: {upd_res.text}")
                except Exception as e:
                    st.error(f"Error saving: {e}")

    # TAB 2: User Management (Placeholder)
    with tabs[1]:
        st.info("User Management module coming soon. (Invite/Remove members)")
        # Future: List users filtering by org_id, show roles.

    # TAB 3: Billing (Placeholder)
    with tabs[2]:
        st.info("Billing & Usage statistics are not enabled for this tier.")
