import tkinter
import tkinter as tk
import tkinter.messagebox
import pyaudio
import wave
import os

#from recorder import Tape_Recorder

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()

class Record_Store:
    
    def record(self):
        self.isRecording = True
        self.frames = []
        stream = self.p.open(format = self.FORMAT, 
                            channels = self.CHANNELS, 
                            rate = self.RATE, 
                            input = True, 
                            frames_per_buffer = self.CHUNK)
        while self.isRecording:
            data = stream.read(self.CHUNK)
            self.frames.append(data)
            self.base.update()
        
        stream.close()

        wf = wave.open('test_recording.wav', 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
    
    def stop(self):
        self.isRecording = False

    def action(self):
        print('action called')
        if self.record_button['text'] == 'Record':
            self.record_button['text'] = 'Stop'
            #self.recorder.record(self.base)
            self.base.record()
            print('*recording*')
        else:
            self.record_button['text'] = 'Record'
            #self.recorder.stop()
            self.base.stop()
            print('*recording stopped*')

    def __init__(self):
        #set up for base tkinter window
        self.base = tk.Tk()
        self.base.geometry('300x200')
        self.base.resizable(False, False)
        self.base.title('Record Store')

        #create record button
        self.record_button = tk.Button(
            self.base,
            text =  'Record',
            command = self.action
        )
        self.record_button.pack()
        #self.recorder = Tape_Recorder()
        #create recording capabilities
        self.CHUNK = CHUNK
        self.FORMAT = FORMAT
        self.CHANNELS = CHANNELS
        self.RATE = RATE
        self.p = p

        self.frames = []
        self.isRecording = False
        self.stream = self.p.open(format = self.FORMAT, 
                                channels = self.CHANNELS, 
                                rate = self.RATE, 
                                input = True, 
                                frames_per_buffer = self.CHUNK)
        #main loop
        self.base.mainloop()

shop = Record_Store()




        