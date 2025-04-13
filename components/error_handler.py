# components/error_handler.py
import traceback
import webbrowser
from customtkinter import *
from CTkXYFrame.CTkXYFrame.ctk_xyframe import *

def global_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            show_error_popup(args[0], str(e))
    return wrapper

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
        webbrowser.open("https://github.com/oss-slu/SpeechTranscription/issues")

    file_bug_button = CTkButton(popup, text="File a Bug", command=file_bug)
    file_bug_button.pack(pady=20)