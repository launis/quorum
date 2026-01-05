import pandas as pd
import streamlit as st

from frontend.api import APIClient


def render_user_view(api_client: APIClient):
    """Renders the User Management (Team) view.

    Allows listing and creating users within the authenticated organization.

    Args:
        api_client (APIClient): The API client instance.
    """
    st.header("👥 User Management (Team)")

    user = st.session_state.get("user")
    token = st.session_state.get("auth_token")

    if not user or not token:
        st.error("Access Denied")
        return

    user_role = user.get("role", "").upper()
    user_org = user.get("organization_id", "UNKNOWN")

    st.caption(f"Managing Users for Organization: **{user_org}**")

    # 1. Fetch Users
    try:
        users_list = api_client.list_users(token)
    except Exception as e:
        st.error(f"Failed to fetch users: {e}")
        users_list = []

    # 2. Display Users
    st.markdown("### Existing Team Members")
    if users_list:
        df = pd.DataFrame(users_list)
        # Select clean columns
        display_cols = ["display_name", "email", "role", "uid", "created_by", "created_at"]
        # Filter to only cols that exist
        cols = [c for c in display_cols if c in df.columns]

        # Format timestamps nicely if possible, else raw
        st.dataframe(df[cols], hide_index=True)
    else:
        st.info("No users found in this organization.")

    st.markdown("---")

    # 3. Create User Form (Permissions Check)
    # Rules:
    # ROOT -> Can create ROOT
    # ADMIN -> Can create ADMIN, MANAGER, MEMBER, VIEWER
    # MANAGER -> Read Only
    # MEMBER/VIEWER -> Access Denied (Should not be seeing this view)

    allowed_roles = []

    if user_role == "ROOT":
        allowed_roles = ["ROOT"]
        st.info("💡 As ROOT, you are managing System Administrators. To manage Tenants, go to 'Organizations'.")

    elif user_role == "ADMIN":
        allowed_roles = ["ADMIN", "MANAGER", "MEMBER", "VIEWER"]

    elif user_role == "MANAGER":
        st.warning("Managers provide technical leadership but do not manage user accounts. Contact an Admin to add users.")
        return

    if not allowed_roles:
        return

    st.markdown("### Invite New Member")

    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_email = st.text_input("Email Address")
            new_name = st.text_input("Display Name")
        with col2:
            new_role = st.selectbox("Assign Role", allowed_roles)
            new_password = st.text_input("Temporary Password", type="password")

        st.caption("New users will be created in your organization.")
        submit = st.form_submit_button("Create User")

        if submit:
            if not new_email or not new_password:
                st.error("Email and Password are required.")
            else:
                payload = {
                    "email": new_email,
                    "password": new_password,
                    "display_name": new_name,
                    "role": new_role
                }
                try:
                    res = api_client.create_user(token, payload)
                    st.success(f"User created: {res.get('email')}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create user: {e}")

    st.markdown("---")
    st.markdown("### Manage Members")

    if not users_list:
        return

    # User Selection Logic
    # Map UID -> Display String
    user_map = {u['uid']: f"{u.get('display_name', 'Unknown')} ({u.get('email')}) - {u.get('role')}" for u in users_list}
    
    # Filter out self (optional, but usually good to avoid deleting self)
    # But allowing self-update might be okay. Let's keep it simple.
    
    selected_uid = st.selectbox("Select User to Manage", options=list(user_map.keys()), format_func=lambda x: user_map[x])

    if selected_uid:
        target_user = next((u for u in users_list if u['uid'] == selected_uid), None)
        if not target_user:
            st.error("User not found.")
            return

        st.info(f"Managing: **{target_user.get('display_name')}** ({target_user.get('role')})")

        # 1. Edit User Form
        with st.expander("📝 Edit Details", expanded=False):
            with st.form(key=f"edit_form_{selected_uid}"):
                new_role_edit = st.selectbox("Role", allowed_roles, index=allowed_roles.index(target_user.get('role')) if target_user.get('role') in allowed_roles else 0)
                new_name_edit = st.text_input("Display Name", value=target_user.get('display_name', ''))
                
                if st.form_submit_button("Update User"):
                     payload = {"role": new_role_edit, "display_name": new_name_edit}
                     try:
                         api_client.update_user(token, selected_uid, payload)
                         st.success("User updated!")
                         st.rerun()
                     except Exception as e:
                         st.error(f"Update failed: {e}")

        # 2. Administrative Actions
        col_actions_1, col_actions_2 = st.columns(2)

        # Impersonate (ROOT ONLY)
        if user_role == "ROOT":
            with col_actions_1:
                if st.button("🎭 Impersonate", key=f"imp_{selected_uid}", help="Switch to this user's view"):
                    try:
                        imp_token = api_client.impersonate_user(token, selected_uid)
                        if imp_token:
                            # Set session state
                            st.session_state["auth_token"] = imp_token
                            # We need to refresh the 'user' object in session state too, 
                            # usually main.py handles this on rerun if we clear 'user' or just rerun.
                            # Best practice: Clear 'user' so main.py refetches it.
                            st.session_state["user"] = None 
                            st.success(f"Impersonating {target_user.get('email')}...")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Impersonation failed: {e}")

        # Delete User
        with col_actions_2:
            if st.button("🗑️ Delete User", key=f"del_{selected_uid}", type="primary"):
                # Confirmation? Streamlit buttons are instant. 
                # For safety, maybe a checkbox "Confirm Delete" first? 
                # Or use a separate popover in newer Streamlit, but here let's stick to basic.
                pass 
            
            # Since standard button doesn't have confirmation dialog easily, we use a session state trick or just a simple "Confirm" action
            # Let's add a checkbox for safety in the same column
            confirm_del = st.checkbox("Confirm Deletion", key=f"confirm_del_{selected_uid}")
            if confirm_del and st.button("⚠️ CONFIRM DELETE", key=f"real_del_{selected_uid}", type="primary"):
                 try:
                     api_client.delete_user(token, selected_uid)
                     st.success("User deleted.")
                     st.rerun()
                 except Exception as e:
                     st.error(f"Delete failed: {e}")
