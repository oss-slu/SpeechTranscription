from customtkinter import *
import diarizationAndTranscription
from audio import AudioManager
from client_info import ClientInfo
from grammar import GrammarChecker
from export import Exporter
from PIL import Image
from CTkXYFrame.CTkXYFrame.ctk_xyframe import * # Uses Third party license found in CtkXYFrame/ folder
import threading
import matplotlib.pyplot as plt
import time


WIDTH = 1340
HEIGHT = 740
SETTINGS_FILE = "user_settings.txt"
LOCK_ICON = customtkinter.CTkImage(Image.open("images/locked_icon.png"), Image.open("images/locked_icon.png"), (30, 30))
UNLOCK_ICON = customtkinter.CTkImage(Image.open("images/unlocked_icon.png"), Image.open("images/unlocked_icon.png"), (30, 30))
CLEAR_ICON = customtkinter.CTkImage(Image.open("images/clear_icon.png"), Image.open("images/clear_icon.png"), (30, 30))

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
        session_name = dialog.get_input().strip() # Get input and strip any whitespace
        if session_name: # Check if the name is not empty after stripping
            self.audioMenuList.append(audioMenu(self))
            newButton = createButton(self.userFrame.audioTabs, session_name, len(self.audioButtonList), 0, lambda x=self.currentAudioNum: self.changeAudioWindow(x), width = self.userFrame.audioTabs.cget("width"), lock=False)
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
        try:
            if os.path.getsize(SETTINGS_FILE) != 0:
                file = open(SETTINGS_FILE, "r")
                set_appearance_mode(file.read())
                file.close()
            else:
                set_appearance_mode("dark")
        except FileNotFoundError:
            print("Settings file not found. Defaulting to dark mode.")
            set_appearance_mode("dark")
        set_default_color_theme("blue")
        deactivate_automatic_dpi_awareness()
        self.resizable(False, False)

        self.geometry(str(WIDTH) + 'x' + str(HEIGHT))

        self.userFrame = userMenu(master=self)
        self.userFrame.grid(row=0, column=0, padx = 1, sticky=NW)

        self.newAudioButton = createButton(self.userFrame, "New Audio", 1, 0, self.new_audio, height=60, columnspan=2, lock=False)

        self.audioFrame = CTkFrame(self)

        self.mainloop()

class userMenu(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width = WIDTH / 5)
        self.configure(height = HEIGHT)

        self.label = CTkLabel(master=self, text="Speech Transcription", height=75, font=("Arial", 26))
        self.label.grid(row=0, columnspan=2, padx=10, pady=10, sticky=N+E+S+W)

        self.audioTabs = CTkXYFrame(self, height=465)
        self.audioTabs.grid(row=2, rowspan=8, columnspan=2, pady=5, padx=10, sticky=N+E+S+W)

        CTkLabel(self, text="Theme").grid(row=10, column=0, padx=10, pady=5, sticky=N+E+S+W)

        self.themeSetting = CTkOptionMenu(self, values=["Dark", "Light", "System"], command=self.changeTheme)
        self.themeSetting.grid(row=10, column=1, padx=10, pady=5, sticky=N+E+S+W)
        
    def changeTheme(self, theme: str):
        set_appearance_mode(theme.lower())

        # Save theme setting to txt file
        file = open(SETTINGS_FILE, "w")
        file.write(theme.lower())
        file.close()

