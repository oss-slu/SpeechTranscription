from customtkinter import *
import diarizationAndTranscription
from audio import AudioManager
from client_info import ClientInfo
from grammar import GrammarChecker
from export import Exporter
import threading
import matplotlib.pyplot as plt

WIDTH = 1340
HEIGHT = 800

def plotAudio(time, signal):
    '''Plots the waveform of audio'''
    plt.figure(1)
    plt.title("Audio Wave")
    plt.xlabel("Time")
    plt.plot(time, signal)
    plt.show()

class mainGUI(CTk):
    def new_audio(self):
        dialog = CTkInputDialog(text="Enter Name of Session", title="New Audio")
        session_name = dialog.get_input().strip()  # Get input and strip any whitespace
        if session_name:  # Check if the name is not empty after stripping
            self.audioMenuList.append(audioMenu(self))
            newButton = createButton(self.userFrame.audioTabs, session_name, len(self.audioButtonList), 0, lambda x=self.currentAudioNum: self.changeAudioWindow(x), lock=False)
            self.audioButtonList.append(newButton)
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
        self.audioButtonList: list[CTkButton] = []
        self.audioMenuList: list[audioMenu] = []

        self.title('Speech Transcription')
        set_appearance_mode("dark")
        set_default_color_theme("blue")
        deactivate_automatic_dpi_awareness()
        self.resizable(False, False)

        self.geometry(str(WIDTH) + 'x' + str(HEIGHT))

        self.userFrame = userMenu(master=self)
        self.userFrame.grid(row=0, column=0, padx = 1, sticky=NW)

        self.newAudioButton = createButton(self.userFrame, "New Audio", 1, 0, self.new_audio, columnspan=2, lock=False)

        self.audioFrame = CTkFrame(self)

        self.mainloop()

class userMenu(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width = WIDTH / 5)
        self.configure(height = HEIGHT)

        self.label = CTkLabel(master=self, text="Speech Transcription", height=75, font=("Arial", 26))
        self.label.grid(row=0, columnspan=2, padx=10, pady=10, sticky=N+E+S+W)

        self.audioTabs = CTkScrollableFrame(self, height=465)
        self.audioTabs.grid(row=2, rowspan=8, columnspan=2, pady=5, padx=10, sticky=N+E+S+W)

        CTkLabel(self, text="Theme").grid(row=10, column=0, padx=10, pady=5, sticky=N+E+S+W)

        self.themeSetting = CTkOptionMenu(self, values=["Dark", "Light", "System"], command=self.changeTheme)
        self.themeSetting.grid(row=10, column=1, padx=10, pady=5, sticky=N+E+S+W)
        
    def changeTheme(self, theme: str):
        set_appearance_mode(theme.lower())

