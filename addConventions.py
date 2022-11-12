from nltk import word_tokenize, pos_tag, WordNetLemmatizer
import language_tool_python

wnl = WordNetLemmatizer()
tool = language_tool_python.LanguageTool("en-US")

def addInflectionalMorphemes (x):
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
                converted = converted[:-1] + tuple[0] + "\n"
            else:
                converted = converted[:-1] + tuple[0] + " "
        # Token is a word with no changes needed
        else:
            converted += tuple[0] + " "

    # Manual replacements for irregular cases
    converted = converted.replace("ca/n't", "can/'t")
    converted = converted.replace("do/n't", "don't")

    return converted + "\n"


# Takes a sentence x and returns the correct form in SALT standard with error coding
def correctSentence(x) :
    corrected = tool.correct(x)
    originalWords = x.split()
    correctedWords = corrected.split()
    print("Original: ", originalWords)
    print("Corrected: ", correctedWords)
    originalIndex = 0
    correctedIndex = 0
    saltSentence = ""
    while (originalIndex < len(originalWords) or correctedIndex < len(correctedWords)):
        # Words only remain in the corrected sentence, append all with asterisk (missing word)
        if (originalIndex >= len(originalWords)):
            print(1)
            while (correctedIndex < len(correctedWords)):
                saltSentence += correctedWords[correctedIndex] + "* "
                correctedIndex += 1
        # Words only remain in the original sentence, append all unchanged
        elif (correctedIndex >= len(correctedWords)):
            print(2)
            while (originalIndex < len(originalWords)):
                saltSentence += originalWords[originalIndex] + "* "
                originalIndex += 1
        # The current word in each sentence is the same, so append it
        elif (originalWords[originalIndex] == correctedWords[correctedIndex]):
            saltSentence += originalWords[originalIndex] + " "
            originalIndex += 1
            correctedIndex += 1
        # The current word in the original sentence matches the next word in the corrected one, append word in corrected with asterisk
        # (Checks to make sure index won't go out of bounds)
        elif (correctedIndex < len(correctedWords) - 1 and originalWords[originalIndex] == correctedWords[correctedIndex+1]):
            print(4)
            saltSentence += corrected[correctedIndex] + "* "
            correctedIndex += 1
        # The current word in the corrected sentence matches the next word in the original one, append word in original with [EW]
        # (Checks to make sure index won't go out of bounds)
        elif (originalIndex < len(originalWords) - 1 and originalWords[originalIndex+1] == correctedWords[correctedIndex]):
            print(5)
            saltSentence += originalWords[originalIndex] + "[EW] "
            originalIndex += 1
        # If either index is at the last element, default to word-level error
        elif (originalIndex == len(originalWords) - 1 or correctedIndex == len(correctedWords) - 1):
            print(6)
            saltSentence += originalWords[originalIndex] + "[EW:" + correctedWords[correctedIndex] + "] "
            originalIndex += 1
            correctedIndex += 1
        # Word-level error if both words up next are matching
        elif (originalWords[originalIndex+1] == correctedWords[correctedIndex+1]):
            print(7)
            saltSentence += originalWords[originalIndex] + "[EW:" + correctedWords[correctedIndex] + "] "
            originalIndex += 1
            correctedIndex += 1
        # Both words up next do not match, defer to original sentence and increment both indices
        else:
            print(8)
            saltSentence += originalWords[originalIndex]
            originalIndex += 1
            correctedIndex += 1

    return saltSentence