
#model insights
import streamlit as st
import pandas as pd
import json, os, joblib

FEATURES = ["Age","BMI","Cholesterol","Blood_pressure","Gender",
            "Glucose_level","Smoking_status","Insulin","Physical_activity"]
DISEASES  = ["Diabetes_Diagnosis","hypertension","cardiovascular","kidney"]
LABELS    = {"Diabetes_Diagnosis":"Diabetes","hypertension":"Hypertension",
             "cardiovascular":"Cardiovascular","kidney":"Kidney Disease"}


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_model_insights(models_dict):
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"],[data-testid="stMain"],
    [data-testid="stVerticalBlock"],.stApp,.main,
    [data-testid="stAppViewBlockContainer"] {
        transition: none !important; animation: none !important;
        backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
        filter: none !important; opacity: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("## 📈 Model Insights")

    tab1, tab2 = st.tabs(["📊 Feature Importance", "🏆 Model Performance"])

    # ── TAB 1: FEATURE IMPORTANCE ─────────────────────────────────────────
    with tab1:
        st.markdown("### 📊 Feature Importance — XGBoost")
        st.caption("Which features matter most for each disease prediction across all patients.")

        disease = st.selectbox("Select Disease", DISEASES,
                               format_func=lambda x: LABELS[x],
                               key="fi_disease")

        model_key = f"{disease}_xgb"
        if model_key in models_dict:
            xgb_model  = models_dict[model_key]
            importance = xgb_model.feature_importances_
            fi_df = pd.DataFrame({
                "Feature":    FEATURES,
                "Importance": importance
            }).sort_values("Importance", ascending=False)

            st.bar_chart(fi_df.set_index("Feature")["Importance"])

            fi_df["Importance %"] = (fi_df["Importance"] * 100).round(2).astype(str) + "%"
            fi_df["Rank"]         = range(1, len(fi_df) + 1)
            st.dataframe(fi_df[["Rank", "Feature", "Importance %"]],
                         hide_index=True, use_container_width=True)

            top = fi_df.iloc[0]["Feature"]
            st.success(f"✅ Most important feature for **{LABELS[disease]}**: **{top}** "
                       f"({fi_df.iloc[0]['Importance']*100:.1f}%)")
        else:
            st.warning(f"Model `{model_key}` not found. Run `train_models.py` first.")

    # ── TAB 2: MODEL PERFORMANCE ──────────────────────────────────────────
    with tab2:
        st.markdown("### 🏆 Saved Model Performance Metrics")
        metrics_path = "models/model_metrics.json"

        if os.path.exists(metrics_path):
            with open(metrics_path, encoding="utf-8") as f:
                metrics = json.load(f)

            st.markdown("#### Classification Models (Disease Risk)")
            for disease, model_metrics in metrics.items():
                if disease == "Glucose_Regression":
                    continue
                st.markdown(f"**{LABELS.get(disease, disease)}**")
                rows = []
                for model_name, m in model_metrics.items():
                    rows.append({
                        "Model":     model_name,
                        "Accuracy":  f"{m['accuracy']*100:.2f}%",
                        "F1 Score":  f"{m['f1']*100:.2f}%",
                        "Precision": f"{m['precision']*100:.2f}%",
                        "Recall":    f"{m['recall']*100:.2f}%",
                    })
                df_m = pd.DataFrame(rows)

                def highlight_best(col):
                    vals = col.str.rstrip("%").astype(float)
                    styles = [""] * len(vals)
                    styles[vals.idxmax()] = \
                        "background-color:#dcfce7;color:#166534;font-weight:bold"
                    return styles

                styled = df_m.style
                for c in ["Accuracy", "F1 Score", "Precision", "Recall"]:
                    styled = styled.apply(highlight_best, subset=[c])
                st.dataframe(styled, hide_index=True, use_container_width=True)
                st.markdown("---")

            if "Glucose_Regression" in metrics:
                st.markdown("#### Glucose Regression Models")
                g_rows = []
                for model_name, m in metrics["Glucose_Regression"].items():
                    g_rows.append({
                        "Model":    model_name,
                        "MAE":      m["MAE"],
                        "R² Score": m["R2"]
                    })
                st.dataframe(pd.DataFrame(g_rows), hide_index=True,
                             use_container_width=True)
        else:
            st.warning("No metrics file found. Run `python train_models.py` to generate metrics.")
            st.info("Metrics will be saved to `models/model_metrics.json` automatically.")