"""
graph_generator.py
All Plotly visualizations — light theme, clean professional look.
"""

import numpy as np
import plotly.graph_objects as go

# ── Light-theme palette ────────────────────────────────────────────────────────
BG      = "#FFFFFF"
PAPER   = "#F8FAFC"
GRID    = "#E2E8F0"
LINE    = "#CBD5E1"
TEXT    = "#1E293B"
C1      = "#2563EB"   # blue
C2      = "#DC2626"   # red
C3      = "#16A34A"   # green
C4      = "#7C3AED"   # purple
C5      = "#D97706"   # amber

_BASE = dict(
    paper_bgcolor=PAPER,
    plot_bgcolor=BG,
    font=dict(family="Inter, Arial, sans-serif", color=TEXT, size=12),
    xaxis=dict(gridcolor=GRID, zerolinecolor=LINE, linecolor=LINE, color=TEXT, showgrid=True),
    yaxis=dict(gridcolor=GRID, zerolinecolor=LINE, linecolor=LINE, color=TEXT, showgrid=True),
    legend=dict(bgcolor="rgba(248,250,252,0.9)", bordercolor=LINE, borderwidth=1, font=dict(color=TEXT)),
    margin=dict(l=60, r=30, t=55, b=55),
)

def _layout(**kw) -> dict:
    d = dict(_BASE)
    d.update(kw)
    return d


# ── 1. Ohm's Law ──────────────────────────────────────────────────────────────
def plot_ohms_law(R: float = 1000.0) -> go.Figure:
    I = np.linspace(0, 0.01, 300)
    V = I * R
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=I*1000, y=V, mode="lines", name=f"R = {R} Ω",
        line=dict(color=C1, width=3),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.07)"
    ))
    fig.update_layout(**_layout(title=f"<b>Ohm's Law — V = I·R &nbsp;(R = {R} Ω)</b>"),
                      xaxis_title="Current (mA)", yaxis_title="Voltage (V)")
    return fig


# ── 2. Power dissipation ──────────────────────────────────────────────────────
def plot_power(R: float = 1000.0) -> go.Figure:
    I = np.linspace(0, 0.05, 300)
    P = I**2 * R
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=I*1000, y=P*1000, mode="lines", name="P = I²·R",
        line=dict(color=C2, width=3),
        fill="tozeroy", fillcolor="rgba(220,38,38,0.07)"
    ))
    fig.update_layout(**_layout(title=f"<b>Power Dissipation — P = I²·R &nbsp;(R = {R} Ω)</b>"),
                      xaxis_title="Current (mA)", yaxis_title="Power (mW)")
    return fig


# ── 3. RC step response ───────────────────────────────────────────────────────
def plot_rc(R: float = 1000.0, C: float = 1e-6, V0: float = 5.0) -> go.Figure:
    tau = R * C
    t   = np.linspace(0, 5*tau, 500)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t*1000, y=V0*(1-np.exp(-t/tau)), mode="lines",
                             name="Charging",    line=dict(color=C1, width=2.5)))
    fig.add_trace(go.Scatter(x=t*1000, y=V0*np.exp(-t/tau),       mode="lines",
                             name="Discharging", line=dict(color=C2, width=2.5, dash="dash")))
    fig.add_vline(x=tau*1000, line=dict(color=C3, dash="dot", width=1.5),
                  annotation_text=f"τ = {tau*1000:.2g} ms", annotation_font_color=C3)
    fig.update_layout(**_layout(title=f"<b>RC Step Response &nbsp;(R={R}Ω, C={C*1e6:.2g}µF)</b>"),
                      xaxis_title="Time (ms)", yaxis_title="Voltage (V)")
    return fig


# ── 4. RL step response ───────────────────────────────────────────────────────
def plot_rl(R: float = 100.0, L: float = 0.01, V0: float = 5.0) -> go.Figure:
    tau = L / R
    t   = np.linspace(0, 5*tau, 500)
    I   = (V0/R) * (1 - np.exp(-t/tau))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t*1000, y=I*1000, mode="lines",
                             name="Current", line=dict(color=C4, width=3)))
    fig.add_vline(x=tau*1000, line=dict(color=C3, dash="dot", width=1.5),
                  annotation_text=f"τ = {tau*1000:.2g} ms", annotation_font_color=C3)
    fig.update_layout(**_layout(title=f"<b>RL Step Response &nbsp;(R={R}Ω, L={L*1000:.2g}mH)</b>"),
                      xaxis_title="Time (ms)", yaxis_title="Current (mA)")
    return fig


