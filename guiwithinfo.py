from tkinter import Button, Checkbutton, IntVar, Label, Text, Entry, StringVar, OptionMenu
import tkinter as tk
import speechrecog.recogtest

class GUI:
    def __init__(self):
        self.master = tk.Tk()
        self.master.title('Speech Transcription')
        self.master.geometry('960x540')

        # Sends client info submitted by user to the transciption box
        def submitClientInfo() :
            # Gets the current text in the entry box
            infoEntryText = infoEntry.get()
            # Prints the relevant field
            if (clicked.get() == "Name"):
                transcription.insert("end", "Name: ")
            elif (clicked.get() == "Age"):
                transcription.insert("end", "Age: ")
            elif (clicked.get() == "Gender"):
                transcription.insert("end", "Gender: ")
            elif (clicked.get() == "Date of Birth"):
                transcription.insert("end", "Date of Birth: ")
            elif (clicked.get() == "Date of Sample"):
                transcription.insert("end", "Date of Sample: ")
            elif (clicked.get() == "Examiner Info"):
                transcription.insert("end", "Examiner Info: ")
            elif (clicked.get() == "Sampling Context"):
                transcription.insert("end", "Sampling Context: ")
            # Appends the submitted text after the field name
            transcription.insert("end", infoEntryText + "\n")
            # Clears the entry box
            infoEntry.delete(0, "end")

        def transcribe() :
            speechrecog.recogtest

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
                "Date of Birth",
                "Date of Sample",
                "Examiner Info",
                "Sampling Context"
                ]
        clicked = StringVar()
        clicked.set("Name")
        infoDropdown = OptionMenu(self.master, clicked, *clientOptions)
        infoDropdown.grid(row=1, column=1)

        infoEntry = Entry(self.master)
        infoEntry.grid(row=1, column=2)

        infoSubmit = Button(self.master, text="Submit", command=submitClientInfo)
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
