
# # disease_risk.py
# """
# Disease Risk Prediction — with:
#   • Updated 9-feature input form (Age, BMI, Cholesterol, BP, Glucose,
#     Insulin, Gender, Smoking, Physical Activity)
#   • Inline mini progress tracker (latest 3 entries)
#   • "Who is this for?" option (Myself / Another Patient)
#   • Temporary Check vs Track Progress mode
#   • AI Health Summary (English only)
#   • Medicine Suggestions via Gemini
#   • AI Follow-up Questions via Gemini
#   • PDF download
# """
# import streamlit as st
# import numpy as np
# import pandas as pd
# import google.generativeai as genai
# from database import log_activity


# # ─────────────────────────────────────────────────────────────────────────────
# # MINI PROGRESS PANEL
# # ─────────────────────────────────────────────────────────────────────────────
# def _mini_progress(patient_id: str, load_progress):
#     history = load_progress(patient_id)
#     if not history or len(history) < 2:
#         return

#     df = pd.DataFrame(history).tail(3)
#     st.markdown("#### 📅 Recent Progress")
#     for _, row in df.iterrows():
#         max_risk = max(
#             row.get("diabetes", 0), row.get("hypertension", 0),
#             row.get("cardiovascular", 0), row.get("kidney", 0)
#         )
#         badge_color = "#fee2e2" if max_risk >= 70 else ("#fef9c3" if max_risk >= 40 else "#dcfce7")
#         badge_text  = "High"    if max_risk >= 70 else ("Moderate" if max_risk >= 40 else "Low")
#         text_color  = "#991b1b" if max_risk >= 70 else ("#854d0e"  if max_risk >= 40 else "#166534")
#         st.markdown(
#             f"<div style='background:#f8faff;border:1px solid #e2e8f0;"
#             f"border-radius:10px;padding:0.5rem 0.8rem;margin-bottom:0.4rem;"
#             f"font-size:0.82rem;color:#334155;'>"
#             f"<b>{row.get('date','')}</b> &nbsp; "
#             f"D:{row.get('diabetes',0):.0f}% &nbsp;"
#             f"H:{row.get('hypertension',0):.0f}% &nbsp;"
#             f"C:{row.get('cardiovascular',0):.0f}% &nbsp;"
#             f"K:{row.get('kidney',0):.0f}% &nbsp;"
#             f"<span style='background:{badge_color};color:{text_color};"
#             f"border-radius:6px;padding:0.1rem 0.5rem;font-weight:600;'>"
#             f"{badge_text}</span></div>",
#             unsafe_allow_html=True,
#         )
#     st.caption("👉 Full history in **Health Progress Tracker**")


# # ─────────────────────────────────────────────────────────────────────────────
# # MAIN
# # ─────────────────────────────────────────────────────────────────────────────
# def show_disease_risk(
#     scaler, diabetes_model, hypertension_model, cardio_model, kidney_model,
#     username, show_loader, generate_ai_health_summary,
#     create_disease_pdf, save_prediction, load_progress=None
# ):
#     st.markdown("## 🩺 Disease Risk Prediction")

#     # ── Who is this prediction for? ───────────────────────────────────────
#     st.markdown("### 👤 Prediction For")
#     who = st.radio(
#         "This prediction is for:",
#         ["Myself", "Another Patient"],
#         horizontal=True,
#         key="risk_who_radio",
#     )

#     patient_id    = username
#     track_default = True

#     if who == "Another Patient":
#         col_name, col_track = st.columns([2, 1])
#         with col_name:
#             patient_id = st.text_input(
#                 "Patient Name / ID",
#                 placeholder="e.g. John_Doe or patient_001",
#                 key="risk_other_patient_name",
#             ).strip()
#         with col_track:
#             st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
#             track_default = st.checkbox(
#                 "Save this patient's progress",
#                 value=False,
#                 key="risk_other_track",
#             )
#         if not patient_id:
#             st.warning("⚠️ Please enter a patient name / ID to continue.")
#             return
#     else:
#         track_default = st.checkbox(
#             "💾 Save this prediction to my progress tracker",
#             value=True,
#             key="risk_self_track",
#         )

#     st.markdown("<hr style='border-color:#e2e8f0;margin:0.6rem 0 1rem 0;'>",
#                 unsafe_allow_html=True)

#     # ── Input form ────────────────────────────────────────────────────────
#     st.markdown("### 📝 Patient Details")

