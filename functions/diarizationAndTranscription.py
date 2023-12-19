# Diarization-related libraries
# from resemblyzer import VoiceEncoder
# from resemblyzer.audio import sampling_rate
# from spectralcluster import SpectralClusterer
# import librosa
from pydub import AudioSegment
from pyannote.audio import Pipeline
import whisper
import torch
import torchaudio
import os
import re
from dotenv import load_dotenv
import tempfile
import soundfile as sf
from simple_diarizer.diarizer import Diarizer
from simple_diarizer.utils import (check_wav_16khz_mono, convert_wavfile,
                                   waveplot, combined_waveplot, waveplot_perspeaker)


# Adapted from https://github.com/raotnameh/Trim_audio"
# start: start time (s) of segment to be trimmed
# end: end time (s) of segment to be trimmed
# filename: name of wav file
# 
# Trims a segment from a wav file, exports to current directory as 'filename'_segment.wav
"""
def trim(start, end, filename):

    t1 = start * 1000 # converts to milliseconds
    t2 = end * 1000
    trimmedAudio = AudioSegment.from_wav(filename)
    trimmedAudio = trimmedAudio[t1:t2]
    # Gets name of file without extension
    name = filename.split('.')[0]
    trimmedAudio.export(name + "_segment.wav", format="wav")
"""
    
# Formats audio to be accepted by clustering process
"""
def resample(audio):
    wav, sampleRate = librosa.load(str(audio), sr=None)
    resampledAudio = librosa.resample(wav, orig_sr=sampleRate, target_sr=sampling_rate)
    return resampledAudio
"""

# Function adapted from https://medium.com/saarthi-ai/who-spoke-when-build-your-own-speaker-diarization-module-from-scratch-e7d725ee279
# Returns an array of tuples of form [speakerNumber, startTime, endTime]
# Effectively identifies segments and the speakers of those segments
"""
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
"""

def transcribeAudio(audioFile):
    model = whisper.load_model("base.en")
    transcribedAudio = model.transcribe(audioFile, fp16=False, language='English')
    # print("this is transcribed audio:", transcribedAudio["text"])
    return transcribedAudio

def millisec(timeStr):
  spl = timeStr.split(":")
  s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
  return s

def diarizeAndTranscribe(audioFile):
    # Diarization Process
    
    load_dotenv()
    token = os.getenv("ACCESS_TOKEN")
    pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', use_auth_token=token)
    DEMO_FILE = {'uri': 'blabal', 'audio': audioFile}
    dz = pipeline(DEMO_FILE)  

    # with open("diarization.txt", "w") as text_file:
    #     text_file.write(str(dz))
        
    audio = AudioSegment.from_wav(audioFile)
    spacer = AudioSegment.silent(duration=2000)
    sounds = spacer
    segments = []
    dzList = []
    diarization = str(dz).splitlines()

    for l in diarization:
        start, end =  tuple(re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=l))
        start = int(millisec(start))
        end = int(millisec(end))
        dzList.append([start - 2000, end - 2000, l.split(" ")[-1]])
        segments.append(len(sounds))
        sounds = sounds.append(audio[start:end], crossfade=0)
        sounds = sounds.append(spacer, crossfade=0)

    print(dzList)
    print("Diarized")
    result = transcribeAudio(audioFile)
    captions = [[(int)(caption["start"] * 1000), (int)(caption["end"] * 1000), caption["text"]] for caption in result["segments"]]
    print(*captions, sep='\n')
    print("Transcribed")
    for i in range(len(segments)):
        x = 0
        for x in range(len(captions)):
            if ((segments[i] - 2000) >= captions[x][0]) and ((segments[i] - 2000) <= captions[x][1])  :
                break
        c = captions[x]  
            
        start = dzList[i][0] + (c[0] -segments[i])

        if start < 0: 
            start = 0

        start = start / 1000.0
        startStr = '{0:02d}:{1:02d}:{2:02.2f}'.format((int)(start // 3600), (int)(start % 3600 // 60), start % 60)
        print(startStr, dzList[i][2], c[2])
    for i in range(len(segments)):
        idx = 0
        for idx in range(len(captions)):
            if captions[idx][0] >= (segments[i] - 2000):
                break
        
        while (idx < (len(captions))) and ((i == len(segments) - 1) or (captions[idx][1] < segments[i+1])):
            c = captions[idx]  
            
            start = dzList[i][0] + (c[0] -segments[i])

            if start < 0: 
                start = 0
            idx += 1

            start = start / 1000.0
            startStr = '{0:02d}:{1:02d}:{2:02.2f}'.format((int)(start // 3600), 
                                                    (int)(start % 3600 // 60), 
                                                    start % 60)
            print(startStr, dzList[i][2], c[2])
            
    transcript = result["text"] + "\n"
    transcript = transcript.replace('...', '')
    transcript = transcript.replace('. ', '.\n')
    transcript = transcript.replace('! ', '!\n')
    transcript = transcript.replace('? ', '?\n')
    transcript = transcript.replace('`', "'")
    transcript = transcript.strip()
    return transcript, ""
