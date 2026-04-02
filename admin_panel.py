# admin_panel.py
"""
Admin Panel — accessible only when role == "admin".
Shows:  User list · Activity log · Per-user prediction count · Model Insights link
"""
import streamlit as st
import pandas as pd
import os
import json
from database import get_connection


# ─────────────────────────────────────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _all_users():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id, username, role FROM users ORDER BY id", conn
    )
    conn.close()
    return df


def _activity_log(limit=200):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT username, action, detail, timestamp "
        "FROM activity_log ORDER BY id DESC LIMIT ?",
        conn, params=(limit,)
    )
    conn.close()
    return df


def _prediction_counts():
    """Read health_progress/ to count saved predictions per user."""
    progress_dir = "health_progress"
    counts = {}
    if os.path.exists(progress_dir):
        for fname in os.listdir(progress_dir):
            if fname.endswith(".json"):
                uname = fname.replace(".json", "")
                try:
                    with open(os.path.join(progress_dir, fname)) as f:
                        records = json.load(f)
                    counts[uname] = len(records)
                except Exception:
                    counts[uname] = 0
    return counts


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def show_admin_panel():
    st.markdown("## 🛡️ Admin Panel")

    # ── Summary metrics ───────────────────────────────────────────────────
    users_df = _all_users()
    log_df   = _activity_log()
    pred_map = _prediction_counts()

    total_users   = len(users_df)
    total_actions = len(log_df)
    total_preds   = sum(pred_map.values())

    # Count unique users who logged in today
    today_str = pd.Timestamp.now().strftime("%Y-%m-%d")
    logins_today = (
        log_df[
            (log_df["action"] == "Login") &
            (log_df["timestamp"].str.startswith(today_str))
        ]["username"].nunique()
        if not log_df.empty else 0
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👤 Total Users",       total_users)
    m2.metric("🔑 Logins Today",      logins_today)
    m3.metric("🩺 Total Predictions", total_preds)
    m4.metric("📋 Total Actions",     total_actions)

    st.markdown("<hr style='border-color:#e2e8f0;margin:1rem 0;'>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "📁 User Management",
        "📊 Activity Log",
        "🩺 Prediction Usage",
    ])

    # ── Tab 1 : User list ─────────────────────────────────────────────────
    with tab1:
        st.markdown("### Registered Users")

        # Merge prediction counts
        users_df["predictions"] = users_df["username"].map(pred_map).fillna(0).astype(int)

        st.dataframe(
            users_df.rename(columns={
                "id": "ID", "username": "Username",
                "role": "Role", "predictions": "Predictions Saved"
            }),
            hide_index=True,
            use_container_width=True,
        )

        st.caption(f"Total registered users: **{total_users}**")

        # Role management
        st.markdown("#### ✏️ Change User Role")
        non_admin = users_df[users_df["role"] != "admin"]["username"].tolist()
        if non_admin:
            col_u, col_r, col_btn = st.columns([2, 2, 1])
            with col_u:
                sel_user = st.selectbox("Select user", non_admin, key="admin_role_user")
            with col_r:
                new_role = st.selectbox("New role", ["user", "admin"], key="admin_role_val")
            with col_btn:
                st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
                if st.button("Update", key="admin_role_btn"):
                    try:
                        conn = get_connection()
                        conn.execute(
                            "UPDATE users SET role=? WHERE username=?",
                            (new_role, sel_user)
                        )
                        conn.commit()
                        conn.close()
                        st.success(f"✅ {sel_user} → {new_role}")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        else:
            st.info("No non-admin users yet.")

    # ── Tab 2 : Activity log ──────────────────────────────────────────────
    with tab2:
        st.markdown("### Recent Activity (last 200 actions)")

        if log_df.empty:
            st.info("No activity recorded yet.")
        else:
            # Filter controls
            f1, f2 = st.columns(2)
            with f1:
                users_in_log = ["All"] + sorted(log_df["username"].unique().tolist())
                filter_user  = st.selectbox("Filter by user", users_in_log, key="log_filter_user")
            with f2:
                actions_in_log = ["All"] + sorted(log_df["action"].unique().tolist())
                filter_action  = st.selectbox("Filter by action", actions_in_log, key="log_filter_action")

            filtered = log_df.copy()
            if filter_user != "All":
                filtered = filtered[filtered["username"] == filter_user]
            if filter_action != "All":
                filtered = filtered[filtered["action"] == filter_action]

            st.dataframe(
                filtered.rename(columns={
                    "username": "User", "action": "Action",
                    "detail": "Detail", "timestamp": "Time"
                }),
                hide_index=True,
                use_container_width=True,
            )
            st.caption(f"Showing {len(filtered)} of {len(log_df)} records")

    # ── Tab 3 : Prediction usage ──────────────────────────────────────────
    with tab3:
        st.markdown("### Prediction Usage per User")

        if not pred_map:
            st.info("No predictions saved yet.")
        else:
            pred_df = pd.DataFrame(
                list(pred_map.items()), columns=["Username", "Predictions Saved"]
            ).sort_values("Predictions Saved", ascending=False)

            st.bar_chart(pred_df.set_index("Username"))
            st.dataframe(pred_df, hide_index=True, use_container_width=True)