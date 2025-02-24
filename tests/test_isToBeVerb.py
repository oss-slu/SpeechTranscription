import pytest
import addConventions
#or run export PYTHONPATH=$(pwd) before running python tests/saltify_test.py


def test_one():
    x = "is"
    assert addConventions.isToBeVerb(x) == True

def test_two():
    x = "walk"
    assert addConventions.isToBeVerb(x) == False

def test_three():
    x = "been"
    assert addConventions.isToBeVerb(x) == True

def test_four():
    x = "'m"
    assert addConventions.isToBeVerb(x) == True