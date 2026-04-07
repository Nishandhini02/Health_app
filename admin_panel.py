



# admin_panel.py
"""
Admin Panel — accessible only when role == "admin".
Shows:  User list · Activity log · Per-user prediction count
        API Usage Tracker (Gemini + Groq) · Estimated daily users
"""
import streamlit as st
import pandas as pd
import os
import json
import datetime
from database import get_connection

# ─────────────────────────────────────────────────────────────────────────────
# API USAGE LOG HELPERS
# ─────────────────────────────────────────────────────────────────────────────
API_LOG_PATH = "api_usage_log.json"

def log_api_call(provider: str, feature: str, success: bool):
    """
    Call this wherever you make an API call in your feature files.
    provider: "gemini" or "groq"
    feature:  "disease_risk", "lab_report", "diet", "symptom", "bmi", "medication"
    success:  True if call succeeded, False if it failed/fell back
    """
    record = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date":      datetime.datetime.now().strftime("%Y-%m-%d"),
        "provider":  provider,
        "feature":   feature,
        "success":   success,
    }
    log = []
    if os.path.exists(API_LOG_PATH):
        try:
            with open(API_LOG_PATH, "r") as f:
                log = json.load(f)
        except Exception:
            log = []
    log.append(record)
    # Keep only last 10,000 records to avoid huge file
    log = log[-10000:]
    try:
        with open(API_LOG_PATH, "w") as f:
            json.dump(log, f, indent=2)
    except Exception:
        pass

