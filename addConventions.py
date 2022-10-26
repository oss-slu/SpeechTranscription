from nltk import word_tokenize, pos_tag, WordNetLemmatizer
import language_tool_python

wnl = WordNetLemmatizer()
tool = language_tool_python.LanguageTool("en-US")

def addEndPunctuation (x) :
    return x

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


def addWordLevelErrors(x) :
    # Gets all detected errors in a single sentence
    matches = tool.check(x)
    suggestions = ""
    for match in matches:
        suggestions += match + "\n\n"
    return suggestions

def addOmissions(x):
    return x
