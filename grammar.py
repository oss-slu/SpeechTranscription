import logging
import os
import sys
import nltk

import addConventions

# ---------------------------------------------------------------------------
# Frozen-app NLTK data resolution
# ---------------------------------------------------------------------------
# When running as a PyInstaller-bundled executable, NLTK data is bundled
# inside the app and extracted to sys._MEIPASS.  We point NLTK there first.
# Runtime downloads are NOT attempted — all data is bundled at build time.
# ---------------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    _base_dir = sys._MEIPASS
else:
    _base_dir = os.path.dirname(os.path.abspath(__file__))

BUNDLED_NLTK = os.path.join(_base_dir, "nltk_data")
if os.path.exists(BUNDLED_NLTK):
    nltk.data.path.insert(0, BUNDLED_NLTK)

# Verify that critical NLTK resources are available; log warnings if missing
# but do NOT attempt downloads (would fail in frozen app without network).
MISSING_NLTK = []

def _ensure_resource(res_name, path):
    try:
        nltk.data.find(path)
    except LookupError:
        MISSING_NLTK.append(res_name)
        logging.warning("grammar.py: NLTK resource '%s' not found at path '%s'", res_name, path)

_ensure_resource("punkt", "tokenizers/punkt")
_ensure_resource("punkt_tab", "tokenizers/punkt_tab")
_ensure_resource("averaged_perceptron_tagger", "taggers/averaged_perceptron_tagger")
_ensure_resource("wordnet", "corpora/wordnet")

class GrammarChecker:
    tokenizedSentences = []
    checkAllSentences = False
    
    def checkGrammar(self, transcriptionText: str, checkAllSentences: bool):
        self.checkAllSentences = checkAllSentences
        if "punkt" in MISSING_NLTK and "punkt_tab" in MISSING_NLTK:
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