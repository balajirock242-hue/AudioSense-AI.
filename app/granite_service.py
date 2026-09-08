"""
IBM Granite language-model service for AudioSense AI.

Credentials are loaded exclusively from environment variables — never
hard-coded.  When credentials are absent the service operates in DEMO
MODE and all responses are clearly labelled as such.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from app.config import GraniteConfig, load_granite_config

# ---------------------------------------------------------------------------
# Knowledge-base loader
# ---------------------------------------------------------------------------

_KB_PATH = Path(__file__).parent.parent / "knowledge_base" / "audio_engineering.md"


def _load_knowledge_base() -> str:
    """Return the contents of the local knowledge base file."""
    if _KB_PATH.exists():
        return _KB_PATH.read_text(encoding="utf-8")
    return ""


_KNOWLEDGE_BASE: str = _load_knowledge_base()

# ---------------------------------------------------------------------------
# IBM Granite client (optional dependency)
# ---------------------------------------------------------------------------

def _build_ibm_client(config: GraniteConfig):
    """
    Attempt to instantiate an IBM watsonx.ai client.
    Returns the client object or None if the SDK is not installed.
    """
    try:
        from ibm_watsonx_ai import APIClient, Credentials  # type: ignore
        credentials = Credentials(url=config.endpoint, api_key=config.api_key)
        return APIClient(credentials)
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Context helpers
# ---------------------------------------------------------------------------

def _extract_category(context: Optional[str]) -> str:
    """
    Extract the pre-classified category tag injected by ask_circuit_advisor.

    ask_circuit_advisor prepends ``CATEGORY:<name>\\n`` to every context string.
    Returns the category name, or an empty string when no tag is present.
    """
    if context and context.startswith("CATEGORY:"):
        first_line = context.split("\n", 1)[0]
        return first_line[len("CATEGORY:"):]
    return ""


# ---------------------------------------------------------------------------
# Main service
# ---------------------------------------------------------------------------

class GraniteService:
    """
    Wrapper around IBM Granite via watsonx.ai.

    • When IBM_API_KEY / IBM_PROJECT_ID are configured and the
      ibm-watsonx-ai SDK is installed, live Granite responses are
      returned.
    • Otherwise DEMO MODE is active and a clearly labelled fallback
      response is returned.  DEMO MODE responses NEVER claim to be
      from IBM Granite.
    """

    SYSTEM_PROMPT = (
        "You are AudioSense AI, an expert Electronics and Telecommunication "
        "Engineering assistant specialising in audio signal processing, "
        "preamplifiers, filters, amplifiers, and audio circuit troubleshooting. "
        "Provide precise, technical, actionable guidance. "
        "Always remind users to verify component ratings and circuit conditions "
        "before making hardware changes. "
        "Use the following knowledge base as your primary reference:\n\n"
        "{knowledge_base}"
    )

    def __init__(self) -> None:
        self.config: GraniteConfig = load_granite_config()
        self._client = None
        if self.config.is_configured:
            self._client = _build_ibm_client(self.config)

    @property
    def is_live(self) -> bool:
        """True only when credentials are configured AND client was built."""
        return self.config.is_configured and self._client is not None

    @property
    def mode_label(self) -> str:
        return "🟢 IBM Granite (Live)" if self.is_live else "🟡 Demo Mode"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query(self, user_message: str, context: Optional[str] = None) -> dict:
        """
        Submit a question and return a dict:
            {
                "answer": str,
                "source": "ibm_granite" | "demo",
                "model": str | None,
                "is_demo": bool,
            }
        """
        if self.is_live:
            return self._query_granite(user_message, context)
        return self._demo_response(user_message, context)

    # ------------------------------------------------------------------
    # Live Granite call
    # ------------------------------------------------------------------

    def _query_granite(self, user_message: str, context: Optional[str]) -> dict:
        try:
            from ibm_watsonx_ai.foundation_models import ModelInference  # type: ignore
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as Params  # type: ignore

            system = self.SYSTEM_PROMPT.format(
                knowledge_base=_KNOWLEDGE_BASE[:6000]  # stay within token budget
            )
            prompt = (
                f"[SYSTEM]\n{system}\n\n"
                f"[CONTEXT]\n{context}\n\n" if context else
                f"[SYSTEM]\n{system}\n\n"
            ) + f"[USER]\n{user_message}\n\n[ASSISTANT]\n"

            model = ModelInference(
                model_id=self.config.model_id,
                project_id=self.config.project_id,
                api_client=self._client,
                params={
                    Params.MAX_NEW_TOKENS: 800,
                    Params.TEMPERATURE: 0.3,
                    Params.TOP_P: 0.9,
                    Params.REPETITION_PENALTY: 1.1,
                },
            )
            result = model.generate_text(prompt=prompt)
            answer = result.strip() if isinstance(result, str) else str(result)
            return {
                "answer": answer,
                "source": "ibm_granite",
                "model": self.config.model_id,
                "is_demo": False,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "answer": (
                    f"⚠️ IBM Granite request failed: {exc}\n\n"
                    "Falling back to demo response.\n\n"
                    + self._demo_response(user_message, context)["answer"]
                ),
                "source": "demo",
                "model": None,
                "is_demo": True,
            }

    # ------------------------------------------------------------------
    # Demo-mode fallback — clearly labelled, never claims to be Granite
    # ------------------------------------------------------------------

    def _demo_response(self, user_message: str, context: Optional[str]) -> dict:
        # Prefer the pre-classified category encoded in context (set by circuit_advisor)
        # over re-doing independent keyword matching, which is narrower and causes misses.
        category = _extract_category(context)

        if category == "noise":
            answer = _DEMO_NOISE
        elif category == "filter":
            answer = _DEMO_FILTER
        elif category == "amplifier":
            answer = _DEMO_AMP
        elif category == "circuit":
            answer = _DEMO_CIRCUIT
        elif category == "general":
            answer = _DEMO_GENERIC
        else:
            # No structured context (e.g. called directly without a CATEGORY tag);
            # fall back to keyword matching on the message.
            msg_lower = user_message.lower()
            if any(k in msg_lower for k in ["hum", "50 hz", "60 hz", "ground loop"]):
                answer = _DEMO_HUM
            elif any(k in msg_lower for k in ["filter", "cutoff", "low-pass", "high-pass", "band"]):
                answer = _DEMO_FILTER
            elif any(k in msg_lower for k in ["amplif", "gain", "clip", "distort", "oscillat"]):
                answer = _DEMO_AMP
            elif any(k in msg_lower for k in ["op-amp", "opamp", "feedback", "shield", "ground"]):
                answer = _DEMO_CIRCUIT
            elif any(k in msg_lower for k in ["noise", "ripple", "interference"]):
                answer = _DEMO_NOISE
            else:
                answer = _DEMO_GENERIC

        return {
            "answer": answer,
            "source": "demo",
            "model": None,
            "is_demo": True,
        }


# ---------------------------------------------------------------------------
# Demo responses — educational, factually accurate, clearly NOT from Granite
# ---------------------------------------------------------------------------

_DEMO_HUM = """\
**[DEMO MODE — Not IBM Granite]**

