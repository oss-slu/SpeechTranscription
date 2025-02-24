import pytest
import addConventions

def test_one():
    x = "He liked his[EP:her] shoes."
    assert addConventions.addInflectionalMorphemes(x) == "He like/ed his[EP:her] shoe/s. \n"

def test_two():
    x = "He looked at[EW] sad."
    assert addConventions.addInflectionalMorphemes(x) == "He look/ed at[EW] sad. \n"
