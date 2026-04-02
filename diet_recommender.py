import streamlit as st
import google.generativeai as genai
import json, os, datetime
from dotenv import load_dotenv; load_dotenv()
import os
API_KEY = os.getenv("GEMINI_API_KEY")


#API_KEY = "AIzaSyDsVEs0hKDmIrN8NY48BwH8bAvfDSnrXrM"

def show_diet_recommender(show_loader, load_progress_fn=None, username="user"):
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
            gender = st.selectbox("Gender", ["Male","Female"], key="diet_gender")
            height = st.number_input("Height (cm)", 100.0, 220.0, 165.0,
                                      step=0.1, key="diet_height")

        bmi = weight / ((height/100)**2)
        bmi_cat = ("Underweight" if bmi < 18.5 else "Normal" if bmi < 25
                   else "Overweight" if bmi < 30 else "Obese")
        st.info(f"BMI: **{bmi:.1f}** — {bmi_cat}")

        st.markdown("### 🏥 Health Conditions")
        cond_diab  = st.checkbox("Diabetes / Pre-diabetes",   key="diet_diab")
        cond_hyp   = st.checkbox("Hypertension",               key="diet_hyp")
        cond_heart = st.checkbox("Cardiovascular Disease",     key="diet_heart")
        cond_kid   = st.checkbox("Kidney Disease",             key="diet_kid")
        cond_chol  = st.checkbox("High Cholesterol",           key="diet_chol")

        st.markdown("### 🥗 Preferences")
        diet_pref = st.selectbox("Diet Type", [
            "No restriction", "Vegetarian", "Vegan",
            "Non-vegetarian", "Eggetarian"
        ], key="diet_pref")

        cuisine = st.selectbox("Cuisine Preference", [
            "Indian", "South Indian", "North Indian",
            "Mediterranean", "Any"
        ], key="diet_cuisine")

        allergies = st.text_input("Food Allergies (if any)",
                                   placeholder="e.g. nuts, dairy, gluten",
                                   key="diet_allergy")

        activity = st.select_slider("Activity Level",
                                     ["Sedentary","Light","Moderate","Active","Very Active"],
                                     value="Moderate", key="diet_activity")

        goal = st.selectbox("Primary Goal", [
            "Maintain weight", "Lose weight", "Gain weight",
            "Control blood sugar", "Reduce cholesterol",
            "Improve heart health", "Manage kidney health"
        ], key="diet_goal")

        meals = st.slider("Meals per day", 2, 6, 3, key="diet_meals")

        gen_btn = st.button("🍽️ Generate Meal Plan", key="diet_gen", width='stretch')

    with col2:
        if gen_btn:
            conditions = []
            if cond_diab:  conditions.append("Diabetes/Pre-diabetes")
            if cond_hyp:   conditions.append("Hypertension")
            if cond_heart: conditions.append("Cardiovascular Disease")
            if cond_kid:   conditions.append("Kidney Disease")
            if cond_chol:  conditions.append("High Cholesterol")

            loader_ph = st.empty()
            show_loader(loader_ph, "Creating your meal plan…")

            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                cond_str = ", ".join(conditions) if conditions else "None"

                prompt = f"""You are a certified nutritionist and dietitian.
Create a personalised 7-day meal plan for:
- Age: {age}, Gender: {gender}, BMI: {bmi:.1f} ({bmi_cat})
- Health conditions: {cond_str}
- Diet type: {diet_pref}, Cuisine: {cuisine}
- Allergies: {allergies if allergies else 'None'}
- Activity: {activity}, Goal: {goal}
- Meals per day: {meals}

Structure your response as:

## 🥗 Nutritional Guidelines
Key targets (calories, macros) for this person.

## 📅 7-Day Meal Plan
For each day (Day 1 to Day 7), list:
- Breakfast
- Lunch
- Dinner
{"- Snack" if meals >= 4 else ""}

Keep meals practical, affordable, and easy to prepare.
Use {cuisine} cuisine where possible.
Strictly avoid: {allergies if allergies else 'nothing specific'}.

## ✅ Foods to Eat More
List 8-10 beneficial foods with brief reasons.

## ❌ Foods to Avoid
List 6-8 foods to avoid with reasons based on conditions.

## 💧 Hydration & Lifestyle Tips
3-4 practical tips.

## 🛒 Weekly Shopping List
Categorised list of ingredients needed."""

                result = model.generate_content(prompt)
                st.session_state.diet_plan = result.text.strip()
            except Exception as e:
                st.session_state.diet_plan = f"Error generating plan: {e}"

            loader_ph.empty()

        if st.session_state.get("diet_plan"):
            st.markdown("### 🍽️ Your Personalised Meal Plan")

            # Download button
            plan_text = st.session_state.diet_plan
            st.download_button(
                "📥 Download Meal Plan (TXT)",
                plan_text.encode("utf-8"),
                "meal_plan.txt",
                "text/plain"
            )

            st.markdown(plan_text)

            # Save history
            _save_diet_history(username, plan_text)
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
        except:
            pass
    history.append({
        "date": datetime.datetime.now().strftime("%d %b %Y"),
        "plan": plan
    })
    history = history[-5:]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)