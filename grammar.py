import addConventions
import nltk
import threading
import time



class GrammarChecker:
    def __init__(self):
        self.tokenizedSentences = []
        self.checkAllSentences = False
        self.processed_text = None  # Store processed text for quick retrieval


    def checkGrammar(self, transcriptionText: str, checkAllSentences: bool):
        """Starts grammar check immediately in a background thread"""
        self.checkAllSentences = checkAllSentences
        self.tokenizedSentences = nltk.sent_tokenize(transcriptionText)

        # Process grammar check in a separate thread
        threading.Thread(target=self._processGrammar, daemon=True).start()


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
        return self.processed_text or "Processing..."
    
    
    def getInflectionalMorphemes(self, converting: str):
        return addConventions.addInflectionalMorphemes(converting) 
    
# Step 1: Creates an instance of GrammarChecker
grammar_checker = GrammarChecker()

# Step 2: Start grammar checking in the background
transcriptionText = "Your transcription text here"  # Example text
grammar_checker.checkGrammar(transcriptionText=transcriptionText, checkAllSentences=True)

# Step 3: Wait for grammar check to finish
while grammar_checker.getCorrectedText() == "Processing...":
    time.sleep(1)  # Wait for 1 second and check again

# Step 4: Retrieve and use the corrected text
corrected = grammar_checker.getCorrectedText()  # Get corrected text
print(corrected)  # Print the corrected text 