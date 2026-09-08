# Audio Engineering Knowledge Base
## AudioSense AI — IBM Granite Powered Reference

---

## 1. Audio Amplifiers

### 1.1 Classification
- **Class A**: Conducts for full 360° of input cycle. High linearity, very low distortion, inefficient (~25%). Used in high-fidelity preamplifier stages.
- **Class B**: Two transistors conduct 180° each. Efficient (~78%) but suffers from crossover distortion.
- **Class AB**: Compromise between A and B. Small quiescent current eliminates crossover distortion. Most common in audio power amplifiers.
- **Class D**: Switching amplifier using PWM. Very high efficiency (>90%). Requires low-pass output filter. Increasingly common in portable audio.

### 1.2 Key Parameters
- **Voltage Gain (Av)**: Ratio of output to input voltage. Non-inverting op-amp: Av = 1 + (Rf/R1).
- **Input Impedance**: High input impedance prevents loading the source. Typical preamplifier: 10 kΩ–1 MΩ.
- **Output Impedance**: Should be low (< 1 Ω for power amplifiers) to drive loads efficiently.
- **Bandwidth**: Frequency range over which gain is within 3 dB of midband. Gain-bandwidth product (GBW) is constant for op-amps.
- **Slew Rate**: Maximum rate of output voltage change (V/µs). Limits high-frequency, large-signal performance. Insufficient slew rate causes slew-rate distortion.
- **CMRR (Common-Mode Rejection Ratio)**: Ability to reject signals common to both inputs. High CMRR (> 80 dB) essential for differential amplifiers.
- **PSRR (Power Supply Rejection Ratio)**: Ability to reject power-supply noise. Poor PSRR causes hum and ripple in output.
- **THD (Total Harmonic Distortion)**: Sum of all harmonic distortion products. Quality audio amplifiers: THD < 0.01%.

---

## 2. Preamplifiers

### 2.1 Purpose
Preamplifiers boost weak signals (microphones, phono cartridges, instrument pickups) to line level before power amplification.

### 2.2 Microphone Preamplifier
- Input impedance: 1–2 kΩ (balanced XLR)
- Gain: 20–70 dB adjustable
- Noise Figure: < 1 dB (professional)
- Phantom Power: 48 V for condenser microphones

### 2.3 Phono Preamplifier (RIAA)
- Applies RIAA equalisation curve during playback
- Turnover frequencies: 50 Hz, 500 Hz, 2122 Hz
- MM (Moving Magnet): 47 kΩ input impedance, ~40 dB gain
- MC (Moving Coil): 100 Ω input impedance, ~60 dB gain

### 2.4 Instrument Preamplifier
- Guitar DI boxes: High-Z input (1 MΩ+)
- Buffer amplifiers with unity gain prevent cable capacitance from rolling off high frequencies

---

## 3. Operational Amplifiers (Op-Amps)

### 3.1 Ideal vs Real Op-Amp
| Parameter | Ideal | Typical Real (e.g., TL072) |
|---|---|---|
| Open-loop gain | Infinite | 100–120 dB |
| Input impedance | Infinite | 1 TΩ (FET input) |
| Output impedance | 0 Ω | 75 Ω |
| Bandwidth | Infinite | 3 MHz GBW |
| Offset voltage | 0 V | 3–15 mV |
| Slew rate | Infinite | 13 V/µs |

### 3.2 Common Configurations
- **Inverting Amplifier**: Av = -(Rf/Rin). Input impedance = Rin.
- **Non-Inverting Amplifier**: Av = 1 + (Rf/R1). High input impedance.
- **Voltage Follower (Buffer)**: Av = 1. Very high Zin, very low Zout.
- **Summing Amplifier**: Vout = -(Rf/R1·V1 + Rf/R2·V2 + ...). Used in audio mixers.
- **Difference Amplifier**: Vout = Rf/R1·(V2 − V1). Rejects common-mode noise.
- **Integrator**: Vout = -(1/RC)∫Vin dt. Used in active filters.
- **Differentiator**: Vout = -RC·dVin/dt. Amplifies high-frequency noise — use with care.

