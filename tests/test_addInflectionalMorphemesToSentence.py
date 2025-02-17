import addConventions


def test_one(self):
    x = "John's dogs are smart."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "John/z dog/s are smart."
def test_two(self):
    x = "I walked my dog."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "I walk/ed my dog."
def test_three(self):
    x = "He goes for a walk every evening."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "He go/3s for a walk every evening."
def test_four(self):
    x = "I'm not doing my homework, but I can't do it now anyway."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "I/'m not do/ing my homework, but I can/'t do it now anyway."
def test_five(self):
    x = "I'll finish my homework after we're done with this."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "I/'ll finish my homework after we/'re done with this."
def test_six(self):
    x = "I'd like to go to Disneyland; it's famous for a reason."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "I/'d like to go to Disneyland; it/'s famous for a reason."
def test_seven(self):
    x = "I've been working for a long time."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "I/'ve been work/ing for a long time."