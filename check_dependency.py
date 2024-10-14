import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
import webbrowser

def check_java():
    try:
        subprocess.run(['java', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False
    
def check_nltk():
    try:
        import nltk
        return True
    except ImportError:
        return False
    
def prompt_java_installation():
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askyesno("Java Not Found", "Java is not installed. Would you like to install it?")
    if response:
        webbrowser.open("https://www.java.com/en/download/")
    root.destroy()

def prompt_nltk_installation():
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askyesno("NLTK Not Found", "NLTK is not installed. Would you like to install it?")
    if response:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
        root.destroy()

def check_dependency():

    if check_java() == False:
        prompt_java_installation()

    if check_nltk() == False:
        prompt_nltk_installation()

    if check_java() and check_nltk() == True:
        print("All dependencies are installed.")

if __name__ == "__main__":
    check_dependency()