### 3.3 Popular Audio Op-Amp ICs
- **NE5532**: Low noise, high current output. Workhorse of audio design.
- **TL072/TL082**: JFET input, low bias current, moderate noise. Common in effects pedals.
- **OPA2134**: Ultra-low distortion (0.00008% THD). High-fidelity audio.
- **LM358**: Dual op-amp, single supply. Not ideal for audio — high noise and limited bandwidth.
- **AD797**: Extremely low noise (0.9 nV/√Hz). Microphone preamps, instrumentation.

### 3.4 Stability and Compensation
- Feedback can cause oscillation if phase shift reaches 180° at unity gain (Barkhausen criterion).
- Phase margin should be > 45° for stable operation (> 60° preferred).
- Adding a small capacitor (10–100 pF) across feedback resistor increases phase margin.
- Decoupling capacitors (100 nF ceramic + 10 µF electrolytic) on supply pins are mandatory.

---

## 4. Filters

### 4.1 First-Order RC Filters
**Cutoff Frequency:**
```
fc = 1 / (2 × π × R × C)
```
At fc, signal is attenuated by −3 dB (70.7% of passband value) and phase shifts by ±45°.

**Low-Pass Filter (RC):**
- Capacitor in shunt to ground, resistor in series
- Roll-off: −20 dB/decade (−6 dB/octave)
- Passes frequencies below fc

**High-Pass Filter (RC):**
- Capacitor in series, resistor in shunt to ground
- Roll-off: −20 dB/decade
- Passes frequencies above fc

### 4.2 Band-Pass and Notch Filters
**Band-Pass:**
- Combines high-pass and low-pass stages: f_low < f < f_high
- Q factor = fc / BW (higher Q = narrower band)
- Multiple feedback (MFB) topology for active band-pass

**Notch (Band-Reject):**
- Twin-T notch: deep null at fn. Sensitive to component matching.
- Wien bridge notch: tunable but requires matched components.
- Active notch: op-amp buffers the twin-T for sharper response.
- 50/60 Hz notch filters remove power-line hum from sensitive measurements.

### 4.3 Filter Order and Topology
- **Butterworth**: Maximally flat passband. −3 dB at fc. Good general-purpose.
- **Chebyshev**: Steeper roll-off, passband ripple. Better selectivity than Butterworth.
- **Bessel**: Linear phase (constant group delay). Best for transient response (square waves, audio).
- **Sallen-Key**: 2nd-order active filter, unity-gain or fixed-gain. Easy to implement with one op-amp.
- **Multiple Feedback (MFB)**: Inverting, good for band-pass. Better noise performance than Sallen-Key at high Q.

### 4.4 Component Selection
- Use 1% metal-film resistors for filter accuracy (carbon-film: ±5% tolerance causes fc errors).
- Use C0G/NP0 ceramic or film capacitors — avoid X7R/Y5V ceramics (capacitance varies with voltage).
- Match capacitor values within 1% for notch filters to achieve deep null (>40 dB).

---

## 5. Noise in Audio Circuits

### 5.1 Types of Noise
- **Thermal (Johnson) Noise**: Vn = √(4kTRB). Unavoidable, increases with resistance and bandwidth. Use minimum necessary bandwidth.
- **Shot Noise**: Due to discrete nature of charge carriers. Significant in diodes and BJT base current.
- **Flicker (1/f) Noise**: Dominant at low frequencies (< 1 kHz). JFET and MOSFET input op-amps have lower 1/f corner than BJT types for audio.
- **Excess Noise**: Present in carbon-composition resistors. Use metal-film resistors to minimise.

### 5.2 Noise Figure and SNR
- **SNR (Signal-to-Noise Ratio)**: 20·log10(Vsignal/Vnoise) dB. Professional audio: > 90 dB.
- **Noise Figure (NF)**: Degradation of SNR by a network. NF = 0 dB for ideal, want < 3 dB for preamp stages.
- **Noise Floor**: Lowest signal level a system can handle. Limited by thermal noise of source impedance.