**50/60 Hz Hum — Probable Causes & Solutions**

**Most Common Cause: Ground Loop**
A ground loop occurs when two pieces of equipment share the same signal ground but are connected to different points on the AC mains earth, creating a circulating current that induces hum.

**Diagnostic Steps:**
1. Disconnect all input sources one at a time — note whether hum disappears.
2. Measure AC voltage between chassis of each piece of equipment (should be < 5 mV).
3. Try a single cable run with all other inputs disconnected.

**Recommended Solutions:**
- Use a balanced (XLR) connection or a DI box to break the loop.
- Connect all equipment to the same mains outlet (common earth point).
- Install an audio isolation transformer on suspect connection.
- Apply star-ground topology — single converging ground point.
- Route signal cables at 90° to mains cables.

> ⚠️ Educational guidance only. Verify circuit conditions before making hardware changes.
"""

_DEMO_FILTER = """\
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

_DEMO_AMP = """\
**[DEMO MODE — Not IBM Granite]**

**Amplifier Troubleshooting Guide**

| Symptom | Likely Cause | Action |
|---|---|---|
| No output | No supply / open feedback R | Check rails, probe stage by stage |
| Low gain | Wrong Rf/R1 ratio | Measure resistors in-circuit |
| Clipping | Insufficient headroom | Reduce input level or increase supply |
| Oscillation | Missing decoupling caps | Add 100 nF ceramic at supply pins |
| Distortion | Non-linearity / clipping | Check operating point, bias |
| Overheating | Excess quiescent current | Adjust bias, check for oscillation |
| DC offset | Input offset voltage | Check op-amp spec, add offset null |

**Gain Formula (Non-Inverting):**
```
Av = 1 + (Rf / R1)
```

> ⚠️ Educational guidance only. Verify component ratings before hardware changes.
"""

_DEMO_CIRCUIT = """\
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

_DEMO_NOISE = """\
**[DEMO MODE — Not IBM Granite]**

**Noise, Hum & Ripple Troubleshooting**

**50/60 Hz Hum — Ground Loops**
A ground loop occurs when two pieces of equipment share the same signal ground but connect to different mains earth points, inducing a circulating current.
- Disconnect input sources one at a time to identify the offending cable.
- Use a balanced (XLR) connection or a DI box to break the loop.
- Connect all equipment to the same mains outlet (common earth point).
- Install an audio isolation transformer on the suspect connection.
- Route signal cables at 90° to mains cables.

**Noise Types:**
- *Thermal noise*: Vn = √(4kTRB) — reduce bandwidth and source resistance.
- *1/f (flicker) noise*: Dominant below 1 kHz — use JFET-input op-amps.
- *Power supply ripple*: Add 100 nF ceramic + 10 µF electrolytic at each IC supply pin.

**Power-Supply Ripple Solutions:**
1. Increase bulk filter capacitance (1000–10 000 µF).
2. Use a regulated supply (LM7812, LDO).
3. Add RC decoupling on supply rail to sensitive stages.
4. Check electrolytic capacitor ESR — replace aging caps.

**Shielding & Layout:**
- Apply star-ground topology — all returns converge at one point.
- Keep input traces short and away from switching nodes.
- Use coaxial cable for high-impedance signal routing.
- Ground cable shields at the source end only (prevents ground loop via shield).

> ⚠️ Educational guidance only. Verify circuit conditions before hardware changes.
"""

_DEMO_GENERIC = """\
**[DEMO MODE — Not IBM Granite]**

Welcome to **AudioSense AI** — your Audio Signal Processing Assistant.

I can help with:
- **Noise Troubleshooting**: Hum, ground loops, ripple, interference
- **Filter Design**: RC cutoff calculations, filter types, component selection
- **Amplifier Troubleshooting**: No output, low gain, distortion, oscillation
- **Circuit Advice**: Op-amp configurations, grounding, shielding, feedback

**To enable IBM Granite AI responses**, configure the following environment variables:
```
IBM_API_KEY=your_api_key
IBM_PROJECT_ID=your_project_id
IBM_GRANITE_MODEL=ibm/granite-13b-chat-v2
IBM_ENDPOINT=https://us-south.ml.cloud.ibm.com
```

Ask me anything about audio circuit engineering!

> ⚠️ Educational guidance only. Verify component ratings and circuit conditions before hardware changes.
"""
