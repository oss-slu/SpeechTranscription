from docx import Document
from datetime import date
import os
import sys

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

class Exporter:
    def exportToWord(self, transcriptionText: str, outputPath: str):
        exportDocument = Document()
        exportDocument.add_paragraph(transcriptionText)
        exportDocument.save(outputPath)
        
    def getDefaultFilename(self):
        return str(date.today()) + "_SALT_Transcription"
        
    def printTranscription(self, transcriptionText: str):
        # TODO: Add functionality to print the transcription
        print(transcriptionText)