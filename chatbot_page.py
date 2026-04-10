import streamlit as st
import datetime
from datetime import datetime
import pytz

def show_chatbot(username, _init_chat_state, _new_chat, _get_active_session,
                 _auto_title, _delete_chat, _save_user_history, _call_rag,
                 show_loader):

    _init_chat_state(username)

    if not st.session_state.chat_sessions:
        _new_chat(username)
    if _get_active_session() is None and st.session_state.chat_sessions:
        st.session_state.active_chat_id = st.session_state.chat_sessions[0]["id"]

    st.markdown("""
    <style>
    /* ══════════════════════════════════════════════════════════════════════
       CHATBOT PAGE — FULL BACKGROUND & LAYOUT
    ══════════════════════════════════════════════════════════════════════ */

    /* Wrap entire chatbot section in a soft gradient background */
    .chatbot-wrapper {
        background: linear-gradient(135deg, #eef2ff 0%, #f0f9ff 50%, #faf5ff 100%);
        border-radius: 20px;
        padding: 1.5rem 1.5rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 24px rgba(30,58,95,0.08), 0 1px 4px rgba(30,58,95,0.04);
        border: 1px solid rgba(99,102,241,0.1);
    }

    /* Page title styling */
    .chatbot-page-title {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e3a5f, #3b82f6, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        letter-spacing: -0.5px;
    }

    /* ── History anchor scope ───────────────────────────────────────────── */
    .hist-box-anchor { display:none; }

    /* All buttons inside hist col */
    div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .stButton > button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #94a3b8 !important;
        font-size: 0.82rem !important;
        font-weight: 400 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 0.5rem 0.9rem !important;
        border-radius: 0 !important;
        width: 100% !important;
        border-bottom: 1px solid rgba(255,255,255,0.04) !important;
        min-height: 40px !important;
        transition: background 0.12s, color 0.12s !important;
    }
    div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .stButton > button:hover {
        background: rgba(255,255,255,0.06) !important;
        color: #e2e8f0 !important;
    }
    /* Active history item */
    div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .active-btn .stButton > button {
        background: rgba(59,130,246,0.2) !important;
        border-left: 3px solid #3b82f6 !important;
        color: #93c5fd !important;
        font-weight: 500 !important;
        padding-left: 0.7rem !important;
    }

    /* Inline delete button */
    div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .del-inline-btn .stButton > button {
        background: rgba(239,68,68,0.1) !important;
        border: 1px solid rgba(239,68,68,0.25) !important;
        border-radius: 0 0 6px 6px !important;
        color: #fca5a5 !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        padding: 0.2rem 0.7rem !important;
        width: 100% !important;
        min-height: unset !important;
        text-align: center !important;
        justify-content: center !important;
        border-bottom: 1px solid rgba(239,68,68,0.25) !important;
        margin-top: -1px !important;
    }
    div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .del-inline-btn .stButton > button:hover {
        background: rgba(239,68,68,0.25) !important;
        color: white !important;
    }
    /* New Chat / Clear action buttons */
    div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .action-btn .stButton > button {
        background: rgba(59,130,246,0.18) !important;
        border: 1px solid rgba(59,130,246,0.35) !important;
        border-radius: 8px !important;
        color: #60a5fa !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        width: auto !important;
        text-align: center !important;
        justify-content: center !important;
        min-height: unset !important;
        border-bottom: 1px solid rgba(59,130,246,0.35) !important;
        padding: 0.35rem 0.7rem !important;
    }
    div[data-testid="stVerticalBlock"]:has(.hist-box-anchor) .clear-btn .stButton > button {
        background: rgba(239,68,68,0.12) !important;
        border: 1px solid rgba(239,68,68,0.3) !important;
        border-radius: 8px !important;
        color: #fca5a5 !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        width: auto !important;
        text-align: center !important;
        justify-content: center !important;
        min-height: unset !important;
        border-bottom: 1px solid rgba(239,68,68,0.3) !important;
        padding: 0.35rem 0.7rem !important;
    }

    /* ── Left history panel ─────────────────────────────────────────────── */
    .hist-panel-wrap {
        background: #0f172a;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        border: 1px solid rgba(255,255,255,0.06);
    }
    .hist-scroll-area {
        max-height: 400px;
        overflow-y: auto;
        scrollbar-width: thin;
        scrollbar-color: #3b82f6 #1a1a2e;
        background: #1a1a2e;
    }
    .hist-scroll-area::-webkit-scrollbar { width: 4px; }
    .hist-scroll-area::-webkit-scrollbar-thumb {
        background: #3b82f6; border-radius: 4px;
    }

    /* ── Right chat window ──────────────────────────────────────────────── */
    .chat-panel-wrap {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(30,58,95,0.1);
        border: 1px solid rgba(99,102,241,0.12);
    }
    .chat-scroll-area {
        max-height: 460px;
        overflow-y: auto;
        padding: 1.2rem;
        background: linear-gradient(180deg, #f8faff 0%, #ffffff 100%);
        border: 1px solid #e8eef8;
        border-top: none;
        border-radius: 0 0 14px 14px;
        scrollbar-width: thin;
        scrollbar-color: #3b82f6 #f0f4ff;
    }
    .chat-scroll-area::-webkit-scrollbar { width: 5px; }
    .chat-scroll-area::-webkit-scrollbar-thumb {
        background: linear-gradient(#3b82f6, #7c3aed);
        border-radius: 5px;
    }

    /* ── Chat header ─────────────────────────────────────────────────────── */
    .chat-win-hdr {
        background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 60%, #4f46e5 100%);
        border-radius: 14px 14px 0 0;
        padding: 0.9rem 1.3rem;
        font-weight: 700;
        color: #e2e8f0;
        font-size: 1rem;
        box-shadow: 0 3px 14px rgba(15,52,96,0.35);
        letter-spacing: 0.01em;
    }

    /* ── Empty state welcome box ─────────────────────────────────────────── */
    .chat-empty-state {
        background: linear-gradient(135deg, #eef2ff 0%, #f0f9ff 100%);
        border: 1px solid rgba(99,102,241,0.15);
        border-top: none;
        border-radius: 0 0 14px 14px;
        padding: 2.5rem 1.5rem;
        text-align: center;
    }

    /* ── Suggestion section label ────────────────────────────────────────── */
    .sug-label {
        font-size: 0.72rem;
        color: #6366f1;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 1rem 0 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* ── Suggestion buttons — transparent over coloured card ────────────── */
    .sug-btn-1 .stButton > button,
    .sug-btn-2 .stButton > button,
    .sug-btn-3 .stButton > button,
    .sug-btn-4 .stButton > button {
        background: transparent !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 0.8rem 1rem !important;
        width: 100% !important;
        white-space: normal !important;
        height: auto !important;
        min-height: 64px !important;
        line-height: 1.45 !important;
        box-shadow: none !important;
        transition: opacity 0.15s !important;
    }
    .sug-btn-1 .stButton > button:hover,
    .sug-btn-2 .stButton > button:hover,
    .sug-btn-3 .stButton > button:hover,
    .sug-btn-4 .stButton > button:hover {
        opacity: 0.88 !important;
        background: rgba(255,255,255,0.08) !important;
    }

    /* ── Chat input box ──────────────────────────────────────────────────── */
    [data-testid="stChatInput"] {
        border-radius: 14px !important;
        border: 2px solid rgba(99,102,241,0.2) !important;
        background: white !important;
        box-shadow: 0 2px 12px rgba(99,102,241,0.1) !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }

    /* ── Chat messages ───────────────────────────────────────────────────── */
    [data-testid="stChatMessage"] {
        border-radius: 14px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        margin-bottom: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Coloured background wrapper ───────────────────────────────────────
    st.markdown("<div class='chatbot-wrapper'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='chatbot-page-title'>💬 Medical Chatbot</div>",
        unsafe_allow_html=True
    )

    hist_col, chat_col = st.columns([1.5, 3], gap="medium")

    # ── LEFT — scrollable history panel ──────────────────────────────────────
    with hist_col:
        st.markdown("<div class='hist-box-anchor'></div>", unsafe_allow_html=True)
        st.markdown("<div class='hist-panel-wrap'>", unsafe_allow_html=True)

        # Dark header
        st.markdown("""
        <div style='background:#16213e;padding:0.7rem 0.9rem 0.6rem;
                    border-bottom:1px solid rgba(255,255,255,0.08);
                    border-radius:16px 16px 0 0;'>
            <span style='font-size:0.68rem;font-weight:700;color:#475569;
                         text-transform:uppercase;letter-spacing:0.09em;'>
                🕐 Chat History
            </span>
        </div>
        """, unsafe_allow_html=True)

        # New Chat button always visible. Clear only when active chat has messages.
        active_sess_check = _get_active_session()
        has_msgs = bool(active_sess_check and active_sess_check.get("messages"))

        if has_msgs:
            ab1, ab2 = st.columns([1, 1])
            with ab1:
                st.markdown("<div class='action-btn'>", unsafe_allow_html=True)
                if st.button("✏️ New Chat", key="new_chat_btn", width='stretch'):
                    _new_chat(username)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with ab2:
                st.markdown("<div class='clear-btn'>", unsafe_allow_html=True)
                if st.button("🗑️ Clear", key="clear_hist_btn", width='stretch'):
                    active_sess_check["messages"] = []
                    _save_user_history(username, st.session_state.chat_sessions)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='action-btn'>", unsafe_allow_html=True)
            if st.button("✏️ New Chat", key="new_chat_btn", width='stretch'):
                _new_chat(username)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:0.15rem;background:#1a1a2e;'></div>",
                    unsafe_allow_html=True)

        # Scrollable history list
        st.markdown("<div class='hist-scroll-area'>", unsafe_allow_html=True)

        if not st.session_state.chat_sessions:
            st.markdown("""
            <div style='padding:2rem 1rem;text-align:center;
                        font-size:0.8rem;color:#475569;background:#1a1a2e;'>
                No chats yet.<br>
                <span style='color:#60a5fa;'>Click ✏️ New to start.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            for sess in st.session_state.chat_sessions:
                is_active = sess["id"] == st.session_state.active_chat_id
                label     = sess.get("title") or "New Chat"
                date_str  = sess.get("date", "")
                q_count   = len([m for m in sess["messages"] if m["role"] == "user"])

                # Single full-width button — no misaligned X column
                if is_active:
                    st.markdown("<div class='active-btn'>", unsafe_allow_html=True)
                if st.button(
                    f"{'▶ ' if is_active else ''}{label}",
                    key=f"hist_{sess['id']}",
                    width='stretch',
                    help=f"{date_str} · {q_count} question(s)"
                ):
                    st.session_state.active_chat_id = sess["id"]
                    st.rerun()
                if is_active:
                    st.markdown("</div>", unsafe_allow_html=True)
                    # Show delete button only for active (selected) item
                    st.markdown("<div class='del-inline-btn'>", unsafe_allow_html=True)
                    if st.button("🗑️ Delete this chat", key=f"del_{sess['id']}", width='stretch'):
                        _delete_chat(sess["id"], username)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # close hist-scroll-area

        # Bottom rounded corner + close panel wrap
        st.markdown("""
        <div style='background:#0f172a;min-height:16px;
                    border-radius:0 0 16px 16px;'></div>
        </div>
        """, unsafe_allow_html=True)

    # ── RIGHT — scrollable chat window ────────────────────────────────────────
    with chat_col:
        active_sess = _get_active_session()
        chat_title  = active_sess.get("title", "Chat") if active_sess else "Chat"

        st.markdown(
            f'<div class="chat-win-hdr">💬 &nbsp;{chat_title}</div>',
            unsafe_allow_html=True)

        if not active_sess or not active_sess["messages"]:
            st.markdown("""
            <div class='chat-empty-state'>
                <div style='font-size:3rem;margin-bottom:0.8rem;
                            filter:drop-shadow(0 4px 10px rgba(99,102,241,0.25));'>🏥</div>
                <div style='font-weight:700;color:#1e3a5f;font-size:1.15rem;
                            margin-bottom:0.5rem;'>How can I help you today?</div>
                <div style='color:#6b7280;font-size:0.87rem;line-height:1.7;'>
                    Ask about symptoms, medications,<br>lab results, or any health topic.
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(
                "<div class='sug-label'>💡 Try one of these</div>",
                unsafe_allow_html=True)

            # Coloured background cards for each suggestion
            suggestions = [
                ("🩺 What does a high HbA1c mean?",
                 "linear-gradient(135deg,#1e3a5f,#2563eb)",
                 "rgba(37,99,235,0.3)"),
                ("💓 How can I lower my blood pressure naturally?",
                 "linear-gradient(135deg,#065f46,#059669)",
                 "rgba(5,150,105,0.3)"),
                ("🫘 What are early signs of kidney disease?",
                 "linear-gradient(135deg,#6d28d9,#7c3aed)",
                 "rgba(124,58,237,0.3)"),
                ("⚖️ Is a BMI of 28 a concern?",
                 "linear-gradient(135deg,#b45309,#d97706)",
                 "rgba(217,119,6,0.3)"),
            ]
            sc1, sc2 = st.columns(2)
            for i, (sug, bg, shadow) in enumerate(suggestions):
                with (sc1 if i % 2 == 0 else sc2):
                    st.markdown(
                        f"<div style='background:{bg};"
                        f"border-radius:14px;padding:0.1rem 0.2rem;"
                        f"box-shadow:0 4px 16px {shadow};"
                        f"margin-bottom:0.6rem;'>",
                        unsafe_allow_html=True
                    )
                    if st.button(sug, key=f"sug_{i}", width='stretch'):
                        _auto_title(active_sess, sug, username)
                        ts = datetime.now().strftime("%I:%M %p")
                        active_sess["messages"].append(
                            {"role": "user", "content": sug, "time": ts})
                        _save_user_history(username, st.session_state.chat_sessions)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Scrollable message area
            st.markdown("<div class='chat-scroll-area'>", unsafe_allow_html=True)
            for msg in active_sess["messages"]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    if "time" in msg:
                        st.caption(msg["time"])
            st.markdown("</div>", unsafe_allow_html=True)

        # Generate answer
        active_sess = _get_active_session()
        if (active_sess and active_sess["messages"]
                and active_sess["messages"][-1]["role"] == "user"):
            pending_q = active_sess["messages"][-1]["content"]
            loader_ph = st.empty()
            show_loader(loader_ph, "Thinking…")
            ans = _call_rag(pending_q)
            loader_ph.empty()
            ist = pytz.timezone("Asia/Kolkata")
            ts_a= datetime.now(ist).strftime("%I:%M %p")
            #ts_a = datetime.datetime.now().strftime("%I:%M %p")
            with st.chat_message("assistant"):
                st.write(ans)
                st.caption(ts_a)
            active_sess["messages"].append(
                {"role": "assistant", "content": ans, "time": ts_a})
            _save_user_history(username, st.session_state.chat_sessions)

        q = st.chat_input("Ask your medical question…", key="medical_chat_input")
        if q:
            active_sess = _get_active_session()
            _auto_title(active_sess, q, username)
            ts = datetime.now(ist).strftime("%I:%M %p")
            active_sess["messages"].append({"role": "user", "content": q, "time": ts})
            _save_user_history(username, st.session_state.chat_sessions)
            st.rerun()

    # Close outer background wrapper
    st.markdown("</div>", unsafe_allow_html=True)


# # chatbot_page.py
# """
# Medical Chatbot page.
#   • Persistent chat sessions (stored in chat_history/{username}.json)
#   • Sessions capped at MAX_CHAT_SESSIONS (default 50) — oldest auto-pruned
#   • Original dark sidebar styling restored
#   • No session count badge shown to user
# """
# import streamlit as st


# def show_chatbot(
#     username: str,
#     _init_chat_state,
#     _new_chat,
#     _get_active_session,
#     _auto_title,
#     _delete_chat,
#     _save_user_history,
#     _call_rag,
#     show_loader,
#     max_sessions: int = 50,
# ):
#     st.markdown("## 💬 Medical Chatbot")

#     # ── Init persistent state ─────────────────────────────────────────────
#     _init_chat_state(username)

#     # ── Layout: history panel (left) + chat window (right) ───────────────
#     left_col, right_col = st.columns([1, 3])

#     # ══════════════════════════════════════════════════════════════════════
#     # LEFT — chat history panel  (original dark styling)
#     # ══════════════════════════════════════════════════════════════════════
#     with left_col:
#         st.markdown("<span class='hist-box-anchor'></span>", unsafe_allow_html=True)

#         # ── New chat button ───────────────────────────────────────────────
#         st.markdown("<div class='action-btn'>", unsafe_allow_html=True)
#         if st.button("＋ New Chat", key="new_chat_btn"):
#             _new_chat(username)
#             st.rerun()
#         st.markdown("</div>", unsafe_allow_html=True)

#         st.markdown(
#             "<div style='font-size:0.7rem;color:#475569;text-transform:uppercase;"
#             "letter-spacing:0.08em;margin:0.6rem 0 0.2rem;'>Recent chats</div>",
#             unsafe_allow_html=True,
#         )

#         # ── Session list ──────────────────────────────────────────────────
#         for session in st.session_state.chat_sessions:
#             cid      = session["id"]
#             title    = session["title"]
#             date     = session.get("date", "")
#             is_active = cid == st.session_state.active_chat_id

#             row_l, row_r = st.columns([5, 1])
#             with row_l:
#                 _cls = "active-btn" if is_active else ""
#                 st.markdown(f"<div class='{_cls}'>", unsafe_allow_html=True)
#                 if st.button(
#                     f"{'▶ ' if is_active else ''}{title}\n{date}",
#                     key=f"sess_{cid}",
#                 ):
#                     st.session_state.active_chat_id = cid
#                     st.rerun()
#                 st.markdown("</div>", unsafe_allow_html=True)
#             with row_r:
#                 st.markdown("<div class='del-btn'>", unsafe_allow_html=True)
#                 if st.button("🗑", key=f"del_{cid}"):
#                     _delete_chat(cid, username)
#                     st.rerun()
#                 st.markdown("</div>", unsafe_allow_html=True)

#         # ── Clear all ─────────────────────────────────────────────────────
#         if st.session_state.chat_sessions:
#             st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
#             st.markdown("<div class='clear-btn'>", unsafe_allow_html=True)
#             if st.button("🗑 Clear All", key="clear_all_btn"):
#                 st.session_state.chat_sessions  = []
#                 st.session_state.active_chat_id = None
#                 _save_user_history(username, [])
#                 st.rerun()
#             st.markdown("</div>", unsafe_allow_html=True)

#     # ══════════════════════════════════════════════════════════════════════
#     # RIGHT — chat window
#     # ══════════════════════════════════════════════════════════════════════
#     with right_col:
#         session = _get_active_session()

#         if session is None:
#             st.markdown(
#                 "<div style='text-align:center;padding:3rem 0;color:#94a3b8;'>"
#                 "<div style='font-size:3rem;margin-bottom:0.5rem;'>💬</div>"
#                 "<div style='font-size:1rem;font-weight:500;'>No chat selected</div>"
#                 "<div style='font-size:0.85rem;margin-top:0.3rem;'>"
#                 "Click <b>＋ New Chat</b> to start a conversation</div>"
#                 "</div>",
#                 unsafe_allow_html=True,
#             )
#             return

#         # Header
#         st.markdown(
#             f"<div class='chat-win-hdr'>💬 {session['title']}"
#             f"<span style='float:right;font-size:0.75rem;color:#94a3b8;'>"
#             f"{session.get('date','')}</span></div>",
#             unsafe_allow_html=True,
#         )

#         # Message history
#         for msg in session["messages"]:
#             with st.chat_message(msg["role"]):
#                 st.markdown(msg["content"])

#         # Input
#         user_input = st.chat_input("Ask a medical question…")
#         if user_input:
#             session["messages"].append({"role": "user", "content": user_input})
#             _auto_title(session, user_input, username)
#             _save_user_history(username, st.session_state.chat_sessions)

#             with st.chat_message("user"):
#                 st.markdown(user_input)

#             with st.chat_message("assistant"):
#                 loader_ph = st.empty()
#                 show_loader(loader_ph, "Thinking…")
#                 answer = _call_rag(user_input)
#                 loader_ph.empty()
#                 st.markdown(answer)

#             session["messages"].append({"role": "assistant", "content": answer})
#             _save_user_history(username, st.session_state.chat_sessions)
#             st.rerun()