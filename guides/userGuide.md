# Getting started with SALTIFY

## **Downloading the Application**

[This link](https://github.com/oss-slu/SpeechTranscription/releases) will take you to a page where you can download the executable files. Please select the correct executable based on your operating system (Windows or macOS)

<br />
<br />

# Using the Application

## **Audio-Related Functionality**
### _The five buttons along the top row all contain audio-related functionality._
1. **Upload** - This button will allow you to choose a file from your file system to be uploaded as audio, which can later be transcribed to text using speech recognition via the **Transcibe** button.
2. **Record** - This button will begin recording audio from your computer's default microphone. During recording, this button is replaced with a **Stop** button, which will end your recording.
3. **Play** - This button will play back the currently selected audio file, whether manually uploaded or recorded within the program. During playback, this button is replaced with a **Stop** button that allows you to stop playback.
    * Note that we currently recommend for the user to play back audio using their computer's default media player program, as we are still developing functions for pausing, scrubbing, and skipping, and rewinding audio. We eventually hope to have the program in a state where this isn't necessary!
4. **Download** - This button allows the user to download the currently uploaded audio to their file system. If you recorded a session within the application, this is what would allow you to download that audio as a .wav file.
5. **Transcribe** - This button converted the currently selected audio into text using speech recognition, which will be placed in the large box in the center of the application.
    * Note that the quality of recording and the quality of speaking will affect the results of this functionality. In some cases, it may be advisable to still manually transcribe the audio.

## **Providing Session Information**
### _The second row of buttons and the table along the left side allow the user to enter information about the session, including the participant name, age, gender, date of birth, date of sample, examiner name, and sampling context._

1. **Dropdown Button** - This button allows you to choose which piece of information you want to enter. If you make a mistake, don't worry, because you can simply resubmit the correct data.
2. **Entry Box** - This box is between the dropdown button and the submit button is a text box. Here, you can enter data for the relevant field.
3. **Submit** - This button allows you to submit the data entered for the selected field. This data will then appear in the left hand table.
4. **Session Information Table** - This table holds all information about the session that has been submitted. 
5. **Toggle Table** - This button allows the user to hide the table.

## **Editing the Raw Transcript**
### _The large box in the center of the application is used to handle the raw transcript before any conventions are applied to the text. If manually transcribing audio, please enter text in this box such that each sentence starts on a new line._

1. **Transcription Box** - This box should hold the text of the raw trancript.
2. **Unlock/Lock** - To avoid editing text accidentally, the user may lock the box at any time so that changes cannot be made to it. 
3. **Clear** - This button clears the transcription box. Be careful, as this action cannot be undone.
4. **Toggle Table** - This button allows the user to hide the transcription box.

## **Adding and Editing Conventions**
### _After the raw transcript is edited to liking, the user may move on to adding and editing conventions within the convention box._

1. **Grammar Check** - This button triggers what should be the first step of adding conventions, which is to add error coding. The application will look at each sentence from the raw transcript and check if it is grammatically correct. If so, it will be automatically added to the convention box, which is created upon pressing this button. If not, it will be added to a smaller rectangular box below the convention box, with an attempt at adding the correct error coding. The user can then edit this sentence to their liking and then the grammar checking process will continue with further sentences.
    * Note that not every grammatically incorrect sentence will be caught, and some attempts at corrections may not be perfect.
2. **Convention Box** - The large box to the right of the transcription box should hold text that will be edited to add conventions.
3. **Grammar Correction Box** - Below the convention box, this box will hold sentences that are caught as incorrect during the grammar check process. The user can edit the sentence in the box to correct the error coding.
    * Note that inflectional morphemes should not be added during this step.
4. **Submit** - This button appends the sentence within the grammar correction box to the convention box. Click this when you are finished editing a sentence within the grammar correction box.
5. **Add Morphemes** - After finishing the grammar check procress (all sentences from the raw transcript should be in the convention box), the user may select this button to add inflectional morphemes to the text.
    * Note that not all inflectional morphemes will be added perfectly. We hope to resolve bugs of this type as quickly as possible.
6. **Lock/Unlock** and **Clear** - These buttons work similarly for the convention box as they did for the transcription box.

<br />
<br />

# Relaying Bugs to the Development Team

You may find that some features do not work as intended. Please either email the development team explaining your issue or go to [this link](https://github.com/oss-slu/SpeechTranscription/issues) where you can create a new "issue" and describe your problem. We are happy to help diagnose and resolve problems!
