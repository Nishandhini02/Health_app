
# # # symptom_checker.py
# # import streamlit as st
# # import json, os, datetime

# # COMMON_SYMPTOMS = [
# #     "Headache", "Fever", "Fatigue", "Cough", "Shortness of breath",
# #     "Chest pain", "Nausea", "Vomiting", "Diarrhea", "Abdominal pain",
# #     "Joint pain", "Muscle ache", "Dizziness", "Blurred vision",
# #     "Excessive thirst", "Frequent urination", "Swelling in legs",
# #     "Loss of appetite", "Weight loss", "Night sweats", "Back pain",
# #     "Skin rash", "Palpitations", "Numbness", "Difficulty sleeping"
# # ]

# # def show_symptom_checker(show_loader, groq_generate=None):
# #     st.markdown("## 🩺 Symptom Checker")
# #     st.markdown("""
# #     <div style='background:linear-gradient(135deg,#fff7ed,#fef3c7);
# #                 border-left:4px solid #f59e0b;border-radius:10px;
# #                 padding:0.8rem 1rem;margin-bottom:1.2rem;font-size:0.88rem;color:#92400e;'>
# #         ⚠️ <b>Disclaimer:</b> This tool provides general information only.
# #         It is NOT a substitute for professional medical advice.
# #         Always consult a qualified doctor for diagnosis and treatment.
# #     </div>
# #     """, unsafe_allow_html=True)

# #     col1, col2 = st.columns([1.2, 1])

# #     with col1:
# #         st.markdown("### 📝 Select Your Symptoms")

# #         selected = st.multiselect(
# #             "Choose from common symptoms:",
# #             COMMON_SYMPTOMS,
# #             key="symptom_multiselect"
# #         )

# #         custom = st.text_input(
# #             "Add other symptoms (comma separated):",
# #             placeholder="e.g. ringing in ears, dry mouth",
# #             key="symptom_custom"
# #         )

# #         st.markdown("### 👤 Patient Info (Optional)")
# #         sc1, sc2 = st.columns(2)
# #         with sc1:
# #             age    = st.number_input("Age", min_value=1, max_value=100,
# #                                      value=30, key="sym_age")
# #             gender = st.selectbox("Gender", ["Not specified", "Male", "Female"],
# #                                   key="sym_gender")
# #         with sc2:
# #             duration = st.selectbox(
# #                 "Duration of symptoms",
# #                 ["Less than 1 day", "1–3 days", "4–7 days",
# #                  "1–2 weeks", "More than 2 weeks"],
# #                 key="sym_duration"
# #             )
# #             severity = st.select_slider(
# #                 "Severity",
# #                 options=["Mild", "Moderate", "Severe"],
# #                 key="sym_severity"
# #             )

# #         all_symptoms = list(selected)
# #         if custom.strip():
# #             all_symptoms += [s.strip() for s in custom.split(",") if s.strip()]

# #         if st.button("🔍 Analyse Symptoms", key="sym_check_btn", width='stretch'):
# #             if not all_symptoms:
# #                 st.warning("Please select or enter at least one symptom.")
# #             else:
# #                 loader_ph = st.empty()
# #                 show_loader(loader_ph, "Analysing symptoms…")

# #                 symptoms_str = ", ".join(all_symptoms)
# #                 context = (
# #                     f"Patient: {age} year old {gender.lower()}, "
# #                     f"symptoms for {duration.lower()}, severity: {severity.lower()}"
# #                 )

# #                 system = (
# #                     "You are a knowledgeable medical assistant. "
# #                     "Always recommend consulting a doctor. Do NOT diagnose definitively."
# #                 )

# #                 prompt = f"""A patient presents with the following symptoms: {symptoms_str}
# # Context: {context}

# # Provide a structured medical assessment with these sections:

# # ## 🔍 Symptom Summary
# # Brief overview of the symptom pattern.

