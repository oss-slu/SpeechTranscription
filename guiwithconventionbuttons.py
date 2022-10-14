from tkinter import Button, Checkbutton, IntVar, Label, Text, Entry, StringVar, OptionMenu, filedialog
from speechrecog.recogtest import recog
import tkinter as tk
import recording_audio
import addConventions

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
        elif (self.clicked.get() == "Sampling Context"):
            self.transcription.insert("end", "Sampling Context: ")
        # Appends the submitted text after the field name
        self.transcription.insert("end", infoEntryText + "\n")
        # Clears the entry box
        self.infoEntry.delete(0, "end")

# Runs recogtest.py (transcribes audio.wav in the current directory) then prints to the transcription box 
    def transcribe(self) :
        transcribedAudio = recog(self.filePath).getTranscript()
        self.transcription.insert("end", transcribedAudio + "\n");

# Adds conventions to text from transcription box and puts output in transcriptionwithGrammar box
    def addConventionsClick(self):
        converting = self.transcription.get("1.0", "end")
        if (self.grammarCheck1.get() == 1):
            converting = addConventions.addEndPunctuation(converting)
        if (self.grammarCheck2.get() == 1):
            converting = addConventions.addInflectionalMorphemes(converting)
        if (self.grammarCheck3.get() == 1):
            converting = addConventions.addWordLevelErrors(converting)
        if (self.grammarCheck4.get() == 1):
            converting = addConventions.addOmissions(converting)
        self.transcriptionwithGrammar.delete('1.0', "end")
        self.transcriptionwithGrammar.insert("end", converting)

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

        self.grammarCheck1 = IntVar()
        self.grammarCheck2 = IntVar()
        self.grammarCheck3 = IntVar()
        self.grammarCheck4 = IntVar()
        grammarButton1 = Checkbutton(self.master, text='End Punctuation', variable=self.grammarCheck1)
        grammarButton2 = Checkbutton(self.master, text='Inflectional Morphemes', variable=self.grammarCheck2)
        grammarButton3 = Checkbutton(self.master, text='Word Level Errors', variable=self.grammarCheck3)
        grammarButton4 = Checkbutton(self.master, text='Omissions', variable=self.grammarCheck4)

        grammarButton1.grid(row=2, column=1)
        grammarButton2.grid(row=2, column=3)
        grammarButton3.grid(row=3, column=1)
        grammarButton4.grid(row=3, column=3)

        addConventionsButton = Button(self.master, text='Add Conventions', command=self.addConventionsClick)
        addConventionsButton.grid(row=4, column=2)

        editTranscriptionButton = Button(self.master, text='Edit Transcription')
        editTranscriptionButton.grid(row=6, column=1)
        exportButton = Button(self.master, text='Export to Word Document')
        exportButton.grid(row=6, column=4)
        printButton = Button(self.master, text='Print')
        printButton.grid(row=7, column=4)

        self.transcription = Text(self.master)
        self.transcription.grid(row=5, column=0, columnspan=3)

        self.transcriptionwithGrammar = Text(self.master)
        self.transcriptionwithGrammar.grid(row=5, column=3, columnspan=3)


        self.master.mainloop()

if __name__ == "__main__":
    myGui = GUI()