# ── 5. RLC frequency response ─────────────────────────────────────────────────
def plot_rlc(R: float = 10.0, L: float = 0.001, C: float = 1e-6) -> go.Figure:
    f  = np.logspace(1, 6, 1000)
    w  = 2*np.pi*f
    Zl = 1j*w*L
    Zc = 1/(1j*w*C)
    H  = R / (R + Zl + Zc)
    db = 20*np.log10(np.abs(H))
    f0 = 1/(2*np.pi*np.sqrt(L*C))
    Q  = (1/R)*np.sqrt(L/C)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=f, y=db, mode="lines", name="|H(f)| dB",
                             line=dict(color=C1, width=2.5)))
    fig.add_vline(x=f0, line=dict(color=C2, dash="dot", width=1.5),
                  annotation_text=f"f₀={f0:.0f}Hz", annotation_font_color=C2)
    fig.update_layout(**_layout(
        title=f"<b>RLC Frequency Response &nbsp;(f₀={f0:.0f}Hz, Q={Q:.2f})</b>",
        xaxis=dict(type="log", title="Frequency (Hz)", gridcolor=GRID, zerolinecolor=LINE, linecolor=LINE, color=TEXT),
        yaxis_title="Magnitude (dB)",
    ))
    return fig


# ── 6. Signal waveforms ───────────────────────────────────────────────────────
def plot_signals(freq: float = 1000.0, amp: float = 5.0) -> go.Figure:
    t    = np.linspace(0, 3/freq, 1000)
    sine = amp * np.sin(2*np.pi*freq*t)
    sq   = amp * np.sign(np.sin(2*np.pi*freq*t))
    tri  = amp * (2/np.pi) * np.arcsin(np.sin(2*np.pi*freq*t))
    fig  = go.Figure()
    for name, data, color in [("Sine", sine, C1), ("Square", sq, C2), ("Triangle", tri, C3)]:
        fig.add_trace(go.Scatter(x=t*1000, y=data, mode="lines", name=name,
                                 line=dict(color=color, width=2)))
    fig.update_layout(**_layout(title=f"<b>Signal Waveforms &nbsp;(f={freq:.0f}Hz, A={amp}V)</b>"),
                      xaxis_title="Time (ms)", yaxis_title="Voltage (V)")
    return fig


# ── 7. Op-amp frequency response ──────────────────────────────────────────────
def plot_opamp(dc_gain: float = 100.0, f3db: float = 10000.0) -> go.Figure:
    f  = np.logspace(0, 7, 1000)
    H  = dc_gain / np.sqrt(1 + (f/f3db)**2)
    db = 20*np.log10(H)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=f, y=db, mode="lines", name="Gain",
                             line=dict(color=C1, width=2.5)))
    fig.add_hline(y=20*np.log10(dc_gain)-3, line=dict(color=C2, dash="dot"),
                  annotation_text="−3 dB", annotation_font_color=C2)
    fig.update_layout(**_layout(
        title=f"<b>Op-Amp Frequency Response &nbsp;(ADC={dc_gain}, f₋₃dB={f3db}Hz)</b>",
        xaxis=dict(type="log", title="Frequency (Hz)", gridcolor=GRID, zerolinecolor=LINE, linecolor=LINE, color=TEXT),
        yaxis_title="Gain (dB)",
    ))
    return fig


# ── 8. Diode I-V ──────────────────────────────────────────────────────────────
def plot_diode(Is: float = 1e-12, n: float = 1.0) -> go.Figure:
    VT = 0.02585
    V  = np.linspace(-1.0, 0.75, 1000)
    I  = Is * (np.exp(V/(n*VT)) - 1) * 1000  # mA
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=V, y=np.clip(I, -0.05, 40), mode="lines",
                             name="Diode I-V", line=dict(color=C3, width=3)))
    fig.add_vline(x=0.7, line=dict(color=C2, dash="dot", width=1.5),
                  annotation_text="≈0.7V", annotation_font_color=C2)
    fig.update_layout(**_layout(title="<b>Diode I-V Characteristic</b>"),
                      xaxis_title="Voltage (V)", yaxis_title="Current (mA)")
    return fig


