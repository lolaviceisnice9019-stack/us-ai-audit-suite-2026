"""Tests for token parsing and WCAG contrast math.

Contrast reference values verified against the WCAG 2.x formula:
white (#ffffff) on black (#000000) = 21.0; identical colors = 1.0.
"""

import math

import pytest

from us_ai_audit_suite_2026.tokens import (
    classify_tokens,
    contrast_ratio,
    hex_to_rgb,
    parse_css_variables,
    relative_luminance,
    wcag_grade,
)


def test_parse_variables_basic():
    css = ":root { --color-bg: #0c0c0e; --radius-sm: 8px; --fg: #fff; }"
    tokens = parse_css_variables(css)
    assert tokens["color-bg"] == "#0c0c0e"
    assert tokens["radius-sm"] == "8px"
    assert tokens["fg"] == "#fff"


def test_parse_ignores_malformed():
    assert parse_css_variables("") == {}
    assert parse_css_variables("--no-semicolon: #fff") == {}
    assert parse_css_variables("color: red;") == {}


def test_hex_to_rgb_shorthand_and_long():
    assert hex_to_rgb("#ffffff") == (1.0, 1.0, 1.0)
    assert hex_to_rgb("#fff") == (1.0, 1.0, 1.0)
    assert hex_to_rgb("#000") == (0.0, 0.0, 0.0)
    # 8-digit hex: alpha ignored
    assert hex_to_rgb("#ff0000ff") == (1.0, 0.0, 0.0)


def test_hex_to_rgb_rejects_garbage():
    with pytest.raises(ValueError):
        hex_to_rgb("#12")
    with pytest.raises(ValueError):
        hex_to_rgb("red")


def test_relative_luminance_extremes():
    assert relative_luminance((0, 0, 0)) == 0.0
    assert math.isclose(relative_luminance((1, 1, 1)), 1.0, rel_tol=1e-6)


def test_contrast_known_values():
    # WCAG reference pairs
    assert math.isclose(contrast_ratio("#ffffff", "#000000"), 21.0, rel_tol=1e-6)
    assert math.isclose(contrast_ratio("#777777", "#777777"), 1.0, rel_tol=1e-9)
    # symmetry
    assert math.isclose(
        contrast_ratio("#9aa8b4", "#0c0c0e"),
        contrast_ratio("#0c0c0e", "#9aa8b4"),
        rel_tol=1e-9,
    )


def test_contrast_range_bounds():
    import random
    random.seed(42)
    for _ in range(200):
        a = "#%06x" % random.randrange(0x1000000)
        b = "#%06x" % random.randrange(0x1000000)
        r = contrast_ratio(a, b)
        assert 1.0 <= r <= 21.0 + 1e-9


def test_wcag_grade_thresholds():
    assert wcag_grade(7.0) == "AAA"
    assert wcag_grade(4.5) == "AA"
    assert wcag_grade(4.49) == "FAIL"
    assert wcag_grade(3.0, large_text=True) == "AA"
    assert wcag_grade(2.99, large_text=True) == "FAIL"


def test_classify_tokens_roles():
    tokens = {
        "color-bg": "#0c0c0e",
        "color-surface": "#161618",
        "color-fg": "#eeeee8",
        "color-muted": "#9aa8b4",
        "radius-sm": "8px",  # not a color: ignored
        "shadow-border": "0 0 0 1px rgba(255,255,255,0.08)",  # ignored
    }
    fg, bg = classify_tokens(tokens)
    assert set(bg) == {"color-bg", "color-surface"}
    assert set(fg) == {"color-fg", "color-muted"}
