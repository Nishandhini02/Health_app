

# # lab_report.py
# import streamlit as st
# import io
# import re
# import pytesseract
# import google.generativeai as genai
# from PIL import Image, ImageFilter, ImageEnhance, ImageOps
# from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import mm
# from reportlab.lib.enums import TA_CENTER
# from dotenv import load_dotenv; load_dotenv()
# import os
# from google import genai as _genai_module
# API_KEY = os.getenv("GEMINI_API_KEY")


# # ─────────────────────────────────────────────────────────────────────────────
# # TXT / PDF HELPERS  (unchanged from your original)
# # ─────────────────────────────────────────────────────────────────────────────
# def _make_txt(summary_text: str, language: str) -> bytes:
#     import re as _re
#     lines = []
#     for line in summary_text.split("\n"):
#         t = line.strip()
#         if not t:
#             lines.append(""); continue
#         if _re.match(r'^[-\*_]{3,}$', t):
#             lines.append("-" * 48); continue
#         t = _re.sub(r'^#{1,6}\s*', '', t)
#         t = _re.sub(r'^\d+\.\s+', '', t)
#         t = _re.sub(r'^[\*\-\+•]\s+', '', t)
#         t = t.strip('|').strip()
#         t = _re.sub(r'\*\*(.+?)\*\*', r'\1', t, flags=_re.DOTALL)
#         t = t.replace('*', '').replace('#', '')
#         t = _re.sub(r'  +', ' ', t)
#         lines.append(t.strip())
#     content = (
#         "MediAI Connect - Lab Report Summary\n"
#         "------------------------------------------------\n"
#         f"Language: {language}\n"
#         "------------------------------------------------\n\n"
#         + "\n".join(lines)
#     )
#     return content.encode("utf-8")


# def _create_lab_pdf_local(summary_text: str, language: str = "English") -> bytes:
#     import re as _re, os

#     if language != "English":
#         return _make_txt(summary_text, language)

#     try:
#         import requests
#         from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable, Spacer
#         from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
#         from reportlab.lib.pagesizes import A4
#         from reportlab.lib import colors
#         from reportlab.lib.units import mm
#         from reportlab.lib.enums import TA_CENTER
#         from reportlab.pdfbase import pdfmetrics
#         from reportlab.pdfbase.ttfonts import TTFont

#         os.makedirs("assets", exist_ok=True)
#         NOTO_REG  = os.path.join("assets", "NotoSans-Regular.ttf")
#         NOTO_BOLD = os.path.join("assets", "NotoSans-Bold.ttf")

#         def _dl(path, urls):
#             if os.path.exists(path) and os.path.getsize(path) > 10000:
#                 return True
#             for url in urls:
#                 try:
#                     r = requests.get(url, timeout=20)
#                     if r.status_code == 200 and len(r.content) > 10000:
#                         with open(path, "wb") as f:
#                             f.write(r.content)
#                         return True
#                 except Exception:
#                     continue
#             return False

#         _dl(NOTO_REG, [
#             "https://fonts.gstatic.com/s/notosans/v36/o-0mIpQlx3QUlC5A4PNjXhFVZNyB1Wk.ttf",
#             "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf",
#         ])
#         _dl(NOTO_BOLD, [
#             "https://fonts.gstatic.com/s/notosans/v36/o-0NIpQlx3QUlC5A4PNjKhFlYqgnLHU.ttf",
#             "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf",
#         ])

#         if os.path.exists(NOTO_REG):
#             try:
#                 pdfmetrics.registerFont(TTFont("NotoSans",      NOTO_REG))
#                 pdfmetrics.registerFont(TTFont("NotoSans-Bold", NOTO_BOLD))
#                 fn, fb = "NotoSans", "NotoSans-Bold"
#             except Exception:
#                 fn, fb = "Helvetica", "Helvetica-Bold"
#         else:
#             fn, fb = "Helvetica", "Helvetica-Bold"

#         def _clean_rl(t):
#             t = _re.sub(r'^#{1,6}\s*', '', t)
#             t = _re.sub(r'^\d+\.\s+', '', t)
#             t = _re.sub(r'^[\*\-\+•]\s+', '', t)
#             t = t.strip('|').strip()
#             t = _re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t, flags=_re.DOTALL)
#             t = t.replace('*', '').replace('#', '')
#             return t.strip()

