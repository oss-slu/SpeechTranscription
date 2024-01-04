from functions import addConventions
from functions import diarizationAndTranscription
from audio import Audio
import nltk
import threading
from docx import Document
from datetime import date
import customtkinter
import matplotlib.pyplot as plt

def plotAudio(time, signal):
    plt.figure(1)
    plt.title("Audio Wave")
    plt.xlabel("Time")
    plt.plot(time, signal)
    plt.show()

class GUI:
    def __init__(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.WIDTH = 1280
        self.HEIGHT = 720

        self.master = customtkinter.CTk()
        self.master.title('Speech Transcription')
        self.master.geometry(str(self.WIDTH) + 'x' + str(self.HEIGHT))
        
        self.audio = Audio(self.master)

        self.audioPlaceholder = customtkinter.CTkLabel(self.master, text='')
        self.audioPlaceholder.grid(row=0, column=2, padx=2, pady=2)

        # Buttons for managing audio
        self.createButton("Upload", 0, 0, self.uploadAudio)
        self.recordButton = self.createButton("Record", 0, 1, self.recordAudio)
        self.playButton = self.createButton("Play", 0, 3, self.playbackClick)
        self.pauseButton = self.createButton("Pause", 0, 4, self.pausePlayback)
        self.createButton("Download", 1, 5, self.downloadRecordedAudio)

        # Allows user to select a sampling attribute, type the relevant information, and submit it
        self.clientOptions = ["Name", "Age", "Gender", "Date of Birth", "Date of Sample", "Examiner Name", "Sampling Context"]
        self.infoArray = ['','','','','','','']
        self.clicked = customtkinter.StringVar()
        self.clicked.set("Name")
        infoDropdown = customtkinter.CTkOptionMenu(self.master, variable = self.clicked, values = self.clientOptions)
        infoDropdown.grid(row=1, column=1, padx=2, pady=2)
        self.infoEntryBox = customtkinter.CTkEntry(self.master)
        self.infoEntryBox.grid(row=1, column=2, padx=2, pady=2)
        self.createButton("Submit", 1, 3, self.submitClientInfo)

        # Client Information Box (left-hand side)
        self.clientInfoBox = customtkinter.CTkTextbox(self.master, width = self.WIDTH / 5, height = self.HEIGHT / 2)
        self.clientInfoBox.grid(row=5, column=0, padx=10, pady=10)
        self.infoIsVisible = True
        self.createButton("Toggle Table", 6, 0, self.toggleClientInfoBox)

        # Transcription Box (middle)
        self.transcriptionText = ""
        self.transcriptionBox = customtkinter.CTkTextbox(self.master, width = self.WIDTH / 4, height = self.HEIGHT / 2)
        self.transcriptionBox.grid(row=5, column=1, columnspan=3, padx=10, pady=10)

        ## Buttons for the transcription
        self.createButton("Transcribe", 0, 5, self.transcriptionThread)
        self.transcriptionIsVisible = True
        self.createButton("Toggle Table", 6, 3, self.toggleTranscriptionBox)
        self.editTranscriptionBoxButton = self.createButton("Unlock", 6, 1, self.editTranscriptionBox, 10, 10)
        self.clearTranscriptionBoxButton = self.createButton("Clear", 6, 2, self.clearTranscriptionBox, 10, 10)

        # Buttons and textbox for conventions
        self.conventionBox = customtkinter.CTkTextbox(self.master, width = self.WIDTH / 4, height = self.HEIGHT / 2)
        self.editConventionBoxButton = self.createButton("Unlock", None, None, self.editConventionBox)
        self.clearConventionBoxButton = self.createButton("Clear", None, None, self.clearConventionBox)

        # Buttons and textbox for grammar checking
        self.correctionEntryBox = customtkinter.CTkTextbox(self.master, width = self.WIDTH / 5, height = self.HEIGHT / 8) 
        self.createButton("Grammar Check", 7, 2, self.grammarCheck, 5)
        self.submitCorrectionButton = self.createButton("Submit", None, None, self.applyCorrection)
        self.createButton("Add Morphemes", 7, 3, self.inflectionalMorphemes)

        # Buttons used to export the transcription
        self.createButton("Export to Word Document", 8, 5, self.exportToWord)
        self.createButton("Print", 9, 5)

        self.master.mainloop()
    
    def createButton(self, text: str, row: int, column: int, command = None, padx = 2, pady = 2):
        button = customtkinter.CTkButton(self.master, text = text, command = command)
        if row is not None and column is not None:
            button.grid(row = row, column = column, padx = padx, pady = pady)
        return button
    
    def recordAudio(self):
        if self.recordButton.cget("text") == 'Record':
            self.recordButton.configure(text = 'Stop')
            print("*Recording*")
            self.audio.record()
        else:
            self.recordButton.configure(text = 'Record')
            filename, time, signal = self.audio.stop()
            self.audioPlaceholder.configure(text=filename)
            plotAudio(time, signal)
            print("*Recording stopped*")
    
    def playAudio(self):
        self.audio.play()
        self.playButton.configure(text = 'Play')
    
    def pausePlayback(self):
        paused = self.audio.pause()
        labelText = "Unpause" if paused else "Pause"
        self.pauseButton.configure(text=labelText)
        
    def playbackClick(self):
        if not self.audio.playing:
            threading.Thread(target = self.playAudio).start()
            self.playButton.configure(text = 'Stop')
        else:
            self.audio.playing = False
            self.playButton.configure(text = 'Play')

    # Download file of recorded audio
    def downloadRecordedAudio(self):
        print('Downloading audio')
        download_file = customtkinter.filedialog.asksaveasfile(defaultextension = '.wav', filetypes = [("Wave File", '.wav'), ("All Files", '.*')], initialfile = "downloaded_audio.wav")
        self.audio.saveAudioFile(download_file.name)

    def uploadAudio(self):
        filename = customtkinter.filedialog.askopenfilename()
        print('File uploaded: ', filename)
        time, signal = self.audio.upload(filename)
        plotAudio(time, signal)
        self.audioPlaceholder.configure(text=filename)

    # Sends client info submitted by user to the transciption box
    def submitClientInfo(self) :
        infoEntryText = self.infoEntryBox.get()
        for i, option in enumerate(self.clientOptions):
            if self.clicked.get() == option:
                self.infoArray[i] = infoEntryText
        self.infoEntryBox.delete(0, "end")

        self.clientInfoBox.delete('1.0', "end")
        for x in range(7):
            if self.infoArray[x] != '':
                infoText = self.clientOptions[x] + ": " + self.infoArray[x] + "\n"
                self.clientInfoBox.insert("end", infoText)

    # Transcribes audio, then prints to the transcription box
    def transcribe(self):
        my_progress = customtkinter.CTkProgressBar(self.master,  width = 300, mode = 'indeterminate') #creates intederminate progress bar
        my_progress.grid(row=3, column=3, padx=2, pady=2)
        my_progress.start()

        filename = self.audio.normalizeUploadedFile()        
        transcribedAudio = diarizationAndTranscription.transcribe(filename)

        self.transcriptionBox.configure(state='normal')
        self.transcriptionBox.insert("end", transcribedAudio + "\n")
        self.transcriptionText = transcribedAudio
        self.transcriptionBox.configure(state='disabled')
        my_progress.stop()
        my_progress.grid_remove() 
        
    # Creates thread that executes the transcribe function
    def transcriptionThread(self):
        th = threading.Thread(target = self.transcribe).start()

    # Adds conventions to text from transcription box and puts output in conventionBox box
    def inflectionalMorphemes(self):
        converting = self.conventionBox.get("1.0", "end")
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
            return
        while (len(self.tokenizedSentences)):
            if ((self.tokenizedSentences[0] != addConventions.correctSentence(self.tokenizedSentences[0])) or self.checkAllSentences):
                self.correctionEntryBox.insert("end", addConventions.correctSentence(self.tokenizedSentences[0]))
                del self.tokenizedSentences[0]
                break
            else:
                self.conventionBox.insert("end", self.tokenizedSentences[0] + "\n")
                del self.tokenizedSentences[0]

    # Apply's the user's grammar correction
    def applyCorrection(self):
        self.conventionBox.insert("end", self.correctionEntryBox.get("1.0", "end"))
        self.correctionEntryBox.delete('1.0', "end")
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
        outputPath = customtkinter.filedialog.askdirectory()
        exportDocument = Document()
        text = self.transcriptionText
        exportDocument.add_paragraph(text)
        exportDocument.save(outputPath + '/' + str(date.today())+'_SALT_Transcription.docx')      


if __name__ == "__main__":
    myGui = GUI()
