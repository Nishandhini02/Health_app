# import streamlit as st
# import numpy as np
# import joblib
# import pandas as pd
# import base64
# import os
# import tempfile
# import io
# import uuid
# import datetime
# import json
# import pytesseract
# from PIL import Image
# import google.generativeai as genai
# from deep_translator import GoogleTranslator
# from auth import login_user, register_user
# from rag_chatbot import create_rag

# from reportlab.platypus import (
#     SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
# )
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import mm
# from reportlab.lib.enums import TA_CENTER


# import os
# import warnings

# # Suppress warnings from the environment
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
# warnings.filterwarnings("ignore", category=UserWarning, module='transformers')

# # ─────────────────────────────────────────────────────────────────────────────
# # PAGE CONFIG
# # ─────────────────────────────────────────────────────────────────────────────
# st.set_page_config(page_title="MediAI Connect", layout="wide", page_icon="🏥")

# # ─────────────────────────────────────────────────────────────────────────────
# # BLUR FIX — aggressive CSS + JS, kills all Streamlit rerun blur
# # ─────────────────────────────────────────────────────────────────────────────
# st.markdown("""
# <style>
# *, *::before, *::after {
#     backdrop-filter: none !important;
#     -webkit-backdrop-filter: none !important;
# }
# [data-testid="stAppViewContainer"]::before,
# [data-testid="stAppViewContainer"]::after,
# .stApp::before, .stApp::after,
# body::before, body::after {
#     backdrop-filter: none !important;
#     -webkit-backdrop-filter: none !important;
#     filter: none !important;
#     display: none !important;
# }
# .stApp,
# [data-testid="stAppViewContainer"],
# [data-testid="stMain"],
# [data-testid="stVerticalBlock"],
# [data-testid="stAppViewBlockContainer"] {
#     backdrop-filter: none !important;
#     -webkit-backdrop-filter: none !important;
#     filter: none !important;
#     transition: none !important;
#     animation: none !important;
# }
# [data-baseweb="popover"], [data-baseweb="popover"] *,
# [data-baseweb="menu"], [data-baseweb="menu"] *,
# [data-baseweb="select"], [data-baseweb="select"] *,
# [role="listbox"], [role="option"],
# [data-baseweb="base-input"], [data-baseweb="base-input"] * {
#     backdrop-filter: none !important;
#     -webkit-backdrop-filter: none !important;
#     filter: none !important;
#     transition: none !important;
# }
# [data-testid="stStatusWidget"],
# [data-testid="stDecoration"],
# [data-testid="stHeader"],
# div[class*="overlay"], div[class*="Overlay"] {
#     backdrop-filter: none !important;
#     -webkit-backdrop-filter: none !important;
#     filter: none !important;
#     animation: none !important;
# }
# div[style*="backdrop-filter"], div[style*="backdropFilter"],
# div[style*="blur("], span[style*="blur("] {
#     backdrop-filter: none !important;
#     -webkit-backdrop-filter: none !important;
#     filter: none !important;
# }
# </style>
# <script>
# (function() {
#     function killBlur(el) {
#         if (!el || !el.style) return;
#         var s = el.style;
#         if (s.backdropFilter)       s.backdropFilter = 'none';
#         if (s.webkitBackdropFilter) s.webkitBackdropFilter = 'none';
#         if (s.filter && s.filter.indexOf('blur') > -1) s.filter = 'none';
#         if (s.transition && (s.transition.indexOf('filter') > -1 ||
#             s.transition.indexOf('backdrop') > -1)) s.transition = 'none';
#     }
#     function scanAll() { document.querySelectorAll('*').forEach(killBlur); }
#     scanAll();
#     new MutationObserver(function(muts) {
#         muts.forEach(function(m) {
#             killBlur(m.target);
#             m.addedNodes.forEach(function(n) {
#                 if (n.nodeType === 1) {
#                     killBlur(n);
#                     if (n.querySelectorAll) n.querySelectorAll('*').forEach(killBlur);
#                 }
#             });
#         });
#     }).observe(document.documentElement, {
#         childList: true, subtree: true,
#         attributes: true, attributeFilter: ['style', 'class']
#     });
#     ['mousedown','mouseup','click','keydown','keyup',
#      'focus','change','input','pointerdown'].forEach(function(ev) {
#         document.addEventListener(ev, scanAll, true);
#     });
#     setInterval(scanAll, 30);
# })();
# </script>
# """, unsafe_allow_html=True)

# # ─────────────────────────────────────────────────────────────────────────────
# # GLOBAL CSS
# # ─────────────────────────────────────────────────────────────────────────────
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Playfair+Display:wght@600;700&display=swap');

# html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

# /* ── Blur fix is handled in the dedicated block above global CSS ── */

# .stTextInput input,
# .stNumberInput input,
# .stPasswordInput input {
#     background-color: #ffffff !important;
#     border: 1.5px solid #d1d9e6 !important;
#     border-radius: 8px !important;
#     color: #1a1a2e !important;
#     box-shadow: none !important;
#     backdrop-filter: none !important;
#     -webkit-backdrop-filter: none !important;
# }
# .stTextInput input:focus,
# .stNumberInput input:focus,
# .stPasswordInput input:focus {
#     border-color: #3b82f6 !important;
#     box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
#     background-color: #ffffff !important;
#     backdrop-filter: none !important;
#     -webkit-backdrop-filter: none !important;
#     outline: none !important;
# }

# /* ── App background ─────────────────────────────────────────────────────── */
# .stApp { background: linear-gradient(135deg,#f0f4ff 0%,#fafbff 60%,#eef2ff 100%); }

