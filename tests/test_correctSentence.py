import pytest
import addConventions
#or run export PYTHONPATH=$(pwd) before running python tests/saltify_test.py


def test_one():
    x = "He walk to school."
    assert addConventions.correctSentence(x) == "He walk/*3s to school."
def test_two():
    x = "I I I telled a lie."
    assert addConventions.correctSentence(x) == "(I I) I telled[EW:told] a lie."