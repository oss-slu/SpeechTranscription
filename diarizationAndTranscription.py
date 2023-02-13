# Code adapted from https://medium.com/saarthi-ai/who-spoke-when-build-your-own-speaker-diarization-module-from-scratch-e7d725ee279
from resemblyzer import preprocess_wav, VoiceEncoder
from resemblyzer.audio import sampling_rate
from spectralcluster import SpectralClusterer, RefinementOptions
from speechrecog.recogtest import recog
from pydub import AudioSegment
import numpy as np

# Adapted from https://github.com/raotnameh/Trim_audio
def trim(start, end, filename, fileFormat, i):
    t1 = start * 1000
    t2 = end * 1000
    print("t1: " + str(t1))
    print("t2: " + str(t2))
    trimmedAudio = AudioSegment.from_wav(filename + "." + fileFormat)
    trimmedAudio = trimmedAudio[t1:t2]
    print("Trimmed audio duration: " + str(trimmedAudio.duration_seconds))
    # Exports new file with same name as base file + _(index)
    trimmedAudio.export(filename + "_" + str(i) + ".wav", format=fileFormat)

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

def diarizeAndTranscribe(audioFile):

    wav = preprocess_wav(audioFile)
    encoder = VoiceEncoder("cpu")
    _, cont_embeds, wav_splits = encoder.embed_utterance(wav, return_partials=True, rate=16)
    
    clusterer = SpectralClusterer(min_clusters=1, max_clusters=2)
    labels = clusterer.predict(cont_embeds)

    labelling = create_labelling(labels, wav_splits)
    print("Labelling: " + str(labelling))
    print("Number of splits found: " + str(len(labelling)))
    transcript = ""
    filenameWithoutExtension = audioFile.split('.')[0]
    fileExtension = audioFile.split('.')[1]
    for i in range(len(labelling)):
        transcript += "Speaker " + labelling[i][0] + ": "
        trim(labelling[i][1], labelling[i][2], filenameWithoutExtension, fileExtension, i)
        print("Attempting to transcribe: " + filenameWithoutExtension + "_" + str(i) + "." + fileExtension)
        transcript += recog(filenameWithoutExtension + "_" + str(i) + "." + fileExtension).getTranscript() + "\n"
    return transcript
