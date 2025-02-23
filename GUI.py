from customtkinter import *
import diarizationAndTranscription
from audio import AudioManager
from client_info import ClientInfo
from grammar import GrammarChecker
from export import Exporter
from PIL import Image
from CTkXYFrame.CTkXYFrame.ctk_xyframe import *  # Uses Third party license found in CtkXYFrame/ folder
import threading
import matplotlib.pyplot as plt
import time
import webbrowser
import traceback
import customtkinter as ctk


WIDTH = 1340
HEIGHT = 740
SETTINGS_FILE = "user_settings.txt"

def scale_image(image_path, size=(30, 30)):
    #Makes sure resize the image
    image = Image.open(image_path)
    image = image.resize(size)
    return customtkinter.CTkImage(light_image=image, dark_image=image, size=size)

LOCK_ICON = scale_image("images/locked_icon.png", size=(30, 30))
UNLOCK_ICON = scale_image("images/unlocked_icon.png", size =(30, 30))
CLEAR_ICON = scale_image("images/clear_icon.png", size = (30, 30))

# Global error handler
def global_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()  # Print the full traceback to the console
            show_error_popup(args[0], str(e))  # args[0] is 'self' for instance methods
    return wrapper

# Function to show error pop-up
def show_error_popup(master, error_message):
    popup = CTkToplevel(master)
    popup.title("ERROR")
    popup.geometry("400x200")
    popup.resizable(False, False)

    error_label = CTkLabel(popup, text="ERROR", font=("Arial", 24, "bold"))
    error_label.pack(pady=20)

    message_label = CTkLabel(popup, text=error_message, wraplength=350)
    message_label.pack(pady=10)

    def file_bug():
        # Open the repository's issue page with pre-filled error details
        repo_link = "https://github.com/oss-slu/SpeechTranscription/issues"
        # issue_title = "Bug Report: Error in Application"
        # issue_body = f"Error Details:\n\n{error_message}\n\nStack Trace:\n\n{traceback.format_exc()}"
        webbrowser.open(repo_link)

    file_bug_button = CTkButton(popup, text="File a Bug", command=file_bug)
    file_bug_button.pack(pady=20)

def plotAudio(time, signal):
    '''Plots the waveform of audio'''
    plt.figure(1)
    plt.title("Audio Wave")
    plt.xlabel("Time")
    plt.plot(time, signal)
    plt.show()

# Apply global error handler to all methods in the mainGUI class
class mainGUI(CTk):
    @global_error_handler
    def new_audio(self):
        dialog = CTkInputDialog(text="Enter Name of Session", title="New Audio")
        session_name = dialog.get_input().strip()  # Get input and strip any whitespace
        if session_name:  # Check if the name is not empty after stripping
            self.audioMenuList.append(audioMenu(self))
            newButton = createButton(self.userFrame.audioTabs, session_name, len(self.audioButtonList), 0,
                                     lambda x=self.currentAudioNum: self.changeAudioWindow(x),
                                     width=self.userFrame.audioTabs.cget("width"), lock=False)
            self.audioButtonList.append(newButton)

            self.changeAudioWindow(self.currentAudioNum)
            self.currentAudioNum += 1

    @global_error_handler
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
            if i == num:
                button.configure(fg_color="#029CFF")
            else:
                button.configure(fg_color="#0062B1")
        self.tkraise(self.audioFrame)

    @global_error_handler
    def showHelpOverlay(self):
        '''Displays a pop-up with all button functionalities.'''
        popup = CTkToplevel(self)
        popup.title("Help Guide")

        # Adjust window size to fit all text
        popup.geometry("450x450")  # Adjusted to fit text better
        popup.attributes("-topmost", True)
        popup.resizable(False, False)

        helpText = """
        Help Guide:
        
        - New Audio: Create a new audio session.
        - Upload: Upload an audio file.
        - Record: Record a new audio file.
        - <<: Rewind the audio by 5 seconds.
        - ⏯: Play and Pause the audio.
        - >>: Fast forward the audio by 5 seconds.
        - Transcribe: Transcribe the audio.
        - Label Speakers: Label different speakers in the transcription.
        - Apply Aliases: Customize speaker aliases to give unique names to speakers.
        - Download Audio: Download the recorded audio.
        - Export to Word: Export the transcription to a Word document.
        - Grammar Check: Check the transcription for grammar errors. This button will only work after transcribing the audio.
        - Add Morphemes: Add inflectional morphemes to the transcription. This button will only work after grammar checking.
        - Submit: Submit grammar corrections.
        - Clear Box?: Clear the transcription or convention box.
        - Lock/Unlock: Lock or unlock the transcription or convention box in order to manually edit the transcribed/convention text.
        """

        # Instead of a scrollable frame, use a regular frame
        helpLabel = CTkLabel(popup, text=helpText, justify=LEFT, font=("Arial", 12), wraplength=400)
        helpLabel.pack(padx=10, pady=10)

        closeButton = createButton(popup, "Close", None, None, popup.destroy, height=30, width=80, lock=False)
        closeButton.pack(pady=10)

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
        self.userFrame.grid(row=0, column=0, padx=1, sticky=NW)

        self.newAudioButton = createButton(self.userFrame, "New Audio", 1, 0, self.new_audio, height=60, columnspan=2,
                                           lock=False)

        self.audioFrame = CTkFrame(self)
        
        # Add Help Button
        self.helpButton = createButton(self, "Help", None, None, self.showHelpOverlay, height=30, width=80, lock=False)
        self.helpButton.place(relx=0, rely=1, anchor=SW, x=10, y=-10)  # Position at bottom left corner
        
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