#         buf    = io.BytesIO()
#         doc    = SimpleDocTemplate(buf, pagesize=A4,
#                                    leftMargin=20*mm, rightMargin=20*mm,
#                                    topMargin=18*mm, bottomMargin=18*mm)
#         styles = getSampleStyleSheet()
#         title_s = ParagraphStyle("T", parent=styles["Title"], fontName=fb,
#                                  fontSize=16, textColor=colors.HexColor("#1e3a5f"),
#                                  alignment=TA_CENTER, spaceAfter=6)
#         head_s  = ParagraphStyle("H", parent=styles["Normal"], fontName=fb,
#                                  fontSize=12, textColor=colors.HexColor("#1e3a5f"),
#                                  spaceBefore=10, spaceAfter=4)
#         body_s  = ParagraphStyle("B", parent=styles["Normal"], fontName=fn,
#                                  fontSize=10, textColor=colors.HexColor("#334155"),
#                                  leading=16, spaceAfter=3)

#         story = [
#             Paragraph("MediAI Connect - Lab Report Summary", title_s),
#             HRFlowable(width="100%", thickness=1.5,
#                        color=colors.HexColor("#3b82f6"), spaceAfter=14),
#         ]
#         for raw in summary_text.strip().split("\n"):
#             r = raw.strip()
#             if not r:
#                 story.append(Spacer(1, 4)); continue
#             if _re.match(r'^[-\*_]{3,}$', r):
#                 story.append(HRFlowable(width="100%", thickness=0.5,
#                                         color=colors.HexColor("#e2e8f0"), spaceAfter=4))
#                 continue
#             c = _clean_rl(r)
#             if not c: continue
#             if _re.match(r'^#{1,4}\s', r):
#                 story.append(Paragraph(c, head_s))
#             else:
#                 story.append(Paragraph(c, body_s))
#         doc.build(story)
#         return buf.getvalue()

#     except Exception:
#         return _make_txt(summary_text, language)


# # ─────────────────────────────────────────────────────────────────────────────
# # IMAGE PREPROCESSING
# # ─────────────────────────────────────────────────────────────────────────────
# def preprocess_for_ocr(image: Image.Image) -> Image.Image:
#     w, h = image.size
#     image = image.resize((w * 3, h * 3), Image.LANCZOS)
#     image = ImageOps.grayscale(image)
#     image = ImageEnhance.Contrast(image).enhance(2.5)
#     image = image.filter(ImageFilter.SHARPEN)
#     image = image.filter(ImageFilter.SHARPEN)
#     image = image.filter(ImageFilter.MedianFilter(size=3))
#     image = image.point(lambda px: 255 if px > 150 else 0, "1")
#     image = image.convert("L")
#     return image


# def _run_ocr(image: Image.Image) -> str:
#     """Run Tesseract OCR on the given image."""
#     try:
#         return pytesseract.image_to_string(image, config=r"--oem 3 --psm 6")
#     except Exception as e:
#         return f"[OCR error: {e}]"


# # ─────────────────────────────────────────────────────────────────────────────
# # MAIN PAGE
# # ─────────────────────────────────────────────────────────────────────────────
# def show_lab_report(show_loader):
#     st.markdown("## 🧪 Lab Report Analysis")

#     # Language first — changing language does NOT re-run OCR
#     lang = st.selectbox(
#         "🌐 Select Language for Summary",
#         ["English","Tamil","Hindi","Telugu","Malayalam",
#          "Kannada","Bengali","Marathi","Gujarati","Urdu"],
#         key="lab_lang_select",
#     )

#     file = st.file_uploader(
#         "📁 Upload Report Image",
#         type=["png", "jpg", "jpeg", "webp", "jfif"],
#     )

#     if not file:
#         return

#     # ── Cache OCR per uploaded file (don't re-run on widget changes) ──────
#     file_id = f"{file.name}_{file.size}"
#     if st.session_state.get("lab_file_id") != file_id:
#         img           = Image.open(file).convert("RGB")
#         processed_img = preprocess_for_ocr(img)

