import addConventions

def test_one(self):
    x = "He walk to school."
    assert addConventions.correctSentence(x) == "He walk/*3s to school."
def test_two(self):
    x = "I I I telled a lie."
    assert addConventions.correctSentence(x) == "(I I) I telled[EW:told] a lie."