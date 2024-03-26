import customtkinter
from customtkinter import *
from tkinter import *
from functions import diarizationAndTranscription
from audio import AudioManager
from client_info import ClientInfo
from grammar import GrammarChecker
from export import Exporter
import threading
import matplotlib.pyplot as plt

WIDTH = 1380
HEIGHT = 720

# Plots the waveform of audio
def plotAudio(time, signal):
    plt.figure(1)
    plt.title("Audio Wave")
    plt.xlabel("Time")
    plt.plot(time, signal)
    plt.show()

class mainGUI(customtkinter.CTk):
    def new_audio(self):
        dialog = customtkinter.CTkInputDialog(text="Enter Name of Session", title="New Audio")
        self.audioMenuList.append(audioMenu(self))
        newButton = customtkinter.CTkButton(self.userFrame.audioTabs, text=dialog.get_input(), command=self.changeAudioWindow(self.currentAudioNum))
        self.audioButtonList.append(newButton)
        newButton.grid(row=self.audioButtonList.index(newButton), padx=10, pady=10, sticky=E+W)
        
        print(self.audioMenuList)
        self.currentAudioNum += 1

    def changeAudioWindow(self, num):
        print("Changing Audio to #" + str(num))
        self.audioFrame = self.audioMenuList[num]
        self.audioFrame.grid(row=0, column=1,padx=5)
        self.tkraise(self.audioFrame)

    def __init__(self):
        super().__init__()

        self.currentAudioNum = 0
        self.audioButtonList = []
        self.audioMenuList = []

        #DEFAULT VALUES AND PAGE SETUP
        self.title('Speech Transcription')
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        customtkinter.deactivate_automatic_dpi_awareness()
        self.resizable(False, False)

        self.geometry(str(WIDTH) + 'x' + str(HEIGHT))

        self.userFrame = userMenu(master=self)
        self.userFrame.grid(row=0, column=0, padx = 1, sticky=NW)

        self.newAudioButton = customtkinter.CTkButton(self.userFrame, text="New Audio", height=60, command=self.new_audio)
        self.newAudioButton.grid(row=1, columnspan=2, padx=10, sticky=N+E+S+W)

        self.audioFrame = customtkinter.CTkFrame(self)

        self.mainloop()

class userMenu(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width = WIDTH / 5)
        self.configure(height = HEIGHT)

        self.label = customtkinter.CTkLabel(master=self, text="Speech Transcription", height=75, font=("Arial", 26))
        self.label.grid(row=0, columnspan=2, padx=10, pady=10, sticky=N+E+S+W)

        # self.newAudioButton = customtkinter.CTkButton(self, text="New Audio", height=60, command=master.new_audio)
        # self.newAudioButton.grid(row=1, columnspan=2, padx=10, sticky=N+E+S+W)

        self.audioTabs = customtkinter.CTkScrollableFrame(self, height=465)
        self.audioTabs.grid(row=2, rowspan=8, columnspan=2, pady=5, padx=10, sticky=N+E+S+W)

        self.themelabel = customtkinter.CTkLabel(self, text="Theme")
        self.themelabel.grid(row=10, column=0, padx=10, pady=5, sticky=N+E+S+W)

        self.resolutionLabel = customtkinter.CTkLabel(self, text="Resolution")
        self.resolutionLabel.grid(row=11, column=0, padx=10, pady=5, sticky=N+E+S+W)

        self.themeSetting = customtkinter.CTkOptionMenu(self, values=["Light", "Dark", "System"])
        self.themeSetting.grid(row=10, column=1, padx=10, pady=5, sticky=N+E+S+W)

        self.resolutionSetting = customtkinter.CTkOptionMenu(self, values=["Small", "Medium", "Large"])
        self.resolutionSetting.grid(row=11, column=1, padx=10, pady=5, sticky=N+E+S+W)

