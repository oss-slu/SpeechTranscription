import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#or run export PYTHONPATH=$(pwd) before running python tests/saltify_test.py

import re
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

        # directory containing the test files
        data_dir = os.path.join('tests', 'data')
        files = os.listdir(data_dir)
        
        # filtering out input and output files
        input_files = sorted([f for f in files if re.match(r'input\d+\.txt', f)])
        output_files = sorted([f for f in files if re.match(r'output\d+\.txt', f)])

        # counters for line and word level comparison
        total_line_tests = 0  
        failed_line_tests = 0
        total_word_tests = 0
        failed_word_tests = 0

        file_summaries = []

        for input_file, output_file in zip(input_files, output_files):
            # checking matching input and output numbers
            input_num = re.search(r'input(\d+)\.txt', input_file).group(1)
            output_num = re.search(r'output(\d+)\.txt', output_file).group(1)
            if input_num != output_num:
                print(f"File mismatch: {input_file} does not match {output_file}")
                continue

            input_file_path = os.path.join(data_dir, input_file)
            output_file_path = os.path.join(data_dir, output_file)

            input_lines = self.read_file(input_file_path)
            expected_output_lines = self.read_file(output_file_path)

            # file-specific counters
            file_line_tests = 0
            file_failed_line_tests = 0
            file_word_tests = 0
            file_failed_word_tests = 0

            line_errors = []
            word_errors = []

            # line-by-line comparison
            for input_line, expected_line in zip(input_lines, expected_output_lines):
                file_line_tests += 1
                total_line_tests += 1

                # process the input line
                self.grammar_checker.checkGrammar(input_line.strip(), checkAllSentences=False) 
                corrected, _ = self.grammar_checker.getNextCorrection()
                processed_text = self.grammar_checker.getInflectionalMorphemes(corrected) if corrected else ""

                # check if the entire processed line matches the expected line
                if processed_text.strip() != expected_line.strip():
                    line_errors.append(f"Processed '{processed_text.strip()}' vs Expected '{expected_line.strip()}'")
                    file_failed_line_tests += 1
                    failed_line_tests += 1

                # word-by-word comparison
                processed_words = processed_text.strip().split()
                expected_words = expected_line.strip().split()
                for i, (processed_word, expected_word) in enumerate(zip(processed_words, expected_words)):
                    file_word_tests += 1
                    total_word_tests += 1
                    if processed_word != expected_word:
                        word_errors.append(f"Word mismatch at position {i+1}: Processed '{processed_word}' vs Expected '{expected_word}'")
                        file_failed_word_tests += 1
                        failed_word_tests += 1

                # handle any extra words in processed or expected lines
                if len(processed_words) > len(expected_words):
                    for extra_word in processed_words[len(expected_words):]:
                        word_errors.append(f"Extra word in processed output: '{extra_word}'")
                        file_failed_word_tests += 1
                        failed_word_tests += 1
                        file_word_tests += 1
                        total_word_tests += 1
                elif len(expected_words) > len(processed_words):
                    for missing_word in expected_words[len(processed_words):]:
                        word_errors.append(f"Missing word in processed output: Expected '{missing_word}'")
                        file_failed_word_tests += 1
                        failed_word_tests += 1
                        file_word_tests += 1
                        total_word_tests += 1

            # calculate file-specific accuracy
            file_line_accuracy = (file_line_tests - file_failed_line_tests) / file_line_tests * 100 if file_line_tests else 0
            file_word_accuracy = (file_word_tests - file_failed_word_tests) / file_word_tests * 100 if file_word_tests else 0

            # append summary for each file
            file_summaries.append({
                'file': input_file,
                'total_line_tests': file_line_tests,
                'failed_line_tests': file_failed_line_tests,
                'line_accuracy': file_line_accuracy,
                'total_word_tests': file_word_tests,
                'failed_word_tests': file_failed_word_tests,
                'word_accuracy': file_word_accuracy,
                'line_errors': line_errors,
                'word_errors': word_errors
            })

        # calculate overall accuracy
        line_accuracy = (total_line_tests - failed_line_tests) / total_line_tests * 100 if total_line_tests else 0
        word_accuracy = (total_word_tests - failed_word_tests) / total_word_tests * 100 if total_word_tests else 0
        total_accuracy = (line_accuracy + word_accuracy) / 2 if total_line_tests and total_word_tests else 0

        # display summary for each file
        print("\n===== Detailed Test Summary by File =====\n")
        for summary in file_summaries:
            print(f"File: {summary['file']}")
            print(f"  Total Line Tests: {summary['total_line_tests']}")
            print(f"  Failed Line Tests: {summary['failed_line_tests']}")
            print(f"  Line Accuracy: {summary['line_accuracy']:.2f}%\n")

            print(f"  Total Word Tests: {summary['total_word_tests']}")
            print(f"  Failed Word Tests: {summary['failed_word_tests']}")
            print(f"  Word Accuracy: {summary['word_accuracy']:.2f}%\n")

            # show a limited number of errors per file
            max_errors_to_show = 5
            if summary['line_errors'] or summary['word_errors']:
                print(f"  Showing up to {max_errors_to_show} errors:")
                for error in (summary['line_errors'] + summary['word_errors'])[:max_errors_to_show]:
                    print(f"    {error}")
                if len(summary['line_errors']) + len(summary['word_errors']) > max_errors_to_show:
                    print(f"    ...and more errors.\n")

        # display overall accuracy summary
        print("\n===== Overall Test Summary =====")
        print(f"Total Line Tests: {total_line_tests}")
        print(f"Total Failed Line Tests: {failed_line_tests}")
        print(f"Line-by-Line Accuracy: {line_accuracy:.2f}%\n")

        print(f"Total Word Tests: {total_word_tests}")
        print(f"Total Failed Word Tests: {failed_word_tests}")
        print(f"Word-by-Word Accuracy: {word_accuracy:.2f}%\n")

        print(f"Overall Accuracy (Average of Line and Word Accuracy): {total_accuracy:.2f}%")
        print("=========================\n")

        # fail the test if there are any mismatches
        if failed_line_tests > 0 or failed_word_tests > 0:
            self.fail(f"{failed_line_tests} line mismatches and {failed_word_tests} word mismatches found across files.")

if __name__ == '__main__':
    unittest.main()