### 5.3 Reducing Noise
- Use low-noise op-amps (NE5532, AD797) for first amplifier stage.
- Keep input-stage source impedance low — thermal noise ∝ √R.
- Minimise bandwidth to signal bandwidth only (use appropriate low-pass filter after amplification).
- Use balanced (differential) connections for long cable runs.
- Shield input wiring and keep away from power traces.

---

## 6. Hum and Power-Line Interference

### 6.1 50/60 Hz Hum
**Causes:**
- Ground loops between equipment with different earth potentials
- Capacitive/inductive coupling from power transformers or wiring
- Poor shielding on input cables
- Shared ground paths carrying supply return currents

**Diagnosis:**
- Disconnect all inputs — if hum disappears, source is external (ground loop or cable pick-up).
- Measure ground potential difference between chassis with DMM.
- Replace cables one at a time to locate ground loop.

**Solutions:**
- Use balanced (XLR) connections or DI boxes to break ground loops.
- Install an isolation transformer on suspect equipment.
- Use a star-ground topology — single common ground point.
- Route signal cables away from power cables (90° crossing if unavoidable).
- Use a 50/60 Hz notch filter as last resort (affects audio quality).

### 6.2 Power-Supply Ripple
**Causes:**
- Insufficient filter capacitance on rectifier output
- High ESR (Equivalent Series Resistance) in filter capacitors (aging electrolytic)
- Shared supply rails between power and signal sections
- Inadequate regulation

**Diagnosis:**
- Measure supply rail with oscilloscope — ripple > 10 mV p-p is problematic.
- Check capacitor ESR with ESR meter.
- Load-test the supply — ripple increases under load.

**Solutions:**
- Increase bulk filter capacitance (1000–10,000 µF typical for audio).
- Add local decoupling: 100 nF ceramic + 10 µF electrolytic at each IC supply pin.
- Use regulated supply (LM7812/LM7912 or LDO regulators).
- Separate power and signal ground planes, joining at single star point.
- Use a ripple-rejection stage (RC or LC low-pass on supply rail).

---

## 7. Grounding and Shielding

### 7.1 Ground Topologies
- **Star Ground**: All return currents converge to one point. Prevents ground current from one circuit causing voltage drop seen by another. Essential in audio.
- **Ground Plane**: Large copper area on PCB. Excellent for RF but can create ground loops at audio frequencies if multiple connections are made.
- **Chassis Ground vs Signal Ground**: Keep chassis/safety ground separate from signal ground; connect at one point only.

### 7.2 PCB Grounding Best Practices
- Place decoupling capacitors as close to supply pins as possible.
- Route high-current return currents (speaker, power) away from sensitive input traces.
- Use separate analog and digital ground planes joined at one point (mixed-signal designs).
- Avoid daisy-chaining ground connections through multiple ICs.

### 7.3 Shielding
- Coaxial cable: inner conductor (signal), outer shield (ground). Shield must be grounded at source end only for long runs (prevents ground loop).
- Balanced cable: two conductors (+ and −) twisted together, overall shield. Common-mode rejection rejects induced noise.
- Shielded enclosures: connect to chassis ground. Reduces capacitive coupling of high-frequency interference.
- Faraday shield: grounded conductor between primary and secondary of a transformer eliminates capacitive coupling.

---

## 8. Distortion

### 8.1 Harmonic Distortion
- **Even-order (2nd, 4th)**: Adds octave harmonics. Often perceived as "warm" — characteristic of tube amplifiers. Cancels in push-pull configurations.
- **Odd-order (3rd, 5th)**: Adds musically dissonant harmonics. Perceived as harsh. Dominant in clipped solid-state amplifiers.
- **THD measurement**: Inject a sine wave, measure harmonic content: THD = √(V2² + V3² + ...) / V1.

### 8.2 Intermodulation Distortion (IMD)
- Two tones (f1, f2) produce sum and difference frequencies: f1±f2, 2f1±f2, etc.
- IMD products within the audio band are particularly audible and objectionable.
- Caused by non-linearity; reduced by operating in the linear region with adequate headroom.

### 8.3 Clipping Distortion
- Occurs when output stage is driven beyond its supply rails.
- Hard clipping: abrupt flat tops — rich in odd harmonics, very harsh.
- Soft clipping: gradual saturation — more even harmonics, less harsh (tube character).
- Prevention: ensure adequate headroom (signal peaks 6–20 dB below clipping).
- Recovery: clipping in input/driver stages propagates. Check gain structure throughout signal chain.

