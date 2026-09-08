"""
Amplifier troubleshooter — structured symptom → diagnosis → solution data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class AmpDiagnosis:
    symptom: str
    probable_causes: List[str]
    diagnostic_checks: List[str]
    recommended_solutions: List[str]
    related_concepts: List[str]


_AMP_DATA: dict[str, AmpDiagnosis] = {
    "No Output": AmpDiagnosis(
        symptom="No Output",
        probable_causes=[
            "Power supply rails absent or incorrect polarity.",
            "Open-circuit feedback resistor — op-amp saturates to a supply rail.",
            "Input coupling capacitor open-circuit — DC path to input blocked.",
            "Op-amp in latch-up (output stuck at rail, unresponsive to input).",
            "Broken ground connection — signal reference is floating.",
            "Shorted output load pulling output to 0 V.",
        ],
        diagnostic_checks=[
            "Measure V+ and V− supply rails — confirm they are present and symmetrical.",
            "Inject a test signal (1 kHz sine) at the amplifier input with an oscilloscope probe.",
            "Stage-by-stage probing: trace signal forward until the stage that drops it.",
            "Measure DC output voltage — if stuck at ±Vcc, op-amp may be saturated.",
            "Check feedback resistor Rf continuity with DMM (power off).",
            "Verify ground continuity from circuit common to output reference.",
        ],
        recommended_solutions=[
            "Restore correct supply voltages within the op-amp's rated range.",
            "Replace open feedback resistor.",
            "Discharge and replace open coupling capacitor.",
            "Power-cycle to clear latch-up; add supply bypass capacitors to prevent recurrence.",
            "Re-establish ground connections; use star-ground topology.",
            "Verify load impedance ≥ op-amp minimum rated load (typically 600 Ω–2 kΩ).",
        ],
        related_concepts=["Power supply", "Feedback", "Coupling capacitors", "Op-amp latch-up"],
    ),

    "Low Gain": AmpDiagnosis(
        symptom="Low Gain",
        probable_causes=[
            "Incorrect or degraded feedback resistors (Rf or R1) — gain = 1 + Rf/R1.",
            "Signal source loading the input due to insufficient input impedance.",
            "Leaky bypass or coupling capacitor attenuating signal.",
            "Op-amp gain-bandwidth product (GBW) too low for operating frequency.",
            "Input signal already at low level before amplification.",
        ],
        diagnostic_checks=[
            "Measure Rf and R1 with DMM (power off) — compare to design values.",
            "Calculate expected gain: Av = 1 + Rf/R1 (non-inverting) or Av = Rf/Rin (inverting).",
            "Check source impedance — if it approaches R1, gain is reduced by the voltage divider.",
            "Measure signal amplitude directly at op-amp input and output pins.",
            "Verify operating frequency vs op-amp GBW (GBW = Av × BW).",
        ],
        recommended_solutions=[
            "Replace out-of-tolerance feedback resistors with 1% metal-film types.",
            "Ensure source impedance << R1 (source should be < 1/10 of R1).",
            "Replace leaky capacitors — measure leakage with DMM diode mode.",
            "Select an op-amp with higher GBW (e.g., upgrade from LM358 to NE5532).",
            "Increase Rf/R1 ratio to achieve target gain, keeping resistors within 1 kΩ–100 kΩ range.",
        ],
        related_concepts=["Gain-bandwidth product", "Input impedance", "Feedback resistors"],
    ),

    "Distortion": AmpDiagnosis(
        symptom="Distortion",
        probable_causes=[
            "Amplifier operating outside its linear region (approaching clipping).",
            "Incorrect DC bias / operating point — output not centred at 0 V.",
            "Crossover distortion in Class B stage (insufficient quiescent bias).",
            "Slew-rate limiting — output cannot keep up with fast input signal.",
            "Non-linear components (saturating inductors, overvoltage capacitors).",
            "Intermodulation from two or more large signals simultaneously.",
        ],
        diagnostic_checks=[
            "Scope the output with a sine-wave input — look for flat-top clipping or crossover glitches.",
            "Reduce input level — if distortion decreases, it is amplitude-driven clipping.",
            "Measure DC output offset — large offset reduces effective headroom.",
            "Check slew rate: max undistorted frequency = SR / (2π × Vpeak).",
            "Measure quiescent current in Class AB output stage.",
        ],
        recommended_solutions=[
            "Reduce input level or increase supply voltage to provide adequate headroom.",
            "Correct DC bias to centre output at mid-rail or 0 V.",
            "Adjust quiescent current bias pot in Class AB stage to eliminate crossover notch.",
            "Use an op-amp with higher slew rate for high-frequency or high-level signals.",
            "Apply negative feedback to linearise the response.",
        ],
        related_concepts=["THD", "Clipping", "Slew rate", "Crossover distortion", "Bias point"],
    ),

    "Clipping": AmpDiagnosis(
        symptom="Clipping",
        probable_causes=[
            "Input signal amplitude too large for the supply voltage headroom.",
            "Gain set too high — output hits supply rails before full input swing.",
            "Supply voltage too low for the required output level.",
            "DC offset shifting output towards one rail, reducing positive or negative headroom.",
        ],
        diagnostic_checks=[
            "Oscilloscope output: flat tops on positive and/or negative peaks = clipping.",
            "Calculate maximum undistorted output: Vout_max ≈ Vsupply − 1 to 2 V (rail-to-rail op-amps differ).",
            "Measure DC output offset — shifts clipping asymmetrically.",
            "Temporarily reduce input level — if clipping disappears, gain/level is the issue.",
        ],
        recommended_solutions=[
            "Reduce input signal level (add attenuator or adjust source level).",
            "Reduce gain (increase R1 or decrease Rf).",
            "Increase supply voltage to provide more headroom (within op-amp limits).",
            "Correct DC offset (balanced input resistors, offset null pin).",
            "Add a soft-clip limiter circuit to prevent hard clipping.",
        ],
        related_concepts=["Headroom", "Supply voltage", "THD", "Gain"],
    ),

    "Oscillation": AmpDiagnosis(
        symptom="Oscillation",
        probable_causes=[
            "Missing or open decoupling capacitors on op-amp supply pins.",
            "Insufficient phase margin — feedback network causes 180° phase shift at a frequency where gain > 1.",
            "Long PCB traces at inverting input acting as antenna and providing positive feedback.",
            "Capacitive load on output causing additional phase shift and instability.",
            "Feedback resistor values too high — stray capacitance creates a feedback pole.",
        ],
        diagnostic_checks=[
            "Scope the output with no input — sustained oscillation is visible as continuous sine or square wave.",
            "Check frequency: audio-range (< 20 kHz) or RF (> 100 kHz). RF oscillation is nearly silent but wastes power and causes distortion.",
            "Check supply pins with oscilloscope — HF oscillation appears on supply rails.",
            "Temporarily increase supply bypass capacitance — if oscillation stops, decoupling is the fix.",
            "Check phase margin in simulation or by sweeping gain vs frequency.",
        ],
        recommended_solutions=[
            "Add 100 nF ceramic capacitor (as close as possible) to each op-amp supply pin.",
            "Add 10–100 pF capacitor across the feedback resistor Rf to increase phase margin.",
            "Reduce feedback resistor values to lower impedance seen at inverting input.",
            "Add a small series resistor (10–50 Ω) at the output to isolate capacitive loads.",
            "Shorten PCB traces at inputs; keep input and output traces separated.",
            "Select an op-amp with built-in compensation (unity-gain stable types).",
        ],
        related_concepts=["Phase margin", "Gain margin", "Barkhausen criterion", "Decoupling"],
    ),

    "Overheating": AmpDiagnosis(
        symptom="Overheating",
        probable_causes=[
            "Excessive quiescent current — bias set too high in Class AB output stage.",
            "RF/HF oscillation — continuous switching dissipates power invisibly.",
            "Supply voltage too high — increases quiescent dissipation: P = Vcc²/RL or quiescent.",
            "Insufficient or absent heatsink — thermal resistance too high.",
            "Short circuit or very low load impedance drawing excessive current.",
        ],
        diagnostic_checks=[
            "Measure quiescent current with no signal — compare to datasheet specification.",
            "Probe supply rails with oscilloscope at high bandwidth — check for HF oscillation.",
            "Measure supply voltage — ensure it does not exceed the op-amp or transistor rating.",
            "Calculate thermal dissipation: P = (Vcc − Vout) × Iout (for each output transistor).",
            "Measure load impedance — ensure it is within the rated range.",
        ],
        recommended_solutions=[
            "Adjust bias trimmer to reduce quiescent current to the datasheet value.",
            "Resolve any oscillation (add decoupling, reduce feedback impedance).",
            "Reduce supply voltage to the minimum needed for the required output swing.",
            "Attach an adequate heatsink: calculate Rθjc + Rθcs + Rθsa for target junction temperature.",
            "Add current-limiting protection (fuse, thermistor, or electronic protection circuit).",
            "Ensure load impedance ≥ minimum specified for the output stage.",
        ],
        related_concepts=["Thermal resistance", "Quiescent current", "Heatsink", "Power dissipation"],
    ),

    "DC Offset": AmpDiagnosis(
        symptom="DC Offset at Output",
        probable_causes=[
            "Op-amp input offset voltage (Vos) — even a few mV amplified by closed-loop gain.",
            "Unequal source impedances at + and − inputs — bias current creates offset.",
            "Leaky coupling capacitor passing DC from a previous stage.",
            "No output coupling capacitor — any input DC is amplified and appears at output.",
            "Damaged op-amp with excessive offset beyond the datasheet specification.",
        ],
        diagnostic_checks=[
            "Measure output DC voltage with input shorted — any non-zero voltage is DC offset.",
            "Check op-amp datasheet: maximum Vos × closed-loop gain = maximum output offset.",
            "Measure DC at the non-inverting (+) input — any voltage here is amplified.",
            "Check resistor balance: R_source at + should equal the parallel combination of Rf ∥ Rin at − for lowest offset.",
        ],
        recommended_solutions=[
            "Balance source impedances at + and − inputs: add matching resistor at + input = Rf ∥ Rin.",
            "Use offset null pins (if available on op-amp package) to trim Vos to zero.",
            "Use an op-amp with lower specified Vos (e.g., OPA2134 has 0.5 mV max vs LM741 6 mV).",
            "Add an output coupling capacitor to block DC from reaching the load (AC-coupled output).",
            "Replace leaky coupling capacitors.",
        ],
        related_concepts=["Input offset voltage", "Bias current", "Coupling capacitors"],
    ),

    "Noise": AmpDiagnosis(
        symptom="Amplifier Noise",
        probable_causes=[
            "High input-stage op-amp noise (voltage noise density, en).",
            "Large source impedance amplifying thermal noise floor.",
            "Insufficient power supply filtering entering via supply pins.",
            "Stray pickup on long unshielded input traces.",
            "Excess noise from carbon-composition resistors.",
        ],
        diagnostic_checks=[
            "Short the input: if noise floor drops significantly, the noise is from the source/cable.",
            "Replace op-amp with a lower-noise type and compare noise floor.",
            "Probe supply pins with oscilloscope — ripple and HF noise appear here.",
            "Check resistor types: carbon = noisier; metal-film = quieter.",
        ],
        recommended_solutions=[
            "Use a low-noise op-amp: NE5532 (5 nV/√Hz), AD797 (0.9 nV/√Hz) for the input stage.",
            "Minimise source impedance and keep input traces short and shielded.",
            "Add local supply decoupling: 100 nF ceramic + 10 µF electrolytic at each supply pin.",
            "Use metal-film 1% resistors in the signal path.",
            "Apply appropriate bandwidth limiting (low-pass filter) to restrict noise to the signal band.",
        ],
        related_concepts=["Noise figure", "SNR", "Thermal noise", "Op-amp noise specs"],
    ),
}


def get_amp_diagnosis(symptom: str) -> AmpDiagnosis | None:
    """Return the AmpDiagnosis for the given symptom, or None."""
    return _AMP_DATA.get(symptom)


def list_symptoms() -> list[str]:
    """Return all available symptom names."""
    return list(_AMP_DATA.keys())


def format_amp_diagnosis(diagnosis: AmpDiagnosis) -> str:
    """Format an AmpDiagnosis as a Markdown string."""
    lines = [f"## ⚡ {diagnosis.symptom}", ""]

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

    if diagnosis.related_concepts:
        lines.append("")
        lines.append("### 📚 Related Concepts")
        lines.append(", ".join(diagnosis.related_concepts))

    lines.append("")
    lines.append(
        "> ⚠️ **Disclaimer**: Results are educational guidance. "
        "Verify circuit conditions and component ratings before making any hardware changes."
    )
    return "\n".join(lines)
