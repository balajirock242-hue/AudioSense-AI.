"""
Tests for app.filter_calculator — RC cutoff frequency calculations
and unit conversions.
"""

import math
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.filter_calculator import (
    calculate_rc_cutoff,
    resistance_to_ohms,
    capacitance_to_farads,
    FilterResult,
)


# ---------------------------------------------------------------------------
# Unit conversion: resistance
# ---------------------------------------------------------------------------

class TestResistanceConversion:
    def test_ohms(self):
        assert resistance_to_ohms(100.0, "Ω") == pytest.approx(100.0)

    def test_kilohms(self):
        assert resistance_to_ohms(10.0, "kΩ") == pytest.approx(10_000.0)

    def test_megaohms(self):
        assert resistance_to_ohms(1.0, "MΩ") == pytest.approx(1_000_000.0)

    def test_ohm_alias(self):
        assert resistance_to_ohms(47.0, "ohm") == pytest.approx(47.0)

    def test_kohm_alias(self):
        assert resistance_to_ohms(4.7, "kohm") == pytest.approx(4_700.0)

    def test_mohm_alias(self):
        assert resistance_to_ohms(2.2, "mohm") == pytest.approx(2_200_000.0)

    def test_invalid_unit(self):
        with pytest.raises(ValueError, match="Unknown resistance unit"):
            resistance_to_ohms(10.0, "GΩ")


# ---------------------------------------------------------------------------
# Unit conversion: capacitance
# ---------------------------------------------------------------------------

class TestCapacitanceConversion:
    def test_picofarads(self):
        assert capacitance_to_farads(100.0, "pF") == pytest.approx(100e-12)

    def test_nanofarads(self):
        assert capacitance_to_farads(15.9, "nF") == pytest.approx(15.9e-9)

    def test_microfarads(self):
        assert capacitance_to_farads(1.0, "µF") == pytest.approx(1e-6)

    def test_uf_alias(self):
        assert capacitance_to_farads(10.0, "uF") == pytest.approx(10e-6)

    def test_invalid_unit(self):
        with pytest.raises(ValueError, match="Unknown capacitance unit"):
            capacitance_to_farads(1.0, "F")


# ---------------------------------------------------------------------------
# RC cutoff calculation: core accuracy
# ---------------------------------------------------------------------------

class TestRCCutoff:
    """
    Reference: fc = 1 / (2 * pi * R * C)
    Classic example: 10 kΩ + 15.9 nF ≈ 1 kHz
    """

    def test_classic_1khz(self):
        """10 kΩ + 15.9 nF ≈ 1 kHz (within 1%)."""
        result = calculate_rc_cutoff(10.0, "kΩ", 15.9, "nF")
        assert result.fc_hz == pytest.approx(1000.0, rel=0.01)

    def test_10khz(self):
        """10 kΩ + 1.59 nF ≈ 10 kHz."""
        result = calculate_rc_cutoff(10.0, "kΩ", 1.59, "nF")
        assert result.fc_hz == pytest.approx(10_000.0, rel=0.01)

    def test_100hz(self):
        """10 kΩ + 159 nF ≈ 100 Hz."""
        result = calculate_rc_cutoff(10.0, "kΩ", 159.0, "nF")
        assert result.fc_hz == pytest.approx(100.0, rel=0.01)

    def test_formula_manual(self):
        """Manual formula verification: R=1000 Ω, C=1µF → fc = 1/(2π·1000·1e-6) ≈ 159.15 Hz."""
        expected = 1.0 / (2 * math.pi * 1000 * 1e-6)
        result = calculate_rc_cutoff(1.0, "kΩ", 1.0, "µF")
        assert result.fc_hz == pytest.approx(expected, rel=1e-6)

    def test_megaohm_picofarad(self):
        """1 MΩ + 159 pF ≈ 1 kHz."""
        result = calculate_rc_cutoff(1.0, "MΩ", 159.0, "pF")
        assert result.fc_hz == pytest.approx(1000.0, rel=0.01)

    def test_filter_types_accepted(self):
        for ft in ("Low-Pass", "High-Pass", "Band-Pass", "Notch"):
            result = calculate_rc_cutoff(10.0, "kΩ", 15.9, "nF", filter_type=ft)
            assert result.filter_type == ft

    def test_zero_resistance_raises(self):
        with pytest.raises(ValueError, match="positive non-zero"):
            calculate_rc_cutoff(0.0, "kΩ", 15.9, "nF")

    def test_negative_capacitance_raises(self):
        with pytest.raises(ValueError, match="positive non-zero"):
            calculate_rc_cutoff(10.0, "kΩ", -1.0, "nF")

    def test_result_stores_si_values(self):
        result = calculate_rc_cutoff(10.0, "kΩ", 15.9, "nF")
        assert result.r_ohms == pytest.approx(10_000.0)
        assert result.c_farads == pytest.approx(15.9e-9)


# ---------------------------------------------------------------------------
# FilterResult display helpers
# ---------------------------------------------------------------------------

class TestFilterResultDisplay:
    def test_fc_display_hz(self):
        r = FilterResult(r_ohms=1000, c_farads=1e-6, fc_hz=159.15, filter_type="Low-Pass")
        assert "Hz" in r.fc_display
        assert "kHz" not in r.fc_display

    def test_fc_display_khz(self):
        r = FilterResult(r_ohms=10_000, c_farads=15.9e-9, fc_hz=1000.0, filter_type="Low-Pass")
        assert "kHz" in r.fc_display

    def test_fc_display_mhz(self):
        r = FilterResult(r_ohms=10, c_farads=1e-12, fc_hz=15_915_494.0, filter_type="Low-Pass")
        assert "MHz" in r.fc_display

    def test_r_display_kohms(self):
        r = FilterResult(r_ohms=10_000, c_farads=15.9e-9, fc_hz=1000.0, filter_type="Low-Pass")
        assert "kΩ" in r.r_display

    def test_c_display_nf(self):
        r = FilterResult(r_ohms=10_000, c_farads=15.9e-9, fc_hz=1000.0, filter_type="Low-Pass")
        assert "nF" in r.c_display

    def test_description_contains_formula(self):
        result = calculate_rc_cutoff(10.0, "kΩ", 15.9, "nF")
        desc = result.description()
        assert "fc = 1 / (2 × π × R × C)" in desc