# Define speaker colors (modify as needed for light/dark theme compatibility)
SPEAKER_COLORS = {
    "Speaker 1": "#029CFF",  # Light Blue
    "Speaker 2": "#FF5733"   # Light Red
}


# Apply global error handler to all methods in the audioMenu class
class audioMenu(CTkFrame):
    @global_error_handler
    def __init__(self, master):
        super().__init__(master)
        self.configure(width=WIDTH * .8)
        self.configure(height=HEIGHT)

        self.audio = AudioManager(master)
        self.grammar = GrammarChecker()
        self.exporter = Exporter()
        


        # ROW 0: Frame for Audio Upload/Record buttons
        self.audioInputFrame = CTkFrame(self, height=80)
        self.audioInputFrame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=N + E + W)
        self.audioInputLabel = CTkLabel(self.audioInputFrame, text="Input Audio Source Here", font=("Arial", 18))
        self.audioInputLabel.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.uploadButton = createButton(self.audioInputFrame, "Upload", 1, 0, self.uploadAudio, height=80,
                                         font=("Arial", 18), lock=False)
        self.recordButton = createButton(self.audioInputFrame, "Record", 1, 1, self.recordAudio, height=80,
                                         font=("Arial", 18), lock=False)

        # Configure audio input frame columns
        self.audioInputFrame.grid_columnconfigure(0, weight=1)
        self.audioInputFrame.grid_columnconfigure(1, weight=1)

        # ROW 1: Playback Controls in a Frame
        self.playbackFrame = CTkFrame(self, height=100, width=200)
        self.playbackFrame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        self.playbackFrame.grid_propagate(False)  # Prevent frame from shrinking

        self.backwardButton = createButton(self.playbackFrame, "<<", 0, 0, self.backwardAudio, height=60,
                                           font=("Arial", 18), lock=False)
        self.playPauseButton = createButton(self.playbackFrame, "⏯", 0, 1, self.togglePlayPause, height=60,
                                            font=("Arial", 18))
        self.forwardButton = createButton(self.playbackFrame, ">>", 0, 2, self.forwardAudio, height=60,
                                          font=("Arial", 18), lock=False)

        # Configure playback frame columns
        self.playbackFrame.grid_columnconfigure(0, weight=1)
        self.playbackFrame.grid_columnconfigure(1, weight=1)
        self.playbackFrame.grid_columnconfigure(2, weight=1)

        # ROW 2: Transcribe (and progress bar)
        self.transcribeButton = createButton(self, "Transcribe", 2, 0, self.transcriptionThread, 10, 10, 2, 2, 200, 125,
                                             font=("Arial", 40))

        # ROW 4: Labelling Transcription buttons
        self.labelSpeakersButton = createButton(self, "Label Speakers", 4, 0, self.labelSpeakers, lock=True)  # For speaker labeling
        self.applyAliasesButton = createButton(self, "Apply Aliases", 4, 1, self.customizeSpeakerAliases)  # For more specific labeling

        self.speaker_aliases = {"Speaker 1": "Speaker 1", "Speaker 2": "Speaker 2"} 

        # ROW 5: Export, Grammar, and correction boxes.
        self.downloadAudioButton = createButton(self, "Download Audio", 5, 0, self.downloadRecordedAudio)
        self.exportButton = createButton(self, "Export to Word", 5, 1, self.exportToWord)

        self.grammarButton = createButton(self, "Grammar Check", 5, 2, self.grammarCheckThread)
        self.morphemesButton = createButton(self, "Add Morphemes", 5, 3, self.inflectionalMorphemes)
        self.submitGrammarButton = createButton(self, "Submit", 5, 5, self.applyCorrection)

        self.correctionEntryBox = CTkTextbox(self, height=60)
        self.correctionEntryBox.grid(row=5, column=4, padx=10, sticky=E + W)
        lockItem(self.correctionEntryBox)

        # Transcription Box Control and Frame
        self.transcriptionBoxFrame = CTkFrame(self)

        self.transcriptionBoxFrame.grid(row=0, column=2, rowspan=5, columnspan=2,  padx=10, pady=10,sticky=N+E+S+W)
        self.transcriptionBoxLabel = CTkLabel(self.transcriptionBoxFrame, height=10, text="Transcription Box", font=("Arial", 18))
        self.transcriptionBoxLabel.grid(row=0, column=0, padx=5)
        self.transcriptionBoxLockButton = createButton(master=self.transcriptionBoxFrame, text='', row=0, column=1, command=self.toggleTranscriptionBox, height =10, width=10, lock=False)
        self.transcriptionBoxLockButton.configure(image=LOCK_ICON, width=30, height=30)
        self.transcriptionBoxClearButton = createButton(master=self.transcriptionBoxFrame, text='Clear Box?', row=0, column=2, command=self.clearTranscriptionBox, height=10, width=10, lock=False)
        self.transcriptionBoxClearButton.configure(image=CLEAR_ICON, width=30, height=30)

        self.transcriptionBox = CTkTextbox(self.transcriptionBoxFrame, width=350, height=500)
        self.transcriptionBox.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=N + E + S + W)
        self.transcriptionBox.insert("0.0", text="Text will generate here")
        lockItem(self.transcriptionBox)

        # Conventions Box Control and Frame
        self.conventionBoxFrame = CTkFrame(self)
        self.conventionBoxFrame.grid(row=0, column=4, rowspan=5, columnspan=2, padx=10, pady=10, sticky=N + E + S + W)
        self.conventionBoxLabel = CTkLabel(self.conventionBoxFrame, height=10, text="Convention Box", font=("Arial", 18))
        self.conventionBoxLabel.grid(row=0, column=0, padx=5)

        self.conventionBoxLockButton = createButton(master=self.conventionBoxFrame, text='', row=0, column=1, command=self.toggleGrammarBox, height=10, width=10, lock=False)
        self.conventionBoxLockButton.configure(image=LOCK_ICON, width=30, height=30)
        self.conventionBoxClearButton = createButton(master=self.conventionBoxFrame, text='Clear Box?', row=0, column=2, command=self.clearGrammarBox,height=10, width=10, lock=False)
        self.conventionBoxClearButton.configure(image=CLEAR_ICON, width=30, height=30)

        self.conventionBox = CTkTextbox(self.conventionBoxFrame, width=350, height=500)
        self.conventionBox.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=N + E + S + W)
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

    def apply_labels(self, speaker):
        """Applies speaker labels with color coding."""
        current_text = self.getTranscriptionText()
        current_segments = current_text.split('\n')
        
        for var, idx in self.segment_selections:
            if var.get() and not current_segments[idx].startswith(f"{speaker}:"):
                current_segments[idx] = f"{speaker}: {current_segments[idx]}"
                var.set(0)  # Reset checkbox

        new_transcription_text = "\n".join(current_segments)
        self.transcriptionBox.delete("0.0", "end")
        
        # Apply color formatting
        self.transcriptionBox.insert("0.0", new_transcription_text)
        self.color_code_transcription()
        unlockItem(self.applyAliasesButton)


    def color_code_transcription(self):
        """Applies color to different speakers' transcriptions."""
        self.transcriptionBox.tag_config("Speaker 1", foreground=SPEAKER_COLORS["Speaker 1"])
        self.transcriptionBox.tag_config("Speaker 2", foreground=SPEAKER_COLORS["Speaker 2"])


        for speaker, alias in self.speaker_aliases.items():
            self.transcriptionBox.tag_config(alias, foreground=SPEAKER_COLORS[speaker])
        

        # Clear existing tags before reapplying
        self.transcriptionBox.tag_remove("Speaker 1", "1.0", "end")
        self.transcriptionBox.tag_remove("Speaker 2", "1.0", "end")

        for speaker, alias in self.speaker_aliases.items():
            start_idx = "1.0"
            while True:
                start_idx = self.transcriptionBox.search(f"{alias}:", start_idx, stopindex="end", exact=True, nocase=False)
                if not start_idx:
                    break
                end_idx = self.transcriptionBox.index(f"{start_idx} lineend")
                self.transcriptionBox.tag_add(alias, start_idx, end_idx)
                start_idx = self.transcriptionBox.index(f"{start_idx} + 1 line")

        transcription_text = self.getTranscriptionText()
        self.transcriptionBox.mark_set("range_start", "1.0")

        for speaker in SPEAKER_COLORS.keys():
            start_idx = "1.0"
            while True:
                start_idx = self.transcriptionBox.search(f"{speaker}:", start_idx, stopindex="end", exact=True, nocase=False)
                if not start_idx:
                    break
                end_idx = self.transcriptionBox.index(f"{start_idx} lineend")

            
                # Apply color formatting to the whole line

                self.transcriptionBox.tag_add(speaker, start_idx, end_idx)
                self.transcriptionBox.tag_config(speaker, foreground=SPEAKER_COLORS[speaker])

                # Move to the next occurrence
                start_idx = self.transcriptionBox.index(f"{end_idx} +1c")


    


    @global_error_handler
    def togglePlayPause(self):
        '''Toggles between play and pause states.'''
        if self.is_playing and not self.is_paused:
            self.pauseAudio()
        else:
            self.playAudio()

    @global_error_handler
    def playAudio(self):
        '''Initiates audio playback in a separate thread, resetting the position if not already playing and allowing for resumption if paused.'''
        if not self.is_playing:
            print("Starting audio playback...")
            self.is_playing = True
            self.is_paused = False
            self.current_position = 0
            self.audio_length = self.audio.getAudioDuration(self.audio.filePath)  # Get the length of the audio
            threading.Thread(target=self.audio.play, args=(self.current_position,), daemon=True).start()  # Play in a thread
            self.updatePlayback()  # Start updating playback position
        elif self.is_paused:
            print("Resuming audio...")
            self.is_paused = False
            self.audio.paused = False

    @global_error_handler
    def pauseAudio(self):
        '''Pauses the currently playing audio and updates the button states accordingly.'''
        if self.is_playing and not self.is_paused:
            print("Pausing audio...")
            self.is_paused = True
            self.audio.paused = True

    @global_error_handler
    def forwardAudio(self):
        '''Skips forward by 5 seconds.'''
        if self.audio.playing:
            max_position = self.audio.getAudioDuration()
            self.audio.current_position = min(self.audio.current_position + 5, max_position)
            print(f"Skipping forward to {self.audio.current_position} seconds.")
            self.audio.seek(self.audio.current_position)
        else:
            print("Audio is not currently playing.")

    @global_error_handler
    def backwardAudio(self):
        '''Rewinds by 5 seconds.'''
        if self.audio.playing:
            self.audio.current_position = max(0, self.audio.current_position - 5)
            print(f"Rewinding to {self.audio.current_position} seconds.")
            self.audio.seek(self.audio.current_position)
        else:
            print("Audio is not currently playing.")

    @global_error_handler
    def updatePlayback(self):
        '''Continuously updates the playback position every 300 milliseconds if audio is playing and not paused.'''
        with self.lock:
            if self.is_playing and not self.is_paused:
                self.current_position += 0.3  # Incrementing playback position
            if self.is_playing:  # Continue updating
                self.master.after(300, self.updatePlayback)

    @global_error_handler
    def updateButtons(self):
        '''Updates the state of the play/pause button based on whether the audio is currently playing or paused.'''
        if self.is_playing and not self.is_paused:
            self.playPauseButton.configure(text="Pause")
        else:
            self.playPauseButton.configure(text="Play")

    @global_error_handler
    def scrubAudio(self, value):
        '''Allows users to scrub through the audio by clicking and dragging the playhead along the timeline.'''
        self.current_position = float(value)
        self.audio.setPlaybackPosition(self.current_position)  # Set the audio playback position
        if not self.is_paused:
            self.audio.play(self.current_position)  # Play from the new position

    @global_error_handler
    def startProgressBar(self):
        self.transcribeButton.grid(row=2, column=0, rowspan=1, columnspan=2)
        self.transcribeButton.configure(height=100)
        self.progressBar.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.progressBar.start()

    @global_error_handler
    def stopProgressBar(self):
        self.progressBar.stop()
        self.progressBar.grid_remove()
        self.transcribeButton.configure(height=200)
        self.transcribeButton.grid(row=2, column=0, rowspan=2, columnspan=2)

    @global_error_handler
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
            """Applies speaker labels with color coding."""
            current_text = self.getTranscriptionText()
            current_segments = current_text.split('\n')

            for var, idx in self.segment_selections:
                if var.get() and not current_segments[idx].startswith(f"{speaker}:"):
                    # Append the speaker label only if it's not already labeled
                    current_segments[idx] = f"{speaker}: {current_segments[idx]}"
                    var.set(0)  # Reset checkbox

            # Update the transcriptionBox with the modified text
            new_transcription_text = "\n".join(current_segments)
            self.transcriptionBox.delete("0.0", "end")
            self.transcriptionBox.insert("0.0", new_transcription_text)

            # ✅ Ensure the colors are applied after labeling
            self.color_code_transcription()
            self.transcriptionBox.update_idletasks()  # Force UI refresh

            unlockItem(self.applyAliasesButton)

            self.color_code_transcription()
            
            unlockItem(self.applyAliasesButton)

        # Buttons for applying speaker labels
        CTkButton(popup, text="Label as Speaker 1", command=lambda: apply_labels("Speaker 1"), fg_color=SPEAKER_COLORS["Speaker 1"], text_color="white").pack(side='left', padx=10, pady=10)
        CTkButton(popup, text="Label as Speaker 2", command=lambda: apply_labels("Speaker 2"), fg_color=SPEAKER_COLORS["Speaker 2"], text_color="white").pack(side='right', padx=10, pady=10)

    @global_error_handler
    def customizeSpeakerAliases(self):
        """Allows customization of speaker aliases while keeping color coding."""
        popup = ctk.CTkToplevel(self)
        popup.title("Customize Speaker Aliases")
        popup.geometry("400x200")

        speaker1_alias_label = ctk.CTkLabel(popup, text="Speaker 1 Alias:")
        speaker1_alias_label.pack(pady=(10, 0))
        speaker1_alias_entry = ctk.CTkEntry(popup)
        speaker1_alias_entry.pack(pady=(0, 10))

        speaker2_alias_label = ctk.CTkLabel(popup, text="Speaker 2 Alias:")
        speaker2_alias_label.pack(pady=(10, 0))
        speaker2_alias_entry = ctk.CTkEntry(popup)
        speaker2_alias_entry.pack(pady=(0, 20))

        def applyAliases():
            speaker1_alias = speaker1_alias_entry.get().strip()
            speaker2_alias = speaker2_alias_entry.get().strip()

            transcription_text = self.getTranscriptionText()
