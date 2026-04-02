#progress tracker
import streamlit as st
import pandas as pd
import os


def show_progress(username: str, load_progress):

    st.markdown("## 📅 Health Progress Tracker")

    # ── Patient selector ──────────────────────────────────────────────────────
    # Admin sees all patients; regular users see only themselves
    ADMIN_USER = "admin"
    is_admin   = (username == ADMIN_USER)

    all_patients = [username]   # default: own data only

    if is_admin:
        # Discover all users who have health history
        progress_dir = "health_progress"
        if os.path.exists(progress_dir):
            files = [f.replace(".json","") for f in os.listdir(progress_dir)
                     if f.endswith(".json")]
            all_patients = sorted(files) if files else [username]

    # Patient selection UI
    if is_admin and len(all_patients) > 1:
        st.markdown("""
        <div style='background:#fff7ed;border-left:4px solid #f59e0b;
                    border-radius:8px;padding:0.5rem 1rem;margin-bottom:0.8rem;
                    font-size:0.85rem;color:#92400e;'>
            🔑 <b>Admin view</b> — you can view any patient's health progress
        </div>
        """, unsafe_allow_html=True)

        view_col, compare_col = st.columns([1, 1])
        with view_col:
            selected_patient = st.selectbox(
                "👤 View patient:", all_patients,
                index=all_patients.index(username) if username in all_patients else 0,
                key="progress_patient_select"
            )
        with compare_col:
            compare_mode = st.checkbox("📊 Compare two patients", key="compare_mode")

        if compare_mode:
            other_patient = st.selectbox(
                "Compare with:", [p for p in all_patients if p != selected_patient],
                key="progress_compare_select"
            )
            _show_comparison(selected_patient, other_patient, load_progress)
            return
    else:
        selected_patient = username
        if not is_admin:
            st.caption(f"Tracking health predictions for **{username}**")

    # ── Show selected patient's history ──────────────────────────────────────
    _show_patient_history(selected_patient, load_progress, is_admin)


def _show_comparison(patient1: str, patient2: str, load_progress):
    """Side-by-side comparison of two patients' latest predictions."""
    st.markdown(f"### 📊 Comparing: **{patient1}** vs **{patient2}**")

    h1 = load_progress(patient1)
    h2 = load_progress(patient2)

    if not h1 or not h2:
        st.warning("One or both patients have no prediction history.")
        return

    l1 = pd.DataFrame(h1).iloc[-1]
    l2 = pd.DataFrame(h2).iloc[-1]

    diseases = [(" Diabetes", "diabetes"), ("💓 Hypertension", "hypertension"),
                ("❤️ Cardiovascular", "cardiovascular"), ("🫘 Kidney", "kidney")]

    st.markdown("#### Latest Risk Comparison")
    for emoji_label, key in diseases:
        v1 = l1.get(key, 0)
        v2 = l2.get(key, 0)
        c1, c2, c3 = st.columns([2,2,1])
        with c1:
            st.metric(f"{emoji_label} — {patient1}", f"{v1:.1f}%")
        with c2:
            st.metric(f"{emoji_label} — {patient2}", f"{v2:.1f}%",
                      delta=f"{v2-v1:+.1f}%")
        with c3:
            higher = patient1 if v1 > v2 else patient2
            st.markdown(
                f"<div style='padding:0.4rem;text-align:center;font-size:0.75rem;"
                f"color:#dc2626;'>Higher: {higher}</div>",
                unsafe_allow_html=True
            )


def _show_patient_history(patient: str, load_progress, is_admin: bool):
    """Show full health history for a single patient."""
    history = load_progress(patient)

    if not history:
        if is_admin:
            st.info(f"No predictions recorded yet for **{patient}**.")
        else:
            st.info("No predictions saved yet. Run a **Disease Risk Prediction** first — "
                    "each prediction is automatically saved here.")
        return

    df = pd.DataFrame(history)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["date_str"] = df["date"].dt.strftime("%d %b %Y %H:%M")

    if is_admin and patient:
        st.markdown(f"#### Patient: **{patient}** — {len(df)} prediction(s)")
    else:
        st.markdown(f"**{len(df)} prediction{'s' if len(df)>1 else ''} recorded**")

    # ── Summary metrics — latest vs first ────────────────────────────────
    if len(df) > 1:
        latest = df.iloc[-1]
        first  = df.iloc[0]
        st.markdown("### 📊 Latest vs First Prediction")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(" Diabetes",
                  f"{latest['diabetes']:.1f}%",
                  f"{latest['diabetes']-first['diabetes']:+.1f}%")
        c2.metric("💓 Hypertension",
                  f"{latest['hypertension']:.1f}%",
                  f"{latest['hypertension']-first['hypertension']:+.1f}%")
        c3.metric("❤️ Cardiovascular",
                  f"{latest['cardiovascular']:.1f}%",
                  f"{latest['cardiovascular']-first['cardiovascular']:+.1f}%")
        c4.metric("🫘 Kidney",
                  f"{latest['kidney']:.1f}%",
                  f"{latest['kidney']-first['kidney']:+.1f}%")

    # ── Trend charts ──────────────────────────────────────────────────────
    st.markdown("### 📈 Risk Trends Over Time")
    tab1, tab2 = st.tabs(["Disease Risk Trends", "BMI & Glucose Trends"])
    with tab1:
        chart_df = df.set_index("date_str")[["diabetes","hypertension",
                                              "cardiovascular","kidney"]]
        chart_df.columns = ["Diabetes %","Hypertension %",
                             "Cardiovascular %","Kidney %"]
        st.line_chart(chart_df)
    with tab2:
        if "bmi" in df.columns and "glucose" in df.columns:
            bio_df = df.set_index("date_str")[["bmi","glucose"]]
            bio_df.columns = ["BMI","Glucose (mg/dL)"]
            st.line_chart(bio_df)

    # ── Colour-coded history table ─────────────────────────────────────────
    st.markdown("### 📋 Full Prediction History")

    def colour_row(row):
        max_risk = max(row.get("diabetes",0), row.get("hypertension",0),
                       row.get("cardiovascular",0), row.get("kidney",0))
        if max_risk >= 70:
            return ["background-color:#fee2e2;color:#991b1b"] * len(row)
        elif max_risk >= 40:
            return ["background-color:#fef9c3;color:#854d0e"] * len(row)
        return ["background-color:#dcfce7;color:#166534"] * len(row)

    display_cols = ["date_str","age","bmi","glucose",
                    "diabetes","hypertension","cardiovascular","kidney"]
    available    = [c for c in display_cols if c in df.columns]
    display_df   = df[available].copy()
    display_df.columns = [c.replace("date_str","Date").replace("_"," ").title()
                          for c in available]
    st.dataframe(display_df.style.apply(colour_row, axis=1),
                 hide_index=True, width='stretch')
    st.caption("🟢 Low risk (<40%)  🟡 Moderate (40–70%)  🔴 High (≥70%)")

    # ── Clear history ──────────────────────────────────────────────────────
    import os, json
    if st.button(f"🗑️ Clear history for {patient}", key="clear_progress"):
        path = os.path.join("health_progress", f"{patient}.json")
        if os.path.exists(path):
            os.remove(path)
        st.success("History cleared.")
        st.rerun()