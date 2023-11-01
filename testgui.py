import customtkinter
import tkinter
from tkinter import *

WIDTH = 1280
HEIGHT = 720

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
    def __init__(self, master):
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

        self.lockTranscriptionBox = customtkinter.CTkSwitch(self.tab("Tables"), text="Lock Transcription?")
        self.lockTranscriptionBox.grid(row=0, column=0, columnspan=2, padx=10, pady=12, sticky=E+W)

        self.lockTranscriptionBox = customtkinter.CTkSwitch(self.tab("Tables"), text="Lock Grammar Check?")
        self.lockTranscriptionBox.grid(row=1, column=0, columnspan=2,padx=10, pady=12, sticky=E+W)

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

class audioMenu(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width = WIDTH * .8)
        self.configure(height=HEIGHT)

        # BUTTONS

        self.uploadButton = customtkinter.CTkButton(self, text="Upload", height=60)
        self.uploadButton.grid(row=1,column=0, padx=10, pady=10, sticky=W+E)

        self.recordButton = customtkinter.CTkButton(self, text="Record", height=60)
        self.recordButton.grid(row=1,column=1, padx=10, pady=10, sticky=W+E)

        self.audioPlayback = customtkinter.CTkLabel(self, text="Audio Playback Area", height=175, fg_color="Red", font=("Arial", 30))
        self.audioPlayback.grid(row=2,column=0, columnspan=2, padx=10, pady=10, sticky=W+E)

        self.transcribeButton = customtkinter.CTkButton(self, text="Transcribe", height=100, font=("Arial", 40))
        self.transcribeButton.grid(row=3,column=0, columnspan=2, padx=15, pady=15, sticky=W+E)

        self.downloadButton = customtkinter.CTkButton(self, text="Download Audio", height=60)
        self.downloadButton.grid(row=4,column=0, padx=10, pady=10, sticky=W+E)

        self.exportButton = customtkinter.CTkButton(self, text="Export to DOCX", height=60)
        self.exportButton.grid(row=4,column=1, padx=10, pady=10, sticky=W+E)

        self.grammarCheckButton = customtkinter.CTkButton(self, text="Check Grammar", height=60) 
        self.grammarCheckButton.grid(row=4,column=2, padx=10, pady=10, sticky=W+E)

        self.addMorphemesButton = customtkinter.CTkButton(self, text="Add Morphemes", height=60)
        self.addMorphemesButton.grid(row=4,column=3, padx=10, pady=10, sticky=W+E)

        self.submitCorrectionButton = customtkinter.CTkButton(self, text="Submit", width=50, height=60)
        self.submitCorrectionButton.grid(row=4,column=5, padx=5, pady=10)

        # CLIENT INFORMATION BOX

        self.infoTab = sessionInfoMenu(master=self)
        self.infoTab.grid(row=0, column=0, columnspan=2, padx=15, pady=15)

        # TEXT BOXES AND THEIR RELATED BUTTONS

        # TRANSCRIPTION BOX

        self.transcriptionBox = customtkinter.CTkTextbox(self, width=300)
        self.transcriptionBox.grid(row=0,column=2, columnspan=2, rowspan=4, padx=10, pady= 10, sticky=N+E+S+W)
        self.transcriptionBox.insert("0.0", text="Transcription Box")
        self.transcriptionBox.configure(state=DISABLED)


        # CONVENTION BOX

        self.conventionBox = customtkinter.CTkTextbox(self, width=300)
        self.conventionBox.grid(row=0, column=4, columnspan=2, rowspan=4, padx=10, pady=10, sticky=N+E+S+W)
        self.conventionBox.insert("0.0", text="Grammar Box")
        self.conventionBox.configure(state=DISABLED)

        self.correctionEntryBox = customtkinter.CTkTextbox(self, height=60)
        self.correctionEntryBox.grid(row=4,column=4, padx=10, sticky=E+W)  

class playbackMenu(customtkinter.CTkFrame):
    return

gui = mainGUI()