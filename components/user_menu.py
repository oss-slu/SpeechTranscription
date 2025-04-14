# components/user_menu.py
from customtkinter import *
from CTkXYFrame.CTkXYFrame.ctk_xyframe import *

class userMenu(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width=master.WIDTH / 5)
        self.configure(height=master.HEIGHT)

        self.label = CTkLabel(self, text="Speech Transcription", height=75, font=("Arial", 26))
        self.label.grid(row=0, columnspan=2, padx=10, pady=10, sticky=N+E+S+W)

        self.audioTabs = CTkXYFrame(self, height=465)
        self.audioTabs.grid(row=2, rowspan=8, columnspan=2, pady=5, padx=10, sticky=N+E+S+W)

        CTkLabel(self, text="Theme").grid(row=10, column=0, padx=10, pady=5, sticky=N+E+S+W)
        self.themeSetting = CTkOptionMenu(self, values=["Dark", "Light", "System"], command=self.changeTheme)
        self.themeSetting.grid(row=10, column=1, padx=10, pady=5, sticky=N+E+S+W)
        
    def changeTheme(self, theme: str):
        set_appearance_mode(theme.lower())
        with open("user_settings.txt", "w") as file:
            file.write(theme.lower())