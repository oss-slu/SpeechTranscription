from nltk import sent_tokenize, word_tokenize, pos_tag, WordNetLemmatizer
import language_tool_python

wnl = WordNetLemmatizer()
tool = language_tool_python.LanguageTool("en-US")

# This function removes error coding from a sentence, leaving us with a grammatically correct sentence so NLTK can process it
def removeErrorCoding(x):
    words = x.split()
    sentence = ""
    for word in words:
        # Handles all cases where there is error coding with a bracket
        if ("[" in word):
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
        # Handles missing word case (*)
        elif ("*" in word):
            sentence += word.replace("*", "") + " "
        # Word has no error coding, can be appended as normal
        else:
            sentence += word + " "

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
        if ("[" in sentence or "*" in sentence):
            # First, removes error coding then applies morphemes to clean sentence
            errorCodingRemoved = removeErrorCoding(sentence)
            morphemesOnCorrectedSentence = addInflectionalMorphemesToSentence(errorCodingRemoved)
            # Splits both forms of sentence into words
            originalWords = sentence.split()
            correctedWords = morphemesOnCorrectedSentence.split()
            # Forms final sentence by combining morphemes from corrected sentence and 
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
                # Original word has no error coding; get word from saltified sentence 
                else:
                    finalSentence += correctedWords[correctedWordIndex] + " "
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
        elif (tuple[1] == "VBG"):
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
        elif (tuple[0] == "," or tuple[0] == "." or tuple[0] == "?" or tuple[0] == "!"):
            if (tuple[0] != ","):
                converted = converted[:-1] + tuple[0]
            else:
                converted = converted[:-1] + tuple[0] + " "
        # Token is a word with no changes needed
        else:
            converted += tuple[0] + " "

    # Manual replacements for irregular cases
    converted = converted.replace("ca/n't", "can/'t")
    converted = converted.replace("do/n't", "don't")

    return converted


# Takes a sentence x and returns the correct form in SALT standard with error coding
def correctSentence(x) :
    is_bad_rule = lambda rule: rule.category == 'PUNCTUATION' or rule.message == 'This word is normally spelled with a hyphen.'
    matches = tool.check(x)
    matches = [rule for rule in matches if not is_bad_rule(rule)]
    print(matches)
    corrected = language_tool_python.utils.correct(x, matches)
    print(corrected)
    originalWords = x.split()
    correctedWords = corrected.split()
    originalIndex = 0
    correctedIndex = 0
    saltSentence = ""
    while (originalIndex < len(originalWords) or correctedIndex < len(correctedWords)):
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
        # WARNING - THESE LINES ARE NOT YET RELEVANT - Check if the original sentence repeated the word several times,
        # WARNING - THESE LINES ARE NOT YET RELEVANT - if so provide correct coding "(And and) and" and increment accordingly
        # Otherwise, simply append and increment both sentences by one
        elif (originalWords[originalIndex] == correctedWords[correctedIndex]):
            """ # Code that would process repeats, not ready to be implemented
            repeatCounter = 0;
            while (originalIndex + 1 < len(correctedWords) - 1 and originalWords[originalIndex + repeatCounter + 1] == correctedWords[correctedIndex]):
                repeatCounter += 1
            if (repeatCounter > 0):
                saltSentence += "(" + originalWords[originalIndex]
                for i in range(repeatCounter)
                    saltSentence += " " + originalWords[originalIndex]
                saltSentence += ")"
                originalIndex += repeatCounter + 1
                correctedIndex += 1
            else:
            """
            saltSentence += originalWords[originalIndex] + " "
            originalIndex += 1
            correctedIndex += 1
        # The current word in the original sentence matches the next word in the corrected one, append word in corrected with asterisk
        # (Checks to make sure index won't go out of bounds)
        elif (correctedIndex < len(correctedWords) - 1 and originalWords[originalIndex] == correctedWords[correctedIndex+1]):
            saltSentence += correctedWords[correctedIndex] + "* "
            correctedIndex += 1
        # The current word in the corrected sentence matches the next word in the original one, append word in original with [EW]
        # (Checks to make sure index won't go out of bounds)
        elif (originalIndex < len(originalWords) - 1 and originalWords[originalIndex+1] == correctedWords[correctedIndex]):
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
