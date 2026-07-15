from __future__ import annotations

import io
import os
import requests
from dataclasses import dataclass
from typing import Iterable


def inject_custom_css() -> None:
    import streamlit as st

    st.markdown(
        """
<style>
/* ── Global background ── */
.stApp { background-color: #F0F4F8; }

/* ── Hide Streamlit default header & sidebar ── */
header[data-testid="stHeader"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── Top navigation bar ── */
.topnav {
    position: fixed;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    z-index: 99999;
    background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%);
    display: flex;
    align-items: center;
    padding: 0 1.25rem;
    height: 52px;
    box-shadow: 0 2px 14px rgba(0,0,0,0.22);
    gap: 1rem;
    width: calc(100% - 2.5rem);
    max-width: 890px;
}
.topnav-brand {
    color: #fff;
    font-weight: 800;
    font-size: 0.98rem;
    letter-spacing: -0.2px;
    white-space: nowrap;
    flex-shrink: 0;
}
.topnav-links {
    display: flex;
    gap: 0.2rem;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
}
.topnav-links::-webkit-scrollbar { display: none; }
.topnav-links a {
    color: rgba(224,231,255,0.78) !important;
    text-decoration: none !important;
    padding: 0.38rem 0.9rem;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 500;
    white-space: nowrap;
    transition: background 0.15s, color 0.15s;
}
.topnav-links a:hover {
    background: rgba(255,255,255,0.13) !important;
    color: #fff !important;
}
.topnav-links a.active {
    background: rgba(255,255,255,0.22) !important;
    color: #fff !important;
    font-weight: 700 !important;
}

/* ── Main block padding / max-width ── */
.block-container {
    padding: 5rem 1.25rem 3rem 1.25rem !important;
    max-width: 860px !important;
}

/* ── Page header ── */
h1 {
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    color: #1E293B !important;
    letter-spacing: -0.5px;
    margin-bottom: 0.15rem !important;
}
h2, h3 {
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    color: #334155 !important;
}
[data-testid="stCaptionContainer"] p {
    color: #64748B !important;
    font-size: 0.92rem !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.96rem !important;
    min-height: 46px !important;
    transition: all 0.18s ease !important;
    width: 100% !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
    color: #fff !important;
    border: none !important;
    box-shadow: 0 2px 10px rgba(79,70,229,0.32) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 18px rgba(79,70,229,0.45) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:not([kind="primary"]) {
    background: #fff !important;
    border: 1.5px solid #CBD5E1 !important;
    color: #374151 !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: #94A3B8 !important;
    background: #F8FAFC !important;
}

/* ── Text & number inputs ── */
.stTextInput input,
.stNumberInput input {
    border-radius: 8px !important;
    border: 1.5px solid #CBD5E1 !important;
    padding: 0.6rem 0.85rem !important;
    font-size: 1rem !important;
    min-height: 46px !important;
    background: #fff !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.14) !important;
}

/* ── Forms ── */
[data-testid="stForm"] {
    background: #fff !important;
    border-radius: 16px !important;
    padding: 1.4rem !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.93rem !important;
}

/* ── st.metric ── */
[data-testid="metric-container"] {
    background: #fff !important;
    border-radius: 14px !important;
    padding: 1rem 1.1rem !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 1px 5px rgba(0,0,0,0.05) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploadDropzone"] {
    border-radius: 14px !important;
    border: 2px dashed #A5B4FC !important;
    background: #EEF2FF !important;
    min-height: 90px !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #4F46E5, #7C3AED) !important;
    border-radius: 99px !important;
}
.stProgress > div > div {
    border-radius: 99px !important;
    background: #E2E8F0 !important;
}

/* ── Chat ── */
[data-testid="stChatMessage"] {
    border-radius: 14px !important;
    margin-bottom: 0.4rem !important;
}
.stChatInput textarea {
    border-radius: 12px !important;
    border: 1.5px solid #CBD5E1 !important;
    font-size: 1rem !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
    background: #fff !important;
    overflow: hidden !important;
}

/* ── Radio pill-style (tabs fallback) ── */
[data-testid="stRadio"] > div {
    flex-wrap: wrap !important;
    gap: 0.4rem !important;
}
[data-testid="stRadio"] label {
    background: #fff !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 99px !important;
    padding: 0.35rem 0.9rem !important;
    font-size: 0.88rem !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
}

/* ── Mobile: stack columns ── */
@media (max-width: 640px) {
    .block-container { padding: 4.5rem 0.75rem 2rem 0.75rem !important; }
    .topnav { width: calc(100% - 1.5rem); padding: 0 0.75rem; gap: 0.5rem; }
    .topnav-brand { display: none; }
    .topnav-links a { padding: 0.35rem 0.6rem; font-size: 0.82rem; }
    h1 { font-size: 1.4rem !important; }
    [data-testid="column"] {
        width: 100% !important;
        flex: 0 0 100% !important;
        min-width: 100% !important;
    }
    .stButton > button { font-size: 1rem !important; min-height: 50px !important; }
}
</style>
""",
        unsafe_allow_html=True,
    )

