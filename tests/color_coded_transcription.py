from customtkinter import *
import diarizationAndTranscription
from audio import AudioManager
from client_info import ClientInfo
from grammar import GrammarChecker
from export import Exporter
from PIL import Image
from CTkXYFrame.CTkXYFrame.ctk_xyframe import * 
import threading
import matplotlib.pyplot as plt
import time

# Define speaker colors (choose contrasting colors for readability)
SPEAKER_COLORS = {
    "Speaker 1": "#FF5733",  # Bright Red-Orange
    "Speaker 2": "#3498DB"   # Deep Blue
}

class TranscriptionApp(CTk):
    def __init__(self):
        super().__init__()
        self.title("Transcription and Analysis")
        self.geometry("800x600")

        # GUI Elements
        self.textbox = CTkTextbox(self, width=700, height=400, wrap="word")
        self.textbox.pack(pady=20)
        
        self.process_button = CTkButton(self, text="Start Transcription", command=self.process_audio)
        self.process_button.pack()
    
    def process_audio(self):
        """Simulated processing function"""
        transcription = diarizationAndTranscription.get_transcription()
        self.display_transcription(transcription)
    
    def display_transcription(self, transcription):
        """Displays transcription with assigned colors"""
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")  # Clear previous text
        
        for segment in transcription:
            speaker = segment['speaker']
            text = segment['text']
            color = SPEAKER_COLORS.get(speaker, "#FFFFFF")  # Default to white if speaker unknown
            
            self.textbox.insert("end", f"{speaker}: {text}\n", (speaker,))
            self.textbox.tag_config(speaker, foreground=color)
        
        self.textbox.configure(state="disabled")

if __name__ == "__main__":
    app = TranscriptionApp()
    app.mainloop()