class audioMenu(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width=WIDTH * .8)
        self.configure(height=HEIGHT)

        self.SPEAKER_COLORS = {
            "Speaker 1": "#FF5733",  # Bright Red-Orange
            "Speaker 2": "#3498DB"   # Deep Blue
        }

         # Transcription Box
        self.transcriptionBox = CTkTextbox(self, width=700, height=400, wrap="word")
        self.transcriptionBox.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        
        # Transcribe Button
        self.transcribeButton = CTkButton(self, text="Transcribe", command=self.transcriptionThread)
        self.transcribeButton.grid(row=2, column=0, columnspan=3, pady=10)

        
        self.audio = AudioManager(master)
        self.grammar = GrammarChecker()
        self.exporter = Exporter()
        
        # ROW 0: Frame for Audio Upload/Record buttons
        self.audioInputFrame = CTkFrame(self, height=80)
        self.audioInputFrame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=N+E+W)
        self.audioInputLabel = CTkLabel(self.audioInputFrame, text="Input Audio Source Here", font=("Arial", 18))
        self.audioInputLabel.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.uploadButton = createButton(self.audioInputFrame, "Upload", 1, 0, self.uploadAudio, height=80, font=("Arial", 18), lock=False)
        self.recordButton = createButton(self.audioInputFrame, "Record", 1, 1, self.recordAudio, height=80, font=("Arial", 18), lock=False)

        # Configure audio input frame columns
        self.audioInputFrame.grid_columnconfigure(0, weight=1)
        self.audioInputFrame.grid_columnconfigure(1, weight=1)

        # ROW 1: Playback Controls in a Frame
        self.playbackFrame = CTkFrame(self, height=100, width=200)
        self.playbackFrame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        self.playbackFrame.grid_propagate(False)  # Prevent frame from shrinking
        
        self.backwardButton = createButton(self.playbackFrame, "<<", 0, 0, self.backwardAudio, height=60, font=("Arial", 18), lock=False)
        self.playPauseButton = createButton(self.playbackFrame, "⏯", 0, 1, self.togglePlayPause, height=60, font=("Arial", 18))
        self.forwardButton = createButton(self.playbackFrame, ">>", 0, 2, self.forwardAudio, height=60, font=("Arial", 18), lock=False)
        
        # Configure playback frame columns
        self.playbackFrame.grid_columnconfigure(0, weight=1)
        self.playbackFrame.grid_columnconfigure(1, weight=1)
        self.playbackFrame.grid_columnconfigure(2, weight=1)
        
        # ROW 1: Audio Playback control
        #self.playPauseButton = createButton(self, "Play", 1, 0, self.togglePlayPause, padx=10, pady=10, columnspan=2)

        # ROW 2: Timeline Slider
        #self.timelineSlider = CTkSlider(self, from_=0, to=100, command=self.scrubAudio)
        #self.timelineSlider.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # ROW 2+3: Transcribe (and progress bar)
        self.transcribeButton = createButton(self, "Transcribe", 2, 0, self.transcriptionThread, 10, 10, 2, 2, 200, 125, font=("Arial", 40))


        # ROW 4: Labelling Transcription buttons
        self.labelSpeakersButton = createButton(self, "Label Speakers", 4, 0, self.labelSpeakers, lock=True) # For speaker labeling
        self.applyAliasesButton = createButton(self, "Apply Aliases", 4, 1, self.customizeSpeakerAliases) # For more specific labeling

        # ROW 5: Export, Grammar, and correction boxes.
        self.downloadAudioButton = createButton(self, "Download Audio", 5, 0, self.downloadRecordedAudio)
        self.exportButton = createButton(self, "Export to Word", 5, 1, self.exportToWord)

        self.grammarButton = createButton(self, "Grammar Check", 5, 2, self.grammarCheckThread)
        self.morphemesButton = createButton(self, "Add Morphemes", 5, 3, self.inflectionalMorphemes)
        self.submitGrammarButton = createButton(self, "Submit", 5, 5, self.applyCorrection)

        self.correctionEntryBox = CTkTextbox(self, height=60)
        self.correctionEntryBox.grid(row=5, column=4, padx=10, sticky=E+W)
        lockItem(self.correctionEntryBox)

        # self.audioPlayback = CTkLabel(self, text="", height=50, fg_color=None, font=("Arial", 16))
        # self.audioPlayback.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=W+E)

        # Transcription Box Control and Frame
        self.transcriptionBoxFrame = CTkFrame(self)
        self.transcriptionBoxFrame.grid(row=0, column=2, rowspan=5, columnspan=2, padx=10, pady=10, sticky=N+E+S+W)
        self.transcriptionBoxLabel = CTkLabel(self.transcriptionBoxFrame, height=10, text="Transcription Box", font=("Arial", 18))
        self.transcriptionBoxLabel.grid(row=0, column=0, padx=5)
        self.transcriptionBoxLockButton = createButton(master=self.transcriptionBoxFrame, text='', row=0, column=1, command=self.toggleTranscriptionBox, height=10, width=10, lock=False)
        self.transcriptionBoxLockButton.configure(image=LOCK_ICON)
        self.transcriptionBoxClearButton = createButton(master=self.transcriptionBoxFrame, text='Clear Box?', row=0, column=2, command=self.clearTranscriptionBox, height=10, width=10, lock=False)
        self.transcriptionBoxClearButton.configure(image=CLEAR_ICON)

        self.transcriptionBox = CTkTextbox(self.transcriptionBoxFrame, width=350, height=500)
        self.transcriptionBox.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=N+E+S+W)
        self.transcriptionBox.insert("0.0", text="Text will generate here")
        lockItem(self.transcriptionBox)

        # Conventions Box Control and Frame
        self.conventionBoxFrame = CTkFrame(self)
        self.conventionBoxFrame.grid(row=0, column=4, rowspan=5, columnspan=2, padx=10, pady=10, sticky=N+E+S+W)
        self.conventionBoxLabel = CTkLabel(self.conventionBoxFrame, height=10, text="Convention Box",  font=("Arial", 18))
        self.conventionBoxLabel.grid(row=0, column=0, padx=5)
        self.conventionBoxLockButton = createButton(master=self.conventionBoxFrame, text='', row=0, column=1, command=self.toggleGrammarBox, height=10, width=10, lock=False)
        self.conventionBoxLockButton.configure(image=LOCK_ICON)
        self.conventionBoxClearButton = createButton(master=self.conventionBoxFrame, text='Clear Box?', row=0, column=2, command=self.clearGrammarBox,height=10, width=10, lock=False)
        self.conventionBoxClearButton.configure(image=CLEAR_ICON)


        self.conventionBox = CTkTextbox(self.conventionBoxFrame, width=350, height=500)
        self.conventionBox.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=N+E+S+W)
        self.conventionBox.insert("0.0", text="Text will generate here")
        lockItem(self.conventionBox)

        self.progressBar = CTkProgressBar(self, width=225, mode="indeterminate")
        
        self.grammarCheckPerformed = False

        self.current_position = 0
        self.playback_thread = None  # thread for when audio is playing
        self.is_playing = False
        self.is_paused = False
        self.audio_length = 0  # Store the length of the audio
        self.last_scrub_time = 0  # For debouncing scrubbing events

        self.lock = threading.Lock()


    def display_transcription(self, transcription):
        """Displays transcription with assigned colors."""
        self.transcriptionBox.configure(state="normal")
        self.transcriptionBox.delete("1.0", "end")  # Clear previous text
    
        for segment in transcription:
            speaker = segment['speaker']
            text = segment['text']
            color = self.SPEAKER_COLORS.get(speaker, "#000000")  # Default to black

        # Apply color tag before inserting text
        if not self.transcriptionBox.tag_names():
            self.transcriptionBox.tag_config(speaker, foreground=color)

            self.transcriptionBox.insert("end", f"{speaker}: {text}\n", speaker)

        self.transcriptionBox.configure(state="disabled")

    def transcribe(self):
        """Fetches transcription and applies formatting."""
        self.startProgressBar()
        filename = self.audio.normalizeUploadedFile()        
        transcribedAudio = diarizationAndTranscription.transcribe(filename)

        formatted_transcription = self.format_transcription(transcribedAudio)
        self.display_transcription(formatted_transcription)

        unlockItem(self.labelSpeakersButton)
        unlockItem(self.grammarButton)
        unlockItem(self.exportButton)
        self.stopProgressBar()
        
    def format_transcription(self, text):
        """Simulate speaker diarization by splitting text into segments."""
        segments = text.split("\n")
        formatted_segments = []
        
        for i, segment in enumerate(segments):
            speaker = "Speaker 1" if i % 2 == 0 else "Speaker 2"  # Simulated alternating speakers
            formatted_segments.append({"speaker": speaker, "text": segment})
        
        return formatted_segments

    def transcriptionThread(self):
       """Creates a thread that executes the transcribe function."""
    threading.Thread(target= self.transcribeButton).start()

        
    def togglePlayPause(self):
        '''Toggles between play and pause states.'''
        if self.is_playing and not self.is_paused:
            self.pauseAudio()
        else:
            self.playAudio()

    def playAudio(self):
        '''Initiates audio playback in a separate thread, resetting the position if not already playing and allowing for resumption if paused.'''
        if not self.is_playing:
            print("Starting audio playback...")
            self.is_playing = True
            self.is_paused = False
            self.current_position = 0
            #self.timelineSlider.set(0)  # Reset the slider to the beginning
            self.audio_length = self.audio.getAudioDuration(self.audio.filePath)  # Get the length of the audio
            #self.timelineSlider.configure(to=self.audio_length)  # Set the slider's maximum value to the audio length
            threading.Thread(target=self.audio.play, args=(self.current_position,), daemon=True).start()  # Play in a thread
            self.updatePlayback()  # Start updating playback position
        elif self.is_paused:
            print("Resuming audio...")
            self.is_paused = False
            self.audio.paused = False

    def pauseAudio(self):
        '''Pauses the currently playing audio and updates the button states accordingly.'''
        if self.is_playing and not self.is_paused:
            print("Pausing audio...")
            self.is_paused = True
            self.audio.paused = True

    def forwardAudio(self):
        '''Skips forward by 5 seconds.'''
        if self.audio.playing:
            max_position = self.audio.getAudioDuration()
            self.audio.current_position = min(self.audio.current_position + 5, max_position)
            print(f"Skipping forward to {self.audio.current_position} seconds.")
            self.audio.seek(self.audio.current_position)
        else:
            print("Audio is not currently playing.")

    def backwardAudio(self):
        '''Rewinds by 5 seconds.'''
        if self.audio.playing:
            self.audio.current_position = max(0, self.audio.current_position - 5)
            print(f"Rewinding to {self.audio.current_position} seconds.")
            self.audio.seek(self.audio.current_position)
        else:
            print("Audio is not currently playing.")

    def updatePlayback(self):
        '''Continuously updates the playback position every 300 milliseconds if audio is playing and not paused.'''
        with self.lock:
            if self.is_playing and not self.is_paused:
                self.current_position += 0.3  # Incrementing playback position
                # Update slider or UI here
            if self.is_playing:  # Continue updating
                self.master.after(300, self.updatePlayback)


    def updateButtons(self):
        '''Updates the state of the play/pause button based on whether the audio is currently playing or paused.'''
        if self.is_playing and not self.is_paused:
            self.playPauseButton.configure(text="Pause")
        else:
            self.playPauseButton.configure(text="Play")

    def scrubAudio(self, value):
        '''Allows users to scrub through the audio by clicking and dragging the playhead along the timeline.'''
        self.current_position = float(value)
        self.audio.setPlaybackPosition(self.current_position)  # Set the audio playback position
        if not self.is_paused:
            self.audio.play(self.current_position)  # Play from the new position

    def startProgressBar(self):
        self.transcribeButton.grid(row=2, column=0, rowspan=1, columnspan=2)
        self.transcribeButton.configure(height=100)
        self.progressBar.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.progressBar.start()

    def stopProgressBar(self):
        self.progressBar.stop()
        self.progressBar.grid_remove()
        self.transcribeButton.configure(height=200)
        self.transcribeButton.grid(row=2, column=0, rowspan=2, columnspan=2)

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
            unlockItem(self.playPauseButton)
            unlockItem(self.playPauseButton)
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
            unlockItem(self.playPauseButton)
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
        # if self.infoTab.isTranscriptionLocked(): lockItem(self.transcriptionBox)
        unlockItem(self.grammarButton)
        unlockItem(self.exportButton)
        self.stopProgressBar()
        
    def transcriptionThread(self):
        '''Creates thread that executes the transcribe function'''
        if self.audio.playing or not self.audio.paused:
            self.audio.stopPlayback()
            if self.playback_thread is not None and self.playback_thread.is_alive():
                #threading.Thread(target = self.transcribe).start()
                self.playback_thread.join()
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
        # if self.infoTab.isGrammarLocked(): lockItem(self.conventionBox)
        
    def inflectionalMorphemes(self):
        '''Adds conventions to text from transcription box and puts output in conventionBox box'''
        unlockItem(self.conventionBox)
        converting = self.grammar.getInflectionalMorphemes(self.conventionBox.get("1.0", "end"))
        self.conventionBox.delete("1.0", "end")
        self.conventionBox.insert("end", converting)
        # if self.infoTab.isGrammarLocked(): lockItem(self.conventionBox)
        lockItem(self.morphemesButton)
        
    def getTranscriptionText(self):
        return self.transcriptionBox.get('1.0', "end")
    
    def toggleTranscriptionBox(self):
        if self.transcriptionBoxLockButton.cget('image') == LOCK_ICON:
            self.transcriptionBox.configure(state="normal")
            self.transcriptionBoxLockButton.configure(image = UNLOCK_ICON)
        else: 
            self.transcriptionBox.configure(state="disabled")
            self.transcriptionBoxLockButton.configure(image = LOCK_ICON)
        
    def toggleGrammarBox(self):
        if self.conventionBoxLockButton.cget('image') == LOCK_ICON:
            self.conventionBox.configure(state="normal")
            self.conventionBoxLockButton.configure(image = UNLOCK_ICON)
        else: 
            self.conventionBox.configure(state="disabled")
            self.conventionBoxLockButton.configure(image = LOCK_ICON)
    
    def clearTranscriptionBox(self):
        if self.transcriptionBoxLockButton.cget('image') == LOCK_ICON:
            self.toggleTranscriptionBox()
            self.transcriptionBox.delete("1.0", END)
            self.toggleTranscriptionBox()
        else:
            self.transcriptionBox.delete("1.0", END)

    def clearGrammarBox(self):
        if self.conventionBoxLockButton.cget('image') == LOCK_ICON:
            self.toggleGrammarBox()
            self.conventionBox.delete("1.0", END)
            self.toggleGrammarBox()
        else:
            self.conventionBox.delete("1.0", END)

