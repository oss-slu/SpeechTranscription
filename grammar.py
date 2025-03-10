import addConventions
import nltk
from threading import Thread
from functools import partial

class GrammarChecker:
    tokenizedSentences = []
    checkAllSentences = False
    grammarCheckedText = ""  # To store grammar-checked transcription
    
    def __init__(self):
        self.isGrammarChecked = False  # Flag to track if grammar has been checked
    
    # Function to trigger grammar check in the background
    def triggerGrammarCheck(self, transcriptionText: str, checkAllSentences: bool):
        # Start grammar check in the background without affecting transcription performance
        self.isGrammarChecked = False
        self.tokenizedSentences = nltk.sent_tokenize(transcriptionText)
        self.checkAllSentences = checkAllSentences
        
        # Use partial or lambda to pass arguments to checkGrammar function in the thread
        grammarThread = Thread(target=partial(self.checkGrammar, transcriptionText, checkAllSentences))
        grammarThread.start()

    # Background function to check grammar
    def checkGrammar(self, transcriptionText: str, checkAllSentences: bool):
        self.tokenizedSentences = nltk.sent_tokenize(transcriptionText)
        self.checkAllSentences = checkAllSentences
        corrected = ""

        while len(self.tokenizedSentences):
            sentenceToCorrect = addConventions.correctSentence(self.tokenizedSentences[0])
            if (self.tokenizedSentences[0] != sentenceToCorrect) or self.checkAllSentences:
                corrected += str(sentenceToCorrect) + "\n"
            else:
                corrected += str(self.tokenizedSentences[0]) + "\n"
            del self.tokenizedSentences[0]
        
        self.grammarCheckedText = corrected  # Store the grammar-checked text
        self.isGrammarChecked = True  # Mark grammar check as complete

    # Function to retrieve the grammar-checked text when Grammar Check button is clicked
    def getGrammarCheckedText(self):
        if self.isGrammarChecked:
            return self.grammarCheckedText
        else:
            return "Grammar check is still in progress. Please wait."

    # Function to get next correction (as per original functionality)
    def getNextCorrection(self):
        corrected = ""
        if len(self.tokenizedSentences) == 0:
            return (None, None)
        while len(self.tokenizedSentences):
            sentenceToCorrect = addConventions.correctSentence(self.tokenizedSentences[0])
            if (self.tokenizedSentences[0] != sentenceToCorrect) or self.checkAllSentences:
                del self.tokenizedSentences[0]
                return (corrected, str(sentenceToCorrect))
            else:
                corrected += str(self.tokenizedSentences[0]) + "\n"
                del self.tokenizedSentences[0]
        return (corrected, None)
    
    def getInflectionalMorphemes(self, converting: str):
        return addConventions.addInflectionalMorphemes(converting)
