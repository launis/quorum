"""System Admin View (ROOT)."""
import pandas as pd
import streamlit as st


def render_system_admin_view(api_client):
    """Renders the System Admin Dashboard for ROOT users.
    Focus: Organization Management (Multi-Tenancy).

    Args:
        api_client: The API Client instance.
    """
    st.header("🛡️ System Administration")

    # 0. Security Guard (Frontend Side)
    # The actual API calls will fail if not ROOT, but we should hide UI too.
    user = st.session_state.get("user", {}) or {}
    current_role = user.get("role", "VIEWER").upper()

    if current_role != "ROOT":
        st.error(
            f"⛔ Access Denied: This area is restricted to System Administrators (ROOT). (Current Role: {current_role})"
        )
        return

    tabs = st.tabs(["Organizations", "Global settings", "Audit Logs"])
    token = st.session_state.get("auth_token")

    # --- TAB 1: ORGANIZATION MANAGEMENT ---
    with tabs[0]:
        st.subheader("🏢 Organization Registry")

        # 1. Action Bar
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Refresh List"):
                st.rerun()

        # 2. List Organizations
        try:
            # Replaced requests.get with api_client
            # Note: list_organizations in api.py returns the list directly
            orgs = api_client.list_organizations(token=token)

            if orgs:
                # Convert to DataFrame for nice table
                df = pd.DataFrame(orgs)
                # Reorder columns if possible
                cols = ["id", "name", "tier", "subscription_status", "quota_limit", "contact_email", "created_at"]
                # Filter only existing cols
                cols = [c for c in cols if c in df.columns]

                st.dataframe(
                    df[cols],
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "id": st.column_config.TextColumn("Org ID", help="Unique system identifier"),
                        "name": st.column_config.TextColumn("Display Name"),
                        "tier": st.column_config.SelectboxColumn("Tier", options=["standard", "premium", "enterprise"]),
                        "subscription_status": st.column_config.SelectboxColumn(
                            "Status", options=["active", "past_due", "canceled", "trial"]
                        ),
                        "quota_limit": st.column_config.NumberColumn("Quota"),
                    },
                )
            else:
                st.info("No organizations found or access denied.")

        except Exception as e:
            st.error(f"Connection Error: {e}")

        st.divider()

        # 3. Create New Organization
        st.write("#### ➕ Create New Tenant")
        with st.form("create_org_form"):
            c1, c2 = st.columns(2)
            new_name = c1.text_input("Display Name", placeholder="e.g. Acme Corporation")
            new_email = c2.text_input("Contact Email", placeholder="admin@acme.com")

            c3, c4 = st.columns(2)
            new_tier = c3.selectbox("Service Tier", ["standard", "premium", "enterprise"])
            new_status = c4.selectbox("Subscription Status", ["trial", "active", "past_due", "canceled"])

            c5, c6 = st.columns(2)
            new_quota = c5.number_input("Quota Limit", min_value=100, step=100, value=1000)
            new_billing_id = c6.text_input("Billing ID (e.g. cus_123)", placeholder="Optional")

            if st.form_submit_button("Create Organization"):
                if not new_name:
                    st.error("Display Name is required.")
                else:
                    # Backend handles ID generation now.
                    payload = {
                        "name": new_name,
                        "tier": new_tier,
                        "contact_email": new_email,
                        "subscription_status": new_status,
                        "quota_limit": new_quota,
                        "billing_id": new_billing_id or None,
                    }
                    try:
                        # We don't have create_organization in APIClient yet?
                        # Ideally we add it, but for now fallback to requests?
                        # Wait, list_organizations is there. create_organization is NOT.
                        # I'll use requests just for this one for now to avoid creating too many methods at once,
                        # OR I stick to the plan and add everything.
                        # Given user urgency, I'll use requests but with api_client.base_url
                        import requests

                        headers = {"Authorization": f"Bearer {token}"} if token else {}
                        res = requests.post(f"{api_client.base_url}/organizations/", json=payload, headers=headers)

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
        st.subheader("⚙️ Global System Configuration")
        st.markdown("*These settings affect the entire application for all tenants.*")

        try:
            # Fetch current settings via APIClient
            current_settings = api_client.get_global_settings(token=token)

            if current_settings:
                with st.form("global_settings_form"):
                    col_a, col_b = st.columns(2)

                    with col_a:
                        m_mode = st.checkbox(
                            "Maintenance Mode",
                            value=current_settings.get("maintenance_mode", False),
                            help="Only ROOT admins can login.",
                        )
                        signups = st.checkbox("Allow New Signups", value=current_settings.get("allow_signups", True))
                        beta = st.checkbox(
                            "Enable Beta Features", value=current_settings.get("enable_beta_features", False)
                        )

                    with col_b:
                        # Safety check for index
                        def_strategy = current_settings.get("default_model_strategy", "fast")
                        try:
                            idx = ["fast", "deep", "balanced"].index(def_strategy)
                        except ValueError:
                            idx = 0

                        strategy = st.selectbox("Default AI Strategy", ["fast", "deep", "balanced"], index=idx)
                        banner = st.text_input(
                            "Global Announcement Banner", value=current_settings.get("global_banner") or ""
                        )

                    if st.form_submit_button("💾 Save System Settings"):
                        payload = {
                            "maintenance_mode": m_mode,
                            "allow_signups": signups,
                            "enable_beta_features": beta,
                            "default_model_strategy": strategy,
                            "global_banner": banner if banner.strip() else None,
                        }

                        success = api_client.update_global_settings(payload, token=token)
                        if success:
                            st.success("System settings updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update settings.")
            else:
                st.error("Failed to load settings from backend.")

        except Exception as e:
            st.error(f"Connection Error: {e}")

    # --- TAB 3: AUDIT LOGS ---
    with tabs[2]:
        st.subheader("📜 System Audit Logs")

        # 1. Filters
        with st.form("audit_filter_form"):
            c1, c2, c3, c4 = st.columns(4)
            filter_org = c1.text_input("Filter by Org ID")
            filter_actor = c2.text_input("Filter by Actor UID")
            filter_action = c3.text_input("Filter by Action")
            limit_val = c4.number_input("Limit", min_value=10, max_value=500, value=50)

            submitted = st.form_submit_button("🔍 Search Logs")

        if submitted:
            try:
                params = {"limit": limit_val}
                if filter_org:
                    params["organization_id"] = filter_org
                if filter_actor:
                    params["actor_uid"] = filter_actor
                if filter_action:
                    params["action"] = filter_action

                # Use API Client
                logs = api_client.fetch_system_audit_logs(token=token, filters=params)

                # Store in session state to persist across renders if needed (though Streamlit reruns on interaction)
                st.session_state["audit_results"] = logs

                if not logs:
                    st.warning("No logs found.")

            except Exception as e:
                st.error(f"Connection Error: {e}")

        # 3. Display
        results = st.session_state.get("audit_results", [])
        if results:
            # Convert to DF
            df_logs = pd.DataFrame(results)

            # Reorder
            # Expected fields: id, timestamp, actor_uid, action, organization_id, target_uid, details
            cols = ["timestamp", "action", "actor_uid", "organization_id", "target_uid", "details"]
            existing_cols = [c for c in cols if c in df_logs.columns]

            st.dataframe(
                df_logs[existing_cols],
                width="stretch",
                column_config={
                    "timestamp": st.column_config.DatetimeColumn("Time", format="D.M.YYYY HH:mm:ss"),
                    "details": st.column_config.Column("Details", width="large"),
                },
            )
            st.caption(f"Showing {len(results)} events.")
        else:
            if not submitted:
                st.info("Click 'Search' to view logs.")
