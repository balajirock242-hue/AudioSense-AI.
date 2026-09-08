"""
Quick Diagnosis — analyses a free-text audio problem description, detects
one or more specific symptoms, and returns targeted guidance drawn from the
structured amplifier and noise knowledge bases.

Design principles
-----------------
* Symptom detection is independent of the broad classify_query() categories
  so that specific symptoms (low gain, distortion, 50 Hz hum, …) are matched
  directly rather than collapsing everything into one generic bucket.
* Multiple matched symptoms are each formatted and concatenated so the user
  gets targeted advice for every problem they described.
* Demo mode is clearly labelled.  No response ever claims to come from
  IBM Granite when it does not.
* The IBM Granite integration in granite_service.py is untouched.
"""

from __future__ import annotations

from app.amplifier_troubleshooter import (
    AmpDiagnosis,
    format_amp_diagnosis,
    get_amp_diagnosis,
)
from app.noise_troubleshooter import (
    NoiseDiagnosis,
    format_diagnosis as format_noise_diagnosis,
    get_noise_diagnosis,
)
from app.filter_calculator import classify_query

# ---------------------------------------------------------------------------
# Symptom detection rules
#
# Each entry maps a canonical knowledge-base key (used to look up the
# structured AmpDiagnosis / NoiseDiagnosis) to a set of trigger keywords.
# Keys prefixed with "amp:" look up AmpDiagnosis; "noise:" look up
# NoiseDiagnosis.  Matching is substring-based on the lower-cased query.
# Rules are evaluated in order — first match wins per domain so that the
# most specific rules take priority.
# ---------------------------------------------------------------------------

_AMP_SYMPTOM_RULES: list[tuple[str, set[str]]] = [
    # Most specific first
    ("No Output",    {"no output", "no signal", "nothing at output", "silent", "dead"}),
    ("Low Gain",     {"low gain", "gain is low", "gain too low", "insufficient gain",
                      "not enough gain", "gain lower", "gain is lower", "reduced gain",
                      "weak output", "output too low", "output level low"}),
    ("Clipping",     {"clipping", "clips", "flat top", "flattop", "saturating",
                      "saturation", "hitting the rail", "maxing out"}),
    ("Distortion",   {"distortion", "distorted", "harmonic", "thd", "crossover",
                      "non-linear", "nonlinear", "slew rate", "slew-rate",
                      "sounds bad", "sounds harsh", "harsh sound", "fuzzy", "fuzz"}),
    ("Oscillation",  {"oscillat", "ringing", "rf oscillat", "self-oscillat",
                      "unstable", "instability", "squealing", "squeals", "howling",
                      "phase margin", "feedback loop"}),
    ("Overheating",  {"overheat", "overheating", "hot", "runs hot", "too hot",
                      "thermal", "burning", "warm", "excessive heat"}),
    ("DC Offset",    {"dc offset", "dc at output", "output dc", "offset voltage",
                      "bias offset", "output drifts", "output voltage offset"}),
    ("Noise",        {"hiss", "broadband noise", "amplifier noise", "white noise",
                      "thermal noise", "noise floor", "high noise", "noisy amp",
                      "background noise", "noise in amp"}),
]

_NOISE_SYMPTOM_RULES: list[tuple[str, set[str]]] = [
    ("50/60 Hz Hum",              {"hum", "50 hz", "60 hz", "50hz", "60hz",
                                   "mains hum", "ac hum", "power line hum"}),
    ("Ground Loops",              {"ground loop", "ground loops", "earth loop",
                                   "loop current"}),
    ("Power-Supply Ripple",       {"ripple", "power supply noise", "psu noise",
                                   "supply noise", "psu ripple", "power ripple",
                                   "supply ripple"}),
    ("Shielding / Interference (RFI/EMI)",
                                  {"interference", "rfi", "emi", "shielding",
                                   "radio frequency", "electromagnetic",
                                   "pickup", "radiated noise"}),
    ("Amplifier Noise (Hiss/Broadband)",
                                  {"noise", "hiss", "broadband"}),
]

# ---------------------------------------------------------------------------
# Filter / circuit category labels (no structured data — use demo strings)
# ---------------------------------------------------------------------------

_FILTER_DEMO = """\
**[DEMO MODE — Not IBM Granite]**

**RC Filter — Key Concepts**

**Cutoff Frequency:**
```
fc = 1 / (2 × π × R × C)
```

| Filter Type | Configuration |
|---|---|
| Low-Pass | R in series, C to ground |
| High-Pass | C in series, R to ground |
| Band-Pass | High-pass stage → Low-pass stage |
| Notch | Twin-T or active notch circuit |

**Component Recommendations:**
- Use 1% metal-film resistors for accurate fc.
- Use C0G/NP0 ceramic or film capacitors — avoid X7R (varies with voltage).
- At fc, signal is at −3 dB and phase shifts ±45°.
- Roll-off rate: −20 dB/decade per order (first-order RC).

> ⚠️ Educational guidance only. Verify component ratings before assembly.
"""

