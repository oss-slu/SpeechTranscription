from tkinter import Button, Checkbutton, IntVar, Label, Text, Entry, StringVar, OptionMenu, filedialog
from speechrecog.recogtest import recog
import tkinter as tk
#import recording_audio
import pyaudio
import wave
import os

#global variables needed to record audio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()

class GUI:

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
            self.master.update()
        
        stream.close()

        wf = wave.open('session_output.wav', 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def stop(self):
        self.isRecording = False
        self.filePath = 'session_output.wav'
        self.audioPlaceholder.config(text='Audio Recorded Here!')

    def recordAudio(self):
        if self.recordButton['text'] == 'Record':
            self.recordButton['text'] = 'Stop'
            self.record()
            print('*recording*')
        else:
            self.recordButton['text'] = 'Record'
            self.stop()
            print('*recording stopped*')

    def uploadAudio(self):
        self.filePath = filedialog.askopenfilename()
        print('File uploaded: ', self.filePath)
        self.audioPlaceholder.config(text='Audio Uploaded Here!')


# Sends client info submitted by user to the transciption box
    def submitClientInfo(self) :
        # Gets the current text in the entry box
        infoEntryText = self.infoEntry.get()
        # Prints the relevant field
        if (self.clicked.get() == "Name"):
            self.transcription.insert("end", "Name: ")
        elif (self.clicked.get() == "Age"):
            self.transcription.insert("end", "Age: ")
        elif (self.clicked.get() == "Gender"):
            self.transcription.insert("end", "Gender: ")
        elif (self.clicked.get() == "Date of Birth"):
            self.transcription.insert("end", "Date of Birth: ")
        elif (self.clicked.get() == "Date of Sample"):
            self.transcription.insert("end", "Date of Sample: ")
        elif (self.clicked.get() == "Examiner Info"):
            self.transcription.insert("end", "Examiner Info: ")
        elif (clicked.get() == "Sampling Context"):
            self.transcription.insert("end", "Sampling Context: ")
        # Appends the submitted text after the field name
        self.transcription.insert("end", infoEntryText + "\n")
        # Clears the entry box
        self.infoEntry.delete(0, "end")

# Runs recogtest.py (transcribes audio.wav in the current directory) then prints to the transcription box 
    def transcribe(self) :
        transcribedAudio = recog(self.filePath).getTranscript()
        self.transcription.insert("end", transcribedAudio + "\n");

    def __init__(self):
        self.master = tk.Tk()
        self.master.title('Speech Transcription')
        self.master.geometry('960x540')

        #self.recorder = Record(self.master)
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

        uploadButton = Button(self.master, text='Upload', command=lambda: self.uploadAudio())
        uploadButton.grid(row=0, column=0)
        self.recordButton = Button(self.master, text='Record', command=lambda: self.recordAudio())
        self.recordButton.grid(row=0, column=1)

        self.audioPlaceholder = Label(self.master, text='(This is where the audio would be)')
        self.audioPlaceholder.grid(row=0, column=2)

        playButton = Button(self.master, text='Play')
        playButton.grid(row=0, column=3)

        downloadButton = Button(self.master, text='Download')
        downloadButton.grid(row=0, column=4)

        transcribeButton = Button(self.master, text='Transcribe', command=self.transcribe)
        transcribeButton.grid(row=0, column=5)

        clientOptions = [
                "Name",
                "Age",
                "Gender",
                "Examiner Info"
                ]
        self.clicked = StringVar()
        self.clicked.set("Name")
        infoDropdown = OptionMenu(self.master, self.clicked, *clientOptions)
        infoDropdown.grid(row=1, column=1)

        self.infoEntry = Entry(self.master)
        self.infoEntry.grid(row=1, column=2)

        infoSubmit = Button(self.master, text="Submit", command=self.submitClientInfo)
        infoSubmit.grid(row=1, column=3)

        grammerCheck1 = IntVar()
        grammerCheck2 = IntVar()
        grammerCheck3 = IntVar()
        grammerCheck4 = IntVar()
        grammerButton1 = Checkbutton(self.master, text='Grammer Option 1')
        grammerButton2 = Checkbutton(self.master, text='Grammer Option 2')
        grammerButton3 = Checkbutton(self.master, text='Grammer Option 3')
        grammerButton4 = Checkbutton(self.master, text='Grammer Option 4')

        grammerButton1.grid(row=2, column=1)
        grammerButton2.grid(row=2, column=3)
        grammerButton3.grid(row=3, column=1)
        grammerButton4.grid(row=3, column=3)

        addConventionsButton = Button(self.master, text='Add Conventions')
        addConventionsButton.grid(row=4, column=2)

        editTranscriptionButton = Button(self.master, text='Edit Transcription')
        editTranscriptionButton.grid(row=6, column=1)
        exportButton = Button(self.master, text='Export to Word Document')
        exportButton.grid(row=6, column=4)
        printButton = Button(self.master, text='Print')
        printButton.grid(row=7, column=4)

        self.transcription = Text(self.master)
        self.transcription.grid(row=5, column=0, columnspan=3)

        transcriptionWithGrammer = Text(self.master)
        transcriptionWithGrammer.grid(row=5, column=3, columnspan=3)


        self.master.mainloop()

if __name__ == "__main__":
    myGui = GUI()
