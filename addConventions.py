import logging
import nltk
from nltk import sent_tokenize, word_tokenize, pos_tag, WordNetLemmatizer
from textblob import TextBlob  # Added for Python-only grammar/spelling correction

try:
    from pattern.text.en import conjugate as pattern_conjugate
    PATTERN_AVAILABLE = True
except Exception as e:
    logging.warning(f"addConventions: pattern.text.en not available (likely wordnet): {e}")
    PATTERN_AVAILABLE = False

def safe_conjugate(word: str, **kwargs) -> str:
    if PATTERN_AVAILABLE:
        try:
            return pattern_conjugate(word, **kwargs)
        except Exception as e:
            logging.warning(f"addConventions: conjugate failed for '{word}': {e}")
            return word
    return word

wnl = WordNetLemmatizer()


def isToBeVerb(verb):
    toBeVerbs = ["am", "is", "are", "will be", "was", "were", "been",
                 "'m", "'s", "'re"]
    return verb in toBeVerbs


def removeErrorCoding(x):
    words = x.split()
    sentence = ""
    repeatedWordFlag = False
    for word in words:
        if repeatedWordFlag:
            if ")" in word:
                repeatedWordFlag = False
        elif "[" in word:
            if ":" in word:
                colonIndex = word.find(":")
                closeBracketIndex = word.find("]")
                sentence += word[colonIndex + 1:closeBracketIndex] + " "
        elif "/*3s" in word:
            try:
                safe_conjugate(word.replace("/*3s", ""))
            except:
                pass
            sentence += safe_conjugate(word.replace("/*3s", ""), tense="present",
                                       person=3, number="singular",
                                       mood="indicative", aspect="imperfective",
                                       negated=False) + " "
        elif "*" in word:
            sentence += word.replace("*", "") + " "
        elif "(" in word:
            repeatedWordFlag = True
        else:
            sentence += word + " "
    return sentence.rstrip()


def addInflectionalMorphemes(x):
    sentences = sent_tokenize(x)
    converting = ""
    for sentence in sentences:
        if "[" in sentence or "*" in sentence or "(" in sentence:
            errorCodingRemoved = removeErrorCoding(sentence)
            morphemesOnCorrectedSentence = addInflectionalMorphemesToSentence(errorCodingRemoved)
            originalWords = sentence.split()
            correctedWords = morphemesOnCorrectedSentence.split()
            finalSentence = ""
            originalWordIndex = 0
            correctedWordIndex = 0
            while originalWordIndex < len(originalWords):
                if "[EW]" in originalWords[originalWordIndex]:
                    finalSentence += originalWords[originalWordIndex] + " "
                    originalWordIndex += 1
                elif "[" in originalWords[originalWordIndex] or "*" in originalWords[originalWordIndex]:
                    finalSentence += originalWords[originalWordIndex] + " "
                    originalWordIndex += 1
                    correctedWordIndex += 1
                elif "(" in originalWords[originalWordIndex]:
                    finalSentence += originalWords[originalWordIndex] + " "
                    correctedWord = originalWords[originalWordIndex][1:]
                    originalWordIndex += 1
                    while (originalWordIndex < len(originalWords) and
                           originalWords[originalWordIndex].lower().replace('.', '').replace('?', '').replace('!', '').replace(',', '') == correctedWord.lower() or
                           originalWords[originalWordIndex].lower().replace('.', '').replace('?', '').replace('!', '').replace(',', '') == correctedWord.lower() + ")"):
                        finalSentence += originalWords[originalWordIndex] + " "
                        originalWordIndex += 1
                    correctedWordIndex += 1
                else:
                    if correctedWordIndex < len(correctedWords):
                        finalSentence += correctedWords[correctedWordIndex] + " "
                    elif originalWordIndex < len(originalWords):
                        finalSentence += originalWords[originalWordIndex] + " "
                    originalWordIndex += 1
                    correctedWordIndex += 1
            converting += finalSentence + "\n"
        else:
            converting += addInflectionalMorphemesToSentence(sentence) + "\n"
    return converting


def addInflectionalMorphemesToSentence(x):
    tokens = pos_tag(word_tokenize(x))
    converted = ""
    mostRecentVerbIsToBe = False
    for tuple in tokens:
        word, pos = tuple
        if word in ["C", "E"]:
            converted += "\n" + word + " "
        elif pos == "NNS" and word[-1] == 's':
            converted += wnl.lemmatize(word, "n") + "/s "
        elif word == "'s" and pos == "POS":
            converted = converted[:-1] + "/z "
        elif word == "'s":
            converted = converted[:-1] + "/'s "
        elif pos == "VBD" and word[-2:] == "ed":
            converted += wnl.lemmatize(word, "v") + "/ed "
        elif pos == "VBZ" and word not in ["is", "has"]:
            converted += wnl.lemmatize(word, "v") + "/3s "
        elif pos == "VBG" and mostRecentVerbIsToBe:
            if wnl.lemmatize(word, "v") == word:
                converted += wnl.lemmatize(word, "v") + " "
            else:
                converted += wnl.lemmatize(word, "v") + "/ing "
        elif word in ["n't", "'t", "'ll", "'m", "'d", "'re", "'ve"]:
            converted = converted[:-1] + word + " "
        elif word in [",", ".", "?", "!", ";"]:
            if word not in [",", ";"]:
                converted = converted[:-1] + word
            else:
                converted = converted[:-1] + word + " "
        else:
            converted += word + " "

        if pos in ["VB", "VBD", "VBP", "VBZ"] or word == "been":
            mostRecentVerbIsToBe = isToBeVerb(word)
        else:
            mostRecentVerbIsToBe = False

    converted = converted.replace("ca/n't", "can/'t")
    converted = converted.replace("do/n't", "don't")
    return converted


def correctSentence(x):
    """
    Python-only SALT correction using TextBlob.
    Replaces language_tool_python with TextBlob for spelling correction.
    """
    blob = TextBlob(x)
    corrected_text = str(blob.correct())  # automatic spelling correction

    originalWords = x.split()
    correctedWords = corrected_text.split()
    originalIndex = 0
    correctedIndex = 0
    saltSentence = ""

    while originalIndex < len(originalWords) or correctedIndex < len(correctedWords):
        if originalIndex >= len(originalWords):
            while correctedIndex < len(correctedWords):
                saltSentence += correctedWords[correctedIndex] + "* "
                correctedIndex += 1
        elif correctedIndex >= len(correctedWords):
            while originalIndex < len(originalWords):
                saltSentence += originalWords[originalIndex] + "* "
                originalIndex += 1
        elif originalWords[originalIndex].lower() == correctedWords[correctedIndex].lower():
            saltSentence += originalWords[originalIndex] + " "
            originalIndex += 1
            correctedIndex += 1
        else:
            saltSentence += originalWords[originalIndex] + "[EW:" + correctedWords[correctedIndex] + "] "
            originalIndex += 1
            correctedIndex += 1

    return saltSentence.strip()