# test_transcription.py
from components.transcription_utils import addInflectionalMorphemes, correctSentence

# Sample transcription with errors
sample_text = """
I has an appl. She go to school every day. He is playing football. They are happi today.
I like like the movie. This is a test* sentence with [EW:wrong] coding.
"""

print("=== Original Text ===")
print(sample_text)

# Step 1: Correct sentences (Python-only)
corrected_salt = correctSentence(sample_text)
print("\n=== Corrected Sentence (SALT-style) ===")
print(corrected_salt)

# Step 2: Add inflectional morphemes
full_pipeline_output = addInflectionalMorphemes(sample_text)
print("\n=== Full Pipeline Output (Inflectional Morphemes Applied) ===")
print(full_pipeline_output)