from __future__ import annotations

import streamlit as st

from utils import initialize_state, inject_custom_css, render_top_nav, save_profile


st.set_page_config(page_title="Thesis Defense Studio", page_icon="🎓", layout="centered")
initialize_state()
inject_custom_css()
render_top_nav("home")

# ── Hero banner ──────────────────────────────────────────────────────────────
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
        st.success("Profile saved! Open the sidebar to continue to Document Review.")

with col_right:
    st.subheader("Studio Overview")
    st.metric("Workflow Steps", "3", delta="Profile → Review → Defense", delta_color="off")
    st.metric("Defense Rounds", "10", delta="Adaptive Q&A session", delta_color="off")
    st.metric("Output", "Score + Verdict", delta="Structured evaluator summary", delta_color="off")
    st.info("Use the **sidebar** (☰) to navigate between pages.")
