#
# diet_recommender.py
import streamlit as st
import json, os, datetime


def show_diet_recommender(show_loader, load_progress_fn=None,
                          username="user", groq_generate=None):
    st.markdown("## 🍎 Diet & Nutrition Recommender")

    col1, col2 = st.columns([1, 1.4])

    with col1:
        st.markdown("### 👤 Your Profile")

        dc1, dc2 = st.columns(2)
        with dc1:
            age    = st.number_input("Age", 10, 100, 35, key="diet_age")
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0,
                                     step=0.1, key="diet_weight")
        with dc2:
            gender = st.selectbox("Gender", ["Male", "Female"], key="diet_gender")
            height = st.number_input("Height (cm)", 100.0, 220.0, 165.0,
                                     step=0.1, key="diet_height")

        bmi = weight / ((height / 100) ** 2)
        bmi_cat = ("Underweight" if bmi < 18.5 else "Normal" if bmi < 25
                   else "Overweight" if bmi < 30 else "Obese")
        st.info(f"BMI: **{bmi:.1f}** — {bmi_cat}")

        st.markdown("### 🏥 Health Conditions")
        cond_diab  = st.checkbox("Diabetes / Pre-diabetes",  key="diet_diab")
        cond_hyp   = st.checkbox("Hypertension",              key="diet_hyp")
        cond_heart = st.checkbox("Cardiovascular Disease",    key="diet_heart")
        cond_kid   = st.checkbox("Kidney Disease",            key="diet_kid")
        cond_chol  = st.checkbox("High Cholesterol",          key="diet_chol")

        st.markdown("### 🥗 Preferences")
        diet_pref = st.selectbox("Diet Type", [
            "No restriction", "Vegetarian", "Vegan",
            "Non-vegetarian", "Eggetarian"
        ], key="diet_pref")

        cuisine = st.selectbox("Cuisine", [
            "Indian", "South Indian", "North Indian",
            "Mediterranean", "Any"
        ], key="diet_cuisine")

        allergies = st.text_input("Allergies",
                                  placeholder="e.g. nuts, dairy",
                                  key="diet_allergy")

        activity = st.select_slider("Activity Level",
                                    ["Sedentary", "Light", "Moderate", "Active", "Very Active"],
                                    value="Moderate", key="diet_activity")

        goal = st.selectbox("Goal", [
            "Maintain weight", "Lose weight", "Gain weight",
            "Control blood sugar", "Reduce cholesterol",
            "Improve heart health", "Manage kidney health"
        ], key="diet_goal")

        meals = st.slider("Meals per day", 2, 6, 3, key="diet_meals")

        gen_btn = st.button("🍽️ Generate Meal Plan", key="diet_gen", width='stretch')

    with col2:
        if gen_btn:
            conditions = []
            if cond_diab:  conditions.append("Diabetes")
            if cond_hyp:   conditions.append("Hypertension")
            if cond_heart: conditions.append("Heart Disease")
            if cond_kid:   conditions.append("Kidney Disease")
            if cond_chol:  conditions.append("High Cholesterol")

            loader_ph = st.empty()
            show_loader(loader_ph, "Creating your meal plan…")

            cond_str    = ", ".join(conditions) if conditions else "None"
            allergy_str = allergies if allergies else "None"
            snack_line  = "- Snack: one option" if meals >= 4 else ""

            # ── Concise Groq prompt — small, focused, limited response ───
            prompt = f"""Patient: {age}yr {gender}, BMI {bmi:.1f} ({bmi_cat}), Goal: {goal}
Conditions: {cond_str} | Diet: {diet_pref} | Cuisine: {cuisine}
Allergies: {allergy_str} | Activity: {activity}

Give a concise 7-day meal plan. Format exactly:

**Daily Target:** [calories] kcal, [protein]g protein

**Day 1-7** (repeat for each day):
Day N:
- Breakfast: [one meal]
- Lunch: [one meal]
- Dinner: [one meal]
{snack_line}

**Eat More:** [5 foods, comma separated]
**Avoid:** [5 foods, comma separated]
**Tips:** [3 tips, one line each]

Keep each meal to one line. No explanations. No extra text."""

            if groq_generate:
                plan_text = groq_generate(
                    prompt=prompt,
                    system="You are a dietitian. Be concise. Give only what is asked. No extra commentary.",
                    model="llama-3.1-8b-instant"
                )
            else:
                plan_text = "⚠️ Groq API not configured. Check your .env file."

            loader_ph.empty()
            st.session_state.diet_plan = plan_text
            _save_diet_history(username, plan_text)

            # Log API usage
            try:
                from admin_panel import log_api_call
                log_api_call("groq", "diet", not plan_text.startswith("⚠️"))
            except Exception:
                pass

        if st.session_state.get("diet_plan"):
            st.markdown("### 🍽️ Your 7-Day Meal Plan")
            plan_text = st.session_state.diet_plan
            st.download_button(
                "📥 Download (TXT)",
                plan_text.encode("utf-8"),
                "meal_plan.txt",
                "text/plain"
            )
            st.markdown(plan_text)
        else:
            st.markdown("""
            <div style='background:linear-gradient(135deg,#f0fdf4,#dcfce7);
                        border:2px dashed #86efac;border-radius:14px;
                        padding:4rem 1rem;text-align:center;color:#166534;
                        margin-top:2rem;'>
                <div style='font-size:3rem;margin-bottom:0.5rem;'>🍎</div>
                <div style='font-weight:700;font-size:1rem;'>
                    Fill in your profile and click Generate Meal Plan</div>
                <div style='font-size:0.85rem;margin-top:0.3rem;color:#4ade80;'>
                    Get a personalised 7-day meal plan
                </div>
            </div>
            """, unsafe_allow_html=True)


def _save_diet_history(username, plan):
    os.makedirs("diet_history", exist_ok=True)
    path = f"diet_history/{username}.json"
    history = []
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            pass
    history.append({
        "date": datetime.datetime.now().strftime("%d %b %Y"),
        "plan": plan
    })
    history = history[-5:]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)