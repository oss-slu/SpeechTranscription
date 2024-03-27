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

WIDTH = 1340
HEIGHT = 740

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
        newButton = customtkinter.CTkButton(self.userFrame.audioTabs, text=dialog.get_input(), command = lambda x=self.currentAudioNum: self.changeAudioWindow(x))
        self.audioButtonList.append(newButton)
        newButton.grid(row=self.audioButtonList.index(newButton), padx=10, pady=10, sticky=E+W)
        
        self.changeAudioWindow(self.currentAudioNum)
        self.currentAudioNum += 1

    def changeAudioWindow(self, num):
        print("Changing Audio to #" + str(num))
        for i, frame in enumerate(self.audioMenuList):
            if i == num: 
                self.audioFrame = frame
                frame.grid(row=0, column=1, padx=5)
            else:
                frame.grid()
                frame.grid_remove()
        for i, button in enumerate(self.audioButtonList):
            if i == num: button.configure(fg_color="#029CFF")
            else: button.configure(fg_color="#0062B1")
        self.tkraise(self.audioFrame)

    def __init__(self):
        super().__init__()

        self.currentAudioNum = 0
        self.audioButtonList = []
        self.audioMenuList = []

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

        self.audioTabs = customtkinter.CTkScrollableFrame(self, height=465)
        self.audioTabs.grid(row=2, rowspan=8, columnspan=2, pady=5, padx=10, sticky=N+E+S+W)

        customtkinter.CTkLabel(self, text="Theme").grid(row=10, column=0, padx=10, pady=5, sticky=N+E+S+W)

        self.themeSetting = customtkinter.CTkOptionMenu(self, values=["Dark", "Light", "System"], command=self.changeTheme)
        self.themeSetting.grid(row=10, column=1, padx=10, pady=5, sticky=N+E+S+W)
        
    def changeTheme(self, theme: str):
        customtkinter.set_appearance_mode(theme.lower())

class sessionInfoMenu(customtkinter.CTkTabview):
    def __init__(self, master, transcriptionBox: CTkTextbox, grammarBox: CTkTextbox):
        super().__init__(master)
        self.configure(height=200)
        self.add("Client Information")
        self.add("Examiner Information")
        self.add("Tables")
        
        self.transcriptionBox = transcriptionBox
        self.grammarBox = grammarBox

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

        self.lockTranscription = customtkinter.StringVar(value="on")
        self.lockTranscriptionBox = customtkinter.CTkSwitch(self.tab("Tables"), text="Lock Transcription?", command=self.toggleTranscription, variable=self.lockTranscription, onvalue="on", offvalue="off")
        self.lockTranscriptionBox.grid(row=0, column=0, columnspan=2, padx=10, pady=12, sticky=E+W)

        self.lockGrammar = customtkinter.StringVar(value="on")
        self.lockGrammarBox = customtkinter.CTkSwitch(self.tab("Tables"), text="Lock Grammar Check?", command=self.toggleGrammar, variable=self.lockGrammar, onvalue="on", offvalue="off")
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
    
    def toggleTranscription(self):
        if self.isTranscriptionLocked(): lockItem(self.transcriptionBox)
        else: unlockItem(self.transcriptionBox)
        
    def toggleGrammar(self):
        if self.isGrammarLocked(): lockItem(self.grammarBox)
        else: unlockItem(self.grammarBox)