=======
            # Fetch the current state of the transcription text
            

            if speaker1_alias:
                self.speaker_aliases["Speaker 1"] = speaker1_alias
            if speaker2_alias:
                self.speaker_aliases["Speaker 2"] = speaker2_alias

            transcription_text = self.getTranscriptionText()
            for speaker, alias in self.speaker_aliases.items():
                transcription_text = transcription_text.replace(f"{speaker}:", f"{alias}:")

            self.transcriptionBox.delete("0.0", "end")
            self.transcriptionBox.insert("0.0", transcription_text)
            self.color_code_transcription()
            popup.destroy()

        apply_button = ctk.CTkButton(popup, text="Apply Aliases", command=applyAliases)
        apply_button.pack(pady=10)

# Call color_code_transcription() after labeling speakers or applying aliases


    @global_error_handler
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
            self.audioLength = self.audio.getAudioDuration(filename)

    @global_error_handler
    def recordAudio(self):
        '''Record a custom audio file'''
        if self.recordButton.cget("text") == "Record":
            self.recordButton.configure(text="Stop")
            self.audio.record()
        else:
            self.recordButton.configure(text="Record")
            unlockItem(self.playPauseButton)
            unlockItem(self.transcribeButton)
            unlockItem(self.downloadAudioButton)
            filename, time, signal = self.audio.stop()
            plotAudio(time, signal)

    @global_error_handler
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
        self.color_code_transcription()
        unlockItem(self.grammarButton)
        unlockItem(self.exportButton)
        self.stopProgressBar()

    @global_error_handler
    def transcriptionThread(self):
        '''Creates thread that executes the transcribe function'''
        if self.audio.playing or not self.audio.paused:
            self.audio.stopPlayback()
            if self.playback_thread is not None and self.playback_thread.is_alive():
                self.playback_thread.join()
        threading.Thread(target=self.transcribe).start()

    @global_error_handler
    def downloadRecordedAudio(self):
        '''Download file of recorded audio'''
        downloadFile = filedialog.asksaveasfile(defaultextension=".wav", filetypes=[("Wave File", ".wav"), ("All Files", ".*")],
                                                initialfile="downloaded_audio.wav")
        if downloadFile:
            self.audio.saveAudioFile(downloadFile.name)

    @global_error_handler
    def exportToWord(self):
        '''Exports the transcription to a Word document'''
        downloadFile = filedialog.asksaveasfile(defaultextension=".docx", filetypes=[("Word Document", ".docx"), ("All Files", ".*")],
                                                initialfile=self.exporter.getDefaultFilename() + ".docx")
        if downloadFile:
            text = self.getTranscriptionText()
            if self.grammarCheckPerformed:
                text = self.getGrammarText()
            self.exporter.exportToWord(text, downloadFile.name)

    @global_error_handler
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
        self.color_code_transcription()
        self.stopProgressBar()

    @global_error_handler
    def grammarCheckThread(self):
        '''Creates thread that executes the grammarCheck function'''
        threading.Thread(target=self.grammarCheck).start()

    @global_error_handler
    def applyCorrection(self):
        '''Apply's the user's grammar correction'''
        unlockItem(self.conventionBox)
        self.conventionBox.insert("end", self.correctionEntryBox.get("1.0", "end"))
        self.correctionEntryBox.delete("1.0", "end")
        self.manageGrammarCorrection()

    @global_error_handler
    def manageGrammarCorrection(self):
        '''Get the next grammar correction item'''
        corrected, sentenceToCorrect = self.grammar.getNextCorrection()
        if corrected:
            self.conventionBox.insert("end", corrected)
        if sentenceToCorrect:
            self.correctionEntryBox.insert("end", sentenceToCorrect)
        else:
            unlockItem(self.morphemesButton)
            unlockItem(self.exportButton)
            lockItem(self.correctionEntryBox)
            lockItem(self.submitGrammarButton)
            self.grammarCheckPerformed = True

    @global_error_handler
    def inflectionalMorphemes(self):
        '''Adds conventions to text from transcription box and puts output in conventionBox box'''
        unlockItem(self.conventionBox)
        converting = self.grammar.getInflectionalMorphemes(self.conventionBox.get("1.0", "end"))
        self.conventionBox.delete("1.0", "end")
        self.conventionBox.insert("end", converting)
        lockItem(self.morphemesButton)

    @global_error_handler
    def getTranscriptionText(self):
        return self.transcriptionBox.get('1.0', "end")

    @global_error_handler
    def toggleTranscriptionBox(self):
        if self.transcriptionBoxLockButton.cget('image') == LOCK_ICON:
            self.transcriptionBox.configure(state="normal")
            self.transcriptionBoxLockButton.configure(image=UNLOCK_ICON)
        else:
            self.transcriptionBox.configure(state="disabled")
            self.transcriptionBoxLockButton.configure(image=LOCK_ICON)

    @global_error_handler
    def toggleGrammarBox(self):
        if self.conventionBoxLockButton.cget('image') == LOCK_ICON:
            self.conventionBox.configure(state="normal")
            self.conventionBoxLockButton.configure(image=UNLOCK_ICON)
        else:
            self.conventionBox.configure(state="disabled")
            self.conventionBoxLockButton.configure(image=LOCK_ICON)

    @global_error_handler
    def clearTranscriptionBox(self):
        if self.transcriptionBoxLockButton.cget('image') == LOCK_ICON:
            self.toggleTranscriptionBox()
            self.transcriptionBox.delete("1.0", END)
            self.toggleTranscriptionBox()
        else:
            self.transcriptionBox.delete("1.0", END)

    @global_error_handler
    def clearGrammarBox(self):
        if self.conventionBoxLockButton.cget('image') == LOCK_ICON:
            self.toggleGrammarBox()
            self.conventionBox.delete("1.0", END)
            self.toggleGrammarBox()
        else:
            self.conventionBox.delete("1.0", END)

def createButton(master, text: str, row: int, column: int, command=None, padx=10, pady=10, rowspan=1, columnspan=1, height=60, width=100, font=("Arial", 14), lock=True):
    '''Creates button to be displayed'''
    button = CTkButton(master, text=text, height=height, width=width, command=command, font=font)
    if row is not None and column is not None:
        button.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, padx=padx, pady=pady, sticky=W + E)
    if lock:
        lockItem(button)
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
