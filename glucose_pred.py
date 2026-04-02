# glucose_pred.py
"""
Future Glucose Prediction.

FIX: The trend chart now starts at the user's CURRENT age and projects
     forward in 5-year steps up to age 80 (or age+5 minimum if already
     close to 80). Past ages are never shown — only future projections.
"""
import streamlit as st
import pandas as pd


def show_glucose_prediction(glucose_model, glucose_scaler):

    st.markdown("## 🔬 Future Glucose Prediction")
    st.caption(
        "Enter your current health details below. "
        "The chart will project how your glucose level may change "
        "**from your current age onwards**."
    )

    with st.form("glucose_form"):
        c1, c2, c3 = st.columns(3)
        age     = c1.number_input("Age",            min_value=1,    max_value=120,  value=30)
        bmi     = c2.number_input("BMI",            min_value=10.0, max_value=60.0, value=25.0)
        chol    = c3.number_input("Cholesterol",    min_value=50,   max_value=400,  value=180)

        c4, c5, c6 = st.columns(3)
        bp      = c4.number_input("Blood Pressure", min_value=40,   max_value=200,  value=80)
        insulin = c5.number_input("Insulin",        min_value=0,    max_value=300,  value=80)
        gender  = c6.selectbox("Gender", ["Male", "Female"], key="gluc_gender")

        c7, c8, c9 = st.columns(3)
        smoking  = c7.selectbox("Smoking Status",    ["Never", "Former", "Current"], key="gluc_smoking")
        activity = c8.selectbox("Physical Activity", ["Low", "Moderate", "High"],    key="gluc_activity")
        diabetes = c9.selectbox("Diabetes Diagnosis", ["No", "Yes"],                 key="gluc_diabetes")

        submit = st.form_submit_button("🔮 Predict Future Glucose")

    if not submit:
        return

    # ── Encode ────────────────────────────────────────────────────────────
    se = {"Never": 0, "Former": 1, "Current": 2}[smoking]
    ae = {"Low": 0, "Moderate": 1, "High": 2}[activity]
    ge = 1 if gender == "Male" else 0
    de = 1 if diabetes == "Yes" else 0

    # Column order must match training (Glucose_level excluded — it's the target)
    glucose_cols = [
        "Age", "BMI", "Cholesterol", "Blood_pressure",
        "Gender", "Smoking_status", "Insulin",
        "Physical_activity", "Diabetes_Diagnosis"
    ]

    # ── Current prediction ────────────────────────────────────────────────
    current_row = pd.DataFrame(
        [[age, bmi, chol, bp, ge, se, insulin, ae, de]],
        columns=glucose_cols
    )
    pred_now = glucose_model.predict(glucose_scaler.transform(current_row))[0]

    st.success(
        f" Predicted Glucose at your current age **{age}**: "
        f"**{pred_now:.2f} mg/dL**"
    )

    # ── Risk label for current value ──────────────────────────────────────
    if pred_now >= 126:
        st.error("🔴 Current level falls in the **Diabetic** range (≥ 126 mg/dL).")
    elif pred_now >= 100:
        st.warning("🟡 Current level falls in the **Pre-diabetic** range (100–125 mg/dL).")
    else:
        st.success("🟢 Current level is in the **Normal** range (< 100 mg/dL).")

    # ── Future projection — starts at current age, steps of 5 up to 80 ───
    # Build age checkpoints: current age, then next multiples of 5, up to 80.
    # Always include at least 5 future points so the chart is meaningful.
    start_age = int(age)
    max_age   = max(80, start_age + 20)   # if user is already older than 80

    # Round up to the next 5-year boundary after current age
    next_5 = start_age if start_age % 5 == 0 else start_age + (5 - start_age % 5)
    future_ages = [start_age] + list(range(next_5 + 5, max_age + 1, 5))

    # De-duplicate and sort
    future_ages = sorted(set(future_ages))

    results = []
    for a in future_ages:
        row = pd.DataFrame(
            [[a, bmi, chol, bp, ge, se, insulin, ae, de]],
            columns=glucose_cols
        )
        g = glucose_model.predict(glucose_scaler.transform(row))[0]
        label = (
            "🔴 Diabetic"     if g >= 126 else
            "🟡 Pre-diabetic" if g >= 100 else
            "🟢 Normal"
        )
        results.append({
            "Age": a,
            "Predicted Glucose (mg/dL)": round(float(g), 2),
            "Status": label,
        })

    df = pd.DataFrame(results)

    st.markdown("#### 📈 Projected Glucose — From Now Into the Future")
    st.caption(
        f"Showing projection from **Age {start_age}** (today) "
        f"to **Age {future_ages[-1]}**, all other factors held constant."
    )

    tab_chart, tab_table = st.tabs(["📊 Chart", "📋 Table"])

    with tab_chart:
        # Separate series so the chart can colour-code risk zones
        chart_df = df.set_index("Age")[["Predicted Glucose (mg/dL)"]]

        # Reference lines (drawn as extra series)
        chart_df["Normal Limit (100)"]    = 100
        chart_df["Diabetic Limit (126)"]  = 126

        st.line_chart(chart_df)
        st.caption(
            "🟢 Below 100 = Normal &nbsp;|&nbsp; "
            "🟡 100–125 = Pre-diabetic &nbsp;|&nbsp; "
            "🔴 ≥ 126 = Diabetic"
        )

    with tab_table:
        def colour_row(row):
            g = row["Predicted Glucose (mg/dL)"]
            if g >= 126:
                return ["background-color:#fee2e2;color:#991b1b"] * len(row)
            elif g >= 100:
                return ["background-color:#fef9c3;color:#854d0e"] * len(row)
            return ["background-color:#dcfce7;color:#166534"] * len(row)

        st.dataframe(
            df.style.apply(colour_row, axis=1),
            use_container_width=True,
            hide_index=True,
        )
        st.caption("🟢 Normal (<100)  🟡 Pre-diabetic (100–125)  🔴 Diabetic (≥126)")

    # ── Trend insight ─────────────────────────────────────────────────────
    if len(df) >= 2:
        first_g = df.iloc[0]["Predicted Glucose (mg/dL)"]
        last_g  = df.iloc[-1]["Predicted Glucose (mg/dL)"]
        delta   = last_g - first_g
        trend   = "📈 rising" if delta > 2 else ("📉 falling" if delta < -2 else "➡️ stable")
        st.info(
            f"**Trend:** Your projected glucose is **{trend}** over the next "
            f"{future_ages[-1] - start_age} years "
            f"({first_g:.1f} → {last_g:.1f} mg/dL)."
        )