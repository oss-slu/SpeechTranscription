from customtkinter import *
from CTkXYFrame.CTkXYFrame.ctk_xyframe import *
from constants import *

class userMenu(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width=WIDTH/5, height=HEIGHT)
        self.label = CTkLabel(self, text="Speech Transcription", height=75, font=("Arial", 26))
        self.label.grid(row=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
        
        self.audioTabs = CTkXYFrame(self, height=465)
        self.audioTabs.grid(row=2, rowspan=8, columnspan=2, pady=5, padx=10, sticky=NSEW)
        
        CTkLabel(self, text="Theme").grid(row=10, column=0, padx=10, pady=5, sticky=NSEW)
        self.themeSetting = CTkOptionMenu(self, values=["Dark", "Light", "System"], command=self.changeTheme)
        self.themeSetting.grid(row=10, column=1, padx=10, pady=5, sticky=NSEW)

    def changeTheme(self, theme: str):
        set_appearance_mode(theme.lower())
        with open(SETTINGS_FILE, "w") as file:
            file.write(theme.lower())