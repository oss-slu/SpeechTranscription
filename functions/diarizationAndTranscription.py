from resemblyzer import VoiceEncoder
from resemblyzer.audio import sampling_rate
from spectralcluster import SpectralClusterer
from pydub import AudioSegment
import speech_recognition
import librosa
import whisper

# Adapted from https://github.com/raotnameh/Trim_audio
# start: start time (s) of segment to be trimmed
# end: end time (s) of segment to be trimmed
# filename: name of wav file
# 
# Trims a segment from a wav file, exports to current directory as 'filename'_segment.wav
def trim(start, end, filename):

    t1 = start * 1000 # converts to milliseconds
    t2 = end * 1000
    print("t1: " + str(t1))
    print("t2: " + str(t2))
    trimmedAudio = AudioSegment.from_wav(filename)
    trimmedAudio = trimmedAudio[t1:t2]
    print("Trimmed audio duration: " + str(trimmedAudio.duration_seconds))
    # Gets name of file without extension
    name = filename.split('.')[0]
    trimmedAudio.export(name + "_segment.wav", format="wav")

# Formats audio to be accepted by clustering process
def resample(audio):
    wav, sampleRate = librosa.load(str(audio), sr=None)
    resampledAudio = librosa.resample(wav, orig_sr=sampleRate, target_sr=sampling_rate)
    return resampledAudio

# Function adapted from https://medium.com/saarthi-ai/who-spoke-when-build-your-own-speaker-diarization-module-from-scratch-e7d725ee279
# Returns an array of tuples of form [speakerNumber, startTime, endTime]
# Effectively identifies segments and the speakers of those segments
def create_labelling(labels, wav_splits):
    times = [((s.start + s.stop) / 2) / sampling_rate for s in wav_splits]
    labelling = []
    start_time = 0

    for i, time in enumerate(times):
        if i > 0 and labels[i] != labels[i-1]:
            temp = [str(labels[i-1]),start_time,time]
            labelling.append(tuple(temp))
            start_time = time
        if i==len(times)-1:
            temp = [str(labels[i]),start_time,time]
            labelling.append(tuple(temp))

    return labelling

def transcribeAudio(audioFile):
    model = whisper.load_model("base.en")
    transcribedAudio = model.transcribe(audioFile, fp16=False, language='English')
    # recognizer = speech_recognition.Recognizer()
    # formattedAudio = speech_recognition.AudioFile(audioFile)
    # with formattedAudio as source:
    #     recording = recognizer.record(source)
    # transcribedAudio = recognizer.recognize_google(recording, language = 'en-IN')
    print('Transcribing: ', audioFile)
    # return transcribedAudio
    return transcribedAudio["text"]

def diarizeAndTranscribe(audioFile):

    # Diarization Process
    """
    wav = resample(audioFile)
    encoder = VoiceEncoder("cpu")
    _, cont_embeds, wav_splits = encoder.embed_utterance(wav, return_partials=True, rate=16)
    clusterer = SpectralClusterer(min_clusters=1, max_clusters=2)
    labels = clusterer.predict(cont_embeds)
    labelling = create_labelling(labels, wav_splits)
    print("Labelling: " + str(labelling))
    print("Number of splits found: " + str(len(labelling)))
    """

    # Transcribing Segments
    transcript = ""

    """
    name = audioFile.split(".")[0]
    for i in range(len(labelling)):
        transcript += "Speaker " + labelling[i][0] + ": "
        trim(labelling[i][1], labelling[i][2], audioFile)
        print("Attempting to transcribe: " + audioFile)
        transcript += transcribeAudio(name + "_segment.wav") + "\n"
    """
    transcript = transcribeAudio(audioFile) + "\n"
    transcript = transcript.replace('...', '')
    transcript = transcript.replace('. ', '.\n')
    transcript = transcript.replace('! ', '!\n')
    transcript = transcript.replace('? ', '?\n')
    transcript = transcript.strip()
    print(transcript)
    return transcript
