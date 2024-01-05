from docx import Document
from datetime import date

class Exporter:
    def exportToWord(self, transcriptionText: str, outputPath: str):
        exportDocument = Document()
        exportDocument.add_paragraph(transcriptionText)
        exportDocument.save(outputPath + "/" + str(date.today())+"_SALT_Transcription.docx")
        
    def printTranscription(self, transcriptionText: str):
        # TODO: Add functionality to print the transcription
        print(transcriptionText)