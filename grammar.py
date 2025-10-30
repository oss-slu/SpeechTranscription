import addConventions
import nltk

nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')

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
    
    def getInflectionalMorphemes(self, converting: str):
        return addConventions.addInflectionalMorphemes(converting)