# # ## 🏥 Possible Conditions
# # List 3possible conditions (most likely first). For each:
# # - **Condition name** — Likelihood: High/Medium/Low
# #   - Why: Brief reason
# #   - Key distinguishing features

# # ## ⚠️ Red Flag Warning Signs
# # List any symptoms in this presentation that need IMMEDIATE medical attention.

# # ## 🩺 Recommended Next Steps.Give in 3 lines 
# # - What type of doctor to consult
# # - Tests that may be ordered
# # - Timeline (urgent/within days/routine)

# # ## 💊 General Self-Care (if appropriate)
# # Safe general measures while awaiting medical consultation.

# # ## 🚨 Urgency Level
# # State clearly: EMERGENCY / URGENT (within 24h) / SOON (within week) / ROUTINE"""

# #                 result = groq_generate(
# #                     prompt=prompt,
# #                     system=system,
# #                     model="llama-3.1-8b-instant"
# #                 )

# #                 st.session_state.symptom_result = result
# #                 st.session_state.symptom_list   = all_symptoms
# #                 loader_ph.empty()

# #     with col2:
# #         st.markdown("### 📋 Analysis Results")
# #         if st.session_state.get("symptom_result"):
# #             result = st.session_state.symptom_result
# #             if "EMERGENCY" in result.upper():
# #                 st.error("🚨 EMERGENCY — Seek immediate medical help!")
# #             elif "URGENT" in result.upper():
# #                 st.warning("⚡ URGENT — See a doctor within 24 hours")
# #             elif "SOON" in result.upper():
# #                 st.info("📅 See a doctor within the week")
# #             else:
# #                 st.success("✅ Routine — Schedule a doctor visit")

# #             st.markdown(result)

# #             _save_symptom_history(
# #                 st.session_state.get("_sym_user", "user"),
# #                 st.session_state.symptom_list,
# #                 result
# #             )
# #         else:
# #             st.markdown("""
# #             <div style='background:#f8faff;border:2px dashed #cbd5e1;
# #                         border-radius:14px;padding:3rem 1rem;text-align:center;
# #                         color:#94a3b8;'>
# #                 <div style='font-size:2.5rem;margin-bottom:0.5rem;'>🩺</div>
# #                 <div style='font-weight:600;'>Select symptoms and click Analyse</div>
# #                 <div style='font-size:0.85rem;margin-top:0.3rem;'>
# #                     Results will appear here
# #                 </div>
# #             </div>
# #             """, unsafe_allow_html=True)

# #         history = _load_symptom_history(st.session_state.get("_sym_user", "user"))
# #         if history:
# #             st.markdown("---")
# #             st.markdown("**🕐 Recent Checks**")
# #             for h in history[-3:][::-1]:
# #                 st.markdown(
# #                     f"<div style='font-size:0.78rem;color:#64748b;padding:0.2rem 0;'>"
# #                     f"📅 {h['date']} — {', '.join(h['symptoms'][:3])}"
# #                     f"{'...' if len(h['symptoms']) > 3 else ''}</div>",
# #                     unsafe_allow_html=True
# #                 )

# # def _save_symptom_history(username, symptoms, result):
# #     import pytz
# #     from datetime import datetime
# #     ist = pytz.timezone("Asia/Kolkata")
# #     os.makedirs("symptom_history", exist_ok=True)
# #     path = f"symptom_history/{username}.json"
# #     history = []
# #     if os.path.exists(path):
# #         try:
# #             with open(path, encoding="utf-8") as f:
# #                 history = json.load(f)
# #         except:
# #             pass
# #     history.append({
# #         "date": datetime.now(ist).strftime("%d %b %Y, %I:%M %p"),
# #         "symptoms": symptoms,
# #         "result": result
# #     })
# #     history = history[-20:]
# #     with open(path, "w", encoding="utf-8") as f:
# #         json.dump(history, f, indent=2, ensure_ascii=False)


