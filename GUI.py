from tkinter import Button, Checkbutton, IntVar, Label, Text, Entry, StringVar, OptionMenu, filedialog, scrolledtext, WORD
from functions import addConventions
from functions import diarizationAndTranscription
import tkinter as tk
from tkinter.filedialog import asksaveasfile
#import recording_audio
import pyaudio
import wave
import nltk
import ffmpeg
import ffprobe
from pydub import AudioSegment
from pydub.effects import normalize
import threading
import fleep

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
        self.playing = True
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
        while output != b'' and self.playing:
            out_stream.write(output)
            output = audio_file.readframes(self.CHUNK)

    def pause(self):
        self.playing = False

    def playback_click(self):
        play_thread = threading.Thread(target=self.play)
        if self.playButton['text'] == 'Play':
            self.playButton['text'] = 'Stop'
            play_thread.start()
        else:
            self.playButton['text'] = 'Play'
            self.pause()

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
        infoEntryText = self.infoEntryBox.get()
        self.transcriptionBox.configure(state='normal')
        # Prints the relevant field
        if (self.clicked.get() == "Name"):
            self.transcriptionBox.insert("end", "Name: ")
        elif (self.clicked.get() == "Age"):
            self.transcriptionBox.insert("end", "Age: ")
        elif (self.clicked.get() == "Gender"):
            self.transcriptionBox.insert("end", "Gender: ")
        elif (self.clicked.get() == "Date of Birth"):
            self.transcriptionBox.insert("end", "Date of Birth: ")
        elif (self.clicked.get() == "Date of Sample"):
            self.transcriptionBox.insert("end", "Date of Sample: ")
        elif (self.clicked.get() == "Examiner Name"):
            self.transcriptionBox.insert("end", "Examiner Name: ")
        elif (self.clicked.get() == "Sampling Context"):
            self.transcriptionBox.insert("end", "Sampling Context: ")
        # Appends the submitted text after the field name
        self.transcriptionBox.insert("end", infoEntryText + "\n")
        self.transcriptionBox.configure(state='disabled')
        # Clears the entry box
        self.infoEntryBox.delete(0, "end")

    def mp3towav(self, audiofile):
        dst = self.filePath
        sound = AudioSegment.from_mp3(audiofile)
        sound.export(dst, format="wav")

    def convertToWAV(self, audioSeg):
        audioSeg.export(out_f = "converted.wav", format = "wav")

    # Runs recogtest.py (transcribes audio.wav in the current directory) then prints to the transcription box
    def transcribe(self) :
        name = self.filePath.split('.')[0]
        extension = self.filePath.split('.')[1]
        with open(self.filePath, "rb") as audiofile:
            audiocheck = fleep.get(audiofile.read(128))
        if (extension == "MP3"):
            mp3 = AudioSegment.from_mp3(self.filePath)
            ret = mp3.export("export.wav", format = "wav")
            print("Attempting to export wav from mp3. ret = " + str(ret))
        elif (extension == "wav"):
            wav = AudioSegment.from_wav(self.filePath)
            ret = wav.export("export.wav", format = "wav" )
            print("Attempting to export wav from wav. ret = " + str(ret))
        else:
            print("The format is not valid. name: " + name + " extension: " + extension)
        # create copy of file as AudioSegment for pydub normalize function
        print("File path attempting to be normalized: " + self.filePath)
        pre_normalized_audio = AudioSegment.from_file("export.wav", format = "wav")
        normalized_audio = normalize(pre_normalized_audio)
        # transcribed audio is now using normalized audiofile
        self.convertToWAV(normalized_audio)
        transcribedAudio = diarizationAndTranscription.diarizeAndTranscribe("converted.wav")
        #normal_wav.close()
        self.transcriptionBox.configure(state='normal')
        self.transcriptionBox.insert("end", transcribedAudio + "\n")
        self.transcriptionBox.configure(state='disabled')

    # Adds conventions to text from transcription box and puts output in conventionBox box
    def inflectionalMorphemes(self):
        self.conventionBox.configure(state='normal')
        converting = self.conventionBox.get("1.0", "end")
        # My name is Jake. My name are Jake. (this is a relic of debugging, DO NOT DELETE)
        converting = addConventions.addInflectionalMorphemes(converting)
        self.conventionBox.delete('1.0', "end")
        self.conventionBox.insert("end", converting)
        self.conventionBox.configure(state='disabled')

    # Sends individual sentences to addWordLevelErrors to check for correction, if there is a corrected version, add squiggles
    def grammarCheck(self):
        self.tokenizedSentences = []
        # Flag for if user wants to manually submit each sentence
        self.checkAllSentences = False
        # Configuring right-hand box, correction box, and submit button
        self.conventionBox.grid(row=5, column=3, columnspan=3)
        self.conventionBox.delete('1.0', "end")
        self.editConventionBoxButton.grid(row=7, column=4)
        self.clearConventionBoxButton.grid(row=7, column=5)
        self.correctionEntryBox.grid(row=6, column=3, columnspan=2)
        self.correctionEntryBox.delete('1.0', "end")
        self.submitCorrectionButton.grid(row=6, column=5)
        # Get raw transcription and tokenize into sentences for processing
        text = self.transcriptionBox.get("1.0", "end")
        self.tokenizedSentences = nltk.sent_tokenize(text)
        self.getNextCorrection()
    
    # Loops through tokenizedSentences until one needs to be corrected, sending it to correctionEntryBox
    def getNextCorrection(self):
        if (len(self.tokenizedSentences) == 0):
            # Maybe return message that all sentences were processed
            return
        while (len(self.tokenizedSentences)):
            if ((self.tokenizedSentences[0] != addConventions.correctSentence(self.tokenizedSentences[0])) or self.checkAllSentences):
                self.correctionEntryBox.insert("end", addConventions.correctSentence(self.tokenizedSentences[0]))
                del self.tokenizedSentences[0]
                break
            else:
                self.conventionBox.configure(state='normal')
                self.conventionBox.insert("end", self.tokenizedSentences[0] + "\n")
                self.conventionBox.configure(state='disabled')
                del self.tokenizedSentences[0]

    def applyCorrection(self):
        # Append sentence in correctionEntryBox to right-hand box
        self.conventionBox.configure(state='normal')
        self.conventionBox.insert("end", self.correctionEntryBox.get("1.0", "end"))
        self.conventionBox.configure(state='disabled')
        # Remove previously worked-on sentence
        self.correctionEntryBox.delete('1.0', "end")
        # Queue up the next correction for the user
        self.getNextCorrection()

    def editTranscriptionBox(self):
        if self.editTranscriptionBoxButton['text'] == 'Save Transcription':
            self.editTranscriptionBoxButton['text'] = 'Edit Transcription'
            self.transcriptionBox.configure(state='disabled')

        else:
            self.editTranscriptionBoxButton['text'] = 'Save Transcription'
            self.transcriptionBox.configure(state='normal')

    def editConventionBox(self):
        if self.editConventionBoxButton['text'] == 'Save Convention Box':
            self.editConventionBoxButton['text'] = 'Edit Convention Box'
            self.conventionBox.configure(state='disabled')

        else:
            self.editConventionBoxButton['text'] = 'Save Convention Box'
            self.conventionBox.configure(state='normal')

    def clearTranscriptionBox(self):
        if self.editTranscriptionBoxButton['text'] == 'Save Transcription':
            self.transcriptionBox.delete('1.0', "end")

        else:
            self.transcriptionBox.configure(state='normal')
            self.transcriptionBox.delete('1.0', "end")
            self.transcriptionBox.configure(state='disabled')

    def clearConventionBox(self):
        if self.editConventionBoxButton['text'] == 'Save Convention Box':
            self.conventionBox.delete('1.0', "end")

        else:
            self.conventionBox.configure(state='normal')
            self.conventionBox.delete('1.0', "end")
            self.conventionBox.configure(state='disabled')


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
        self.playing = False
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

        self.playButton = Button(self.master, text='Play', command=lambda: self.playback_click())
        self.playButton.grid(row=0, column=3)

        downloadButton = Button(self.master, text='Download', command=lambda: self.download_recorded_audio())
        downloadButton.grid(row=0, column=4)

        transcribeButton = Button(self.master, text='Transcribe', command=self.transcribe)
        transcribeButton.grid(row=0, column=5)


        # CLIENT INFORMATION-RELATED BUTTONS/BOXES

        # Attributes of sample to be selected and submitted by user
        clientOptions = [
                "Name",
                "Age",
                "Gender",
                "Date of Birth",
                "Date of Sample",
                "Examiner Name",
                "Sampling Context"
                ]

        # Allows user to select a sampling attribute, type the relevant information, and submit it
        self.clicked = StringVar()
        self.clicked.set("Name")
        infoDropdown = OptionMenu(self.master, self.clicked, *clientOptions)
        infoDropdown.grid(row=1, column=1)
        self.infoEntryBox = Entry(self.master)
        self.infoEntryBox.grid(row=1, column=2)
        infoSubmitButton = Button(self.master, text="Submit", command=self.submitClientInfo)
        infoSubmitButton.grid(row=1, column=3)


        # LARGE BOXES AND RELATED BUTTONS

        # transcriptionBox is the left-hand box used for editing speech-recognized text
        self.transcriptionBox = scrolledtext.ScrolledText(self.master, width = 60, height = 20, font=('Courier New',12), spacing1=1)
        self.transcriptionBox.configure(state='disabled', wrap=WORD)
        self.transcriptionBox.grid(row=5, column=0, columnspan=3)
        # Permits user to type in transcriptionBox
        self.editTranscriptionBoxButton = Button(self.master, text='Edit Transcription', command=self.editTranscriptionBox)
        self.editTranscriptionBoxButton.grid(row=6, column=0)
        # Clears transcriptionBox
        self.clearTranscriptionBoxButton = Button(self.master, text='Clear', command=self.clearTranscriptionBox)
        self.clearTranscriptionBoxButton.grid(row=6, column=1)

        # conventionBox is the right-hand box used for adding all types of conventions
        self.conventionBox = scrolledtext.ScrolledText(self.master, width = 60, height = 20, font=('Courier New',12), spacing1=1)
        self.conventionBox.configure(state='disabled', wrap=WORD)
        # Permits user to type in conventionBox
        self.editConventionBoxButton = Button(self.master, text='Edit Convention Box', command=self.editConventionBox)
        # Clears conventionBox
        self.clearConventionBoxButton = Button(self.master, text='Clear', command=self.clearConventionBox)


        # CONVENTION-RELATED BUTTONS/BOXES

        # Initiates grammarCheck process on text in transcriptionBox
        self.grammarCheckButton = Button(self.master, text='Grammar Check', command=self.grammarCheck)
        self.grammarCheckButton.grid(row=6, column=2)
        # Manually edit sentences caught during grammarCheck process
        self.correctionEntryBox = scrolledtext.ScrolledText(self.master, width = 45, height = 1, font=('Courier New',12), spacing1=1)
        self.correctionEntryBox.configure(wrap=WORD)
        # Appends sentence within correctionEntryBox to right-hand box, continues grammarCheck process
        self.submitCorrectionButton = Button(self.master, text='Submit', command=self.applyCorrection)
        # Applies inflectional morphemes to text in right-hand box
        self.addMorphemesButton = Button(self.master, text='Add Morphemes', command=self.inflectionalMorphemes)
        self.addMorphemesButton.grid(row=7, column=2)


        # EXPORT-RELATED

        # Exports to word
        exportButton = Button(self.master, text='Export to Word Document')
        exportButton.grid(row=8, column=4)
        # Prints
        printButton = Button(self.master, text='Print')
        printButton.grid(row=9, column=4)


        self.master.mainloop()

if __name__ == "__main__":
    myGui = GUI()
