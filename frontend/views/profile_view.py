"""User Profile View (Self-Service)."""

import streamlit as st
from frontend.api import APIClient

def render_profile_view(api_client: APIClient):
    """Renders the current user's profile settings."""
    st.header("👤 My Profile")

    user = st.session_state.get("user")
    token = st.session_state.get("auth_token")

    if not user or not token:
        st.error("Session expired.")
        return

    st.info(f"Logged in as: **{user.get('email')}**")
    
    # Read-only fields
    c1, c2 = st.columns(2)
    with c1:
        st.caption("User ID")
        st.code(user.get("uid"))
        st.caption("Role")
        st.code(user.get("role"))
    with c2:
        st.caption("Organization ID")
        st.code(user.get("organization_id"))
        st.caption("Account Created")
        st.text(user.get("created_at", "Unknown"))

    st.divider()

    # Editable Fields
    st.subheader("Edit Details")
    
    with st.form("profile_edit_form"):
        new_name = st.text_input("Display Name", value=user.get("display_name", ""))
        
        # In future: Password change could go here
        
        if st.form_submit_button("Save Changes"):
            payload = {"display_name": new_name}
            try:
                # Update Self
                updated_user = api_client.update_user(token, user["uid"], payload)
                
                # Update Session State
                st.session_state.user = updated_user
                st.success("Profile updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to update profile: {e}")
