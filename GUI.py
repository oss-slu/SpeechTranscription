# Adding Logging - CICD Internal Dev 
import logging
import os
import sys
import nltk # type: ignore

# Ensure NLTK knows where to find the bundled data when running as a frozen app
app_dir = os.path.dirname(os.path.abspath(__file__))
nltk_data_dir = os.path.join(app_dir, "nltk_data")
if os.path.exists(nltk_data_dir):
    # put it first, not last
    nltk.data.path.insert(0, nltk_data_dir)
else:
    logging.warning("GUI.py: bundled nltk_data not found")

# main.py
from customtkinter import *
from components.user_menu import userMenu
from components.audio_menu import audioMenu
from components.audio_menu import plotAudio
from components.utils import createButton, lockItem, unlockItem
from components.error_handler import global_error_handler, show_error_popup
from components.constants import WIDTH, HEIGHT, SETTINGS_FILE
import os
import sys
import platform

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")


promptRestart = False
if platform.system() == 'Windows':
    proc = subprocess.run("winget list -q \"ffmpeg\" --accept-source-agreements", shell=True, encoding='utf-8', stdout=subprocess.PIPE)
    output = proc.stdout.split('\n')
    if "No installed package found matching input criteria." in output[len(output)-2]:
        print("Installing ffmpeg. This is a one time installation.")
        subprocess.run("winget install ffmpeg --accept-source-agreements --accept-package-agreements", shell=True)
        promptRestart = True

class mainGUI(CTk):

    @global_error_handler
    def restartPromptPopup(self):
        popup = CTkToplevel(self)
        popup.title("Restart Required")
        popup.geometry("450x200")
        popup.attributes("-topmost", True)
        popup.resizable(False, False)

        text = "RESTART REQUIRED\nPlease close and reopen Saltify"

        text = CTkLabel(popup, text=text, justify=CENTER, font=("Arial", 20), wraplength=400)
        text.pack(padx=10, pady=10)

        closeButton = createButton(popup, "Close", None, None, height=30, width=80, lock=False, command=self.close_program)
        closeButton.pack(pady=10)

    def close_program(self):
        sys.exit()


    @global_error_handler
    def new_session(self):
        '''Automatically generates a new session with a unique name and navigates to the main page.'''
        from datetime import datetime

        # Generate session name in the format: "Session <Number> - <Date> <Time>"
        session_number = self.currentAudioNum + 1
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_name = f"Session {session_number} - {current_time}"

        # Create a new audio session
        self.audioMenuList.append(audioMenu(self))
        newButton = createButton(self.userFrame.audioTabs, session_name, len(self.audioButtonList), 0,
                                 lambda x=self.currentAudioNum: self.changeAudioWindow(x),
                                 width=self.userFrame.audioTabs.cget("width"), lock=False)
        self.audioButtonList.append(newButton)

        # Navigate directly to the new session
        self.changeAudioWindow(self.currentAudioNum)
        self.currentAudioNum += 1

        # Lock the "Show Audio Graph" button for the new session
        lockItem(self.showGraphButton)

    @global_error_handler
    def changeAudioWindow(self, num):
        for i, frame in enumerate(self.audioMenuList):
            if i == num:
                self.audioFrame = frame
                frame.grid(row=0, column=1, padx=5)
                # Unlock "Show Audio Graph" button if a file exists in the selected session
                if frame.audio.filePath:
                    unlockItem(self.showGraphButton)
                else:
                    lockItem(self.showGraphButton)
            else:
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
        popup.geometry("450x450")
        popup.attributes("-topmost", True)
        popup.resizable(False, False)

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
        """

        helpLabel = CTkLabel(popup, text=helpText, justify=LEFT, font=("Arial", 12), wraplength=400)
        helpLabel.pack(padx=10, pady=10)

        closeButton = createButton(popup, "Close", None, None, popup.destroy, height=30, width=80, lock=False)
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
        
        self.after(100, lambda: self.geometry("1375x740"))
        self.currentAudioNum = 0
        self.audioButtonList = []
        self.audioMenuList = []
        self.title('Speech Transcription')
        
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
        self.resizable(False, False)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        self.userFrame = userMenu(master=self)
        self.userFrame.grid(row=0, column=0, padx=1, sticky=NW)

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
            # logger.info("Running in headless mode. GUI mainloop will be skipped.")
            gui = mainGUI()  # You can still initialize for tests if needed, but GUI won't block
        else:
            # Launch the GUI normally
            gui = mainGUI()  # __init__ already calls mainloop()
    except Exception as e:
        # logger.exception("An error occurred while running the GUI.")
        raise