_CIRCUIT_DEMO = """\
**[DEMO MODE — Not IBM Granite]**

**Op-Amp & Circuit Design Guidance**

**Stability Best Practices:**
- Add 100 nF ceramic decoupling capacitor at each supply pin (as close as possible).
- Add 10 pF–100 pF across feedback resistor Rf to improve phase margin.
- Keep input and output traces separated on PCB to prevent feedback.
- Phase margin > 45° required for stable operation.

**Grounding:**
- Use star-ground topology — all returns converge at one point.
- Separate analog and digital grounds; join at single point near power entry.
- Chassis ground connects to signal ground at ONE point only.

**Shielding:**
- Ground cable shields at the source end only (prevents ground loop via shield).
- Use balanced/differential connections for cable runs > 1 m.

> ⚠️ Educational guidance only. Verify circuit conditions before hardware changes.
"""

_GENERIC_DEMO = """\
**[DEMO MODE — Not IBM Granite]**

Welcome to **AudioSense AI — Quick Diagnosis**.

Please describe your specific audio problem. I can help with:
- **No output / low gain / distortion / clipping** — amplifier faults
- **Oscillation / overheating / DC offset** — op-amp stability issues
- **50/60 Hz hum / ground loops / ripple** — noise and grounding
- **Shielding / interference / RFI** — EMI problems
- **Filter design** — cutoff frequency, filter types

Provide as much detail as possible (e.g. "My op-amp has low gain and noticeable distortion").

> ⚠️ Educational guidance only. Verify component ratings and circuit conditions before hardware changes.
"""

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_quick_diagnosis(problem: str) -> dict:
    """
    Analyse *problem* and return a diagnosis dict:

        {
            "answer":   str,   # Markdown-formatted response
            "symptoms": list,  # names of detected symptoms (may be empty)
            "category": str,   # broad category ("amplifier", "noise", …)
            "is_demo":  bool,
            "source":   str,   # always "demo" in demo mode
            "model":    None,
        }

    This function never calls the Granite service — it is the structured
    demo-mode path used exclusively when IBM Granite is not configured.
    Callers that have a live Granite client should use GraniteService.query()
    instead (the granite_service module is untouched).
    """
    category = classify_query(problem)
    sections, detected_symptoms = _build_sections(problem, category)

    if sections:
        header = (
            "**[DEMO MODE — Not IBM Granite]**\n\n"
            f"**Quick Diagnosis — {len(detected_symptoms)} symptom(s) detected**\n\n"
        )
        answer = header + "\n\n---\n\n".join(sections)
    else:
        answer = _fallback(category)

    return {
        "answer":   answer,
        "symptoms": detected_symptoms,
        "category": category,
        "is_demo":  True,
        "source":   "demo",
        "model":    None,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_sections(problem: str, category: str) -> tuple[list[str], list[str]]:
    """
    Detect all matching symptoms and build one formatted section per symptom.
    Returns (sections, symptom_names).
    """
    q = problem.lower()
    sections: list[str] = []
    symptom_names: list[str] = []

    # --- Amplifier symptoms ---
    for symptom_key, keywords in _AMP_SYMPTOM_RULES:
        if any(kw in q for kw in keywords):
            diagnosis = get_amp_diagnosis(symptom_key)
            if diagnosis:
                sections.append(format_amp_diagnosis(diagnosis))
                symptom_names.append(symptom_key)

    # --- Noise symptoms ---
    for noise_key, keywords in _NOISE_SYMPTOM_RULES:
        if any(kw in q for kw in keywords):
            # Avoid duplicating "Noise" if the amplifier Noise entry was already added
            if noise_key == "Amplifier Noise (Hiss/Broadband)" and "Noise" in symptom_names:
                continue
            diagnosis = get_noise_diagnosis(noise_key)
            if diagnosis:
                sections.append(format_noise_diagnosis(diagnosis))
                symptom_names.append(noise_key)

    # --- Filter / circuit: no structured data, append demo strings ---
    if not sections:
        if category == "filter":
            sections.append(_FILTER_DEMO)
            symptom_names.append("Filter Design")
        elif category == "circuit":
            sections.append(_CIRCUIT_DEMO)
            symptom_names.append("Circuit Design")

    return sections, symptom_names


def _fallback(category: str) -> str:
    """Return a fallback demo string for unrecognised queries."""
    if category == "filter":
        return _FILTER_DEMO
    if category == "circuit":
        return _CIRCUIT_DEMO
    return _GENERIC_DEMO
