"""
utils.py
Export helpers (Markdown, JSON, HTML), session-state init, progress tracking.
"""

import json
import datetime
import os
import streamlit as st

# ── Session-state keys ─────────────────────────────────────────────────────────
KEY_PROGRESS  = "learning_progress"
KEY_SOLUTIONS = "solutions_history"
KEY_QUIZ      = "quiz_results"


def init_session():
    defaults = {
        KEY_PROGRESS:  {"topics_studied": [], "questions_asked": 0,
                        "quiz_scores": [], "sessions": 0},
        KEY_SOLUTIONS: [],
        KEY_QUIZ:      [],
        "conversation":       [],
        "current_solution":   None,
        "auto_graph":         None,
        "quiz_questions":     [],
        "quiz_answers":       {},
        "quiz_submitted":     False,
        "viva_questions":     [],
        "study_notes":        None,
        "challenge":          None,
        "cheatsheet":         None,
        "show_hints":         False,
        "show_solution":      False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def record_question(topic: str):
    p = st.session_state[KEY_PROGRESS]
    p["questions_asked"] += 1
    if topic and topic not in p["topics_studied"]:
        p["topics_studied"].append(topic)


def record_quiz(topic: str, correct: int, total: int):
    pct = round(correct / total * 100, 1) if total else 0
    st.session_state[KEY_QUIZ].append({
        "topic": topic, "correct": correct, "total": total,
        "score_pct": pct,
        "timestamp": datetime.datetime.now().isoformat(),
    })
    st.session_state[KEY_PROGRESS]["quiz_scores"].append(pct)


def save_solution(sol: dict, question: str):
    st.session_state[KEY_SOLUTIONS].append({
        "question": question, "solution": sol,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
    })
    st.session_state["current_solution"] = sol


# ── Export ─────────────────────────────────────────────────────────────────────
def to_markdown(sol: dict, question: str = "") -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Circuit Tutor — Solution Report",
        f"*Generated: {now}*\n",
        f"## Question\n> {question}\n",
        f"## Topic: {sol.get('topic','')}\n",
        f"## Theory\n{sol.get('theory','')}\n",
    ]
    if sol.get("known_values"):
        lines += ["## Known Values"] + [f"- {v}" for v in sol["known_values"]] + [""]
    if sol.get("formulas_used"):
        lines += ["## Formulas"] + [f"- `{f}`" for f in sol["formulas_used"]] + [""]
    if sol.get("calculations"):
        lines.append("## Step-by-Step Calculations")
        for s in sol["calculations"]:
            lines += [
                f"\n**Step {s.get('step','?')} — {s.get('description','')}**",
                f"```\n{s.get('expression','')} = {s.get('result','')}\n```"
            ]
    lines += [f"\n## Final Answer\n**{sol.get('final_answer','')}**\n"]
    if sol.get("design_improvements"):
        lines += ["## Design Improvements"] + [f"- {d}" for d in sol["design_improvements"]] + [""]
    if sol.get("common_mistakes"):
        lines += ["## Common Mistakes"] + [f"- ⚠️ {m}" for m in sol["common_mistakes"]] + [""]
    if sol.get("practical_applications"):
        lines += ["## Practical Applications"] + [f"- {a}" for a in sol["practical_applications"]] + [""]
    return "\n".join(lines)


def to_json(sol: dict, question: str = "") -> str:
    return json.dumps({
        "question": question, "solution": sol,
        "exported_at": datetime.datetime.now().isoformat()
    }, indent=2, ensure_ascii=False)


def to_html(sol: dict, question: str = "") -> str:
    now   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    steps = ""
    for s in sol.get("calculations", []):
        steps += f"""<div class="step">
            <span class="sn">{s.get('step','?')}</span>
            <strong>{s.get('description','')}</strong><br>
            <code>{s.get('expression','')} = {s.get('result','')}</code>
        </div>"""
    ul = lambda lst: "".join(f"<li>{i}</li>" for i in lst)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>Circuit Tutor — {sol.get('topic','')}</title>
<style>
body{{font-family:Segoe UI,sans-serif;max-width:900px;margin:40px auto;color:#1e293b;line-height:1.7;background:#fff}}
h1{{color:#1d4ed8;border-bottom:3px solid #3b82f6;padding-bottom:8px}}
h2{{color:#1d4ed8;margin-top:28px}}
.q{{background:#eff6ff;border-left:4px solid #3b82f6;padding:12px 16px;border-radius:4px}}
.theory{{background:#f8fafc;padding:16px;border-radius:8px;border:1px solid #e2e8f0}}
.step{{background:#fff;border:1px solid #e2e8f0;padding:12px;border-radius:6px;margin:8px 0}}
.sn{{background:#1d4ed8;color:#fff;border-radius:50%;width:24px;height:24px;display:inline-flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:700;margin-right:8px}}
.answer{{background:#f0fdf4;border:2px solid #22c55e;border-radius:8px;padding:16px;font-weight:600;color:#15803d;font-size:1.05rem}}
code{{background:#f1f5f9;padding:2px 6px;border-radius:4px;font-family:monospace}}
ul{{padding-left:20px}}li{{margin:4px 0}}
</style></head><body>
<h1>⚡ Circuit Design Q&A Tutor</h1>
<p><em>Generated: {now}</em></p>
<h2>Question</h2><div class="q">{question}</div>
<h2>Topic</h2><p><strong>{sol.get('topic','')}</strong></p>
<h2>Theory</h2><div class="theory">{sol.get('theory','').replace(chr(10),'<br>')}</div>
{'<h2>Known Values</h2><ul>'+ul(sol.get('known_values',[]))+'</ul>' if sol.get('known_values') else ''}
{'<h2>Formulas Used</h2><ul>'+ul([f'<code>{f}</code>' for f in sol.get('formulas_used',[])])+'</ul>' if sol.get('formulas_used') else ''}
{'<h2>Step-by-Step Calculations</h2>'+steps if steps else ''}
<h2>Final Answer</h2><div class="answer">✅ {sol.get('final_answer','')}</div>
{'<h2>Design Improvements</h2><ul>'+ul(sol.get('design_improvements',[]))+'</ul>' if sol.get('design_improvements') else ''}
{'<h2>Common Mistakes</h2><ul>'+ul(sol.get('common_mistakes',[]))+'</ul>' if sol.get('common_mistakes') else ''}
{'<h2>Practical Applications</h2><ul>'+ul(sol.get('practical_applications',[]))+'</ul>' if sol.get('practical_applications') else ''}
</body></html>"""


# ── .env file generator ────────────────────────────────────────────────────────
def generate_env_file(api_key: str, path: str = ".env") -> bool:
    """Write the API key to a .env file. Returns True on success."""
    try:
        content = f"# Groq API Key — https://console.groq.com/keys\nGROQ_API_KEY={api_key}\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False


def load_api_key() -> str:
    """
    Load GROQ_API_KEY: first from environment / .env file,
    returns empty string if not found.
    """
    # Try os.environ (already set if .env was loaded by dotenv elsewhere)
    key = os.environ.get("GROQ_API_KEY", "")
    if key:
        return key
    # Try reading .env manually
    if os.path.exists(".env"):
        try:
            with open(".env", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GROQ_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if key:
                            return key
        except Exception:
            pass
    return ""
