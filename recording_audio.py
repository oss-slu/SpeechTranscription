import pyaudio
import wave

class Record:
    def __init__(self):

        self.isRecording = False

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)


        print("start recording...")
        print("hit r to stop recording")

        frames = []
        #seconds = 5
        #for i in range(0, int(RATE / CHUNK * seconds)):
        #    data = stream.read(CHUNK)
        #    frames.append(data)
        while self.isRecording:
            data = stream.read(CHUNK)
            frames.append(data)


        print("recording stopped")

        stream.stop_stream()
        stream.close()
        p.terminate()

        outfile = wave.open("output1.wav", 'wb')
        outfile.setnchannels(CHANNELS)
        outfile.setsampwidth(p.get_sample_size(FORMAT))
        outfile.setframerate(RATE)
        outfile.writeframes(b''.join(frames))
        outfile.close()

    def start(self):
        self.isRecording = True
    def stop(self):
        self.isRecording = False




