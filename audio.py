import customtkinter # Only imported for typing
import wave
import pyaudio
import numpy as np

class Audio:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    p = pyaudio.PyAudio()
    filePath = "session_output.wav"
    
    def __init__(self, root: customtkinter.CTk):
        self.root = root
        file = open(self.filePath, "w+")
        file.close()

    def record(self):
        self.filePath = 'session_output.wav'
        self.isRecording = True
        self.frames = []
        stream = self.p.open(format = self.FORMAT, channels = self.CHANNELS, rate = self.RATE, input = True, frames_per_buffer = self.CHUNK)
        
        while self.isRecording:
            data = stream.read(self.CHUNK)
            self.frames.append(data)
            self.root.update()
            
        stream.close()

        self.createRecordedAudioOutput(self.filePath)
        
    def stop(self):
        self.isRecording = False

        # Create waveform audio
        self.audioExists = True
        raw = wave.open(self.filePath)
        signal = raw.readframes(-1)
        signal = np.frombuffer(signal, dtype = "int16")
        f_rate = raw.getframerate()
        time = np.linspace(0, len(signal) / f_rate, num=len(signal))
        
        return (self.filePath, time, signal)
        
    def play(self):
        self.playing = True
        self.paused = False
        audio_file = wave.open(self.filePath, 'rb')
        
        # Code to create seperate output audio stream so audio can be played
        out_p = pyaudio.PyAudio()
        out_stream = out_p.open(
            format = out_p.get_format_from_width(audio_file.getsampwidth()),
            channels = audio_file.getnchannels(),
            rate = audio_file.getframerate(),
            output = True
        )

        self.playing = False
        out_stream.close()
        
    def pause(self):
        self.paused = not self.paused
        return self.paused
        
    def createRecordedAudioOutput(self, filename: str):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()