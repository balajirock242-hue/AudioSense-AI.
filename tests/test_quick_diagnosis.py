"""
Tests for app.quick_diagnosis.run_quick_diagnosis.

Covers:
  - Single specific symptoms (low gain, distortion, clipping, noise,
    50/60 Hz hum, oscillation, overheating, DC offset, no output)
  - Multi-symptom queries (low gain + distortion)
  - Noise / grounding / shielding problems
  - Filter problems
  - Generic / unrecognised input
  - Demo mode labelling (never claims to be IBM Granite)
  - Return dict shape
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.quick_diagnosis import run_quick_diagnosis


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _answer(problem: str) -> str:
    return run_quick_diagnosis(problem)["answer"]


def _symptoms(problem: str) -> list:
    return run_quick_diagnosis(problem)["symptoms"]


def _result(problem: str) -> dict:
    return run_quick_diagnosis(problem)


# ---------------------------------------------------------------------------
# Return-dict contract
# ---------------------------------------------------------------------------

class TestReturnShape:
    def test_keys_present(self):
        r = _result("my amplifier has low gain")
        assert set(r.keys()) >= {"answer", "symptoms", "category", "is_demo", "source", "model"}

    def test_is_demo_true(self):
        assert _result("my amplifier has low gain")["is_demo"] is True

    def test_source_is_demo(self):
        assert _result("my amplifier has low gain")["source"] == "demo"

    def test_model_is_none(self):
        assert _result("my amplifier has low gain")["model"] is None

    def test_never_claims_granite(self):
        """Answer must not claim to come from IBM Granite."""
        answer = _answer("my amplifier has low gain")
        assert "IBM Granite" not in answer or "Not IBM Granite" in answer


# ---------------------------------------------------------------------------
# Required test cases (from requirements)
# ---------------------------------------------------------------------------

class TestRequiredCases:
    def test_low_gain(self):
        """'My amplifier has low gain' must detect Low Gain and NOT be the generic table."""
        r = _result("My amplifier has low gain")
        assert "Low Gain" in r["symptoms"]
        # Should contain specific low-gain content, not just the generic table header
        assert "Rf" in r["answer"] or "feedback" in r["answer"].lower() or "gain" in r["answer"].lower()
        # Must NOT be the bare generic amplifier table (which has no detailed sections)
        assert "### ⚠️ Probable Causes" in r["answer"]

    def test_distortion(self):
        """'My amplifier has distortion' must detect Distortion."""
        r = _result("My amplifier has distortion")
        assert "Distortion" in r["symptoms"]
        assert "### ⚠️ Probable Causes" in r["answer"]
        assert "distort" in r["answer"].lower() or "clipping" in r["answer"].lower()

    def test_low_gain_and_distortion(self):
        """'My audio amplifier has low gain and noticeable distortion' must detect BOTH symptoms."""
        r = _result("My audio amplifier has low gain and noticeable distortion")
        assert "Low Gain" in r["symptoms"]
        assert "Distortion" in r["symptoms"]
        # Both sections present
        assert r["answer"].count("### ⚠️ Probable Causes") >= 2

    def test_50hz_hum(self):
        """'There is a 50 Hz hum' must detect the hum symptom."""
        r = _result("There is a 50 Hz hum")
        assert any("Hum" in s or "hum" in s.lower() for s in r["symptoms"])
        assert "ground" in r["answer"].lower() or "hum" in r["answer"].lower()


# ---------------------------------------------------------------------------
# Individual symptom detection
# ---------------------------------------------------------------------------

class TestSingleSymptoms:
    def test_no_output(self):
        r = _result("My amplifier has no output signal")
        assert "No Output" in r["symptoms"]
        assert "### ✅ Recommended Solutions" in r["answer"]

    def test_clipping(self):
        r = _result("The output is clipping badly")
        assert "Clipping" in r["symptoms"]
        assert "headroom" in r["answer"].lower() or "clip" in r["answer"].lower()

    def test_oscillation(self):
        r = _result("My op-amp circuit is oscillating at high frequency")
        assert "Oscillation" in r["symptoms"]
        assert "decoupling" in r["answer"].lower() or "phase margin" in r["answer"].lower()

    def test_overheating(self):
        r = _result("The amplifier chip is overheating")
        assert "Overheating" in r["symptoms"]
        assert "quiescent" in r["answer"].lower() or "heatsink" in r["answer"].lower()

    def test_dc_offset(self):
        r = _result("There is a DC offset at the output of my op-amp")
        assert "DC Offset" in r["symptoms"]
        assert "offset" in r["answer"].lower()

    def test_hiss(self):
        r = _result("I hear broadband hiss from my amplifier")
        assert len(r["symptoms"]) > 0
        assert "noise" in r["answer"].lower() or "hiss" in r["answer"].lower()

    def test_60hz_hum(self):
        r = _result("There is a 60 Hz hum in my audio system")
        assert any("Hum" in s or "hum" in s.lower() for s in r["symptoms"])

    def test_ground_loop(self):
        r = _result("I think I have a ground loop problem")
        assert any("Ground" in s for s in r["symptoms"])

    def test_power_supply_ripple(self):
        r = _result("My circuit has power supply ripple noise")
        assert any("Ripple" in s or "ripple" in s.lower() for s in r["symptoms"])

    def test_shielding_interference(self):
        r = _result("There is radio frequency interference in my circuit")
        assert any("Interference" in s or "RFI" in s for s in r["symptoms"])


# ---------------------------------------------------------------------------
# Multi-symptom queries
# ---------------------------------------------------------------------------

class TestMultiSymptom:
    def test_low_gain_and_distortion_sections(self):
        r = _result("My amplifier has low gain and also distortion")
        assert "Low Gain" in r["symptoms"]
        assert "Distortion" in r["symptoms"]

    def test_hum_and_noise(self):
        r = _result("I have a 60 Hz hum and broadband hiss")
        # At least two symptoms
        assert len(r["symptoms"]) >= 2

    def test_clipping_and_oscillation(self):
        r = _result("The output is clipping and I also see oscillation on the scope")
        assert "Clipping" in r["symptoms"]
        assert "Oscillation" in r["symptoms"]

    def test_three_symptoms(self):
        r = _result("My amplifier has low gain, distortion and the chip is overheating")
        assert "Low Gain" in r["symptoms"]
        assert "Distortion" in r["symptoms"]
        assert "Overheating" in r["symptoms"]
        # Three separate sections
        assert r["answer"].count("### ⚠️ Probable Causes") >= 3


# ---------------------------------------------------------------------------
# Structured content — not the generic table
# ---------------------------------------------------------------------------

class TestNotGenericTable:
    """Verify that specific queries do NOT return the catch-all generic table."""

    def test_low_gain_has_prob_causes_section(self):
        """Specific response must have Probable Causes section, not a flat table row."""
        answer = _answer("My amplifier has low gain")
        assert "### ⚠️ Probable Causes" in answer

    def test_distortion_has_solutions_section(self):
        answer = _answer("I hear distortion")
        assert "### ✅ Recommended Solutions" in answer

    def test_hum_not_generic_welcome(self):
        answer = _answer("There is a 50 Hz hum")
        assert "Welcome to" not in answer

    def test_low_gain_not_generic_table_only(self):
        """The generic _DEMO_AMP table has 'Wrong Rf/R1 ratio' as a table cell;
        the structured response has it in Probable Causes prose."""
        answer = _answer("My amplifier has low gain")
        # The structured response contains the actual diagnosis text
        assert "feedback resistor" in answer.lower() or "rf/r1" in answer.lower() or "Rf" in answer


# ---------------------------------------------------------------------------
# Demo mode labelling
# ---------------------------------------------------------------------------

class TestDemoLabelling:
    def test_demo_label_present(self):
        answer = _answer("My amplifier has low gain")
        assert "DEMO MODE" in answer

    def test_not_granite_label_present(self):
        answer = _answer("My amplifier has low gain")
        assert "Not IBM Granite" in answer

    def test_generic_demo_labelled(self):
        answer = _answer("What is the speed of light?")
        assert "DEMO MODE" in answer


# ---------------------------------------------------------------------------
# Filter and circuit queries fall back gracefully
# ---------------------------------------------------------------------------

class TestFallbacks:
    def test_filter_query(self):
        r = _result("I need to design a low-pass filter at 1 kHz")
        # Should not crash; should return something sensible
        assert len(r["answer"]) > 50
        assert r["is_demo"] is True

    def test_circuit_query(self):
        r = _result("Best practices for PCB grounding in audio circuits")
        assert len(r["answer"]) > 50
        assert r["is_demo"] is True

    def test_unrecognised_query(self):
        r = _result("What is the speed of light?")
        assert r["is_demo"] is True
        assert len(r["answer"]) > 50


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_string(self):
        r = _result("")
        assert r["is_demo"] is True
        assert isinstance(r["answer"], str)

    def test_whitespace_only(self):
        r = _result("   ")
        assert r["is_demo"] is True

    def test_case_insensitive_low_gain(self):
        r = _result("MY AMPLIFIER HAS LOW GAIN")
        assert "Low Gain" in r["symptoms"]

    def test_case_insensitive_hum(self):
        r = _result("THERE IS A 60 HZ HUM")
        assert any("Hum" in s or "hum" in s.lower() for s in r["symptoms"])

    def test_answer_is_string(self):
        assert isinstance(_answer("my amplifier clips"), str)

    def test_symptoms_is_list(self):
        assert isinstance(_symptoms("my amplifier clips"), list)
