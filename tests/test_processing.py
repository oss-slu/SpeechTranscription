"""Tests for the transcription/grammar processing workflow: progress, cancel, and error recovery."""

import importlib
import multiprocessing
import os
import shutil
import subprocess
import sys
import threading
import time

import pytest

import grammar as grammar_module
from components.processing import TranscriptionJob, describeTranscriptionError


# Worker targets must be module-level so the spawned process can import them.
def _succeedingWorker(audioFile, messages):
    messages.put(("progress", "Transcribing", 0.5))
    messages.put(("done", f"[0:00] transcript of {os.path.basename(audioFile)}"))


def _failingWorker(audioFile, messages):
    messages.put(("error", "friendly message", "traceback text"))


def _crashingWorker(audioFile, messages):
    os._exit(3)


def _slowWorker(audioFile, messages):
    messages.put(("progress", "Transcribing", 0.1))
    time.sleep(60)


def _runUntilFinished(job, timeout=30):
    messages = []
    deadline = time.time() + timeout
    while job.isRunning() and time.time() < deadline:
        messages += job.poll()
        time.sleep(0.05)
    return messages


class TestTranscriptionJob:
    def test_reports_progress_then_result(self):
        job = TranscriptionJob("clip.wav", target=_succeedingWorker)
        job.start()
        messages = _runUntilFinished(job)
        assert messages == [("progress", "Transcribing", 0.5), ("done", "[0:00] transcript of clip.wav")]
        assert job.poll() == []

    def test_passes_worker_errors_through(self):
        job = TranscriptionJob("clip.wav", target=_failingWorker)
        job.start()
        assert _runUntilFinished(job) == [("error", "friendly message", "traceback text")]

    def test_worker_that_dies_without_reporting_becomes_an_error(self):
        job = TranscriptionJob("clip.wav", target=_crashingWorker)
        job.start()
        messages = _runUntilFinished(job)
        assert len(messages) == 1
        kind, message, details = messages[0]
        assert kind == "error"
        assert "stopped unexpectedly" in message
        assert "3" in details

    def test_cancel_stops_the_worker_process(self):
        job = TranscriptionJob("clip.wav", target=_slowWorker)
        job.start()
        deadline = time.time() + 30
        while not job.poll() and time.time() < deadline:
            time.sleep(0.05)
        job.cancel()
        assert not job.isAlive()
        assert job.exitcode is not None
        assert not job.isRunning()
        assert job.poll() == []

    def test_polling_a_dead_worker_never_blocks(self):
        job = TranscriptionJob("clip.wav", target=_crashingWorker)
        job.start()
        slowest = 0.0
        messages = []
        deadline = time.time() + 30
        while job.isRunning() and time.time() < deadline:
            started = time.perf_counter()
            messages += job.poll()
            slowest = max(slowest, time.perf_counter() - started)
            time.sleep(0.05)
        assert messages and messages[0][0] == "error"
        # poll() runs on the GUI thread, so it must return immediately even while waiting out the grace
        # period. A normal call takes a few ms; the limit leaves room for a busy machine but is well
        # under the 0.5 s a blocking wait for the queue would take.
        assert slowest < 0.2, f"poll() blocked for {slowest:.3f}s"

    def test_repeated_cancel_and_retry_leaves_no_workers_behind(self):
        for _ in range(4):
            job = TranscriptionJob("clip.wav", target=_slowWorker)
            job.start()
            deadline = time.time() + 30
            while not job.poll() and time.time() < deadline:
                time.sleep(0.05)
            job.cancel()
            assert job.poll() == []

        job = TranscriptionJob("clip.wav", target=_succeedingWorker)
        job.start()
        assert _runUntilFinished(job)[-1] == ("done", "[0:00] transcript of clip.wav")
        # Only the last worker may still be finishing; every cancelled one is gone
        deadline = time.time() + 5
        while multiprocessing.active_children() and time.time() < deadline:
            time.sleep(0.05)
        assert multiprocessing.active_children() == []


