import addConventions
import pytest
#or run export PYTHONPATH=$(pwd) before running python tests/saltify_test.py



def test_one():
    x = "John's dogs are smart."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "John/z dog/s are smart."
def test_two():
    x = "I walked my dog."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "I walk/ed my dog."
def test_three():
    x = "He goes for a walk every evening."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "He go/3s for a walk every evening."
def test_four():
    x = "I'm not doing my homework, but I can't do it now anyway."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "I/'m not do/ing my homework, but I can/'t do it now anyway."
def test_five():
    x = "I'll finish my homework after we're done with this."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "I/'ll finish my homework after we/'re done with this."
def test_six():
    x = "I'd like to go to Disneyland; it's famous for a reason."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "I/'d like to go to Disneyland; it/'s famous for a reason."
def test_seven():
    x = "I've been working for a long time."
    assert addConventions.addInflectionalMorphemesToSentence(x) == "I/'ve been work/ing for a long time."