import logging
import os
import nltk

import addConventions


#looking into the bundled nltk_data first (frozen app)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLED_NLTK = os.path.join(APP_DIR, "nltk_data")
if os.path.exists(BUNDLED_NLTK):
    nltk.data.path.insert(0, BUNDLED_NLTK)
else:
    logging.warning("grammar.py: bundled nltk_data not found, using system paths.")

#trying to load the resources, but DO NOT download at runtime on client machines
MISSING_NLTK = []

def _ensure_resource(res_name, path):
    try:
        nltk.data.find(path)
    except LookupError:
        # we don't download here — we just record that it's missing
        logging.warning(f"grammar.py: NLTK resource missing: {res_name} ({path})")
        MISSING_NLTK.append(res_name)

_ensure_resource("punkt", "tokenizers/punkt")
_ensure_resource("averaged_perceptron_tagger", "taggers/averaged_perceptron_tagger")
_ensure_resource("wordnet", "corpora/wordnet")


class GrammarChecker:
    tokenizedSentences = []
    checkAllSentences = False
    
    def checkGrammar(self, transcriptionText: str, checkAllSentences: bool):
        self.checkAllSentences = checkAllSentences
        if "punkt" in MISSING_NLTK:
            logging.warning("grammar.py: punkt missing, using fallback sentence split.")
            self.tokenizedSentences = [s.strip() for s in transcriptionText.split(".") if s.strip()]
        else:
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