@pytest.mark.parametrize("error, expected", [
    (MemoryError(), "ran out of memory"),
    (RuntimeError("CUDA out of memory"), "ran out of memory"),
    (RuntimeError("Failed to load audio: ffmpeg error"), "could not be read"),
    (FileNotFoundError(2, "No such file", "ffmpeg"), "ffmpeg could not be found"),
    (FileNotFoundError(2, "No such file", "/tmp/a.wav"), "could not be found"),
    (ConnectionError("reset"), "internet connection"),
    (RuntimeError("<urlopen error [Errno 8]>"), "internet connection"),
    (ValueError("something odd"), "Transcription failed: something odd"),
])
def test_errors_explain_what_to_do(error, expected):
    assert expected in describeTranscriptionError(error)


class TestGrammarCheckerCancellation:
    @pytest.fixture
    def checker(self, monkeypatch):
        # Every sentence is already correct, so the checker would otherwise run to the end
        monkeypatch.setattr(grammar_module.addConventions, "correctSentence", lambda sentence: sentence)
        checker = grammar_module.GrammarChecker()
        checker.checkGrammar("One. Two. Three. Four.", False)
        return checker

    def test_progress_counts_checked_sentences(self, checker):
        assert checker.getProgress() == 0.0
        checker.getNextCorrection()
        assert checker.getProgress() == 1.0

    def test_should_stop_ends_the_check_early(self, checker):
        calls = []

        def shouldStop():
            calls.append(1)
            return len(calls) > 2

        corrected, sentenceToCorrect = checker.getNextCorrection(shouldStop=shouldStop)
        assert sentenceToCorrect is None
        assert corrected == "One.\nTwo.\n"
        assert checker.getProgress() == 0.5


class FakeJob:
    """Stands in for TranscriptionJob; tests choose which messages it returns."""
    instances = []
    script = []

    def __init__(self, audioFile):
        self.audioFile = audioFile
        self.cancelled = False
        self.started = False
        self.messages = list(FakeJob.script)
        FakeJob.instances.append(self)

    def start(self):
        self.started = True

    def isRunning(self):
        return not self.cancelled

    def poll(self):
        messages, self.messages = self.messages, []
        return messages

    def cancel(self):
        self.cancelled = True


@pytest.fixture(scope="module")
def root():
    # One window for every test: the app's icons belong to the first Tk window created
    customtkinter = pytest.importorskip("customtkinter")
    try:
        root = customtkinter.CTk()
    except Exception as error:  # no display available
        pytest.skip(f"Tk is not available: {error}")
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def menu(root, monkeypatch, tmp_path):
    from components import audio_menu

    popups = []
    monkeypatch.setattr(audio_menu, "show_error_popup",
                        lambda master, message, retry=None: popups.append((message, retry)))
    FakeJob.instances = []
    FakeJob.script = []
    monkeypatch.setattr(audio_menu, "TranscriptionJob", FakeJob)

    menu = audio_menu.audioMenu(root)
    menu.popups = popups
    wav = tmp_path / "session.wav"
    wav.write_bytes(b"RIFF fake audio")
    menu.audio.filePath = str(wav)
    menu.audio.normalizeUploadedFile = lambda: str(wav)
    for button in (menu.transcribeButton, menu.uploadButton, menu.exportButton, menu.grammarButton):
        button.configure(state="normal")
    menu.transcriptionBox.configure(state="normal")
    menu.transcriptionBox.delete("1.0", "end")
    menu.transcriptionBox.insert("1.0", "[0:00] Existing transcript.")

    yield menu
    menu.cancelProcessing()
    menu.destroy()


def _pump(menu, until, timeout=5):
    deadline = time.time() + timeout
    while not until() and time.time() < deadline:
        menu.update()
        time.sleep(0.02)
    menu.update()
    return until()


def _transcript(menu):
    return menu.transcriptionBox.get("1.0", "end").strip()