def render_top_nav(current_page: str = "home") -> None:
    """Render a fixed top navigation bar and hide the Streamlit sidebar."""
    import streamlit as st

    pages = [
        ("home", "🎓 Home", "/"),
        ("review", "📄 Document Review", "/Document_Review"),
        ("defense", "🗣️ Thesis Defense", "/Thesis_Defense"),
    ]

    items_html = "".join(
        f'<a href="{url}" class="{"active" if key == current_page else ""}">{label}</a>'
        for key, label, url in pages
    )

    st.markdown(
        f"""
        <div class="topnav">
            <span class="topnav-brand">🎓 Thesis Defense Studio</span>
            <nav class="topnav-links">{items_html}</nav>
        </div>
        """,
        unsafe_allow_html=True,
    )


from docx import Document
from pypdf import PdfReader


@dataclass
class ReviewResult:
    strengths: str
    weaknesses: str
    suggestions: str
    summary: str


def initialize_state() -> None:
    import streamlit as st

    defaults = {
        "profile": {"name": "", "age": 0, "school": ""},
        "paper_text": "",
        "paper_summary": "",
        "review_result": None,
        "defense_history": [],
        "defense_turn": 0,
        "defense_complete": False,
        "defense_score": None,
        "defense_conclusion": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_profile(name: str, age: int, school: str) -> None:
    import streamlit as st

    st.session_state.profile = {"name": name.strip(), "age": age, "school": school.strip()}


def extract_text_from_upload(uploaded_file) -> str:
    suffix = uploaded_file.name.lower().split(".")[-1]
    data = uploaded_file.getvalue()

    if suffix == "txt":
        return data.decode("utf-8", errors="ignore")

    if suffix == "pdf":
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if suffix == "docx":
        document = Document(io.BytesIO(data))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")


def summarize_text(text: str, limit: int = 1800) -> str:
    cleaned = " ".join(text.split())
    return cleaned[:limit]


def build_review_prompt(profile: dict, paper_text: str) -> str:
    return (
        f"You are an expert academic reviewer. Review the following student paper written by "
        f"{profile.get('name', 'the student')} from {profile.get('school', 'their school')}. "
        "Provide constructive feedback divided into Strengths, Weaknesses, and Actionable Improvement Suggestions. "
        "Be practical, specific, and supportive.\n\n"
        f"Student age: {profile.get('age', 'unknown')}\n\n"
        f"Paper text:\n{paper_text}"
    )


def build_defense_question(profile: dict, paper_summary: str, turn: int, history: Iterable[dict]) -> str:
    recent = list(history)[-4:]
    context = "\n".join(f"{item['role']}: {item['content']}" for item in recent)
    if turn == 0:
        prompt = "Start the thesis defense with a challenging first question."
    else:
        prompt = "Ask the next challenging follow-up question based on the student's last answer."

    return (
        f"You are a strict but fair thesis defense teacher. {prompt} "
        f"The student is {profile.get('name', 'the student')} from {profile.get('school', 'their school')}. "
        f"Use this paper summary to stay grounded in the topic:\n{paper_summary}\n\n"
        f"Recent dialogue:\n{context if context else 'No prior dialogue.'}\n\n"
        "Return only the next teacher question, plus one short sentence of critique if appropriate."
    )


def build_final_defense_report(profile: dict, history: Iterable[dict], paper_summary: str) -> str:
    dialogue = "\n".join(f"{item['role']}: {item['content']}" for item in history)
    return (
        f"You are a thesis defense evaluator. Review the full dialogue and give a final conclusion and score out of 100. "
        f"The student is {profile.get('name', 'the student')} from {profile.get('school', 'their school')}. "
        f"Use the paper summary as background:\n{paper_summary}\n\n"
        f"Conversation:\n{dialogue}\n\n"
        "Return markdown with sections: Defense Summary, Strengths, Concerns, Final Score, and Final Verdict."
    )


def local_review_fallback(profile: dict, paper_text: str) -> ReviewResult:
    word_count = len(paper_text.split())
    summary = summarize_text(paper_text, 500)
    strengths = (
        f"The draft from {profile.get('name', 'the student')} appears to be a solid starting point. "
        "The argument structure can be strengthened by clearer transitions and explicit thesis signaling."
    )
    weaknesses = (
        "The prototype fallback cannot read nuance deeply, but the draft should still be checked for clarity, evidence density, "
        "and whether each section directly supports the central claim."
    )
    suggestions = (
        f"1. Expand the introduction and conclusion.\n2. Add more citations and explain why each matters.\n"
        f"3. Revise for consistency in terminology.\n4. Consider a tighter outline.\n\nWord count detected: {word_count}."
    )
    return ReviewResult(strengths=strengths, weaknesses=weaknesses, suggestions=suggestions, summary=summary)


def local_defense_question(profile: dict, paper_summary: str, turn: int) -> str:
    topic = paper_summary[:220] or "the paper topic"
    questions = [
        f"Can you explain the core research problem in {topic}?",
        "Why is this problem important, and who benefits from solving it?",
        "What assumptions does your approach rely on, and how could they fail?",
        "How did you evaluate whether your method was effective?",
        "What is the strongest criticism of your work?",
        "How does your work differ from existing approaches?",
        "What would you improve if you had two more weeks?",
        "Which part of the thesis is most vulnerable to challenge?",
        "How would you defend your contribution to a skeptical reviewer?",
        "What is the single most important takeaway from your defense?",
    ]
    idx = min(turn, len(questions) - 1)
    return f"{questions[idx]}"


def local_defense_report(profile: dict, history: Iterable[dict]) -> str:
    rounds = sum(1 for item in history if item["role"] == "user")
    score = max(60, 92 - max(0, 10 - rounds) * 2)
    return (
        f"**Defense Summary**\n\n"
        f"{profile.get('name', 'The student')} completed {rounds} response rounds in the simulated defense. "
        "The answers showed baseline understanding, but some responses would benefit from sharper evidence, clearer definitions, and more confident defense of methodology.\n\n"
        f"**Final Score**\n\n{score}/100\n\n"
        "**Final Verdict**\n\nPass with revisions recommended."
    )


def get_nvidia_api_key() -> str | None:
    import streamlit as st
    """Get Nvidia API key from environment variable."""
    #return os.getenv("NVIDIA_API_KEY")
    return st.secrets["NVIDIA_API_KEY"]


def generate_ai_text(system_prompt: str, user_prompt: str) -> str:
    import streamlit as st
    """Generate text using Nvidia LLM endpoint."""
    api_key = get_nvidia_api_key()
    if not api_key:
        return ""

    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    payload = {
        "model": st.secrets.get("NVIDIA_MODEL", "qwen/qwen3.5-397b-a17b"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 2048,
        "temperature": 0.70,
        "top_p": 0.95,
        "stream": False,
    }

    try:
        response = requests.post(invoke_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException:
        pass

    return ""


def review_paper(profile: dict, paper_text: str) -> ReviewResult:
    system_prompt = "You are a careful academic writing reviewer."
    prompt = build_review_prompt(profile, paper_text)
    ai_text = generate_ai_text(system_prompt, prompt)
    if ai_text:
        return ReviewResult(
            strengths=ai_text,
            weaknesses="See the generated critique above.",
            suggestions="Use the AI output directly for the full review.",
            summary=summarize_text(paper_text),
        )
    return local_review_fallback(profile, paper_text)


def defense_question(profile: dict, paper_summary: str, turn: int, history: Iterable[dict]) -> str:
    system_prompt = "You simulate a strict thesis defense examiner."
    prompt = build_defense_question(profile, paper_summary, turn, history)
    ai_text = generate_ai_text(system_prompt, prompt)
    return ai_text or local_defense_question(profile, paper_summary, turn)


def defense_report(profile: dict, history: Iterable[dict], paper_summary: str) -> str:
    system_prompt = "You are an academic defense evaluator."
    prompt = build_final_defense_report(profile, history, paper_summary)
    ai_text = generate_ai_text(system_prompt, prompt)
    return ai_text or local_defense_report(profile, history)
