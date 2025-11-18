import logging
from nltk import sent_tokenize, word_tokenize, pos_tag, WordNetLemmatizer
import language_tool_python
from pattern.text.en import conjugate
import os
import sys

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

wnl = WordNetLemmatizer()
tool = language_tool_python.LanguageTool("en-US")

def isToBeVerb(verb):
    toBeVerbs = ["am", "is", "are", "will be", "was", "were", "been",
                 "'m", "'s", "'re"]
    if (verb in toBeVerbs):
        return True
    else:
        return False

# This function removes error coding from a sentence, leaving us with a grammatically correct sentence so NLTK can process it
def removeErrorCoding(x):
    words = x.split()
    sentence = ""
    repeatedWordFlag = False
    for word in words:
        # Currently handling repeated words
        if (repeatedWordFlag == True):
            # Ends handling of repeated words (')' indicates the end)
            if (")" in word):
                repeatedWordFlag = False
            # Continues handling of repeated words (')' has not yet been reached)
            else:
                pass       
        # Handles all cases where there is error coding with a bracket
        elif ("[" in word):
            # This case handles bracketed error codes that also have a suggestion by getting the substring between : and ]
            # ex: "are[EW:is]"" returns "is"
            if (":" in word):
                colonIndex = word.find(":")
                closeBracketIndex = word.find("]")
                sentence += word[colonIndex + 1:closeBracketIndex] + " "
            # This case handles extra words ([EW]) by not appending them to the corrected sentence
            # ex: "at[EW]" returns ""
            else:
                pass
        elif("/*3s" in word):
            # This try-catch block is NECESSARY. The "pattern" library is not being maintained and slightly broke with Python 3.7. This bypasses the problem.
            try:
                safe_conjugate(word.replace("/*3s", ""))
            except:
                pass
            sentence += safe_conjugate(word.replace("/*3s", ""), tense = "present", person = 3, number = "singular", mood = "indicative", aspect = "imperfective", negated = False)
            sentence += " "
       
        # Handles missing word case (*)
        elif ("*" in word):
            sentence += word.replace("*", "") + " "
        # Begins handling of repeated word case
        elif ("(" in word):
            repeatedWordFlag = True
        # Word has no error coding, can be appended as normal
        else:
            sentence += word + " "

    # Removes final space
    if (sentence[-1] == " "):
        sentence = sentence[:-1]
    return sentence

# Splits transcription into sentences first, then sends each sentence to addInflectionalMorphemesToSentence()
# Sentences with error coding are sent to removeErrorCoding() first so NLTK can process them
def addInflectionalMorphemes(x):
    sentences = []
    
    sentences = sent_tokenize(x)
    converting = "" # Will contain entire transcript fully corrected at end of function
    for sentence in sentences:
        # There is error coding in the sentence
        if ("[" in sentence or "*" in sentence or "(" in sentence):
            # First, removes error coding then applies morphemes to clean sentence
            errorCodingRemoved = removeErrorCoding(sentence)
            morphemesOnCorrectedSentence = addInflectionalMorphemesToSentence(errorCodingRemoved)
            # Splits both forms of sentence into words
            originalWords = sentence.split()
            correctedWords = morphemesOnCorrectedSentence.split()
            # Forms final sentence by combining morphemes from corrected sentence and error coding from original sentence
            finalSentence = ""
            originalWordIndex = 0
            correctedWordIndex = 0
            while (originalWordIndex < len(originalWords)):
                # Extra word; was not processed during saltification so do NOT increment correctedWordIndex
                if ("[EW]" in originalWords[originalWordIndex]):
                    finalSentence += originalWords[originalWordIndex] + " "
                    originalWordIndex += 1
                # Word contains error coding; preserve it from original sentence
                elif ("[" in originalWords[originalWordIndex] or "*" in originalWords[originalWordIndex]):
                    finalSentence += originalWords[originalWordIndex] + " "
                    originalWordIndex += 1
                    correctedWordIndex += 1
                # Word contains marker for beginning of repeated words; preserve it from original sentence
                elif ("(" in originalWords[originalWordIndex]):
                    finalSentence += originalWords[originalWordIndex] + " "
                    correctedWordIndex += 1
                    repeatedWord = originalWords[originalWordIndex][1:] # Remove parenthesis
                    originalWordIndex += 1
                    if (originalWordIndex < len(originalWords)):
                        # While words are repeating, preserve from original
                        potentialRepeat = originalWords[originalWordIndex].lower().replace('.', '').replace('?', '').replace('!', '').replace(',', '')
                        while ((originalWordIndex < len(originalWords)) and (potentialRepeat == repeatedWord.lower() or potentialRepeat == repeatedWord.lower() + ")")):
                            finalSentence += originalWords[originalWordIndex] + " "
                            originalWordIndex += 1
                # Original word has no error coding; get word from saltified sentence 
                else:
                    if correctedWordIndex < len(correctedWords): finalSentence += correctedWords[correctedWordIndex] + " "
                    elif originalWordIndex < len(originalWords): finalSentence += originalWords[originalWordIndex] + " "
                    originalWordIndex += 1
                    correctedWordIndex += 1
            converting += finalSentence + "\n"
        # There is no error coding in the sentence
        else: 
            converting += addInflectionalMorphemesToSentence(sentence) + "\n"
    return converting

