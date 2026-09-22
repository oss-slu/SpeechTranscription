"""Regression tests for AudioManager WAV normalization lifecycle (issue #77)."""

import os
import struct
import wave
from unittest.mock import Mock

import pytest
from pydub import AudioSegment

import audio as audio_module
from audio import AudioManager


def _write_sine_wav(path, seconds=0.25, rate=16000, amp=8000):
    nframes = int(rate * seconds)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        frames = b"".join(
            struct.pack("<h", int(amp * ((i % 40) / 20 - 1))) for i in range(nframes)
        )
        wf.writeframes(frames)


@pytest.fixture
def audio_manager(monkeypatch, tmp_path):
    """AudioManager with PyAudio mocked so tests do not need a real device."""
    mock_pa = Mock()
    mock_pa.get_sample_size.return_value = 2
    monkeypatch.setattr(audio_module.pyaudio, "PyAudio", lambda: mock_pa)
    manager = AudioManager(root=Mock())
    manager.filePath = str(tmp_path / "session.wav")
    yield manager
    if manager.wf:
        manager.wf.close()
        manager.wf = None


def test_normalize_wav_without_exception(audio_manager, tmp_path):
    path = str(tmp_path / "session.wav")
    _write_sine_wav(path)
    audio_manager.filePath = path
    audio_manager.wf = wave.open(path, "rb")

    result = audio_manager.normalizeUploadedFile()

    assert result == path
    assert os.path.exists(path)


def test_normalized_wav_is_valid(audio_manager, tmp_path):
    path = str(tmp_path / "session.wav")
    _write_sine_wav(path)
    audio_manager.filePath = path
    audio_manager.wf = wave.open(path, "rb")

    audio_manager.normalizeUploadedFile()

    with wave.open(path, "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 16000
        assert wf.getnframes() > 0


def test_playback_handle_reopened_after_normalize(audio_manager, tmp_path):
    path = str(tmp_path / "session.wav")
    _write_sine_wav(path)
    audio_manager.filePath = path
    audio_manager.wf = wave.open(path, "rb")

    audio_manager.normalizeUploadedFile()

    assert audio_manager.wf is not None
    assert audio_manager.wf.getnframes() > 0
    assert audio_manager.wf.getframerate() == 16000


def test_normalize_closes_prior_handle_before_replace(audio_manager, tmp_path):
    path = str(tmp_path / "session.wav")
    _write_sine_wav(path)
    audio_manager.filePath = path
    old_wf = wave.open(path, "rb")
    audio_manager.wf = old_wf

    audio_manager.normalizeUploadedFile()

    # Old handle must not remain the active reader after replacement.
    assert audio_manager.wf is not old_wf
    with pytest.raises(Exception):
        old_wf.readframes(1)


def test_mp3_conversion_then_normalize(audio_manager, tmp_path):
    wav_src = str(tmp_path / "src.wav")
    mp3_path = str(tmp_path / "src.mp3")
    export_wav = str(tmp_path / "export.wav")
    _write_sine_wav(wav_src)
    AudioSegment.from_wav(wav_src).export(mp3_path, format="mp3")

    segment = AudioSegment.from_file(mp3_path, format="mp3")
    segment.export(export_wav, format="wav")
    audio_manager.filePath = export_wav
    audio_manager.wf = wave.open(export_wav, "rb")

    result = audio_manager.normalizeUploadedFile()

    assert result == export_wav
    with wave.open(export_wav, "rb") as wf:
        assert wf.getnframes() > 0


def test_temp_file_removed_after_normalize(audio_manager, tmp_path):
    path = str(tmp_path / "session.wav")
    _write_sine_wav(path)
    audio_manager.filePath = path
    audio_manager.wf = wave.open(path, "rb")

    before = set(os.listdir(tmp_path))
    audio_manager.normalizeUploadedFile()
    after = set(os.listdir(tmp_path))

    # Only the destination WAV should remain; mkstemp temps must be gone.
    leftover_temps = [
        name for name in (after - before) if name.endswith(".wav") and name != "session.wav"
    ]
    assert leftover_temps == []


def test_normalize_export_failure_cleans_temp_and_preserves_source(audio_manager, tmp_path, monkeypatch):
    path = str(tmp_path / "session.wav")
    _write_sine_wav(path)
    with open(path, "rb") as f:
        original_bytes = f.read()

    audio_manager.filePath = path
    audio_manager.wf = wave.open(path, "rb")

    def failing_export(self, *args, **kwargs):
        raise OSError("simulated export failure")

    monkeypatch.setattr(AudioSegment, "export", failing_export)

    with pytest.raises(OSError, match="simulated export failure"):
        audio_manager.normalizeUploadedFile()

    assert audio_manager.wf is None
    assert os.path.exists(path)
    with open(path, "rb") as f:
        assert f.read() == original_bytes
    leftover_temps = [name for name in os.listdir(tmp_path) if name.endswith(".wav") and name != "session.wav"]
    assert leftover_temps == []
