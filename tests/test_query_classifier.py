"""
Tests for query classification (app.filter_calculator.classify_query).
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.filter_calculator import classify_query


class TestClassifyQuery:
    """Verify that common query strings are classified into the correct category."""

    # ---- noise ----

    def test_hum(self):
        assert classify_query("my amplifier has a 60 Hz hum") == "noise"

    def test_50hz(self):
        assert classify_query("How do I remove 50 Hz hum from my preamp?") == "noise"

    def test_ground_loop(self):
        assert classify_query("I suspect a ground loop between my devices") == "noise"

    def test_power_supply_ripple(self):
        assert classify_query("There is power supply ripple on my output") == "noise"

    def test_shielding(self):
        assert classify_query("How does shielding help with interference?") == "noise"

    def test_mains_interference(self):
        assert classify_query("mains interference is audible in my circuit") == "noise"

    # ---- filter ----

    def test_filter_keyword(self):
        assert classify_query("I need to design a low-pass filter") == "filter"

    def test_cutoff(self):
        assert classify_query("What is the cutoff frequency for 10k and 15nF?") == "filter"

    def test_notch_filter(self):
        assert classify_query("Design a notch filter at 60 Hz") == "filter"

    def test_bandpass(self):
        assert classify_query("Explain how a bandpass filter works") == "filter"

    def test_highpass(self):
        assert classify_query("I need a highpass filter for my circuit") == "filter"

    def test_frequency(self):
        assert classify_query("What frequency does my RC circuit pass?") == "filter"

    # ---- amplifier ----

    def test_no_output(self):
        assert classify_query("My amplifier has no output signal") == "amplifier"

    def test_clipping(self):
        assert classify_query("The output is clipping on loud notes") == "amplifier"

    def test_distortion(self):
        assert classify_query("I hear distortion in my audio amplifier") == "amplifier"

    def test_oscillation(self):
        assert classify_query("My op-amp is oscillating at high frequency") == "amplifier"

    def test_low_gain(self):
        assert classify_query("The gain is lower than expected") == "amplifier"

    def test_preamp(self):
        assert classify_query("Troubleshoot my preamp circuit") == "amplifier"

    # ---- circuit ----

    def test_grounding(self):
        assert classify_query("Best practices for grounding in audio circuits") == "circuit"

    def test_feedback(self):
        assert classify_query("How does negative feedback affect stability?") == "circuit"

    def test_stability(self):
        assert classify_query("How do I check the phase margin for stability?") == "circuit"

    def test_decoupling(self):
        assert classify_query("Where should I place decoupling capacitors?") == "circuit"

    def test_pcb(self):
        assert classify_query("PCB layout tips for low-noise design") == "circuit"

    # ---- general ----

    def test_general(self):
        assert classify_query("Tell me about audio engineering") == "general"

    def test_empty(self):
        assert classify_query("") == "general"

    def test_unrelated(self):
        assert classify_query("What is the speed of light?") == "general"

    # ---- priority: noise takes precedence over filter ----

    def test_noise_over_filter(self):
        """'hum' should classify as noise even if 'filter' is also present."""
        assert classify_query("Should I use a filter to remove the hum?") == "noise"


class TestClassifyQueryCaseInsensitive:
    """Classification should work regardless of case."""

    def test_uppercase_hum(self):
        assert classify_query("THERE IS A HUM IN MY AUDIO") == "noise"

    def test_mixed_case_filter(self):
        assert classify_query("I need a Low-Pass Filter") == "filter"

    def test_uppercase_amplifier(self):
        assert classify_query("AMPLIFIER GAIN IS TOO LOW") == "amplifier"
