"""Unit tests for the audio playback state and controls."""

import struct
import threading
import wave
from unittest.mock import Mock

import pytest

import audio as audio_module
from audio import AudioManager


class FakeOutputStream:
    """Small PyAudio output-stream substitute for deterministic tests."""

    def __init__(self):
        self.writes = []
        self.closed = False
        self.stopped = False

    def write(self, data):
        self.writes.append(data)

    def is_stopped(self):
        return self.stopped

    def stop_stream(self):
        self.stopped = True

    def close(self):
        self.closed = True


class BlockingOutputStream(FakeOutputStream):
    """Output stream that stays active until playback is stopped externally."""

    def __init__(self):
        super().__init__()
        self.started = threading.Event()
        self.release = threading.Event()

    def write(self, data):
        self.writes.append(data)
        self.started.set()
        self.release.wait(timeout=1)

    def close(self):
        super().close()
        self.release.set()


def _write_wav(path, seconds=1, rate=8):
    """Write a small mono PCM WAV file without external audio tools."""
    frame_count = int(seconds * rate)
    frames = b"".join(struct.pack("<h", index) for index in range(frame_count))
    # Pylint cannot distinguish wave readers from writers here.
    # pylint: disable=no-member
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(rate)
        wav_file.writeframes(frames)
    # pylint: enable=no-member


@pytest.fixture
def audio_manager(monkeypatch, tmp_path):
    """Create an AudioManager without opening a real audio device."""
    output_stream = FakeOutputStream()
    mock_pyaudio = Mock()
    mock_pyaudio.get_format_from_width.return_value = 8
    mock_pyaudio.open.return_value = output_stream
    monkeypatch.setattr(audio_module.pyaudio, "PyAudio", lambda: mock_pyaudio)
    AudioManager._active_manager = None

    manager = AudioManager(root=Mock())
    audio_path = tmp_path / "sample.wav"
    _write_wav(audio_path)
    manager.filePath = str(audio_path)
    manager.duration = 1.0

    yield manager, output_stream, mock_pyaudio

    manager.stopPlayback()
    AudioManager._active_manager = None


def test_playback_resets_to_zero_after_reaching_end(audio_manager):
    """Natural completion returns playback to the beginning for replay."""
    manager, output_stream, mock_pyaudio = audio_manager

    manager.play()

    assert manager.playing is False
    assert manager.paused is True
    assert manager.current_position == 0.0
    assert output_stream.writes
    assert output_stream.closed is True
    mock_pyaudio.open.assert_called_once()


def test_seek_clamps_to_audio_bounds(audio_manager):
    """Seeking never moves before the start or after the duration."""
    manager, _, _ = audio_manager
    # pylint: disable=no-member
    manager.wf = wave.open(manager.filePath, "rb")
    # pylint: enable=no-member

    assert manager.seek(-5) == 0.0
    assert manager.seek(5) == manager.duration


def test_playback_error_is_reported_on_the_ui_thread(audio_manager):
    """Playback failures are passed to the callback instead of being swallowed."""
    manager, _, mock_pyaudio = audio_manager
    mock_pyaudio.open.side_effect = OSError("output unavailable")
    callback = Mock()
    manager.root.after.side_effect = lambda _delay, function: function()

    manager.play(on_error=callback)

    callback.assert_called_once()
    assert "output unavailable" in str(callback.call_args.args[0])


def test_playback_stream_is_replaced_when_another_manager_starts(audio_manager):
    """Only one AudioManager may own an active playback stream at a time."""
    first_manager, first_stream, _ = audio_manager
    first_stream = BlockingOutputStream()
    first_manager.p.open.return_value = first_stream
    second_manager = AudioManager(root=Mock())
    second_manager.filePath = first_manager.filePath
    second_manager.duration = first_manager.duration
    second_stream = FakeOutputStream()
    second_manager.p = Mock()
    second_manager.p.get_format_from_width.return_value = 8
    second_manager.p.open.return_value = second_stream

    first_thread = threading.Thread(target=first_manager.play, daemon=True)
    first_thread.start()
    assert first_stream.started.wait(timeout=1)
    second_manager.play()
    first_thread.join(timeout=1)

    assert first_stream.closed is True
    assert first_thread.is_alive() is False
    assert second_stream.writes
    second_manager.stopPlayback()
