# Diarization-related libraries
# from resemblyzer import VoiceEncoder
# from resemblyzer.audio import sampling_rate
# from spectralcluster import SpectralClusterer
# import librosa
# from pydub import AudioSegment
import whisper
import torch
import torchaudio
from pydub import AudioSegment
from pyannote.audio import Model
model = Model.from_pretrained("pyannote/segmentation", use_auth_token="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")
from pyannote.audio.pipelines import SpeakerDiarization
from pyannote.pipeline.parameter import Uniform
from pyannote.database.util import load_rttm


# Adapted from https://github.com/raotnameh/Trim_audio
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
    print("this is transcribed audio:", transcribedAudio["text"])
    return transcribedAudio["text"]


def millisec(timeStr):
    spl = timeStr.split(":")
    s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
    return s
    
def diarizeAndTranscribe(audioFile):
    ##no ts = transcribedAudio(audioFile)
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
    # new implementation, hopefully works or idk what to do
    from pyannote.audio import Pipeline
    pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization')

    DEMO_FILE = {'audio': audioFile}
    dz = pipeline(DEMO_FILE)

    with open("diarization.txt", "w") as text_file:
        text_file.write(str(dz))

    print(*list(dz.itertracks(yield_label = True))[:10], sep="\n")

    ###
    import re
    spacermilli = 2000#
    dz = open('diarization.txt').read().splitlines()
    dzList = []
    for l in dz:
        start, end =  tuple(re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=l))
        start = millisec(start) - spacermilli
        end = millisec(end)  - spacermilli
        lex = not re.findall('SPEAKER_01', string=l)
        dzList.append([start, end, lex])

    print(*dzList[:10], sep='\n')




    #pyannote version includes diarization and transcription... partially works as is, but doesnt mesh with Whisper library well.
    '''
    pipeline = SpeakerDiarization()
    from pyannote.audio import Pipeline
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token="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")
    diarization = pipeline({'audio': audioFile})

    # Load the Whisper model
    device = torch.device('cpu')  # or 'cuda' if you have a GPU
    model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                        model='silero_stt',
                                        language='en', # Choose your language
                                        device=device)
    (read_batch, split_into_batches, read_audio, prepare_model_input) = utils

    # Load the entire audio data
    audio_data = AudioSegment.from_wav(audioFile)

    for segment, _, label in diarization.itertracks(yield_label=True):
        start, end = segment.start * 1000, segment.end * 1000  # Convert to milliseconds
        snippet = audio_data[start:end]  # Extract the snippet of audio
        #self.filePath = 'segment.wav'
        # Convert the snippet to raw audio data and then to tensor for recognition
        #with snippet.export(format="wav") as exported_snippet:
        snippet.export('segment.wav', format="wav").close()

        waveform= read_audio('segment.wav')#exported_snippet.name)
        #inputs = prepare_model_input(waveform, device=device)
        inputs = prepare_model_input(waveform.unsqueeze(0), device=device)

            
        # Recognize the audio snippet
        output = model(inputs)
        text = decoder(output[0].cpu())
            
        print(f"Speaker {label}: {text}")
    '''

    """
    name = audioFile.split(".")[0]
    for i in range(len(labelling)):
        transcript += "Speaker " + labelling[i][0] + ": "
        trim(labelling[i][1], labelling[i][2], audioFile)
        transcript += transcribeAudio(name + "_segment.wav") + "\n"
    """
    print("HERE")
    transcript = transcribeAudio(audioFile) + "\n"
    print('Passed line')
    transcript = transcript.replace('...', '')
    transcript = transcript.replace('. ', '.\n')
    transcript = transcript.replace('! ', '!\n')
    transcript = transcript.replace('? ', '?\n')
    transcript = transcript.replace('`', "'")
    transcript = transcript.strip()
    return transcript
