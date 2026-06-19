# ⚡ Circuit Design Q&A Tutor — Groq Edition (Free, Fast, Error-Free)

An AI electronics professor powered by **Groq's `llama-3.3-70b-versatile`** — completely free,
extremely fast (Groq's specialty), and built with a clean, professional **light theme**.

Your API key is **never displayed anywhere in the UI**. You enter it once on first run, it's saved
quietly to a local `.env` file, and from then on the app just works.

---

## 🆓 Why Groq?

| | Groq (this app) | OpenAI / Anthropic |
|---|---|---|
| Free tier | ✅ Yes — 14,400 requests/day | ❌ Paid only |
| Speed | ⚡⚡⚡ Extremely fast (LPU hardware) | Fast |
| Sign-up | Email/Google/GitHub, no card | Credit card required |
| Model used | `llama-3.3-70b-versatile` | — |

Get your **free API key**: 👉 **[console.groq.com/keys](https://console.groq.com/keys)**

---

## 🗂️ Project Structure

```
circuit_tutor_groq/
├── app.py               ← Main Streamlit app (light theme, 10 tabs)
├── tutor_engine.py       ← Groq SDK wrapper, conversation history, JSON parsing
├── circuit_analyzer.py  ← Formula library, quick calculators, topic list
├── graph_generator.py   ← 10 interactive Plotly charts (light theme)
├── prompts.py           ← All Professor Ohm system prompts
├── utils.py             ← Export (MD/JSON/HTML), .env handling, progress tracking
├── .env.example         ← Reference only — the app generates the real .env for you
├── .gitignore           ← Keeps your real .env out of version control
├── requirements.txt
├── sample_problems.md
└── README.md
```

> **Note:** there is no pre-filled `.env` file in this package. The app walks you through
> entering your key the first time you run it, and writes `.env` automatically — your key
> is never shown in any text box, log, or exported file afterward.

---

## 🚀 Setup on Windows + VS Code

### Step 1 — Get Your Free Groq API Key
1. Open [console.groq.com/keys](https://console.groq.com/keys)
2. Sign in (Google / GitHub / email)
3. Click **Create API Key** → copy it (starts with `gsk_`)

### Step 2 — Open the Project
- Unzip `circuit_tutor_groq.zip` anywhere, e.g. `C:\Projects\circuit_tutor_groq\`
- Open **VS Code** → `File → Open Folder` → select the folder

### Step 3 — Open a Terminal
Press `` Ctrl+` `` or **Terminal → New Terminal**

### Step 4 — Create & Activate a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
> If PowerShell blocks the script:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
You should see `(venv)` in your prompt.

### Step 5 — Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 6 — Run the App
```powershell
streamlit run app.py
```
Your browser opens at **http://localhost:8501**.

### Step 7 — Enter Your Key (one time only)
On first launch you'll see a **Setup** card. Paste your `gsk_...` key and click
**Save & Connect**. It's written to `.env` automatically — you won't be asked again.

---

## ✨ Features

| Tab | What it does |
|---|---|
| 🎓 Ask | Type a question → full structured solution: theory, knowns, formulas, step-by-step calc, final answer, design tips, mistakes, applications |
| 💬 Chat | Multi-turn conversation with full memory of prior turns |
| 📊 Graphs | 10 interactive Plotly visualizations: Ohm's Law, Power, RC/RL/RLC response, signal waveforms, Op-Amp gain, Diode I-V, BJT load line, logic gates |
| 📝 Quiz | AI-generated MCQ quiz with instant grading and explanations |
| 🎤 Viva | Oral-exam practice questions with model answers and examiner follow-ups |
| 📚 Notes | Auto-generated key concepts, formulas, memory tricks, exam tips |
| 🏆 Challenge | Realistic circuit design challenges with progressive hints |
| 📋 Formulas | Built-in formula library + AI-generated topic cheat sheets |
| 📁 History | Every solved problem this session, exportable as MD / JSON / HTML |
| ⚙️ Settings | Update your API key (never shown) or clear session data |

**Sidebar tools:** Quick Calculator (Ohm's Law, RC/RL/RLC, Voltage Divider, Op-Amp Gain),
learning-progress tracker, topic/difficulty selector.

---

## 🔒 API Key Privacy

- The key is requested **once**, on a dedicated setup screen.
- It is saved only to your local `.env` file (excluded from git via `.gitignore`).
- It is **never printed, displayed, or included** in any exported file, chat bubble, or log.
- The Settings tab lets you rotate the key without ever revealing the current one.

---

## 🧠 How It Works

Every question is sent to **Professor Ohm**, a system prompt that always returns structured JSON:

```json
{
  "topic": "RC Circuits",
  "theory": "An RC circuit consists of a resistor and capacitor...",
  "known_values": ["R = 10 kΩ", "C = 100 µF"],
  "formulas_used": ["τ = R × C", "fc = 1/(2πRC)"],
  "calculations": [
    {"step": 1, "description": "Time constant", "expression": "τ = 10000 × 0.0001", "result": "1 s"}
  ],
  "final_answer": "τ = 1 s, cutoff frequency ≈ 0.159 Hz",
  "design_improvements": ["Add a buffer op-amp to isolate the load"],
  "common_mistakes": ["Forgetting source impedance affects τ"],
  "practical_applications": ["Audio tone controls", "Camera flash circuits"]
}
```

The app's JSON parser is defensive: it strips markdown fences, extracts the first valid
`{...}`/`[...]` block even from messy output, and falls back to a safe placeholder structure
if parsing fails entirely — so the UI never crashes on an unexpected model response.

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push the project to a **public GitHub repo** (`.env` is already gitignored)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo, branch `main`, file `app.py`
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```
5. Click **Deploy** — live in about 2 minutes

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Activate the venv, then `pip install -r requirements.txt` |
| PowerShell execution blocked | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| "Invalid key" on setup | Key must start with `gsk_`; copy it fresh from console.groq.com/keys |
| `429` / rate limit error | Free tier allows ~30 requests/min — wait a few seconds and retry |
| App asks for key again after restart | Make sure `.env` wasn't deleted or excluded by your OS |
| Graph doesn't match topic | Only topics with a clear circuit-type keyword auto-generate a graph; others show text only |

---

## 📄 License
MIT — free for personal, educational, and commercial use.
