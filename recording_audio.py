import pyaudio
import wave
import tkinter as tk

class Record:
    def __init__(self, main):

        self.main = main

        self.CHUNK = 8000
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100

        self.p = pyaudio.PyAudio()

        self.frames = []

        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)

    def recording(self, isRecording): 
        print("test")
        self.frames = []   
        stream = self.p.open(format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK)
                    
        while isRecording:
            data = self.stream.read(self.CHUNK, exception_on_overflow = False)
            self.frames.append(data)
            self.main.update()
            print("**recording**")

        print("recording ended")

        stream.close()

        outfile = wave.open("output1.wav", 'wb')
        outfile.setnchannels(self.CHANNELS)
        outfile.setsampwidth(self.p.get_sample_size(self.FORMAT))
        outfile.setframerate(self.RATE)
        outfile.writeframes(b''.join(self.frames))
        outfile.close()

        print("file saved")

        

    def stop_recording(self):
        self.isRecording = False
        print("not recording")
        
        print("file saved")



