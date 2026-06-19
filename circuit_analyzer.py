"""
circuit_analyzer.py
Component value parser, formula library, quick calculators, topic list.
No AI calls — pure Python maths used in the sidebar calculators.
"""

import re
import math
from typing import Optional
from dataclasses import dataclass, field


# ── Data class ─────────────────────────────────────────────────────────────────
@dataclass
class CircuitContext:
    resistances:  list[float] = field(default_factory=list)
    capacitances: list[float] = field(default_factory=list)
    inductances:  list[float] = field(default_factory=list)
    voltages:     list[float] = field(default_factory=list)
    currents:     list[float] = field(default_factory=list)
    frequencies:  list[float] = field(default_factory=list)
    topic_hints:  list[str]   = field(default_factory=list)


# ── SI prefix map ──────────────────────────────────────────────────────────────
_SI = {"T":1e12,"G":1e9,"M":1e6,"k":1e3,"":1,"m":1e-3,"u":1e-6,"µ":1e-6,"n":1e-9,"p":1e-12}

def _parse(text: str) -> Optional[float]:
    m = re.match(r"([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)\s*([TGMkmuµnp]?)", text.strip())
    if not m:
        return None
    return float(m.group(1)) * _SI.get(m.group(2), 1)


# ── Quick calculators ──────────────────────────────────────────────────────────
def calc_ohms_law(V=None, I=None, R=None) -> dict:
    res = {}
    try:
        if V and I:
            res["R"] = f"{V/I:.4g} Ω"
            res["P"] = f"{V*I*1000:.4g} mW"
        elif V and R:
            res["I"] = f"{V/R*1000:.4g} mA"
            res["P"] = f"{V*V/R*1000:.4g} mW"
        elif I and R:
            res["V"] = f"{I*R:.4g} V"
            res["P"] = f"{I*I*R*1000:.4g} mW"
    except ZeroDivisionError:
        pass
    return res

def calc_rc(R: float, C: float) -> dict:
    tau = R * C
    fc  = 1 / (2 * math.pi * tau) if tau else 0
    return {
        "τ (time constant)": f"{tau*1000:.4g} ms",
        "Cutoff frequency":  f"{fc:.4g} Hz",
        "t₆₃% (one τ)":      f"{tau*1000:.4g} ms",
        "t₉₉% (5τ)":         f"{tau*5000:.4g} ms",
    }

def calc_rl(R: float, L: float) -> dict:
    if R == 0:
        return {}
    tau = L / R
    fc  = R / (2 * math.pi * L) if L else 0
    return {
        "τ (time constant)": f"{tau*1000:.4g} ms",
        "Cutoff frequency":  f"{fc:.4g} Hz",
    }

def calc_rlc(R: float, L: float, C: float) -> dict:
    if L <= 0 or C <= 0:
        return {}
    f0 = 1 / (2 * math.pi * math.sqrt(L * C))
    Q  = (1 / R) * math.sqrt(L / C) if R else 0
    BW = f0 / Q if Q else 0
    return {
        "Resonant freq f₀": f"{f0:.4g} Hz",
        "Quality factor Q":  f"{Q:.4g}",
        "Bandwidth BW":      f"{BW:.4g} Hz",
        "Z₀":                f"{math.sqrt(L/C):.4g} Ω",
    }

def calc_vdiv(Vin: float, R1: float, R2: float) -> dict:
    if R1 + R2 == 0:
        return {}
    Vout  = Vin * R2 / (R1 + R2)
    ratio = R2 / (R1 + R2)
    return {
        "V_out": f"{Vout:.4g} V",
        "Ratio": f"{ratio:.4g}",
        "Attenuation": f"{20*math.log10(ratio):.2f} dB" if ratio > 0 else "—",
    }

def calc_opamp(R1: float, Rf: float, inverting: bool = True) -> dict:
    if R1 == 0:
        return {}
    if inverting:
        Av = -Rf / R1
        return {
            "Av (inverting)": f"{Av:.4g}",
            "|Av|":            f"{abs(Av):.4g}",
            "Gain (dB)":       f"{20*math.log10(abs(Av)):.2f} dB" if Av != 0 else "—",
        }
    else:
        Av = 1 + Rf / R1
        return {
            "Av (non-inv)": f"{Av:.4g}",
            "Gain (dB)":    f"{20*math.log10(Av):.2f} dB" if Av > 0 else "—",
        }