class TestAudioMenuProcessing:
    def test_transcription_success_replaces_transcript_and_unlocks(self, menu):
        FakeJob.script = [("progress", "Transcribing", 0.5), ("done", "[0:00] New transcript.")]
        menu.toggleTranscription()
        assert menu.transcribeButton.cget("text") == "Cancel"
        assert menu.uploadButton.cget("state") == "disabled"

        assert _pump(menu, lambda: menu.processing is None)
        assert _transcript(menu) == "[0:00] New transcript."
        assert menu.transcribeButton.cget("text") == "Transcribe"
        assert menu.uploadButton.cget("state") == "normal"
        assert menu.grammarButton.cget("state") == "normal"
        assert menu.progressLabel.cget("text") == "Transcription complete"
        assert menu.popups == []

    def test_repeated_clicks_start_only_one_job(self, menu):
        FakeJob.script = []  # job keeps running
        menu.startTranscription()
        menu.startTranscription()
        menu.grammarCheckThread()
        assert _pump(menu, lambda: FakeJob.instances)
        menu.startTranscription()
        _pump(menu, lambda: False, timeout=0.3)
        assert len(FakeJob.instances) == 1
        assert menu.processing == "transcription"

    def test_cancel_stops_job_and_keeps_transcript(self, menu):
        FakeJob.script = []
        menu.toggleTranscription()
        assert _pump(menu, lambda: FakeJob.instances)
        menu.toggleTranscription()  # the button now says Cancel

        assert FakeJob.instances[0].cancelled
        assert menu.processing is None
        assert _transcript(menu) == "[0:00] Existing transcript."
        assert menu.transcribeButton.cget("text") == "Transcribe"
        assert menu.transcribeButton.cget("state") == "normal"
        assert menu.uploadButton.cget("state") == "normal"
        assert menu.progressLabel.cget("text") == "Transcription cancelled"

    def test_failure_keeps_transcript_and_audio_and_offers_retry(self, menu):
        FakeJob.script = [("error", "The speech model could not be downloaded.", "details")]
        audioPath = menu.audio.filePath
        menu.toggleTranscription()

        assert _pump(menu, lambda: menu.popups)
        assert _transcript(menu) == "[0:00] Existing transcript."
        assert os.path.exists(audioPath)
        assert menu.transcribeButton.cget("state") == "normal"
        message, retry = menu.popups[0]
        assert "could not be downloaded" in message

        FakeJob.script = [("done", "[0:00] Retried transcript.")]
        retry()
        assert _pump(menu, lambda: menu.processing is None and len(FakeJob.instances) == 2)
        assert _transcript(menu) == "[0:00] Retried transcript."

    def test_audio_preparation_failure_is_reported(self, menu):
        def brokenNormalize():
            raise OSError("disk full")
        menu.audio.normalizeUploadedFile = brokenNormalize
        menu.toggleTranscription()

        assert _pump(menu, lambda: menu.popups)
        assert "disk full" in menu.popups[0][0]
        assert FakeJob.instances == []
        assert menu.processing is None

    def test_empty_result_does_not_wipe_transcript(self, menu):
        FakeJob.script = [("done", "   ")]
        menu.toggleTranscription()

        assert _pump(menu, lambda: menu.popups)
        assert "No speech was detected" in menu.popups[0][0]
        assert _transcript(menu) == "[0:00] Existing transcript."

    def test_grammar_check_can_be_cancelled(self, menu, monkeypatch):
        release = threading.Event()

        def slowCorrect(sentence):
            release.wait(5)
            return sentence
        monkeypatch.setattr(grammar_module.addConventions, "correctSentence", slowCorrect)

        menu.toggleGrammarCheck()
        assert menu.grammarButton.cget("text") == "Cancel"
        assert menu.transcribeButton.cget("state") == "disabled"
        menu.toggleGrammarCheck()
        release.set()

        assert menu.processing is None
        assert menu.grammarButton.cget("text") == "Grammar Check"
        assert menu.transcribeButton.cget("state") == "normal"
        _pump(menu, lambda: False, timeout=0.3)
        assert menu.popups == []