# /* ── Sidebar ─────────────────────────────────────────────────────────────── */
# [data-testid="stSidebar"] {
#     background: linear-gradient(180deg,#1a1a2e 0%,#16213e 60%,#0f3460 100%);
#     border-right: none;
# }
# [data-testid="stSidebar"],
# [data-testid="stSidebar"] label,
# [data-testid="stSidebar"] p,
# [data-testid="stSidebar"] span,
# [data-testid="stSidebar"] div { color: #e2e8f0 !important; }
# [data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
#     background: rgba(59,130,246,0.18) !important;
#     border: 1.5px solid rgba(59,130,246,0.45) !important;
#     border-radius: 10px !important;
#     color: #93c5fd !important;
#     font-weight: 600 !important;
# }
# [data-testid="stSidebar"] [data-baseweb="select"] svg { color:#93c5fd !important; fill:#93c5fd !important; }
# [data-testid="stSidebar"] [role="listbox"],
# [data-testid="stSidebar"] [role="option"] { background:#16213e !important; color:#e2e8f0 !important; }
# [data-testid="stSidebar"] [role="option"]:hover,
# [data-testid="stSidebar"] [aria-selected="true"] { background:rgba(59,130,246,0.25) !important; color:#60a5fa !important; }
# [data-testid="stSidebar"] .stButton > button {
#     background: rgba(239,68,68,0.15) !important;
#     border: 1px solid rgba(239,68,68,0.4) !important;
#     color: #fca5a5 !important;
#     border-radius: 10px;
# }
# [data-testid="stSidebar"] .stButton > button:hover {
#     background: rgba(239,68,68,0.28) !important; border-color:#ef4444 !important;
# }

# /* ── Buttons ─────────────────────────────────────────────────────────────── */
# .stButton > button {
#     background: linear-gradient(135deg,#3b82f6,#2563eb);
#     color: white !important; border: none; border-radius: 10px;
#     padding: 0.55rem 1.6rem; font-weight: 600;
#     transition: all 0.2s ease; box-shadow: 0 4px 14px rgba(59,130,246,0.35);
# }
# .stButton > button:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(59,130,246,0.45); }
# [data-testid="stFormSubmitButton"] > button {
#     background: linear-gradient(135deg,#10b981,#059669);
#     width:100%; padding:0.65rem; font-size:1rem;
#     box-shadow:0 4px 14px rgba(16,185,129,0.35);
# }
# [data-testid="stFormSubmitButton"] > button:hover {
#     box-shadow:0 6px 20px rgba(16,185,129,0.45); transform:translateY(-2px);
# }
# [data-testid="stDownloadButton"] > button {
#     background: linear-gradient(135deg,#8b5cf6,#6d28d9) !important;
#     color:white !important; border:none !important; border-radius:10px !important;
#     font-weight:600 !important; box-shadow:0 4px 14px rgba(139,92,246,0.35) !important;
# }
# [data-testid="stDownloadButton"] > button:hover {
#     box-shadow:0 6px 20px rgba(139,92,246,0.45) !important; transform:translateY(-2px) !important;
# }

# /* ── Misc ────────────────────────────────────────────────────────────────── */
# .stProgress > div > div { background:linear-gradient(90deg,#3b82f6,#8b5cf6); border-radius:99px; }
# [data-testid="stMetric"] {
#     background:white; border-radius:14px; padding:1rem 1.2rem;
#     box-shadow:0 2px 12px rgba(0,0,0,0.07); border:1px solid #e8edf5;
# }
# h1 { font-family:'Playfair Display',serif !important; color:#1a1a2e !important; }
# h2, h3 { color:#1e3a5f !important; font-weight:600 !important; }
# .stAlert { border-radius:12px !important; border-left-width:4px !important; }
# [data-testid="stChatMessage"] {
#     border-radius:14px !important; background:white !important;
#     box-shadow:0 2px 10px rgba(0,0,0,0.06) !important; margin-bottom:0.5rem !important;
# }
# div[data-testid="stStatusWidget"] { display:none !important; }
# [data-testid="stSpinner"] { display:none !important; }
# [data-testid="stDataFrame"] { border-radius:12px; overflow:hidden; }

# /* ── Login card ──────────────────────────────────────────────────────────── */
# .login-card {
#     max-width:460px; margin:2rem auto; background:white; border-radius:24px;
#     padding:2.8rem 2.5rem;
#     box-shadow:0 20px 60px rgba(0,0,0,0.10),0 4px 16px rgba(59,130,246,0.08);
#     border:1px solid #e8edf5;
# }
# .login-logo { text-align:center; margin-bottom:0.4rem; font-size:3rem; }
# .login-title {
#     text-align:center; font-family:'Playfair Display',serif;
#     font-size:1.8rem; font-weight:700; color:#1a1a2e; margin-bottom:0.2rem;
# }
# .login-subtitle { text-align:center; color:#64748b; font-size:0.9rem; margin-bottom:1.6rem; }
# .rule-box {
#     background:#f8faff; border:1px solid #dbeafe; border-radius:10px;
#     padding:0.8rem 1rem; margin-bottom:1rem; font-size:0.82rem;
#     color:#3b5988; line-height:1.7;
# }

# /* ── Chatbot history panel ───────────────────────────────────────────────── */
# .hist-box-anchor { display:none; }
# div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .stButton > button {
#     background: transparent !important;
#     border: none !important;
#     box-shadow: none !important;
#     color: #94a3b8 !important;
#     font-size: 0.82rem !important;
#     font-weight: 400 !important;
#     text-align: left !important;
#     justify-content: flex-start !important;
#     padding: 0.45rem 0.9rem !important;
#     border-radius: 0 !important;
#     width: 100% !important;
#     border-bottom: 1px solid rgba(255,255,255,0.04) !important;
#     transition: background 0.12s, color 0.12s !important;
# }
# div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .stButton > button:hover {
#     background: rgba(255,255,255,0.05) !important; color: #e2e8f0 !important;
# }
# div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .active-btn .stButton > button {
#     background: rgba(59,130,246,0.18) !important;
#     border-left: 3px solid #3b82f6 !important;
#     color: #93c5fd !important; font-weight: 500 !important;
# }
# div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .del-btn .stButton > button {
#     background: transparent !important; border: none !important;
#     border-bottom: none !important; color: #334155 !important;
#     font-size: 0.7rem !important; padding: 0.3rem 0.4rem !important; width: auto !important;
# }
# div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .del-btn .stButton > button:hover {
#     background: rgba(239,68,68,0.15) !important; color: #fca5a5 !important;
# }
# div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .action-btn .stButton > button {
#     background: rgba(59,130,246,0.15) !important;
#     border: 1px solid rgba(59,130,246,0.3) !important;
#     border-radius: 8px !important; color: #60a5fa !important;
#     font-size: 0.75rem !important; font-weight: 600 !important;
#     padding: 0.3rem 0.7rem !important; width: auto !important;
#     text-align: center !important; justify-content: center !important;
# }
# div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .clear-btn .stButton > button {
#     background: rgba(239,68,68,0.1) !important;
#     border: 1px solid rgba(239,68,68,0.25) !important;
#     border-radius: 8px !important; color: #fca5a5 !important;
#     font-size: 0.75rem !important; font-weight: 600 !important;
#     padding: 0.3rem 0.7rem !important; width: auto !important;
#     text-align: center !important; justify-content: center !important;
# }
# .chat-win-hdr {
#     background: #f8faff; border: 1px solid #e2e8f0;
#     border-radius: 12px 12px 0 0; padding: 0.75rem 1rem;
#     font-weight: 600; color: #1e3a5f; font-size: 0.92rem;
# }
# </style>
# """, unsafe_allow_html=True)

