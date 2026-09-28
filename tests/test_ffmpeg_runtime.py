import os
import stat

import ffmpeg_runtime


def test_configure_bundled_ffmpeg_prepends_path_and_sets_exec_bit(tmp_path, monkeypatch):
    bin_dir = tmp_path / "ffmpeg_bin"
    bin_dir.mkdir()
    for name in ("ffmpeg", "ffprobe"):
        tool = bin_dir / name
        tool.write_text("#!/bin/sh\n")
        tool.chmod(0o644)

    monkeypatch.setattr(ffmpeg_runtime, "get_base_path", lambda: str(tmp_path))
    monkeypatch.setenv("PATH", "/usr/bin")

    found = ffmpeg_runtime.configure_bundled_ffmpeg()

    assert found == str(bin_dir / "ffmpeg")
    assert os.environ["PATH"].split(os.pathsep)[0] == str(bin_dir)
    for name in ("ffmpeg", "ffprobe"):
        assert os.stat(bin_dir / name).st_mode & stat.S_IXUSR


def test_configure_bundled_ffmpeg_missing_leaves_path(tmp_path, monkeypatch):
    monkeypatch.setattr(ffmpeg_runtime, "get_base_path", lambda: str(tmp_path))
    monkeypatch.setenv("PATH", "/usr/bin")

    assert ffmpeg_runtime.configure_bundled_ffmpeg() is None
    assert os.environ["PATH"] == "/usr/bin"
