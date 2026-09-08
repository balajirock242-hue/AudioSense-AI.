"""
RC Filter cutoff frequency calculator with unit conversion.

Formula: fc = 1 / (2 * pi * R * C)

Supports:
  Resistance: Ω, kΩ, MΩ
  Capacitance: pF, nF, µF (also accepts uF)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Unit conversion helpers
# ---------------------------------------------------------------------------

RESISTANCE_UNITS: dict[str, float] = {
    "Ω": 1.0,
    "ohm": 1.0,
    "ohms": 1.0,
    "kΩ": 1_000.0,
    "kohm": 1_000.0,
    "kohms": 1_000.0,
    "kω": 1_000.0,
    "MΩ": 1_000_000.0,
    "mohm": 1_000_000.0,
    "mohms": 1_000_000.0,
    "mω": 1_000_000.0,
}

CAPACITANCE_UNITS: dict[str, float] = {
    "pF": 1e-12,
    "pf": 1e-12,
    "nF": 1e-9,
    "nf": 1e-9,
    "µF": 1e-6,
    "µf": 1e-6,
    "uF": 1e-6,
    "uf": 1e-6,
}


def resistance_to_ohms(value: float, unit: str) -> float:
    """Convert a resistance value from the given unit to Ohms."""
    multiplier = RESISTANCE_UNITS.get(unit)
    if multiplier is None:
        raise ValueError(
            f"Unknown resistance unit '{unit}'. "
            f"Valid units: {list(RESISTANCE_UNITS.keys())}"
        )
    return value * multiplier


def capacitance_to_farads(value: float, unit: str) -> float:
    """Convert a capacitance value from the given unit to Farads."""
    multiplier = CAPACITANCE_UNITS.get(unit)
    if multiplier is None:
        raise ValueError(
            f"Unknown capacitance unit '{unit}'. "
            f"Valid units: {list(CAPACITANCE_UNITS.keys())}"
        )
    return value * multiplier


# ---------------------------------------------------------------------------
# Calculator result
# ---------------------------------------------------------------------------

@dataclass
class FilterResult:
    r_ohms: float
    c_farads: float
    fc_hz: float
    filter_type: str

    @property
    def fc_display(self) -> str:
        """Human-readable cutoff frequency."""
        if self.fc_hz >= 1_000_000:
            return f"{self.fc_hz / 1_000_000:.3f} MHz"
        if self.fc_hz >= 1_000:
            return f"{self.fc_hz / 1_000:.3f} kHz"
        return f"{self.fc_hz:.2f} Hz"

    @property
    def r_display(self) -> str:
        if self.r_ohms >= 1_000_000:
            return f"{self.r_ohms / 1_000_000:.3f} MΩ"
        if self.r_ohms >= 1_000:
            return f"{self.r_ohms / 1_000:.3f} kΩ"
        return f"{self.r_ohms:.2f} Ω"

    @property
    def c_display(self) -> str:
        if self.c_farads >= 1e-6:
            return f"{self.c_farads * 1e6:.3f} µF"
        if self.c_farads >= 1e-9:
            return f"{self.c_farads * 1e9:.3f} nF"
        return f"{self.c_farads * 1e12:.3f} pF"

    def description(self) -> str:
        lines = [
            f"**Filter Type**: {self.filter_type}",
            f"**Resistance**: {self.r_display}",
            f"**Capacitance**: {self.c_display}",
            f"**Cutoff Frequency (fc)**: {self.fc_display}",
            "",
            "**Formula**: fc = 1 / (2 × π × R × C)",
            f"fc = 1 / (2 × π × {self.r_ohms:.4g} × {self.c_farads:.4g})",
            f"fc ≈ **{self.fc_display}**",
            "",
        ]
        lines += _filter_characteristics(self.filter_type, self.fc_hz)
        return "\n".join(lines)


def _filter_characteristics(filter_type: str, fc: float) -> list[str]:
    fc_str = FilterResult(1, 1e-9, fc, filter_type).fc_display  # reuse display
    if filter_type == "Low-Pass":
        return [
            f"**Behaviour**: Passes signals below {fc_str}, attenuates above.",
            "**Roll-off**: −20 dB/decade (−6 dB/octave) per order.",
            "**At fc**: Signal attenuated by −3 dB, phase shift −45°.",
            "**Application**: Anti-aliasing, audio tone control (bass), noise reduction.",
        ]
    if filter_type == "High-Pass":
        return [
            f"**Behaviour**: Passes signals above {fc_str}, attenuates below.",
            "**Roll-off**: −20 dB/decade per order.",
            "**At fc**: Signal attenuated by −3 dB, phase shift +45°.",
            "**Application**: DC blocking, rumble filter, audio tone control (treble).",
        ]
    if filter_type == "Band-Pass":
        return [
            f"**Behaviour**: Passes a band of frequencies centred near {fc_str}.",
            "**Note**: This fc is the geometric mean of the low and high cutoff frequencies.",
            "**Application**: Equalisation, specific frequency extraction.",
        ]
    if filter_type == "Notch":
        return [
            f"**Behaviour**: Deep attenuation (null) at {fc_str}, passes all other frequencies.",
            "**Application**: Remove 50/60 Hz mains hum, eliminate interference.",
            "**Note**: Requires precise component matching (≤1%) for deep null.",
        ]
    return []


# ---------------------------------------------------------------------------
# Main calculator function
# ---------------------------------------------------------------------------

def calculate_rc_cutoff(
    r_value: float,
    r_unit: str,
    c_value: float,
    c_unit: str,
    filter_type: str = "Low-Pass",
) -> FilterResult:
    """
    Calculate the RC cutoff frequency.

    Parameters
    ----------
    r_value : float   Resistance magnitude (positive).
    r_unit  : str     Unit string, e.g. "kΩ", "Ω", "MΩ".
    c_value : float   Capacitance magnitude (positive).
    c_unit  : str     Unit string, e.g. "nF", "pF", "µF".
    filter_type : str One of: Low-Pass, High-Pass, Band-Pass, Notch.

    Returns
    -------
    FilterResult with fc_hz, r_ohms, c_farads and display helpers.
    """
    if r_value <= 0:
        raise ValueError("Resistance must be a positive non-zero value.")
    if c_value <= 0:
        raise ValueError("Capacitance must be a positive non-zero value.")

    r_ohms = resistance_to_ohms(r_value, r_unit)
    c_farads = capacitance_to_farads(c_value, c_unit)
    fc = 1.0 / (2.0 * math.pi * r_ohms * c_farads)

    return FilterResult(
        r_ohms=r_ohms,
        c_farads=c_farads,
        fc_hz=fc,
        filter_type=filter_type,
    )


# ---------------------------------------------------------------------------
# Query classification helper (used by tests and circuit advisor)
# ---------------------------------------------------------------------------

_NOISE_KEYWORDS = {
    "hum", "buzz", "50hz", "60hz", "50 hz", "60 hz",
    "ground loop", "power supply", "ripple", "shielding", "interference",
    "mains", "hiss", "thermal noise", "flicker",
}
# High-priority filter keywords: beat noise (e.g. "notch filter at 60 Hz").
# Generic "filter" is intentionally excluded so that noise wins in queries
# like "use a filter to remove the hum" (see test_noise_over_filter).
_FILTER_KEYWORDS_HIGH = {
    "cutoff", "low-pass", "high-pass", "lowpass", "highpass",
    "bandpass", "band-pass", "notch", "rc filter",
}
# Mid-priority filter keywords: beat circuit but lose to amplifier keywords.
_FILTER_KEYWORDS_MID = {"frequency"}
# Low-priority filter keyword: wins only when no other category matches.
_FILTER_KEYWORDS_LOW = {"filter"}
_AMPLIFIER_KEYWORDS = {
    "amplif", "gain", "clip", "clipping", "distort", "oscillat",
    "overheating", "dc offset", "no output", "low gain", "op-amp",
    "opamp", "preamp",
}
_CIRCUIT_KEYWORDS = {
    "grounding", "feedback", "stability", "phase margin", "decoupling",
    "bypass capacitor", "layout", "pcb", "schematic", "circuit",
    "shield",
}


def classify_query(query: str) -> str:
    """
    Classify a user query into one of:
        noise | filter | amplifier | circuit | general

    Priority order:
        1. High-priority filter keywords (e.g. "notch", "low-pass") beat noise.
        2. Noise keywords beat low-priority filter / amplifier / circuit.
        3. Amplifier keywords beat low-priority filter keywords.
        4. Low-priority filter keyword ("frequency") beats circuit/general.
    """
    q = query.lower()
    if any(k in q for k in _FILTER_KEYWORDS_HIGH):
        return "filter"
    if any(k in q for k in _NOISE_KEYWORDS):
        return "noise"
    if any(k in q for k in _AMPLIFIER_KEYWORDS):
        return "amplifier"
    if any(k in q for k in _FILTER_KEYWORDS_MID):
        return "filter"
    if any(k in q for k in _CIRCUIT_KEYWORDS):
        return "circuit"
    if any(k in q for k in _FILTER_KEYWORDS_LOW):
        return "filter"
    return "general"