# # def _load_symptom_history(username):
# #     path = f"symptom_history/{username}.json"
# #     if os.path.exists(path):
# #         try:
# #             with open(path, encoding="utf-8") as f:
# #                 return json.load(f)
# #         except:
# #             pass
# #     return []



# # symptom_checker.py
# import streamlit as st
# import json
# import os
# import datetime

# COMMON_SYMPTOMS = [
#     "Headache", "Fever", "Fatigue", "Cough", "Shortness of breath",
#     "Chest pain", "Nausea", "Vomiting", "Diarrhea", "Abdominal pain",
#     "Joint pain", "Muscle ache", "Dizziness", "Blurred vision",
#     "Excessive thirst", "Frequent urination", "Swelling in legs",
#     "Loss of appetite", "Weight loss", "Night sweats", "Back pain",
#     "Skin rash", "Palpitations", "Numbness", "Difficulty sleeping"
# ]

# # ─────────────────────────────────────────────────────────────────────────────
# # SINGLE-CALL SELF-REVIEW PROMPT
# #
# # Strategy: reflection happens INSIDE one prompt — not a second API call.
# # The model is told to:
# #   1. Draft an initial answer internally (not shown)
# #   2. Review it for hallucination / overclaiming
# #   3. Output only the verified, corrected final answer
# #
# # This gives you ~80% of a two-call reflection agent at 0% extra API cost.
# # ─────────────────────────────────────────────────────────────────────────────

# _SYSTEM = (
#     "You are a cautious medical assistant. "
#     "Never claim a definitive diagnosis. "
#     "Always recommend consulting a qualified doctor. "
#     "Think carefully before responding — avoid speculation."
# )

# def _build_prompt(symptoms_str: str, context: str) -> str:
#     return f"""Patient symptoms: {symptoms_str}
# Context: {context}

# INTERNAL INSTRUCTION (do not show this step in output):
# Before writing your response, mentally draft an answer, then ask yourself:
# - Am I speculating beyond the given symptoms?
# - Have I overclaimed any diagnosis?
# - Are my urgency levels accurate?
# Correct any issues, then write only the final verified answer below.

# ---

# Respond with exactly these 4 sections. Be concise — 2-3 lines per section max.

# **Possible Conditions** (top 2-3, most likely first)
# For each: name | likelihood (High/Medium/Low) | one-line reason

# **Red Flags** (symptoms needing immediate attention, or "None identified")

# **Next Steps** (doctor type, likely tests, timeline in one sentence each)

# **Urgency**
# One word only: EMERGENCY / URGENT / SOON / ROUTINE — followed by one sentence why.

# Do not add any other sections or headings."""


# def show_symptom_checker(show_loader, groq_generate=None):
#     st.markdown("## 🩺 Symptom Checker")
#     st.markdown("""
#     <div style='background:linear-gradient(135deg,#fff7ed,#fef3c7);
#                 border-left:4px solid #f59e0b;border-radius:10px;
#                 padding:0.8rem 1rem;margin-bottom:1.2rem;font-size:0.88rem;color:#92400e;'>
#         ⚠️ <b>Disclaimer:</b> This tool provides general information only.
#         It is NOT a substitute for professional medical advice.
#         Always consult a qualified doctor for diagnosis and treatment.
#     </div>
#     """, unsafe_allow_html=True)

#     col1, col2 = st.columns([1.2, 1])

#     with col1:
#         st.markdown("### 📝 Select Your Symptoms")

#         selected = st.multiselect(
#             "Choose from common symptoms:",
#             COMMON_SYMPTOMS,
#             key="symptom_multiselect"
#         )

#         custom = st.text_input(
#             "Add other symptoms (comma separated):",
#             placeholder="e.g. ringing in ears, dry mouth",
#             key="symptom_custom"
#         )

