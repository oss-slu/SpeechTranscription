from tkinter import Button, Checkbutton, IntVar, Label, Text, Entry, StringVar, OptionMenu, filedialog, scrolledtext, WORD
from speechrecog.recogtest import recog
import tkinter as tk
from tkinter.filedialog import asksaveasfile
#import recording_audio
import pyaudio
import wave
import os
import shutil
import nltk
import addConventions

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
    
    def play(self):
        audio_file = wave.open(self.filePath, 'rb')
        #code to create seperate output audio stream so audio can be played
        out_p = pyaudio.PyAudio()
        out_stream = out_p.open(
            format = out_p.get_format_from_width(audio_file.getsampwidth()),
            channels = audio_file.getnchannels(),
            rate = audio_file.getframerate(),
            output = True
        )
        output = audio_file.readframes(self.CHUNK)
        while output != b'':
            out_stream.write(output)
            output = audio_file.readframes(self.CHUNK)

    def download_recorded_audio(self):
        print('downloading')
        #self.filePath = filedialog.asksaveasfile(filetypes = files, defaultextension = files)
        #create a copy of audio that is saved to computer
        download_file = filedialog.asksaveasfile(defaultextension = '.wav',
                                        filetypes = [("Wave File", '.wav'),
                                                    ("All Files", '.*')],
                                        #initialdir = self.filePath,
                                        initialfile = "downloaded_audio.wav"         
                                        )
        #print(download_file)
        #print(self.filePath)
        download = wave.open(download_file.name, 'wb')
        download.setnchannels(self.CHANNELS)
        download.setsampwidth(self.p.get_sample_size(self.FORMAT))
        download.setframerate(self.RATE)
        download.writeframes(b''.join(self.frames))
        download.close() 

    def uploadAudio(self):
        self.filePath = filedialog.askopenfilename()
        print('File uploaded: ', self.filePath)
        self.audioPlaceholder.config(text='Audio Uploaded Here!')


# Sends client info submitted by user to the transciption box
    def submitClientInfo(self) :
        # Gets the current text in the entry box
        infoEntryText = self.infoEntry.get()
        self.transcription.configure(state='normal')
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
        elif (self.clicked.get() == "Examiner Name"):
            self.transcription.insert("end", "Examiner Name: ")
        elif (self.clicked.get() == "Sampling Context"):
            self.transcription.insert("end", "Sampling Context: ")
        # Appends the submitted text after the field name
        self.transcription.insert("end", infoEntryText + "\n")
        self.transcription.configure(state='disabled')
        # Clears the entry box
        self.infoEntry.delete(0, "end")

# Runs recogtest.py (transcribes audio.wav in the current directory) then prints to the transcription box
    def transcribe(self) :
        transcribedAudio = recog(self.filePath).getTranscript()
        self.transcription.configure(state='normal')
        self.transcription.insert("end", transcribedAudio + "\n");
        self.transcription.configure(state='disabled')

# Adds conventions to text from transcription box and puts output in transcriptionWithGrammar box
    def addConventionsClick(self):
        self.transcriptionWithGrammar.configure(state='normal')
        converting = self.transcription.get("1.0", "end")
        if (self.grammarCheck1.get() == 1):
            converting = addConventions.addEndPunctuation(converting)
        if (self.grammarCheck2.get() == 1):
            converting = addConventions.addInflectionalMorphemes(converting)
        if (self.grammarCheck3.get() == 1):
            converting = addConventions.addWordLevelErrors(converting)
        if (self.grammarCheck4.get() == 1):
            converting = addConventions.addOmissions(converting)
        self.transcriptionWithGrammar.delete('1.0', "end")
        self.transcriptionWithGrammar.insert("end", converting)
        self.transcriptionWithGrammar.configure(state='disabled')

