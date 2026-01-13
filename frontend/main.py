"""Frontend Entrypoint (Streamlit)."""

import os
import sys

import streamlit as st

# Add project root to path to allow absolute imports (e.g. from frontend.utils...)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Utils
# ruff: noqa: E402
from frontend.api import APIClient
from frontend.utils.session_manager import init_session_state
from frontend.views.admin_view import render_admin_view

# Views
from frontend.views.audit_view import render_audit_view
from frontend.views.builder_view import render_workflow_builder
from frontend.views.config_view import render_config_view
from frontend.views.dashboard_view import render_dashboard  # New View
from frontend.views.matrix_view import render_matrix_view
from frontend.views.org_admin_view import render_org_admin_view
from frontend.views.profile_view import render_profile_view
from frontend.views.system_admin_view import render_system_admin_view
from frontend.views.system_view import render_system_view
from frontend.views.user_view import render_user_view

# Config
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
api_client = APIClient(BACKEND_URL)


def get_workflow_map(token=None):
    """Fetches workflows and returns a mapping of ID to Workflow Data."""
    try:
        wfs = api_client.get_workflows(token=token)
        return {w["id"]: w for w in wfs} if wfs else {}
    except Exception:
        return {}


def render_login_screen():
    """Renders the Dev/Mock Login Screen for Streamlit."""
    st.markdown("## 🔐 Admin Console Login")
    st.info("Cognitive Quorum Hybrid Auth. Use Dev Tokens for local development.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Dev / Root Access")
        if st.button("⚡ Impersonate ROOT", type="primary"):
            _perform_login("mock-token:root_master")

        st.markdown("---")
        st.subheader("Manual Token")
        token_input = st.text_input("Firebase ID Token / Mock Token", type="password")
        if st.button("Login with Token"):
            _perform_login(token_input)

    with col2:
        st.subheader("Role Simulation")
        if st.button("👥 Impersonate VIEWER"):
            _perform_login("mock-token:viewer_1")
        if st.button("👤 Impersonate MANAGER"):
            _perform_login("mock-token:manager_1")
        if st.button("🔧 Impersonate ADMIN"):
            _perform_login("mock-token:admin_1")
        if st.button("🧪 Impersonate MEMBER"):
            _perform_login("mock-token:member_1")


@st.cache_resource
def _print_mock_banner_once():
    """Prints a startup banner to the console only once."""
    print("\n" + "=" * 60)
    print(" 🖥️  COGNITIVE QUORUM UI v2.2 - FRONTEND STATUS")
    print("=" * 60)
    print(f" 🔗  BACKEND:     {BACKEND_URL}")
    print(" 🔑  AUTH SYSTEM: Active (Dev Tokens Enabled)")
    print("=" * 60 + "\n")
    return True


def _perform_login(token):
    user = api_client.login_with_token(token)
    if user:
        st.success(f"Welcome, {user['display_name']}!")
        st.session_state.user = user
        st.session_state.auth_token = token
        st.rerun()
    else:
        st.error("Login Failed. Backend refused token.")


def main():
    """Main Streamlit Application Entrypoint."""
    st.set_page_config(page_title="Cognitive Quorum v2", layout="wide")

    # Init State
    init_session_state()

    # Print Console Banner (Once)
    _print_mock_banner_once()

    # --- AUTHENTICATION CHECK ---
    if "user" not in st.session_state:
        st.session_state.user = None

    if not st.session_state.user:
        render_login_screen()
        return
    # ----------------------------

    st.title("Cognitive Quorum v2 - Admin Console")
    st.markdown(
        f"**Backend:** `{BACKEND_URL}` | "
        f"**User:** `{st.session_state.user['display_name']} ({st.session_state.user['role']})`"
    )

    # Sidebar
    with st.sidebar:
        st.title("🧠 Cognitive Quorum")
        st.caption(f"v2.2 Admin | {st.session_state.user['role'].upper()}")
        st.divider()

        st.markdown("### Navigation")
        # Filter views
        nav_options = ["Dashboard", "Assessment", "My Profile"]  # Everyone sees Profile

        user_role = st.session_state.user["role"].lower()  # normalize

        # ROOT: Everything
        if user_role == "root":
            nav_options.extend(
                [
                    "Workflow Builder",
                    "Global Config",
                    "Audit Matrix Library",
                    "User Management",
                    "System Info",
                    "🛡️ System Admin",
                    "🏢 Organization Settings",
                ]
            )

        # ADMIN: Users + Workflows (Inherited from Manager)
        elif user_role == "admin":
            nav_options.extend(
                [
                    "Workflow Builder",  # Inherited
                    "Audit Matrix Library",  # Inherited
                    "User Management",
                    "🏢 Organization Settings",
                ]
            )

        # MANAGER: Workflow Config - Technical Lead
        elif user_role == "manager":
            nav_options.extend(["Workflow Builder", "Global Config", "Audit Matrix Library"])

        # MEMBER & VIEWER: Assessment Only (Default)

        page = st.radio("Go to", nav_options, label_visibility="collapsed")

        st.divider()
        if st.button("Logout"):
            # Clear all session state to prevent data bleeding between users
            st.session_state.clear()
            st.rerun()

        st.caption(f"Session: `{st.session_state.get('session_id', '???')[:8]}...`")

    # Fetch Data with Token
    workflow_options = get_workflow_map(token=st.session_state.get("auth_token"))

    # Routing
    if page == "Dashboard":
        render_dashboard(api_client)
    elif page == "Assessment":
        # Pass backend_url if needed by view, though we are moving away from it.
        render_audit_view(api_client, BACKEND_URL, workflow_options)

    elif page == "My Profile":
        render_profile_view(api_client)

    elif page == "Workflow Builder":
        render_workflow_builder(api_client)

    elif page == "Global Config":
        render_config_view(api_client, BACKEND_URL)

    elif page == "Audit Matrix Library":
        render_matrix_view(api_client, BACKEND_URL)

    elif page == "User Management":
        render_user_view(api_client)

    elif page == "Admin":  # Legacy, maybe merge into Global Config or System Info?
        render_admin_view(api_client, BACKEND_URL, workflow_options)

    elif page == "System Info":
        render_system_view(api_client)

    elif page == "🛡️ System Admin":
        render_system_admin_view(api_client)

    elif page == "🏢 Organization Settings":
        render_org_admin_view(BACKEND_URL)


if __name__ == "__main__":
    main()