#         # Run OCR on BOTH versions once, cache both texts
#         ocr_orig = _run_ocr(img)
#         ocr_proc = _run_ocr(processed_img)

#         st.session_state["lab_file_id"]   = file_id
#         st.session_state["lab_img_orig"]  = img
#         st.session_state["lab_img_proc"]  = processed_img
#         st.session_state["lab_ocr_orig"]  = ocr_orig
#         st.session_state["lab_ocr_proc"]  = ocr_proc
#         st.session_state["lab_summary"]   = None   # reset on new file

#     img           = st.session_state["lab_img_orig"]
#     processed_img = st.session_state["lab_img_proc"]
#     ocr_orig      = st.session_state["lab_ocr_orig"]
#     ocr_proc      = st.session_state["lab_ocr_proc"]

#     # ── Show both images ──────────────────────────────────────────────────
#     col_orig, col_proc = st.columns(2)
#     with col_orig:
#         st.markdown("**Original Image**")
#         st.image(img, use_container_width=True)
#     with col_proc:
#         st.markdown("**Processed for OCR**")
#         st.image(processed_img, use_container_width=True)

#     # ── OCR SOURCE SELECTOR — the key fix for Q3 ─────────────────────────
#     st.markdown("#### 🔍 OCR Text Source")
#     st.markdown(
#         "<small style='color:#64748b;'>If the processed image looks worse than the "
#         "original (e.g. blurry scans or coloured headers), switch to <b>Original</b> "
#         "for better OCR accuracy.</small>",
#         unsafe_allow_html=True,
#     )

#     ocr_source = st.radio(
#         "Use which image for text extraction?",
#         ["Processed (recommended for most reports)",
#          "Original (better for high-quality / coloured images)"],
#         key="lab_ocr_source",
#         horizontal=True,
#     )

#     use_processed = ocr_source.startswith("Processed")
#     extracted_text = ocr_proc if use_processed else ocr_orig

#     # Live quality indicator
#     word_count = len(extracted_text.split())
#     if word_count < 20:
#         st.warning(
#             f"⚠️ Only **{word_count} words** extracted from the "
#             f"{'processed' if use_processed else 'original'} image. "
#             "Try switching the source above."
#         )
#     else:
#         st.success(
#             f"✅ Extracted **{word_count} words** from the "
#             f"{'processed' if use_processed else 'original'} image."
#         )

#     if extracted_text.strip():
#         with st.expander("📄 View Extracted Text", expanded=False):
#             st.text_area("OCR Output", extracted_text, height=200,
#                          label_visibility="collapsed")

#         # ── Action buttons ────────────────────────────────────────────────
#         btn_col1, btn_col2 = st.columns(2)
#         with btn_col1:
#             gen_clicked = st.button("🤖 Generate Medical Summary", use_container_width=True)
#         with btn_col2:
#             trans_clicked = (
#                 st.button("🌐 Translate Summary", use_container_width=True)
#                 if st.session_state.get("lab_summary") else None
#             )

#         # ── Generate summary ──────────────────────────────────────────────
#         if gen_clicked:
#             loader_ph = st.empty()
#             show_loader(loader_ph, "Analysing lab report…")
#             try:
#                 gemini_model = genai.GenerativeModel("gemini-2.5-flash")
#                 prompt = f"""You are an expert medical assistant helping a patient understand their lab report.

# The patient has uploaded a lab report. The extracted text is below.
# Provide a complete medical summary and suggestions in **{lang}** language.

# Lab Report Text:
# \"\"\"
# {extracted_text}
# \"\"\"

# Your response must include all sections below, written entirely in {lang}:

# 1. 📋 **Report Overview**
#    - What type of report is this?
#    - What date/hospital if mentioned?

# 2. 🔬 **Test Results Analysis**
#    - For each test found, show:
#      • Test name
#      • Patient's value
#      • Normal reference range
#      • Status: 🟢 Normal / 🟡 Borderline / 🔴 High / 🔵 Low
#      • Simple explanation of what this test measures

# 3. ⚠️ **Key Findings**
#    - List abnormal or concerning values clearly

# 4. 💊 **Medical Suggestions**
#    - Based on the results, give specific dietary advice
#    - Lifestyle changes recommended
#    - Medications or supplements to discuss with doctor