class sessionInfoMenu(CTkTabview):
    def __init__(self, master, transcriptionBox: CTkTextbox, grammarBox: CTkTextbox):
        super().__init__(master)
        self.configure(height=200)
        self.add("Client Information")
        self.add("Examiner Information")
        self.add("Tables")
        
        self.transcriptionBox = transcriptionBox
        self.grammarBox = grammarBox

        self.clientLocked = False

        self.nameBox = CTkEntry(self.tab("Client Information"), placeholder_text="Name")
        self.nameBox.grid(row=0,column=0, padx=10, pady=10, sticky=W+E)

        self.ageBox = CTkEntry(self.tab("Client Information"), placeholder_text="Age")
        self.ageBox.grid(row=0,column=1, padx=10, pady=10, sticky=W+E)

        self.genderBox = CTkEntry(self.tab("Client Information"), placeholder_text="Gender")
        self.genderBox.grid(row=1,column=0, padx=10, pady=10, sticky=W+E)

        self.dobBox = CTkEntry(self.tab("Client Information"), placeholder_text="Date of Birth")
        self.dobBox.grid(row=1,column=1, padx=10, pady=10, sticky=W+E)

        self.saveClientInfo = createButton(self.tab("Client Information"), "Lock", 2, 0, self.lockClientInfo, height=28, lock=False)
        self.resetClientInfoButton = createButton(self.tab("Client Information"), "Reset", 2, 1, self.resetClientInfo, height=28, lock=False)

        self.examinerLocked = False

        self.exNameBox = CTkEntry(self.tab("Examiner Information"), placeholder_text="Examiner Name")
        self.exNameBox.grid(row=0,column=0, padx=10, pady=10, sticky=W+E)

        self.dosBox = CTkEntry(self.tab("Examiner Information"), placeholder_text="Date of Sample")
        self.dosBox.grid(row=0,column=1, padx=10, pady=10, sticky=W+E)

        self.contextBox = CTkEntry(self.tab("Examiner Information"), placeholder_text="Sample Context")
        self.contextBox.grid(row=1,column=0, padx=10, pady=10, columnspan=2, sticky=W+E)

        self.saveExaminerInfo = createButton(self.tab("Examiner Information"), "Lock", 2, 0, self.lockExaminerInfo, height=28, lock=False)
        self.resetExaminerInfoButton = createButton(self.tab("Examiner Information"), "Reset", 2, 1, self.resetExaminerInfo, height=28, lock=False)

        self.lockTranscription = StringVar(value="on")
        self.lockTranscriptionBox = CTkSwitch(self.tab("Tables"), text="Lock Transcription?", command=self.toggleTranscription, variable=self.lockTranscription, onvalue="on", offvalue="off")
        self.lockTranscriptionBox.grid(row=0, column=0, columnspan=2, padx=10, pady=12, sticky=E+W)

        self.lockGrammar = StringVar(value="on")
        self.lockGrammarBox = CTkSwitch(self.tab("Tables"), text="Lock Grammar Check?", command=self.toggleGrammar, variable=self.lockGrammar, onvalue="on", offvalue="off")
        self.lockGrammarBox.grid(row=1, column=0, columnspan=2,padx=10, pady=12, sticky=E+W)

        self.clearTranscriptionBox = createButton(self.tab("Tables"), "Clear Transcription", 2, 0, height=28, lock=False)
        self.clearGrammarBox = createButton(self.tab("Tables"), "Clear Grammar Check", 2, 1, height=28, lock=False)

    def lockClientInfo(self):
        if not self.clientLocked:
            lockMultipleItems([self.nameBox, self.ageBox, self.genderBox, self.dobBox])
            self.saveClientInfo.configure(text="Unlock")
        else:
            unlockMultipleItems([self.nameBox, self.ageBox, self.genderBox, self.dobBox])
            self.saveClientInfo.configure(text="Lock")
        self.clientLocked = not self.clientLocked
        
    def resetClientInfo(self):
        if not self.clientLocked:
            for item in [self.nameBox, self.ageBox, self.genderBox, self.dobBox]:
                item.delete("0.0", "end")

    def lockExaminerInfo(self):
        if not self.examinerLocked:
            lockMultipleItems([self.exNameBox, self.dosBox, self.contextBox])
            self.saveExaminerInfo.configure(text="Unlock")
        else:
            unlockMultipleItems([self.exNameBox, self.dosBox, self.contextBox])
            self.saveExaminerInfo.configure(text="Lock")
        self.examinerLocked = not self.examinerLocked
        
    def resetExaminerInfo(self):
        if not self.examinerLocked:
            for item in [self.exNameBox, self.dosBox, self.contextBox]:
                item.delete("0.0", "end")
            
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