# # ─────────────────────────────────────────────────────────────────────────────
# # TESSERACT CONFIG — uses local system install (as-is from user's machine)
# # ─────────────────────────────────────────────────────────────────────────────
# tempfile.tempdir = "D:/temp"
# if not os.path.exists("D:/temp"):
#     os.makedirs("D:/temp")

# # Fix: use the actual path where Tesseract is installed on this machine
# pytesseract.pytesseract.tesseract_cmd = (
#     r"C:\Users\nishandhini.ravi\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
# )
# os.environ["TESSDATA_PREFIX"] = (
#     r"C:\Users\nishandhini.ravi\AppData\Local\Programs\Tesseract-OCR\tessdata"
# )

# # ─────────────────────────────────────────────────────────────────────────────
# # API CONFIG — cached to prevent reload on every rerun (fixes blur/freeze)
# # ─────────────────────────────────────────────────────────────────────────────
# API_KEY = "AIzaSyCpSJySVgy5wXEbIgJJDsBfB1dRNvwE-I8"
# genai.configure(api_key=API_KEY)

# @st.cache_resource
# def load_rag():
#     return create_rag(API_KEY)

# def _pick_best_model(disease_key: str, disease_col: str):
#     """
#     Reads model_metrics.json and loads the model with highest accuracy
#     for the given disease. Falls back to XGBoost if metrics not found.
#     """
#     metrics_path = "models/model_metrics.json"
#     model_file_map = {
#         "LogisticRegression": f"models/{disease_col}_logreg.pkl",
#         "RandomForest":       f"models/{disease_col}_rf.pkl",
#         "XGBoost":            f"models/{disease_col}_xgb.pkl",
#         "MLP_NeuralNetwork":  f"models/{disease_col}_mlp.pkl",
#     }

#     best_name = "XGBoost"  # default
#     best_acc  = 0.0

#     if os.path.exists(metrics_path):
#         try:
#             with open(metrics_path, "r", encoding="utf-8") as f:
#                 metrics = json.load(f)
#             if disease_col in metrics:
#                 for model_name, m in metrics[disease_col].items():
#                     # Only consider models that have a saved .pkl file
#                     if model_name in model_file_map:
#                         if m.get("accuracy", 0) > best_acc:
#                             best_acc  = m["accuracy"]
#                             best_name = model_name
#         except Exception:
#             pass

#     model_path = model_file_map.get(best_name, f"models/{disease_col}_xgb.pkl")

#     # Special handling for TF/TabNet if they were saved and have metrics
#     tf_path = f"models/{disease_col}_tf_mlp.keras"
#     tn_path = f"models/{disease_col}_tabnet.zip"
#     if os.path.exists(metrics_path):
#         try:
#             with open(metrics_path, "r", encoding="utf-8") as f:
#                 metrics = json.load(f)
#             if disease_col in metrics:
#                 for model_name, m in metrics[disease_col].items():
#                     if model_name == "TF_MLP" and os.path.exists(tf_path):
#                         if m.get("accuracy", 0) > best_acc:
#                             best_acc  = m["accuracy"]
#                             best_name = "TF_MLP"
#                             model_path = tf_path
#                     if model_name == "TabNet" and os.path.exists(tn_path):
#                         if m.get("accuracy", 0) > best_acc:
#                             best_acc  = m["accuracy"]
#                             best_name = "TabNet"
#                             model_path = tn_path
#         except Exception:
#             pass

#     # Load the selected model
#     try:
#         if best_name == "TF_MLP":
#             import tensorflow as tf
#             model = tf.keras.models.load_model(model_path)
#         elif best_name == "TabNet":
#             from pytorch_tabnet.tab_model import TabNetClassifier
#             model = TabNetClassifier()
#             model.load_model(tn_path)
#         else:
#             model = joblib.load(model_path)
#         print(f"✅ {disease_key}: using {best_name} (acc={best_acc:.4f}) from {model_path}")
#         return model, best_name
#     except Exception as e:
#         print(f"⚠️ Could not load {best_name} for {disease_key}: {e}. Falling back to XGBoost.")
#         return joblib.load(f"models/{disease_col}_xgb.pkl"), "XGBoost"


# @st.cache_resource
# def load_ml_models():
#     diabetes_model, diabetes_best  = _pick_best_model("diabetes",     "Diabetes_Diagnosis")
#     hyper_model,    hyper_best     = _pick_best_model("hypertension",  "hypertension")
#     cardio_model,   cardio_best    = _pick_best_model("cardio",        "cardiovascular")
#     kidney_model,   kidney_best    = _pick_best_model("kidney",        "kidney")

#     # Store best model names for display
#     st.session_state["best_models"] = {
#         "Diabetes":       diabetes_best,
#         "Hypertension":   hyper_best,
#         "Cardiovascular": cardio_best,
#         "Kidney":         kidney_best,
#     }

#     return {
#         "scaler":       joblib.load("models/scaler.pkl"),
#         "diabetes":     diabetes_model,
#         "hypertension": hyper_model,
#         "cardio":       cardio_model,
#         "kidney":       kidney_model,
#         "glucose":      joblib.load("models/glucose_regression.pkl"),
#         "glucose_sc":   joblib.load("models/glucose_scaler.pkl"),
#     }


# qa             = load_rag()
# _m             = load_ml_models()
# scaler             = _m["scaler"]
# diabetes_model     = _m["diabetes"]
# hypertension_model = _m["hypertension"]
# cardio_model       = _m["cardio"]
# kidney_model       = _m["kidney"]
# glucose_model      = _m["glucose"]
# glucose_scaler     = _m["glucose_sc"]