class sessionInfoMenu(customtkinter.CTkTabview):
    def __init__(self, master, transcriptionBox: CTkTextbox, grammarBox: CTkTextbox):
        super().__init__(master)
        self.configure(height=200)
        self.add("Client Information")
        self.add("Examiner Information")
        self.add("Tables")

        # CLIENT INFO TAB [NAME, AGE, GENDER, DATE OF BIRTH]

        self.clientLocked = False

        self.nameBox = customtkinter.CTkEntry(self.tab("Client Information"), placeholder_text="Name")
        self.nameBox.grid(row=0,column=0, padx=10, pady=10, sticky=W+E)

        self.ageBox = customtkinter.CTkEntry(self.tab("Client Information"), placeholder_text="Age")
        self.ageBox.grid(row=0,column=1, padx=10, pady=10, sticky=W+E)

        self.genderBox = customtkinter.CTkEntry(self.tab("Client Information"), placeholder_text="Gender")
        self.genderBox.grid(row=1,column=0, padx=10, pady=10, sticky=W+E)

        self.dobBox = customtkinter.CTkEntry(self.tab("Client Information"), placeholder_text="Date of Birth")
        self.dobBox.grid(row=1,column=1, padx=10, pady=10, sticky=W+E)

        self.saveClientInfo = customtkinter.CTkButton(self.tab("Client Information"), text="Lock", command=self.lockClientInfo)
        self.saveClientInfo.grid(row=2,column=0, padx=10, pady=10, sticky=W+E)

        self.resetClientInfo = customtkinter.CTkButton(self.tab("Client Information"), text="Reset")
        self.resetClientInfo.grid(row=2,column=1, padx=10, pady=10, sticky=W+E)

        # EXAMINER INFO TAB [EXAMINER NAME, DATE OF SAMPLE, SAMPLE CONTEXT]

        self.ExaminerLocked = False

        self.exNameBox = customtkinter.CTkEntry(self.tab("Examiner Information"), placeholder_text="Examiner Name")
        self.exNameBox.grid(row=0,column=0, padx=10, pady=10, sticky=W+E)

        self.dosBox = customtkinter.CTkEntry(self.tab("Examiner Information"), placeholder_text="Date of Sample")
        self.dosBox.grid(row=0,column=1, padx=10, pady=10, sticky=W+E)

        self.contextBox = customtkinter.CTkEntry(self.tab("Examiner Information"), placeholder_text="Sample Context")
        self.contextBox.grid(row=1,column=0, padx=10, pady=10, columnspan=2, sticky=W+E)

        self.saveExaminerInfo = customtkinter.CTkButton(self.tab("Examiner Information"), text="Lock", command=self.lockExaminerInfo)
        self.saveExaminerInfo.grid(row=2,column=0, padx=10, pady=10, sticky=W+E)

        self.resetExaminerInfo = customtkinter.CTkButton(self.tab("Examiner Information"), text="Reset")
        self.resetExaminerInfo.grid(row=2,column=1, padx=10, pady=10, sticky=W+E)

        self.name = self.nameBox.get()
        self.age = self.ageBox.get()
        self.gender = self.genderBox.get()
        self.dateOfBirth = self.dobBox.get()
        self.dateOfSample = self.dosBox.get()
        self.examinerName = self.exNameBox.get()
        self.samplingContext = self.contextBox.get()

        # TABLE TOGGLE BUTTONS/SWITCHES

        self.lockTranscription = customtkinter.StringVar(value="on")
        self.lockTranscriptionBox = customtkinter.CTkSwitch(self.tab("Tables"), text="Lock Transcription?", variable=self.lockTranscription, onvalue="on", offvalue="off")
        self.lockTranscriptionBox.grid(row=0, column=0, columnspan=2, padx=10, pady=12, sticky=E+W)

        self.lockGrammar = customtkinter.StringVar(value="on")
        self.lockGrammarBox = customtkinter.CTkSwitch(self.tab("Tables"), text="Lock Grammar Check?", variable=self.lockGrammar, onvalue="on", offvalue="off")
        self.lockGrammarBox.grid(row=1, column=0, columnspan=2,padx=10, pady=12, sticky=E+W)

        self.clearTranscriptionBox = customtkinter.CTkButton(self.tab("Tables"), text="Clear Transcription")
        self.clearTranscriptionBox.grid(row=2, column=0, padx=10, pady=10, sticky=N+E+S+W)

        self.clearGrammarBox = customtkinter.CTkButton(self.tab("Tables"), text="Clear Grammar Check")
        self.clearGrammarBox.grid(row=2, column=1, padx=10, pady=10, sticky=N+E+S+W)

    def lockClientInfo(self):
        self.name = self.nameBox.get()
        self.age = self.ageBox.get()
        self.gender = self.genderBox.get()
        self.dateOfBirth = self.dobBox.get()

        if self.clientLocked == False:
            self.nameBox.configure(state="disabled")
            self.ageBox.configure(state="disabled")
            self.genderBox.configure(state="disabled")
            self.dobBox.configure(state="disabled")
            self.clientLocked = True
            self.saveClientInfo.configure(text="Unlock")
        else:
            self.nameBox.configure(state="normal")
            self.ageBox.configure(state="normal")
            self.genderBox.configure(state="normal")
            self.dobBox.configure(state="normal")
            self.clientLocked = False
            self.saveClientInfo.configure(text="Lock")

    def lockExaminerInfo(self):
        self.dateOfSample = self.dosBox.get()
        self.examinerName = self.exNameBox.get()
        self.samplingContext = self.contextBox.get()

        if self.clientLocked == False:
            self.exNameBox.configure(state="disabled")
            self.dosBox.configure(state="disabled")
            self.contextBox.configure(state="disabled")
            self.ExaminerLocked = True
            self.saveExaminerInfo.configure(text="Unlock")
        else:
            self.exNameBox.configure(state="normal")
            self.dosBox.configure(state="normal")
            self.contextBox.configure(state="normal")
            self.ExaminerLocked = False
            self.saveExaminerInfo.configure(text="Lock")
            
    def isTranscriptionLocked(self):
        return self.lockTranscription.get() == "on"
    
    def isGrammarLocked(self):
        return self.lockGrammar.get() == "on"

