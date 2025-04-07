from customtkinter import *
from user_menu import userMenu
from audio_menu import audioMenu
from utils import createButton, lockItem, unlockItem
from error_handling import global_error_handler
from constants import *

class mainGUI(CTk):
    @global_error_handler
    def __init__(self):
        super().__init__()
        self.after(100, lambda: self.geometry("1375x740"))
        self.title('Speech Transcription')
        self.currentAudioNum = 0
        self.audioButtonList = []
        self.audioMenuList = []

        # Appearance setup
        try:
            with open(SETTINGS_FILE, "r") as file:
                set_appearance_mode(file.read())
        except FileNotFoundError:
            set_appearance_mode("dark")
        
        set_default_color_theme("blue")
        self.resizable(False, False)

        # Main UI components
        self.userFrame = userMenu(self)
        self.userFrame.grid(row=0, column=0, padx=1, sticky=NW)
        
        self.newAudioButton = createButton(
            master=self.userFrame,
            text="New Audio",
            row=1,
            column=0,
            command=self.new_audio,
            height=60,
            columnspan=2,
            lock=False
        )
        
        self.helpButton = createButton(
            master=self,
            text="Help",
            row=None,
            column=None,
            command=self.showHelpOverlay,
            height=30,
            width=80,
            lock=False
        )
        self.helpButton.place(relx=0, rely=1, anchor=SW, x=10, y=-10)
        
        self.mainloop()

    @global_error_handler
    def new_audio(self):
        dialog = CTkInputDialog(text="Enter Name of Session", title="New Audio")
        session_name = dialog.get_input().strip()
        if session_name:
            self.audioMenuList.append(audioMenu(self))
            newButton = createButton(
                master=self.userFrame.audioTabs,
                text=session_name,
                row=len(self.audioButtonList),
                column=0,
                command=lambda x=self.currentAudioNum: self.changeAudioWindow(x),
                width=self.userFrame.audioTabs.cget("width"),
                lock=False
            )
            self.audioButtonList.append(newButton)
            self.changeAudioWindow(self.currentAudioNum)
            self.currentAudioNum += 1
            unlockItem(self.audioMenuList[-1].uploadButton)
            unlockItem(self.audioMenuList[-1].recordButton)

    @global_error_handler
    def changeAudioWindow(self, num):
        for i, frame in enumerate(self.audioMenuList):
            frame.grid(row=0, column=1, padx=5) if i == num else frame.grid_remove()
        for i, button in enumerate(self.audioButtonList):
            button.configure(fg_color="#029CFF" if i == num else "#0062B1")

    @global_error_handler
    def showHelpOverlay(self):
        popup = CTkToplevel(self)
        popup.title("Help Guide")
        popup.geometry("450x450")
        popup.resizable(False, False)
        
        help_text = """Help Guide:
        - New Audio: Create new session
        - Upload: Import audio file
        - Record: Capture new audio
        - <<: Rewind 5 seconds
        - ⏯: Play/Pause
        - >>: Forward 5 seconds
        - Transcribe: Convert to text
        - Label Speakers: Identify speakers
        - Apply Aliases: Customize names
        - Download: Save audio
        - Export: Word document
        - Grammar Check: Find errors
        - Add Morphemes: Add inflections
        - Submit: Apply corrections
        - Clear Box: Reset text areas
        - Lock/Unlock: Edit protection"""
        
        CTkLabel(popup, text=help_text, justify=LEFT, wraplength=400).pack(padx=10, pady=10)
        createButton(popup, "Close", None, None, popup.destroy, lock=False).pack(pady=10)

if __name__ == "__main__":
    gui = mainGUI()