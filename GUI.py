from tkinter import Button, Checkbutton, IntVar, Label, Text, Entry, StringVar, OptionMenu, filedialog
from speechrecog.recogtest import recog
import tkinter as tk
import recording_audio

class GUI:

    isRecording = False
    recorder = recording_audio.Record()

    def recordAudio(self, recordButton):
        if self.isRecording:
            self.recorder.start()
            recordButton.config(text='Record')
            self.isRecording = False
        else:
            self.recorder.stop()
            recordButton.config(text='Stop')
            self.isRecording = True

    def uploadAudio(self, audioPlaceholder):
        self.filePath = filedialog.askopenfilename()
        print('File uploaded: ', self.filePath)
        audioPlaceholder.config(text='Audio Uploaded Here!')

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
        recog(self.filePath)
        transcribedAudio = recog(filePath).transcript
        self.transcription.insert("end", transcribedAudio + "\n");

    def __init__(self):
        self.master = tk.Tk()
        self.master.title('Speech Transcription')
        self.master.geometry('960x540')

        uploadButton = Button(self.master, text='Upload', command=lambda: self.uploadAudio(self.audioPlaceholder))
        uploadButton.grid(row=0, column=0)

        self.recordButton = Button(self.master, text='Record', command=lambda: self.recordAudio(self.recordButton))
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
