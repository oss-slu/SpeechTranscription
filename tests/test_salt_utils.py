from components.salt_utils import format_correction_for_convention_box


def test_submit_preserves_salt_annotation():
    correction = "[00:01] He walk/*3s\n"

    formatted = format_correction_for_convention_box(correction)

    assert formatted == correction
    assert "/*3s" in formatted


def test_submit_normalizes_whitespace_without_changing_correction():
    correction = "\n[00:02] She walk/*3s   \n"

    assert format_correction_for_convention_box(correction) == "[00:02] She walk/*3s\n"