class audioMenu(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width = WIDTH * .8)
        self.configure(height=HEIGHT)
        
        self.audio = AudioManager(master)
        self.grammar = GrammarChecker()
        self.exporter = Exporter()
        
        createButton(self, "Upload", 1, 0, self.uploadAudio, lock=False)
        self.recordButton = createButton(self, "Record", 1, 1, self.recordAudio, lock=False)
        self.transcribeButton = createButton(self, "Transcribe", 3, 0, self.transcriptionThread, 15, 15, 2, 100, ("Arial", 40))
        self.downloadAudioButton = createButton(self, "Download Audio", 4, 0, self.downloadRecordedAudio)
        self.exportButton = createButton(self, "Export to Word", 4, 1, self.exportToWord)
        self.grammarButton = createButton(self, "Grammar Check", 4, 2, self.grammarCheckThread)
        self.morphemesButton = createButton(self, "Add Morphemes", 4, 3, self.inflectionalMorphemes)
        self.submitGrammarButton = createButton(self, "Submit", 4, 5, self.applyCorrection, 5)

        self.audioPlayback = customtkinter.CTkLabel(self, text="Audio Playback Area", height=175, fg_color="Red", font=("Arial", 30))
        self.audioPlayback.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=W+E)

        self.transcriptionBox = customtkinter.CTkTextbox(self, width=300)
        self.transcriptionBox.grid(row=0, column=2, columnspan=2, rowspan=4, padx=10, pady= 10, sticky=N+E+S+W)
        self.transcriptionBox.insert("0.0", text="Transcription Box")
        lockItem(self.transcriptionBox)

        self.conventionBox = customtkinter.CTkTextbox(self, width=300)
        self.conventionBox.grid(row=0, column=4, columnspan=2, rowspan=4, padx=10, pady=10, sticky=N+E+S+W)
        self.conventionBox.insert("0.0", text="Grammar Box")
        lockItem(self.conventionBox)

        self.correctionEntryBox = customtkinter.CTkTextbox(self, height=60)
        self.correctionEntryBox.grid(row=4,column=4, padx=10, sticky=E+W)
        lockItem(self.correctionEntryBox)

        self.infoTab = sessionInfoMenu(self, self.transcriptionBox, self.conventionBox)
        self.infoTab.grid(row=0, column=0, columnspan=2, padx=15, pady=15)
        
        self.progressBar = customtkinter.CTkProgressBar(self, width = 500, mode = "indeterminate")
        
        self.grammarCheckPerformed = False
        
    def startProgressBar(self):
        self.progressBar.grid(row=5, column=0, columnspan=6, padx=2, pady=2)
        self.progressBar.start()
    
    def stopProgressBar(self):
        self.progressBar.stop()
        self.progressBar.grid_remove()
        
    def uploadAudio(self):
        '''Upload user's audio file'''
        filename = customtkinter.filedialog.askopenfilename()
        if filename:
            print("File uploaded: ", filename)
            unlockItem(self.transcribeButton)
            unlockItem(self.downloadAudioButton)
            time, signal = self.audio.upload(filename)
            plotAudio(time, signal)
            # self.audioPlaceholder.configure(text=filename)
            self.audioLength = self.audio.getAudioDuration(filename)
            # self.updateSlider()
        
    def recordAudio(self):
        '''Record a custom audio file'''
        if self.recordButton.cget("text") == "Record":
            self.recordButton.configure(text = "Stop")
            self.audio.record()
        else:
            self.recordButton.configure(text = "Record")
            unlockItem(self.transcribeButton)
            unlockItem(self.downloadAudioButton)
            filename, time, signal = self.audio.stop()
            plotAudio(time, signal)
            
    def transcribe(self):
        '''Transcribes audio, then prints to the transcription box'''
        self.startProgressBar()
        filename = self.audio.normalizeUploadedFile()        
        transcribedAudio = diarizationAndTranscription.transcribe(filename)

        self.transcriptionBox.configure(state="normal")
        unlockItem(self.transcriptionBox)
        self.transcriptionBox.delete("0.0", "end")
        self.transcriptionBox.insert("end", transcribedAudio + "\n")
        if self.infoTab.isTranscriptionLocked(): lockItem(self.transcriptionBox)
        unlockItem(self.grammarButton)
        unlockItem(self.exportButton)
        self.stopProgressBar()
        
    def transcriptionThread(self):
        '''Creates thread that executes the transcribe function'''
        threading.Thread(target = self.transcribe).start()
        
    def downloadRecordedAudio(self):
        '''Download file of recorded audio'''
        downloadFile = customtkinter.filedialog.asksaveasfile(defaultextension = ".wav", filetypes = [("Wave File", ".wav"), ("All Files", ".*")], initialfile = "downloaded_audio.wav")
        if downloadFile: self.audio.saveAudioFile(downloadFile.name)
        
    def exportToWord(self):
        '''Exports the transcription to a Word document'''
        downloadFile = customtkinter.filedialog.asksaveasfile(defaultextension = ".docx", filetypes = [("Word Document", ".docx"), ("All Files", ".*")], initialfile = self.exporter.getDefaultFilename() + ".docx")
        if downloadFile:
            text = self.getTranscriptionText()
            if self.grammarCheckPerformed: text = self.getGrammarText()
            self.exporter.exportToWord(text, downloadFile.name)
        
    def grammarCheck(self):
        '''Starts the grammar checking process'''
        self.startProgressBar()
        lockItem(self.exportButton)
        unlockItem(self.conventionBox)
        unlockItem(self.correctionEntryBox)
        unlockItem(self.submitGrammarButton)
        self.conventionBox.delete("1.0", "end")
        self.correctionEntryBox.delete("1.0", "end")
        self.grammar.checkGrammar(self.getTranscriptionText(), False)
        self.manageGrammarCorrection()
        self.stopProgressBar()
        
    def grammarCheckThread(self):
        '''Creates thread that executes the grammarCheck function'''
        threading.Thread(target = self.grammarCheck).start()
        
    def applyCorrection(self):
        '''Apply's the user's grammar correction'''
        unlockItem(self.conventionBox)
        self.conventionBox.insert("end", self.correctionEntryBox.get("1.0", "end"))
        self.correctionEntryBox.delete("1.0", "end")
        self.manageGrammarCorrection()
        
    def manageGrammarCorrection(self):
        '''Get the next grammar correction item'''
        corrected, sentenceToCorrect = self.grammar.getNextCorrection()
        if corrected: self.conventionBox.insert("end", corrected)
        if sentenceToCorrect: self.correctionEntryBox.insert("end", sentenceToCorrect)
        else:
            unlockItem(self.morphemesButton)
            unlockItem(self.exportButton)
            lockItem(self.correctionEntryBox)
            lockItem(self.submitGrammarButton)
            self.grammarCheckPerformed = True
        if self.infoTab.isGrammarLocked(): lockItem(self.conventionBox)
        
    def inflectionalMorphemes(self):
        '''Adds conventions to text from transcription box and puts output in conventionBox box'''
        unlockItem(self.conventionBox)
        converting = self.grammar.getInflectionalMorphemes(self.conventionBox.get("1.0", "end"))
        self.conventionBox.delete("1.0", "end")
        self.conventionBox.insert("end", converting)
        if self.infoTab.isGrammarLocked(): lockItem(self.conventionBox)
        lockItem(self.morphemesButton)
        
    def getTranscriptionText(self):
        return self.transcriptionBox.get('1.0', "end")
    
    def getGrammarText(self):
        return self.conventionBox.get('1.0', "end")

def createButton(master, text: str, row: int, column: int, command = None, padx = 10, pady = 10, columnspan = 1, height = 60, font = ("Arial", 14), lock=True):
    '''Creates button to be displayed'''
    button = customtkinter.CTkButton(master, text = text, height = height, command = command, font = font)
    if row is not None and column is not None:
        button.grid(row = row, column = column, columnspan = columnspan, padx = padx, pady = pady, sticky=W+E)
    if lock: lockItem(button)
    return button

def unlockItem(item: CTkTextbox | CTkButton):
    '''Unlock a CustomTkinter item'''
    item.configure(state="normal")
        
def lockItem(item: CTkTextbox | CTkButton):
    '''Lock a CustomTkinter item'''
    item.configure(state="disabled")

gui = mainGUI()
