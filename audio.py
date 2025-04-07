import customtkinter  # Only imported for typing
import wave
import pyaudio
from pydub import AudioSegment
from pydub.effects import normalize
import numpy as np
import tkinter.messagebox as msgbox
<<<<<<< HEAD
import time 
=======
import threading
import time
>>>>>>> 15e6e966e3785c01cd3cfe721142552194110b6b

class AudioManager:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    filePath = "session_output.wav"
    playing = False
    isRecording = False
    paused = True
    
    def __init__(self, root: customtkinter.CTk):
        self.root = root
        self.p = pyaudio.PyAudio()
        self.out_stream = None
        self.wf = None
<<<<<<< HEAD
        self.progress_bar = None  # Assuming you want a progress bar object

    def startProgressBar(self):
        # You can create and display a progress bar here
        # Example (if you are using tkinter or customtkinter):
        self.progress_bar = customtkinter.CTkProgressBar(self.root)
        self.progress_bar.grid(row=0, column=0)  # Example placement
        self.progress_bar.set(0)  # Set initial value to 0%

    def update_progress_bar(self, progress):
        if self.progress_bar:
            self.progress_bar.set(progress)  # Update progress bar value

    def stopProgressBar(self):
        if self.progress_bar:
            self.progress_bar.set(1)  # Set progress to 100% (complete)
            self.progress_bar.grid_forget()  # Hide the progress bar after completion
=======
        self.paused = False
        self.playing = False
        self.lock = threading.Lock()
        self.current_position = 0.0
>>>>>>> 15e6e966e3785c01cd3cfe721142552194110b6b

    def record(self):
        self.filePath = "session_output.wav"
        self.isRecording = True
        self.frames = []
        try:
            stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
            
            while self.isRecording:
                data = stream.read(self.CHUNK)
                self.frames.append(data)
                self.root.update()
                
            stream.close()
        except OSError as e:
            if e.errno == -9996 or e.errno == -9999:
                print("Warning: No default output device available.")
                self.root.after(0, lambda: msgbox.showerror("Audio Error", "No default audio device available. Please check your audio settings."))
            else:
                raise

    def stop(self):
        self.isRecording = False
        self.saveAudioFile(self.filePath)
        time, signal = self.createWaveformFile()
        return (self.filePath, time, signal)
    
    def play(self, startPosition=None):
        '''Plays audio starting from the given position in seconds.'''
        try:
            with self.lock:
                if self.playing and not self.paused:
                    return  # Already playing

                # Initialize audio resources
                if not self.wf:
                    self.wf = wave.open(self.filePath, "rb")
                
                if not self.out_stream or self.out_stream.is_stopped():
                    self.out_stream = self.p.open(
                        format=self.p.get_format_from_width(self.wf.getsampwidth()),
                        channels=self.wf.getnchannels(),
                        rate=self.wf.getframerate(),
                        output=True,
                        frames_per_buffer=self.CHUNK,
                    )

                # Set initial position
                if startPosition is not None:
                    self.current_position = startPosition
                self.wf.setpos(int(self.current_position * self.wf.getframerate()))

                self.playing = True
                self.paused = False

            # Playback loop
            while self.playing:
                with self.lock:
                    if self.paused:
                        time.sleep(0.1)
                        continue

                    data = self.wf.readframes(self.CHUNK)
                    if not data:
                        break

                    # Update current position before writing to stream
                    self.current_position = self.wf.tell() / self.wf.getframerate()
                
                self.out_stream.write(data)

        except Exception as e:
            print(f"Playback error: {e}")
        finally:
            self.stopPlayback()

    def pause(self):
        with self.lock:
            self.paused = not self.paused
        return self.paused
    
    def upload(self, filename: str):
        self.filePath = filename
        try:
            # Close any previously opened wave file
            if self.wf:
                self.wf.close()
                self.wf = None

            # Open and process the file
            name, extension = filename.rsplit(".", 1)
            extension = extension.lower()
            if extension in ["mp3", "wav"]:
                segment = AudioSegment.from_file(self.filePath, format=extension)
                segment.export("export.wav", format="wav")
                self.filePath = "export.wav"

                # Open the wave file
                self.wf = wave.open(self.filePath, "rb")
                time, signal = self.createWaveformFile()
                return (time, signal)
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            print(f"Error uploading file: {e}")
            msgbox.showerror("Upload Error", f"Failed to upload file: {e}")
            # Ensure return values are consistent
            return None, None

    def normalizeUploadedFile(self):
        print("The audio file is attempting to be normalized")
        pre_normalized_audio = AudioSegment.from_file(self.filePath, format="wav")
        normalized_audio = normalize(pre_normalized_audio)
        normalized_audio.export(out_f=self.filePath, format="wav")
        return self.filePath
        
    def createWaveformFile(self):
        self.audioExists = True
        raw = wave.open(self.filePath)
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
            filename = self.filePath
        audio = AudioSegment.from_file(filename)
        return len(audio) / 1000.0  # Return duration in seconds

    def setPlaybackPosition(self, position):
        self.seek(position)

    def seek(self, position):
        with self.lock:
            if self.wf:
                self.current_position = max(0, min(position, self.getAudioDuration()))
                self.wf.setpos(int(self.current_position * self.wf.getframerate()))

        try:
            # Clamp the position to valid bounds
            self.current_position = max(0, min(position, self.getAudioDuration()))

            # Seek to the appropriate frame
            frame = int(self.current_position * self.wf.getframerate())
            self.wf.setpos(frame)

            print(f"Seeked to {self.current_position} seconds.")

            # Update playback if currently playing
            if self.playing and self.out_stream:
                self.paused = False  # Resume playback
        except Exception as e:
            print(f"Error during seek: {e}")
            msgbox.showerror("Seek Error", f"An error occurred while seeking: {e}")

    def stopPlayback(self):
        '''Stops the audio playback and cleans up resources.'''
        with self.lock:
            self.playing = False
        self.paused = True  # Ensure paused is True so playback can reset correctly

        # Stop and close the output stream
        if self.out_stream:
            try:
                self.out_stream.stop_stream()
                self.out_stream.close()
            except OSError as e:
                print(f"Error stopping/closing stream: {e}")
            self.out_stream = None

        # Close and reset the wave file
        if self.wf:
            self.wf.close()
            self.wf = None

        # Terminate PyAudio if active
        if self.p:
            self.p.terminate()
            self.p = None

        # Reinitialize PyAudio to prepare for future playback
        self.p = pyaudio.PyAudio()

<<<<<<< HEAD
    def transcribe_audio(self):
        """Starts transcription and updates progress bar."""
        self.startProgressBar()

        for progress in range(101):  # Replace this with actual transcription progress
            time.sleep(0.1)  # Simulated delay
            self.update_progress_bar(progress / 100)  

        self.stopProgressBar()  # Hide when done
=======
    def get_current_position(self):
        with self.lock:
            return self.current_position
>>>>>>> 15e6e966e3785c01cd3cfe721142552194110b6b