#     with st.form("disease_form"):
#         c1, c2, c3 = st.columns(3)
#         age     = c1.number_input("Age",            min_value=1,    max_value=120,  value=30)
#         bmi     = c2.number_input("BMI",            min_value=10.0, max_value=60.0, value=25.0)
#         chol    = c3.number_input("Cholesterol",    min_value=50,   max_value=400,  value=180)

#         c4, c5, c6 = st.columns(3)
#         bp      = c4.number_input("Blood Pressure", min_value=40,   max_value=200,  value=80)
#         glucose = c5.number_input("Glucose Level",  min_value=40,   max_value=300,  value=100)
#         insulin = c6.number_input("Insulin",        min_value=0,    max_value=300,  value=80)

#         c7, c8, c9 = st.columns(3)
#         gender   = c7.selectbox("Gender",            ["Male", "Female"],              key="dis_gender")
#         smoking  = c8.selectbox("Smoking Status",    ["Never", "Former", "Current"], key="dis_smoking")
#         activity = c9.selectbox("Physical Activity", ["Low", "Moderate", "High"],    key="dis_activity")

#         submitted = st.form_submit_button("🔍 Predict Disease Risk", use_container_width=True)

#     if not submitted:
#         if who == "Myself" and load_progress:
#             _mini_progress(username, load_progress)
#         return

#     # ── Encode categoricals ───────────────────────────────────────────────
#     gender_enc   = 1 if gender == "Male" else 0
#     smoking_enc  = {"Never": 0, "Former": 1, "Current": 2}[smoking]
#     activity_enc = {"Low": 0, "Moderate": 1, "High": 2}[activity]

#     # Feature order must match training:
#     # Age, BMI, Cholesterol, Blood_pressure, Gender,
#     # Glucose_level, Smoking_status, Insulin, Physical_activity
#     features = np.array([[
#         age, bmi, chol, bp,
#         gender_enc, glucose,
#         smoking_enc, insulin, activity_enc
#     ]])

#     try:
#         features_scaled = scaler.transform(features)
#     except Exception:
#         features_scaled = features

#     loader_ph = st.empty()
#     show_loader(loader_ph, "Running predictions…")

#     try:
#         d_prob = float(diabetes_model.predict_proba(features_scaled)[0][1])
#         h_prob = float(hypertension_model.predict_proba(features_scaled)[0][1])
#         c_prob = float(cardio_model.predict_proba(features_scaled)[0][1])
#         k_prob = float(kidney_model.predict_proba(features_scaled)[0][1])
#     except Exception as e:
#         loader_ph.empty()
#         st.error(f"Prediction error: {e}")
#         return

#     loader_ph.empty()

#     # ── Results grid ──────────────────────────────────────────────────────
#     st.markdown(f"### 📊 Results — Patient: **{patient_id}**")

#     def _risk_badge(pct):
#         if pct >= 70: return "🔴 High Risk"
#         if pct >= 40: return "🟡 Moderate"
#         return "🟢 Low Risk"

#     res_col, prog_col = st.columns([3, 2])
#     with res_col:
#         rc1, rc2 = st.columns(2)
#         rc1.metric(" Diabetes",       f"{d_prob*100:.1f}%", _risk_badge(d_prob*100))
#         rc2.metric("💓 Hypertension",   f"{h_prob*100:.1f}%", _risk_badge(h_prob*100))
#         rc3, rc4 = st.columns(2)
#         rc3.metric("❤️ Cardiovascular", f"{c_prob*100:.1f}%", _risk_badge(c_prob*100))
#         rc4.metric("🫘 Kidney Disease", f"{k_prob*100:.1f}%", _risk_badge(k_prob*100))
#     with prog_col:
#         if load_progress:
#             _mini_progress(patient_id, load_progress)

#     # ── Save prediction ───────────────────────────────────────────────────
#     if track_default:
#         save_prediction(patient_id, age, bmi, glucose, d_prob, h_prob, c_prob, k_prob)
#         st.success(f"✅ Prediction saved for **{patient_id}**'s progress tracker.")
#         log_activity(username, "Prediction Saved", f"patient={patient_id}")
#     else:
#         st.info("ℹ️ This was a **temporary check** — prediction not saved.")
#         log_activity(username, "Temporary Prediction", f"patient={patient_id}")

#     st.markdown("<hr style='border-color:#e2e8f0;margin:1rem 0;'>", unsafe_allow_html=True)

#     # ── AI Health Summary ─────────────────────────────────────────────────
#     loader_ai = st.empty()
#     show_loader(loader_ai, "Generating AI Health Summary…")
#     try:
#         summary = generate_ai_health_summary(
#             age, bmi, glucose, d_prob, h_prob, c_prob, k_prob
#         )
#     except Exception as e:
#         summary = f"Could not generate summary: {e}"
#     loader_ai.empty()

