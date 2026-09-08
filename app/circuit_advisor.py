"""
Circuit Advisor — answers questions about op-amps, grounding, shielding,
distortion, feedback, and amplifier troubleshooting using the Granite
service (or demo mode).
"""

from __future__ import annotations

from app.filter_calculator import classify_query
from app.granite_service import GraniteService


_CONTEXT_MAP = {
    "noise": (
        "The user is asking about audio noise, hum, interference, or power-supply ripple. "
        "Focus on noise sources, ground loops, shielding, and power-supply filtering."
    ),
    "filter": (
        "The user is asking about electronic filters (low-pass, high-pass, band-pass, notch). "
        "Focus on RC cutoff frequency calculations, filter topologies, and component selection."
    ),
    "amplifier": (
        "The user is asking about amplifier troubleshooting or amplifier design. "
        "Focus on op-amp configurations, gain, distortion, clipping, oscillation, and DC offset."
    ),
    "circuit": (
        "The user is asking about circuit design, grounding, shielding, feedback, or PCB layout. "
        "Focus on best practices for analog audio circuit design."
    ),
    "general": (
        "The user has a general audio engineering question. "
        "Provide a thorough, educational answer about audio signal processing."
    ),
}

_service: GraniteService | None = None


def _get_service() -> GraniteService:
    global _service
    if _service is None:
        _service = GraniteService()
    return _service


def ask_circuit_advisor(question: str) -> dict:
    """
    Submit a free-text question to the Circuit Advisor.

    Returns the same dict structure as GraniteService.query():
        {
            "answer": str,
            "source": "ibm_granite" | "demo",
            "model": str | None,
            "is_demo": bool,
        }
    """
    service = _get_service()
    category = classify_query(question)
    context = f"CATEGORY:{category}\n{_CONTEXT_MAP.get(category, _CONTEXT_MAP['general'])}"
    return service.query(question, context=context)
