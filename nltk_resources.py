"""NLTK data the app needs, shared by the build script and the packaged-app self-test."""

import nltk

PACKAGES = [
    "punkt",  # grammar.py checks tokenizers/punkt and falls back to naive splitting without it
    "punkt_tab",
    "averaged_perceptron_tagger_eng",
    "wordnet",
    "omw-1.4",
    "wordnet_ic",
]


def verify(data_dir=None):
    """Run the NLTK calls the app makes. Raises if any resource is missing.

    If data_dir is given, NLTK is restricted to it, so success proves the data
    there is complete rather than found somewhere else on the machine.
    """
    if data_dir is not None:
        nltk.data.path[:] = [data_dir]

    from nltk import pos_tag, sent_tokenize, word_tokenize
    from nltk.stem import WordNetLemmatizer

    nltk.data.find("tokenizers/punkt")
    assert sent_tokenize("The dog runs. The cat sleeps.") == ["The dog runs.", "The cat sleeps."]
    assert pos_tag(word_tokenize("The dog runs"))[1] == ("dog", "NN")
    assert WordNetLemmatizer().lemmatize("dogs") == "dog"