# # ─────────────────────────────────────────────────────────────────────────────
# # GIF LOADER
# # ─────────────────────────────────────────────────────────────────────────────
# _GIF_PATH = "assets/loading.gif"

# def _gif_b64() -> str:
#     if os.path.exists(_GIF_PATH):
#         with open(_GIF_PATH, "rb") as f:
#             return base64.b64encode(f.read()).decode()
#     return ""

# def show_loader(placeholder, message: str = "Processing…"):
#     b64 = _gif_b64()
#     if b64:
#         placeholder.markdown(f"""
#         <div style="display:flex;flex-direction:column;align-items:center;
#                     justify-content:center;gap:0.7rem;padding:1.5rem 0;background:transparent;">
#             <img src="data:image/gif;base64,{b64}" width="72"
#                  style="border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.10);">
#             <p style="font-size:0.9rem;color:#1e3a5f;font-weight:600;margin:0;">{message}</p>
#         </div>
#         """, unsafe_allow_html=True)
#     else:
#         placeholder.info(f"⏳ {message}")

# # ─────────────────────────────────────────────────────────────────────────────
# # HELPERS
# # ─────────────────────────────────────────────────────────────────────────────
# def translate_text(text: str, language: str) -> str:
#     lang_codes = {
#         "English":"en","Tamil":"ta","Hindi":"hi","Telugu":"te",
#         "Malayalam":"ml","Kannada":"kn","Bengali":"bn","Marathi":"mr",
#         "Gujarati":"gu","Urdu":"ur"
#     }
#     return GoogleTranslator(source="auto", target=lang_codes[language]).translate(text)

# def generate_ai_health_summary(age, bmi, glucose, diabetes, hyper, cardio, kidney) -> str:
#     model = genai.GenerativeModel("gemini-2.5-flash")
#     prompt = f"""You are a medical assistant.
# Patient: Age {age}, BMI {bmi}, Glucose {glucose}
# Risks: Diabetes {diabetes:.2f}, Hypertension {hyper:.2f},
#        Cardiovascular {cardio:.2f}, Kidney {kidney:.2f}
# 1. Explain each risk simply  2. Identify most dangerous
# 3. Give lifestyle suggestions  4. Keep it short and clear"""
#     return model.generate_content(prompt).text

# # ─────────────────────────────────────────────────────────────────────────────
# # PDF HELPERS
# # ─────────────────────────────────────────────────────────────────────────────
# def create_disease_pdf(age, bmi, glucose, diabetes_pct, hyper_pct,
#                         cardio_pct, kidney_pct, ai_summary: str) -> bytes:
#     buf = io.BytesIO()
#     doc = SimpleDocTemplate(buf, pagesize=A4,
#                             leftMargin=20*mm, rightMargin=20*mm,
#                             topMargin=18*mm, bottomMargin=18*mm)
#     styles = getSampleStyleSheet()
#     title_s = ParagraphStyle("T", parent=styles["Title"], fontName="Helvetica-Bold",
#                               fontSize=18, textColor=colors.HexColor("#1e3a5f"),
#                               alignment=TA_CENTER, spaceAfter=4)
#     sub_s   = ParagraphStyle("S", parent=styles["Normal"], fontName="Helvetica",
#                               fontSize=10, textColor=colors.HexColor("#64748b"),
#                               alignment=TA_CENTER, spaceAfter=14)
#     sec_s   = ParagraphStyle("Se", parent=styles["Normal"], fontName="Helvetica-Bold",
#                               fontSize=12, textColor=colors.HexColor("#1e3a5f"),
#                               spaceBefore=12, spaceAfter=6)
#     body_s  = ParagraphStyle("B", parent=styles["Normal"], fontName="Helvetica",
#                               fontSize=10, textColor=colors.HexColor("#334155"),
#                               leading=16, spaceAfter=4)
#     foot_s  = ParagraphStyle("F", parent=styles["Normal"], fontName="Helvetica",
#                               fontSize=8, textColor=colors.HexColor("#94a3b8"),
#                               alignment=TA_CENTER)

#     def risk_colour(pct):
#         if pct >= 70: return colors.HexColor("#fee2e2")
#         if pct >= 40: return colors.HexColor("#fef9c3")
#         return colors.HexColor("#dcfce7")

#     story = [
#         Paragraph("MediAI Connect", title_s),
#         Paragraph("Disease Risk Prediction Report", sub_s),
#         HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3b82f6"), spaceAfter=12),
#         Paragraph("Patient Details", sec_s),
#     ]
#     pt = Table([["Age", str(age), "BMI", f"{bmi:.1f}"],
#                 ["Glucose", f"{glucose} mg/dL", "", ""]],
#                colWidths=[40*mm, 55*mm, 40*mm, 35*mm])
#     pt.setStyle(TableStyle([
#         ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#eff6ff")),
#         ("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#1e3a5f")),
#         ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
#         ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
#         ("FONTSIZE",(0,0),(-1,-1),10),
#         ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#dbeafe")),
#         ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
#         ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
#     ]))
#     story.append(pt)
#     story.append(Spacer(1,10))
#     story.append(Paragraph("Predicted Risk Levels", sec_s))
#     risks = [("Diabetes", diabetes_pct), ("Hypertension", hyper_pct),
#              ("Cardiovascular", cardio_pct), ("Kidney Disease", kidney_pct)]
#     rt_data = [["Condition","Risk (%)","Level"]]
#     for lbl, pct in risks:
#         rt_data.append([lbl, f"{pct:.1f}%",
#                         "High" if pct>=70 else ("Moderate" if pct>=40 else "Low")])
#     rt = Table(rt_data, colWidths=[80*mm,50*mm,40*mm])
#     rt_style = [
#         ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1e3a5f")),
#         ("TEXTCOLOR",(0,0),(-1,0),colors.white),
#         ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
#         ("FONTSIZE",(0,0),(-1,-1),10),
#         ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#e2e8f0")),
#         ("ALIGN",(1,0),(-1,-1),"CENTER"),
#         ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
#         ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
#     ]
#     for i,(_, pct) in enumerate(risks, 1):
#         rt_style.append(("BACKGROUND",(0,i),(-1,i), risk_colour(pct)))
#     rt.setStyle(TableStyle(rt_style))
#     story.append(rt)
#     story.append(Spacer(1,12))
#     story.append(HRFlowable(width="100%",thickness=0.8,
#                              color=colors.HexColor("#e2e8f0"),spaceAfter=8))
#     story.append(Paragraph("AI Health Summary", sec_s))
#     for line in ai_summary.strip().split("\n"):
#         if line.strip():
#             story.append(Paragraph(line.strip(), body_s))
#     story.append(Spacer(1,16))
#     story.append(HRFlowable(width="100%",thickness=0.8,
#                              color=colors.HexColor("#e2e8f0"),spaceAfter=6))
#     story.append(Paragraph(
#         "Generated by MediAI Connect · Informational only · Consult a physician.", foot_s))
#     doc.build(story)
#     return buf.getvalue()

