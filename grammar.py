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
        """Perform grammar check and return corrected version with timestamps preserved."""
        corrected_lines = []

        for line in transcriptionText.strip().splitlines():
            if line.strip() == "":
                continue  # Skip empty lines

            # Expect format like: [0:10] some sentence
            if line.startswith("[") and "]" in line:
                timestamp_end = line.find("]") + 1
                timestamp = line[:timestamp_end]
                sentence = line[timestamp_end:].strip()
                corrected_sentence = addConventions.correctSentence(sentence)
                corrected_lines.append(f"{timestamp} {corrected_sentence}")
            else:
                # If there's no timestamp, just correct the whole line
                corrected_lines.append(addConventions.correctSentence(line))

        return "\n".join(corrected_lines)

    
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
