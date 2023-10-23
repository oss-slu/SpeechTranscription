from tkinter import Button, Label, Entry, StringVar, OptionMenu, filedialog, scrolledtext, WORD
from functions import addConventions
from functions import diarizationAndTranscription
import tkinter as tk
from tkinter.ttk import Button, Entry, OptionMenu
import sv_ttk
from tkinter.filedialog import asksaveasfile
import pyaudio
import wave
import nltk
from pydub import AudioSegment
from pydub.effects import normalize
import threading
from docx import Document
from datetime import date
import customtkinter
import matplotlib.pyplot as plt
import numpy as np
import sys

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

        # waveform audio added here
        self.audioExists = True
        raw = wave.open(self.filePath)
        signal = raw.readframes(-1)
        signal = np.frombuffer(signal, dtype = "int16")
        f_rate = raw.getframerate()
        time = np.linspace(0, len(signal) / f_rate, num=len(signal))
        plt.figure(1)
        plt.title("Audio Wave")
        plt.xlabel("Time")
        plt.plot(time, signal)
        plt.show()

        self.audioPlaceholder.configure(text=self.filePath)

    def recordAudio(self):
        if self.recordButton.cget("text") == 'Record':
            self.recordButton.configure(text = 'Stop')
            self.record()
            print('*recording*')
        else:
            self.recordButton.configure(text = 'Record')
            self.stop()
            print('*recording stopped*')
    
    def play(self):
        self.playing = True
        self.paused = False
        print(self.filePath)
        audio_file = wave.open(self.filePath, 'rb')
        #code to create seperate output audio stream so audio can be played
        out_p = pyaudio.PyAudio()
        out_stream = out_p.open(
            format = out_p.get_format_from_width(audio_file.getsampwidth()),
            channels = audio_file.getnchannels(),
            rate = audio_file.getframerate(),
            output = True
        )

        dat = audio_file.readframes(self.CHUNK)
        while dat != b'' and self.playing:

            if not self.paused:
                out_stream.write(dat)
                dat = audio_file.readframes(self.CHUNK)
        self.playing = False
        self.playButton.configure(text = 'Play')
        print('audio ended')
        out_stream.close()

    '''
    def waveform_audio(self):
        if self.filePath == 'session_output.wav':
            #display waveform audio
            self.audioPlaceholder = customtkinter.CTkLabel(self.master, text=self.filePath)
            self.audioPlaceholder.grid(row=0, column=2, padx=2, pady=2)
    '''

    
    def pause_playback(self):
        if self.paused:
            self.paused = False
            self.pauseButton.configure(text = 'Pause')
        else:
            self.paused = True
            self.pauseButton.configure(text = 'Unpause')
        
    def playback_click(self):
        if not self.playing:
            threading.Thread(target = self.play).start()
            self.playButton.configure(text = 'Stop')
            print("Play")
        else:
            self.playing = False
            self.playButton.configure(text = 'Play')

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
        
        # waveform added audio here
        self.audioExists = True
        raw = wave.open(self.filePath)
        signal = raw.readframes(-1)
        signal = np.frombuffer(signal, dtype = "int16")
        f_rate = raw.getframerate()
        time = np.linspace(0, len(signal) / f_rate, num=len(signal))
        plt.figure(1)
        plt.title("Audio Wave")
        plt.xlabel("Time")
        plt.plot(time, signal)
        plt.show()

        self.audioPlaceholder.configure(text=self.filePath)


    # Sends client info submitted by user to the transciption box
    def submitClientInfo(self) :
        # Gets the current text in the entry box
        infoEntryText = self.infoEntryBox.get()
        # Sets the relevant variable
        if (self.clicked.get() == "Name"):
            self.name = infoEntryText;
            self.infoArray[0] = self.name
        elif (self.clicked.get() == "Age"):
            self.age = infoEntryText;
            self.infoArray[1] = self.age
        elif (self.clicked.get() == "Gender"):
            self.gender = infoEntryText;
            self.infoArray[2] = self.gender
        elif (self.clicked.get() == "Date of Birth"):
            self.dateOfBirth = infoEntryText;
            self.infoArray[3] = self.dateOfBirth
        elif (self.clicked.get() == "Date of Sample"):
            self.dateOfSample = infoEntryText;
            self.infoArray[4] = self.dateOfSample
        elif (self.clicked.get() == "Examiner Name"):
            self.examinerName = infoEntryText;
            self.infoArray[5] = self.examinerName
        elif (self.clicked.get() == "Sampling Context"):
            self.samplingContext = infoEntryText;
            self.infoArray[6] = self.samplingContext
        # Clears the entry box
        self.infoEntryBox.delete(0, "end")

        # Updates Table
        #self.clientInfoBox.configure(state='normal')
        self.clientInfoBox.delete('1.0', "end")
        for x in range(7):
            if self.infoArray[x] != '':
                if x == 0:
                    self.clientInfoBox.insert("end", "Name: ")
                if x == 1:
                    self.clientInfoBox.insert("end", "Age: ")
                if x == 2:
                    self.clientInfoBox.insert("end", "Gender: ")
                if x == 3:
                    self.clientInfoBox.insert("end", "Date of Birth: ")
                if x == 4:
                    self.clientInfoBox.insert("end", "Date of Sample: ")
                if x == 5:
                    self.clientInfoBox.insert("end", "Examiner Name: ")
                if x == 6:
                    self.clientInfoBox.insert("end", "Sampling Context: ")

                self.clientInfoBox.insert("end", self.infoArray[x] + "\n")
        #self.clientInfoBox.configure(state='disabled')

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
        #self.transcriptionBox.configure(state='normal')
        self.transcriptionBox.insert("end", transcribedAudio + "\n")

        self.transcriptionText = transcribedAudio
        self.transcriptionBox.configure(state='disabled')


    # Adds conventions to text from transcription box and puts output in conventionBox box
    def inflectionalMorphemes(self):
        #self.conventionBox.configure(state='normal')
        converting = self.conventionBox.get("1.0", "end")
        # My name is Jake. My name are Jake. (this is a relic of debugging, DO NOT DELETE)
        converting = addConventions.addInflectionalMorphemes(converting)
        self.conventionBox.delete('1.0', "end")
        self.conventionBox.insert("end", converting)
        #self.conventionBox.configure(state='disabled')

    # Sends individual sentences to addWordLevelErrors to check for correction, if there is a corrected version, add squiggles
    def grammarCheck(self):
        self.tokenizedSentences = []
        # Flag for if user wants to manually submit each sentence
        self.checkAllSentences = False
        # Configuring right-hand box, correction box, and submit button
        self.conventionBox.grid(row=5, column=4, columnspan=3)
        self.conventionBox.delete('1.0', "end")
        self.editConventionBoxButton.grid(row=7, column=5)
        self.clearConventionBoxButton.grid(row=7, column=6)
        self.correctionEntryBox.grid(row=6, column=4, columnspan=2)
        self.correctionEntryBox.delete('1.0', "end")
        self.submitCorrectionButton.grid(row=6, column=6)
        # Get raw transcription and tokenize into sentences for processing
        text = self.transcriptionText 
        # perhaps above and below is the state he was talking about, but it already gets assigned to a variable called 'text'
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
                #self.conventionBox.configure(state='normal')
                self.conventionBox.insert("end", self.tokenizedSentences[0] + "\n")
                #self.conventionBox.configure(state='disabled')
                del self.tokenizedSentences[0]

    def applyCorrection(self):
        # Append sentence in correctionEntryBox to right-hand box
        #self.conventionBox.configure(state='normal')
        self.conventionBox.insert("end", self.correctionEntryBox.get("1.0", "end"))
       # self.conventionBox.configure(state='disabled')
        # Remove previously worked-on sentence
        self.correctionEntryBox.delete('1.0', "end")
        # Queue up the next correction for the user
        self.getNextCorrection()

    def toggleClientInfoBox(self):
        if self.infoIsVisible:
            self.clientInfoBox.grid_remove()
        else:
            self.clientInfoBox.grid(row=5, column=0)
        self.infoIsVisible = not self.infoIsVisible

    def toggleTranscriptionBox(self):
        if self.transcriptionIsVisible:
            self.transcriptionBox.grid_remove()
        else:
            self.transcriptionBox.grid(row=5, column=1, columnspan=3, padx=10, pady=10)
        self.transcriptionIsVisible = not self.transcriptionIsVisible 

    def editTranscriptionBox(self):
        if self.editTranscriptionBoxButton.cget("text") == 'Lock':
            self.editTranscriptionBoxButton.configure(text = 'Unlock')
            self.transcriptionBox.configure(state='disabled')

        else:
            self.editTranscriptionBoxButton.configure(text = 'Lock')
            self.transcriptionBox.configure(state='normal')
            
    def editConventionBox(self):
        if self.editConventionBoxButton.cget("text") ==  'Lock':
            self.editConventionBoxButton.configure(text = 'Unlock')
            self.conventionBox.configure(state='disabled')

        else:
            self.editConventionBoxButton.configure(text = 'Lock')
            self.conventionBox.configure(state='normal')

    def clearTranscriptionBox(self):
        if self.editTranscriptionBoxButton.cget("text") == 'Lock':
            self.transcriptionBox.delete('0.0', "end")
        else:
            #self.transcriptionBox.configure(state='normal')
            self.transcriptionBox.delete('0.0', "end")
            #self.transcriptionBox.configure(state='disabled')

    def clearConventionBox(self):
        if self.editConventionBoxButton.cget("text") == 'Lock':
            self.conventionBox.delete('0.0', "end")
        else:
            #self.conventionBox.configure(state='normal')
            self.conventionBox.delete('0.0', "end")
            #self.conventionBox.configure(state='disabled')

    def exportToWord(self):
        outputPath = filedialog.askdirectory()
        exportDocument = Document()
        text = self.transcriptionText
        exportDocument.add_paragraph(text)
        exportDocument.save(outputPath + '/' + str(date.today())+'_SALT_Transcription.docx')      


    def __init__(self):
        #customtkinter.set_ctk_parent_class(tkinterDnd.tk)
        
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.WIDTH = 1280
        self.HEIGHT = 720

        self.master = customtkinter.CTk()
        self.master.title('Speech Transcription')
        self.master.geometry(str(self.WIDTH) + 'x' + str(self.HEIGHT))

        #self.recorder = Record(self.master)
        self.CHUNK = CHUNK
        self.FORMAT = FORMAT
        self.CHANNELS = CHANNELS
        self.RATE = RATE
        self.p = p

        self.frames = []
        self.isRecording = False
        self.playing = False
        self.audioExists = False
        self.paused = True
        self.stream = self.p.open(format = self.FORMAT,
                                channels = self.CHANNELS,
                                rate = self.RATE,
                                input = True,
                                frames_per_buffer = self.CHUNK)

        self.name = ''
        self.age = ''
        self.gender = ''
        self.dateOfBirth = ''
        self.dateOfSample = ''
        self.examinerName = ''
        self.samplingContext = ''
        self.infoArray = ['','','','','','','']
        self.transcriptionText = ''


        uploadButton = customtkinter.CTkButton(self.master, text='Upload', command=lambda: self.uploadAudio())
        uploadButton.grid(row=0, column=0, padx=2, pady=2)
        self.recordButton = customtkinter.CTkButton(self.master, text='Record', command=lambda: self.recordAudio())
        self.recordButton.grid(row=0, column=1, padx=2, pady=2)

        self.audioPlaceholder = customtkinter.CTkLabel(self.master, text='(This is where the audio would be)')
        self.audioPlaceholder.grid(row=0, column=2, padx=2, pady=2)

        self.pauseButton = customtkinter.CTkButton(self.master, text='Pause', command=lambda: self.pause_playback())
        self.pauseButton.grid(row=0, column=4, padx=2, pady=2)
        
        self.playButton = customtkinter.CTkButton(self.master, text='Play', command=lambda: self.playback_click())
        self.playButton.grid(row=0, column=3, padx=2, pady=2)

        downloadButton = customtkinter.CTkButton(self.master, text='Download', command=lambda: self.download_recorded_audio())
        downloadButton.grid(row=1, column=5, padx=2, pady=2)

        transcribeButton = customtkinter.CTkButton(self.master, text='Transcribe', command=self.transcribe)
        transcribeButton.grid(row=0, column=5, padx=2, pady=2)

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
        self.clicked = customtkinter.StringVar()
        self.clicked.set("Name")
        infoDropdown = customtkinter.CTkOptionMenu(self.master, variable = self.clicked, values = clientOptions)
        infoDropdown.grid(row=1, column=1, padx=2, pady=2)
        self.infoEntryBox = customtkinter.CTkEntry(self.master)
        self.infoEntryBox.grid(row=1, column=2, padx=2, pady=2)
        infoSubmitButton = customtkinter.CTkButton(self.master, text="Submit", command=self.submitClientInfo)
        infoSubmitButton.grid(row=1, column=3, padx=2, pady=2)


        # LARGE BOXES AND RELATED BUTTONS
        
        # Client Information Box on the far left
        #self.clientInfoBox = customtkinter.CTkScrollableFrame(self.master, width = 100, height = 20)
        self.clientInfoBox = customtkinter.CTkTextbox(self.master, width = self.WIDTH / 5, height = self.HEIGHT / 2)
        #self.clientInfoBox.configure(state= 'disabled')
        self.clientInfoBox.grid(row=5, column=0, padx=10, pady=10)

        # Show/hide button for the box 
        self.infoIsVisible = True
        self.toggleClientInfoBoxButton = customtkinter.CTkButton(self.master, text='Toggle Table', command=self.toggleClientInfoBox)
        self.toggleClientInfoBoxButton.grid(row=6, column=0, padx=2, pady=2)

        # transcriptionBox is the left-hand box used for editing speech-recognized text
        #self.transcriptionBox = customtkinter.CTkScrollableFrame(self.master, width = 50, height = 20)
        self.transcriptionBox = customtkinter.CTkTextbox(self.master, width = self.WIDTH / 4, height = self.HEIGHT / 2)
        #self.transcriptionBox.configure(state='disabled', wrap=WORD)
        self.transcriptionBox.grid(row=5, column=1, columnspan=3, padx=10, pady=10)

        # Show/hide button for the box
        self.transcriptionIsVisible = True
        self.toggleTranscriptionBoxButton = customtkinter.CTkButton(self.master, text='Toggle Table', command=self.toggleTranscriptionBox)
        self.toggleTranscriptionBoxButton.grid(row=6, column=3, padx=2, pady=2)

        # Permits user to type in transcriptionBox
        self.editTranscriptionBoxButton = customtkinter.CTkButton(self.master, text='Unlock', command=self.editTranscriptionBox)
        self.editTranscriptionBoxButton.grid(row=6, column=1, padx=10, pady=10)
        # Clears transcriptionBox
        self.clearTranscriptionBoxButton = customtkinter.CTkButton(self.master, text='Clear', command=self.clearTranscriptionBox)
        self.clearTranscriptionBoxButton.grid(row=6, column=2, padx=10, pady=10)

        # conventionBox is the right-hand box used for adding all types of conventions
        self.conventionBox = customtkinter.CTkTextbox(self.master, width = self.WIDTH / 4, height = self.HEIGHT / 2)
        # self.conventionBox.configure(state='disabled', wrap=WORD)
        # Permits user to type in conventionBox
        self.editConventionBoxButton = customtkinter.CTkButton(self.master, text='Unlock', command=self.editConventionBox)
        # Clears conventionBox
        self.clearConventionBoxButton = customtkinter.CTkButton(self.master, text='Clear', command=self.clearConventionBox)


        # CONVENTION-RELATED BUTTONS/BOXES

        # Initiates grammarCheck process on text in transcriptionBox
        self.grammarCheckButton = customtkinter.CTkButton(self.master, text='Grammar Check', command=self.grammarCheck)
        self.grammarCheckButton.grid(row=7, column=2, padx=5, pady=2)
        # Manually edit sentences caught during grammarCheck process
        self.correctionEntryBox = customtkinter.CTkTextbox(self.master, width = self.WIDTH / 5, height = self.HEIGHT / 8) 
        #self.correctionEntryBox.configure(wrap=WORD)
        # Appends sentence within correctionEntryBox to right-hand box, continues grammarCheck process
        self.submitCorrectionButton = customtkinter.CTkButton(self.master, text='Submit', command=self.applyCorrection)
        # Applies inflectional morphemes to text in right-hand box
        self.addMorphemesButton = customtkinter.CTkButton(self.master, text='Add Morphemes', command=self.inflectionalMorphemes)
        self.addMorphemesButton.grid(row=7, column=3, padx=2, pady=2)


        # EXPORT-RELATED

        # Exports to word
        exportButton = customtkinter.CTkButton(self.master, text='Export to Word Document', command=self.exportToWord)
        exportButton.grid(row=8, column=5, padx=2, pady=2)
        # Prints
        printButton = customtkinter.CTkButton(self.master, text='Print')
        printButton.grid(row=9, column=5, padx=2, pady=2)


        self.master.mainloop()

if __name__ == "__main__":
    myGui = GUI()