class TestWhisperProgressHook:
    @pytest.fixture
    def transcription(self):
        return pytest.importorskip("diarizationAndTranscription")

    def test_installed_whisper_still_reports_progress_through_tqdm(self, transcription):
        # Canary: if a whisper update changes this, progress silently falls back to stages only
        import inspect
        whisperTranscribe = importlib.import_module("whisper.transcribe")
        assert transcription._whisperProgressHook() is whisperTranscribe
        source = inspect.getsource(whisperTranscribe.transcribe)
        assert "tqdm.tqdm(" in source and "pbar.update(" in source

    def test_progress_is_forwarded_and_tqdm_restored(self, transcription, monkeypatch):
        whisperTranscribe = importlib.import_module("whisper.transcribe")
        original = whisperTranscribe.tqdm

        class FakeModel:
            def transcribe(self, audioFile, **options):
                assert options["verbose"] is False  # whisper only drives the bar when verbose is False
                with whisperTranscribe.tqdm.tqdm(total=4, disable=True) as bar:
                    for _ in range(4):
                        bar.update(1)
                return {"text": "Hello.", "segments": []}

        monkeypatch.setattr(transcription, "loadModel", lambda: FakeModel())
        fractions = []
        result = transcription.transcribeAudio("clip.wav", on_progress=fractions.append)
        assert result["text"] == "Hello."
        assert fractions == [0.25, 0.5, 0.75, 1.0]
        assert whisperTranscribe.tqdm is original

    def test_falls_back_when_whisper_internals_change(self, transcription, monkeypatch):
        whisperTranscribe = importlib.import_module("whisper.transcribe")
        monkeypatch.setattr(whisperTranscribe, "tqdm", object())

        class FakeModel:
            def transcribe(self, audioFile, **options):
                assert "verbose" not in options
                return {"text": "Hello.", "segments": []}

        monkeypatch.setattr(transcription, "loadModel", lambda: FakeModel())
        fractions = []
        assert transcription.transcribeAudio("clip.wav", on_progress=fractions.append)["text"] == "Hello."
        assert fractions == []


@pytest.mark.skipif(os.environ.get("SALTIFY_WHISPER_TESTS") != "1",
                    reason="set SALTIFY_WHISPER_TESTS=1 to run real Whisper (slow, needs the small.en model)")
@pytest.mark.skipif(sys.platform != "darwin" or not shutil.which("say"), reason="uses macOS 'say' to make speech")
def test_real_whisper_transcription_in_worker_process(tmp_path):
    wav = tmp_path / "speech.wav"
    subprocess.run(["say", "-o", str(wav), "--data-format=LEI16@16000", "The dog runs to the park."], check=True)
    job = TranscriptionJob(str(wav))
    job.start()
    messages = _runUntilFinished(job, timeout=300)
    progress = [message[2] for message in messages if message[0] == "progress"]
    assert progress == sorted(progress)
    assert any(message[1] == "Transcribing" and message[2] > 0.1 for message in messages if message[0] == "progress")
    assert messages[-1][0] == "done"
    assert "dog" in messages[-1][1].lower()


