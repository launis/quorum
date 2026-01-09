import pandas as pd
import streamlit as st


def render_dashboard(api_client):
    """Renders the main dashboard metrics and activity.

    Args:
        api_client: The API client instance.
    """
    st.header("Dashboard")

    # Get User Context
    user = st.session_state.user
    role = user["role"]

    st.caption(f"Welcome back, **{user.get('display_name', 'User')}**! ({role})")

    # --- Quick Metrics (Mock Data for now, connect to API later) ---
    # In a real scenario, we would have `api_client.get_stats()`

    col1, col2, col3 = st.columns(3)

    if role in ["ROOT", "ADMIN"]:
        with col1:
            st.metric("Total Users", "42", "+2")
        with col2:
            st.metric("Workflows Run (Today)", "15", "+5")
        with col3:
            st.metric("System Health", "98%", "Stable")

        st.divider()
        st.subheader("System Activity")
        # Placeholder chart using native Streamlit
        df = pd.DataFrame({"Day": ["Mon", "Tue", "Wed", "Thu", "Fri"], "Executions": [10, 15, 8, 22, 18]})
        st.bar_chart(df.set_index("Day"))

    elif role in ["MANAGER", "MEMBER"]:
        # Fetch actual recent runs for the user/org
        recent_runs = api_client.get_recent_runs(limit=5, token=st.session_state.auth_token)

        with col1:
            st.metric("My Audits (Total)", len(recent_runs) if recent_runs else 0)
        with col2:
            # Calculate average score if possible
            st.metric("Avg Score", "8.4", "+0.2")

        st.divider()
        st.subheader("Recent Audits")

        if recent_runs:
            for run in recent_runs:
                with st.container(border=True):
                    scol1, scol2, scol3 = st.columns([2, 1, 1])
                    with scol1:
                        st.write(f"**{run.get('workflow_id', 'Unknown Workflow')}**")
                        st.caption(f"ID: {run.get('id')}")
                    with scol2:
                        ts = run.get("created_at")
                        # Format timestamp logic here
                        st.write(ts)
                    with scol3:
                        status = run.get("status", "unknown")
                        if status == "COMPLETED":
                            st.success(status)
                        else:
                            st.info(status)

            if st.button("View All History"):
                # Ideally switch tab, but Streamlit nav is tricky.
                st.info("Go to 'Assessment' tab for full history.")
        else:
            st.info("No recent audits found. Start one in the Assessment tab!")

    else:  # VIEWER
        st.info("Welcome to the Viewer Portal. Please navigate to 'Assessment' to view reports.")
