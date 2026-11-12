"""Checks for the Saltify 2.0 design tokens (issue #361).

These keep the token model honest: both themes share one semantic model,
declared colour pairs meet WCAG contrast targets, and the generated CSS
matches the JSON source.
"""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import build_design_tokens as bdt  # noqa: E402  pylint: disable=wrong-import-position

TOKENS = bdt.load_tokens()
THEMES = TOKENS["themes"]
COLOR_VALUE = re.compile(r"^(#[0-9A-Fa-f]{6}|rgba\(\s*\d+,\s*\d+,\s*\d+,\s*(0|1|0?\.\d+)\s*\))$")


def test_light_and_dark_share_the_same_semantic_tokens():
    light, dark = set(THEMES["light"]), set(THEMES["dark"])
    assert light - dark == set(), f"missing from dark: {sorted(light - dark)}"
    assert dark - light == set(), f"missing from light: {sorted(dark - light)}"


def test_theme_tokens_do_not_collide_with_base_tokens():
    assert set(TOKENS["base"]).isdisjoint(THEMES["light"])


@pytest.mark.parametrize("theme", sorted(THEMES))
def test_colour_tokens_are_valid_values(theme):
    for key, value in THEMES[theme].items():
        if key.startswith("color-"):
            assert COLOR_VALUE.match(value), f"{theme}.{key} has invalid colour {value!r}"


def test_required_semantic_groups_exist():
    keys = THEMES["light"]
    required_prefixes = [
        "color-bg-", "color-text-", "color-border-", "color-accent-",
        "color-focus-ring", "color-disabled-", "color-status-", "color-error-",
        "color-speaker-", "color-waveform-",
    ]
    for prefix in required_prefixes:
        assert any(k.startswith(prefix) for k in keys), f"no tokens for {prefix}"


def test_every_status_and_speaker_has_matching_bg_and_fg():
    keys = THEMES["light"]
    for name in ("success", "info", "review", "warning", "danger", "neutral"):
        assert f"color-status-{name}-bg" in keys and f"color-status-{name}-fg" in keys
    for index in range(1, 7):
        for part in ("solid", "bg", "fg"):
            assert f"color-speaker-{index}-{part}" in keys


def test_contrast_pairs_reference_existing_tokens():
    for spec in TOKENS["contrastPairs"].values():
        for fg, bg in spec["pairs"]:
            assert fg in THEMES["light"] and bg in THEMES["light"], (fg, bg)


@pytest.mark.parametrize(
    "theme,kind,fg,bg,ratio,minimum",
    list(bdt.contrast_results(TOKENS)),
    ids=lambda v: v if isinstance(v, str) else None,
)
def test_contrast_meets_wcag(theme, kind, fg, bg, ratio, minimum):  # pylint: disable=unused-argument
    assert ratio >= minimum, f"{theme}: {fg} on {bg} is {ratio:.2f}:1, needs {minimum}:1"


def test_contrast_ratio_matches_known_values():
    assert bdt.contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0)
    assert bdt.contrast_ratio("#FFFFFF", "#FFFFFF") == pytest.approx(1.0)
    assert bdt.contrast_ratio("#767676", "#FFFFFF") == pytest.approx(4.54, abs=0.01)


def test_minimum_target_size_meets_wcag_2_2():
    assert int(TOKENS["base"]["target-min"].rstrip("px")) >= 24


def test_generated_css_is_up_to_date():
    expected = bdt.render_css(TOKENS)
    actual = bdt.TOKENS_CSS.read_text(encoding="utf-8")
    assert actual == expected, "Run: python scripts/build_design_tokens.py"
