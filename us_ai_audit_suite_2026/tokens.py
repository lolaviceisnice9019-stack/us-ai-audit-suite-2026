"""CSS design-token parsing and WCAG 2.x contrast mathematics.

Pure functions, no I/O. Contrast math follows WCAG 2.x relative luminance:
https://www.w3.org/TR/WCAG22/#dfn-relative-luminance
"""

from __future__ import annotations

import re

_VAR_RE = re.compile(r"--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);")
_HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")

# Tokens whose role is "paint text/icon in this color" vs "paint a surface".
_FOREGROUND_HINTS = (
    "fg", "foreground", "text", "color-primary", "muted", "subtle",
    "danger", "ok", "accent", "route", "ring",
)
_BACKGROUND_HINTS = (
    "bg", "background", "surface", "map", "elevated",
)


def parse_css_variables(css_text: str) -> dict[str, str]:
    """Extract `--name: value;` custom properties. Values are stripped."""
    return {m.group(1): m.group(2).strip() for m in _VAR_RE.finditer(css_text)}


def is_hex_color(value: str) -> bool:
    return bool(_HEX_RE.match(value.strip()))


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    """#rgb / #rrggbb / #rrggbbaa -> (r, g, b) in 0..1. Alpha is ignored
    (composited color must be supplied by the caller if needed)."""
    h = value.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) == 8:
        h = h[:6]
    if len(h) != 6:
        raise ValueError(f"not a 6-digit hex color: {value!r}")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)


def _channel_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = rgb
    return (
        0.2126 * _channel_linear(r)
        + 0.7152 * _channel_linear(g)
        + 0.0722 * _channel_linear(b)
    )


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """WCAG contrast ratio between two hex colors, in [1.0, 21.0]."""
    l1 = relative_luminance(hex_to_rgb(fg_hex))
    l2 = relative_luminance(hex_to_rgb(bg_hex))
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def classify_tokens(
    variables: dict[str, str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Split hex-valued tokens into (foregrounds, backgrounds) by name hints.

    Tokens matching neither hint are ignored (reported as skipped upstream).
    A token may appear in both maps only if its name contains hints of both,
    which in practice does not happen with the hint lists above because
    background hints are checked first for exact role prefixes.
    """
    foregrounds: dict[str, str] = {}
    backgrounds: dict[str, str] = {}
    for name, value in variables.items():
        if not is_hex_color(value):
            continue
        lname = name.lower()
        if any(h in lname for h in _BACKGROUND_HINTS):
            backgrounds[name] = value
        elif any(h in lname for h in _FOREGROUND_HINTS):
            foregrounds[name] = value
    return foregrounds, backgrounds


def wcag_grade(ratio: float, *, large_text: bool = False) -> str:
    """Return the highest WCAG level the ratio satisfies for text."""
    aa = 3.0 if large_text else 4.5
    aaa = 4.5 if large_text else 7.0
    if ratio >= aaa:
        return "AAA"
    if ratio >= aa:
        return "AA"
    return "FAIL"