# 5. 🏥 **When to See a Doctor**
#    - Which results need urgent attention?
#    - What type of specialist should the patient consult?

# Write in simple, easy-to-understand language for a non-medical person.
# Respond entirely in {lang} language."""

#                 response = gemini_model.generate_content(prompt)
#                 summary  = response.text.strip()
#             except Exception as e:
#                 summary = f"Could not generate summary: {e}"

#             loader_ph.empty()
#             st.session_state["lab_summary"] = summary

#         # ── Translate ─────────────────────────────────────────────────────
#         if trans_clicked and st.session_state.get("lab_summary"):
#             loader_ph2 = st.empty()
#             show_loader(loader_ph2, f"Translating to {lang}…")
#             try:
#                 gemini_model = genai.GenerativeModel("gemini-2.5-flash")
#                 trans_prompt = (
#                     f"Translate the following medical summary into {lang} language.\n"
#                     f"Keep all medical terms accurate. Keep emojis and structure.\n\n"
#                     f"{st.session_state['lab_summary']}"
#                 )
#                 trans_resp = gemini_model.generate_content(trans_prompt)
#                 st.session_state["lab_summary"] = trans_resp.text.strip()
#             except Exception as e:
#                 st.error(f"Translation failed: {e}")
#             loader_ph2.empty()

#         # ── Display + download ────────────────────────────────────────────
#         if st.session_state.get("lab_summary"):
#             st.markdown("### 🤖 Medical Summary & Suggestions")
#             st.info(st.session_state["lab_summary"])

#             pdf_bytes = _create_lab_pdf_local(st.session_state["lab_summary"], lang)

#             if lang == "English":
#                 st.download_button(
#                     "📥 Download Lab Report (PDF)",
#                     pdf_bytes,
#                     "lab_report_english.pdf",
#                     "application/pdf",
#                 )
#             else:
#                 st.download_button(
#                     f"📥 Download Lab Report — {lang} (TXT)",
#                     pdf_bytes,
#                     f"lab_report_{lang.lower()}.txt",
#                     "text/plain; charset=utf-8",
#                 )
#                 st.caption("💡 Open with Notepad, Word, or any text editor.")
#     else:
#         st.warning(
#             "⚠️ Could not extract text from either image version.\n\n"
#             "Tips:\n"
#             "- Use a clear, high-resolution image\n"
#             "- Ensure good lighting, no shadows\n"
#             "- Keep image straight, not tilted\n"
#             "- Black text on white background works best"
#         )


"""
lab_report.py
─────────────
Lab Report Analysis page.
Uses gemini_fallback.py for full key-rotation + model-fallback chain:
  gemini-2.5-flash-lite -> gemini-2.5-flash -> gemini-1.5-flash -> gemini-1.5-flash-8b
"""

import io
import re
import os

import streamlit as st
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
from dotenv import load_dotenv

from gemini_fallback import (
    RoundRobinKeyManager,
    gemini_generate_with_fallback,
    GEMINI_MODEL_CHAIN,
)

load_dotenv()

# ── Shared key manager (picks up all keys from secrets / env) ─────────────────

def _load_keys(secret_name: str, env_fallback: str) -> list:
    try:
        import streamlit as _st
        val = _st.secrets[secret_name]
        if isinstance(val, list):
            return [k.strip() for k in val if k.strip()]
        return [k.strip().strip('"').strip("'")
                for k in str(val).split(",") if k.strip()]
    except Exception:
        pass
    raw = os.environ.get(env_fallback, "").strip()
    if not raw:
        return []
    return [k.strip().strip('"').strip("'") for k in raw.split(",") if k.strip()]


_LAB_KEY_MGR = RoundRobinKeyManager(
    _load_keys("GEMINI_API_KEY", "GEMINI_API_KEY"),
    cooldown_seconds=70,
)


