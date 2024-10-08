import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#or run export PYTHONPATH=$(pwd) before running python tests/saltify_test.py

import unittest
import addConventions
import grammar 

class Test_isToBeVerb:
    def test_one(self):
        x = "is"
        assert addConventions.isToBeVerb(x) == True
    def test_two(self):
        x = "walk"
        assert addConventions.isToBeVerb(x) == False
    def test_three(self):
        x = "been"
        assert addConventions.isToBeVerb(x) == True
    def test_four(self):
        x = "'m"
        assert addConventions.isToBeVerb(x) == True

class Test_removeErrorCoding:
    def test_one(self):
        x = "(I I) I telled[EO:told] a lie."
        assert addConventions.removeErrorCoding(x) == "I told a lie."
    def test_two(self):
        x = "He walking[EW:walked] on the sidewalk."
        assert addConventions.removeErrorCoding(x) == "He walked on the sidewalk."
    def test_three(self):
        x = "This is a normal sentence with no error coding."
        assert addConventions.removeErrorCoding(x) == "This is a normal sentence with no error coding."
    def test_four(self):
        x = "He liked his[EP:her] shoes."
        assert addConventions.removeErrorCoding(x) == "He liked her shoes."
    def test_five(self):
        x = "He looked at[EW] sad."
        assert addConventions.removeErrorCoding(x) == "He looked sad."
    def test_six(self):
        x = "Give it *to me."
        assert addConventions.removeErrorCoding(x) == "Give it to me."
    def test_seven(self):
        x = "The car go/*3s fast."
        assert addConventions.removeErrorCoding(x) == "The car goes fast."

class Test_addInflectionalMorphemesToSentence:
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
    
class Test_correctSentence:
    def test_one(self):
        x = "He walk to school."
        assert addConventions.correctSentence(x) == "He walk/*3s to school."
    def test_two(self):
        x = "I I I telled a lie."
        assert addConventions.correctSentence(x) == "(I I) I telled[EW:told] a lie."

class Test_addInflectionalMorphemes:
    def test_one(self):
        x = "He liked his[EP:her] shoes."
        assert addConventions.addInflectionalMorphemes(x) == "He like/ed his[EP:her] shoe/s. \n"
    def test_two(self):
        x = "He looked at[EW] sad."
        assert addConventions.addInflectionalMorphemes(x) == "He look/ed at[EW] sad. \n"

class TestGrammarAndMorphemeFunctions(unittest.TestCase):

    def setUp(self):
        self.grammar_checker = grammar.GrammarChecker()

    def read_file(self, file_path):
        with open(file_path, 'r') as f:
            return f.readlines()

    def test_compare_input_with_output(self):
        input_file_path = os.path.join('tests', 'data', 'input1.txt')
        output_file_path = os.path.join('tests', 'data', 'output1.txt')

        input_lines = self.read_file(input_file_path)
        expected_output_lines = self.read_file(output_file_path)

        total_tests = 0  
        failed_tests = 0 

        errors = []

        # Only one loop to iterate through both input and expected output lines
        for input_line, expected_line in zip(input_lines, expected_output_lines):
            total_tests += 1  # Increment total test count

            # Simulate processing the input line
            self.grammar_checker.checkGrammar(input_line.strip(), checkAllSentences=False) 
            corrected, _ = self.grammar_checker.getNextCorrection()  # Grammar check
            processed_text = self.grammar_checker.getInflectionalMorphemes(corrected)  # Add morphemes

            # Print intermediate results for debugging
            print(f"Input Line: {input_line.strip()}")
            print(f"Corrected Text: {corrected.strip()}")
            print(f"Processed with Morphemes: {processed_text.strip()}")
            print(f"Expected Line: {expected_line.strip()}")
            print("-------------------------------------------------")

            # Compare the processed output with the expected output
            try:
                self.assertEqual(processed_text.strip(), expected_line.strip(), f"Mismatch for line: {input_file_path} -> {input_line}")
            except AssertionError as e:
                errors.append(str(e))
                failed_tests += 1  # Count failed tests

        # Calculate accuracy
        passed_tests = total_tests - failed_tests
        accuracy = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        # Print the final accuracy
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {failed_tests}")
        print(f"Accuracy: {accuracy:.2f}%")

        # Print any errors that occurred
        if errors:
            print("Some tests failed:")
            for error in errors:
                print(error)
            self.fail(f"{len(errors)} test(s) failed. Check the errors above.")

if __name__ == '__main__':
    unittest.main()
