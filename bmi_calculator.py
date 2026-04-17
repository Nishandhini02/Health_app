



# bmi_calculator.py
import streamlit as st

def show_bmi_calculator(show_loader, groq_generate=None):
    st.markdown("## 📊 BMI & Health Score Calculator")

    st.markdown("""
    <style>
    .grade-card {
        border-radius:16px;padding:1.5rem;text-align:center;
        box-shadow:0 4px 20px rgba(0,0,0,0.10);margin-bottom:1rem;
    }
    .score-ring {
        font-size:3.5rem;font-weight:800;
        background:linear-gradient(135deg,#3b82f6,#8b5cf6);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.markdown("### 📋 Enter Your Details")
        bc1, bc2 = st.columns(2)
        with bc1:
            age    = st.number_input("Age (years)", 10, 100, 30, key="bmi_age")
            weight = st.number_input("Weight (kg)", 20.0, 300.0, 70.0,
                                     step=0.1, key="bmi_weight")
        with bc2:
            gender = st.selectbox("Gender", ["Male", "Female"], key="bmi_gender")
            height = st.number_input("Height (cm)", 100.0, 250.0, 170.0,
                                     step=0.1, key="bmi_height")

        st.markdown("### 🩺 Health Metrics")
        hc1, hc2 = st.columns(2)
        with hc1:
            bp      = st.number_input("Blood Pressure (mmHg)", 40, 120, 70, key="bmi_bp")
            glucose = st.number_input("Glucose (mg/dL)", 40, 400, 90, key="bmi_glucose")
        with hc2:
            chol    = st.number_input("Cholesterol (mg/dL)", 100, 400, 180, key="bmi_chol")
            insulin = st.number_input("Insulin (μU/mL)", 0, 300, 80, key="bmi_insulin")

        activity  = st.select_slider("Physical Activity Level",
                                     ["Sedentary", "Low", "Moderate", "High", "Very High"],
                                     value="Moderate", key="bmi_activity")
        smoking   = st.checkbox("Current / Former Smoker", key="bmi_smoking")
        sleep_hrs = st.slider("Sleep Hours per Night", 3, 12, 7, key="bmi_sleep")
        stress    = st.select_slider("Stress Level",
                                     ["Very Low", "Low", "Moderate", "High", "Very High"],
                                     value="Moderate", key="bmi_stress")

        calc_btn = st.button("📊 Calculate Health Score", key="bmi_calc", width='stretch')

    with col2:
        if calc_btn:
            bmi = weight / ((height / 100) ** 2)

            # ── Scoring system (100 points total) ──────────────────────
            score = 0

            # BMI (25 pts)
            if 18.5 <= bmi < 25:   score += 25
            elif 25 <= bmi < 27:   score += 20
            elif 17 <= bmi < 18.5: score += 18
            elif 27 <= bmi < 30:   score += 14
            elif 15 <= bmi < 17:   score += 10
            else:                  score += 4

            # Blood Pressure (20 pts)
            if bp < 70:            score += 20
            elif bp < 80:          score += 16
            elif bp < 90:          score += 11
            elif bp < 100:         score += 6
            else:                  score += 2

            # Glucose (20 pts)
            if glucose < 100:      score += 20
            elif glucose < 110:    score += 16
            elif glucose < 126:    score += 10
            elif glucose < 160:    score += 5
            else:                  score += 1

            # Cholesterol (10 pts)
            if chol < 170:         score += 10
            elif chol < 200:       score += 8
            elif chol < 240:       score += 5
            else:                  score += 2

            # Activity (10 pts)
            act_map = {"Sedentary": 0, "Low": 3, "Moderate": 6, "High": 9, "Very High": 10}
            score += act_map[activity]

            # Smoking (5 pts)
            if not smoking:        score += 5

            # Sleep (5 pts)
            if 7 <= sleep_hrs <= 9:    score += 5
            elif 6 <= sleep_hrs <= 10: score += 3
            else:                      score += 1

            # Stress (5 pts)
            str_map = {"Very Low": 5, "Low": 4, "Moderate": 3, "High": 1, "Very High": 0}
            score += str_map[stress]

            # Grade
            if score >= 85:   grade, col, emoji = "A", "#059669", "🌟"
            elif score >= 70: grade, col, emoji = "B", "#2563eb", "👍"
            elif score >= 55: grade, col, emoji = "C", "#d97706", "⚠️"
            elif score >= 40: grade, col, emoji = "D", "#dc2626", "🚨"
            else:             grade, col, emoji = "F", "#7f1d1d", "🆘"

            # BMI category
            if bmi < 18.5:        bmi_cat = "Underweight"
            elif bmi < 25:        bmi_cat = "Normal"
            elif bmi < 30:        bmi_cat = "Overweight"
            elif bmi < 35:        bmi_cat = "Obese Class I"
            elif bmi < 40:        bmi_cat = "Obese Class II"
            else:                 bmi_cat = "Obese Class III"

            # Display grade card
            st.markdown("### 🎯 Your Health Score")
            st.markdown(f"""
            <div class='grade-card' style='background:linear-gradient(135deg,
                 {col}18,{col}08);border:2px solid {col}40;'>
                <div style='font-size:0.9rem;color:#64748b;margin-bottom:0.3rem;'>
                    Overall Health Grade</div>
                <div style='font-size:5rem;font-weight:900;color:{col};
                            line-height:1;'>{grade}</div>
                <div class='score-ring'>{score}/100</div>
                <div style='font-size:0.85rem;color:#64748b;margin-top:0.4rem;'>
                    {emoji} {'Excellent' if grade=='A' else 'Good' if grade=='B'
                     else 'Fair' if grade=='C' else 'Poor' if grade=='D' else 'Critical'}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Metrics
            m1, m2 = st.columns(2)
            with m1:
                st.metric("BMI", f"{bmi:.1f}", bmi_cat)
                st.metric("Blood Pressure", f"{bp} mmHg")
            with m2:
                st.metric("Glucose", f"{glucose} mg/dL")
                st.metric("Cholesterol", f"{chol} mg/dL")

            # Score breakdown
            st.markdown("### 📈 Score Breakdown")
            breakdown = {
                "BMI":            (25, min(25, 25 if 18.5<=bmi<25 else 20 if bmi<27
                                           else 18 if bmi<18.5 else 14 if bmi<30
                                           else 10 if bmi<17 else 4)),
                "Blood Pressure": (20, 20 if bp<70 else 16 if bp<80 else 11
                                      if bp<90 else 6 if bp<100 else 2),
                "Glucose":        (20, 20 if glucose<100 else 16 if glucose<110
                                      else 10 if glucose<126 else 5 if glucose<160 else 1),
                "Cholesterol":    (10, 10 if chol<170 else 8 if chol<200
                                      else 5 if chol<240 else 2),
                "Activity":       (10, act_map[activity]),
                "Non-Smoker":     (5,  5 if not smoking else 0),
                "Sleep":          (5,  5 if 7<=sleep_hrs<=9 else 3
                                      if 6<=sleep_hrs<=10 else 1),
                "Stress":         (5,  str_map[stress]),
            }
            for label, (max_pts, pts) in breakdown.items():
                pct = pts / max_pts
                bar_col = ("#059669" if pct >= 0.8 else "#2563eb" if pct >= 0.6
                           else "#d97706" if pct >= 0.4 else "#dc2626")
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:0.6rem;"
                    f"margin-bottom:0.3rem;font-size:0.82rem;'>"
                    f"<span style='width:110px;color:#334155;'>{label}</span>"
                    f"<div style='flex:1;background:#e2e8f0;border-radius:99px;height:10px;'>"
                    f"<div style='width:{pct*100:.0f}%;background:{bar_col};"
                    f"height:10px;border-radius:99px;'></div></div>"
                    f"<span style='color:{bar_col};font-weight:700;width:50px;"
                    f"text-align:right;'>{pts}/{max_pts}</span></div>",
                    unsafe_allow_html=True
                )

            # AI tips via Groq
            st.markdown("### 💡 AI Health Tips")
            loader_ph = st.empty()
            show_loader(loader_ph, "Generating tips…")

            tips = groq_generate(
                prompt=(
                    f"Patient: {age}yr {gender}, BMI={bmi:.1f} ({bmi_cat}), "
                    f"BP={bp}, Glucose={glucose}, Cholesterol={chol}, "
                    f"Activity={activity}, Smoking={smoking}, Sleep={sleep_hrs}h, "
                    f"Stress={stress}, Health Score={score}/100 Grade={grade}."
                ),
                system=(
                    "You are a health advisor. Give 3 specific, actionable health "
                    "improvement tips in bullet points. Be concise and practical. "
                    "Focus on the lowest scoring areas."
                ),
                model="llama-3.1-8b-instant"
            )

            loader_ph.empty()
            st.markdown(tips)

            st.session_state["bmi_result"] = {
                "bmi": bmi, "score": score, "grade": grade
            }

        else:
            st.markdown("""
            <div style='background:#f8faff;border:2px dashed #cbd5e1;
                        border-radius:14px;padding:4rem 1rem;text-align:center;
                        color:#94a3b8;margin-top:2rem;'>
                <div style='font-size:3rem;margin-bottom:0.5rem;'>📊</div>
                <div style='font-weight:600;font-size:1rem;'>
                    Fill in your details and click Calculate</div>
                <div style='font-size:0.85rem;margin-top:0.3rem;'>
                    Get your personalised health grade A–F
                </div>
            </div>
            """, unsafe_allow_html=True)