#         st.markdown("### 👤 Patient Info (Optional)")
#         sc1, sc2 = st.columns(2)
#         with sc1:
#             age    = st.number_input("Age", min_value=1, max_value=100,
#                                      value=30, key="sym_age")
#             gender = st.selectbox("Gender", ["Not specified", "Male", "Female"],
#                                   key="sym_gender")
#         with sc2:
#             duration = st.selectbox(
#                 "Duration of symptoms",
#                 ["Less than 1 day", "1–3 days", "4–7 days",
#                  "1–2 weeks", "More than 2 weeks"],
#                 key="sym_duration"
#             )
#             severity = st.select_slider(
#                 "Severity",
#                 options=["Mild", "Moderate", "Severe"],
#                 key="sym_severity"
#             )

#         all_symptoms = list(selected)
#         if custom.strip():
#             all_symptoms += [s.strip() for s in custom.split(",") if s.strip()]

#         # Use st.empty for warning so it doesn't shift layout
#         _warn_ph = st.empty()

#         if st.button("🔍 Analyse Symptoms", key="sym_check_btn", width='stretch'):
#             if not all_symptoms:
#                 _warn_ph.warning("Please select or enter at least one symptom.")
#             else:
#                 _warn_ph.empty()
#                 loader_ph = st.empty()
#                 show_loader(loader_ph, "Analysing symptoms…")

#                 symptoms_str = ", ".join(all_symptoms)
#                 context = (
#                     f"Patient: {age} year old {gender.lower()}, "
#                     f"symptoms for {duration.lower()}, severity: {severity.lower()}"
#                 )

#                 # Single API call — self-review is embedded in the prompt
#                 result = groq_generate(
#                     prompt=_build_prompt(symptoms_str, context),
#                     system=_SYSTEM,
#                     model="llama-3.1-8b-instant",
#                     feature="symptom_checker",
#                 )

#                 st.session_state.symptom_result = result
#                 st.session_state.symptom_list   = all_symptoms
#                 loader_ph.empty()

#     with col2:
#         st.markdown("### 📋 Analysis Results")

#         if st.session_state.get("symptom_result"):
#             result = st.session_state.symptom_result

#             # Urgency badge — derived from result text, no extra API call
#             result_upper = result.upper()
#             if "EMERGENCY" in result_upper:
#                 st.error("🚨 EMERGENCY — Seek immediate medical help!")
#             elif "URGENT" in result_upper:
#                 st.warning("⚡ URGENT — See a doctor within 24 hours")
#             elif "SOON" in result_upper:
#                 st.info("📅 See a doctor within the week")
#             else:
#                 st.success("✅ Routine — Schedule a doctor visit")

#             st.markdown(result)

#             # Save history only once per analysis (not on every rerun)
#             _last_saved = st.session_state.get("_sym_last_saved")
#             _current_key = str(st.session_state.symptom_list)
#             if _last_saved != _current_key:
#                 _save_symptom_history(
#                     st.session_state.get("_sym_user", "user"),
#                     st.session_state.symptom_list,
#                     result,
#                 )
#                 st.session_state["_sym_last_saved"] = _current_key

#         else:
#             st.markdown("""
#             <div style='background:#f8faff;border:2px dashed #cbd5e1;
#                         border-radius:14px;padding:3rem 1rem;text-align:center;
#                         color:#94a3b8;'>
#                 <div style='font-size:2.5rem;margin-bottom:0.5rem;'>🩺</div>
#                 <div style='font-weight:600;'>Select symptoms and click Analyse</div>
#                 <div style='font-size:0.85rem;margin-top:0.3rem;'>
#                     Results will appear here
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)

#         # Recent history
#         history = _load_symptom_history(st.session_state.get("_sym_user", "user"))
#         if history:
#             st.markdown("---")
#             st.markdown("**🕐 Recent Checks**")
#             for h in history[-3:][::-1]:
#                 st.markdown(
#                     f"<div style='font-size:0.78rem;color:#64748b;padding:0.2rem 0;'>"
#                     f"📅 {h['date']} — {', '.join(h['symptoms'][:3])}"
#                     f"{'...' if len(h['symptoms']) > 3 else ''}</div>",
#                     unsafe_allow_html=True
#                 )


