
# disease_risk.py
"""
Disease Risk Prediction.
FIX: All 3 AI sections (Summary + Medicine + Follow-up) now use a SINGLE
     Gemini API call instead of 3 separate calls — saves 2/3 of quota usage.
"""
import streamlit as st
import numpy as np
import pandas as pd
from database import log_activity


# ─────────────────────────────────────────────────────────────────────────────
# PATIENT ID HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _make_patient_key(owner: str, patient_name: str) -> str:
    safe = patient_name.strip().replace(" ", "_")
    return f"{owner}__{safe}"

def _display_name(patient_key: str) -> str:
    if "__" in patient_key:
        return patient_key.split("__", 1)[1].replace("_", " ")
    return patient_key


# ─────────────────────────────────────────────────────────────────────────────
# MINI PROGRESS PANEL
# ─────────────────────────────────────────────────────────────────────────────
def _mini_progress(patient_key: str, load_progress):
    history = load_progress(patient_key)
    if not history or len(history) < 2:
        return
    df = pd.DataFrame(history).tail(3)
    st.markdown("#### 📅 Recent Progress")
    for _, row in df.iterrows():
        max_risk = max(
            row.get("diabetes", 0), row.get("hypertension", 0),
            row.get("cardiovascular", 0), row.get("kidney", 0)
        )
        badge_color = "#fee2e2" if max_risk >= 70 else ("#fef9c3" if max_risk >= 40 else "#dcfce7")
        badge_text  = "High"    if max_risk >= 70 else ("Moderate" if max_risk >= 40 else "Low")
        text_color  = "#991b1b" if max_risk >= 70 else ("#854d0e"  if max_risk >= 40 else "#166534")
        st.markdown(
            f"<div style='background:#f8faff;border:1px solid #e2e8f0;"
            f"border-radius:10px;padding:0.5rem 0.8rem;margin-bottom:0.4rem;"
            f"font-size:0.82rem;color:#334155;'>"
            f"<b>{row.get('date','')}</b> &nbsp; "
            f"D:{row.get('diabetes',0):.0f}% "
            f"H:{row.get('hypertension',0):.0f}% "
            f"C:{row.get('cardiovascular',0):.0f}% "
            f"K:{row.get('kidney',0):.0f}% "
            f"<span style='background:{badge_color};color:{text_color};"
            f"border-radius:6px;padding:0.1rem 0.5rem;font-weight:600;'>"
            f"{badge_text}</span></div>",
            unsafe_allow_html=True,
        )
    st.caption("👉 Full history in **Health Progress Tracker**")


# ─────────────────────────────────────────────────────────────────────────────
# SINGLE COMBINED AI PROMPT  ← KEY CHANGE
# One call returns all 3 sections: Summary + Medicine + Follow-up Questions
# ─────────────────────────────────────────────────────────────────────────────
def _build_combined_prompt(age, bmi, chol, bp, glucose, insulin,
                            smoking, activity,
                            d_prob, h_prob, c_prob, k_prob) -> str:
    return f"""You are a medical assistant. A patient has just received their disease risk scores.
Provide a complete health report in exactly 3 sections using these headings.

PATIENT: Age {age}, BMI {bmi:.1f}, Glucose {glucose} mg/dL,
Cholesterol {chol} mg/dL, BP {bp} mmHg, Insulin {insulin},
Smoking: {smoking}, Activity: {activity}

RISK SCORES: Diabetes {d_prob*100:.1f}% | Hypertension {h_prob*100:.1f}% | Cardiovascular {c_prob*100:.1f}% | Kidney {k_prob*100:.1f}%

---
### 🤖 AI Health Summary
Briefly explain each risk in simple language. Identify the most dangerous one. Give 3 lifestyle tips. Keep it short.

---
### 💊 Suggested Medicines & Treatments
Only for diseases with risk above 30%. For each:
- Common generic medications (no doses)
- Lifestyle treatment
- When to see a doctor urgently
End with: ⚠️ This is general information only, not a prescription.

---
### 🧑‍⚕️ Doctor Follow-up Questions
List exactly 3 numbered questions a doctor would ask this patient based on their specific risks. One per line, no extra explanation.
"""


