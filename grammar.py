import addConventions
import nltk

class GrammarChecker:
    tokenizedSentences = []
    checkAllSentences = False
    lastCheckedText = ""  
    grammarCheckedText = ""

    
    def checkGrammar(self, transcriptionText: str, checkAllSentences: bool):
        self.checkAllSentences = checkAllSentences
        self.tokenizedSentences = nltk.sent_tokenize(transcriptionText)
        self.lastCheckedText = transcriptionText  # ⬅️ Cache it
        self.grammarCheckedText = self.performGrammarCheck(transcriptionText)

    def performGrammarCheck(self, transcriptionText: str):
        """Perform grammar check and return the corrected version."""
        # Perform grammar check logic here (simplified)
        corrected_text = addConventions.correctSentence(transcriptionText)
        return corrected_text

    
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

    def getGrammarText(self):
        """Return the grammar-checked text."""
        return self.grammarCheckedText
