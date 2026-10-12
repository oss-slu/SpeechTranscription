import selftest


def _ok():
    return "fine"


def _skip():
    raise selftest.Skip("not applicable")


def _boom():
    raise RuntimeError("bundled thing missing")


def test_all_pass_writes_report_and_returns_zero(tmp_path, monkeypatch):
    report = tmp_path / "report.txt"
    monkeypatch.setenv(selftest.REPORT_ENV_VAR, str(report))

    assert selftest.run_selftest([("a", _ok), ("b", _skip)]) == 0

    text = report.read_text()
    assert "PASS a: fine" in text
    assert "SKIP b: not applicable" in text
    assert "RESULT: PASS (1 passed, 0 failed, 1 skipped)" in text


def test_failure_is_reported_and_returns_one(tmp_path, monkeypatch):
    report = tmp_path / "report.txt"
    monkeypatch.setenv(selftest.REPORT_ENV_VAR, str(report))

    assert selftest.run_selftest([("a", _ok), ("b", _boom)]) == 1

    text = report.read_text()
    assert "FAIL b:" in text
    assert "RuntimeError: bundled thing missing" in text
    assert "RESULT: FAIL (1 passed, 1 failed, 0 skipped)" in text
