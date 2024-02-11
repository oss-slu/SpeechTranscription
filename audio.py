import customtkinter # Only imported for typing
import wave
import pyaudio
from pydub import AudioSegment
from pydub.effects import normalize
import numpy as np

class AudioManager:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    p = pyaudio.PyAudio()
    filePath = "session_output.wav"
    playing = False
    isRecording = False
    paused = True
    
    def __init__(self, root: customtkinter.CTk):
        self.root = root
        self.out_stream = None

    def record(self):
        self.filePath = "session_output.wav"
        self.isRecording = True
        self.frames = []
        stream = self.p.open(format = self.FORMAT, channels = self.CHANNELS, rate = self.RATE, input = True, frames_per_buffer = self.CHUNK)
        
        while self.isRecording:
            data = stream.read(self.CHUNK)
            self.frames.append(data)
            self.root.update()
            
        stream.close()
        
    def stop(self):
        self.isRecording = False
        self.saveAudioFile(self.filePath)
        time, signal = self.createWaveformFile()
        return (self.filePath, time, signal)
    
    def play(self, startPosition=0):
        '''
        self.stopPlayback()

        print("Playing audio...from", startPosition)
        self.playing = True
        self.paused = False
        audio_file = wave.open(self.filePath, "rb")
        
        startFrame = int(startPosition * audio_file.getframerate())
        audio_file.setpos(startFrame)  # Seek to the start position

        # Code to create seperate output audio stream so audio can be played
        out_p = pyaudio.PyAudio()
        print('here3')
        out_stream = out_p.open(
            format = out_p.get_format_from_width(audio_file.getsampwidth()),
            channels = audio_file.getnchannels(),
            rate = audio_file.getframerate(),
            output = True
        )
        print('here4')
        
        dat = audio_file.readframes(self.CHUNK)
        while dat != b"" and self.playing:
            if not self.paused:
                out_stream.write(dat)
                dat = audio_file.readframes(self.CHUNK)

        self.playing = False
        out_stream.close()
        print("Audio has ended")
        '''
    def play(self, startPosition=0):
        self.stopPlayback()  # Ensure any previous playback is stopped

        print("Playing audio...from", startPosition)
        self.playing = True
        self.paused = False
        audio_file = wave.open(self.filePath, "rb")
        
        startFrame = int(startPosition * audio_file.getframerate())
        audio_file.setpos(startFrame)  # Seek to the start position

        self.out_stream = self.p.open(
            format = self.p.get_format_from_width(audio_file.getsampwidth()),
            channels = audio_file.getnchannels(),
            rate = audio_file.getframerate(),
            output = True
        )
        
        data = audio_file.readframes(self.CHUNK)
        while data != b"" and self.playing:
            if not self.paused:
                self.out_stream.write(data)
                data = audio_file.readframes(self.CHUNK)

        audio_file.close()  # Close the file after playback is finished
        self.stopPlayback()  # Stop and clean up the stream

        
    def pause(self):
        self.paused = not self.paused
        return self.paused
    
    def upload(self, filename: str):
        self.filePath = filename
        name = filename.split(".")[0]
        extension = filename.split(".")[1].lower()
        if extension in ["mp3", "wav"]:
            if extension == "mp3":
                segment = AudioSegment.from_mp3(self.filePath)
                print("Attempting to convert mp3 to wav")
            else:
                segment = AudioSegment.from_wav(self.filePath)
            spacer = AudioSegment.silent(duration=2000)
            segment = spacer.append(segment, crossfade=0)
            segment.export("export.wav", format="wav")
            self.filePath = "export.wav"
            time, signal = self.createWaveformFile()
            return (time, signal)
        else:
            print("The file format is not valid. Name: " + name + "; Extension: " + extension)
            
    def normalizeUploadedFile(self):
        # Create copy of file as AudioSegment for pydub normalize function
        print("The audio file is attempting to be normalized")
        pre_normalized_audio = AudioSegment.from_file(self.filePath, format="wav")
        normalized_audio = normalize(pre_normalized_audio)
        normalized_audio.export(out_f=self.filePath, format="wav")
        return self.filePath
        
    def createWaveformFile(self):
        self.audioExists = True
        raw = wave.open(self.filePath)
        signal = raw.readframes(-1)
        signal = np.frombuffer(signal, dtype = "int16")
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

    def getAudioDuration(self, filename):
        audio = AudioSegment.from_file(filename)
        return len(audio) / 1000.0  # Return duration in seconds

    def seek(self, position):

        self.stopPlayback()
        self.play(startPosition=position)
        #if self.playing:
            # Pause playback if currently playing
        #    self.pause()
            # Restart playback from the new position
        #    self.play(startPosition=position)
        #else:
            # If not currently playing, just update the position to start from later
        #    self.play(startPosition=position)
        #    self.pause()  # Immediately pause since we're only updating the position

    def stopPlayback(self):
        '''        
        if self.playing:
            #self.playing = False
            # Stop playback and close the stream
            if self.out_stream is not None:
                print("out stream", self.out_stream)
                print('here2')
                self.out_stream.stop_stream()
                self.out_stream.close()
                self.playing = False
                self.paused = True
            # Reset the PyAudio instance if needed
            self.p.terminate()
            self.p = pyaudio.PyAudio()  # Reinitialize PyAudio instance
        '''
        self.playing = False  # Stop the playback loop
        if self.out_stream is not None:
            self.out_stream.stop_stream()
            self.out_stream.close()
            self.out_stream = None  # Reset out_stream to None after closing
        self.p.terminate()
        self.p = pyaudio.PyAudio()  # Reinitialize PyAudio instance