# # ─────────────────────────────────────────────────────────────────────────────
# # HEALTH PROGRESS TRACKER — saves predictions per user
# # ─────────────────────────────────────────────────────────────────────────────
# PROGRESS_DIR = "health_progress"

# def save_prediction(username: str, age, bmi, glucose, d, h, c, k):
#     os.makedirs(PROGRESS_DIR, exist_ok=True)
#     path = os.path.join(PROGRESS_DIR, f"{username}.json")
#     record = {
#         "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
#         "age": age, "bmi": round(float(bmi),1), "glucose": glucose,
#         "diabetes": round(float(d)*100,1), "hypertension": round(float(h)*100,1),
#         "cardiovascular": round(float(c)*100,1), "kidney": round(float(k)*100,1)
#     }
#     history = []
#     if os.path.exists(path):
#         try:
#             with open(path, "r") as f:
#                 history = json.load(f)
#         except Exception:
#             history = []
#     history.append(record)
#     with open(path, "w") as f:
#         json.dump(history, f, indent=2)

# def load_progress(username: str) -> list:
#     path = os.path.join(PROGRESS_DIR, f"{username}.json")
#     if os.path.exists(path):
#         try:
#             with open(path, "r") as f:
#                 return json.load(f)
#         except Exception:
#             return []
#     return []

# # ─────────────────────────────────────────────────────────────────────────────
# # CHATBOT PERSISTENCE HELPERS
# # ─────────────────────────────────────────────────────────────────────────────
# CHAT_DIR = "chat_history"

# def _history_path(username: str) -> str:
#     os.makedirs(CHAT_DIR, exist_ok=True)
#     return os.path.join(CHAT_DIR, f"{username}.json")

# def _load_user_history(username: str) -> list:
#     path = _history_path(username)
#     if os.path.exists(path):
#         try:
#             with open(path, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except Exception:
#             return []
#     return []

# def _save_user_history(username: str, sessions: list):
#     path = _history_path(username)
#     try:
#         with open(path, "w", encoding="utf-8") as f:
#             json.dump(sessions, f, ensure_ascii=False, indent=2)
#     except Exception as e:
#         st.warning(f"Could not save chat history: {e}")

# def _init_chat_state(username: str):
#     if st.session_state.get("_history_user") != username:
#         st.session_state.chat_sessions  = _load_user_history(username)
#         st.session_state.active_chat_id = (
#             st.session_state.chat_sessions[0]["id"]
#             if st.session_state.chat_sessions else None
#         )
#         st.session_state["_history_user"] = username
#     if "chat_sessions" not in st.session_state:
#         st.session_state.chat_sessions = []
#     if "active_chat_id" not in st.session_state:
#         st.session_state.active_chat_id = None

# def _new_chat(username: str):
#     cid = str(uuid.uuid4())
#     now = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
#     st.session_state.chat_sessions.insert(0, {
#         "id": cid, "title": "New Chat", "date": now, "messages": []
#     })
#     st.session_state.active_chat_id = cid
#     _save_user_history(username, st.session_state.chat_sessions)

# def _get_active_session():
#     for s in st.session_state.chat_sessions:
#         if s["id"] == st.session_state.active_chat_id:
#             return s
#     return None

# def _auto_title(session, first_msg: str, username: str):
#     if session["title"] == "New Chat":
#         session["title"] = first_msg[:40] + ("…" if len(first_msg) > 40 else "")
#         _save_user_history(username, st.session_state.chat_sessions)

# def _delete_chat(cid: str, username: str):
#     st.session_state.chat_sessions = [
#         s for s in st.session_state.chat_sessions if s["id"] != cid
#     ]
#     if st.session_state.active_chat_id == cid:
#         st.session_state.active_chat_id = (
#             st.session_state.chat_sessions[0]["id"]
#             if st.session_state.chat_sessions else None
#         )
#     _save_user_history(username, st.session_state.chat_sessions)

# def _call_rag(question: str) -> str:
#     try:
#         result = qa(question)
#         if isinstance(result, dict):
#             ans = result.get("answer") or result.get("result") or ""
#         elif isinstance(result, str):
#             ans = result
#         else:
#             ans = str(result)
#         ans = ans.strip()
#         return ans or "I'm sorry, I couldn't find a relevant answer. Please rephrase."
#     except Exception as e:
#         return f"⚠️ Error: {e}"

# # ─────────────────────────────────────────────────────────────────────────────
# # SESSION STATE INIT
# # ─────────────────────────────────────────────────────────────────────────────
# for key, val in [("chat", []), ("logged_in", False), ("auth_tab", "Login")]:
#     if key not in st.session_state:
#         st.session_state[key] = val

# # =============================================================================
# # LOGIN / REGISTER SCREEN
# # =============================================================================
# if not st.session_state.logged_in:
#     # Block entire page background — prevent any content bleed-through
#     st.markdown("""
#     <style>
#     [data-testid="stAppViewContainer"] {
#         background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 50%, #f5f0ff 100%) !important;
#     }
#     [data-testid="stSidebar"] { display: none !important; }
#     .stApp { background: linear-gradient(135deg,#f0f4ff,#e8f0fe,#f5f0ff) !important; }
#     </style>
#     """, unsafe_allow_html=True)
#     _, center, _ = st.columns([1, 1.6, 1])
#     with center:
#         st.markdown("""
#         <div class="login-card">
#             <div class="login-logo">🏥</div>
#             <div class="login-title">MediAI Connect</div>
#             <div class="login-subtitle">Smart Healthcare Assistant</div>
#         </div>
#         """, unsafe_allow_html=True)

#         tab = st.radio("Select tab", ["🔑  Login", "📝  Register"],
#                        horizontal=True, label_visibility="collapsed")
#         st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

