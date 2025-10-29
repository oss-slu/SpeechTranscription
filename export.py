from docx import Document
from datetime import date
import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,  
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler("app.log", mode="a"))

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