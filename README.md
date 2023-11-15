# SpeechTranscription

The primary purpose of the application is to transcribe an audio sample into a written format that is accepted by `SALT software`. SALT software is an app that analyzes the speech of children and scores it according to their metrics.
The app can currently transcribe audio samples of a conversation between a child and an adult into text. It will need to distinguish who is speaking though as well what is being said. Second, the app will need to transcribe errors and features that are auto-corrected in currently available speech-to-text programs. Children naturally produce speech sound errors, language errors, and language features such as disfluencies. Language errors and features are diagnostically meaningful to speech-language pathologists (SLPs) and need to be maintained in the transcription. Unlike any programs currently available, the app will also offer suggestions for coding the sample.

The program can currently be run by:
`python gui.py`

Requirements include:

* Allow the user to input participant/client information like name, age, gender and examiner details.
* Record and Transcribe an audio language sample into text that SLPs can transfer to SALT’s program.
* The transcription should automatically correct errors like accents and mispronounced letters. (e.g, bath instead of “baf”).
* The transcription should include errors like missed grammatical morphemes, missing words, incorrect word usage and ungrammatical sentences.
* Identify and label the speakers (For e.g., if a child says “I am fine” it should be represented as “C I am fine”).
* The user can play the audio and manually change the transcription.
* The program should be able to generate a transcription with SALT’s convention or without any conventions.
* Finally, there should be an option to export the transcription into a word document.
