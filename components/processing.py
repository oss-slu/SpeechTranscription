# components/processing.py
"""Runs transcription in its own process so it can be cancelled part way through.

Whisper's transcribe call can't be interrupted from inside, so the only way to stop
it is to stop the process running it. Messages come back over a queue as tuples:
    ("progress", stage, fraction)  -- fraction is overall progress from 0.0 to 1.0
    ("done", transcript)
    ("error", user_message, details)
"""
import multiprocessing
import queue
import time
import traceback


def describeTranscriptionError(error):
    '''Turns an exception into a message that says what happened and what to do next.'''
    text = str(error)
    lowered = text.lower()
    if isinstance(error, MemoryError) or "out of memory" in lowered:
        return ("The computer ran out of memory while transcribing. "
                "Close other programs or try a shorter recording, then retry.")
    if "failed to load audio" in lowered or "could not decode" in lowered or "decoding" in lowered:
        return ("The audio file could not be read. Make sure it plays correctly, "
                "or try converting it to WAV and uploading it again.")
    if isinstance(error, FileNotFoundError) and "ffmpeg" in lowered:
        return "ffmpeg could not be found, so the audio can't be read. Reinstall Saltify and try again."
    if isinstance(error, FileNotFoundError):
        return f"The audio file could not be found ({text}). Upload or record the audio again."
    if isinstance(error, (ConnectionError, TimeoutError)) or any(
            word in lowered for word in ("urlopen", "connection", "sha256", "timed out", "name resolution")):
        return ("The speech model could not be downloaded. "
                "Check your internet connection and retry.")
    return f"Transcription failed: {text or type(error).__name__}. You can retry, or file a bug if it keeps happening."


def _transcriptionWorker(audioFile, messages):
    try:
        # Imported here so the slow whisper/torch import happens in the worker process
        import diarizationAndTranscription
        transcript = diarizationAndTranscription.transcribe(
            audioFile, on_progress=lambda stage, fraction: messages.put(("progress", stage, fraction)))
        messages.put(("done", transcript))
    except BaseException as error:
        messages.put(("error", describeTranscriptionError(error), traceback.format_exc()))


class TranscriptionJob:
    # How long to keep checking for a final message after the worker exits. The queue's
    # feeder can still be flushing then, but poll() never waits for it.
    EXIT_GRACE_SECONDS = 1.0

    def __init__(self, audioFile, target=_transcriptionWorker):
        # spawn behaves the same on every OS and doesn't copy Tk state into the child
        context = multiprocessing.get_context("spawn")
        self._messages = context.Queue()
        self._process = context.Process(target=target, args=(audioFile, self._messages), daemon=True)
        self._exitedAt = None
        self.exitcode = None
        self.finished = False
        self.cancelled = False

    def start(self):
        self._process.start()

    def isAlive(self):
        return self.exitcode is None and self._process.is_alive()

    def isRunning(self):
        return not self.finished and not self.cancelled

    def poll(self):
        '''Returns the messages received since the last call. Never blocks the GUI.'''
        if not self.isRunning():
            return []
        messages = self._drain()
        if not self.finished and not self._process.is_alive():
            if self._exitedAt is None:
                self._exitedAt = time.monotonic()
            elif time.monotonic() - self._exitedAt >= self.EXIT_GRACE_SECONDS:
                self.finished = True
                messages.append(("error",
                                 "The transcription process stopped unexpectedly. Retry, or try a shorter recording.",
                                 f"Worker exit code: {self._process.exitcode}"))
        if self.finished:
            self._cleanUp()
        return messages

    def _drain(self):
        messages = []
        while True:
            try:
                message = self._messages.get_nowait()
            except (queue.Empty, OSError, ValueError):
                return messages
            messages.append(message)
            if message[0] in ("done", "error"):
                self.finished = True
                return messages

    def cancel(self):
        if not self.isRunning():
            return
        self.cancelled = True
        if self._process.is_alive():
            self._process.terminate()
            self._process.join(timeout=2)
            if self._process.is_alive():
                self._process.kill()
                self._process.join(timeout=2)
        self._cleanUp()

    def _cleanUp(self):
        '''Releases the queue and process. Each job has its own queue, so nothing stale can
        reach a later job.'''
        # A terminated worker can leave the queue half written; don't wait on flushing it
        self._messages.cancel_join_thread()
        self._messages.close()
        if not self._process.is_alive():
            self._process.join(timeout=0)
            self.exitcode = self._process.exitcode
            self._process.close()