# ── 9. BJT load line ──────────────────────────────────────────────────────────
def plot_bjt(VCC: float = 12.0, RC: float = 1000.0, hFE: float = 100.0) -> go.Figure:
    VCE  = np.linspace(0, VCC, 300)
    ICs  = VCC / RC * 1000          # saturation mA
    IClL = (VCC - VCE) / RC * 1000  # load line
    fig  = go.Figure()
    fig.add_trace(go.Scatter(x=VCE, y=IClL, mode="lines", name="Load Line",
                             line=dict(color=C1, width=3)))
    for IB_uA in [10, 20, 40, 60, 80]:
        IC_curve = np.clip(hFE*(IB_uA*1e-6)*1000*np.ones_like(VCE), 0, ICs)
        fig.add_trace(go.Scatter(x=VCE, y=IC_curve, mode="lines",
                                 name=f"IB={IB_uA}µA", line=dict(width=1.5, dash="dot")))
    fig.update_layout(**_layout(title=f"<b>BJT Load Line &nbsp;(VCC={VCC}V, RC={RC}Ω, β={hFE})</b>"),
                      xaxis_title="VCE (V)", yaxis_title="IC (mA)")
    return fig


# ── 10. Logic gate truth table ────────────────────────────────────────────────
def plot_logic(gate: str = "AND") -> go.Figure:
    tables = {
        "AND":  [(0,0,0),(0,1,0),(1,0,0),(1,1,1)],
        "OR":   [(0,0,0),(0,1,1),(1,0,1),(1,1,1)],
        "NAND": [(0,0,1),(0,1,1),(1,0,1),(1,1,0)],
        "NOR":  [(0,0,1),(0,1,0),(1,0,0),(1,1,0)],
        "XOR":  [(0,0,0),(0,1,1),(1,0,1),(1,1,0)],
        "XNOR": [(0,0,1),(0,1,0),(1,0,0),(1,1,1)],
    }
    rows   = tables.get(gate.upper(), tables["AND"])
    labels = [f"A={r[0]}, B={r[1]}" for r in rows]
    outs   = [r[2] for r in rows]
    fig    = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=outs,
        marker_color=[C3 if v else C2 for v in outs],
        text=[str(v) for v in outs], textposition="outside",
    ))
    fig.update_layout(**_layout(
        title=f"<b>{gate.upper()} Gate Truth Table</b>",
        xaxis_title="Inputs",
        yaxis=dict(range=[-0.2,1.6], tickvals=[0,1], ticktext=["LOW (0)","HIGH (1)"],
                   gridcolor=GRID, zerolinecolor=LINE, linecolor=LINE, color=TEXT),
        showlegend=False,
    ))
    return fig


# ── Smart dispatcher ──────────────────────────────────────────────────────────
import re as _re

_MAP = {
    "ohm": plot_ohms_law, "power": plot_power,
    "rlc": plot_rlc,      "frequency response": plot_rlc, "resonance": plot_rlc,
    "rc":  plot_rc,       "rl":    plot_rl,
    "signal": plot_signals, "waveform": plot_signals,
    "op-amp": plot_opamp, "opamp": plot_opamp, "operational amplifier": plot_opamp,
    "diode": plot_diode,
    "transistor": plot_bjt, "bjt": plot_bjt,
    "logic": plot_logic,  "gate": plot_logic,
}

# Sort keys longest-first so multi-word/specific terms are tried before
# short ones that might be contained inside them.
_MAP_KEYS_SORTED = sorted(_MAP.keys(), key=len, reverse=True)


def get_graph_for_topic(topic: str) -> go.Figure | None:
    """
    Pick the most relevant chart for a free-text topic string.
    Uses word-prefix matching (e.g. "diode" matches "Diodes & Rectifiers")
    so short keys like "rc"/"rl" don't false-positive match inside unrelated
    words such as "Circuits" (which contains the substring "rc"), while
    still matching plural/inflected forms like "Diodes", "Resistors", etc.
    """
    t = topic.lower()
    for key in _MAP_KEYS_SORTED:
        if "-" in key or " " in key:
            if key in t:
                return _MAP[key]()
        else:
            # Match key as a whole word OR as the start of a longer word
            # (e.g. "diode" at the start of "diodes"), but never as a
            # substring buried inside an unrelated word like "circuits".
            if _re.search(rf"\b{_re.escape(key)}", t):
                return _MAP[key]()
    return None
