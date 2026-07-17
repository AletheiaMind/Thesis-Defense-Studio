from __future__ import annotations

import streamlit as st

from utils import (
    extract_text_from_upload,
    initialize_state,
    inject_custom_css,
    render_top_nav,
    review_paper,
    save_uploaded_document,
    summarize_text,
)


st.set_page_config(page_title="Document Review", page_icon="📄", layout="centered")
initialize_state()
inject_custom_css()
render_top_nav("review")

# ── Page header ──────────────────────────────────────────────────────────────
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
    st.warning("⚠️ Complete your profile on the Home page first so the review can be personalised.")

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
