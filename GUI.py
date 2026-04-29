import logging
import os
import sys
import platform
import subprocess
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", module="matplotlib")
logging.getLogger("language_tool_python").setLevel(logging.ERROR)

import nltk

# Ensure NLTK knows where to find the bundled data when running as a frozen app
if getattr(sys, 'frozen', False):
    app_dir = sys._MEIPASS
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))

nltk_data_dir = os.path.join(app_dir, "nltk_data")
if os.path.exists(nltk_data_dir):
    nltk.data.path.insert(0, nltk_data_dir)
else:
    logging.warning(f"GUI.py: bundled nltk_data not found at {nltk_data_dir}")

# Prevent NLTK from trying to download data at runtime in the packaged app
if getattr(sys, 'frozen', False):
    nltk.download = lambda *args, **kwargs: None
else:
    # Only download if not frozen (development mode)
    try:
        nltk.download('punkt_tab', quiet=True)
        nltk.download('averaged_perceptron_tagger_eng', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('wordnet_ic', quiet=True)
    except Exception as e:
        logging.warning(f"Failed to download NLTK data: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from components.constants import DEFAULT_FONT_SIZE, LARGE_FONT_SIZE, BUTTON_FONT_SIZE, LABEL_FONT_SIZE 


# Set JAVA_HOME for bundled JRE and PATH for FFmpeg
if getattr(sys, 'frozen', False):
    # JRE Setup
    jre_path = os.path.join(sys._MEIPASS, "jre")
    if platform.system() == "Darwin":
        jre_home = os.path.join(jre_path, "Contents", "Home")
    else:
        jre_home = jre_path
    
    if os.path.exists(jre_home):
        os.environ["JAVA_HOME"] = jre_home
        os.environ["PATH"] = os.path.join(jre_home, "bin") + os.pathsep + os.environ.get("PATH", "")
        logging.info(f"JAVA_HOME set to bundled JRE: {jre_home}")
    
    # FFmpeg Setup
    ffmpeg_dir = os.path.join(sys._MEIPASS, "bundled_ffmpeg")
    if os.path.exists(ffmpeg_dir):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
        logging.info(f"Bundled FFmpeg found at {ffmpeg_dir}, added to PATH")
        
        # Explicitly set pydub paths to avoid any lookup issues
        try:
            from pydub import AudioSegment
            AudioSegment.converter = os.path.join(ffmpeg_dir, "ffmpeg")
            AudioSegment.ffprobe = os.path.join(ffmpeg_dir, "ffprobe")
        except ImportError:
            pass
    else:
        logging.warning(f"Bundled FFmpeg not found at {ffmpeg_dir}")

# main.py
from customtkinter import *
from components.user_menu import userMenu
from components.audio_menu import audioMenu
from components.audio_menu import plotAudio
from components.utils import createButton, lockItem, unlockItem
from components.error_handler import global_error_handler, show_error_popup
from components.constants import WIDTH, HEIGHT, SETTINGS_FILE


if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

promptRestart = False
if platform.system() == "Windows":
    try:
        proc = subprocess.run("winget list -q \"ffmpeg\" --accept-source-agreements", shell=True, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = proc.stdout.split('\n')
        if len(output) > 1 and "No installed package found matching input criteria." in output[len(output)-2]:
            print("Installing ffmpeg. This is a one time installation.")
            subprocess.run("winget install ffmpeg --accept-source-agreements --accept-package-agreements", shell=True)
            promptRestart = True
    except Exception as e:
        logging.debug(f"Winget check failed: {e}")

class mainGUI(CTk):

    def start_rename_session(self, index, button):
        parent = button.master
        old_text = button.cget("text")

        # Get Button measurements Before Hiding it
        button.update_idletasks()
        btn_width = button.winfo_width()
        btn_height = button.winfo_height()

    # Hide button
        button.pack_forget()

    # Create entry
        entry = CTkEntry(parent, width=btn_width, height=btn_height)
        entry.insert(0, old_text)
        entry.pack(side="left", fill="x", expand=True)
        entry.focus_set()
        entry.select_range(0, "end")

        def confirm(event=None):
            new_text = entry.get().strip() or old_text
            cleanup(new_text)

        def cancel(event=None):
            cleanup(old_text)

        def cleanup(final_text):
            entry.destroy()
            button.configure(text=final_text)
            button.pack(side="left", fill="x", expand=True)

        # Optional: store on session object
            self.audioMenuList[index].name = final_text

    # Key bindings
        entry.bind("<Return>", confirm)
        entry.bind("<Escape>", cancel)

    @global_error_handler
    def restartPromptPopup(self):
        popup = CTkToplevel(self)
        popup.title("Restart Required")
        popup.geometry("450x200")
        popup.attributes("-topmost", True)
        popup.resizable(False, False)

        text = "RESTART REQUIRED\nPlease close and reopen Saltify"

        text = CTkLabel(popup, text=text, justify=CENTER, font=("Arial", LARGE_FONT_SIZE), wraplength=400)
        text.pack(padx=10, pady=10)

        closeButton = createButton(popup, "Close", None, None, height=30, width=80, lock=False, command=self.close_program)
        closeButton.pack(pady=10)

    def close_program(self):
        sys.exit()

    @global_error_handler
    def new_session(self):
        from datetime import datetime

        session_number = len(self.audioMenuList) + 1
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_name = f"Session {session_number} - {current_time}"

        # Create the session object
        self.audioMenuList.append(audioMenu(self))

        # A frame to hold both the button + delete icon
        session_frame = CTkFrame(self.userFrame.audioTabs)
        session_frame.grid(row=len(self.audioButtonList), column=0, sticky="ew", pady=2)

        # Main session button
        btn = createButton(
            session_frame, session_name, None, None,
            lambda x=session_number-1: self.changeAudioWindow(x),
            width=self.userFrame.audioTabs.cget("width") - 40,  # leave space for delete
            lock=False
        )
        btn.pack(side="left", fill="x", expand=True)

        #Double-Click to rename
        btn.bind(
            "<Double-Button-1>",
            lambda e, i=session_number-1, b=btn: self.start_rename_session(i, b)
        )

        # Delete button to remove all instances of current selected session
        del_btn = CTkButton(
            session_frame,
            text="✖",
            width=30,
            fg_color="red",
            command=lambda idx=session_number-1: self.delete_session(idx)
        )
        del_btn.pack(side="right", padx=5)

        # Save both references so we can delete them later
        self.audioButtonList.append((session_frame, btn, del_btn))

        self.currentAudioNum = session_number - 1
        self.changeAudioWindow(self.currentAudioNum)
        lockItem(self.showGraphButton)


    @global_error_handler
    def delete_session(self, index):
        from tkinter import messagebox

        # Confirm
        result = messagebox.askyesno(
            "Delete Session",
            "Are you sure you want to delete this session?"
        )
        if not result:
            return

        # --- Remove UI Elements ---
        frame, btn, del_btn = self.audioButtonList[index]
        frame.destroy()

        # Remove session object
        self.audioButtonList.pop(index)
        self.audioMenuList.pop(index)

        # Reindex remaining sessions
        for i, (frame, btn, del_btn) in enumerate(self.audioButtonList):
            btn.configure(command=lambda x=i: self.changeAudioWindow(x))
            del_btn.configure(command=lambda x=i: self.delete_session(x))

        # Fix currentAudioNum
        if self.currentAudioNum >= len(self.audioButtonList):
            self.currentAudioNum = len(self.audioButtonList) - 1

        # If sessions remain, switch to closest one
        if self.audioButtonList:
            self.changeAudioWindow(self.currentAudioNum)
        else:
            # No sessions left → lock graph button and clear screen
            lockItem(self.showGraphButton)
            if hasattr(self, "audioFrame"):
                self.audioFrame.grid_remove()



    @global_error_handler
    def changeAudioWindow(self, num):
        for i, frame in enumerate(self.audioMenuList):
            if i == num:
                self.audioFrame = frame
                frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                # Unlock "Show Audio Graph" button if a file exists in the selected session
                if frame.audio.filePath:
                    unlockItem(self.showGraphButton)
                else:
                    lockItem(self.showGraphButton)
            else:
                frame.grid_remove()
        for i, (session_frame, btn, del_btn) in enumerate(self.audioButtonList):
            if i == num:
                btn.configure(fg_color="#029CFF")
            else:
                btn.configure(fg_color="#0062B1")
        self.tkraise(self.audioFrame)

    @global_error_handler
    def showHelpOverlay(self):
        '''Displays a pop-up with all button functionalities.'''
        if self.helpOpen:
            return
        self.helpOpen = True

        popup = CTkToplevel(self)
        popup.title("Help Guide")
        popup.geometry("450x450")
        popup.attributes("-topmost", True)
        popup.resizable(False, False)

        def on_closing():
            popup.destroy()
            self.helpOpen = False
        popup.protocol("WM_DELETE_WINDOW", on_closing)

        helpText = """
        Help Guide:
        
        - New Audio: Create a new audio session.
        - Upload: Upload an audio file. (Disabled after first upload to prevent modifications, but enabled again after starting a new session)
        - Record: Record a new audio file. (Disabled after first recording to prevent modifications, but enabled again after starting a new session)
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
        - Rename Session: Double-click on a session name in the session list to rename it (Press Enter to save the new name or Esc to cancel)
        - Delete Session: Click the "X" button next to a session to delete it.
        """

        helpLabel = CTkLabel(popup, text=helpText, justify=LEFT, font=("Arial", DEFAULT_FONT_SIZE), wraplength=400, state="normal")
        helpLabel.pack(padx=10, pady=10)

        closeButton = createButton(popup, "Close", None, None, on_closing, height=30, width=80, lock=False)
        closeButton.pack(pady=10)

    @global_error_handler
    def showAudioGraph(self):
        '''Render and display the audio waveform graph dynamically based on the current session's audio file.'''
        if hasattr(self, 'audioMenuList') and self.audioMenuList:
            current_audio_menu = self.audioMenuList[self.currentAudioNum - 1]
            if current_audio_menu.audio.filePath:
                # Dynamically generate the graph data from the audio file associated with this session
                time, signal = current_audio_menu.audio.createWaveformFile()
                plotAudio(time, signal)
            else:
                show_error_popup("No Audio File", "No audio file available for this session. Please upload or record an audio file.")
        else:
            show_error_popup("No Session Available", "Please create a session and upload or record an audio file to view the graph.")

    def __init__(self):
        super().__init__()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        
        self.currentAudioNum = 0
        self.audioButtonList = []
        self.audioMenuList = []
        self.title('Speech Transcription')
        self.attributes("-topmost", False)

        self.helpOpen = False
        self.graphOpen = False
        
        try:
            if os.path.getsize(SETTINGS_FILE) != 0:
                with open(SETTINGS_FILE, "r") as file:
                    set_appearance_mode(file.read())
            else:
                set_appearance_mode("dark")
        except FileNotFoundError:
            set_appearance_mode("dark")
        
        set_default_color_theme("blue")
        deactivate_automatic_dpi_awareness()
        self.resizable(True, True)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        
        #To prevent shrinking 
        self.minsize(self.WIDTH, self.HEIGHT)

        self.userFrame = userMenu(master=self)
        self.userFrame.grid(row=0, column=0, padx=1, sticky="nsw")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Replace "New Audio" button with "New Session" button
        self.newSessionButton = createButton(self.userFrame, "New Session", 1, 0, self.new_session, 
                                             height=60, columnspan=2, lock=False)
        self.audioFrame = CTkFrame(self)
        
        # Add Help Button
        self.helpButton = createButton(self, "Help", None, None, self.showHelpOverlay, 
                                     height=30, width=80, lock=False)
        self.helpButton.place(relx=0, rely=1, anchor=SW, x=10, y=-10)  # Position at bottom left corner

        # Add "Show Audio Graph" Button (initially locked)
        self.showGraphButton = createButton(self, "Show Audio Graph", None, None, self.showAudioGraph, 
                                            height=30, width=120, lock=True)
        self.showGraphButton.place(relx=0, rely=1, anchor=SW, x=110, y=-10)  # Position to the right of the Help button
        
        promptRestart = False
        if promptRestart:
            self.restartPromptPopup()
        self.mainloop()

if __name__ == "__main__":
    try:
        headless = os.environ.get("HEADLESS", "false").lower() == "true"
        if headless:
            logger.info("Running in headless mode. GUI launch skipped.")
            # Optionally test imports or basic initialization
            import torch, whisper
            logger.info("Core modules loaded successfully in headless mode.")
            sys.exit(0)
        else:
            # Launch the GUI normally
            gui = mainGUI()  # __init__ already calls mainloop()
    except Exception as e:
        # logger.exception("An error occurred while running the GUI.")
        raise