def _gemini(prompt: str, feature: str = "lab_report") -> str:
    """Call Gemini with full key-rotation + model-fallback."""
    return gemini_generate_with_fallback(
        prompt=prompt,
        key_manager=_LAB_KEY_MGR,
        model_chain=GEMINI_MODEL_CHAIN,
        feature=feature,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TXT / PDF HELPERS  (unchanged from original)
# ─────────────────────────────────────────────────────────────────────────────

def _make_txt(summary_text: str, language: str) -> bytes:
    lines = []
    for line in summary_text.split("\n"):
        t = line.strip()
        if not t:
            lines.append(""); continue
        if re.match(r'^[-\*_]{3,}$', t):
            lines.append("-" * 48); continue
        t = re.sub(r'^#{1,6}\s*', '', t)
        t = re.sub(r'^\d+\.\s+', '', t)
        t = re.sub(r'^[\*\-\+•]\s+', '', t)
        t = t.strip('|').strip()
        t = re.sub(r'\*\*(.+?)\*\*', r'\1', t, flags=re.DOTALL)
        t = t.replace('*', '').replace('#', '')
        t = re.sub(r'  +', ' ', t)
        lines.append(t.strip())
    content = (
        "MediAI Connect - Lab Report Summary\n"
        "------------------------------------------------\n"
        f"Language: {language}\n"
        "------------------------------------------------\n\n"
        + "\n".join(lines)
    )
    return content.encode("utf-8")


def _create_lab_pdf_local(summary_text: str, language: str = "English") -> bytes:
    if language != "English":
        return _make_txt(summary_text, language)

    try:
        import requests
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, HRFlowable, Spacer
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.lib.enums import TA_CENTER
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        os.makedirs("assets", exist_ok=True)
        NOTO_REG  = os.path.join("assets", "NotoSans-Regular.ttf")
        NOTO_BOLD = os.path.join("assets", "NotoSans-Bold.ttf")

        def _dl(path, urls):
            if os.path.exists(path) and os.path.getsize(path) > 10000:
                return True
            for url in urls:
                try:
                    r = requests.get(url, timeout=20)
                    if r.status_code == 200 and len(r.content) > 10000:
                        with open(path, "wb") as f:
                            f.write(r.content)
                        return True
                except Exception:
                    continue
            return False

        _dl(NOTO_REG, [
            "https://fonts.gstatic.com/s/notosans/v36/o-0mIpQlx3QUlC5A4PNjXhFVZNyB1Wk.ttf",
            "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf",
        ])
        _dl(NOTO_BOLD, [
            "https://fonts.gstatic.com/s/notosans/v36/o-0NIpQlx3QUlC5A4PNjKhFlYqgnLHU.ttf",
            "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf",
        ])

        if os.path.exists(NOTO_REG):
            try:
                pdfmetrics.registerFont(TTFont("NotoSans",      NOTO_REG))
                pdfmetrics.registerFont(TTFont("NotoSans-Bold", NOTO_BOLD))
                fn, fb = "NotoSans", "NotoSans-Bold"
            except Exception:
                fn, fb = "Helvetica", "Helvetica-Bold"
        else:
            fn, fb = "Helvetica", "Helvetica-Bold"

        def _clean_rl(t):
            t = re.sub(r'^#{1,6}\s*', '', t)
            t = re.sub(r'^\d+\.\s+', '', t)
            t = re.sub(r'^[\*\-\+•]\s+', '', t)
            t = t.strip('|').strip()
            t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t, flags=re.DOTALL)
            t = t.replace('*', '').replace('#', '')
            return t.strip()

        buf    = io.BytesIO()
        doc    = SimpleDocTemplate(buf, pagesize=A4,
                                   leftMargin=20*mm, rightMargin=20*mm,
                                   topMargin=18*mm, bottomMargin=18*mm)
        styles = getSampleStyleSheet()
        title_s = ParagraphStyle("T", parent=styles["Title"], fontName=fb,
                                 fontSize=16, textColor=colors.HexColor("#1e3a5f"),
                                 alignment=TA_CENTER, spaceAfter=6)
        head_s  = ParagraphStyle("H", parent=styles["Normal"], fontName=fb,
                                 fontSize=12, textColor=colors.HexColor("#1e3a5f"),
                                 spaceBefore=10, spaceAfter=4)
        body_s  = ParagraphStyle("B", parent=styles["Normal"], fontName=fn,
                                 fontSize=10, textColor=colors.HexColor("#334155"),
                                 leading=16, spaceAfter=3)

        story = [
            Paragraph("MediAI Connect - Lab Report Summary", title_s),
            HRFlowable(width="100%", thickness=1.5,
                       color=colors.HexColor("#3b82f6"), spaceAfter=14),
        ]
        for raw in summary_text.strip().split("\n"):
            r = raw.strip()
            if not r:
                story.append(Spacer(1, 4)); continue
            if re.match(r'^[-\*_]{3,}$', r):
                story.append(HRFlowable(width="100%", thickness=0.5,
                                        color=colors.HexColor("#e2e8f0"), spaceAfter=4))
                continue
            c = _clean_rl(r)
            if not c:
                continue
            if re.match(r'^#{1,4}\s', r):
                story.append(Paragraph(c, head_s))
            else:
                story.append(Paragraph(c, body_s))
        doc.build(story)
        return buf.getvalue()

    except Exception:
        return _make_txt(summary_text, language)


