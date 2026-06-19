"""
app.py  —  Circuit Design Q&A Tutor  (Groq Edition)
Light-theme Streamlit app powered by Groq llama-3.3-70b-versatile (FREE).

Run:  streamlit run app.py
Key:  https://console.groq.com/keys  (free, no credit card)
"""

import os
import json
import streamlit as st

# ── Load dotenv before anything else ──────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass

from tutor_engine    import TutorEngine
from circuit_analyzer import (
    get_topics, FORMULA_LIBRARY, SAMPLE_PROBLEMS,
    calc_ohms_law, calc_rc, calc_rl, calc_rlc, calc_vdiv, calc_opamp,
)
from graph_generator import (
    get_graph_for_topic,
    plot_ohms_law, plot_power, plot_rc, plot_rl, plot_rlc,
    plot_signals, plot_opamp, plot_diode, plot_bjt, plot_logic,
)
from utils import (
    init_session, record_question, record_quiz, save_solution,
    to_markdown, to_json, to_html, generate_env_file, load_api_key,
    KEY_PROGRESS, KEY_SOLUTIONS, KEY_QUIZ,
)

# ─────────────────────────────────────────────────────────────────────────────
# Page config — MUST be first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Circuit Tutor AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

# ─────────────────────────────────────────────────────────────────────────────
# Global CSS  (light theme)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #F1F5F9 !important;
    color: #1E293B !important;
}
.stApp { background: #F1F5F9; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E2E8F0;
    box-shadow: 2px 0 8px rgba(0,0,0,0.06);
}
[data-testid="stSidebar"] * { color: #1E293B !important; }

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 40%, #3B82F6 100%);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 28px;
    box-shadow: 0 4px 24px rgba(37,99,235,0.18);
}
.hero h1 {
    font-size: 2.2rem; font-weight: 700;
    color: #FFFFFF; margin: 0 0 8px 0; letter-spacing: -0.5px;
}
.hero p { color: #BFDBFE; margin: 0; font-size: 1rem; }
.groq-badge {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    color: #FFFFFF;
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    margin-top: 10px;
}

/* ── Cards ── */
.card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.card-blue   { border-left: 4px solid #3B82F6; }
.card-green  { border-left: 4px solid #22C55E; }
.card-amber  { border-left: 4px solid #F59E0B; }
.card-red    { border-left: 4px solid #EF4444; }

/* ── Section labels ── */
.sec-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; letter-spacing: 0.14em;
    color: #2563EB; text-transform: uppercase;
    font-weight: 600; margin-bottom: 10px;
    display: block;
}

/* ── Theory block ── */
.theory-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 16px 20px;
    line-height: 1.8;
    color: #334155;
    font-size: 0.95rem;
}

/* ── Step block ── */
.step-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.step-num {
    background: #2563EB;
    color: #FFFFFF;
    border-radius: 50%;
    width: 26px; height: 26px;
    display: inline-flex;
    align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700;
    margin-right: 10px;
    font-family: 'JetBrains Mono', monospace;
}
.step-expr {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    color: #1D4ED8;
    background: #EFF6FF;
    padding: 4px 10px;
    border-radius: 4px;
    display: inline-block;
    margin-top: 6px;
}

/* ── Formula chip ── */
.formula-chip {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 6px;
    padding: 5px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #1D4ED8;
    display: inline-block;
    margin: 3px;
}

/* ── Value pill ── */
.val-pill {
    background: #F1F5F9;
    border: 1px solid #CBD5E1;
    border-radius: 20px;
    padding: 4px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #334155;
    display: inline-block;
    margin: 3px;
}

/* ── Answer block ── */
.answer-box {
    background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
    border: 2px solid #22C55E;
    border-radius: 10px;
    padding: 18px 24px;
    font-size: 1.05rem;
    font-weight: 600;
    color: #15803D;
    margin: 12px 0;
}

/* ── Info rows ── */
.improve-item { padding:9px 14px; background:#EFF6FF; border-left:3px solid #3B82F6; border-radius:0 6px 6px 0; margin:5px 0; color:#1E40AF; font-size:.9rem; }
.mistake-item { padding:9px 14px; background:#FFFBEB; border-left:3px solid #F59E0B; border-radius:0 6px 6px 0; margin:5px 0; color:#92400E; font-size:.9rem; }
.app-item     { padding:9px 14px; background:#F0FDF4; border-left:3px solid #22C55E; border-radius:0 6px 6px 0; margin:5px 0; color:#14532D; font-size:.9rem; }

/* ── Chat bubbles ── */
.chat-you  { background:#EFF6FF; border-radius:14px 14px 4px 14px; padding:12px 16px; margin:8px 0 8px 60px; color:#1E40AF; border:1px solid #BFDBFE; }
.chat-ai   { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px 14px 14px 4px; padding:12px 16px; margin:8px 60px 8px 0; color:#1E293B; box-shadow:0 1px 4px rgba(0,0,0,0.05); }
.chat-lbl  { font-size:.65rem; font-family:'JetBrains Mono',monospace; color:#94A3B8; margin-bottom:3px; text-transform:uppercase; letter-spacing:.08em; }

/* ── Quiz ── */
.q-correct { padding:10px 14px; background:#F0FDF4; border-left:4px solid #22C55E; border-radius:4px; margin:5px 0; color:#15803D; font-weight:500; }
.q-wrong   { padding:10px 14px; background:#FFF7ED; border-left:4px solid #F97316; border-radius:4px; margin:5px 0; color:#9A3412; font-weight:500; }

/* ── Metric box ── */
.metric-box { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:16px; text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.05); }
.metric-val { font-size:2rem; font-weight:700; color:#2563EB; font-family:'JetBrains Mono',monospace; }
.metric-lbl { font-size:.75rem; color:#64748B; margin-top:4px; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #2563EB, #3B82F6) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(37,99,235,0.25);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1D4ED8, #2563EB) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37,99,235,0.35) !important;
}

/* ── Inputs ── */
.stTextArea textarea {
    background: #FFFFFF !important; border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important; color: #1E293B !important; font-size:.93rem !important;
}
.stTextArea textarea:focus { border-color: #3B82F6 !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important; }
.stTextInput input {
    background: #FFFFFF !important; border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important; color: #1E293B !important;
}
.stSelectbox > div > div { background: #FFFFFF !important; border: 1px solid #CBD5E1 !important; color: #1E293B !important; border-radius:8px !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]  { background:#FFFFFF; border-radius:10px 10px 0 0; border-bottom:2px solid #E2E8F0; }
.stTabs [data-baseweb="tab"]       { color:#64748B; font-weight:500; font-size:.9rem; }
.stTabs [aria-selected="true"]     { color:#2563EB !important; border-bottom:2px solid #2563EB !important; font-weight:600 !important; }

/* ── Expanders ── */
[data-testid="stExpander"] { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; }
[data-testid="stExpander"] summary { color:#1E293B !important; font-weight:500; }

/* ── Scrollbar ── */
::-webkit-scrollbar       { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#F1F5F9; }
::-webkit-scrollbar-thumb { background:#CBD5E1; border-radius:3px; }

/* ── Misc ── */
hr { border-color:#E2E8F0 !important; }
.stAlert { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# API-key management  (NO key shown anywhere in the visible UI)
# ─────────────────────────────────────────────────────────────────────────────
if "api_key" not in st.session_state:
    st.session_state["api_key"] = load_api_key()

if "engine" not in st.session_state:
    st.session_state["engine"] = None

if "key_saved" not in st.session_state:
    st.session_state["key_saved"] = False


def _try_init_engine(key: str) -> bool:
    """Try to create a TutorEngine; return True on success."""
    try:
        engine = TutorEngine(api_key=key)
        # Quick smoke-test (will raise if key invalid)
        st.session_state["engine"]  = engine
        st.session_state["api_key"] = key
        return True
    except Exception as e:
        st.session_state["engine"] = None
        return False


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ Circuit Tutor")
    st.markdown('<span class="groq-badge" style="color:#1E293B;background:#EFF6FF;border-color:#BFDBFE;">Groq llama-3.3-70b — FREE</span>', unsafe_allow_html=True)
    st.markdown("")

    # ── Connection status indicator only (no key displayed) ───────────────────
    if st.session_state["api_key"]:
        st.success("🔒 API key loaded — connected", icon="✅")
    else:
        st.warning("No API key detected — set up below", icon="⚠️")

    st.markdown("---")

    # ── Topic / difficulty ─────────────────────────────────────────────────────
    st.markdown('<span class="sec-label">Topic Focus</span>', unsafe_allow_html=True)
    topic_hint = st.selectbox("Topic (optional)", ["Auto-detect"] + get_topics(), index=0, label_visibility="collapsed")
    if topic_hint == "Auto-detect":
        topic_hint = ""

    difficulty = st.select_slider("Level", ["Beginner","Intermediate","Advanced","Expert"], value="Intermediate")

    st.markdown("---")

    # ── Quick calculator ───────────────────────────────────────────────────────
    st.markdown('<span class="sec-label">Quick Calculator</span>', unsafe_allow_html=True)
    calc_mode = st.selectbox("Calculator", [
        "Ohm's Law", "RC Time Constant", "RL Time Constant",
        "RLC Resonance", "Voltage Divider", "Op-Amp Gain",
    ], label_visibility="collapsed")

    calc_result = {}
    if calc_mode == "Ohm's Law":
        c1, c2 = st.columns(2)
        V = c1.number_input("V (V)",  value=0.0, step=0.5, format="%.3f")
        I = c2.number_input("I (mA)", value=0.0, step=0.1, format="%.3f")
        R = st.number_input("R (Ω)",  value=0.0, step=10.0, format="%.1f")
        calc_result = calc_ohms_law(V or None, I/1000 if I else None, R or None)

    elif calc_mode == "RC Time Constant":
        c1, c2 = st.columns(2)
        R_k = c1.number_input("R (kΩ)", value=1.0, step=0.1, min_value=0.001)
        C_u = c2.number_input("C (µF)", value=1.0, step=0.1, min_value=0.001)
        calc_result = calc_rc(R_k * 1000, C_u * 1e-6)

    elif calc_mode == "RL Time Constant":
        c1, c2 = st.columns(2)
        R_v = c1.number_input("R (Ω)",  value=100.0, step=10.0, min_value=0.001)
        L_m = c2.number_input("L (mH)", value=10.0,  step=1.0,  min_value=0.001)
        calc_result = calc_rl(R_v, L_m / 1000)

    elif calc_mode == "RLC Resonance":
        c1, c2, c3 = st.columns(3)
        R_v = c1.number_input("R (Ω)",  value=10.0, step=1.0,  min_value=0.001)
        L_m = c2.number_input("L (mH)", value=1.0,  step=0.1,  min_value=0.001)
        C_u = c3.number_input("C (µF)", value=1.0,  step=0.1,  min_value=0.001)
        calc_result = calc_rlc(R_v, L_m/1000, C_u*1e-6)

    elif calc_mode == "Voltage Divider":
        Vin  = st.number_input("Vin (V)",  value=12.0, step=0.5)
        c1, c2 = st.columns(2)
        R1_k = c1.number_input("R1 (kΩ)", value=10.0, step=1.0, min_value=0.001)
        R2_k = c2.number_input("R2 (kΩ)", value=2.2,  step=0.1, min_value=0.001)
        calc_result = calc_vdiv(Vin, R1_k*1000, R2_k*1000)

    elif calc_mode == "Op-Amp Gain":
        c1, c2 = st.columns(2)
        R1_k = c1.number_input("R1 (kΩ)", value=1.0,  step=0.1, min_value=0.001)
        Rf_k = c2.number_input("Rf (kΩ)", value=10.0, step=1.0, min_value=0.001)
        inv  = st.checkbox("Inverting config", value=True)
        calc_result = calc_opamp(R1_k*1000, Rf_k*1000, inv)

    for k, v in calc_result.items():
        st.markdown(f'<div class="val-pill">📐 <strong>{k}</strong> = {v}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Progress ───────────────────────────────────────────────────────────────
    st.markdown('<span class="sec-label">Learning Progress</span>', unsafe_allow_html=True)
    prog = st.session_state[KEY_PROGRESS]
    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="metric-box"><div class="metric-val">{prog["questions_asked"]}</div><div class="metric-lbl">Questions</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box"><div class="metric-val">{len(prog["topics_studied"])}</div><div class="metric-lbl">Topics</div></div>', unsafe_allow_html=True)

    if prog["quiz_scores"]:
        avg = sum(prog["quiz_scores"]) / len(prog["quiz_scores"])
        st.markdown(f'<div class="metric-box" style="margin-top:8px"><div class="metric-val">{avg:.0f}%</div><div class="metric-lbl">Avg Quiz Score</div></div>', unsafe_allow_html=True)

    if prog["topics_studied"]:
        with st.expander("Topics covered"):
            for t in prog["topics_studied"]:
                st.markdown(f"• {t}")

    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state["conversation"] = []
        st.session_state["current_solution"] = None
        if st.session_state["engine"]:
            st.session_state["engine"].clear_history()
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>⚡ Circuit Design Q&A Tutor</h1>
    <p>Your AI electronics professor — step-by-step solutions for analog &amp; digital circuits</p>
    <div class="groq-badge">✦ Groq llama-3.3-70b-versatile &nbsp;|&nbsp; Free API &nbsp;|&nbsp; Ultra-fast</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SETUP SCREEN  (shown only when no API key is configured)
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state["api_key"]:
    st.markdown('<div class="card card-blue">', unsafe_allow_html=True)
    st.markdown("### 🔑 First-Time Setup — Enter Your Free Groq API Key")
    st.markdown("""
**Get your free key in 30 seconds:**
1. Go to **[console.groq.com/keys](https://console.groq.com/keys)**
2. Sign in with Google / GitHub / email
3. Click **Create API Key** → copy it
4. Paste below and click **Save & Connect**

> 💡 No credit card required. Free tier: 14,400 requests/day.
""")
    setup_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        label_visibility="visible",
    )
    save_col, _ = st.columns([1, 3])
    if save_col.button("💾 Save & Connect", type="primary"):
        if setup_key.strip().startswith("gsk_"):
            if _try_init_engine(setup_key.strip()):
                generate_env_file(setup_key.strip())
                st.session_state["key_saved"] = True
                st.success("✅ Connected! Your key has been saved to `.env` — you won't need to enter it again.")
                st.rerun()
            else:
                st.error("❌ Could not connect with that key. Please check it and try again.")
        else:
            st.error("❌ Key must start with `gsk_`. Please copy it from console.groq.com/keys")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Key is present — ensure engine is initialised
if st.session_state["engine"] is None:
    if not _try_init_engine(st.session_state["api_key"]):
        st.error("❌ Stored API key is invalid or expired. Please reload the page and enter a new key.")
        # Clear stored key so setup screen appears
        st.session_state["api_key"] = ""
        generate_env_file("")
        st.stop()

engine: TutorEngine = st.session_state["engine"]


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
(tab_ask, tab_chat, tab_viz, tab_quiz, tab_viva,
 tab_notes, tab_challenge, tab_formula, tab_history, tab_settings) = st.tabs([
    "🎓 Ask", "💬 Chat", "📊 Graphs", "📝 Quiz",
    "🎤 Viva", "📚 Notes", "🏆 Challenge",
    "📋 Formulas", "📁 History", "⚙️ Settings",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ASK A QUESTION
# ══════════════════════════════════════════════════════════════════════════════
with tab_ask:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<span class="sec-label">Your Circuit Question</span>', unsafe_allow_html=True)

        with st.expander("💡 Sample Problems"):
            for i, prob in enumerate(SAMPLE_PROBLEMS):
                if st.button(f"▶ {prob[:68]}…", key=f"sp_{i}"):
                    st.session_state["_sq"] = prob
                    st.rerun()

        question = st.text_area(
            "Question",
            value=st.session_state.pop("_sq", ""),
            height=130,
            placeholder="e.g. A 4.7 kΩ resistor has 9 V across it. Find the current and power.",
            label_visibility="collapsed",
        )

        ask_btn = st.button("⚡ Get Solution", type="primary", use_container_width=True)

    with right:
        st.markdown('<span class="sec-label">AI Tutor Response</span>', unsafe_allow_html=True)

        if ask_btn:
            if not question.strip():
                st.warning("Please enter a question first.")
            else:
                with st.spinner("🧠 Professor Ohm is solving your problem…"):
                    try:
                        sol = engine.ask_question(question, topic_hint, difficulty)
                        save_solution(sol, question)
                        record_question(sol.get("topic", ""))
                        fig = get_graph_for_topic(sol.get("topic", ""))
                        st.session_state["auto_graph"] = fig
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                        st.stop()

        sol = st.session_state.get("current_solution")

        if sol:
            # Topic badge
            st.markdown(f'<div class="card card-blue"><strong>📐 Topic:</strong> {sol.get("topic","")}</div>', unsafe_allow_html=True)

            with st.expander("📖 Theory & Concepts", expanded=True):
                st.markdown(f'<div class="theory-box">{sol.get("theory","")}</div>', unsafe_allow_html=True)

            if sol.get("known_values"):
                with st.expander("🔢 Known Values"):
                    for v in sol["known_values"]:
                        st.markdown(f'<span class="val-pill">📌 {v}</span>', unsafe_allow_html=True)

            if sol.get("formulas_used"):
                with st.expander("📐 Formulas Used"):
                    for f in sol["formulas_used"]:
                        st.markdown(f'<span class="formula-chip">∫ {f}</span>', unsafe_allow_html=True)

            if sol.get("calculations"):
                with st.expander("🧮 Step-by-Step Calculations", expanded=True):
                    for s in sol["calculations"]:
                        st.markdown(f"""
                        <div class="step-box">
                            <span class="step-num">{s.get('step','?')}</span>
                            <strong style="color:#1E293B">{s.get('description','')}</strong>
                            <div class="step-expr">{s.get('expression','')} = {s.get('result','')}</div>
                        </div>""", unsafe_allow_html=True)

            st.markdown(f'<div class="answer-box">✅ {sol.get("final_answer","")}</div>', unsafe_allow_html=True)

            ca, cb = st.columns(2)
            with ca:
                if sol.get("design_improvements"):
                    with st.expander("💡 Design Improvements"):
                        for d in sol["design_improvements"]:
                            st.markdown(f'<div class="improve-item">🔧 {d}</div>', unsafe_allow_html=True)
                if sol.get("practical_applications"):
                    with st.expander("🌐 Applications"):
                        for a in sol["practical_applications"]:
                            st.markdown(f'<div class="app-item">🚀 {a}</div>', unsafe_allow_html=True)
            with cb:
                if sol.get("common_mistakes"):
                    with st.expander("⚠️ Common Mistakes"):
                        for m in sol["common_mistakes"]:
                            st.markdown(f'<div class="mistake-item">⚠️ {m}</div>', unsafe_allow_html=True)

            if st.session_state.get("auto_graph"):
                st.plotly_chart(st.session_state["auto_graph"], use_container_width=True)

            st.markdown("---")
            st.markdown('<span class="sec-label">Export Solution</span>', unsafe_allow_html=True)
            e1, e2, e3 = st.columns(3)
            e1.download_button("⬇️ Markdown", to_markdown(sol, question), "solution.md",   "text/markdown",    use_container_width=True)
            e2.download_button("⬇️ JSON",     to_json(sol, question),     "solution.json", "application/json", use_container_width=True)
            e3.download_button("⬇️ HTML",     to_html(sol, question),     "solution.html", "text/html",        use_container_width=True)

        elif not ask_btn:
            st.markdown("""
            <div class="card" style="text-align:center;padding:48px 24px;">
                <div style="font-size:3.5rem">⚡</div>
                <h3 style="color:#2563EB;margin:16px 0 8px">Ready to Learn!</h3>
                <p style="color:#64748B">Type a circuit question on the left<br>and click <strong>Get Solution</strong>.</p>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CHAT
# ══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown('<span class="sec-label">Conversational Learning — context is remembered</span>', unsafe_allow_html=True)

    for msg in st.session_state["conversation"]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-lbl">You</div><div class="chat-you">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            content = msg["content"]
            if isinstance(content, dict):
                text = f"**{content.get('topic','')}**\n\n{content.get('theory','')[:300]}…\n\n**Answer:** {content.get('final_answer','')}"
            else:
                text = str(content)
            st.markdown(f'<div class="chat-lbl">Professor Ohm</div><div class="chat-ai">{text}</div>', unsafe_allow_html=True)

    ci_col, btn_col = st.columns([5, 1])
    chat_in = ci_col.text_input("Message", placeholder="Ask a follow-up…", label_visibility="collapsed", key="chat_in")
    if btn_col.button("Send ➤", use_container_width=True):
        if chat_in.strip():
            st.session_state["conversation"].append({"role": "user", "content": chat_in})
            with st.spinner("Thinking…"):
                try:
                    resp = engine.ask_question(chat_in, topic_hint, difficulty)
                    st.session_state["conversation"].append({"role": "assistant", "content": resp})
                    record_question(resp.get("topic", ""))
                except Exception as e:
                    st.session_state["conversation"].append({"role": "assistant", "content": f"Error: {e}"})
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_viz:
    st.markdown('<span class="sec-label">Interactive Circuit Graphs</span>', unsafe_allow_html=True)

    graph_choice = st.selectbox("Graph type", [
        "Ohm's Law — V vs I", "Power Dissipation", "RC Step Response",
        "RL Step Response", "RLC Frequency Response", "Signal Waveforms",
        "Op-Amp Gain vs Frequency", "Diode I-V Characteristic",
        "BJT Transistor Load Line", "Logic Gate Truth Table",
    ])
    st.markdown("---")

    if graph_choice == "Ohm's Law — V vs I":
        R = st.slider("Resistance (Ω)", 100, 100000, 1000, 100)
        st.plotly_chart(plot_ohms_law(R), use_container_width=True)

    elif graph_choice == "Power Dissipation":
        R = st.slider("Resistance (Ω)", 10, 10000, 1000, 10)
        st.plotly_chart(plot_power(R), use_container_width=True)

    elif graph_choice == "RC Step Response":
        c1, c2, c3 = st.columns(3)
        R_v = c1.number_input("R (kΩ)", 0.1, 1000.0, 1.0, 0.1) * 1000
        C_v = c2.number_input("C (µF)", 0.001, 1000.0, 1.0, 0.1) * 1e-6
        V0  = c3.number_input("V₀ (V)", 0.1, 100.0, 5.0, 0.5)
        st.plotly_chart(plot_rc(R_v, C_v, V0), use_container_width=True)

    elif graph_choice == "RL Step Response":
        c1, c2, c3 = st.columns(3)
        R_v = c1.number_input("R (Ω)",  1.0, 10000.0, 100.0, 10.0)
        L_v = c2.number_input("L (mH)", 0.1, 1000.0,  10.0,  1.0) / 1000
        V0  = c3.number_input("V₀ (V)", 0.1, 100.0,   5.0,   0.5)
        st.plotly_chart(plot_rl(R_v, L_v, V0), use_container_width=True)

    elif graph_choice == "RLC Frequency Response":
        c1, c2, c3 = st.columns(3)
        R_v = c1.number_input("R (Ω)",  1.0, 1000.0, 10.0, 1.0)
        L_v = c2.number_input("L (mH)", 0.01, 100.0,  1.0, 0.1) / 1000
        C_v = c3.number_input("C (µF)", 0.001, 100.0,  1.0, 0.1) * 1e-6
        st.plotly_chart(plot_rlc(R_v, L_v, C_v), use_container_width=True)

    elif graph_choice == "Signal Waveforms":
        c1, c2 = st.columns(2)
        freq = c1.number_input("Frequency (Hz)", 10.0, 100000.0, 1000.0, 100.0)
        amp  = c2.number_input("Amplitude (V)",  0.1,  100.0,    5.0,    0.5)
        st.plotly_chart(plot_signals(freq, amp), use_container_width=True)

    elif graph_choice == "Op-Amp Gain vs Frequency":
        c1, c2 = st.columns(2)
        gain = c1.number_input("DC Gain",      1.0, 100000.0, 100.0, 10.0)
        f3db = c2.number_input("f₋₃dB (Hz)",  1.0, 1000000.0, 10000.0, 1000.0)
        st.plotly_chart(plot_opamp(gain, f3db), use_container_width=True)

    elif graph_choice == "Diode I-V Characteristic":
        c1, c2 = st.columns(2)
        Is_v = c1.number_input("Is (pA)", 0.001, 1000.0, 1.0, 0.1) * 1e-12
        n_v  = c2.number_input("Ideality n", 1.0, 2.0, 1.0, 0.1)
        st.plotly_chart(plot_diode(Is_v, n_v), use_container_width=True)

    elif graph_choice == "BJT Transistor Load Line":
        c1, c2, c3 = st.columns(3)
        VCC = c1.number_input("VCC (V)",  1.0, 50.0,    12.0, 1.0)
        RC  = c2.number_input("RC (Ω)",  10.0, 10000.0, 1000.0, 100.0)
        hFE = c3.number_input("hFE (β)", 10.0, 500.0,   100.0, 10.0)
        st.plotly_chart(plot_bjt(VCC, RC, hFE), use_container_width=True)

    elif graph_choice == "Logic Gate Truth Table":
        gate = st.selectbox("Gate", ["AND","OR","NAND","NOR","XOR","XNOR"])
        st.plotly_chart(plot_logic(gate), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — QUIZ
# ══════════════════════════════════════════════════════════════════════════════
with tab_quiz:
    st.markdown('<span class="sec-label">Knowledge Quiz</span>', unsafe_allow_html=True)

    qc1, qc2, qc3 = st.columns(3)
    qtopic = qc1.selectbox("Topic",      get_topics(), key="qt")
    qnum   = qc2.slider("Questions",     3, 10, 5,     key="qn")
    qdiff  = qc3.selectbox("Difficulty", ["Easy","Medium","Hard","Mixed"], index=3, key="qd")

    if st.button("🎯 Generate Quiz", type="primary"):
        with st.spinner("Building quiz…"):
            try:
                qs = engine.generate_quiz(qtopic, qnum, qdiff)
                st.session_state["quiz_questions"] = qs
                st.session_state["quiz_answers"]   = {}
                st.session_state["quiz_submitted"]  = False
            except Exception as e:
                st.error(f"Error: {e}")

    qs = st.session_state.get("quiz_questions", [])
    if qs:
        for i, q in enumerate(qs):
            with st.container():
                st.markdown(f'<div class="card card-blue"><strong>Q{i+1}.</strong> {q.get("question","")}</div>', unsafe_allow_html=True)
                sel = st.radio("Options", q.get("options",[]), key=f"qr_{i}", index=None, label_visibility="collapsed")
                if sel:
                    st.session_state["quiz_answers"][i] = sel[0]

        if st.button("✅ Submit Quiz", type="primary"):
            st.session_state["quiz_submitted"] = True

        if st.session_state.get("quiz_submitted"):
            correct = 0
            for i, q in enumerate(qs):
                ua = st.session_state["quiz_answers"].get(i, "")
                ca = q.get("correct", "")
                if ua == ca:
                    correct += 1
                    st.markdown(f'<div class="q-correct">✅ Q{i+1}: Correct! (Answer: {ca})</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="q-wrong">❌ Q{i+1}: Your answer: {ua or "—"} &nbsp;|&nbsp; Correct: {ca}</div>', unsafe_allow_html=True)
                with st.expander(f"Explanation — Q{i+1}"):
                    st.write(q.get("explanation",""))

            pct = correct / len(qs) * 100
            st.markdown(f'<div class="answer-box">🏆 Score: {correct}/{len(qs)} ({pct:.0f}%)</div>', unsafe_allow_html=True)
            record_quiz(qtopic, correct, len(qs))


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — VIVA
# ══════════════════════════════════════════════════════════════════════════════
with tab_viva:
    st.markdown('<span class="sec-label">Viva / Oral Exam Preparation</span>', unsafe_allow_html=True)

    vc1, vc2 = st.columns([3,1])
    vtopic = vc1.selectbox("Viva topic", get_topics(), key="vt")
    vnum   = vc2.slider("Questions", 3, 10, 5, key="vn")

    if st.button("🎤 Generate Viva Questions", type="primary"):
        with st.spinner("Preparing questions…"):
            try:
                vqs = engine.generate_viva(vtopic, vnum)
                st.session_state["viva_questions"] = vqs
            except Exception as e:
                st.error(f"Error: {e}")

    for i, vq in enumerate(st.session_state.get("viva_questions",[])):
        diff  = vq.get("difficulty","Medium")
        color = {"Easy":"#22C55E","Medium":"#F59E0B","Hard":"#EF4444"}.get(diff,"#64748B")
        with st.expander(f"Q{i+1} [{diff}]: {vq.get('question','')[:75]}…"):
            st.markdown(f"**Question:** {vq.get('question','')}")
            st.markdown("---")
            st.info(f"**Model Answer:** {vq.get('model_answer','')}")
            st.markdown(f"*Follow-up: {vq.get('follow_up','')}*")

    if st.session_state.get("viva_questions"):
        md = "\n\n".join([
            f"## Q{i+1}: {vq.get('question','')}\n\n**Answer:** {vq.get('model_answer','')}\n\n**Follow-up:** {vq.get('follow_up','')}"
            for i, vq in enumerate(st.session_state["viva_questions"])
        ])
        st.download_button("⬇️ Download Viva Q&A", md, "viva.md", "text/markdown")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — STUDY NOTES
# ══════════════════════════════════════════════════════════════════════════════
with tab_notes:
    st.markdown('<span class="sec-label">AI Study Notes</span>', unsafe_allow_html=True)

    ntopic = st.selectbox("Topic", get_topics(), key="nt")
    if st.button("📝 Generate Study Notes", type="primary"):
        with st.spinner("Writing notes…"):
            try:
                notes = engine.generate_notes(ntopic)
                st.session_state["study_notes"] = notes
            except Exception as e:
                st.error(f"Error: {e}")

    notes = st.session_state.get("study_notes")
    if notes:
        st.markdown(f"## 📘 {notes.get('title', ntopic)}")
        st.markdown(f'<div class="theory-box">{notes.get("summary","")}</div>', unsafe_allow_html=True)
        nc1, nc2 = st.columns(2)
        with nc1:
            if notes.get("key_concepts"):
                st.markdown("### 🔑 Key Concepts")
                for c in notes["key_concepts"]:
                    st.markdown(f'<div class="improve-item">{c}</div>', unsafe_allow_html=True)
            if notes.get("memory_tricks"):
                st.markdown("### 🧠 Memory Tricks")
                for t in notes["memory_tricks"]:
                    st.markdown(f'<div class="app-item">💡 {t}</div>', unsafe_allow_html=True)
        with nc2:
            if notes.get("important_formulas"):
                st.markdown("### 📐 Formulas")
                for f in notes["important_formulas"]:
                    st.markdown(f'<span class="formula-chip">{f}</span>', unsafe_allow_html=True)
            if notes.get("exam_tips"):
                st.markdown("### 🎯 Exam Tips")
                for tip in notes["exam_tips"]:
                    st.markdown(f'<div class="mistake-item">📌 {tip}</div>', unsafe_allow_html=True)
        md = f"# {notes.get('title','')}\n\n{notes.get('summary','')}\n\n"
        md += "## Key Concepts\n" + "\n".join(f"- {c}" for c in notes.get("key_concepts",[]))
        md += "\n\n## Formulas\n"  + "\n".join(f"- `{f}`" for f in notes.get("important_formulas",[]))
        st.download_button("⬇️ Download Notes", md, "notes.md", "text/markdown")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — CHALLENGE
# ══════════════════════════════════════════════════════════════════════════════
with tab_challenge:
    st.markdown('<span class="sec-label">Circuit Design Challenge</span>', unsafe_allow_html=True)

    cc1, cc2 = st.columns([3,1])
    ctopic = cc1.selectbox("Topic", get_topics(), key="ct")
    cdiff  = cc2.selectbox("Difficulty", ["Beginner","Intermediate","Advanced"], index=1, key="cd")

    if st.button("🏆 Generate Challenge", type="primary"):
        with st.spinner("Creating challenge…"):
            try:
                chal = engine.generate_challenge(ctopic, cdiff)
                st.session_state["challenge"]     = chal
                st.session_state["show_hints"]    = False
                st.session_state["show_solution"] = False
            except Exception as e:
                st.error(f"Error: {e}")

    chal = st.session_state.get("challenge")
    if chal:
        diff_color = {"Beginner":"#22C55E","Intermediate":"#F59E0B","Advanced":"#EF4444"}.get(chal.get("difficulty",""),"#64748B")
        st.markdown(f"""
        <div class="card card-blue">
            <h2 style="color:#1D4ED8;margin:0 0 8px">🏆 {chal.get('title','')}</h2>
            <span style="background:{diff_color};color:#fff;padding:3px 12px;border-radius:12px;font-size:.78rem;font-weight:700">{chal.get('difficulty','')}</span>
        </div>""", unsafe_allow_html=True)

        st.markdown("### 📋 Scenario")
        st.markdown(f'<div class="theory-box">{chal.get("scenario","")}</div>', unsafe_allow_html=True)
        st.markdown("### 📌 Requirements")
        for req in chal.get("requirements",[]):
            st.markdown(f'<div class="improve-item">✅ {req}</div>', unsafe_allow_html=True)

        if chal.get("components_needed"):
            st.markdown("### 🔧 Components")
            cols = st.columns(min(len(chal["components_needed"]),4))
            for i, comp in enumerate(chal["components_needed"]):
                cols[i%len(cols)].markdown(f'<span class="val-pill">🔩 {comp}</span>', unsafe_allow_html=True)

        h1, h2 = st.columns(2)
        if h1.button("💡 Show Hints"):
            st.session_state["show_hints"] = True
        if h2.button("🔓 Show Solution Approach"):
            st.session_state["show_solution"] = True

        if st.session_state.get("show_hints"):
            st.markdown("### 💡 Hints")
            for j, hint in enumerate(chal.get("hints",[]),1):
                st.markdown(f'<div class="mistake-item">💡 Hint {j}: {hint}</div>', unsafe_allow_html=True)
        if st.session_state.get("show_solution"):
            st.markdown("### 🔓 Solution Approach")
            st.info(chal.get("solution_approach",""))


# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — FORMULA SHEET
# ══════════════════════════════════════════════════════════════════════════════
with tab_formula:
    st.markdown('<span class="sec-label">Formula Reference</span>', unsafe_allow_html=True)
    fs1, fs2 = st.columns(2)

    with fs1:
        st.markdown("### 📚 Built-in Library")
        for cat, fmls in FORMULA_LIBRARY.items():
            with st.expander(f"📐 {cat}"):
                for formula, desc in fmls.items():
                    st.markdown(
                        f'<span class="formula-chip">{formula}</span>'
                        f'<span style="color:#64748B;font-size:.8rem;margin-left:8px">— {desc}</span>',
                        unsafe_allow_html=True
                    )

    with fs2:
        st.markdown("### 🤖 AI Cheat Sheet")
        cstopic = st.selectbox("Topic", get_topics(), key="cst")
        if st.button("📋 Generate Cheat Sheet", type="primary"):
            with st.spinner("Generating…"):
                try:
                    cs = engine.generate_cheatsheet(cstopic)
                    st.session_state["cheatsheet"] = cs
                except Exception as e:
                    st.error(f"Error: {e}")

        cs = st.session_state.get("cheatsheet")
        if cs:
            st.markdown(f"**{cs.get('topic','')}**")
            for fi in cs.get("formulas",[]):
                with st.expander(f"∫ {fi.get('name','')}"):
                    st.code(fi.get("formula",""), language=None)
                    if fi.get("variables"):
                        for var, meaning in fi["variables"].items():
                            st.markdown(f"- **{var}**: {meaning}")
                    if fi.get("notes"):
                        st.caption(f"📝 {fi['notes']}")
            cs_md = f"# {cs.get('topic','')} Cheat Sheet\n\n" + "\n\n".join([
                f"## {f.get('name','')}\n`{f.get('formula','')}`\n\n{f.get('notes','')}"
                for f in cs.get("formulas",[])
            ])
            st.download_button("⬇️ Download Cheat Sheet", cs_md, "cheatsheet.md", "text/markdown")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 9 — HISTORY
# ══════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.markdown('<span class="sec-label">Solutions History</span>', unsafe_allow_html=True)
    hist = st.session_state[KEY_SOLUTIONS]
    if not hist:
        st.markdown('<div class="card" style="text-align:center;padding:40px"><div style="font-size:2.5rem">📂</div><p style="color:#64748B;margin-top:12px">No solutions yet — ask a question first!</p></div>', unsafe_allow_html=True)
    else:
        st.caption(f"{len(hist)} solution(s) saved this session")
        for idx, item in enumerate(reversed(hist)):
            sol = item["solution"]
            with st.expander(f"[{item['timestamp']}] {sol.get('topic','?')} — {item['question'][:55]}…"):
                st.markdown(f"**Q:** {item['question']}")
                st.markdown(f'<div class="answer-box" style="font-size:.95rem">✅ {sol.get("final_answer","")}</div>', unsafe_allow_html=True)
                hc1, hc2, hc3 = st.columns(3)
                hc1.download_button("⬇️ MD",   to_markdown(sol,item['question']), f"sol_{idx}.md",   "text/markdown",    key=f"hmd_{idx}")
                hc2.download_button("⬇️ JSON", to_json(sol,item['question']),     f"sol_{idx}.json", "application/json", key=f"hjs_{idx}")
                hc3.download_button("⬇️ HTML", to_html(sol,item['question']),     f"sol_{idx}.html", "text/html",        key=f"hht_{idx}")

        if len(hist) > 1:
            st.markdown("---")
            st.download_button("⬇️ Export All (JSON)",
                               json.dumps(hist, indent=2, ensure_ascii=False, default=str),
                               "all_solutions.json", "application/json")

    if st.session_state[KEY_QUIZ]:
        st.markdown("---")
        st.markdown('<span class="sec-label">Quiz History</span>', unsafe_allow_html=True)
        for qr in st.session_state[KEY_QUIZ]:
            badge = "🟢" if qr["score_pct"]>=70 else "🟡" if qr["score_pct"]>=40 else "🔴"
            st.markdown(
                f'{badge} **{qr["topic"]}** — {qr["correct"]}/{qr["total"]} ({qr["score_pct"]}%) '
                f'<span style="color:#94A3B8;font-size:.8rem">{qr["timestamp"][:19]}</span>',
                unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 10 — SETTINGS  (change API key, no key ever shown)
# ══════════════════════════════════════════════════════════════════════════════
with tab_settings:
    st.markdown('<span class="sec-label">Settings</span>', unsafe_allow_html=True)

    st.markdown("### 🔑 API Key Management")
    st.info("Your API key is stored only in the local `.env` file and is never displayed here.")

    with st.expander("🔄 Update API Key"):
        new_key = st.text_input("New Groq API Key", type="password", placeholder="gsk_…", label_visibility="visible")
        if st.button("💾 Save New Key", type="primary"):
            if new_key.strip().startswith("gsk_"):
                if _try_init_engine(new_key.strip()):
                    generate_env_file(new_key.strip())
                    st.success("✅ New key saved and connected successfully.")
                    st.rerun()
                else:
                    st.error("❌ Invalid key. Check console.groq.com/keys")
            else:
                st.error("❌ Key must start with `gsk_`")

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
| | |
|---|---|
| **App** | Circuit Design Q&A Tutor |
| **AI Model** | Groq `llama-3.3-70b-versatile` |
| **API Cost** | 🆓 Free (14,400 req/day) |
| **Key URL** | [console.groq.com/keys](https://console.groq.com/keys) |
| **Rate Limit** | 30 req/min on free tier |
""")

    st.markdown("---")
    st.markdown("### 🗑️ Reset App Data")
    if st.button("Clear All Session Data", type="secondary"):
        for k in [KEY_SOLUTIONS, KEY_QUIZ, "conversation", "current_solution",
                  "quiz_questions", "quiz_answers", "viva_questions",
                  "study_notes", "challenge", "cheatsheet", "auto_graph"]:
            st.session_state[k] = [] if k in (KEY_SOLUTIONS, KEY_QUIZ, "conversation",
                                               "quiz_questions", "viva_questions") else None
        st.session_state[KEY_PROGRESS] = {"topics_studied":[], "questions_asked":0, "quiz_scores":[], "sessions":0}
        if engine:
            engine.clear_history()
        st.success("✅ Session data cleared.")
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#94A3B8;font-size:.8rem;padding:12px 0">
    ⚡ Circuit Design Q&A Tutor &nbsp;•&nbsp;
    Groq llama-3.3-70b-versatile &nbsp;•&nbsp;
    <span style="font-family:'JetBrains Mono',monospace">Professor Ohm v3.0</span>
</div>
""", unsafe_allow_html=True)