# Sends individual sentences to addWordLevelErrors to check for correction, if there is a corrected version, add squiggles
    def grammarCheck(self):
        self.tokenizedSentences = []
        # Flag for if user wants to manually submit each sentence
        self.checkAllSentences = False
        # Configuring right-hand box, correction box, and submit button
        self.transcriptionWithGrammar.grid(row=5, column=3, columnspan=3)
        self.transcriptionWithGrammar.configure(state='normal')
        self.transcriptionWithGrammar.delete('1.0', "end")
        self.transcriptionWithGrammar.configure(state='disabled')
        self.correctionEntry.grid(row=6, column=3, columnspan=2)
        self.submitCorrectionButton.grid(row=6, column=5)
        # Get raw transcription and tokenize into sentences for processing
        text = self.transcription.get("1.0", "end")
        self.tokenizedSentences = nltk.sent_tokenize(text)
        self.getNextCorrection()
    
    # Loops through tokenizedSentences until one needs to be corrected, sending it to correctionEntry
    def getNextCorrection(self):
        if (len(self.tokenizedSentences) == 0):
            # Maybe return message that all sentences were processed
            return
        while (len(self.tokenizedSentences)):
            if ((self.tokenizedSentences[0] != addConventions.correctSentence(self.tokenizedSentences[0])) or self.checkAllSentences):
                self.correctionEntry.insert("end", addConventions.correctSentence(self.tokenizedSentences[0]))
                del self.tokenizedSentences[0]
                break
            else:
                self.transcriptionWithGrammar.configure(state='normal')
                self.transcriptionWithGrammar.insert("end", self.tokenizedSentences[0] + "\n")
                self.transcriptionWithGrammar.configure(state='disabled')
                del self.tokenizedSentences[0]

    def applyCorrection(self):
        # Append sentence in correctionEntry to right-hand box
        self.transcriptionWithGrammar.configure(state='normal')
        self.transcriptionWithGrammar.insert("end", self.correctionEntry.get("1.0", "end"))
        self.transcriptionWithGrammar.configure(state='disabled')
        # Remove previously worked-on sentence
        self.correctionEntry.delete('1.0', "end")
        # Queue up the next correction for the user
        self.getNextCorrection()

    def editTranscription(self):
        if self.editTranscriptionButton['text'] == 'Save Transcription':
            self.editTranscriptionButton['text'] = 'Edit Transcription'
            self.transcription.configure(state='disabled')

        else:
            self.editTranscriptionButton['text'] = 'Save Transcription'
            self.transcription.configure(state='normal')

    def editGrammar(self):
        if self.editGrammarButton['text'] == 'Save Grammar':
            self.editGrammarButton['text'] = 'Edit Grammar'
            self.transcriptionWithGrammar.configure(state='disabled')

        else:
            self.editGrammarButton['text'] = 'Save Grammar'
            self.transcriptionWithGrammar.configure(state='normal')


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

        playButton = Button(self.master, text='Play', command=lambda: self.play())
        playButton.grid(row=0, column=3)

        downloadButton = Button(self.master, text='Download', command=lambda: self.download_recorded_audio())
        downloadButton.grid(row=0, column=4)

        transcribeButton = Button(self.master, text='Transcribe', command=self.transcribe)
        transcribeButton.grid(row=0, column=5)

        clientOptions = [
                "Name",
                "Age",
                "Gender",
                "Date of Birth",
                "Date of Sample",
                "Examiner Name",
                "Sampling Context"
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

        self.transcription = scrolledtext.ScrolledText(self.master, width = 60, height = 20, font=('Courier New',12), spacing1=1)
        self.transcription.configure(state='disabled', wrap=WORD)
        self.transcription.grid(row=5, column=0, columnspan=3)
        self.transcription.tag_config('squiggly', bgstipple='@squiggly.xbm', background='red')

        self.transcriptionWithGrammar = scrolledtext.ScrolledText(self.master, width = 60, height = 20, font=('Courier New',12), spacing1=1)
        self.transcriptionWithGrammar.configure(state='disabled', wrap=WORD)

        self.editTranscriptionButton = Button(self.master, text='Edit Transcription', command=self.editTranscription)
        self.editTranscriptionButton.grid(row=6, column=1)
        self.grammarCheckButton = Button(self.master, text='Grammar Check', command=self.grammarCheck)
        self.grammarCheckButton.grid(row=6, column=2)

        self.correctionEntry = scrolledtext.ScrolledText(self.master, width = 45, height = 1, font=('Courier New',12), spacing1=1)
        self.correctionEntry.configure(wrap=WORD)

        self.submitCorrectionButton = Button(self.master, text='Submit', command=self.applyCorrection)

        self.editGrammarButton = Button(self.master, text='Edit', command=self.editGrammar)
        self.editGrammarButton.grid(row=7, column=4)

        exportButton = Button(self.master, text='Export to Word Document')
        exportButton.grid(row=8, column=4)
        printButton = Button(self.master, text='Print')
        printButton.grid(row=9, column=4)


        self.master.mainloop()

if __name__ == "__main__":
    myGui = GUI()
