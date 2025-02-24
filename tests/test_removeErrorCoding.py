import pytest
import addConventions

def test_one():
    x = "(I I) I telled[EO:told] a lie."
    assert addConventions.removeErrorCoding(x) == "I told a lie."
def test_two():
    x = "He walking[EW:walked] on the sidewalk."
    assert addConventions.removeErrorCoding(x) == "He walked on the sidewalk."
def test_three():
    x = "This is a normal sentence with no error coding."
    assert addConventions.removeErrorCoding(x) == "This is a normal sentence with no error coding."
def test_four():
    x = "He liked his[EP:her] shoes."
    assert addConventions.removeErrorCoding(x) == "He liked her shoes."
def test_five():
    x = "He looked at[EW] sad."
    assert addConventions.removeErrorCoding(x) == "He looked sad."
def test_six():
    x = "Give it *to me."
    assert addConventions.removeErrorCoding(x) == "Give it to me."
def test_seven():
    x = "The car go/*3s fast."
    assert addConventions.removeErrorCoding(x) == "The car goes fast."
