"""
Noise troubleshooter — returns structured diagnostic information for
common audio noise problems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class NoiseDiagnosis:
    noise_type: str
    probable_causes: List[str]
    diagnostic_checks: List[str]
    recommended_solutions: List[str]


# ---------------------------------------------------------------------------
# Noise type data
# ---------------------------------------------------------------------------

_NOISE_DATA: dict[str, NoiseDiagnosis] = {
    "50/60 Hz Hum": NoiseDiagnosis(
        noise_type="50/60 Hz Hum",
        probable_causes=[
            "Ground loop — different earth potentials between interconnected equipment.",
            "Capacitive/inductive coupling from a nearby power transformer or mains wiring.",
            "Unbalanced cable picking up electromagnetic field from nearby AC wiring.",
            "Shared ground path carrying supply return current through signal ground.",
            "Missing or broken shield on input cable.",
        ],
        diagnostic_checks=[
            "Disconnect all input sources one at a time — note whether hum disappears.",
            "Measure AC voltage between chassis of each piece of equipment (should be < 5 mV).",
            "Lift signal ground at one end of each cable (use DI box or transformer) and check if hum stops.",
            "Move signal cables away from mains cables — if hum reduces, coupling is the culprit.",
            "Check cable shield continuity and grounding at both ends.",
        ],
        recommended_solutions=[
            "Use balanced (XLR) connections or a passive DI box to break ground loops.",
            "Power all equipment from the same mains outlet/strip (common earth point).",
            "Install a 1:1 audio isolation transformer on the suspect connection.",
            "Implement star-ground topology — all signal returns converge at one point.",
            "Route signal cables at 90° to mains cables; keep physical separation ≥ 15 cm.",
            "As a last resort, insert a 50/60 Hz notch filter (will slightly affect audio quality).",
        ],
    ),

    "Amplifier Noise (Hiss/Broadband)": NoiseDiagnosis(
        noise_type="Amplifier Noise (Hiss/Broadband)",
        probable_causes=[
            "High thermal (Johnson) noise from large source-impedance resistors.",
            "Excessive first-stage gain amplifying op-amp input noise.",
            "Use of a high-noise op-amp in the input stage (e.g., LM358 for audio).",
            "1/f (flicker) noise dominating at low frequencies — especially with BJT-input op-amps.",
            "Insufficient bandwidth limiting — noise outside the signal band is amplified.",
        ],
        diagnostic_checks=[
            "Replace op-amp with a low-noise type (NE5532, OPA2134) — compare noise floor.",
            "Reduce source impedance — noise voltage ∝ √R.",
            "Check resistor types: carbon-composition generates excess noise; use metal-film.",
            "Measure noise with an oscilloscope — check if it is wideband hiss or tonal.",
            "Temporarily short the input — if noise disappears, the source is external.",
        ],
        recommended_solutions=[
            "Use a low-noise op-amp for the first gain stage: NE5532, AD797, OPA2134.",
            "Minimise source impedance seen by first-stage input (< 1 kΩ target).",
            "Use metal-film 1% resistors throughout the signal path.",
            "Add a low-pass filter after the amplifier stage to limit noise bandwidth.",
            "Increase first-stage gain before additional noise sources are introduced.",
            "Use JFET-input op-amps (TL072, OPA2134) for high-impedance sources to reduce 1/f noise.",
        ],
    ),

    "Ground Loops": NoiseDiagnosis(
        noise_type="Ground Loops",
        probable_causes=[
            "Two or more pieces of equipment connected via both signal cables and separate mains earth paths.",
            "Multiple ground connections creating a loop that acts as a loop antenna.",
            "Mixing analog and digital ground planes with multiple connection points.",
            "Using unbalanced (RCA/TS jack) interconnects between equipment at different locations.",
        ],
        diagnostic_checks=[
            "Disconnect all equipment from mains one at a time while monitoring hum.",
            "Use a DMM to measure AC voltage between chassis of each pair of devices.",
            "Try lifting the cable shield at one end — hum stopping confirms a ground loop.",
            "Identify all ground paths (signal, chassis, mains earth) and map them on a diagram.",
        ],
        recommended_solutions=[
            "Convert to balanced (XLR/TRS) connections — CMRR rejects common-mode loop voltage.",
            "Use a passive isolation transformer or active DI box on each problem connection.",
            "Adopt strict star-ground topology: single ground convergence point.",
            "Connect all equipment chassis to a common mains earth; signal grounds converge separately.",
            "On PCBs: join analog and digital ground planes at exactly one point near the power input.",
        ],
    ),

    "Power-Supply Ripple": NoiseDiagnosis(
        noise_type="Power-Supply Ripple",
        probable_causes=[
            "Insufficient bulk filter capacitance on the rectifier output.",
            "High ESR (Equivalent Series Resistance) in aging electrolytic filter capacitors.",
            "Shared supply rail serving both high-current (output stage) and sensitive (input stage) circuitry.",
            "Unregulated supply — output voltage modulates with load current.",
            "Missing local decoupling capacitors at op-amp supply pins.",
        ],
        diagnostic_checks=[
            "Measure the supply rail with an oscilloscope — ripple > 10 mV p-p is problematic.",
            "Check electrolytic capacitor ESR with an ESR meter — replace if ESR is high.",
            "Load-test the supply: increase load current and observe ripple increase.",
            "Check if ripple frequency is 50/60 Hz (half-wave) or 100/120 Hz (full-wave rectifier).",
            "Temporarily substitute a bench supply — if hum disappears, PSU is the cause.",
        ],
        recommended_solutions=[
            "Increase bulk filter capacitance: 1000–10 000 µF for audio power supplies.",
            "Add local decoupling at each IC: 100 nF ceramic (close to pin) + 10 µF electrolytic.",
            "Use a voltage regulator (LM7812/LM7912 for ±12 V, or LDO for low-dropout).",
            "Separate high-current output stage supply from sensitive input stage supply.",
            "Add an RC pi-filter (resistor + capacitor) on the supply to sensitive input stages.",
            "Replace aging electrolytic capacitors — ESR increases significantly after 5–10 years.",
        ],
    ),

    "Shielding / Interference (RFI/EMI)": NoiseDiagnosis(
        noise_type="Shielding / Interference (RFI/EMI)",
        probable_causes=[
            "Unshielded input cables acting as antennas, picking up RF from mobile phones, Wi-Fi, etc.",
            "Long unbalanced cable runs adjacent to switching power supplies or digital circuits.",
            "Poor PCB layout with sensitive input traces running parallel to high-frequency switching nodes.",
            "Inadequate bypassing allowing RF into the op-amp supply pins (rectified to DC offset or audio-band noise).",
            "Open or vented metal enclosure providing insufficient shielding.",
        ],
        diagnostic_checks=[
            "Move cables and equipment away from suspected RF sources — if noise reduces, coupling confirmed.",
            "Wrap cable in aluminium foil temporarily — if noise reduces, shielding is the fix.",
            "Check for RF demodulation: short the input — if noise is still present, supply or PCB is the entry point.",
            "Probe supply pins with a high-bandwidth oscilloscope — look for HF spikes.",
        ],
        recommended_solutions=[
            "Use shielded coaxial or twisted-pair cables for all signal runs.",
            "Ground cable shields at the source end only to prevent ground loops via the shield.",
            "Add ferrite beads on supply and signal leads entering the PCB.",
            "Place 100 nF ceramic capacitors at every op-amp supply pin (C0G/NP0 type for HF performance).",
            "Enclose the circuit in a grounded metal (steel or aluminium) enclosure.",
            "Keep input traces short on PCB; use a ground guard-ring around sensitive nodes.",
            "Install RF bypass capacitors (10–100 pF) at input connector pins to chassis ground.",
        ],
    ),
}


def get_noise_diagnosis(noise_type: str) -> NoiseDiagnosis | None:
    """Return the NoiseDiagnosis for the given noise type, or None."""
    return _NOISE_DATA.get(noise_type)


def list_noise_types() -> list[str]:
    """Return all available noise type names."""
    return list(_NOISE_DATA.keys())


def format_diagnosis(diagnosis: NoiseDiagnosis) -> str:
    """Format a NoiseDiagnosis as a Markdown string."""
    lines = [f"## 🔊 {diagnosis.noise_type}", ""]

    lines.append("### ⚠️ Probable Causes")
    for i, cause in enumerate(diagnosis.probable_causes, 1):
        lines.append(f"{i}. {cause}")

    lines.append("")
    lines.append("### 🔍 Diagnostic Checks")
    for i, check in enumerate(diagnosis.diagnostic_checks, 1):
        lines.append(f"{i}. {check}")

    lines.append("")
    lines.append("### ✅ Recommended Solutions")
    for i, sol in enumerate(diagnosis.recommended_solutions, 1):
        lines.append(f"{i}. {sol}")

    lines.append("")
    lines.append(
        "> ⚠️ **Disclaimer**: Results are educational guidance. "
        "Verify circuit conditions and component ratings before making any hardware changes."
    )
    return "\n".join(lines)