#         if tab == "🔑  Login":
#             username = st.text_input("👤  Username", placeholder="Enter your username")
#             password = st.text_input("🔒  Password", placeholder="Enter your password",
#                                      type="password")
#             st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
#             if st.button("Login  →", width='stretch'):
#                 if login_user(username, password):
#                     st.session_state.logged_in = True
#                     st.session_state.username  = username
#                     # Cover ENTIRE screen including right-side login remnants
#                     _b64 = _gif_b64()
#                     gif_tag = (
#                         f'<img src="data:image/gif;base64,{_b64}" width="90"'
#                         ' style="border-radius:14px;box-shadow:0 4px 24px rgba(0,0,0,0.12);">'
#                         if _b64 else '<div style="font-size:3rem;">🏥</div>'
#                     )
#                     st.markdown(
#                         "<style>body,.stApp,.main,[data-testid='stAppViewContainer']"
#                         "{visibility:hidden !important;}</style>"
#                         "<div style='position:fixed;inset:0;z-index:99999;"
#                         "background:#f0f4ff;"
#                         "display:flex;flex-direction:column;"
#                         "align-items:center;justify-content:center;gap:1.2rem;'>"
#                         + gif_tag +
#                         f"<p style='font-family:DM Sans,sans-serif;font-size:1.1rem;"
#                         f"color:#1e3a5f;font-weight:600;margin:0;'>"
#                         f"Welcome back, {username}! Loading…</p>"
#                         "</div>",
#                         unsafe_allow_html=True
#                     )
#                     st.rerun()
#                 else:
#                     st.error("❌ Invalid username or password.")
#         else:
#             st.markdown("""
#             <div class="rule-box">
#                 🔐 <b>Password must have:</b><br>
#                 ✅ Min 8 chars &nbsp;|&nbsp; ✅ Upper & lowercase<br>
#                 ✅ A number &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp; ✅ Special char (!@#$…)
#             </div>
#             """, unsafe_allow_html=True)
#             new_username = st.text_input("👤  Create Username", placeholder="Choose a username")
#             new_password = st.text_input("🔒  Create Password",
#                                          placeholder="Choose a strong password", type="password")
#             st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
#             if st.button("Create Account  →", width='stretch'):
#                 success, msg = register_user(new_username, new_password)
#                 if success:
#                     st.success(f"✅ {msg} — You can now log in.")
#                 else:
#                     st.error(f"❌ {msg}")
#     st.stop()

# # =============================================================================
# # MAIN APP — Sidebar
# # =============================================================================
# with st.sidebar:
#     st.markdown(f"""
#     <div style='padding:1rem 0 0.5rem 0;'>
#         <div style='font-size:2rem;text-align:center;'>🏥</div>
#         <div style='text-align:center;font-size:1.1rem;font-weight:600;
#                     color:#e2e8f0;margin-top:0.3rem;'>MediAI Connect</div>
#         <div style='text-align:center;font-size:0.8rem;color:#94a3b8;
#                     margin-bottom:1.2rem;'>Smart Healthcare Assistant</div>
#         <hr style='border-color:rgba(255,255,255,0.1);margin-bottom:1rem;'>
#         <div style='font-size:0.82rem;color:#94a3b8;margin-bottom:0.3rem;'>Logged in as</div>
#         <div style='font-weight:600;color:#60a5fa;font-size:0.95rem;
#                     margin-bottom:1.4rem;'>👤 {st.session_state.get("username","User")}</div>
#     </div>
#     """, unsafe_allow_html=True)

#     menu = st.selectbox(
#         "🧭 Navigate",
#         ["About", "🩺 Disease Risk Prediction", "🔬 Future Glucose Prediction",
#          "🧪 Lab Report Analysis", "💬 Medical Chatbot", "📅 Health Progress Tracker",
#          "🏥 Symptom Checker", "📊 BMI & Health Score", "🍎 Diet Recommender",
#          "💊 Medication Info", "📈 Model Insights"]
#     )

#     # Feature icon cards in sidebar
#     st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
#     nav_items = [
#         ("🩺", "Disease Risk",    "XGBoost + MLP"),
#         ("🔬", "Glucose Predict", "Regression ML"),
#         ("🧪", "Lab Report",      "OCR + Gemini"),
#         ("💬", "Chatbot",         "RAG + FAISS"),
#         ("📅", "Progress",        "Trend Tracker"),
#         ("🏥", "Symptom Check",   "Gemini AI"),
#         ("📊", "BMI Score",       "Health Grade"),
#         ("🍎", "Diet Plan",       "7-Day Meal"),
#         ("💊", "Medication",      "Drug Info"),
#         ("📈", "Model Insights",  "SHAP + Metrics"),
#     ]
#     for icon, name, tech in nav_items:
#         st.markdown(
#             f"<div style='display:flex;align-items:center;gap:0.6rem;"
#             f"padding:0.35rem 0.5rem;border-radius:8px;"
#             f"margin-bottom:0.2rem;background:rgba(255,255,255,0.04);'>"
#             f"<span style='font-size:1.1rem;'>{icon}</span>"
#             f"<div><div style='font-size:0.78rem;color:#e2e8f0;font-weight:600;"
#             f"line-height:1.2;'>{name}</div>"
#             f"<div style='font-size:0.68rem;color:#64748b;'>{tech}</div></div>"
#             f"</div>",
#             unsafe_allow_html=True
#         )
#     st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
#     if st.button("🚪  Logout", width='stretch'):
#         st.session_state.logged_in = False
#         st.rerun()

# # App header
# hcol1, hcol2 = st.columns([1, 9])
# with hcol1:
#     if os.path.exists("assets/logo.avif"):
#         st.image("assets/logo.avif", width=80)
#     else:
#         st.markdown("<div style='font-size:3rem;'>🏥</div>", unsafe_allow_html=True)
# with hcol2:
#     st.markdown(
#         "<h1 style='margin-top:10px;font-size:3rem;font-family:\"Playfair Display\",serif;"
#         "color:#1a1a2e;letter-spacing:-1px;font-weight:700;'>MediAI Connect</h1>"
#         "<p style='margin-top:-12px;color:#64748b;font-size:1rem;font-weight:500;'>"
#         "Smart Healthcare Assistant</p>",
#         unsafe_allow_html=True
#     )
# st.markdown("<hr style='border-color:#e2e8f0;margin:0 0 1.5rem 0;'>", unsafe_allow_html=True)