# ── Topics list ────────────────────────────────────────────────────────────────
def get_topics() -> list[str]:
    return [
        "Ohm's Law", "Kirchhoff's Laws (KVL/KCL)", "DC Circuit Analysis",
        "AC Circuit Analysis", "RC Circuits", "RL Circuits", "RLC Circuits",
        "Operational Amplifiers", "Diodes & Rectifiers", "BJT Transistors",
        "MOSFET Transistors", "Logic Gates", "Combinational Logic",
        "Sequential Logic & Flip-Flops", "Power Electronics",
        "Filters (Low / High / Band Pass)", "Thevenin & Norton Theorems",
        "Superposition Principle", "Voltage Dividers", "Current Dividers",
        "Impedance & Admittance", "Resonance", "Signal Waveforms",
        "Microcontroller GPIO Interfacing", "Communication Circuits",
    ]


# ── Built-in formula library ───────────────────────────────────────────────────
FORMULA_LIBRARY: dict[str, dict[str, str]] = {
    "Ohm's Law": {
        "V = I × R":   "Voltage = Current × Resistance",
        "I = V / R":   "Current = Voltage / Resistance",
        "R = V / I":   "Resistance = Voltage / Current",
    },
    "Power": {
        "P = V × I":   "Power = Voltage × Current",
        "P = I² × R":  "Power from current",
        "P = V² / R":  "Power from voltage",
    },
    "RC Circuit": {
        "τ = R × C":              "Time constant",
        "Vc(t) = V₀(1−e^−t/τ)":  "Charging voltage",
        "fc = 1 / (2πRC)":        "Cutoff frequency",
    },
    "RL Circuit": {
        "τ = L / R":              "Time constant",
        "IL(t) = (V/R)(1−e^−t/τ)":"Current build-up",
        "fc = R / (2πL)":         "Cutoff frequency",
    },
    "RLC Circuit": {
        "f₀ = 1 / (2π√LC)":      "Resonant frequency",
        "Q = (1/R)√(L/C)":        "Quality factor",
        "BW = f₀ / Q":            "Bandwidth",
    },
    "Op-Amp": {
        "Av = −Rf/Rin":           "Inverting gain",
        "Av = 1 + Rf/R1":         "Non-inverting gain",
        "CMRR = Ad / Ac":         "Common-mode rejection ratio",
    },
    "Diode": {
        "I = Is(e^(V/nVT)−1)":   "Shockley equation",
        "VT = kT/q ≈ 26 mV":     "Thermal voltage at 300K",
    },
    "Capacitor": {
        "Xc = 1/(2πfC)":          "Capacitive reactance",
        "Q = C × V":               "Charge stored",
        "E = ½CV²":                "Energy stored",
    },
    "Inductor": {
        "XL = 2πfL":              "Inductive reactance",
        "E = ½LI²":               "Energy stored",
        "V = L × dI/dt":          "Inductor voltage",
    },
    "Kirchhoff's Laws": {
        "ΣV = 0 (KVL)":          "Voltages around a closed loop sum to zero",
        "ΣI = 0 (KCL)":          "Currents at a node sum to zero",
    },
}

# Sample problems shown in the Ask tab
SAMPLE_PROBLEMS = [
    "A 4.7 kΩ resistor has 9 V across it. Find the current and power dissipated.",
    "RC circuit: R = 10 kΩ, C = 100 µF. Find time constant and cutoff frequency.",
    "Design an inverting op-amp amplifier with gain = -10 using Rin = 1 kΩ.",
    "Series RLC: R = 50 Ω, L = 10 mH, C = 1 µF. Find resonant frequency and Q.",
    "Using KVL, find the current in a loop with 12 V, 3 kΩ and 1 kΩ in series.",
    "BJT switch: hFE = 100, VCC = 12 V, RC = 1 kΩ. Find IC(sat) and required IB.",
    "Non-inverting op-amp: Rf = 100 kΩ, R1 = 10 kΩ, Vin = 1 V. Find Vout.",
    "Parallel RC at 1 kHz: R = 1 kΩ, C = 100 nF. Find impedance magnitude.",
]