### 8.4 Crossover Distortion
- Specific to Class B amplifiers — zero-crossing gap between NPN and PNP transistors.
- Eliminated by Class AB bias (small forward bias keeps transistors on the verge of conduction).
- Symptoms: audible at low signal levels, "grainy" texture.
- Fix: adjust quiescent current/bias trimmer until crossover distortion is minimised.

---

## 9. Feedback in Amplifiers

### 9.1 Negative Feedback Effects
- Reduces gain by factor (1 + Aβ)
- Reduces distortion by factor (1 + Aβ)
- Reduces output impedance by factor (1 + Aβ)
- Increases bandwidth by factor (1 + Aβ)
- Reduces noise contributed by amplifier stages within the feedback loop

### 9.2 Stability
- Too much feedback → phase shift → oscillation.
- Gain margin: dB below unity gain when phase shift = 180°. Should be > 6 dB.
- Phase margin: degrees away from 180° when gain = 0 dB. Should be > 45°.
- Dominant pole compensation: add capacitor to create early roll-off and ensure gain < 1 before phase shift reaches 180°.

### 9.3 Oscillation Troubleshooting
- Oscillation appears at frequencies from kHz to MHz (not 50/60 Hz — that is hum).
- Check for missing or dry decoupling capacitors on supply pins.
- Check for long lead lengths at op-amp inputs — act as antennas.
- Reduce feedback resistor values to lower source impedance seen by inverting input.
- Add small feedback capacitor (10–100 pF) across feedback resistor for stability.
- Check PCB layout — input and output traces must not run parallel.

---

## 10. Troubleshooting Audio Circuits — Systematic Approach

### 10.1 No Output
1. Verify power supply rails are present and within spec.
2. Check ground continuity.
3. Inject test signal at input; probe forward stage by stage until signal is lost.
4. Check for open feedback resistors (op-amp saturates to rail).
5. Verify op-amp is not in latch-up (output stuck at rail despite power cycling).

### 10.2 Low Gain
1. Check gain-setting resistors (Rf, R1) with DMM.
2. Verify input signal is reaching the amplifier input pin.
3. Check for leaky capacitors loading the signal.
4. Confirm feedback network is correct.
5. Check op-amp gain-bandwidth product — may be insufficient at operating frequency.

### 10.3 DC Offset at Output
1. Measure input offset voltage of op-amp — compare with datasheet maximum.
2. Check for DC path at input (blocked by coupling capacitor?).
3. Verify resistor balance: source impedance at + and − inputs should match for low-offset.
4. Replace op-amp if offset > datasheet specification.
5. Use offset null pins if provided (e.g., pin 1 and 5 on 741).

### 10.4 Overheating
1. Check quiescent current — excessive bias in Class AB causes heating.
2. Verify heatsink is adequate (calculate thermal resistance Rθ).
3. Check for oscillation — RF oscillation dissipates power invisibly.
4. Measure supply voltage — too-high supply increases quiescent dissipation.
5. Check for shorted output or too-low load impedance.

---

## 11. Component Ratings and Safety

> **⚠️ IMPORTANT DISCLAIMER**: All information in this knowledge base is for educational purposes. Always verify component ratings, supply voltages, load impedances, and thermal limits from manufacturer datasheets before constructing or modifying any circuit. Incorrect component ratings can result in component failure, damage to equipment, or safety hazards.

- **Voltage ratings**: Capacitors must be rated > 2× operating voltage for electrolytic types.
- **Power ratings**: Resistors in high-current paths must have adequate power rating (P = V²/R or I²R). Use 2× calculated power for derating.
- **Op-amp supply voltage**: Check maximum supply voltage in datasheet — exceeding it destroys the IC.
- **Output current**: Op-amp output current is limited (~20–40 mA typical). Use a buffer transistor or dedicated driver for loads below 150 Ω.
- **ESD**: Handle CMOS and JFET-input op-amps with ESD precautions — gate oxides can be damaged by static discharge.
