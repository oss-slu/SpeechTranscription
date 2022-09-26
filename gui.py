from tkinter import Button, Checkbutton, IntVar, Label
import tkinter as tk

class GUI:
    def __init__(self):
        self.master = tk.Tk()
        self.master.title('Speech Transcription')
        self.master.geometry('1920x1080')

        uploadButton = Button(self.master, text='Upload')
        uploadButton.grid(row=0, column=0)
        recordButton = Button(self.master, text='Record')
        recordButton.grid(row=0, column=1)

        audioPlaceholder = Label(self.master, text='(This is where the audio would be)')
        audioPlaceholder.grid(row=0, column=2, columnspan=2)

        downloadButton = Button(self.master, text='Download')
        downloadButton.grid(row=0, column=4)

        transcribeButton = Button(self.master, text='Transcribe')
        transcribeButton.grid(row=0, column=5)

        grammerCheck1 = IntVar()
        grammerCheck2 = IntVar()
        grammerCheck3 = IntVar()
        grammerCheck4 = IntVar()
        grammerButton1 = Checkbutton(self.master, text='Grammer Option 1')
        grammerButton2 = Checkbutton(self.master, text='Grammer Option 2')
        grammerButton3 = Checkbutton(self.master, text='Grammer Option 3')
        grammerButton4 = Checkbutton(self.master, text='Grammer Option 4')

        grammerButton1.grid(row=2, column=3)
        grammerButton2.grid(row=2, column=4)
        grammerButton3.grid(row=3, column=3)
        grammerButton4.grid(row=3, column=4)

        addConventionsButton = Button(self.master, text='Add Conventions')
        addConventionsButton.grid(row=2, rowspan=2, column=5)

        editTranscriptionButton = Button(self.master, text='Edit Transcription')
        editTranscriptionButton.grid(row=4, column=5)
        exportButton = Button(self.master, text='Export to Word Document')
        exportButton.grid(row=5, column=5)
        printButton = Button(self.master, text='Print')
        printButton.grid(row=6, column=5)

        self.master.mainloop()

if __name__ == "__main__":
    myGui = GUI()
