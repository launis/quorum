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
                    st.success(f"User created details: {res.get('email')} ({res.get('role')})")
                    st.balloons()
                    # No rerun immediately to let user see success message, or rerun with delay?
                    # Streamlit rerun is instant.
                    # st.rerun()
                except Exception as e:
                    st.error(f"Failed to create user: {e}")
