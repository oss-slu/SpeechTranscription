import addConventions
import nltk
import threading

class GrammarChecker:
    def __init__(self):
        self.tokenizedSentences = []
        self.correctedSentences = []
        self.checkAllSentences = False
        self.isProcessed = False  # Flag to check if grammar processing is completed

    def checkGrammar(self, transcriptionText: str, checkAllSentences: bool):
        """
        Starts grammar checking as soon as transcription begins.
        Runs in a separate thread to prevent blocking the transcription process.
        """
        self.checkAllSentences = checkAllSentences
        self.tokenizedSentences = nltk.sent_tokenize(transcriptionText)
        self.correctedSentences = []
        self.isProcessed = False
        
        # Run grammar check in the background
        thread = threading.Thread(target=self._processGrammar)
        thread.start()

    def _processGrammar(self):
        """Processes grammar checking in the background."""
        for sentence in self.tokenizedSentences:
            correctedSentence = addConventions.correctSentence(sentence)
            if self.checkAllSentences or sentence != correctedSentence:
                self.correctedSentences.append(correctedSentence)
            else:
                self.correctedSentences.append(sentence)
        self.isProcessed = True  # Mark processing as complete

    def getNextCorrection(self):
        """Retrieves the next corrected sentence instantly without delay."""
        if not self.isProcessed:
            return (None, None)  # Ensure processing is completed before fetching corrections
        
        if not self.correctedSentences:
            return (None, None)
        
        return ("", self.correctedSentences.pop(0))
    
    def getInflectionalMorphemes(self, converting: str):
        return addConventions.addInflectionalMorphemes(converting)
