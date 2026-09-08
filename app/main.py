"""
AudioSense AI — IBM Granite Powered Audio Signal Processing Assistant
Main Streamlit application entry point.
"""

from __future__ import annotations

import sys
import os

# Make sure the project root is on the path when running via `streamlit run`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from app.config import load_granite_config
from app.filter_calculator import (
    calculate_rc_cutoff,
    classify_query,
    RESISTANCE_UNITS,
    CAPACITANCE_UNITS,
)
from app.noise_troubleshooter import (
    list_noise_types,
    get_noise_diagnosis,
    format_diagnosis,
)
from app.amplifier_troubleshooter import (
    list_symptoms,
    get_amp_diagnosis,
    format_amp_diagnosis,
)
from app.circuit_advisor import ask_circuit_advisor
from app.granite_service import GraniteService
from app.quick_diagnosis import run_quick_diagnosis

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AudioSense AI",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — clean, professional engineering theme
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* Main background and text */
    .main { background-color: #f8f9fa; }
    .stApp { font-family: "Segoe UI", system-ui, sans-serif; }

    /* Header banner */
    .app-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .app-header h1 { color: white; margin: 0; font-size: 1.8rem; font-weight: 700; }
    .app-header p  { color: #a0c4ff; margin: 0.3rem 0 0 0; font-size: 0.95rem; }

    /* Feature cards */
    .feature-card {
        background: white;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }
    .feature-card h3 { color: #1e3a5f; margin: 0 0 0.5rem 0; font-size: 1.05rem; }
    .feature-card p  { color: #555; margin: 0; font-size: 0.88rem; }

    /* Status badges */
    .badge-live  { background:#d1fae5; color:#065f46; padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; }
    .badge-demo  { background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; }

    /* Disclaimer box */
    .disclaimer {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-left: 4px solid #f97316;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        font-size: 0.85rem;
        color: #7c2d12;
        margin-top: 1rem;
    }

    /* Result box */
    .result-box {
        background: white;
        border-radius: 8px;
        padding: 1.2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }

    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #1a1a2e !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Singleton granite service (cached for session)
# ---------------------------------------------------------------------------

@st.cache_resource
def get_granite_service() -> GraniteService:
    return GraniteService()


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

def render_header(config_status: str) -> None:
    st.markdown(
        f"""
        <div class="app-header">
            <h1>🎛️ AudioSense AI</h1>
            <p>IBM Granite Powered Audio Signal Processing Assistant &nbsp;|&nbsp; {config_status}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer() -> None:
    st.markdown(
        """
        <div class="disclaimer">
            ⚠️ <strong>Engineering Disclaimer:</strong> All results are educational guidance only.
            Circuit conditions, component ratings, supply voltages, and thermal limits
            <strong>must be verified from manufacturer datasheets</strong> before making any hardware
            changes. This tool does not replace professional circuit design review.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

def render_sidebar() -> str:
    st.sidebar.markdown("## 🎛️ AudioSense AI")
    st.sidebar.markdown("*Audio Engineering Assistant*")
    st.sidebar.divider()

    nav = st.sidebar.radio(
        "Navigate",
        options=[
            "🏠 Home",
            "🔊 Noise Troubleshooter",
            "🔧 Filter Assistant",
            "⚡ Amplifier Troubleshooter",
            "💡 Circuit Advisor",
            "⚡ Quick Diagnosis",
        ],
        label_visibility="collapsed",
    )

    st.sidebar.divider()
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.markdown(
        "AudioSense AI helps ECE students troubleshoot audio circuits — "
        "preamplifiers, filters, amplifiers — powered by IBM Granite AI."
    )
    st.sidebar.divider()
    st.sidebar.caption("AudioSense AI v1.0 · ECE Student Project")

    return nav


# ---------------------------------------------------------------------------
# Page: Home
# ---------------------------------------------------------------------------

def page_home(service: GraniteService) -> None:
    st.markdown("### Welcome to AudioSense AI")
    st.markdown(
        "An AI-powered assistant for **Electronics and Telecommunication Engineering** "
        "students — helping you troubleshoot audio circuits, design filters, and understand "
        "amplifier behaviour."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <h3>🔊 Noise Troubleshooter</h3>
                <p>Diagnose 50/60 Hz hum, ground loops, power-supply ripple,
                shielding issues, and broadband noise.</p>
            </div>
            <div class="feature-card">
                <h3>🔧 Filter Assistant</h3>
                <p>Calculate RC cutoff frequencies for low-pass, high-pass,
                band-pass and notch filters. Supports Ω/kΩ/MΩ and pF/nF/µF.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>⚡ Amplifier Troubleshooter</h3>
                <p>Systematic diagnosis for no output, low gain, distortion,
                clipping, oscillation, overheating and DC offset.</p>
            </div>
            <div class="feature-card">
                <h3>💡 Circuit Advisor</h3>
                <p>Ask any question about op-amps, grounding, shielding,
                feedback, distortion and audio circuit design.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <h3>⚡ Quick Diagnosis</h3>
                <p>Describe your audio problem in plain language and get
                instant AI-powered troubleshooting guidance.</p>
            </div>
            <div class="feature-card">
                <h3>📚 Knowledge Base</h3>
                <p>Built-in reference covering amplifiers, op-amps, filters,
                noise, grounding, shielding and distortion.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    if service.is_live:
        st.success(
            f"✅ **IBM Granite is active.** Model: `{service.config.model_id}` "
            "— AI responses are powered by IBM Granite."
        )
    else:
        st.warning(
            "🟡 **Demo Mode active.** IBM Granite is not yet configured. "
            "Responses use the built-in educational knowledge base. "
            "To enable IBM Granite, set the environment variables listed in `.env.example`."
        )

    render_disclaimer()


# ---------------------------------------------------------------------------
# Page: Noise Troubleshooter
# ---------------------------------------------------------------------------

def page_noise() -> None:
    st.markdown("### 🔊 Noise Troubleshooter")
    st.markdown(
        "Select a noise type to get **probable causes**, **diagnostic checks**, "
        "and **recommended solutions**."
    )

    noise_types = list_noise_types()
    selected = st.selectbox("Select noise type:", noise_types)

    if st.button("🔍 Diagnose", key="noise_btn", type="primary"):
        diagnosis = get_noise_diagnosis(selected)
        if diagnosis:
            st.markdown("---")
            st.markdown(format_diagnosis(diagnosis))
        else:
            st.error("Diagnosis not found.")

    render_disclaimer()


# ---------------------------------------------------------------------------
# Page: Filter Assistant
# ---------------------------------------------------------------------------

def page_filter() -> None:
    st.markdown("### 🔧 Filter Assistant")
    st.markdown(
        "Calculate the **RC cutoff frequency** for your filter design. "
        "Formula: **fc = 1 / (2 × π × R × C)**"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Resistance**")
        r_col1, r_col2 = st.columns([2, 1])
        with r_col1:
            r_value = st.number_input(
                "Value", min_value=0.001, value=10.0, step=0.1,
                key="r_val", label_visibility="collapsed"
            )
        with r_col2:
            r_unit = st.selectbox(
                "Unit", ["kΩ", "Ω", "MΩ"],
                key="r_unit", label_visibility="collapsed"
            )

    with col2:
        st.markdown("**Capacitance**")
        c_col1, c_col2 = st.columns([2, 1])
        with c_col1:
            c_value = st.number_input(
                "Value", min_value=0.001, value=15.9, step=0.1,
                key="c_val", label_visibility="collapsed"
            )
        with c_col2:
            c_unit = st.selectbox(
                "Unit", ["nF", "pF", "µF"],
                key="c_unit", label_visibility="collapsed"
            )

    filter_type = st.selectbox(
        "Filter Type",
        ["Low-Pass", "High-Pass", "Band-Pass", "Notch"],
    )

    if st.button("⚙️ Calculate Cutoff Frequency", type="primary"):
        try:
            result = calculate_rc_cutoff(r_value, r_unit, c_value, c_unit, filter_type)
            st.markdown("---")

            # Hero metric
            colA, colB, colC = st.columns(3)
            colA.metric("Cutoff Frequency (fc)", result.fc_display)
            colB.metric("Resistance (R)", result.r_display)
            colC.metric("Capacitance (C)", result.c_display)

            st.markdown("---")
            st.markdown(result.description())

        except ValueError as e:
            st.error(f"Input error: {e}")

    st.markdown("---")
    with st.expander("📘 Quick Reference — Common Values"):
        st.markdown(
            """
| R | C | fc |
|---|---|---|
| 10 kΩ | 15.9 nF | ≈ 1 kHz |
| 10 kΩ | 1.59 nF | ≈ 10 kHz |
| 1 kΩ | 159 nF | ≈ 1 kHz |
| 100 kΩ | 159 nF | ≈ 10 Hz |
| 47 kΩ | 3.3 nF | ≈ 1 kHz |
| 10 kΩ | 318 nF | ≈ 50 Hz notch |
            """
        )

    render_disclaimer()


# ---------------------------------------------------------------------------
# Page: Amplifier Troubleshooter
# ---------------------------------------------------------------------------

def page_amplifier() -> None:
    st.markdown("### ⚡ Amplifier Troubleshooter")
    st.markdown(
        "Select the symptom you are observing to get a systematic "
        "**diagnosis** with probable causes, checks, and solutions."
    )

    symptoms = list_symptoms()
    selected = st.selectbox("Select symptom:", symptoms)

    if st.button("🔍 Diagnose Symptom", key="amp_btn", type="primary"):
        diagnosis = get_amp_diagnosis(selected)
        if diagnosis:
            st.markdown("---")
            st.markdown(format_amp_diagnosis(diagnosis))
        else:
            st.error("Diagnosis data not found.")

    render_disclaimer()


# ---------------------------------------------------------------------------
# Page: Circuit Advisor (AI)
# ---------------------------------------------------------------------------

def page_circuit_advisor(service: GraniteService) -> None:
    st.markdown("### 💡 Circuit Advisor")

    if service.is_live:
        st.success(f"🟢 IBM Granite is active — `{service.config.model_id}`")
    else:
        st.warning(
            "🟡 **Demo Mode** — IBM Granite is not configured. "
            "Responses are generated from the built-in knowledge base, not IBM Granite."
        )

    st.markdown(
        "Ask any question about **op-amps, grounding, shielding, distortion, "
        "feedback, filter design, or amplifier troubleshooting**."
    )

    example_qs = [
        "Why does my op-amp circuit oscillate?",
        "How do I eliminate a ground loop?",
        "What is the difference between Butterworth and Bessel filters?",
        "How do I calculate gain for a non-inverting amplifier?",
        "What causes crossover distortion and how do I fix it?",
        "How should I place decoupling capacitors?",
    ]

    with st.expander("💬 Example Questions"):
        for q in example_qs:
            st.markdown(f"- *{q}*")

    question = st.text_area(
        "Your question:",
        placeholder="e.g. How do I troubleshoot oscillation in my op-amp circuit?",
        height=100,
    )

    if st.button("💡 Ask Circuit Advisor", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Processing your question..."):
                result = ask_circuit_advisor(question)

            st.markdown("---")

            # Source label
            if result["is_demo"]:
                st.info("📋 Response from built-in knowledge base (Demo Mode — not IBM Granite)")
            else:
                st.success(f"🟢 Response from IBM Granite · Model: `{result['model']}`")

            st.markdown(result["answer"])

    render_disclaimer()


# ---------------------------------------------------------------------------
# Page: Quick Diagnosis
# ---------------------------------------------------------------------------

def page_quick_diagnosis(service: GraniteService) -> None:
    st.markdown("### ⚡ Quick Diagnosis")
    st.markdown(
        "Describe your audio circuit problem in plain language. "
        "The assistant will detect specific symptoms and provide targeted guidance."
    )

    if service.is_live:
        st.success(f"🟢 IBM Granite active — `{service.config.model_id}`")
    else:
        st.warning(
            "🟡 **Demo Mode** — IBM Granite not configured. "
            "Responses use the built-in knowledge base."
        )

    problem = st.text_area(
        "Describe your problem:",
        placeholder=(
            "e.g. My audio amplifier has a 60 Hz hum even when there is no input connected. "
            "I am using an unbalanced RCA connection between my preamp and power amp."
        ),
        height=130,
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        run = st.button("🚀 Run Quick Diagnosis", type="primary")

    if run:
        if not problem.strip():
            st.warning("Please describe your problem.")
        else:
            with st.spinner("Analysing your problem..."):
                if service.is_live:
                    # Live IBM Granite path — full AI response
                    result = ask_circuit_advisor(problem)
                else:
                    # Demo mode — structured symptom-specific response
                    result = run_quick_diagnosis(problem)

            # Show category / symptom badge
            category = result.get("category") or classify_query(problem)
            category_labels = {
                "noise": "🔊 Noise / Hum / Interference",
                "filter": "🔧 Filter Design",
                "amplifier": "⚡ Amplifier Issue",
                "circuit": "💡 Circuit Design",
                "general": "📚 General Audio Engineering",
            }
            symptoms = result.get("symptoms", [])
            if symptoms:
                st.info(
                    f"**Detected symptom(s)**: {', '.join(symptoms)}"
                )
            else:
                st.info(
                    f"**Detected category**: {category_labels.get(category, category)}"
                )

            st.markdown("---")

            if result["is_demo"]:
                st.info("📋 Response from built-in knowledge base (Demo Mode — not IBM Granite)")
            else:
                st.success(f"🟢 Response from IBM Granite · Model: `{result['model']}`")

            st.markdown(result["answer"])

    render_disclaimer()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    service = get_granite_service()

    # Config status for header
    if service.is_live:
        config_status = '<span class="badge-live">🟢 IBM Granite Live</span>'
    else:
        config_status = '<span class="badge-demo">🟡 Demo Mode</span>'

    render_header(config_status)

    nav = render_sidebar()

    if nav == "🏠 Home":
        page_home(service)
    elif nav == "🔊 Noise Troubleshooter":
        page_noise()
    elif nav == "🔧 Filter Assistant":
        page_filter()
    elif nav == "⚡ Amplifier Troubleshooter":
        page_amplifier()
    elif nav == "💡 Circuit Advisor":
        page_circuit_advisor(service)
    elif nav == "⚡ Quick Diagnosis":
        page_quick_diagnosis(service)


if __name__ == "__main__":
    main()