# # ─────────────────────────────────────────────────────────────────────────────
# # HISTORY HELPERS
# # ─────────────────────────────────────────────────────────────────────────────

# def _save_symptom_history(username: str, symptoms: list, result: str):
#     import pytz
#     from datetime import datetime
#     ist = pytz.timezone("Asia/Kolkata")
#     os.makedirs("symptom_history", exist_ok=True)
#     path = f"symptom_history/{username}.json"
#     history = []
#     if os.path.exists(path):
#         try:
#             with open(path, encoding="utf-8") as f:
#                 history = json.load(f)
#         except Exception:
#             pass
#     history.append({
#         "date":     datetime.now(ist).strftime("%d %b %Y, %I:%M %p"),
#         "symptoms": symptoms,
#         "result":   result,
#     })
#     history = history[-20:]
#     with open(path, "w", encoding="utf-8") as f:
#         json.dump(history, f, indent=2, ensure_ascii=False)


# def _load_symptom_history(username: str) -> list:
#     path = f"symptom_history/{username}.json"
#     if os.path.exists(path):
#         try:
#             with open(path, encoding="utf-8") as f:
#                 return json.load(f)
#         except Exception:
#             pass
#     return []


# symptom_checker.py
# KEY FIX: All patient inputs wrapped in st.form().
# Widgets inside a form do NOT trigger a page rerun on +/- or dropdown change.
# Only the submit button fires a rerun — identical to how Disease Risk works.

import streamlit as st
import json
import os

COMMON_SYMPTOMS = [
    "Headache", "Fever", "Fatigue", "Cough", "Shortness of breath",
    "Chest pain", "Nausea", "Vomiting", "Diarrhea", "Abdominal pain",
    "Joint pain", "Muscle ache", "Dizziness", "Blurred vision",
    "Excessive thirst", "Frequent urination", "Swelling in legs",
    "Loss of appetite", "Weight loss", "Night sweats", "Back pain",
    "Skin rash", "Palpitations", "Numbness", "Difficulty sleeping"
]

_SYSTEM = (
    "You are a cautious medical assistant. "
    "Never claim a definitive diagnosis. "
    "Always recommend consulting a qualified doctor. "
    "Think carefully before responding — avoid speculation."
)

def _build_prompt(symptoms_str: str, context: str) -> str:
    return f"""Patient symptoms: {symptoms_str}
Context: {context}

INTERNAL INSTRUCTION (do not show this step in output):
Before writing your response, mentally draft an answer, then ask yourself:
- Am I speculating beyond the given symptoms?
- Have I overclaimed any diagnosis?
- Are my urgency levels accurate?
Correct any issues, then write only the final verified answer below.

---

Respond with exactly these 4 sections. Be concise — 2-3 lines per section max.

**Possible Conditions** (top 2-3, most likely first)
For each: name | likelihood (High/Medium/Low) | one-line reason

**Red Flags** (symptoms needing immediate attention, or "None identified")

**Next Steps** (doctor type, likely tests, timeline in one sentence each)

**Urgency**
One word only: EMERGENCY / URGENT / SOON / ROUTINE — followed by one sentence why.

Do not add any other sections or headings."""


