# components/transcription_utils.py
import re

def correctSentence(text: str) -> str:
    """Basic SALT-style sentence correction"""
    # Remove SALT codes e.g. [EW:wrong]
    text = re.sub(r'\[.*?\]', '', text)
    # Remove special characters like *
    text = re.sub(r'[*]', '', text)
    # Clean up extra whitespace
    text = re.sub(r' +', ' ', text).strip()
    return text


def addInflectionalMorphemes(text: str) -> str:
    """Python-only inflectional morpheme tagging using NLTK"""
    import nltk
    from nltk import pos_tag, word_tokenize

    cleaned = correctSentence(text)
    tokens = word_tokenize(cleaned)
    tagged = pos_tag(tokens)

    result = []
    for word, tag in tagged:
        if tag == 'NNS':
            result.append(f"{word}[plural-s]")
        elif tag == 'VBZ':
            result.append(f"{word}[3sg-s]")
        elif tag == 'VBD':
            result.append(f"{word}[past-ed]")
        elif tag == 'VBG':
            result.append(f"{word}[prog-ing]")
        else:
            result.append(word)

    return ' '.join(result)