#     st.markdown("### 🤖 AI Health Summary")
#     st.info(summary)

#     # ── Medicine Suggestions ──────────────────────────────────────────────
#     st.markdown("### 💊 Suggested Medicines & Treatments")
#     st.caption("⚠️ These are general suggestions only. Always consult a doctor before taking any medication.")

#     loader_med = st.empty()
#     show_loader(loader_med, "Generating medicine suggestions…")
#     try:
#         gemini_med = genai.GenerativeModel("gemini-2.5-flash")
#         med_prompt = f"""You are a medical assistant providing general educational information.

# Patient profile: Age {age}, BMI {bmi:.1f}, Glucose {glucose} mg/dL,
# Cholesterol {chol} mg/dL, Blood Pressure {bp} mmHg, Insulin {insulin},
# Smoking: {smoking}, Physical Activity: {activity}

# Predicted disease risks:
# - Diabetes: {d_prob*100:.1f}%
# - Hypertension: {h_prob*100:.1f}%
# - Cardiovascular: {c_prob*100:.1f}%
# - Kidney Disease: {k_prob*100:.1f}%

# For each disease where risk is above 30%, provide:
# 1. Common medications typically prescribed (generic names only)
# 2. Typical lifestyle treatments (diet, exercise)
# 3. When to see a doctor urgently

# Format clearly with disease headings.
# IMPORTANT: Add disclaimer that this is general information only and not a prescription.
# Do NOT recommend specific doses. Keep it brief and clear."""
#         med_text = gemini_med.generate_content(med_prompt).text.strip()
#     except Exception as e:
#         med_text = f"Could not generate suggestions: {e}"
#     loader_med.empty()
#     st.markdown(med_text)

#     # ── AI Follow-up Questions ────────────────────────────────────────────
#     st.markdown("### 🧑‍⚕️ AI Follow-up Questions")
#     st.caption("Questions a doctor might ask based on your results:")

#     loader_fq = st.empty()
#     show_loader(loader_fq, "Generating follow-up questions…")
#     try:
#         gemini_fq = genai.GenerativeModel("gemini-2.5-flash")
#         fq_prompt = f"""You are a doctor reviewing a patient's health prediction results.

# Patient Details: Age {age}, BMI {bmi:.1f}, Glucose {glucose} mg/dL,
# Cholesterol {chol} mg/dL, Blood Pressure {bp} mmHg, Insulin {insulin},
# Smoking: {smoking}, Physical Activity: {activity}

# Predicted Risks: Diabetes {d_prob*100:.1f}%, Hypertension {h_prob*100:.1f}%,
# Cardiovascular {c_prob*100:.1f}%, Kidney {k_prob*100:.1f}%

# Generate 5 smart follow-up questions a doctor would ask this patient
# to better understand their condition. Make them specific to the risks shown.
# Format: numbered list, one question per line, no extra explanation."""
#         follow_up = gemini_fq.generate_content(fq_prompt).text.strip()
#     except Exception as e:
#         follow_up = f"Could not generate questions: {e}"
#     loader_fq.empty()
#     st.markdown(follow_up)

#     # ── PDF download ──────────────────────────────────────────────────────
#     st.markdown("<hr style='border-color:#e2e8f0;margin:1rem 0;'>", unsafe_allow_html=True)
#     try:
#         pdf_bytes = create_disease_pdf(
#             age, bmi, glucose,
#             d_prob * 100, h_prob * 100, c_prob * 100, k_prob * 100,
#             summary,
#         )
#         st.download_button(
#             "📥 Download Health Report (PDF)",
#             pdf_bytes,
#             f"risk_report_{patient_id}.pdf",
#             "application/pdf",
#         )
#     except Exception as e:
#         st.warning(f"PDF generation failed: {e}")


# disease_risk.py
"""
Disease Risk Prediction.
Accepts gemini_generate from app.py so all Gemini calls automatically
use the dual-key fallback (primary key → secondary key on failure).
"""
import streamlit as st
import numpy as np
import pandas as pd
from database import log_activity