class audioMenu(CTkFrame):
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

        self.labelSpeakersButton = createButton(self, "Label Speakers", 5, 0, self.labelSpeakers) # For speaker labeling
        self.applyAliasesButton = createButton(self, "Apply Aliases", 5, 1, self.customizeSpeakerAliases) # For more specific labeling


        self.audioPlayback = CTkLabel(self, text="Audio Playback Area", height=175, fg_color="Red", font=("Arial", 30))
        self.audioPlayback.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=W+E)

        self.transcriptionBox = CTkTextbox(self, width=300)
        self.transcriptionBox.grid(row=0, column=2, columnspan=2, rowspan=4, padx=10, pady= 10, sticky=N+E+S+W)
        self.transcriptionBox.insert("0.0", text="Transcription Box")
        lockItem(self.transcriptionBox)

        self.conventionBox = CTkTextbox(self, width=300)
        self.conventionBox.grid(row=0, column=4, columnspan=2, rowspan=4, padx=10, pady=10, sticky=N+E+S+W)
        self.conventionBox.insert("0.0", text="Grammar Box")
        lockItem(self.conventionBox)

        self.correctionEntryBox = CTkTextbox(self, height=60)
        self.correctionEntryBox.grid(row=4,column=4, padx=10, sticky=E+W)
        lockItem(self.correctionEntryBox)

        self.infoTab = sessionInfoMenu(self, self.transcriptionBox, self.conventionBox)
        self.infoTab.grid(row=0, column=0, columnspan=2, padx=15, pady=15)
        
        self.progressBar = CTkProgressBar(self, width = 500, mode = "indeterminate")
        
        self.grammarCheckPerformed = False
        
    def startProgressBar(self):
        self.progressBar.grid(row=5, column=1, columnspan=6, padx=2, pady=2)
        self.progressBar.start()
    
    def stopProgressBar(self):
        self.progressBar.stop()
        self.progressBar.grid_remove()

    def labelSpeakers(self):
        popup = CTkToplevel(self)
        popup.title("Label Speakers")
        popup.geometry("600x400")  # Adjust size as needed

        scrollable_frame = CTkScrollableFrame(popup)
        scrollable_frame.pack(fill='both', expand=True)

        # Initial split of the transcription text (used to generate checkboxes only)
        initial_segments = self.getTranscriptionText().split('\n')

        # Store checkboxes, associated with the index in the original text
        self.segment_selections = []
        for idx, segment in enumerate(initial_segments):
            if segment.strip():  # Ignore empty lines
                var = IntVar()
                chk = CTkCheckBox(scrollable_frame, text=segment, variable=var)
                chk.pack(anchor='w', padx=5, pady=2)
                self.segment_selections.append((var, idx))

        def apply_labels(speaker):
            # Fetch the current state of the transcription text
            current_text = self.getTranscriptionText()
            current_segments = current_text.split('\n')

            for var, idx in self.segment_selections:
                if var.get() and not current_segments[idx].startswith(f"{speaker}:"):
                    # Append the speaker label only if it's not already labeled
                    current_segments[idx] = f"{speaker}: {current_segments[idx]}"
                    var.set(0)  # Optionally reset the checkbox after labeling

            # Update the transcriptionBox with the modified text
            new_transcription_text = "\n".join(current_segments)
            self.transcriptionBox.delete("0.0", "end")
            self.transcriptionBox.insert("0.0", new_transcription_text)
            unlockItem(self.applyAliasesButton)

        # Buttons for applying speaker labels
        CTkButton(popup, text="Label as Speaker 1", command=lambda: apply_labels("Speaker 1")).pack(side='left', padx=10, pady=10)
        CTkButton(popup, text="Label as Speaker 2", command=lambda: apply_labels("Speaker 2")).pack(side='right', padx=10, pady=10)
    
    def customizeSpeakerAliases(self):
        popup = CTkToplevel(self)
        popup.title("Customize Speaker Aliases")
        popup.geometry("400x200")

        # Entry for Speaker 1 alias
        speaker1_alias_label = CTkLabel(popup, text="Speaker 1 Alias:")
        speaker1_alias_label.pack(pady=(10, 0))
        speaker1_alias_entry = CTkEntry(popup)
        speaker1_alias_entry.pack(pady=(0, 10))

        # Entry for Speaker 2 alias
        speaker2_alias_label = CTkLabel(popup, text="Speaker 2 Alias:")
        speaker2_alias_label.pack(pady=(10, 0))
        speaker2_alias_entry = CTkEntry(popup)
        speaker2_alias_entry.pack(pady=(0, 20))

        def applyAliases():
            speaker1_alias = speaker1_alias_entry.get().strip()
            speaker2_alias = speaker2_alias_entry.get().strip()

            # Fetch the current state of the transcription text
            transcription_text = self.getTranscriptionText()
            if speaker1_alias:
                transcription_text = transcription_text.replace("Speaker 1:", f"{speaker1_alias}:")
            if speaker2_alias:
                transcription_text = transcription_text.replace("Speaker 2:", f"{speaker2_alias}:")

            # Update the transcriptionBox with the new aliases
            self.transcriptionBox.delete("0.0", "end")
            self.transcriptionBox.insert("0.0", transcription_text)
            popup.destroy()

        # Button to apply the custom aliases
        apply_button = CTkButton(popup, text="Apply Aliases", command=applyAliases)
        apply_button.pack(pady=10)
    
    def uploadAudio(self):
        '''Upload user's audio file'''
        filename = filedialog.askopenfilename()
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
        unlockItem(self.labelSpeakersButton)
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
        downloadFile = filedialog.asksaveasfile(defaultextension = ".wav", filetypes = [("Wave File", ".wav"), ("All Files", ".*")], initialfile = "downloaded_audio.wav")
        if downloadFile: self.audio.saveAudioFile(downloadFile.name)
        
    def exportToWord(self):
        '''Exports the transcription to a Word document'''
        downloadFile = filedialog.asksaveasfile(defaultextension = ".docx", filetypes = [("Word Document", ".docx"), ("All Files", ".*")], initialfile = self.exporter.getDefaultFilename() + ".docx")
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
    button = CTkButton(master, text = text, height = height, command = command, font = font)
    if row is not None and column is not None:
        button.grid(row = row, column = column, columnspan = columnspan, padx = padx, pady = pady, sticky=W+E)
    if lock: lockItem(button)
    return button

def unlockItem(item: CTkTextbox | CTkButton | CTkEntry):
    '''Unlock a CustomTkinter item'''
    item.configure(state="normal")
    
def unlockMultipleItems(items: list):
    '''Unlocks all CustomTkinter items in a list'''
    for item in items:
        unlockItem(item)
        
def lockItem(item: CTkTextbox | CTkButton | CTkEntry):
    '''Lock a CustomTkinter item'''
    item.configure(state="disabled")
    
def lockMultipleItems(items: list):
    '''Locks all CustomTkinter items in a list'''
    for item in items:
        lockItem(item)
    
if __name__ == "__main__":
    gui = mainGUI()

