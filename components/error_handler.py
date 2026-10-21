# components/error_handler.py
import traceback
import webbrowser
from customtkinter import *
from CTkXYFrame.CTkXYFrame.ctk_xyframe import *
import os
import sys

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

def global_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            show_error_popup(args[0], str(e))
    return wrapper

def show_error_popup(master, error_message, retry=None):
    '''retry, if given, adds a Retry button that closes the popup and calls it.'''
    popup = CTkToplevel(master)
    popup.title("ERROR")
    popup.geometry("420x240")
    popup.resizable(False, False)

    error_label = CTkLabel(popup, text="ERROR", font=("Arial", 26, "bold"))
    error_label.pack(pady=20)

    message_label = CTkLabel(popup, text=error_message, wraplength=350)
    message_label.pack(pady=10)

    def file_bug():
        webbrowser.open("https://github.com/oss-slu/SpeechTranscription/issues")

    button_frame = CTkFrame(popup, fg_color="transparent")
    button_frame.pack(pady=20)

    if retry is not None:
        def retry_and_close():
            popup.destroy()
            retry()

        retry_button = CTkButton(button_frame, text="Retry", command=retry_and_close)
        retry_button.pack(side="left", padx=10)

    file_bug_button = CTkButton(button_frame, text="File a Bug", command=file_bug)
    file_bug_button.pack(side="left", padx=10)