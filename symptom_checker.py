import streamlit as st
import google.generativeai as genai
import json, os, datetime
from dotenv import load_dotenv; load_dotenv()
import os
API_KEY = os.getenv("GEMINI_API_KEY")

#API_KEY = "AIzaSyDsVEs0hKDmIrN8NY48BwH8bAvfDSnrXrM"

COMMON_SYMPTOMS = [
    "Headache", "Fever", "Fatigue", "Cough", "Shortness of breath",
    "Chest pain", "Nausea", "Vomiting", "Diarrhea", "Abdominal pain",
    "Joint pain", "Muscle ache", "Dizziness", "Blurred vision",
    "Excessive thirst", "Frequent urination", "Swelling in legs",
    "Loss of appetite", "Weight loss", "Night sweats", "Back pain",
    "Skin rash", "Palpitations", "Numbness", "Difficulty sleeping"
]

def show_symptom_checker(show_loader):
    st.markdown("## 🩺 Symptom Checker")
    st.markdown("""
    <div style='background:linear-gradient(135deg,#fff7ed,#fef3c7);
                border-left:4px solid #f59e0b;border-radius:10px;
                padding:0.8rem 1rem;margin-bottom:1.2rem;font-size:0.88rem;color:#92400e;'>
        ⚠️ <b>Disclaimer:</b> This tool provides general information only.
        It is NOT a substitute for professional medical advice.
        Always consult a qualified doctor for diagnosis and treatment.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("### 📝 Select Your Symptoms")

        # Quick select from common symptoms
        selected = st.multiselect(
            "Choose from common symptoms:",
            COMMON_SYMPTOMS,
            key="symptom_multiselect"
        )

        # Custom symptom input
        custom = st.text_input(
            "Add other symptoms (comma separated):",
            placeholder="e.g. ringing in ears, dry mouth",
            key="symptom_custom"
        )

        # Patient context
        st.markdown("### 👤 Patient Info (Optional)")
        sc1, sc2 = st.columns(2)
        with sc1:
            age = st.number_input("Age", min_value=1, max_value=100,
                                   value=30, key="sym_age")
            gender = st.selectbox("Gender", ["Not specified", "Male", "Female"],
                                   key="sym_gender")
        with sc2:
            duration = st.selectbox(
                "Duration of symptoms",
                ["Less than 1 day", "1–3 days", "4–7 days",
                 "1–2 weeks", "More than 2 weeks"],
                key="sym_duration"
            )
            severity = st.select_slider(
                "Severity",
                options=["Mild", "Moderate", "Severe"],
                key="sym_severity"
            )

        # Combine all symptoms
        all_symptoms = list(selected)
        if custom.strip():
            all_symptoms += [s.strip() for s in custom.split(",") if s.strip()]

        if st.button("🔍 Analyse Symptoms", key="sym_check_btn", width='stretch'):
            if not all_symptoms:
                st.warning("Please select or enter at least one symptom.")
            else:
                loader_ph = st.empty()
                show_loader(loader_ph, "Analysing symptoms…")
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    symptoms_str = ", ".join(all_symptoms)
                    context = f"Patient: {age} year old {gender.lower()}, symptoms for {duration.lower()}, severity: {severity.lower()}"

                    prompt = f"""You are a knowledgeable medical assistant.
A patient presents with the following symptoms: {symptoms_str}
Context: {context}

Provide a structured medical assessment with these sections:

## 🔍 Symptom Summary
Brief overview of the symptom pattern.

## 🏥 Possible Conditions
List 3-5 possible conditions (most likely first). For each:
- **Condition name** — Likelihood: High/Medium/Low
  - Why: Brief reason
  - Key distinguishing features

## ⚠️ Red Flag Warning Signs
List any symptoms in this presentation that need IMMEDIATE medical attention.

## 🩺 Recommended Next Steps
- What type of doctor to consult
- Tests that may be ordered
- Timeline (urgent/within days/routine)

## 💊 General Self-Care (if appropriate)
Safe general measures while awaiting medical consultation.

## 🚨 Urgency Level
State clearly: EMERGENCY / URGENT (within 24h) / SOON (within week) / ROUTINE

Important: Always recommend consulting a doctor. Do NOT diagnose definitively."""

                    response = model.generate_content(prompt)
                    st.session_state.symptom_result = response.text.strip()
                    st.session_state.symptom_list   = all_symptoms
                except Exception as e:
                    st.session_state.symptom_result = f"Error: {e}"
                loader_ph.empty()

    with col2:
        st.markdown("### 📋 Analysis Results")
        if st.session_state.get("symptom_result"):
            # Urgency badge
            result = st.session_state.symptom_result
            if "EMERGENCY" in result.upper():
                st.error("🚨 EMERGENCY — Seek immediate medical help!")
            elif "URGENT" in result.upper():
                st.warning("⚡ URGENT — See a doctor within 24 hours")
            elif "SOON" in result.upper():
                st.info("📅 See a doctor within the week")
            else:
                st.success("✅ Routine — Schedule a doctor visit")

            st.markdown(result)

            # Save to history
            _save_symptom_history(
                st.session_state.get("_sym_user","user"),
                st.session_state.symptom_list,
                result
            )
        else:
            st.markdown("""
            <div style='background:#f8faff;border:2px dashed #cbd5e1;
                        border-radius:14px;padding:3rem 1rem;text-align:center;
                        color:#94a3b8;'>
                <div style='font-size:2.5rem;margin-bottom:0.5rem;'>🩺</div>
                <div style='font-weight:600;'>Select symptoms and click Analyse</div>
                <div style='font-size:0.85rem;margin-top:0.3rem;'>
                    Results will appear here
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Recent history
        history = _load_symptom_history(
            st.session_state.get("_sym_user","user"))
        if history:
            st.markdown("---")
            st.markdown("**🕐 Recent Checks**")
            for h in history[-3:][::-1]:
                st.markdown(
                    f"<div style='font-size:0.78rem;color:#64748b;padding:0.2rem 0;'>"
                    f"📅 {h['date']} — {', '.join(h['symptoms'][:3])}"
                    f"{'...' if len(h['symptoms'])>3 else ''}</div>",
                    unsafe_allow_html=True
                )

def _save_symptom_history(username, symptoms, result):
    os.makedirs("symptom_history", exist_ok=True)
    path = f"symptom_history/{username}.json"
    history = []
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                history = json.load(f)
        except:
            pass
    history.append({
        "date": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "symptoms": symptoms,
        "result": result
    })
    history = history[-20:]  # keep last 20
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def _load_symptom_history(username):
    path = f"symptom_history/{username}.json"
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []