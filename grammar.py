import logging
import os
import sys

import nltk

from java_runtime import get_base_path

# Prefer bundled nltk_data (PyInstaller _MEIPASS or source tree) before any download.
BUNDLED_NLTK = os.path.join(get_base_path(), "nltk_data")
if os.path.exists(BUNDLED_NLTK):
    nltk.data.path.insert(0, BUNDLED_NLTK)

_FROZEN = getattr(sys, "frozen", False)

# Never download NLTK corpora inside the packaged app (no network / SSL on clients).
if not _FROZEN:
    for _pkg in (
        "punkt_tab",
        "averaged_perceptron_tagger_eng",
        "wordnet",
        "wordnet_ic",
    ):
        try:
            nltk.download(_pkg, quiet=True)
        except Exception as exc:  # noqa: BLE001 - best-effort for local/dev
            logging.warning("grammar.py: nltk.download(%s) failed: %s", _pkg, exc)

import addConventions  # noqa: E402  - after NLTK path / download setup

MISSING_NLTK = []


def _ensure_resource(res_name, path):
    try:
        nltk.data.find(path)
    except LookupError:
        if _FROZEN:
            logging.warning(
                "grammar.py: missing bundled NLTK resource %s (%s)", res_name, path
            )
            MISSING_NLTK.append(res_name)
            return
        try:
            nltk.download("punkt_tab", quiet=True)
            nltk.download("averaged_perceptron_tagger_eng", quiet=True)
            nltk.download("wordnet", quiet=True)
        except Exception as exc:  # noqa: BLE001
            logging.warning("grammar.py: nltk download fallback failed: %s", exc)
            MISSING_NLTK.append(res_name)


_ensure_resource("punkt", "tokenizers/punkt")
_ensure_resource("averaged_perceptron_tagger_eng", "taggers/averaged_perceptron_tagger_eng")
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