def show_symptom_checker(show_loader, groq_generate=None):
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
        # ── ALL INPUTS INSIDE st.form ──────────────────────────────────────
        # This is the EXACT reason Disease Risk has no blur:
        # widgets inside a form don't fire reruns on individual interactions.
        # Only clicking the submit button triggers a rerun.
        with st.form(key="symptom_form", border=False):
            st.markdown("### 📝 Select Your Symptoms")

            selected = st.multiselect(
                "Choose from common symptoms:",
                COMMON_SYMPTOMS,
                key="symptom_multiselect"
            )

            custom = st.text_input(
                "Add other symptoms (comma separated):",
                placeholder="e.g. ringing in ears, dry mouth",
                key="symptom_custom"
            )

            st.markdown("### 👤 Patient Info (Optional)")
            sc1, sc2 = st.columns(2)
            with sc1:
                age    = st.number_input("Age", min_value=1, max_value=100,
                                         value=30, key="sym_age")
                gender = st.selectbox("Gender",
                                      ["Not specified", "Male", "Female"],
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

            # Form submit button — this is the ONLY thing that triggers a rerun
            submitted = st.form_submit_button(
                "🔍 Analyse Symptoms", use_container_width=True
            )

    # ── HANDLE SUBMIT (outside form so loader renders correctly) ───────────
    with col1:
        if submitted:
            all_symptoms = list(selected)
            if custom.strip():
                all_symptoms += [s.strip() for s in custom.split(",") if s.strip()]

            if not all_symptoms:
                st.warning("Please select or enter at least one symptom.")
            else:
                loader_ph = st.empty()
                show_loader(loader_ph, "Analysing symptoms…")

                symptoms_str = ", ".join(all_symptoms)
                context = (
                    f"Patient: {age} year old {gender.lower()}, "
                    f"symptoms for {duration.lower()}, severity: {severity.lower()}"
                )

                result = groq_generate(
                    prompt=_build_prompt(symptoms_str, context),
                    system=_SYSTEM,
                    model="llama-3.1-8b-instant",
                    feature="symptom_checker",
                )

                st.session_state.symptom_result = result
                st.session_state.symptom_list   = all_symptoms
                st.session_state["_sym_last_saved"] = None  # reset dedup guard
                loader_ph.empty()

    # ── RESULTS COLUMN ─────────────────────────────────────────────────────
    with col2:
        st.markdown("### 📋 Analysis Results")

        if st.session_state.get("symptom_result"):
            result       = st.session_state.symptom_result
            result_upper = result.upper()

            if "EMERGENCY" in result_upper:
                st.error("🚨 EMERGENCY — Seek immediate medical help!")
            elif "URGENT" in result_upper:
                st.warning("⚡ URGENT — See a doctor within 24 hours")
            elif "SOON" in result_upper:
                st.info("📅 See a doctor within the week")
            else:
                st.success("✅ Routine — Schedule a doctor visit")

            st.markdown(result)

            # Save history only once per new analysis
            _last_saved  = st.session_state.get("_sym_last_saved")
            _current_key = str(st.session_state.get("symptom_list", []))
            if _last_saved != _current_key:
                _save_symptom_history(
                    st.session_state.get("_sym_user", "user"),
                    st.session_state.symptom_list,
                    result,
                )
                st.session_state["_sym_last_saved"] = _current_key
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

        history = _load_symptom_history(st.session_state.get("_sym_user", "user"))
        if history:
            st.markdown("---")
            st.markdown("**🕐 Recent Checks**")
            for h in history[-3:][::-1]:
                st.markdown(
                    f"<div style='font-size:0.78rem;color:#64748b;padding:0.2rem 0;'>"
                    f"📅 {h['date']} — {', '.join(h['symptoms'][:3])}"
                    f"{'...' if len(h['symptoms']) > 3 else ''}</div>",
                    unsafe_allow_html=True
                )


def _save_symptom_history(username: str, symptoms: list, result: str):
    import pytz
    from datetime import datetime
    ist = pytz.timezone("Asia/Kolkata")
    os.makedirs("symptom_history", exist_ok=True)
    path = f"symptom_history/{username}.json"
    history = []
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            pass
    history.append({
        "date":     datetime.now(ist).strftime("%d %b %Y, %I:%M %p"),
        "symptoms": symptoms,
        "result":   result,
    })
    history = history[-20:]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def _load_symptom_history(username: str) -> list:
    path = f"symptom_history/{username}.json"
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []