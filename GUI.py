from functions import diarizationAndTranscription
from audio import AudioManager
from client_info import ClientInfo
from grammar import GrammarChecker
from export import Exporter
import threading
import customtkinter
import matplotlib.pyplot as plt

# Plots the waveform of audio
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
        self.master.title("Speech Transcription")
        self.master.geometry(str(self.WIDTH) + "x" + str(self.HEIGHT))
        
        self.audio = AudioManager(self.master)
        self.clientInfo = ClientInfo()
        self.grammar = GrammarChecker()
        self.exporter = Exporter()

        self.audioPlaceholder = customtkinter.CTkLabel(self.master, text="")
        self.audioPlaceholder.grid(row=0, column=2, padx=2, pady=2)

        # Buttons for managing audio
        self.createButton("Upload", 0, 0, self.uploadAudio)
        self.recordButton = self.createButton("Record", 0, 1, self.recordAudio)
        self.playButton = self.createButton("Play", 0, 3, self.playbackClick)
        self.pauseButton = self.createButton("Pause", 0, 4, self.pausePlayback)
        self.createButton("Download", 1, 5, self.downloadRecordedAudio)

        # Allows user to select a sampling attribute, type the relevant information, and submit it
        self.clicked = customtkinter.StringVar()
        self.clicked.set("Name")
        infoDropdown = customtkinter.CTkOptionMenu(self.master, variable = self.clicked, values = self.clientInfo.clientOptions)
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
    
    # Creates button to be displayed
    def createButton(self, text: str, row: int, column: int, command = None, padx = 2, pady = 2):
        button = customtkinter.CTkButton(self.master, text = text, command = command)
        if row is not None and column is not None:
            button.grid(row = row, column = column, padx = padx, pady = pady)
        return button
    
    # Record audio
    def recordAudio(self):
        if self.recordButton.cget("text") == "Record":
            self.recordButton.configure(text = "Stop")
            print("*Recording*")
            self.audio.record()
        else:
            self.recordButton.configure(text = "Record")
            filename, time, signal = self.audio.stop()
            self.audioPlaceholder.configure(text=filename)
            plotAudio(time, signal)
            print("*Recording stopped*")
    
    # Play the selected audio
    def playAudio(self):
        self.audio.play()
        self.playButton.configure(text = "Play")
    
    # Pause the audio that is currently playing
    def pausePlayback(self):
        paused = self.audio.pause()
        labelText = "Unpause" if paused else "Pause"
        self.pauseButton.configure(text=labelText)
        
    # Creates thread that executes the playAudio function
    def playbackClick(self):
        if not self.audio.playing:
            threading.Thread(target = self.playAudio).start()
            self.playButton.configure(text = "Stop")
        else:
            self.audio.playing = False
            self.playButton.configure(text = "Play")

    # Download file of recorded audio
    def downloadRecordedAudio(self):
        print("Downloading audio")
        download_file = customtkinter.filedialog.asksaveasfile(defaultextension = ".wav", filetypes = [("Wave File", ".wav"), ("All Files", ".*")], initialfile = "downloaded_audio.wav")
        self.audio.saveAudioFile(download_file.name)

    # Upload user's audio file
    def uploadAudio(self):
        filename = customtkinter.filedialog.askopenfilename()
        print("File uploaded: ", filename)
        time, signal = self.audio.upload(filename)
        plotAudio(time, signal)
        self.audioPlaceholder.configure(text=filename)

    # Sends client info submitted by user to the transciption box
    def submitClientInfo(self):
        self.clientInfo.submitInfo(self.infoEntryBox.get(), self.clicked.get())
        self.infoEntryBox.delete(0, "end")
        self.clientInfoBox.delete("1.0", "end")
        self.clientInfoBox.insert("end", str(self.clientInfo))

    # Transcribes audio, then prints to the transcription box
    def transcribe(self):
        my_progress = customtkinter.CTkProgressBar(self.master,  width = 300, mode = "indeterminate") #creates intederminate progress bar
        my_progress.grid(row=3, column=3, padx=2, pady=2)
        my_progress.start()

        filename = self.audio.normalizeUploadedFile()        
        transcribedAudio = diarizationAndTranscription.transcribe(filename)

        self.transcriptionBox.configure(state="normal")
        self.transcriptionBox.insert("end", transcribedAudio + "\n")
        self.transcriptionText = transcribedAudio
        self.transcriptionBox.configure(state="disabled")
        my_progress.stop()
        my_progress.grid_remove() 
        
    # Creates thread that executes the transcribe function
    def transcriptionThread(self):
        threading.Thread(target = self.transcribe).start()

    # Adds conventions to text from transcription box and puts output in conventionBox box
    def inflectionalMorphemes(self):
        converting = self.grammar.getInflectionalMorphemes(self.conventionBox.get("1.0", "end"))
        self.conventionBox.delete("1.0", "end")
        self.conventionBox.insert("end", converting)
        self.conventionBox.configure(state="disabled")

    # Sends individual sentences to addWordLevelErrors to check for correction, if there is a corrected version, add squiggles
    def grammarCheck(self):
        self.conventionBox.grid(row=5, column=4, columnspan=3)
        self.conventionBox.delete("1.0", "end")
        self.editConventionBoxButton.grid(row=7, column=5)
        self.clearConventionBoxButton.grid(row=7, column=6)
        self.correctionEntryBox.grid(row=6, column=4, columnspan=2)
        self.correctionEntryBox.delete("1.0", "end")
        self.submitCorrectionButton.grid(row=6, column=6)
        
        self.grammar.checkGrammar(self.transcriptionText, False)
        self.manageGrammarCorrection()
        
    # Apply's the user's grammar correction
    def applyCorrection(self):
        self.conventionBox.insert("end", self.correctionEntryBox.get("1.0", "end"))
        self.correctionEntryBox.delete("1.0", "end")
        self.manageGrammarCorrection()
        
    def manageGrammarCorrection(self):
        corrected, sentenceToCorrect = self.grammar.getNextCorrection()
        if corrected: self.conventionBox.insert("end", corrected)
        if sentenceToCorrect: self.correctionEntryBox.insert("end", sentenceToCorrect)

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
        self.toggleLockButton(self.editTranscriptionBoxButton, self.transcriptionBox)
            
    def editConventionBox(self):
        self.toggleLockButton(self.editConventionBoxButton, self.conventionBox)

    def clearTranscriptionBox(self):
        self.clearTextbox(self.editTranscriptionBoxButton, self.transcriptionBox)

    def clearConventionBox(self):
        self.clearTextbox(self.editConventionBoxButton, self.conventionBox)
            
    def toggleLockButton(self, button: customtkinter.CTkButton, textbox: customtkinter.CTkTextbox):
        if button.cget("text") == "Lock":
            button.configure(text = "Unlock")
            textbox.configure(state = "disabled")
        else:
            button.configure(text = "Lock")
            textbox.configure(state = "normal")
            
    def clearTextbox(self, button: customtkinter.CTkButton, textbox: customtkinter.CTkTextbox):
        # textbox.configure(state = "normal") if button.cget("text") == "Lock"
        textbox.delete("0.0", "end")
        # textbox.configure(state = "disabled") if button.cget("text") == "Lock"

    def exportToWord(self):
        outputPath = customtkinter.filedialog.askdirectory()
        self.exporter.exportToWord(self.transcriptionText, outputPath)

if __name__ == "__main__":
    myGui = GUI()
