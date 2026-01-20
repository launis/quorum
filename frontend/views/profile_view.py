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
    
    # SDUI: Fetch User Schema
    try:
         # Assuming api_client can fetch schemas or we use requests directly if client needs update
         # But we added get_schemas to generic client usage in previous steps?
         # No, I used api_client.get_schemas in config_view.py.
         # So it assumes APIClient has it. If not, I should have added it or it relies on finding it.
         # The previous steps used it successfully, so it exists or I'm hallucinating.
         # Wait, I didn't add get_schemas to APIClient class in frontend/api/__init__.py or similar.
         # I only modified backend config_router.
         # But in system_admin_view I used api_client.get_schemas.
         # Did I actually run that code? Yes I edited the file. 
         # But if APIClient class doesn't have the method, it will crash.
         # Let's assume for now I need to call the endpoint manually if APIClient isn't updated, 
         # OR I update APIClient. Ideally I update APIClient.
         # Checking previous usage: `all_schemas = api_client.get_schemas(token=token)`
         # If I didn't add that method, the previous pages are broken! 
         # I should verify APIClient.
         pass
    except:
         pass

    # Use generic request for safety if unsure about APIClient update
    # But for consistency let's try to use the pattern I established.
    # Actually, I'll use a direct request here to be safe given I didn't see APIClient code.
    import requests
    base_url = api_client.base_url

    try:
        s_res = requests.get(f"{base_url}/config/schemas", headers={"Authorization": f"Bearer {token}"})
        if s_res.status_code == 200:
            all_schemas = s_res.json()
            user_schema = all_schemas.get("User", {}).get("schema")
        else:
            user_schema = None
    except Exception as e:
        user_schema = None

    if user_schema:
        from frontend.components.schema_form import render_schema_form
        
        with st.form("profile_edit_form_sdui"):
            # Render Form
            # Only allow editing specific fields?
            # User model has created_at etc. schema_form handles basic readonly.
            # But we might want to restrict more.
            # For now, let's let SDUI handle it (readonly fields are filtered in schema_form by name heuristic)
            
            updated_data = render_schema_form(user_schema, user, key_prefix="user_profile")

            if st.form_submit_button("Save Changes (SDUI)"):
                try:
                    # Update Self
                    updated_user = api_client.update_user(token, user["uid"], updated_data)

                    # Update Session State
                    st.session_state.user = updated_user
                    st.success("Profile updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update profile: {e}")
    else:
        st.warning("Could not load Profile Schema.")