def addInflectionalMorphemesToSentence(x):
    # Creates tuples for each word or contraction with their part of speech
    tokens = pos_tag(word_tokenize(x))
    converted = ""
    mostRecentVerbIsToBe = False
    for tuple in tokens:
        # Token is C or E for child/examiner
        if (tuple[0] == "C" or tuple[0] == "E"):
            converted += "\n" + tuple[0] + " "
        # Token is plural and ends in s
        elif (tuple[1] == "NNS" and tuple[0][-1] == 's'):
            converted += wnl.lemmatize(tuple[0], "n") + "/s "
        # Token is "'s" and is possessive
        elif (tuple[0] == "'s" and tuple[1] == "POS"):
            converted = converted[:-1] + "/z "
        # Token is "'s" and is verb contraction
        elif (tuple[0] == "'s"):
            converted = converted[:-1] + "/'s "
        # Token is past tense verb ending in "ed"
        elif (tuple[1] == "VBD" and tuple[0][-2:] == "ed"):
            converted += wnl.lemmatize(tuple[0], "v") + "/ed "
        # Token is third-person singular present verb
        elif (tuple[1] == "VBZ" and tuple[0] != "is" and tuple[0] != "has"):
            converted += wnl.lemmatize(tuple[0], "v") + "/3s "
        # Token is present participle
        elif (tuple[1] == "VBG" and mostRecentVerbIsToBe):
            if wnl.lemmatize(tuple[0], "v") == tuple[0]:
                converted += wnl.lemmatize(tuple[0], "v") + " "
            else:
                converted += wnl.lemmatize(tuple[0], "v") + "/ing "
        # Contraction tokens
        elif (tuple[0] == "n't"):
            converted = converted[:-1] + "/n't "
        elif (tuple[0] == "'t"):
            converted = converted[:-1] + "/'t "
        elif (tuple[0] == "'ll"):
            converted = converted[:-1] + "/'ll "
        elif (tuple[0] == "'m"):
            converted = converted[:-1] + "/'m "
        elif (tuple[0] == "'d"):
            converted = converted[:-1] + "/'d "
        elif (tuple[0] == "'re"):
            converted = converted[:-1] + "/'re "
        elif (tuple[0] == "'ve"):  
            converted = converted[:-1] + "/'ve "
        # Token is punctuation
        elif (tuple[0] == "," or tuple[0] == "." or tuple[0] == "?" or tuple[0] == "!" or tuple[0] == ";"):
            if (tuple[0] != "," and tuple[0] != ";"):
                converted = converted[:-1] + tuple[0]
            else:
                converted = converted[:-1] + tuple[0] + " "
        # Token is a word with no changes needed
        else:
            converted += tuple[0] + " "
        # Updates mostRecentVerbIsToBe to be used to distinguish later potential gerunds from participles
        # (Participles should be given /ing convention while gerunds should not, so this flag is used for that)
        if (tuple[1] == "VB" or tuple[1] == "VBD" or tuple[1] == "VBP" or tuple[1] == "VBZ" or tuple[0] == "been"):
            if (isToBeVerb(tuple[0])):
                mostRecentVerbIsToBe = True 
            else:
                mostRecentVerbIsToBe = False

    # Manual replacements for irregular cases
    converted = converted.replace("ca/n't", "can/'t")
    converted = converted.replace("do/n't", "don't")

    return converted