def _parse_combined_response(full_text: str) -> tuple:
    """
    Splits the single AI response into 3 parts.
    Returns (summary, medicine, followup) as strings.
    """
    summary   = ""
    medicine  = ""
    followup  = ""

    # Split on the section headings
    parts = full_text.split("###")
    for part in parts:
        p = part.strip()
        if p.startswith("🤖 AI Health Summary"):
            summary = p[len("🤖 AI Health Summary"):].strip()
        elif p.startswith("💊 Suggested Medicines"):
            medicine = p[len("💊 Suggested Medicines & Treatments"):].strip()
        elif p.startswith("🧑‍⚕️ Doctor Follow-up"):
            followup = p[len("🧑‍⚕️ Doctor Follow-up Questions"):].strip()

    # Fallback: if parsing fails just show full text in summary
    if not summary and not medicine and not followup:
        summary = full_text

    return summary, medicine, followup


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def show_disease_risk(
    scaler, diabetes_model, hypertension_model, cardio_model, kidney_model,
    username, show_loader, generate_ai_health_summary,
    create_disease_pdf, save_prediction,
    load_progress=None,
    gemini_generate=None,
):
    st.markdown("## 🩺 Disease Risk Prediction")

    # ── Who is this prediction for? ───────────────────────────────────────
    st.markdown("### 👤 Prediction For")
    who = st.radio(
        "This prediction is for:",
        ["Myself", "Another Patient"],
        horizontal=True,
        key="risk_who_radio",
    )

    patient_key   = username
    display_name  = username
    track_default = True

    if who == "Another Patient":
        col_name, col_track = st.columns([2, 1])
        with col_name:
            raw_name = st.text_input(
                "Patient Name / ID",
                placeholder="e.g. John Doe or patient_001",
                key="risk_other_patient_name",
            ).strip()
        with col_track:
            st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
            track_default = st.checkbox(
                "Save this patient's progress",
                value=False,
                key="risk_other_track",
            )
        if not raw_name:
            st.warning("⚠️ Please enter a patient name / ID to continue.")
            return
        patient_key  = _make_patient_key(username, raw_name)
        display_name = raw_name
        st.caption(f"📁 Saved under your account as `{patient_key}` — only visible to you.")
    else:
        track_default = st.checkbox(
            "💾 Save this prediction to my progress tracker",
            value=True,
            key="risk_self_track",
        )

    st.markdown("<hr style='border-color:#e2e8f0;margin:0.6rem 0 1rem 0;'>",
                unsafe_allow_html=True)

    # ── Input form ────────────────────────────────────────────────────────
    st.markdown("### 📝 Patient Details")

    with st.form("disease_form"):
        c1, c2, c3 = st.columns(3)
        age     = c1.number_input("Age",            min_value=1,    max_value=120,  value=30)
        bmi     = c2.number_input("BMI",            min_value=10.0, max_value=60.0, value=25.0)
        chol    = c3.number_input("Cholesterol",    min_value=50,   max_value=400,  value=180)

        c4, c5, c6 = st.columns(3)
        bp      = c4.number_input("Blood Pressure", min_value=40,   max_value=200,  value=80)
        glucose = c5.number_input("Glucose Level",  min_value=40,   max_value=300,  value=100)
        insulin = c6.number_input("Insulin",        min_value=0,    max_value=300,  value=80)

        c7, c8, c9 = st.columns(3)
        gender   = c7.selectbox("Gender",            ["Male", "Female"],              key="dis_gender")
        smoking  = c8.selectbox("Smoking Status",    ["Never", "Former", "Current"], key="dis_smoking")
        activity = c9.selectbox("Physical Activity", ["Low", "Moderate", "High"],    key="dis_activity")

        submitted = st.form_submit_button("🔍 Predict Disease Risk", width='stretch')

    if not submitted:
        if load_progress:
            _mini_progress(patient_key, load_progress)
        return

    # ── Encode ────────────────────────────────────────────────────────────
    gender_enc   = 1 if gender == "Male" else 0
    smoking_enc  = {"Never": 0, "Former": 1, "Current": 2}[smoking]
    activity_enc = {"Low": 0, "Moderate": 1, "High": 2}[activity]

    features = np.array([[
        age, bmi, chol, bp, gender_enc, glucose, smoking_enc, insulin, activity_enc
    ]])

    try:
        features_scaled = scaler.transform(features)
    except Exception:
        features_scaled = features

    loader_ph = st.empty()
    show_loader(loader_ph, "Running predictions…")

    try:
        d_prob = float(diabetes_model.predict_proba(features_scaled)[0][1])
        h_prob = float(hypertension_model.predict_proba(features_scaled)[0][1])
        c_prob = float(cardio_model.predict_proba(features_scaled)[0][1])
        k_prob = float(kidney_model.predict_proba(features_scaled)[0][1])
    except Exception as e:
        loader_ph.empty()
        st.error(f"Prediction error: {e}")
        return

    loader_ph.empty()

    # ── Results grid ──────────────────────────────────────────────────────
    st.markdown(f"### 📊 Results — Patient: **{display_name}**")

    def _risk_badge(pct):
        if pct >= 70: return "🔴 High Risk"
        if pct >= 40: return "🟡 Moderate"
        return "🟢 Low Risk"

    res_col, prog_col = st.columns([3, 2])
    with res_col:
        rc1, rc2 = st.columns(2)
        rc1.metric(" Diabetes",       f"{d_prob*100:.1f}%", _risk_badge(d_prob*100))
        rc2.metric("💓 Hypertension",   f"{h_prob*100:.1f}%", _risk_badge(h_prob*100))
        rc3, rc4 = st.columns(2)
        rc3.metric("❤️ Cardiovascular", f"{c_prob*100:.1f}%", _risk_badge(c_prob*100))
        rc4.metric("🫘 Kidney Disease", f"{k_prob*100:.1f}%", _risk_badge(k_prob*100))
    with prog_col:
        if load_progress:
            _mini_progress(patient_key, load_progress)

    # ── Save prediction ───────────────────────────────────────────────────
    if track_default:
        save_prediction(patient_key, age, bmi, glucose, d_prob, h_prob, c_prob, k_prob)
        st.success(f"✅ Prediction saved for **{display_name}**.")
        log_activity(username, "Prediction Saved", f"patient_key={patient_key}")
    else:
        st.info("ℹ️ Temporary check — prediction not saved.")
        log_activity(username, "Temporary Prediction", f"patient_key={patient_key}")

    st.markdown("<hr style='border-color:#e2e8f0;margin:1rem 0;'>", unsafe_allow_html=True)

    # ── SINGLE API CALL for all 3 AI sections ────────────────────────────
    # Before: 3 separate calls = 3 quota units used
    # Now:    1 combined call  = 1 quota unit used
    # ─────────────────────────────────────────────────────────────────────
    loader_ai = st.empty()
    show_loader(loader_ai, "Generating AI health report… (1 call)")

    combined_prompt = _build_combined_prompt(
        age, bmi, chol, bp, glucose, insulin,
        smoking, activity,
        d_prob, h_prob, c_prob, k_prob
    )

    try:
        if gemini_generate:
            full_response = gemini_generate(combined_prompt)
        else:
            full_response = generate_ai_health_summary(
                age, bmi, glucose, d_prob, h_prob, c_prob, k_prob
            )
    except Exception as e:
        full_response = f"### 🤖 AI Health Summary\nCould not generate report: {e}"

    loader_ai.empty()

    # Parse the single response into 3 sections
    summary, medicine, followup = _parse_combined_response(full_response)

    # ── Display Section 1: AI Health Summary ─────────────────────────────
    st.markdown("### 🤖 AI Health Summary")
    st.info(summary if summary else full_response)

    # ── Display Section 2: Medicine Suggestions ───────────────────────────
    if medicine:
        st.markdown("### 💊 Suggested Medicines & Treatments")
        st.caption("⚠️ General suggestions only. Always consult a doctor before taking any medication.")
        st.markdown(medicine)

    # ── Display Section 3: Follow-up Questions ────────────────────────────
    if followup:
        st.markdown("### 🧑‍⚕️ AI Follow-up Questions")
        st.caption("Questions a doctor might ask based on your results:")
        st.markdown(followup)

    # ── PDF download ──────────────────────────────────────────────────────
    st.markdown("<hr style='border-color:#e2e8f0;margin:1rem 0;'>", unsafe_allow_html=True)
    try:
        pdf_bytes = create_disease_pdf(
            age, bmi, glucose,
            d_prob*100, h_prob*100, c_prob*100, k_prob*100,
            summary if summary else full_response,
        )
        st.download_button(
            "📥 Download Health Report (PDF)",
            pdf_bytes,
            f"risk_report_{display_name.replace(' ', '_')}.pdf",
            "application/pdf",
        )
    except Exception as e:
        st.warning(f"PDF generation failed: {e}")