def createButton(master, text: str, row: int, column: int, command = None, padx = 10, pady = 10, rowspan = 1, columnspan = 1, height = 60, width = 100, font = ("Arial", 14), lock=True):
    '''Creates button to be displayed'''
    button = CTkButton(master, text = text, height = height, width = width, command = command, font = font)
    if row is not None and column is not None:
        button.grid(row = row, column = column, rowspan = rowspan, columnspan = columnspan, padx = padx, pady = pady, sticky=W+E)
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

# class sessionInfoMenu(CTkTabview):
#     def __init__(self, master, transcriptionBox: CTkTextbox, grammarBox: CTkTextbox):
#         super().__init__(master)
#         self.configure(height=200)
#         self.add("Client Information")
#         self.add("Examiner Information")
#         self.add("Tables")
        
#         self.transcriptionBox = transcriptionBox
#         self.grammarBox = grammarBox

#         self.clientLocked = False

#         self.nameBox = CTkEntry(self.tab("Client Information"), placeholder_text="Name")
#         self.nameBox.grid(row=0,column=0, padx=10, pady=10, sticky=W+E)

#         self.ageBox = CTkEntry(self.tab("Client Information"), placeholder_text="Age")
#         self.ageBox.grid(row=0,column=1, padx=10, pady=10, sticky=W+E)