# # Import feature pages
# from disease_risk      import show_disease_risk
# from glucose_pred      import show_glucose_prediction
# from lab_report        import show_lab_report
# from chatbot_page      import show_chatbot
# from progress_page     import show_progress
# from symptom_checker   import show_symptom_checker
# from bmi_calculator    import show_bmi_calculator
# from diet_recommender  import show_diet_recommender
# from medication_info   import show_medication_info
# from model_insights    import show_model_insights

# username = st.session_state.get("username", "User")

# # =============================================================================
# # ROUTE TO FEATURE PAGES
# # =============================================================================
# if menu == "About":
#     # ── Hero banner with robot hand image ────────────────────────────────────
#     if os.path.exists("assets/robot_hand.jpg"):
#         with open("assets/robot_hand.jpg", "rb") as f:
#             img_b64 = base64.b64encode(f.read()).decode()
#         hero_html = (
#             "<div style='position:relative;border-radius:20px;overflow:hidden;"
#             "margin-bottom:2rem;box-shadow:0 8px 40px rgba(0,0,0,0.25);'>"
#             "<img src='data:image/jpeg;base64," + img_b64 + "'"
#             " style='width:100%;height:320px;object-fit:cover;"
#             "object-position:center;display:block;"
#             "filter:blur(2px) brightness(0.5);transform:scale(1.05);'>"
#             "<div style='position:absolute;inset:0;"
#             "background:linear-gradient(120deg,"
#             "rgba(10,20,50,0.6) 0%,rgba(15,40,80,0.45) 55%,rgba(10,20,50,0.4) 100%);'>"
#             "</div>"
#             "<div style='position:absolute;inset:0;display:flex;flex-direction:column;"
#             "justify-content:flex-end;padding:2rem 3rem;'>"
#             "<p style='color:#bfdbfe;font-size:1.1rem;margin:0 0 1rem 0;font-weight:500;"
#             "letter-spacing:0.02em;text-shadow:0 1px 8px rgba(0,0,0,0.8);'>"
#             "AI-Powered Smart Healthcare Assistant</p>"
#             "<div style='display:flex;gap:0.6rem;flex-wrap:wrap;'>"
            # "<span style='background:rgba(59,130,246,0.35);border:1px solid rgba(59,130,246,0.6);"
            # "color:#bfdbfe;border-radius:20px;padding:0.25rem 0.9rem;"
            # "font-size:0.8rem;font-weight:600;'>🩺 Disease Risk</span>"
#             "<span style='background:rgba(16,185,129,0.3);border:1px solid rgba(16,185,129,0.5);"
#             "color:#a7f3d0;border-radius:20px;padding:0.25rem 0.9rem;"
#             "font-size:0.8rem;font-weight:600;'>🔬 Glucose Prediction</span>"
#             "<span style='background:rgba(139,92,246,0.3);border:1px solid rgba(139,92,246,0.5);"
#             "color:#ddd6fe;border-radius:20px;padding:0.25rem 0.9rem;"
#             "font-size:0.8rem;font-weight:600;'>🧪 Lab Analysis</span>"
#             "<span style='background:rgba(245,158,11,0.3);border:1px solid rgba(245,158,11,0.5);"
#             "color:#fde68a;border-radius:20px;padding:0.25rem 0.9rem;"
#             "font-size:0.8rem;font-weight:600;'>💬 AI Chatbot</span>"
            # "<span style='background:rgba(239,68,68,0.3);border:1px solid rgba(239,68,68,0.5);"
            # "color:#fca5a5;border-radius:20px;padding:0.25rem 0.9rem;"
            # "font-size:0.8rem;font-weight:600;'>📅 Progress Tracker</span>"
#            
            # "<span style='background:rgba(16,185,129,0.3);border:1px solid rgba(16,185,129,0.5);"
            # "color:#a7f3d0;border-radius:20px;padding:0.25rem 0.9rem;"
            # "font-size:0.8rem;font-weight:600;'>📊 BMI & Health Score</span>"
            # "<span style='background:rgba(139,92,246,0.3);border:1px solid rgba(139,92,246,0.5);"
            # "color:#ddd6fe;border-radius:20px;padding:0.25rem 0.9rem;"
            # "font-size:0.8rem;font-weight:600;'>🍎 Diet Recommender</span>"
            # "<span style='background:rgba(245,158,11,0.3);border:1px solid rgba(245,158,11,0.5);"
            # "color:#fde68a;border-radius:20px;padding:0.25rem 0.9rem;"
            # "font-size:0.8rem;font-weight:600;'>💊 Medication Info</span>"
            # "<span style='background:rgba(239,68,68,0.3);border:1px solid rgba(239,68,68,0.5);"
            # "color:#fca5a5;border-radius:20px;padding:0.25rem 0.9rem;"
            # "font-size:0.8rem;font-weight:600;'>📈 Model Insights</span>"
#             "</div></div></div>"
#         )
#         st.markdown(hero_html, unsafe_allow_html=True)

#     st.markdown("## 👋 About MediAI Connect")

#     col_a, col_b = st.columns(2)
#     with col_a:
#         st.markdown("""
#         **MediAI Connect** is an AI-powered healthcare assistant that combines
#         machine learning, deep learning, and Gemini AI to help users understand
#         and manage their health comprehensively.

#         **Core ML Features:**
#         - 🩺 Predicts risk for Diabetes, Hypertension, Cardiovascular & Kidney disease
#         - 🔬 Forecasts future glucose levels with age-trend graphs
#         - 🧪 Analyses lab reports using OCR + Gemini AI in 10 languages
#         - 💬 Answers medical questions using a RAG-powered chatbot
#         - 📅 Tracks your health progress over time with trend graphs
#         - 📈 Explains model predictions with Feature Importance & SHAP

#         **New Health Tools:**
#         - 🏥 Symptom Checker powered by Gemini AI
#         - 📊 BMI & Health Score with A–F grading
#         - 🍎 Personalised 7-day Diet & Meal Planner
#         - 💊 Medication Information & Reminder Scheduler
#         """)
#     with col_b:
#         st.markdown("""
#         **Technology Stack:**

