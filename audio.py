import customtkinter  # Only imported for typing
import wave
import pyaudio
from pydub import AudioSegment
from pydub.effects import normalize
import numpy as np
import threading
import time

import os
import sys
import tempfile

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

class AudioManager:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    _playback_guard = threading.RLock()
    _active_manager = None
    
    def __init__(self, root: customtkinter.CTk, audio_menu=None):
        self.root = root
        self.p = pyaudio.PyAudio()
        self.out_stream = None
        self.wf = None
        self.filePath = None
        self.playing = False
        self.paused = True
        self.isRecording = False
        self.lock = threading.RLock()
        self.current_position = 0.0
        self.duration = 0.0
        self.audio_menu = audio_menu  # ✅ Now it's declared properly

    @property
    def has_audio(self):
        return bool(self.filePath and os.path.isfile(self.filePath))

    @staticmethod
    def _temporary_wav_path():
        file = tempfile.NamedTemporaryFile(prefix="saltify_audio_", suffix=".wav", delete=False)
        file.close()
        return file.name

    def record(self):
        self.filePath = self._temporary_wav_path()
        self.isRecording = True
        self.frames = []
        stream = None
        try:
            stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
            
            while self.isRecording:
                # exception_on_overflow=False avoids macOS Input overflowed (-9981)
                # crashes when the UI update loop briefly stalls mic reads.
                # Overflowed frames are dropped silently instead of raising.
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                self.frames.append(data)
                self.root.update()
                
        except OSError as e:
            self.isRecording = False
            if e.errno == -9996 or e.errno == -9999:
                raise RuntimeError("No default microphone is available. Check your audio input settings.") from e
            else:
                raise
        finally:
            self.isRecording = False
            if stream:
                try:
                    stream.close()
                except (OSError, IOError):
                    pass

    def stop(self):
        self.isRecording = False
        self.saveAudioFile(self.filePath)
        self.duration = self.getAudioDuration(self.filePath)
        if self.duration <= 0:
            raise ValueError("The recording is empty. Record some audio before stopping.")
        self.current_position = 0.0
        time, signal = self.createWaveformFile()
        return (self.filePath, time, signal)
    
    def play(self, startPosition=None, on_error=None):
        """Play audio from the current position, replacing any other session's stream."""
        error = None
        started = False
        duplicate_request = False
        audio_file = None
        try:
            if not self.has_audio:
                raise FileNotFoundError("Upload or record audio before playing it.")

            with self._playback_guard:
                previous = self.__class__._active_manager
                if previous is not None and previous is not self:
                    previous.stopPlayback()
                self.__class__._active_manager = self
                with self.lock:
                    if self.playing:
                        if self.paused:
                            self.paused = False
                        duplicate_request = True
                    else:
                        if startPosition is not None:
                            self.current_position = max(0.0, min(float(startPosition), self.duration))
                        if self.current_position >= self.duration:
                            self.current_position = 0.0

                        audio_file = wave.open(self.filePath, "rb")
                        audio_file.setpos(int(self.current_position * audio_file.getframerate()))
                        stream = self.p.open(
                            format=self.p.get_format_from_width(audio_file.getsampwidth()),
                            channels=audio_file.getnchannels(),
                            rate=audio_file.getframerate(),
                            output=True,
                            frames_per_buffer=self.CHUNK,
                        )
                        self.wf = audio_file
                        self.out_stream = stream
                        self.playing = True
                        self.paused = False
                        started = True

            if duplicate_request:
                return

            while self.playing:
                with self.lock:
                    paused = self.paused
                    audio_file = self.wf
                    stream = self.out_stream
                if paused:
                    time.sleep(0.03)
                    continue

                with self.lock:
                    if not self.playing or self.paused or audio_file is not self.wf:
                        continue
                    data = audio_file.readframes(self.CHUNK)
                    if not data:
                        break
                    self.current_position = audio_file.tell() / audio_file.getframerate()
                stream.write(data)
        except Exception as exc:
            with self.lock:
                stopped_externally = started and not self.playing
            if not stopped_externally:
                error = exc
                print(f"Playback error: {exc}")
        finally:
            if not duplicate_request:
                self.stopPlayback(reset_position=error is None)
                if audio_file is not None:
                    try:
                        audio_file.close()
                    except (OSError, IOError):
                        pass
            if error is not None and on_error is not None:
                try:
                    self.root.after(0, lambda err=error: on_error(err))
                except Exception:
                    pass

    def pause(self):
        with self.lock:
            self.paused = not self.paused
        return self.paused
    
    def upload(self, filename: str):
        extension = os.path.splitext(filename)[1].lower().lstrip(".")
        if extension not in {"mp3", "wav"}:
            raise ValueError("Unsupported audio format. Choose an MP3 or WAV file.")

        self.stopPlayback(reset_position=True)
        converted_path = self._temporary_wav_path()
        try:
            AudioSegment.from_file(filename, format=extension).export(converted_path, format="wav")
            with wave.open(converted_path, "rb") as audio_file:
                duration = audio_file.getnframes() / audio_file.getframerate()
            if duration <= 0:
                raise ValueError("The selected audio file is empty.")
        except Exception:
            if os.path.exists(converted_path):
                os.remove(converted_path)
            raise

        self.filePath = converted_path
        self.duration = duration
        self.current_position = 0.0
        return self.createWaveformFile()

    def normalizeUploadedFile(self):
        """Normalize loudness and rewrite the session WAV safely.

        Closes any open wave reader before replacement, writes to a temp file,
        then replaces the destination. Overwriting the same path while a
        wave.Wave_read handle remains open has caused macOS segmentation faults.

        Close/reopen of self.wf is done under self.lock so a playback thread
        cannot readframes() on a handle we are closing. Heavy normalize/export
        work stays outside the lock to avoid deadlocking with play()'s paused
        sleep that also holds the lock.
        """
        print("The audio file is attempting to be normalized")

        with self.lock:
            if self.wf:
                self.wf.close()
                self.wf = None

        pre_normalized_audio = AudioSegment.from_file(self.filePath, format="wav")
        normalized_audio = normalize(pre_normalized_audio)

        directory = os.path.dirname(os.path.abspath(self.filePath)) or "."
        fd, temp_path = tempfile.mkstemp(suffix=".wav", dir=directory)
        os.close(fd)
        try:
            normalized_audio.export(out_f=temp_path, format="wav")
            os.replace(temp_path, self.filePath)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

        with self.lock:
            self.wf = wave.open(self.filePath, "rb")
        return self.filePath
        
    def createWaveformFile(self):
        self.audioExists = True
        with wave.open(self.filePath) as raw:
            signal = raw.readframes(-1)
            signal = np.frombuffer(signal, dtype="int16")
            f_rate = raw.getframerate()
            time = np.linspace(0, len(signal) / f_rate, num=len(signal))
        return (time, signal)
        
    def saveAudioFile(self, filename: str):
        wf = wave.open(filename, "wb")
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b"".join(self.frames))
        wf.close()

    def getAudioDuration(self, filename=None):
        if filename is None:
            if self.duration:
                return self.duration
            filename = self.filePath
        audio = AudioSegment.from_file(filename)
        return len(audio) / 1000.0  # Return duration in seconds

    def setPlaybackPosition(self, position):
        self.seek(position)

    def seek(self, position):
        if not self.has_audio:
            return 0.0
        with self.lock:
            self.current_position = max(0.0, min(float(position), self.duration))
            if self.wf:
                self.wf.setpos(int(self.current_position * self.wf.getframerate()))
            return self.current_position

    def stopPlayback(self, reset_position=True):
        '''Stops the audio playback and cleans up resources.'''
        with self.lock:
            self.playing = False
            self.paused = True
            stream, self.out_stream = self.out_stream, None
            audio_file, self.wf = self.wf, None
            if reset_position:
                self.current_position = 0.0

        if stream:
            try:
                if not stream.is_stopped():
                    stream.stop_stream()
                stream.close()
            except (OSError, IOError):
                pass
        if audio_file:
            try:
                audio_file.close()
            except (OSError, IOError):
                pass

        with self._playback_guard:
            if self.__class__._active_manager is self:
                self.__class__._active_manager = None

    def get_current_position(self):
        with self.lock:
            return self.current_position


    def transcribe_audio(self):
        """Starts transcription and updates progress bar."""
        self.audio_menu.startProgressBar()


        for progress in range(101):  # Replace with actual transcription progress
            time.sleep(0.1)  # Simulated delay
            self.audio_menu.update_progress_bar(progress / 100)

        self.audio_menu.stopProgressBar()  # Hide when done
