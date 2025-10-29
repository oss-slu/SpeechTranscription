import pytest
import os
import re
import grammar
#or run export PYTHONPATH=$(pwd) before running python tests/saltify_test.py
import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,  
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler("app.log", mode="a"))

@pytest.fixture
def grammar_checker():
    return grammar.GrammarChecker()

def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.readlines()

def test_compare_input_with_output(grammar_checker):
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

        input_lines = read_file(input_file_path)
        expected_output_lines = read_file(output_file_path)

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
            grammar_checker.checkGrammar(input_line.strip(), checkAllSentences=False) 
            corrected, _ = grammar_checker.getNextCorrection()
            processed_text = grammar_checker.getInflectionalMorphemes(corrected) if corrected else ""

            # Print intermediate results for debugging
            print(f"Input Line: {input_line.strip()}")
            print(f"Corrected Text: {corrected.strip()}")
            print(f"Processed with Morphemes: {processed_text.strip()}")
            print(f"Expected Line: {expected_line.strip()}")
            print("-------------------------------------------------")

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
        pytest.fail(f"{failed_line_tests} line mismatches and {failed_word_tests} word mismatches found across files.")

if __name__ == '__main__':
    pytest.main()
