import requests
import streamlit as st

from frontend.api import APIClient


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
    user = st.session_state.get("user", {}) or {}
    role = user.get("role", "VIEWER").upper()
    org_id = user.get("organization_id")

    if role not in ["ADMIN", "ROOT"]:
        st.error(f"⛔ Access Denied: You must be an Organization Administrator or Root. (Current Role: {role})")
        return

    if not org_id and role != "ROOT":
        st.error("Error: No Organization Context found.")
        return

    # Handle ROOT without personal Org
    if role == "ROOT" and not org_id:
        st.warning("⚠️ You are logged in as ROOT without a bound Organization.")
        st.markdown("To manage organizations globally, use the **🛡️ System Admin** view.")

        st.divider()
        st.markdown("#### 🕵️ Debug: Impersonate Organization")
        target_override = st.text_input("Enter Organization ID to View/Edit manually:")
        if not target_override:
            st.info("Enter an ID above to load that organization's context.")
            return
        else:
            org_id = target_override  # Override for subsequent logic

    # For user context, we fetch 'My Organization'
    # If ROOT is here, they usually are viewing their OWN system org, or impersonating.
    # For now, we use the '/organizations/me' endpoint to get the context of the logged in user.

    try:
        # Fetch current org details
        token = st.session_state.get("auth_token")
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        res = requests.get(f"{api_url}/organizations/me", headers=headers)

        # Fallback logic if /me doesn't return (e.g. ROOT viewing specific org)
        if res.status_code != 200 and org_id:
            res = requests.get(f"{api_url}/organizations/{org_id}", headers=headers)

        if res.status_code == 200:
            org_data = res.json()
        else:
            if role == "ROOT":
                st.warning(f"⚠️ Could not load organization data for ID: '{org_id}'. (Status: {res.status_code})")
                st.markdown("The organization might not exist in the database yet.")

                st.markdown("#### 🕵️ Try Another ID")
                st.text_input("New Target Org ID", key="retry_org_id_input")
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
    c1.metric("Organization", org_data.get("name", "Unknown"))
    c2.metric("Tier", org_data.get("tier", "Standard").upper())
    c3.metric("ID", org_data.get("id"))

    tabs = st.tabs(["⚙️ General Settings", "👥 User Management", "💳 Billing & Usage"])

    # TAB 1: General Settings
    with tabs[0]:
        st.subheader("General Configuration")

        with st.form("edit_org_form"):
            new_name = st.text_input("Display Name", value=org_data.get("name", ""))
            new_email = st.text_input("Contact Email", value=org_data.get("contact_email", ""))

            # Read-only fields
            st.text_input("Organization ID", value=org_data.get("id"), disabled=True, help="Cannot be changed.")
            # Tier selection with fallback
            available_tiers = ["standard", "premium", "enterprise"]
            current_tier = org_data.get("tier", "standard").lower()

            try:
                tier_index = available_tiers.index(current_tier)
            except ValueError:
                tier_index = 0  # Default to standard if unknown value

            st.selectbox("Tier", available_tiers, index=tier_index, disabled=True, help="Contact Sales to upgrade.")

            if st.form_submit_button("Save Changes"):
                update_payload = {"name": new_name, "contact_email": new_email}
                try:
                    # Update endpoint
                    upd_res = requests.put(
                        f"{api_url}/organizations/{org_data['id']}", json=update_payload, headers=headers
                    )
                    if upd_res.status_code == 200:
                        st.success("✅ Settings updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"Update failed: {upd_res.text}")
                except Exception as e:
                    st.error(f"Error saving: {e}")

    # TAB 2: User Management
    with tabs[1]:
        st.subheader("👥 User Management")

        # Initialize Client
        client = APIClient(api_url)
        token = st.session_state.get("auth_token")

        # 1. Fetch roles dynamically (Zero Hardcoding)
        available_roles = client.get_available_roles()
        if not available_roles:
            st.error("Could not load roles from backend. Configuring users is disabled.")
            available_roles = []

        # 2. Add User Form
        with st.expander("➕ Add New User", expanded=False):
            with st.form("add_user_form"):
                c_add1, c_add2 = st.columns(2)
                display_name = c_add1.text_input("Display Name")
                email = c_add2.text_input("Email Address")

                # Organization Selector (ROOT Only)
                target_org_id = org_id
                if role == "ROOT":
                    c_add5, c_add6 = st.columns(2)
                    # Fetch Orgs
                    all_orgs = client.list_organizations(token)
                    org_options = {o["name"]: o["id"] for o in all_orgs}

                    # Logic: If we are in "system" view, default to blank or system?
                    # User requested "list of all OTHER organizations".
                    # Let's provide a dropdown. Default to current org.
                    selected_org_name = c_add5.selectbox(
                        "Target Organization",
                        options=list(org_options.keys()),
                        index=list(org_options.values()).index(org_id) if org_id in org_options.values() else 0,
                    )
                    target_org_id = org_options[selected_org_name]

                # Filter out ROOT from selection if not in System Org OR if acting user is not ROOT
                # Dynamic check: If target_org_id is system, allow ROOT.
                can_assign_root = role == "ROOT" and target_org_id == "system"

                c_add3, c_add4 = st.columns(2)

                # STRICT Filtering:
                if can_assign_root:
                    selectable_roles = available_roles  # [ROOT, ADMIN, ...]
                else:
                    selectable_roles = [r for r in available_roles if r != "ROOT"]

                # Enforce valid index to prevent UI errors
                # If ROOT was previously selected but now invalid, Strealit might error or reset.
                # We can't easily control the 'previous' state here without session_state helper,
                # but defining the list correctly usually works.
                user_role = c_add3.selectbox("Role", selectable_roles)

                # Feedback to user if they are confused
                if role == "ROOT" and target_org_id != "system":
                    c_add3.caption("ℹ️ Root role is only available in 'system' organization.")

                password = c_add4.text_input(
                    "Password (Optional)", type="password", help="Leave blank for auto-generated."
                )

                if st.form_submit_button("Create User"):
                    if not email or not display_name:
                        st.error("Display Name and Email are required.")
                    else:
                        payload = {
                            "email": email,
                            "display_name": display_name,
                            "role": user_role,
                            "password": password if password else None,  # Explicit None to satisfy Pydantic Optional
                        }

                        try:
                            # Use target_org_id
                            client.create_organization_user(target_org_id, payload, token)
                            st.success(
                                f"User '{display_name}' created in '{selected_org_name if role == 'ROOT' else 'Organization'}'!"
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to create user: {e}")

        # 3. List Users
        st.markdown("### Existing Users")
        users = client.get_organization_users(org_id, token)

        if not users:
            st.info("No users found in this organization.")
        else:
            # Display as a clean table with actions
            for u in users:
                with st.container(border=True):
                    uc1, uc2, uc3, uc4 = st.columns([2, 3, 2, 2])
                    uc1.markdown(f"**{u.get('display_name')}**")
                    uc2.caption(u.get("email"))
                    uc3.badge(u.get("role", "UNKNOWN"))

                    # Actions
                    if uc4.button("🗑️ Delete", key=f"del_{u['uid']}"):
                        try:
                            client.delete_organization_user(org_id, u["uid"], token)
                            st.success("User deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete failed: {e}")

    # TAB 3: Billing (Placeholder)
    with tabs[2]:
        st.info("Billing & Usage statistics are not enabled for this tier.")
