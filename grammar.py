from functions import addConventions
import nltk

class GrammarChecker:
    tokenizedSentences = []
    checkAllSentences = False
    
    def checkGrammar(self, transcriptionText: str, checkAllSentences: bool):
        self.checkAllSentences = checkAllSentences
        self.tokenizedSentences = nltk.sent_tokenize(transcriptionText)
    
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