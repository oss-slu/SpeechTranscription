import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import addConventions
import diarizationAndTranscription

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

class TestTranscriptionAndDiarization(unittest.TestCase):

    def compare_outputs_line_by_line(self, generated_output, expected_output):
        """
        Compare each line of the generated output to the expected output.
        Asserts that each line matches.
        """
        # Iterate through both generated and expected lines
        for gen_line, exp_line in zip(generated_output.splitlines(), expected_output.splitlines()):
            # Asserting that each corresponding line matches
            self.assertEqual(gen_line.strip(), exp_line.strip(),
                             f"Mismatch found:\nGenerated: {gen_line}\nExpected: {exp_line}")

    def test_diarization_and_transcription(self):
        """
        Test diarization and transcription by comparing the generated output
        with the expected output from a file.
        """
        # Define paths for the test audio and expected output
        audio_file = "test_audio.wav"
        expected_output_file = "expected_output.txt"

        # Generate transcription and diarization output
        generated_output = diarizationAndTranscription.diarizeAndTranscribe(audio_file)

        # Load the expected output from the file
        with open(expected_output_file, "r") as file:
            expected_output = file.read()

        # Compare generated output with expected output, line by line
        self.compare_outputs_line_by_line(generated_output, expected_output)

if __name__ == "__main__":
    unittest.main()