#         | Module | Technology |
#         |---|---|
#         | Disease Risk | XGBoost + MLP Neural Net |
#         | Glucose Forecast | LinearReg + MLP Regressor |
#         | Explainability | SHAP + Feature Importance |
#         | AI Summary | Gemini 2.5 Flash |
#         | Lab OCR | Tesseract + PIL |
#         | Chatbot | RAG + FAISS + LangChain |
#         | Progress | JSON longitudinal storage |
#         | Symptom Check | Gemini 2.5 Flash |
#         | Diet Plan | Gemini 2.5 Flash |
#         | Drug Info | Gemini 2.5 Flash |
#         | Auth | bcrypt password hashing |

#         **Dataset:** 1,700 clinical records, 9 features, 4 disease targets
#         """)

#     st.info("💡 Use the sidebar to navigate between all 10 features.")

# elif menu == "🩺 Disease Risk Prediction":
#     show_disease_risk(scaler, diabetes_model, hypertension_model,
#                       cardio_model, kidney_model, username,
#                       show_loader, generate_ai_health_summary,
#                       create_disease_pdf, save_prediction)

# elif menu == "🔬 Future Glucose Prediction":
#     show_glucose_prediction(glucose_model, glucose_scaler)

# elif menu == "🧪 Lab Report Analysis":
#     show_lab_report(show_loader)

# elif menu == "💬 Medical Chatbot":
#     show_chatbot(username, _init_chat_state, _new_chat, _get_active_session,
#                  _auto_title, _delete_chat, _save_user_history, _call_rag,
#                  show_loader)

# elif menu == "📅 Health Progress Tracker":
#     show_progress(username, load_progress)

# elif menu == "🏥 Symptom Checker":
#     st.session_state["_sym_user"] = username
#     show_symptom_checker(show_loader)

# elif menu == "📊 BMI & Health Score":
#     show_bmi_calculator(show_loader)

# elif menu == "🍎 Diet Recommender":
#     show_diet_recommender(show_loader, username=username)

# elif menu == "💊 Medication Info":
#     show_medication_info(show_loader, username=username)

# elif menu == "📈 Model Insights":
#     @st.cache_resource
#     def _load_insight_models():
#         _m = {"scaler": joblib.load("models/scaler.pkl")}
#         for _disease in ["Diabetes_Diagnosis","hypertension","cardiovascular","kidney"]:
#             for _mtype in ["xgb","rf","logreg","mlp"]:
#                 _path = f"models/{_disease}_{_mtype}.pkl"
#                 if os.path.exists(_path):
#                     _m[f"{_disease}_{_mtype}"] = joblib.load(_path)
#         return _m
#     show_model_insights(_load_insight_models())



# import streamlit as st
# import pandas as pd


# def show_progress(username: str, load_progress):

#     st.markdown("## 📅 Health Progress Tracker")
#     st.caption(f"Tracking health predictions for **{username}**")

#     history = load_progress(username)

#     if not history:
#         st.info("No predictions saved yet. Run a **Disease Risk Prediction** first — "
#                 "each prediction is automatically saved here.")
#         return

#     df = pd.DataFrame(history)
#     df["date"] = pd.to_datetime(df["date"])
#     df = df.sort_values("date")
#     df["date_str"] = df["date"].dt.strftime("%d %b %Y %H:%M")

#     st.markdown(f"**{len(df)} prediction{'s' if len(df)>1 else ''} recorded**")

#     # ── Summary metrics — latest vs first ────────────────────────────────────
#     if len(df) > 1:
#         latest = df.iloc[-1]
#         first  = df.iloc[0]
#         st.markdown("### 📊 Latest vs First Prediction")
#         c1, c2, c3, c4 = st.columns(4)
#         c1.metric(" Diabetes",
#                   f"{latest['diabetes']}%",
#                   f"{latest['diabetes']-first['diabetes']:+.1f}%")
#         c2.metric("💓 Hypertension",
#                   f"{latest['hypertension']}%",
#                   f"{latest['hypertension']-first['hypertension']:+.1f}%")
#         c3.metric("❤️ Cardiovascular",
#                   f"{latest['cardiovascular']}%",
#                   f"{latest['cardiovascular']-first['cardiovascular']:+.1f}%")
#         c4.metric("🫘 Kidney",
#                   f"{latest['kidney']}%",
#                   f"{latest['kidney']-first['kidney']:+.1f}%")

#     # ── Risk trends chart ─────────────────────────────────────────────────────
#     st.markdown("### 📈 Risk Trends Over Time")
#     chart_df = df.set_index("date_str")[
#         ["diabetes", "hypertension", "cardiovascular", "kidney"]
#     ]
#     chart_df.columns = ["Diabetes %", "Hypertension %", "Cardiovascular %", "Kidney %"]
#     st.line_chart(chart_df)

#     # ── BMI and Glucose trends ────────────────────────────────────────────────
#     st.markdown("### 📈 BMI & Glucose Trends")
#     bg_df = df.set_index("date_str")[["bmi", "glucose"]]
#     bg_df.columns = ["BMI", "Glucose (mg/dL)"]
#     st.line_chart(bg_df)

#     # ── Full history table ────────────────────────────────────────────────────
#     st.markdown("### 📋 Full History")
#     display_df = df[["date_str", "age", "bmi", "glucose",
#                       "diabetes", "hypertension", "cardiovascular", "kidney"]].copy()
#     display_df.columns = ["Date", "Age", "BMI", "Glucose",
#                            "Diabetes %", "Hypertension %", "Cardio %", "Kidney %"]

#     def colour_risk(val):
#         if isinstance(val, float):
#             if val >= 70: return "background-color:#fee2e2;color:#991b1b"
#             elif val >= 40: return "background-color:#fef9c3;color:#854d0e"
#             elif val > 0: return "background-color:#dcfce7;color:#166534"
#         return ""

#     st.dataframe(
#         display_df.style.applymap(colour_risk,
#             subset=["Diabetes %","Hypertension %","Cardio %","Kidney %"]),
#         width='stretch',
#         hide_index=True
#     )
#     st.caption("🟢 Low (<40%)  🟡 Moderate (40–70%)  🔴 High (≥70%)")

#     # ── Clear history ─────────────────────────────────────────────────────────
#     if st.button("🗑️ Clear My Progress History"):
#         import os, json
#         path = os.path.join("health_progress", f"{username}.json")
#         if os.path.exists(path):
#             os.remove(path)
#         st.success("Progress history cleared.")
#         st.rerun()