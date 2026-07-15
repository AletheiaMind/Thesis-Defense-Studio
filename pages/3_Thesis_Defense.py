from __future__ import annotations

import streamlit as st

from utils import defense_question, defense_report, initialize_state, inject_custom_css, render_top_nav


st.set_page_config(page_title="Thesis Defense", page_icon="🗣️", layout="centered")
initialize_state()
inject_custom_css()
render_top_nav("defense")

# ── Page header ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="
        background:linear-gradient(135deg,#DC2626 0%,#9333EA 100%);
        border-radius:16px;padding:1.2rem 1.5rem 1rem;margin-bottom:1.2rem;color:#fff;
    ">
        <div style="font-size:1.65rem;font-weight:800;">🗣️ Simulated Thesis Defense</div>
        <div style="font-size:0.9rem;opacity:0.88;margin-top:0.25rem;">
            Answer ~10 questions from your AI examiner, then receive a final score and verdict.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

profile = st.session_state.profile
if not profile["name"]:
    st.warning("⚠️ Add your profile on the Home page first.")

if not st.session_state.paper_summary:
    st.info("📄 Upload a document on the Document Review page first so questions stay on-topic.")

# ── Progress ──────────────────────────────────────────────────────────────────
turns_done = min(st.session_state.defense_turn, 10)
st.markdown(
    f"""
    <div style="
        background:#fff;border-radius:12px;padding:0.9rem 1.1rem;
        border:1px solid #E2E8F0;margin-bottom:0.9rem;
        display:flex;align-items:center;gap:1rem;
    ">
        <div style="flex:1;">
            <div style="font-size:0.78rem;color:#64748B;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">Defense Progress</div>
            <div style="background:#E2E8F0;border-radius:99px;height:8px;margin-top:0.35rem;">
                <div style="background:linear-gradient(90deg,#4F46E5,#7C3AED);width:{turns_done*10}%;height:8px;border-radius:99px;transition:width 0.4s;"></div>
            </div>
        </div>
        <div style="font-size:1.4rem;font-weight:800;color:#4F46E5;">{turns_done}<span style="font-size:1rem;color:#94A3B8;font-weight:500;">/10</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_reset, _ = st.columns([1, 3])
with col_reset:
    if st.button("🔄  Reset Session", key="reset_defense_button"):
        st.session_state.defense_history = []
        st.session_state.defense_turn = 0
        st.session_state.defense_complete = False
        st.session_state.defense_score = None
        st.session_state.defense_conclusion = ""
        st.rerun()

# ── Chat ──────────────────────────────────────────────────────────────────────
if not st.session_state.defense_history:
    opening = defense_question(profile, st.session_state.paper_summary, 0, [])
    st.session_state.defense_history.append(
        {"role": "assistant", "content": f"Hello {profile.get('name', 'student')}. {opening}"}
    )

for message in st.session_state.defense_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.defense_complete:
    answer = st.chat_input("Type your answer here…")
    if answer:
        st.session_state.defense_history.append({"role": "user", "content": answer})
        st.session_state.defense_turn += 1

        if st.session_state.defense_turn >= 10:
            conclusion = defense_report(profile, st.session_state.defense_history, st.session_state.paper_summary)
            st.session_state.defense_history.append({"role": "assistant", "content": conclusion})
            st.session_state.defense_conclusion = conclusion
            st.session_state.defense_score = conclusion
            st.session_state.defense_complete = True
        else:
            next_question = defense_question(
                profile,
                st.session_state.paper_summary,
                st.session_state.defense_turn,
                st.session_state.defense_history,
            )
            st.session_state.defense_history.append({"role": "assistant", "content": next_question})

        st.rerun()

if st.session_state.defense_complete:
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align:center;padding:0.5rem 0 1rem;">
            <span style="font-size:2.5rem;">🏆</span>
            <div style="font-size:1.25rem;font-weight:700;color:#1E293B;margin-top:0.25rem;">Defense Complete!</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown("#### Final Verdict")
        st.markdown(st.session_state.defense_conclusion)
