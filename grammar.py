import addConventions
import nltk
import threading

class GrammarChecker:
    tokenizedSentences = []
    checkAllSentences = False
    correctedText = ""  # To store the corrected transcription

    def __init__(self):
        self.transcriptionInProgress = False
        self.grammarChecked = False

    # Triggered as soon as transcription begins
    def startGrammarCheck(self, transcriptionText: str, checkAllSentences: bool):
        self.checkAllSentences = checkAllSentences
        self.tokenizedSentences = nltk.sent_tokenize(transcriptionText)
        self.transcriptionInProgress = True
        self.grammarChecked = False
        
        # Run grammar check in a background thread to avoid blocking UI
        threading.Thread(target=self._processGrammarCheck).start()

    # Grammar check runs in the background
    def _processGrammarCheck(self):
        corrected = ""
        while self.tokenizedSentences:
            sentenceToCorrect = addConventions.correctSentence(self.tokenizedSentences[0])
            if self.tokenizedSentences[0] != sentenceToCorrect or self.checkAllSentences:
                corrected += str(sentenceToCorrect) + "\n"
            else:
                corrected += str(self.tokenizedSentences[0]) + "\n"
            
            # Remove the processed sentence from the list
            del self.tokenizedSentences[0]
        
        # Store the grammar-checked text
        self.correctedText = corrected
        self.grammarChecked = True
        self.transcriptionInProgress = False  # Process is complete

    # Retrieve the corrected text when the user clicks Grammar Check
    def getGrammarCheckedText(self):
        if self.transcriptionInProgress:
            return "Transcription and grammar check are still in progress. Please wait."
        
        if self.grammarChecked:
            return self.correctedText
        else:
            return "No grammar corrections have been made yet."

    # To retrieve inflectional morphemes if needed
    def getInflectionalMorphemes(self, converting: str):
        return addConventions.addInflectionalMorphemes(converting)