#         self.genderBox = CTkEntry(self.tab("Client Information"), placeholder_text="Gender")
#         self.genderBox.grid(row=1,column=0, padx=10, pady=10, sticky=W+E)

#         self.dobBox = CTkEntry(self.tab("Client Information"), placeholder_text="Date of Birth")
#         self.dobBox.grid(row=1,column=1, padx=10, pady=10, sticky=W+E)

#         self.saveClientInfo = createButton(self.tab("Client Information"), "Lock", 2, 0, self.lockClientInfo, height=28, lock=False)
#         self.resetClientInfoButton = createButton(self.tab("Client Information"), "Reset", 2, 1, self.resetClientInfo, height=28, lock=False)

#         self.examinerLocked = False

#         self.exNameBox = CTkEntry(self.tab("Examiner Information"), placeholder_text="Examiner Name")
#         self.exNameBox.grid(row=0,column=0, padx=10, pady=10, sticky=W+E)

#         self.dosBox = CTkEntry(self.tab("Examiner Information"), placeholder_text="Date of Sample")
#         self.dosBox.grid(row=0,column=1, padx=10, pady=10, sticky=W+E)

#         self.contextBox = CTkEntry(self.tab("Examiner Information"), placeholder_text="Sample Context")
#         self.contextBox.grid(row=1,column=0, padx=10, pady=10, columnspan=2, sticky=W+E)