class audioMenu(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width = WIDTH * .8)
        self.configure(height=HEIGHT)
        
        self.audio = AudioManager(master)
        self.grammar = GrammarChecker()
        self.exporter = Exporter()

        # BUTTONS
        
        createButton(self, "Upload", 1, 0, self.uploadAudio)
        self.recordButton = createButton(self, "Record", 1, 1, self.recordAudio)
        createButton(self, "Transcribe", 3, 0, self.transcriptionThread, 15, 15, 2, 100, ("Arial", 40))
        createButton(self, "Download Audio", 4, 0, self.downloadRecordedAudio)
        createButton(self, "Export to Word", 4, 1, self.exportToWord)
        createButton(self, "Grammar Check", 4, 2, self.grammarCheck)
        createButton(self, "Add Morphemes", 4, 3, self.inflectionalMorphemes)
        createButton(self, "Submit", 4, 5, self.applyCorrection, 5)

        self.audioPlayback = customtkinter.CTkLabel(self, text="Audio Playback Area", height=175, fg_color="Red", font=("Arial", 30))
        self.audioPlayback.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=W+E)

        # CLIENT INFORMATION BOX

        self.infoTab = sessionInfoMenu(master=self)
        self.infoTab.grid(row=0, column=0, columnspan=2, padx=15, pady=15)

        # TEXT BOXES AND THEIR RELATED BUTTONS

        # TRANSCRIPTION BOX

        self.transcriptionText = ""
        self.transcriptionBox = customtkinter.CTkTextbox(self, width=300)
        self.transcriptionBox.grid(row=0, column=2, columnspan=2, rowspan=4, padx=10, pady= 10, sticky=N+E+S+W)
        self.transcriptionBox.insert("0.0", text="Transcription Box")
        self.lockBox(self.transcriptionBox)

        # CONVENTION BOX

        self.conventionBox = customtkinter.CTkTextbox(self, width=300)
        self.conventionBox.grid(row=0, column=4, columnspan=2, rowspan=4, padx=10, pady=10, sticky=N+E+S+W)
        self.conventionBox.insert("0.0", text="Grammar Box")
        self.lockBox(self.conventionBox)

        self.correctionEntryBox = customtkinter.CTkTextbox(self, height=60)
        self.correctionEntryBox.grid(row=4,column=4, padx=10, sticky=E+W)  
        
    # Upload user's audio file
    def uploadAudio(self):
        filename = customtkinter.filedialog.askopenfilename()
        print("File uploaded: ", filename)
        time, signal = self.audio.upload(filename)
        plotAudio(time, signal)
        # self.audioPlaceholder.configure(text=filename)
        self.audioLength = self.audio.getAudioDuration(filename)
        # self.updateSlider()
        
    def recordAudio(self):
        if self.recordButton.cget("text") == "Record":
            self.recordButton.configure(text = "Stop")
            print("*Recording*")
            self.audio.record()
        else:
            self.recordButton.configure(text = "Record")
            filename, time, signal = self.audio.stop()
            plotAudio(time, signal)
            print("*Recording stopped*")
            
    # Transcribes audio, then prints to the transcription box
    def transcribe(self):
        # my_progress = customtkinter.CTkProgressBar(self.master,  width = 300, mode = "indeterminate") #creates intederminate progress bar
        # my_progress.grid(row=4, column=0, padx=2, pady=2)
        # my_progress.start()

        filename = self.audio.normalizeUploadedFile()        
        transcribedAudio = diarizationAndTranscription.transcribe(filename)

        self.transcriptionBox.configure(state="normal")
        self.unlockBox(self.transcriptionBox)
        self.transcriptionBox.delete("0.0", "end")
        self.transcriptionBox.insert("end", transcribedAudio + "\n")
        self.transcriptionText = transcribedAudio
        if self.infoTab.isTranscriptionLocked(): self.lockBox(self.transcriptionBox)
        # my_progress.stop()
        # my_progress.grid_remove() 
        
    # Creates thread that executes the transcribe function
    def transcriptionThread(self):
        threading.Thread(target = self.transcribe).start()
        
    # Download file of recorded audio
    def downloadRecordedAudio(self):
        print("Downloading audio")
        download_file = customtkinter.filedialog.asksaveasfile(defaultextension = ".wav", filetypes = [("Wave File", ".wav"), ("All Files", ".*")], initialfile = "downloaded_audio.wav")
        self.audio.saveAudioFile(download_file.name)
        
    def exportToWord(self):
        outputPath = customtkinter.filedialog.askdirectory()
        self.exporter.exportToWord(self.transcriptionText, outputPath)
        
    def grammarCheck(self):
        self.unlockBox(self.conventionBox)
        self.conventionBox.delete("1.0", "end")
        self.correctionEntryBox.delete("1.0", "end")
        self.transcriptionText = self.transcriptionBox.get('1.0', "end")
        self.grammar.checkGrammar(self.transcriptionText, False)
        self.manageGrammarCorrection()
        
    # Apply's the user's grammar correction
    def applyCorrection(self):
        self.unlockBox(self.conventionBox)
        self.conventionBox.insert("end", self.correctionEntryBox.get("1.0", "end"))
        self.correctionEntryBox.delete("1.0", "end")
        self.manageGrammarCorrection()
        
    def manageGrammarCorrection(self):
        corrected, sentenceToCorrect = self.grammar.getNextCorrection()
        if corrected: self.conventionBox.insert("end", corrected)
        if sentenceToCorrect: self.correctionEntryBox.insert("end", sentenceToCorrect)
        if self.infoTab.isGrammarLocked(): self.lockBox(self.conventionBox)
        
    # Adds conventions to text from transcription box and puts output in conventionBox box
    def inflectionalMorphemes(self):
        self.unlockBox(self.conventionBox)
        converting = self.grammar.getInflectionalMorphemes(self.conventionBox.get("1.0", "end"))
        self.conventionBox.delete("1.0", "end")
        self.conventionBox.insert("end", converting)
        if self.infoTab.isGrammarLocked(): self.lockBox(self.conventionBox)
        
    def unlockBox(self, textbox: CTkTextbox):
        textbox.configure(state="normal")
        
    def lockBox(self, textbox: CTkTextbox):
        textbox.configure(state="disabled")

# Creates button to be displayed
def createButton(master, text: str, row: int, column: int, command = None, padx = 10, pady = 10, columnspan = 1, height = 60, font = ("Arial", 14)):
    button = customtkinter.CTkButton(master, text = text, height = height, command = command, font = font)
    if row is not None and column is not None:
        button.grid(row = row, column = column, columnspan = columnspan, padx = padx, pady = pady, sticky=W+E)
    return button

gui = mainGUI()
