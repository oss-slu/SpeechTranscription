import pyaudio
import wave

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

frames = []
seconds = 5
for i in range(0, int(RATE / CHUNK * seconds)):
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
