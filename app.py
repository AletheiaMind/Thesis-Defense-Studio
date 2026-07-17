from __future__ import annotations

import streamlit as st

from utils import (
    initialize_state,
    inject_custom_css,
    save_profile,
    extract_text_from_upload,
    review_paper,
    save_uploaded_document,
    summarize_text,
    defense_question,
    defense_report,
)


st.set_page_config(page_title="Thesis Defense Studio", page_icon="🎓", layout="centered")
initialize_state()
inject_custom_css()

# ── Custom tab navigation at top ──────────────────────────────────────────────
st.markdown(
    """
    <div class="topnav">
        <span class="topnav-brand">🎓 Thesis Defense Studio</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Tab selection ────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🏠 Home", "📄 Document Review", "🗣️ Thesis Defense"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: HOME
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg,#4F46E5 0%,#7C3AED 100%);
            border-radius: 18px;
            padding: 1.5rem 1.75rem 1.2rem;
            margin-bottom: 1.4rem;
            color: #fff;
        ">
            <div style="font-size:2.2rem;font-weight:800;letter-spacing:-0.5px;line-height:1.2;">🎓 Thesis Defense Studio</div>
            <div style="font-size:0.95rem;opacity:0.88;margin-top:0.35rem;">
                AI-powered academic preparation &mdash; review your thesis and ace the defense.
            </div>
            <div style="display:flex;gap:0.6rem;margin-top:0.9rem;flex-wrap:wrap;">
                <span style="background:rgba(255,255,255,0.22);border-radius:99px;padding:0.2rem 0.75rem;font-size:0.8rem;font-weight:600;">① Profile</span>
                <span style="background:rgba(255,255,255,0.13);border-radius:99px;padding:0.2rem 0.75rem;font-size:0.8rem;">② Document Review</span>
                <span style="background:rgba(255,255,255,0.13);border-radius:99px;padding:0.2rem 0.75rem;font-size:0.8rem;">③ Thesis Defense</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.profile["name"]:
        st.success(
            f"Signed in as **{st.session_state.profile['name']}** · "
            f"Age {st.session_state.profile['age']} · "
            f"{st.session_state.profile['school']}"
        )

    if st.session_state.get("uploaded_document"):
        doc = st.session_state.get("uploaded_document")
        size_kb = (doc.get("size_bytes", 0) or 0) / 1024
        st.info(f"Current shared document: **{doc.get('name', 'Unknown')}** ({size_kb:.1f} KB)")

    col_left, col_right = st.columns([1.1, 0.9])

    with col_left:
        st.subheader("Your Profile")
        with st.form("profile_form", clear_on_submit=False):
            name = st.text_input("Full Name", value=st.session_state.profile.get("name", ""), placeholder="e.g. Jane Smith")
            age = st.number_input("Age", min_value=1, max_value=120, value=int(st.session_state.profile.get("age", 18) or 18))
            school = st.text_input("School / University", value=st.session_state.profile.get("school", ""), placeholder="e.g. MIT")
            submitted = st.form_submit_button("💾  Save Profile", type="primary")

        if submitted:
            save_profile(name, int(age), school)
            st.success("Profile saved! Continue to Document Review.")

    with col_right:
        st.subheader("Studio Overview")
        st.metric("Workflow Steps", "3", delta="Profile → Review → Defense", delta_color="off")
        st.metric("Defense Rounds", "10", delta="Adaptive Q&A session", delta_color="off")
        st.metric("Output", "Score + Verdict", delta="Structured evaluator summary", delta_color="off")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: DOCUMENT REVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        """
        <div style="
            background:linear-gradient(135deg,#0EA5E9 0%,#6366F1 100%);
            border-radius:16px;padding:1.2rem 1.5rem 1rem;margin-bottom:1.2rem;color:#fff;
        ">
            <div style="font-size:1.65rem;font-weight:800;">📄 Document Review</div>
            <div style="font-size:0.9rem;opacity:0.88;margin-top:0.25rem;">
                Upload your thesis or paper and receive structured AI feedback.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    profile = st.session_state.profile
    if not profile["name"]:
        st.warning("⚠️ Complete your profile on the Home tab first so the review can be personalised.")

    st.subheader("1 · Upload your document")
    uploaded = st.file_uploader("Supported formats: PDF, DOCX, TXT", type=["pdf", "docx", "txt"])

    if st.session_state.get("uploaded_document"):
        doc = st.session_state.get("uploaded_document")
        size_kb = (doc.get("size_bytes", 0) or 0) / 1024
        st.caption(f"Current shared document: {doc.get('name', 'Unknown')} ({size_kb:.1f} KB)")

    if uploaded:
        try:
            paper_text = extract_text_from_upload(uploaded)
            paper_summary = summarize_text(paper_text)
            save_uploaded_document(uploaded, paper_text, paper_summary)
            st.success(f"✅ **{uploaded.name}** parsed successfully.")

            words = len(st.session_state.paper_text.split())
            chars = len(st.session_state.paper_text)
            metric_left, metric_right = st.columns(2)
            with metric_left:
                st.metric("Words detected", f"{words:,}")
            with metric_right:
                st.metric("Characters detected", f"{chars:,}")
        except Exception as exc:
            st.error(str(exc))

    if st.session_state.paper_text:
        with st.expander("📋 Extracted text preview"):
            st.write(st.session_state.paper_summary)

        st.subheader("2 · Generate review")
        if st.button("✨  Generate AI Review", type="primary", key="review_generate_button"):
            with st.spinner("Analysing your document…"):
                result = review_paper(profile, st.session_state.paper_text)
            st.session_state.review_result = result

    if st.session_state.review_result:
        st.subheader("3 · Review results")
        result = st.session_state.review_result
        selected_tab = st.radio(
            "Section",
            ["Strengths", "Weaknesses", "Improvement Suggestions", "Condensed Summary"],
            horizontal=True,
            key="review_result_tabs",
            label_visibility="collapsed",
        )

        with st.container(border=True):
            if selected_tab == "Strengths":
                st.markdown("### ✅ Strengths")
                st.markdown(result.strengths)
            elif selected_tab == "Weaknesses":
                st.markdown("### ⚠️ Weaknesses")
                st.markdown(result.weaknesses)
            elif selected_tab == "Improvement Suggestions":
                st.markdown("### 💡 Improvement Suggestions")
                st.markdown(result.suggestions)
            else:
                st.markdown("### 📝 Condensed Summary")
                st.write(result.summary)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: THESIS DEFENSE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
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
        st.warning("⚠️ Add your profile on the Home tab first.")

    if not st.session_state.paper_summary:
        st.info("📄 Upload a document on the Document Review tab first so questions stay on-topic.")
    elif st.session_state.get("uploaded_document"):
        doc = st.session_state.get("uploaded_document")
        size_kb = (doc.get("size_bytes", 0) or 0) / 1024
        st.caption(f"Using shared document: {doc.get('name', 'Unknown')} ({size_kb:.1f} KB)")

    # ── Progress ──────────────────────────────────────────────────────────────
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

    # ── Chat ──────────────────────────────────────────────────────────────────
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