# ─────────────────────────────────────────────────────────────────────────────
# PATIENT ID HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _make_patient_key(owner: str, patient_name: str) -> str:
    """Namespace a patient file under the logged-in user to avoid collisions."""
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
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def show_disease_risk(
    scaler, diabetes_model, hypertension_model, cardio_model, kidney_model,
    username, show_loader, generate_ai_health_summary,
    create_disease_pdf, save_prediction,
    load_progress=None,
    gemini_generate=None,     # dual-key wrapper passed from app.py
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

        submitted = st.form_submit_button("🔍 Predict Disease Risk", use_container_width=True)

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

    # ── Save ──────────────────────────────────────────────────────────────
    if track_default:
        save_prediction(patient_key, age, bmi, glucose, d_prob, h_prob, c_prob, k_prob)
        st.success(f"✅ Prediction saved for **{display_name}**.")
        log_activity(username, "Prediction Saved", f"patient_key={patient_key}")
    else:
        st.info("ℹ️ Temporary check — prediction not saved.")
        log_activity(username, "Temporary Prediction", f"patient_key={patient_key}")

    st.markdown("<hr style='border-color:#e2e8f0;margin:1rem 0;'>", unsafe_allow_html=True)

    # ── Decide which generate function to use ─────────────────────────────
    # If gemini_generate was passed (dual-key wrapper), use it.
    # Otherwise fall back to the generate_ai_health_summary passed in.
    def _gen(prompt: str) -> str:
        if gemini_generate:
            return gemini_generate(prompt)
        return generate_ai_health_summary.__wrapped__(prompt) if hasattr(
            generate_ai_health_summary, "__wrapped__") else str(prompt)

    # ── AI Health Summary ─────────────────────────────────────────────────
    loader_ai = st.empty()
    show_loader(loader_ai, "Generating AI Health Summary…")
    try:
        summary = generate_ai_health_summary(
            age, bmi, glucose, d_prob, h_prob, c_prob, k_prob
        )
    except Exception as e:
        summary = f"Could not generate summary: {e}"
    loader_ai.empty()

    st.markdown("### 🤖 AI Health Summary")
    st.info(summary)

    # ── Medicine Suggestions ──────────────────────────────────────────────
    st.markdown("### 💊 Suggested Medicines & Treatments")
    st.caption("⚠️ General suggestions only. Always consult a doctor before taking any medication.")

    loader_med = st.empty()
    show_loader(loader_med, "Generating medicine suggestions…")
    med_prompt = f"""You are a medical assistant providing general educational information.

Patient: Age {age}, BMI {bmi:.1f}, Glucose {glucose} mg/dL,
Cholesterol {chol} mg/dL, BP {bp} mmHg, Insulin {insulin},
Smoking: {smoking}, Activity: {activity}

Predicted risks — Diabetes: {d_prob*100:.1f}%, Hypertension: {h_prob*100:.1f}%,
Cardiovascular: {c_prob*100:.1f}%, Kidney: {k_prob*100:.1f}%

For each disease where risk > 30%:
1. Common medications (generic names only, no doses)
2. Lifestyle treatments
3. When to see a doctor urgently

Use clear disease headings. End with a disclaimer that this is not a prescription."""
    med_text = _gen(med_prompt)
    loader_med.empty()
    st.markdown(med_text)

    # ── AI Follow-up Questions ────────────────────────────────────────────
    st.markdown("### 🧑‍⚕️ AI Follow-up Questions")
    st.caption("Questions a doctor might ask based on your results:")

    loader_fq = st.empty()
    show_loader(loader_fq, "Generating follow-up questions…")
    fq_prompt = f"""You are a doctor reviewing a patient's health prediction results.

Patient: Age {age}, BMI {bmi:.1f}, Glucose {glucose} mg/dL,
Cholesterol {chol} mg/dL, BP {bp} mmHg, Insulin {insulin},
Smoking: {smoking}, Activity: {activity}

Risks: Diabetes {d_prob*100:.1f}%, Hypertension {h_prob*100:.1f}%,
Cardiovascular {c_prob*100:.1f}%, Kidney {k_prob*100:.1f}%

Generate 5 smart follow-up questions a doctor would ask.
Make them specific to the risks shown.
Format: numbered list, one per line, no extra explanation."""
    follow_up = _gen(fq_prompt)
    loader_fq.empty()
    st.markdown(follow_up)

    # ── PDF download ──────────────────────────────────────────────────────
    st.markdown("<hr style='border-color:#e2e8f0;margin:1rem 0;'>", unsafe_allow_html=True)
    try:
        pdf_bytes = create_disease_pdf(
            age, bmi, glucose,
            d_prob*100, h_prob*100, c_prob*100, k_prob*100,
            summary,
        )
        st.download_button(
            "📥 Download Health Report (PDF)",
            pdf_bytes,
            f"risk_report_{display_name.replace(' ','_')}.pdf",
            "application/pdf",
        )
    except Exception as e:
        st.warning(f"PDF generation failed: {e}")