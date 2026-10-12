import os

import java_runtime


def test_configure_bundled_java_uses_unix_bin(tmp_path, monkeypatch):
    jre_bin = tmp_path / "jre" / "bin"
    jre_bin.mkdir(parents=True)
    java_path = jre_bin / "java"
    java_path.write_text("#!/bin/sh\n")
    java_path.chmod(0o755)

    monkeypatch.setattr(java_runtime, "get_base_path", lambda: str(tmp_path))
    monkeypatch.setattr(java_runtime.sys, "executable", str(tmp_path / "Saltify"))
    monkeypatch.delenv("JAVA_HOME", raising=False)

    found = java_runtime.configure_bundled_java()

    assert found == str(java_path)
    assert os.environ["JAVA_HOME"] == str(tmp_path / "jre")
    assert str(tmp_path / "jre" / "bin") in os.environ["PATH"]


def test_configure_bundled_java_uses_macos_contents_home(tmp_path, monkeypatch):
    home_bin = tmp_path / "jre" / "Contents" / "Home" / "bin"
    home_bin.mkdir(parents=True)
    java_path = home_bin / "java"
    java_path.write_text("#!/bin/sh\n")
    java_path.chmod(0o755)

    monkeypatch.setattr(java_runtime, "get_base_path", lambda: str(tmp_path))
    monkeypatch.setattr(java_runtime.sys, "executable", str(tmp_path / "Saltify"))
    monkeypatch.delenv("JAVA_HOME", raising=False)

    found = java_runtime.configure_bundled_java()

    assert found == str(java_path)
    assert os.environ["JAVA_HOME"] == str(tmp_path / "jre" / "Contents" / "Home")


def test_configure_bundled_java_uses_windows_exe(tmp_path, monkeypatch):
    jre_bin = tmp_path / "jre" / "bin"
    jre_bin.mkdir(parents=True)
    java_path = jre_bin / "java.exe"
    java_path.write_bytes(b"MZ")

    monkeypatch.setattr(java_runtime, "get_base_path", lambda: str(tmp_path))
    monkeypatch.setattr(java_runtime.sys, "executable", str(tmp_path / "Saltify.exe"))
    monkeypatch.delenv("JAVA_HOME", raising=False)

    found = java_runtime.configure_bundled_java()

    assert found == str(java_path)
    assert os.environ["JAVA_HOME"] == str(tmp_path / "jre")


def test_configure_bundled_java_missing_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(java_runtime, "get_base_path", lambda: str(tmp_path))
    monkeypatch.setattr(java_runtime.sys, "executable", str(tmp_path / "Saltify"))
    monkeypatch.delenv("JAVA_HOME", raising=False)

    assert java_runtime.configure_bundled_java() is None
