import streamlit as st
import google.generativeai as genai
import json, os, datetime

#API_KEY = "AIzaSyCpSJySVgy5wXEbIgJJDsBfB1dRNvwE-I8"
API_KEY = os.getenv("GEMINI_API_KEY")
COMMON_DRUGS = [
    "Metformin", "Insulin", "Atorvastatin", "Amlodipine", "Lisinopril",
    "Omeprazole", "Paracetamol", "Ibuprofen", "Aspirin", "Amoxicillin",
    "Azithromycin", "Losartan", "Glibenclamide", "Ramipril", "Furosemide",
    "Atenolol", "Warfarin", "Clopidogrel", "Levothyroxine", "Vitamin D3"
]

def show_medication_info(show_loader, username="user"):
    st.markdown("## 💊 Medication Information & Reminders")

    st.markdown("""
    <div style='background:linear-gradient(135deg,#eff6ff,#dbeafe);
                border-left:4px solid #3b82f6;border-radius:10px;
                padding:0.8rem 1rem;margin-bottom:1.2rem;font-size:0.88rem;color:#1e40af;'>
        ℹ️ <b>Note:</b> This information is for educational purposes only.
        Never start, stop or change medication without consulting your doctor.
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔍 Drug Information", "⏰ Medication Reminders"])

    # ── TAB 1: DRUG INFO ─────────────────────────────────────────────────────
    with tab1:
        col1, col2 = st.columns([1, 1.3])
        with col1:
            st.markdown("### 💊 Search Drug")
            quick = st.selectbox("Quick select common medicines:",
                                  ["Type your own…"] + COMMON_DRUGS,
                                  key="med_quick")
            if quick == "Type your own…":
                drug_name = st.text_input("Enter medicine or drug name:",
                                           placeholder="e.g. Metformin, Paracetamol, Vitamin D",
                                           key="med_input")
            else:
                drug_name = quick

            search_type = st.multiselect(
                "What do you want to know?",
                ["General Info", "Side Effects", "Drug Interactions",
                 "Dosage Guidelines", "Precautions", "Storage"],
                default=["General Info", "Side Effects", "Precautions"],
                key="med_search_type"
            )

            patient_ctx = st.expander("👤 My Health Context (optional)")
            with patient_ctx:
                ctx_age      = st.number_input("Age", 1, 100, 40, key="med_ctx_age")
                ctx_cond     = st.text_input("Health conditions",
                                              placeholder="e.g. diabetes, hypertension",
                                              key="med_ctx_cond")
                ctx_othermeds= st.text_input("Other medications I take",
                                              placeholder="e.g. Aspirin, Lisinopril",
                                              key="med_ctx_meds")

            search_btn = st.button("🔍 Get Drug Info", key="med_search", width='stretch')

        with col2:
            if search_btn and drug_name.strip():
                loader_ph = st.empty()
                show_loader(loader_ph, f"Looking up {drug_name}…")
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    sections = ", ".join(search_type) if search_type else "General Info"
                    ctx_part = ""
                    if ctx_cond or ctx_othermeds:
                        ctx_part = (
                            f"\nPatient context: Age {ctx_age}, "
                            f"Conditions: {ctx_cond or 'none'}, "
                            f"Other medications: {ctx_othermeds or 'none'}. "
                            f"Highlight any specific interactions or precautions for this patient."
                        )

                    prompt = f"""You are a clinical pharmacist providing patient education.
Provide information about: {drug_name}
Sections needed: {sections}
{ctx_part}

Format your response with these sections (only include requested ones):

## 💊 Drug Overview
Generic name, drug class, what it treats.

## ✅ How It Works
Simple explanation of mechanism.

## 📋 Dosage Guidelines
Common doses, timing, with/without food. (Do NOT prescribe — general info only)

## ⚠️ Common Side Effects
List with frequency (common/uncommon/rare).

## 🚨 Serious Side Effects
Symptoms requiring immediate medical attention.

## 🔄 Drug Interactions
Important interactions to be aware of.

## 🚫 Precautions & Contraindications
Who should NOT take this, when to be careful.

## 🗄️ Storage
How to store properly.

## ❓ Patient FAQs
2-3 common questions patients ask about this drug.

Always emphasise consulting a doctor or pharmacist."""

                    result = model.generate_content(prompt)
                    st.session_state.med_info_result = result.text.strip()
                    st.session_state.med_info_name   = drug_name
                except Exception as e:
                    st.session_state.med_info_result = f"Error: {e}"
                loader_ph.empty()

            if st.session_state.get("med_info_result"):
                st.markdown(f"### ℹ️ About: {st.session_state.get('med_info_name','')}")
                # Download
                st.download_button(
                    "📥 Save Drug Info (TXT)",
                    st.session_state.med_info_result.encode("utf-8"),
                    f"{st.session_state.get('med_info_name','drug')}_info.txt",
                    "text/plain"
                )
                st.markdown(st.session_state.med_info_result)
            else:
                st.markdown("""
                <div style='background:#f8faff;border:2px dashed #cbd5e1;
                            border-radius:14px;padding:4rem 1rem;
                            text-align:center;color:#94a3b8;margin-top:1rem;'>
                    <div style='font-size:2.5rem;'>💊</div>
                    <div style='font-weight:600;'>Search for any medication</div>
                    <div style='font-size:0.85rem;margin-top:0.3rem;'>
                        Get detailed, easy-to-understand drug information
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 2: REMINDERS ─────────────────────────────────────────────────────
    with tab2:
        st.markdown("### ⏰ My Medication Schedule")

        reminders = _load_reminders(username)

        # Add new reminder
        with st.expander("➕ Add New Medication Reminder", expanded=not reminders):
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                r_drug = st.text_input("Medication Name", key="r_drug",
                                        placeholder="e.g. Metformin 500mg")
            with rc2:
                r_dose = st.text_input("Dose", key="r_dose",
                                        placeholder="e.g. 1 tablet")
            with rc3:
                r_freq = st.selectbox("Frequency", [
                    "Once daily", "Twice daily", "Three times daily",
                    "Every 8 hours", "Every 12 hours",
                    "Before meals", "After meals", "At bedtime", "As needed"
                ], key="r_freq")

            rc4, rc5 = st.columns(2)
            with rc4:
                r_time = st.time_input("Reminder Time", key="r_time")
            with rc5:
                r_notes = st.text_input("Notes", key="r_notes",
                                         placeholder="e.g. take with water")

            if st.button("💾 Save Reminder", key="r_save"):
                if r_drug.strip():
                    new_rem = {
                        "id":    datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
                        "drug":  r_drug.strip(),
                        "dose":  r_dose.strip(),
                        "freq":  r_freq,
                        "time":  str(r_time),
                        "notes": r_notes.strip(),
                        "added": datetime.datetime.now().strftime("%d %b %Y")
                    }
                    reminders.append(new_rem)
                    _save_reminders(username, reminders)
                    st.success(f"✅ Reminder added for {r_drug}")
                    st.rerun()
                else:
                    st.warning("Please enter a medication name.")

        # Show existing reminders
        if reminders:
            st.markdown(f"**You have {len(reminders)} medication(s) scheduled:**")
            for rem in reminders:
                freq_emoji = {
                    "Once daily": "🌅", "Twice daily": "🌗",
                    "Three times daily": "🔄", "Every 8 hours": "🔄",
                    "Every 12 hours": "🌗", "Before meals": "🍽",
                    "After meals": "🍽", "At bedtime": "🌙", "As needed": "❓"
                }.get(rem["freq"], "⏰")

                with st.container():
                    col_r, col_del = st.columns([10, 1])
                    with col_r:
                        st.markdown(
                            "<div style='background:white;border:1px solid #e2e8f0;"
                            "border-left:4px solid #3b82f6;border-radius:10px;"
                            "padding:0.8rem 1rem;margin-bottom:0.4rem;'>"
                            "<b style='color:#1e3a5f;font-size:0.95rem;'>💊 "
                            + rem['drug'] +
                            "</b>&nbsp;&nbsp;<span style='color:#64748b;font-size:0.82rem;'>"
                            + rem.get('dose', '') +
                            "</span><br>"
                            "<span style='color:#3b82f6;font-size:0.82rem;font-weight:600;'>"
                            "⏰ " + rem['time'] +
                            "</span>&nbsp;&nbsp;"
                            "<span style='color:#64748b;font-size:0.8rem;'>"
                            + freq_emoji + " " + rem['freq'] +
                            ("  |  " + rem['notes'] if rem.get('notes') else "") +
                            "</span><br>"
                            "<span style='color:#94a3b8;font-size:0.72rem;'>Added: "
                            + rem.get('added', '') +
                            "</span></div>",
                            unsafe_allow_html=True
                        )
                    with col_del:
                        if st.button("🗑", key=f"del_rem_{rem['id']}",
                                     help="Delete this reminder"):
                            reminders = [r for r in reminders if r["id"] != rem["id"]]
                            _save_reminders(username, reminders)
                            st.rerun()
        else:
            st.markdown("""
            <div style='background:#f8faff;border:2px dashed #cbd5e1;
                        border-radius:14px;padding:2rem;text-align:center;
                        color:#94a3b8;'>
                <div style='font-size:2rem;'>⏰</div>
                <div style='font-weight:600;'>No reminders added yet</div>
                <div style='font-size:0.85rem;'>
                    Use the form above to add your medications
                </div>
            </div>
            """, unsafe_allow_html=True)

def _load_reminders(username):
    os.makedirs("med_reminders", exist_ok=True)
    path = f"med_reminders/{username}.json"
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f: return json.load(f)
        except: pass
    return []

def _save_reminders(username, reminders):
    os.makedirs("med_reminders", exist_ok=True)
    with open(f"med_reminders/{username}.json", "w", encoding="utf-8") as f:
        json.dump(reminders, f, indent=2, ensure_ascii=False)