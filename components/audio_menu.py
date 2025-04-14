# components/audio_menu.py
from customtkinter import *
from CTkXYFrame.CTkXYFrame.ctk_xyframe import *
from components.utils import createButton, lockItem, unlockItem
from components.error_handler import global_error_handler
from components.constants import LOCK_ICON, UNLOCK_ICON, CLEAR_ICON
from audio import AudioManager
from grammar import GrammarChecker
from export import Exporter
import diarizationAndTranscription
import threading
import time
import re
import matplotlib.pyplot as plt
import os
import sys
import tkinter as tk
import customtkinter as ctk 
from tkinter import filedialog, END
from tkinter import IntVar

SPEAKER_COLORS = {
    "Speaker 1": "#029CFF",  # Light Blue
    "Speaker 2": "#FF5733"   # Light Red
}

def plotAudio(time, signal):
    '''Plots the waveform of audio'''
    plt.figure(1)
    plt.title("Audio Wave")
    plt.xlabel("Time")
    plt.plot(time, signal)
    plt.show()

class audioMenu(CTkFrame):
    @global_error_handler
    def __init__(self, master):
        super().__init__(master)
        self.configure(width=master.WIDTH * .8)
        self.configure(height=master.HEIGHT)

        self.audio = AudioManager(master)
        self.grammar = GrammarChecker()
        self.exporter = Exporter()

        # ROW 0: Frame for Audio Upload/Record buttons
        self.audioInputFrame = CTkFrame(self, height=80)
        self.audioInputFrame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=N + E + W)

        # Textbox for File Name Display & Editing
        self.fileNameEntry = CTkEntry(self.audioInputFrame, placeholder_text="Enter file name here", font=("Arial", 18))
        self.fileNameEntry.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=N + E + W)

        self.uploadButton = createButton(self.audioInputFrame, "Upload", 1, 0, self.uploadAudio, height=80,
                                      font=("Arial", 18), lock=False)
        self.recordButton = createButton(self.audioInputFrame, "Record", 1, 1, self.recordAudio, height=80,
                                      font=("Arial", 18), lock=False)

        # Configure audio input frame columns
        self.audioInputFrame.grid_columnconfigure(0, weight=1)
        self.audioInputFrame.grid_columnconfigure(1, weight=1)

        # ROW 1: Playback Controls in a Frame
        self.playbackFrame = CTkFrame(self, height=125, width=250)
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

        # Timestamp Labels (Start Time, Current Time, End Time)
        self.startTimeLabel = CTkLabel(self.playbackFrame, text="00:00", font=("Arial", 12))
        self.startTimeLabel.grid(row=2, column=0, padx=5, sticky="w")

        self.currentTimeLabel = CTkLabel(self.playbackFrame, text="00:00", font=("Arial", 12))
        self.currentTimeLabel.grid(row=2, column=1, padx=5)

        self.endTimeLabel = CTkLabel(self.playbackFrame, text="--:--", font=("Arial", 12))
        self.endTimeLabel.grid(row=2, column=2, padx=5, sticky="e")

        self.timelineSlider = CTkSlider(self.playbackFrame, from_=0, to=100, command=self.scrubAudio)
        self.timelineSlider.grid(row=1, column=0, columnspan=3, padx=10, pady=(5,0), sticky="ew")
        self.timelineSlider.configure(state="disabled")

        # ROW 2: Transcribe (and progress bar)
        self.transcribeButton = createButton(self, "Transcribe", 2, 0, self.transcriptionThread, 10, 10, 2, 2, 200, 125,
                                          font=("Arial", 40))

        # ROW 4: Labelling Transcription buttons
        self.labelSpeakersButton = createButton(self, "Label Speakers", 4, 0, self.labelSpeakers, lock=True)
        self.applyAliasesButton = createButton(self, "Apply Aliases", 4, 1, self.customizeSpeakerAliases)

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
        self.transcriptionBoxFrame.grid(row=0, column=2, rowspan=5, columnspan=2, padx=10, pady=10, sticky=N+E+S+W)
        self.transcriptionBoxLabel = CTkLabel(self.transcriptionBoxFrame, height=10, text="Transcription Box", font=("Arial", 18))
        self.transcriptionBoxLabel.grid(row=0, column=0, padx=5)
        self.transcriptionBoxLockButton = createButton(master=self.transcriptionBoxFrame, text='', row=0, column=1, 
                                                     command=self.toggleTranscriptionBox, height=10, width=10, lock=False)
        self.transcriptionBoxLockButton.configure(image=LOCK_ICON, width=30, height=30)
        self.transcriptionBoxClearButton = createButton(master=self.transcriptionBoxFrame, text='Clear Box?', row=0, column=2, 
                                                      command=self.clearTranscriptionBox, height=10, width=10, lock=False)
        self.transcriptionBoxClearButton.configure(image=CLEAR_ICON, width=30, height=30)

        self.transcriptionBox = CTkTextbox(self.transcriptionBoxFrame, width=350, height=500)
        self.transcriptionBox.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=N + E + S + W)
        self.transcriptionBox.insert("0.0", text="Text will generate here")
        self.transcriptionBox.bind("<Button-1>", self.on_transcription_click)
        lockItem(self.transcriptionBox)

        # Conventions Box Control and Frame
        self.conventionBoxFrame = CTkFrame(self)
        self.conventionBoxFrame.grid(row=0, column=4, rowspan=5, columnspan=2, padx=10, pady=10, sticky=N + E + S + W)
        self.conventionBoxLabel = CTkLabel(self.conventionBoxFrame, height=10, text="Convention Box", font=("Arial", 18))
        self.conventionBoxLabel.grid(row=0, column=0, padx=5)

        self.conventionBoxLockButton = createButton(master=self.conventionBoxFrame, text='', row=0, column=1, 
                                                  command=self.toggleGrammarBox, height=10, width=10, lock=False)
        self.conventionBoxLockButton.configure(image=LOCK_ICON, width=30, height=30)
        self.conventionBoxClearButton = createButton(master=self.conventionBoxFrame, text='Clear Box?', row=0, column=2, 
                                                   command=self.clearGrammarBox, height=10, width=10, lock=False)
        self.conventionBoxClearButton.configure(image=CLEAR_ICON, width=30, height=30)

        self.conventionBox = CTkTextbox(self.conventionBoxFrame, width=350, height=500)
        self.conventionBox.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=N + E + S + W)
        self.conventionBox.insert("0.0", text="Text will generate here")
        lockItem(self.conventionBox)

        # Progress Bar Canvas (Added More Padding Below the Button)
        self.progressCanvas = tk.Canvas(self, width=225, height=20, bg="white", highlightthickness=0)

        self.running = False  # Flag to control animation
        self.stripe_offset = 0  # Offset to move stripes
        self.progress = 0  # Current progress percentage

        self.grammarCheckPerformed = False
        self.current_position = 0
        self.playback_thread = None
        self.is_playing = False
        self.is_paused = False
        self.audio_length = 0
        self.last_scrub_time = 0
        self.lock = threading.Lock()

    # All the audioMenu methods from the original GUI.py would follow here
    # (apply_labels, on_transcription_click, color_code_transcription, etc.)
    # Each method should be decorated with @global_error_handler

    @global_error_handler
    def apply_labels(self, speaker):
        """Applies speaker labels with color coding."""
        current_text = self.getTranscriptionText()
        current_segments = current_text.split('\n')
        
        for var, idx in self.segment_selections:
            if var.get() and not current_segments[idx].startswith(f"{speaker}:"):
                current_segments[idx] = f"{speaker}: {current_segments[idx]}"
                var.set(0)

        new_transcription_text = "\n".join(current_segments)
        self.transcriptionBox.delete("0.0", "end")
        self.transcriptionBox.insert("0.0", new_transcription_text)
        self.color_code_transcription()
        unlockItem(self.applyAliasesButton)

    @global_error_handler
    def on_transcription_click(self, event):
        index = self.transcriptionBox.index(f"@{event.x},{event.y}")
        line_num = index.split('.')[0]
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        line_text = self.transcriptionBox.get(line_start, line_end).strip()
        
        match = re.match(r'\[(\d+:\d+)\]', line_text)
        if match:
            timestamp_str = match.group(1)
            minutes, seconds = map(int, timestamp_str.split(':'))
            total_seconds = minutes * 60 + seconds
            
            if not self.audio.filePath:
                return
            
            was_playing = self.is_playing and not self.is_paused
            if was_playing:
                self.pauseAudio()
            
            self.current_position = total_seconds
            self.audio.seek(total_seconds)
            self.timelineSlider.set(total_seconds)
            self.updateCurrentTime(total_seconds)
            
            if was_playing:
                self.playAudio()

    @global_error_handler
    def color_code_transcription(self):
        self.transcriptionBox.tag_config("Speaker 1", foreground=SPEAKER_COLORS["Speaker 1"])
        self.transcriptionBox.tag_config("Speaker 2", foreground=SPEAKER_COLORS["Speaker 2"])

        for speaker, alias in self.speaker_aliases.items():
            self.transcriptionBox.tag_config(alias, foreground=SPEAKER_COLORS[speaker])

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
                self.transcriptionBox.tag_add(speaker, start_idx, end_idx)
                start_idx = self.transcriptionBox.index(f"{start_idx} + 1 line")

    @global_error_handler
    def togglePlayPause(self):
        if self.is_playing:
            self.pauseAudio()
        else:
            self.playAudio()
        self.updateButtonState()

    @global_error_handler
    def playAudio(self):
        if not self.audio.filePath:
            return

        if self.playback_thread and self.playback_thread.is_alive():
            with self.audio.lock:
                self.audio.paused = False
        else:
            self.playback_thread = threading.Thread(
                target=self.audio.play, 
                daemon=True,
                kwargs={'startPosition': self.current_position}
            )
            self.playback_thread.start()
        
        self.is_playing = True
        self.is_paused = False
        self.updatePlayback()

    @global_error_handler
    def pauseAudio(self):
        with self.audio.lock:
            self.audio.paused = True
        self.is_playing = False
        self.is_paused = True

    @global_error_handler
    def updateEndTime(self, duration):
        mins, secs = divmod(int(duration), 60)
        self.endTimeLabel.configure(text=f"{mins:02}:{secs:02}")

    @global_error_handler
    def updateCurrentTime(self, position):
        mins, secs = divmod(int(position), 60)
        self.currentTimeLabel.configure(text=f"{mins:02}:{secs:02}")

    @global_error_handler
    def forwardAudio(self):
        if self.audio.playing:
            max_position = self.audio.getAudioDuration()
            new_position = min(self.audio.current_position + 5, max_position)
            
            self.audio.seek(new_position)
            self.current_position = new_position
            self.timelineSlider.set(self.current_position)
            self.updateCurrentTime(self.current_position)

    @global_error_handler
    def backwardAudio(self):
        if self.audio.playing:
            new_position = max(0, self.audio.current_position - 5)
            
            self.audio.seek(new_position)
            self.current_position = new_position
            self.timelineSlider.set(self.current_position)
            self.updateCurrentTime(self.current_position)

    @global_error_handler
    def updatePlayback(self):
        if self.is_playing and not self.is_paused:
            self.current_position = self.audio.get_current_position()
            self.timelineSlider.set(self.current_position)
            self.updateCurrentTime(self.current_position)
            self.master.after(50, self.updatePlayback)
        else:
            self.timelineSlider.set(self.current_position)

    @global_error_handler
    def updateButtonState(self):
        if self.is_playing and not self.is_paused:
            self.playPauseButton.configure(text="Pause")
        else:
            self.playPauseButton.configure(text="Play")

    @global_error_handler
    def scrubAudio(self, value):
        current_time = time.time()
        if current_time - self.last_scrub_time < 0.1:
            return
        self.last_scrub_time = current_time

        was_playing = self.is_playing
        if was_playing:
            self.pauseAudio()

        self.current_position = float(value)
        self.audio.seek(self.current_position)
        self.updateCurrentTime(self.current_position)

        if was_playing:
            self.playAudio()

    @global_error_handler
    def startProgressBar(self):
        """Starts the animated gradient striped progress bar with better spacing."""
        self.transcribeButton.grid(row=2, column=0, rowspan=1, columnspan=2)
        self.transcribeButton.configure(height=100)  # Keep button visible
        self.progressCanvas.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.running = True
        self.progress = 0
        self.animate_striped_progress()


    def animate_striped_progress(self):
        """Creates a moving striped gradient effect on the progress bar."""
        if not self.running:
            return  # Stop animation if needed

        self.progressCanvas.delete("all")  # Clear previous frame

        stripe_width = 20  # Width of each stripe
        num_stripes = 15  # Number of stripes
        self.stripe_offset = (self.stripe_offset + 3) % stripe_width  # Move stripes

        # Define two gradient shades of blue
        color1 = "#1E90FF"  # Lighter blue
        color2 = "#104E8B"  # Darker blue

        # Draw diagonal stripes
        for i in range(-stripe_width, 225, stripe_width):
            x1 = i + self.stripe_offset
            x2 = x1 + stripe_width
            self.progressCanvas.create_polygon(
                x1, 0, x2, 0, x2 - 10, 20, x1 - 10, 20,
                fill=color1 if (i // stripe_width) % 2 == 0 else color2, outline=""
            )

        # Draw a progress overlay
        self.progressCanvas.create_rectangle(0, 0, 225 * self.progress, 20, fill="blue", outline="")

        self.progressCanvas.update_idletasks()  # Force UI update
        self.progressCanvas.after(50, self.animate_striped_progress)  # Schedule next frame

    @global_error_handler
    def update_progress_bar(self, progress):
        """Switches to a solid fill as progress reaches 100%."""
        self.progress = progress  # Store progress value

        if progress >= 1.0:  # If fully completed, stop animation
            self.running = False
            self.progressCanvas.delete("all")
            self.progressCanvas.create_rectangle(0, 0, 225, 20, fill="blue", outline="")
            self.progressCanvas.update_idletasks()

    @global_error_handler
    def stopProgressBar(self):
        """Ensure progress bar is fully filled before hiding it."""
        self.update_progress_bar(1.0)
        time.sleep(0.5)  # Short delay to show solid fill
        self.progressCanvas.grid_remove()
        self.transcribeButton.configure(height=200)  # Reset button size
        self.transcribeButton.grid(row=2, column=0, rowspan=2, columnspan=2)
    

    @global_error_handler
    def labelSpeakers(self):
        popup = CTkToplevel(self)
        popup.title("Label Speakers")
        popup.geometry("600x400")

        scrollable_frame = CTkScrollableFrame(popup)
        scrollable_frame.pack(fill='both', expand=True)

        initial_segments = self.getTranscriptionText().split('\n')
        self.segment_selections = []

        for idx, segment in enumerate(initial_segments):
            if segment.strip():
                var = IntVar()
                chk = CTkCheckBox(scrollable_frame, text=segment, variable=var)
                chk.pack(anchor='w', padx=5, pady=2)
                self.segment_selections.append((var, idx))

        def apply_labels(speaker):
            current_text = self.getTranscriptionText()
            current_segments = current_text.split('\n')

            for var, idx in self.segment_selections:
                if var.get() and not current_segments[idx].startswith(f"{speaker}:"):
                    line = current_segments[idx]
                    match = re.match(r'^\[(\d+:\d+)\]\s*(.*)', line)
                    if match:
                        timestamp = match.group(1)
                        rest = match.group(2)
                        current_segments[idx] = f"[{timestamp}] {speaker}: {rest}"
                    else:
                        current_segments[idx] = f"{speaker}: {line}"
                    var.set(0)

            new_transcription_text = "\n".join(current_segments)
            self.transcriptionBox.configure(state="normal")
            self.transcriptionBox.delete("1.0", "end")
            self.transcriptionBox.insert("1.0", new_transcription_text)
            self.transcriptionBox.configure(state="disabled")
            self.color_code_transcription()

        button_frame = CTkFrame(popup)
        button_frame.pack(pady=10)

        CTkButton(button_frame, text="Label as Speaker 1", command=lambda: apply_labels("Speaker 1"), fg_color="#029CFF").pack(side="left", padx=10)
        CTkButton(button_frame, text="Label as Speaker 2", command=lambda: apply_labels("Speaker 2"), fg_color="#FF5733").pack(side="left", padx=10)

    @global_error_handler
    def customizeSpeakerAliases(self):
        popup = CTkToplevel(self)
        popup.title("Customize Speaker Aliases")
        popup.geometry("400x200")

        speaker1_alias_label = CTkLabel(popup, text="Speaker 1 Alias:")
        speaker1_alias_label.pack(pady=(10, 0))
        speaker1_alias_entry = CTkEntry(popup)
        speaker1_alias_entry.pack(pady=(0, 10))

        speaker2_alias_label = CTkLabel(popup, text="Speaker 2 Alias:")
        speaker2_alias_label.pack(pady=(10, 0))
        speaker2_alias_entry = CTkEntry(popup)
        speaker2_alias_entry.pack(pady=(0, 20))

        def applyAliases():
            speaker1_alias = speaker1_alias_entry.get().strip()
            speaker2_alias = speaker2_alias_entry.get().strip()

            if speaker1_alias:
                self.speaker_aliases["Speaker 1"] = speaker1_alias
            if speaker2_alias:
                self.speaker_aliases["Speaker 2"] = speaker2_alias

            transcription_text = self.getTranscriptionText()

            for speaker, alias in self.speaker_aliases.items():
                pattern = rf'(\[\d{{2}}:\d{{2}}\]\s*)?{re.escape(speaker)}:'
                transcription_text = re.sub(pattern, lambda m: f"{m.group(1) or ''}{alias}:", transcription_text)

            self.transcriptionBox.configure(state="normal")
            self.transcriptionBox.delete("0.0", "end")
            self.transcriptionBox.insert("0.0", transcription_text)
            self.transcriptionBox.configure(state="disabled")
            self.color_code_transcription()
            popup.destroy()

        apply_button = CTkButton(popup, text="Apply Aliases", command=applyAliases)
        apply_button.pack(pady=10)

    @global_error_handler
    def uploadAudio(self):
        filename = filedialog.askopenfilename()
        if filename:
            unlockItem(self.playPauseButton)
            unlockItem(self.transcribeButton)
            unlockItem(self.downloadAudioButton)

            time, signal = self.audio.upload(filename)
            plotAudio(time, signal)

            base_name = os.path.basename(filename)
            self.fileNameEntry.delete(0, END)
            self.fileNameEntry.insert(0, base_name)

            self.audioLength = self.audio.getAudioDuration(filename)
            mins, secs = divmod(int(self.audioLength), 60)
            self.endTimeLabel.configure(text=f"{mins:02}:{secs:02}")

            self.updateCurrentTime(0)

            if self.audio and self.audio.filePath:
                self.timelineSlider.configure(from_=0, to=self.audioLength, state="normal")
            
            lockItem(self.uploadButton)
            lockItem(self.recordButton)

    @global_error_handler
    def recordAudio(self):
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

            self.fileNameEntry.delete(0, END)
            self.fileNameEntry.insert(0, "RECORDING - 1.wav")

            lockItem(self.uploadButton)
            lockItem(self.recordButton)

    @global_error_handler
    def transcribe(self):
        if self.is_playing or self.is_paused:
            self.pauseAudio()

        self.startProgressBar()
        filename = self.audio.normalizeUploadedFile()

        try:
            transcribedAudio = diarizationAndTranscription.transcribe(filename)
            self.updateTranscriptionUI(transcribedAudio)
        except Exception as e:
            self.updateTranscriptionUI("Error during transcription.")

    @global_error_handler
    def transcriptionThread(self):
        if self.is_playing or self.is_paused:
            self.pauseAudio()

        threading.Thread(target=self.transcribe, daemon=True).start()

    @global_error_handler
    def updateTranscriptionUI(self, transcribedAudio):
        self.after(0, self._updateTranscriptionBox, transcribedAudio)

    @global_error_handler
    def _updateTranscriptionBox(self, transcribedAudio):
        self.transcriptionBox.configure(state="normal")
        unlockItem(self.transcriptionBox)
        self.transcriptionBox.delete("1.0", "end")
        self.transcriptionBox.insert("end", transcribedAudio + "\n")
        self.transcriptionBox.configure(state="disabled")

        self.labelSpeakersButton.configure(state="normal")
        self.applyAliasesButton.configure(state="normal")
        self.exportButton.configure(state="normal")
        self.grammarButton.configure(state="normal")
        self.submitGrammarButton.configure(state="normal")
        self.morphemesButton.configure(state="normal")

        self.stopProgressBar()

    @global_error_handler
    def downloadRecordedAudio(self):
        default_name = self.fileNameEntry.get() or "downloaded_audio.wav"
        downloadFile = filedialog.asksaveasfile(defaultextension=".wav", filetypes=[("Wave File", ".wav"), ("All Files", ".*")],
                                              initialfile=default_name)
        if downloadFile:
            self.audio.saveAudioFile(downloadFile.name)

    @global_error_handler
    def exportToWord(self):
        downloadFile = filedialog.asksaveasfile(defaultextension=".docx", filetypes=[("Word Document", ".docx"), ("All Files", ".*")],
                                              initialfile=self.exporter.getDefaultFilename() + ".docx")
        if downloadFile:
            text = self.getTranscriptionText()
            text_without_timestamps = re.sub(r'\[\d+:\d+\] ', '', text)
            
            if self.grammarCheckPerformed:
                grammar_text = self.getGrammarText()
                grammar_text_without_timestamps = re.sub(r'\[\d+:\d+\] ', '', grammar_text)
                self.exporter.exportToWord(grammar_text_without_timestamps, downloadFile.name)
            else:
                self.exporter.exportToWord(text_without_timestamps, downloadFile.name)

    @global_error_handler
    def grammarCheck(self):
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
        threading.Thread(target=self.grammarCheck).start()

    @global_error_handler
    def applyCorrection(self):
        unlockItem(self.conventionBox)
        self.conventionBox.insert("end", self.correctionEntryBox.get("1.0", "end"))
        self.correctionEntryBox.delete("1.0", "end")
        self.manageGrammarCorrection()

    @global_error_handler
    def manageGrammarCorrection(self):
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
        unlockItem(self.conventionBox)
        converting = self.grammar.getInflectionalMorphemes(self.conventionBox.get("1.0", "end"))
        self.conventionBox.delete("1.0", "end")
        self.conventionBox.insert("end", converting)
        lockItem(self.morphemesButton)

    @global_error_handler
    def getTranscriptionText(self):
        return self.transcriptionBox.get('1.0', "end")

    @global_error_handler
    def getGrammarText(self):
        return self.conventionBox.get('1.0', "end")

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