def _load_api_log() -> list:
    if os.path.exists(API_LOG_PATH):
        try:
            with open(API_LOG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

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
# API USAGE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
# Known daily limits per key
_GEMINI_DAILY_PER_KEY = 500
_GROQ_DAILY_PER_KEY   = 14400   # llama-3.1-8b-instant free tier

# Average API calls per feature per user visit
_AVG_CALLS_PER_FEATURE = {
    "disease_risk": 1,   # now 1 combined call
    "lab_report":   1,
    "symptom":      1,
    "diet":         1,
    "bmi":          1,
    "medication":   1,
    "chatbot":      2,   # avg messages per session
}
_AVG_CALLS_PER_USER = sum(_AVG_CALLS_PER_FEATURE.values())   # ~8 calls typical user

def _api_stats(log: list, num_gemini_keys: int, num_groq_keys: int) -> dict:
    if not log:
        return {}

    df = pd.DataFrame(log)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today_df  = df[df["date"] == today]
    total_df  = df.copy()

    # Totals
    total_calls   = len(total_df)
    today_calls   = len(today_df)
    total_success = total_df["success"].sum()
    total_fail    = total_calls - total_success
    success_rate  = round((total_success / total_calls * 100), 1) if total_calls else 0

    # By provider today
    gem_today  = len(today_df[today_df["provider"] == "gemini"])
    groq_today = len(today_df[today_df["provider"] == "groq"])

    # Daily limits
    gemini_limit = num_gemini_keys * _GEMINI_DAILY_PER_KEY
    groq_limit   = num_groq_keys   * _GROQ_DAILY_PER_KEY
    total_limit  = gemini_limit + groq_limit

    # Capacity remaining today
    gemini_remaining = max(0, gemini_limit  - gem_today)
    groq_remaining   = max(0, groq_limit    - groq_today)

    # Estimated users
    est_users_today = round(today_calls / _AVG_CALLS_PER_USER) if today_calls else 0
    est_users_max   = round(total_limit / _AVG_CALLS_PER_USER)

    # By feature
    feature_counts = total_df.groupby("feature").size().reset_index(name="Calls")

    # Last 7 days trend
    df["date"] = pd.to_datetime(df["date"])
    last7 = df[df["date"] >= (pd.Timestamp.now() - pd.Timedelta(days=7))]
    daily_trend = last7.groupby("date").size().reset_index(name="Calls")
    daily_trend["date"] = daily_trend["date"].dt.strftime("%d %b")

    return {
        "total_calls":        total_calls,
        "today_calls":        today_calls,
        "total_success":      int(total_success),
        "total_fail":         int(total_fail),
        "success_rate":       success_rate,
        "gem_today":          gem_today,
        "groq_today":         groq_today,
        "gemini_limit":       gemini_limit,
        "groq_limit":         groq_limit,
        "total_limit":        total_limit,
        "gemini_remaining":   gemini_remaining,
        "groq_remaining":     groq_remaining,
        "est_users_today":    est_users_today,
        "est_users_max":      est_users_max,
        "feature_counts":     feature_counts,
        "daily_trend":        daily_trend,
    }

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def show_admin_panel(num_gemini_keys: int = 2, num_groq_keys: int = 2):
    st.markdown("## 🛡️ Admin Panel")

    # ── Summary metrics ───────────────────────────────────────────────────
    users_df = _all_users()
    log_df   = _activity_log()
    pred_map = _prediction_counts()

    total_users   = len(users_df)
    total_actions = len(log_df)
    total_preds   = sum(pred_map.values())

    today_str    = pd.Timestamp.now().strftime("%Y-%m-%d")
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
    tab1, tab2, tab3, tab4 = st.tabs([
        "📁 User Management",
        "📊 Activity Log",
        "🩺 Prediction Usage",
        "🤖 API Usage",
    ])

    # ── Tab 1: User list ──────────────────────────────────────────────────
    with tab1:
        st.markdown("### Registered Users")
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

    # ── Tab 2: Activity log ───────────────────────────────────────────────
    with tab2:
        st.markdown("### Recent Activity (last 200 actions)")
        if log_df.empty:
            st.info("No activity recorded yet.")
        else:
            f1, f2 = st.columns(2)
            with f1:
                users_in_log  = ["All"] + sorted(log_df["username"].unique().tolist())
                filter_user   = st.selectbox("Filter by user",   users_in_log,  key="log_filter_user")
            with f2:
                actions_in_log = ["All"] + sorted(log_df["action"].unique().tolist())
                filter_action  = st.selectbox("Filter by action", actions_in_log, key="log_filter_action")

            filtered = log_df.copy()
            if filter_user   != "All": filtered = filtered[filtered["username"] == filter_user]
            if filter_action != "All": filtered = filtered[filtered["action"]   == filter_action]

            st.dataframe(
                filtered.rename(columns={
                    "username": "User", "action": "Action",
                    "detail": "Detail", "timestamp": "Time"
                }),
                hide_index=True, use_container_width=True,
            )
            st.caption(f"Showing {len(filtered)} of {len(log_df)} records")

    # ── Tab 3: Prediction usage ───────────────────────────────────────────
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

    # ── Tab 4: API Usage ──────────────────────────────────────────────────
    with tab4:
        st.markdown("### 🤖 API Usage Dashboard")
        st.caption(
            f"Tracking Gemini ({num_gemini_keys} keys × {_GEMINI_DAILY_PER_KEY}/day) "
            f"+ Groq ({num_groq_keys} keys × {_GROQ_DAILY_PER_KEY}/day)"
        )

        api_log  = _load_api_log()
        stats    = _api_stats(api_log, num_gemini_keys, num_groq_keys)

        if not stats:
            st.info("No API calls logged yet. API usage will appear here once users start using the app.")
            st.markdown("""
            **How logging works:**
            - Every Gemini and Groq call is automatically recorded in `api_usage_log.json`
            - Success and failure counts are tracked separately
            - Data resets when you delete the log file
            """)
            return

        # ── Key metrics row ───────────────────────────────────────────────
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("📞 Calls Today",       stats["today_calls"])
        a2.metric("✅ Success Rate",       f"{stats['success_rate']}%")
        a3.metric("❌ Failed Calls",       stats["total_fail"])
        a4.metric("👥 Est. Users Today",  stats["est_users_today"])

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # ── Capacity remaining ────────────────────────────────────────────
        st.markdown("#### 📊 Daily Capacity Remaining")
        cap1, cap2 = st.columns(2)

        with cap1:
            gem_used_pct = round(stats["gem_today"] / stats["gemini_limit"] * 100, 1) if stats["gemini_limit"] else 0
            st.markdown(
                f"<div style='background:#eff6ff;border:1px solid #bfdbfe;"
                f"border-radius:10px;padding:1rem;'>"
                f"<div style='font-weight:700;color:#1e3a5f;margin-bottom:0.3rem;'>🔵 Gemini</div>"
                f"<div style='font-size:1.4rem;font-weight:700;color:#2563eb;'>"
                f"{stats['gemini_remaining']:,} remaining</div>"
                f"<div style='font-size:0.82rem;color:#64748b;'>"
                f"{stats['gem_today']} used of {stats['gemini_limit']} today ({gem_used_pct}%)</div>"
                f"</div>",
                unsafe_allow_html=True
            )

        with cap2:
            groq_used_pct = round(stats["groq_today"] / stats["groq_limit"] * 100, 1) if stats["groq_limit"] else 0
            st.markdown(
                f"<div style='background:#f0fdf4;border:1px solid #bbf7d0;"
                f"border-radius:10px;padding:1rem;'>"
                f"<div style='font-weight:700;color:#166534;margin-bottom:0.3rem;'>🟢 Groq</div>"
                f"<div style='font-size:1.4rem;font-weight:700;color:#16a34a;'>"
                f"{stats['groq_remaining']:,} remaining</div>"
                f"<div style='font-size:0.82rem;color:#64748b;'>"
                f"{stats['groq_today']} used of {stats['groq_limit']:,} today ({groq_used_pct}%)</div>"
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # ── Estimated users capacity ──────────────────────────────────────
        st.markdown("#### 👥 User Capacity Estimate")
        st.info(
            f"**Avg API calls per user per visit:** ~{_AVG_CALLS_PER_USER} calls  \n"
            f"**Total daily limit (all keys):** {stats['total_limit']:,} calls  \n"
            f"**Estimated max users/day:** ~{stats['est_users_max']} users  \n"
            f"**Estimated users today:** ~{stats['est_users_today']} users"
        )

        # ── Calls by feature ──────────────────────────────────────────────
        if not stats["feature_counts"].empty:
            st.markdown("#### 📋 Calls by Feature (All Time)")
            st.bar_chart(stats["feature_counts"].set_index("feature"))
            st.dataframe(
                stats["feature_counts"].rename(columns={"feature": "Feature", "Calls": "Total Calls"}),
                hide_index=True, use_container_width=True
            )

        # ── 7-day trend ───────────────────────────────────────────────────
        if not stats["daily_trend"].empty:
            st.markdown("#### 📈 Daily API Calls — Last 7 Days")
            st.line_chart(stats["daily_trend"].set_index("date"))

        # ── Total summary ─────────────────────────────────────────────────
        st.markdown("#### 🗂️ All-Time Summary")
        s1, s2, s3 = st.columns(3)
        s1.metric("Total Calls",   stats["total_calls"])
        s2.metric("Total Success", stats["total_success"])
        s3.metric("Total Failed",  stats["total_fail"])

        # Clear log button
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear API Log", key="clear_api_log"):
            try:
                if os.path.exists(API_LOG_PATH):
                    os.remove(API_LOG_PATH)
                st.success("✅ API log cleared.")
                st.rerun()
            except Exception as e:
                st.error(str(e))