# Takes a sentence x and returns the correct form in SALT standard with error coding
def correctSentence(x) :
    is_bad_rule = lambda rule: rule.category == 'PUNCTUATION' or rule.message == 'This word is normally spelled with a hyphen.' or rule.message == 'Possible typo: you repeated a word'
    matches = tool.check(x)
    matches = [rule for rule in matches if not is_bad_rule(rule)]
    # print(matches) # Can be used to identify what error the tool is recognizing
    corrected = language_tool_python.utils.correct(x, matches)
    originalWords = x.split()
    correctedWords = corrected.split()
    originalIndex = 0
    correctedIndex = 0
    saltSentence = ""
    while (originalIndex < len(originalWords) or correctedIndex < len(correctedWords)):
        #print('original words:', originalWords)
        # Words only remain in the corrected sentence, append all with asterisk (missing word)
        if (originalIndex >= len(originalWords)):
            while (correctedIndex < len(correctedWords)):
                saltSentence += correctedWords[correctedIndex] + "* "
                correctedIndex += 1
        # Words only remain in the original sentence, append all unchanged
        elif (correctedIndex >= len(correctedWords)):
            while (originalIndex < len(originalWords)):
                saltSentence += originalWords[originalIndex] + "* "
                originalIndex += 1
        # The current word in each sentence is the same
        # Check if the original sentence repeated the word several times,
        # if so provide correct coding "(And and) and" and increment accordingly
        # Otherwise, simply append and increment both sentences by one
        elif (originalWords[originalIndex] == correctedWords[correctedIndex]):
            repeatCounter = 0
            punctuationFlag = False
            punctuation = ['.', '?', '!', ',']
            foundPunctuation = ""
            while (originalIndex + repeatCounter + 1 < len(originalWords) and originalWords[originalIndex + repeatCounter + 1].lower().replace('.', '').replace('?', '').replace('!', '').replace(',', '') == correctedWords[correctedIndex].lower()):
                if any(x in originalWords[originalIndex + repeatCounter + 1] for x in punctuation):
                    punctuationFlag = True
                    # Get final character, which should be punctuation
                    foundPunctuation = originalWords[originalIndex + repeatCounter + 1][-1]
                repeatCounter += 1
            if (repeatCounter > 0):
                repeatedWord = originalWords[originalIndex]
                saltSentence += "(" + repeatedWord
                for i in range(repeatCounter-1):
                    saltSentence += " " + repeatedWord
                saltSentence += ") " + repeatedWord + " "
                if (punctuationFlag == True):
                    saltSentence = saltSentence[:-1]
                    saltSentence += foundPunctuation + " "
                originalIndex += repeatCounter + 1
                correctedIndex += repeatCounter + 1
            else:
                saltSentence += originalWords[originalIndex] + " "
                originalIndex += 1
                correctedIndex += 1
        # The current word in the original sentence matches the next word in the corrected one, append word in corrected with asterisk
        # (Checks to make sure index won't go out of bounds)
        elif (correctedIndex < len(correctedWords)-1 and originalWords[originalIndex] == correctedWords[correctedIndex+1]):
            #print('corrected Index:', correctedIndex)
            #print('corrected Words len:', len(correctedWords))
            saltSentence += correctedWords[correctedIndex] + "* "
            correctedIndex += 1
        # The current word in the corrected sentence matches the next word in the original one, append word in original with [EW]
        # (Checks to make sure index won't go out of bounds)
        elif (originalIndex + 1 < len(originalWords) and originalWords[originalIndex+1] == correctedWords[correctedIndex]):
            saltSentence += originalWords[originalIndex] + "[EW] "
            originalIndex += 1
        # If either index is at the last element, default to word-level error
        elif (originalIndex == len(originalWords) - 1 or correctedIndex == len(correctedWords) - 1):
            saltSentence += originalWords[originalIndex] + "[EW:" + correctedWords[correctedIndex] + "] "
            originalIndex += 1
            correctedIndex += 1
        # Word-level error if both words up next are matching
        elif (originalWords[originalIndex+1] == correctedWords[correctedIndex+1]):
            if (correctedWords[correctedIndex].endswith('s') and ((wnl.lemmatize(correctedWords[correctedIndex], 'v') == originalWords[originalIndex]) and originalWords[originalIndex] != "have")):
                saltSentence += originalWords[originalIndex] + "/*3s "
            else:
                saltSentence += originalWords[originalIndex] + "[EW:" + correctedWords[correctedIndex] + "] "
            originalIndex += 1
            correctedIndex += 1
        # Both words up next do not match, defer to original sentence and increment both indices
        else:
            saltSentence += originalWords[originalIndex] + " "
            originalIndex += 1
            correctedIndex += 1

    saltSentence = saltSentence[:-1]

    return saltSentence 