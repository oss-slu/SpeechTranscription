"""Self-test for the packaged app, run by CI with HEADLESS=true.

Checks that everything the frozen app bundles is present and usable, writes a
PASS/FAIL/SKIP report to $SALTIFY_SELFTEST_REPORT (stdout is unavailable in the
windowed Windows build), and returns a process exit code.
"""

import os
import platform
import subprocess
import sys
import traceback

REPORT_ENV_VAR = "SALTIFY_SELFTEST_REPORT"


class Skip(Exception):
    pass


def _frozen():
    return getattr(sys, "frozen", False)


def _inside_bundle(path):
    from java_runtime import get_base_path

    return os.path.abspath(path).startswith(os.path.abspath(get_base_path()) + os.sep)


def _run_version(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"{cmd[0]} {cmd[1]} exited with {result.returncode}: {result.stderr.strip()}")
    return (result.stdout or result.stderr).strip().splitlines()[0]


def check_bundled_java():
    from java_runtime import configure_bundled_java

    java = configure_bundled_java()
    if java is None:
        if not _frozen():
            raise Skip("running from source; Java is only bundled in the packaged app")
        raise RuntimeError("bundled Java not found")
    if _frozen() and not _inside_bundle(java):
        raise RuntimeError(f"Java found outside the bundle: {java}")
    return f"{java} ({_run_version([java, '-version'])})"


def check_bundled_ffmpeg():
    # Must run before anything imports pydub, which resolves ffmpeg at import time.
    if platform.system() != "Darwin":
        raise Skip("ffmpeg is only bundled in the macOS build")
    from ffmpeg_runtime import configure_bundled_ffmpeg

    ffmpeg = configure_bundled_ffmpeg()
    if ffmpeg is None:
        if not _frozen():
            raise Skip("running from source; ffmpeg is only bundled in the packaged app")
        raise RuntimeError("bundled ffmpeg not found")
    return f"{ffmpeg} ({_run_version([ffmpeg, '-version'])})"


def check_nltk_data():
    import nltk_resources
    from java_runtime import get_base_path

    bundled = os.path.join(get_base_path(), "nltk_data")
    if _frozen():
        if not os.path.isdir(bundled):
            raise RuntimeError(f"bundled nltk_data folder missing: {bundled}")
        nltk_resources.verify(bundled)
        return f"verified {bundled}"
    nltk_resources.verify()
    return "verified (running from source, using the machine's NLTK data)"


def check_app_imports():
    # Imports the same chain the GUI does: grammar/LanguageTool, Whisper, pyannote, torch.
    import components.audio_menu  # noqa: F401
    import whisper  # noqa: F401

    return "components.audio_menu, whisper"


CHECKS = [
    ("bundled_java", check_bundled_java),
    ("bundled_ffmpeg", check_bundled_ffmpeg),
    ("nltk_data", check_nltk_data),
    ("app_imports", check_app_imports),
]


def run_selftest(checks=None):
    """Run the checks, write the report, and return 0 if none failed."""
    checks = CHECKS if checks is None else checks
    lines = [f"Saltify self-test (frozen={_frozen()}, platform={platform.system()})"]
    failed = skipped = 0
    for name, check in checks:
        try:
            lines.append(f"PASS {name}: {check()}")
        except Skip as exc:
            skipped += 1
            lines.append(f"SKIP {name}: {exc}")
        except Exception:  # noqa: BLE001 - every failure belongs in the report
            failed += 1
            lines.append(f"FAIL {name}:\n{traceback.format_exc().rstrip()}")
    passed = len(checks) - failed - skipped
    lines.append(f"RESULT: {'FAIL' if failed else 'PASS'} ({passed} passed, {failed} failed, {skipped} skipped)")

    report = "\n".join(lines) + "\n"
    report_path = os.environ.get(REPORT_ENV_VAR)
    if report_path:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
    if sys.stdout is not None:
        print(report, end="")
    return 1 if failed else 0