# ─────────────────────────────────────────────────────────────────────────────
# IMAGE PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def preprocess_for_ocr(image: Image.Image) -> Image.Image:
    w, h  = image.size
    image = image.resize((w * 3, h * 3), Image.LANCZOS)
    image = ImageOps.grayscale(image)
    image = ImageEnhance.Contrast(image).enhance(2.5)
    image = image.filter(ImageFilter.SHARPEN)
    image = image.filter(ImageFilter.SHARPEN)
    image = image.filter(ImageFilter.MedianFilter(size=3))
    image = image.point(lambda px: 255 if px > 150 else 0, "1")
    image = image.convert("L")
    return image


def _run_ocr(image: Image.Image) -> str:
    try:
        return pytesseract.image_to_string(image, config=r"--oem 3 --psm 6")
    except Exception as e:
        return f"[OCR error: {e}]"


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────────────────────────────────────────

def show_lab_report(show_loader):
    st.markdown("## 🧪 Lab Report Analysis")

    lang = st.selectbox(
        "🌐 Select Language for Summary",
        ["English", "Tamil", "Hindi", "Telugu", "Malayalam",
         "Kannada", "Bengali", "Marathi", "Gujarati", "Urdu"],
        key="lab_lang_select",
    )

    file = st.file_uploader(
        "📁 Upload Report Image",
        type=["png", "jpg", "jpeg", "webp", "jfif"],
    )

    if not file:
        return

    # Cache OCR per uploaded file — don't re-run on widget changes
    file_id = f"{file.name}_{file.size}"
    if st.session_state.get("lab_file_id") != file_id:
        img           = Image.open(file).convert("RGB")
        processed_img = preprocess_for_ocr(img)
        ocr_orig      = _run_ocr(img)
        ocr_proc      = _run_ocr(processed_img)

        st.session_state["lab_file_id"]  = file_id
        st.session_state["lab_img_orig"] = img
        st.session_state["lab_img_proc"] = processed_img
        st.session_state["lab_ocr_orig"] = ocr_orig
        st.session_state["lab_ocr_proc"] = ocr_proc
        st.session_state["lab_summary"]  = None   # reset on new file

    img           = st.session_state["lab_img_orig"]
    processed_img = st.session_state["lab_img_proc"]
    ocr_orig      = st.session_state["lab_ocr_orig"]
    ocr_proc      = st.session_state["lab_ocr_proc"]

    # Show both images
    col_orig, col_proc = st.columns(2)
    with col_orig:
        st.markdown("**Original Image**")
        st.image(img, use_container_width=True)
    with col_proc:
        st.markdown("**Processed for OCR**")
        st.image(processed_img, use_container_width=True)

    # OCR source selector
    st.markdown("#### 🔍 OCR Text Source")
    st.markdown(
        "<small style='color:#64748b;'>If the processed image looks worse than the "
        "original (e.g. blurry scans or coloured headers), switch to <b>Original</b> "
        "for better OCR accuracy.</small>",
        unsafe_allow_html=True,
    )

    ocr_source = st.radio(
        "Use which image for text extraction?",
        ["Processed (recommended for most reports)",
         "Original (better for high-quality / coloured images)"],
        key="lab_ocr_source",
        horizontal=True,
    )

    use_processed  = ocr_source.startswith("Processed")
    extracted_text = ocr_proc if use_processed else ocr_orig

    word_count = len(extracted_text.split())
    if word_count < 20:
        st.warning(
            f"⚠️ Only **{word_count} words** extracted from the "
            f"{'processed' if use_processed else 'original'} image. "
            "Try switching the source above."
        )
    else:
        st.success(
            f"✅ Extracted **{word_count} words** from the "
            f"{'processed' if use_processed else 'original'} image."
        )

    if not extracted_text.strip():
        st.warning(
            "⚠️ Could not extract text from either image version.\n\n"
            "Tips:\n"
            "- Use a clear, high-resolution image\n"
            "- Ensure good lighting, no shadows\n"
            "- Keep image straight, not tilted\n"
            "- Black text on white background works best"
        )
        return

    with st.expander("📄 View Extracted Text", expanded=False):
        st.text_area("OCR Output", extracted_text, height=200,
                     label_visibility="collapsed")

    # Action buttons
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        gen_clicked = st.button("🤖 Generate Medical Summary", use_container_width=True)
    with btn_col2:
        trans_clicked = (
            st.button("🌐 Translate Summary", use_container_width=True)
            if st.session_state.get("lab_summary") else None
        )

    # ── Generate summary ──────────────────────────────────────────────────
    if gen_clicked:
        loader_ph = st.empty()
        show_loader(loader_ph, "Analysing lab report…")

        prompt = f"""You are an expert medical assistant helping a patient understand their lab report.

The patient has uploaded a lab report. The extracted text is below.
Provide a complete medical summary and suggestions in **{lang}** language.

Lab Report Text:
\"\"\"
{extracted_text}
\"\"\"

Your response must include all sections below, written entirely in {lang}:

1. 📋 **Report Overview**
   - What type of report is this?
   - What date/hospital if mentioned?

2. 🔬 **Test Results Analysis**
   - For each test found, show:
     • Test name
     • Patient's value
     • Normal reference range
     • Status: 🟢 Normal / 🟡 Borderline / 🔴 High / 🔵 Low
     • Simple explanation of what this test measures

3. ⚠️ **Key Findings**
   - List abnormal or concerning values clearly

4. 💊 **Medical Suggestions**--give in 3 lines
   - Based on the results, give specific dietary advice
   - Lifestyle changes recommended
   - Medications or supplements to discuss with doctor

5. 🏥 **When to See a Doctor**
   - Which results need urgent attention?
   - What type of specialist should the patient consult?

Write in simple, easy-to-understand language for a non-medical person.
Respond entirely in {lang} language."""

        summary = _gemini(prompt, feature="lab_report")
        loader_ph.empty()
        st.session_state["lab_summary"] = summary

    # ── Translate summary ─────────────────────────────────────────────────
    if trans_clicked and st.session_state.get("lab_summary"):
        loader_ph2 = st.empty()
        show_loader(loader_ph2, f"Translating to {lang}…")

        trans_prompt = (
            f"Translate the following medical summary into {lang} language.\n"
            f"Keep all medical terms accurate. Keep emojis and structure.\n\n"
            f"{st.session_state['lab_summary']}"
        )
        translated = _gemini(trans_prompt, feature="lab_translate")
        loader_ph2.empty()

        if translated.startswith("⚠️"):
            st.error(f"Translation failed: {translated}")
        else:
            st.session_state["lab_summary"] = translated

    # ── Display + download ────────────────────────────────────────────────
    if st.session_state.get("lab_summary"):
        st.markdown("### 🤖 Medical Summary & Suggestions")
        st.info(st.session_state["lab_summary"])

        pdf_bytes = _create_lab_pdf_local(st.session_state["lab_summary"], lang)

        if lang == "English":
            st.download_button(
                "📥 Download Lab Report (PDF)",
                pdf_bytes,
                "lab_report_english.pdf",
                "application/pdf",
            )
        else:
            st.download_button(
                f"📥 Download Lab Report — {lang} (TXT)",
                pdf_bytes,
                f"lab_report_{lang.lower()}.txt",
                "text/plain; charset=utf-8",
            )
            st.caption("💡 Open with Notepad, Word, or any text editor.")