from tkinter import Button, Checkbutton, IntVar, Label, Text, Entry, StringVar, OptionMenu
import tkinter as tk

class GUI:
    def __init__(self):
        self.master = tk.Tk()
        self.master.title('Speech Transcription')
        self.master.geometry('960x540')

        uploadButton = Button(self.master, text='Upload')
        uploadButton.grid(row=0, column=0)
        recordButton = Button(self.master, text='Record')
        recordButton.grid(row=0, column=1)

        audioPlaceholder = Label(self.master, text='(This is where the audio would be)')
        audioPlaceholder.grid(row=0, column=2)

        playButton = Button(self.master, text='Play')
        playButton.grid(row=0, column=3)

        downloadButton = Button(self.master, text='Download')
        downloadButton.grid(row=0, column=4)

        transcribeButton = Button(self.master, text='Transcribe')
        transcribeButton.grid(row=0, column=5)

        clientOptions = [
                "Name",
                "Age",
                "Gender",
                "Examiner Info"
                ]
        clicked = StringVar()
        clicked.set("Name")
        infoDropdown = OptionMenu(self.master, clicked, *clientOptions)
        infoDropdown.grid(row=1, column=1)

        infoEntry = Entry(self.master)
        infoEntry.grid(row=1, column=2)

        infoSubmit = Button(self.master)
        infoSubmit.grid(row=1, column=3)

        grammerCheck1 = IntVar()
        grammerCheck2 = IntVar()
        grammerCheck3 = IntVar()
        grammerCheck4 = IntVar()
        grammerButton1 = Checkbutton(self.master, text='Grammer Option 1')
        grammerButton2 = Checkbutton(self.master, text='Grammer Option 2')
        grammerButton3 = Checkbutton(self.master, text='Grammer Option 3')
        grammerButton4 = Checkbutton(self.master, text='Grammer Option 4')

        grammerButton1.grid(row=2, column=1)
        grammerButton2.grid(row=2, column=3)
        grammerButton3.grid(row=3, column=1)
        grammerButton4.grid(row=3, column=3)

        addConventionsButton = Button(self.master, text='Add Conventions')
        addConventionsButton.grid(row=4, column=2)

        editTranscriptionButton = Button(self.master, text='Edit Transcription')
        editTranscriptionButton.grid(row=6, column=1)
        exportButton = Button(self.master, text='Export to Word Document')
        exportButton.grid(row=6, column=4)
        printButton = Button(self.master, text='Print')
        printButton.grid(row=7, column=4)

        transcription = Text(self.master)
        transcription.grid(row=5, column=0, columnspan=3)

        transcriptionWithGrammer = Text(self.master)
        transcriptionWithGrammer.grid(row=5, column=3, columnspan=3)


        self.master.mainloop()

if __name__ == "__main__":
    myGui = GUI()
