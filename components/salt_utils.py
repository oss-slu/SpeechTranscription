"""Helpers for preserving SALT annotations while applying grammar corrections."""


def format_correction_for_convention_box(corrected_sentence: str) -> str:
    """Normalize a timestamped correction without removing SALT annotations."""
    sentence = corrected_sentence.strip()
    timestart = sentence.index("[")
    timeend = sentence.index("]", timestart)
    timestamp = sentence[timestart : timeend + 1]
    sentence_body = sentence[timeend + 1 :].strip()
    return f"{timestamp} {sentence_body}\n"
