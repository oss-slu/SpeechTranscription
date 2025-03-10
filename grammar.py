import addConventions
import nltk
import threading
import time


class GrammarChecker:
    def __init__(self):
        self.tokenizedSentences = []
        self.checkAllSentences = False
        self.processed_text = None  # Store processed text for quick retrieval
        self.grammar_thread = None  # Track background thread

    def checkGrammar(self, transcriptionText: str, checkAllSentences: bool):
        """Starts grammar check immediately in a background thread"""
        self.checkAllSentences = checkAllSentences
        self.tokenizedSentences = nltk.sent_tokenize(transcriptionText)
        self.processed_text = "Processing..."

        # Process grammar check in a separate thread
        if not self.grammar_thread or not self.grammar_thread.is_alive():
            self.grammar_thread = threading.Thread(target=self._processGrammar, daemon=True)
            self.grammar_thread.start()

    def _processGrammar(self):
        """Runs grammar checking in the background"""
        corrected_sentences = []
        for sentence in self.tokenizedSentences:
            corrected_sentence = addConventions.correctSentence(sentence)
            if corrected_sentence != sentence or self.checkAllSentences:
                corrected_sentences.append(corrected_sentence)
            else:
                corrected_sentences.append(sentence)

        # Store the processed text for quick access
        self.processed_text = "\n".join(corrected_sentences)

    def getCorrectedText(self):
        """Returns pre-processed corrected text"""
        return self.processed_text if self.processed_text else "Processing..."
    
    def getInflectionalMorphemes(self, converting: str):
        return addConventions.addInflectionalMorphemes(converting) 

# Step 1: Creates an instance of GrammarChecker
grammar_checker = GrammarChecker()

# Step 2: Automatically start grammar checking when transcription begins
def startTranscription(transcriptionText: str):
    grammar_checker.checkGrammar(transcriptionText=transcriptionText, checkAllSentences=True)

# Step 3: Retrieve the corrected text when the Grammar Check button is clicked
def getGrammarCheckedText():
    return grammar_checker.getCorrectedText()

# Example usage
transcriptionText = "Your transcription text here"
startTranscription(transcriptionText)  # Automatically starts grammar checking

# When user clicks the Grammar Check button:
corrected_text = getGrammarCheckedText()
print(corrected_text)  # Instantly displays the corrected text