class TestReviewFixes:
    """Cancelling during audio preparation, and finding later grammar corrections in the background."""

    @staticmethod
    def _enablePlayback(menu):
        for widget in (menu.restartButton, menu.backwardButton, menu.playPauseButton, menu.forwardButton,
                       menu.timelineSlider):
            widget.configure(state="normal")

    def test_cancel_during_preparation_keeps_controls_locked_until_it_finishes(self, menu):
        self._enablePlayback(menu)
        release = threading.Event()
        started = threading.Event()
        path = menu.audio.filePath

        def slowNormalize():
            started.set()
            release.wait(10)
            return path
        menu.audio.normalizeUploadedFile = slowNormalize

        menu.toggleTranscription()
        assert started.wait(5)
        assert menu.playPauseButton.cget("state") == "disabled"
        menu.toggleTranscription()  # Cancel

        # Still preparing: nothing is handed back yet
        _pump(menu, lambda: False, timeout=0.3)
        assert menu.processing == "transcription"
        assert menu.transcribeButton.cget("text") == "Cancelling..."
        assert menu.transcribeButton.cget("state") == "disabled"
        assert menu.uploadButton.cget("state") == "disabled"
        assert menu.playPauseButton.cget("state") == "disabled"
        menu.toggleTranscription()  # ignored while cancelling
        menu.startTranscription()
        assert menu.processing == "transcription"

        release.set()
        assert _pump(menu, lambda: menu.processing is None)
        assert menu.transcribeButton.cget("text") == "Transcribe"
        assert menu.transcribeButton.cget("state") == "normal"
        assert menu.uploadButton.cget("state") == "normal"
        assert menu.playPauseButton.cget("state") == "normal"
        assert menu.timelineSlider.cget("state") == "normal"
        assert menu.progressLabel.cget("text") == "Transcription cancelled"
        assert FakeJob.instances == []  # the prepared audio was never transcribed
        assert _transcript(menu) == "[0:00] Existing transcript."

    def test_playback_unlocks_once_audio_is_prepared(self, menu):
        self._enablePlayback(menu)
        FakeJob.script = []  # transcription keeps running
        menu.toggleTranscription()
        assert _pump(menu, lambda: FakeJob.instances)
        assert menu.playPauseButton.cget("state") == "normal"
        assert menu.uploadButton.cget("state") == "disabled"

    def test_cancel_after_preparation_is_immediate(self, menu):
        FakeJob.script = []
        menu.toggleTranscription()
        assert _pump(menu, lambda: FakeJob.instances)
        menu.toggleTranscription()
        assert menu.processing is None
        assert FakeJob.instances[0].cancelled

    @pytest.fixture
    def grammarMenu(self, menu, monkeypatch):
        """Grammar check on a transcript whose first sentence needs a correction and the rest don't.
        Checking the later sentences waits on menu.release and records which thread did the work."""
        menu.release = threading.Event()
        menu.checkThreads = []

        def correctSentence(sentence):
            if "goed" in sentence:
                return sentence.replace("goed", "went")
            menu.checkThreads.append(threading.current_thread())
            menu.release.wait(10)
            return sentence
        monkeypatch.setattr(grammar_module.addConventions, "correctSentence", correctSentence)
        menu.transcriptionBox.delete("1.0", "end")
        menu.transcriptionBox.insert("1.0", "[0:00] She goed home. [0:02] It is fine. [0:04] All good.")
        menu.toggleGrammarCheck()
        assert _pump(menu, lambda: menu.processing is None)
        assert "went" in menu.correctionEntryBox.get("1.0", "end")
        assert menu.submitGrammarButton.cget("state") == "normal"
        return menu

    def test_submit_finds_the_next_correction_off_the_gui_thread(self, grammarMenu):
        menu = grammarMenu
        started = time.perf_counter()
        menu.applyCorrection()
        assert time.perf_counter() - started < 1  # returned without checking the remaining sentences
        assert menu.processing == "grammar"
        assert menu.grammarButton.cget("text") == "Cancel"
        assert menu.submitGrammarButton.cget("state") == "disabled"
        assert menu.correctionEntryBox.cget("state") == "disabled"

        menu.release.set()
        assert _pump(menu, lambda: menu.processing is None)
        assert menu.checkThreads and threading.main_thread() not in menu.checkThreads
        assert menu.grammarCheckPerformed
        assert menu.progressLabel.cget("text") == "Grammar check complete"
        assert menu.exportButton.cget("state") == "normal"
        assert menu.morphemesButton.cget("state") == "normal"
        assert menu.submitGrammarButton.cget("state") == "disabled"
        convention = menu.conventionBox.get("1.0", "end")
        assert "It is fine." in convention and "All good." in convention

    def test_cancelling_the_next_correction_ends_the_grammar_step(self, grammarMenu):
        menu = grammarMenu
        menu.applyCorrection()
        assert _pump(menu, lambda: menu.checkThreads)
        menu.toggleGrammarCheck()  # Cancel
        menu.release.set()

        assert menu.processing is None
        assert menu.grammarButton.cget("text") == "Grammar Check"
        assert menu.grammarButton.cget("state") == "normal"
        assert menu.submitGrammarButton.cget("state") == "disabled"
        assert menu.correctionEntryBox.cget("state") == "disabled"
        assert menu.exportButton.cget("state") == "normal"
        assert not menu.grammarCheckPerformed
        assert menu.progressLabel.cget("text") == "Grammar check cancelled"
        _pump(menu, lambda: False, timeout=0.3)
        assert menu.popups == []