#         self.saveExaminerInfo = createButton(self.tab("Examiner Information"), "Lock", 2, 0, self.lockExaminerInfo, height=28, lock=False)
#         self.resetExaminerInfoButton = createButton(self.tab("Examiner Information"), "Reset", 2, 1, self.resetExaminerInfo, height=28, lock=False)

#         self.lockTranscription = StringVar(value="on")
#         self.lockTranscriptionBox = CTkSwitch(self.tab("Tables"), text="Lock Transcription?", command=self.toggleTranscription, variable=self.lockTranscription, onvalue="on", offvalue="off")
#         self.lockTranscriptionBox.grid(row=0, column=0, columnspan=2, padx=10, pady=12, sticky=E+W)

#         self.lockGrammar = StringVar(value="on")
#         self.lockGrammarBox = CTkSwitch(self.tab("Tables"), text="Lock Grammar Check?", command=self.toggleGrammar, variable=self.lockGrammar, onvalue="on", offvalue="off")
#         self.lockGrammarBox.grid(row=1, column=0, columnspan=2,padx=10, pady=12, sticky=E+W)

#         self.clearTranscriptionBox = createButton(self.tab("Tables"), "Clear Transcription", 2, 0, height=28, lock=False)
#         self.clearGrammarBox = createButton(self.tab("Tables"), "Clear Grammar Check", 2, 1, height=28, lock=False)

#     def lockClientInfo(self):
#         if not self.clientLocked:
#             lockMultipleItems([self.nameBox, self.ageBox, self.genderBox, self.dobBox])
#             self.saveClientInfo.configure(text="Unlock")
#         else:
#             unlockMultipleItems([self.nameBox, self.ageBox, self.genderBox, self.dobBox])
#             self.saveClientInfo.configure(text="Lock")
#         self.clientLocked = not self.clientLocked
        
#     def resetClientInfo(self):
#         if not self.clientLocked:
#             for item in [self.nameBox, self.ageBox, self.genderBox, self.dobBox]:
#                 item.delete("0.0", "end")

#     def lockExaminerInfo(self):
#         if not self.examinerLocked:
#             lockMultipleItems([self.exNameBox, self.dosBox, self.contextBox])
#             self.saveExaminerInfo.configure(text="Unlock")
#         else:
#             unlockMultipleItems([self.exNameBox, self.dosBox, self.contextBox])
#             self.saveExaminerInfo.configure(text="Lock")
#         self.examinerLocked = not self.examinerLocked
        
#     def resetExaminerInfo(self):
#         if not self.examinerLocked:
#             for item in [self.exNameBox, self.dosBox, self.contextBox]:
#                 item.delete("0.0", "end")

