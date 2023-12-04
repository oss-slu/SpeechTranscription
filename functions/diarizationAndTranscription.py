# Diarization-related libraries
# from resemblyzer import VoiceEncoder
# from resemblyzer.audio import sampling_rate
# from spectralcluster import SpectralClusterer
# import librosa
from pydub import AudioSegment
import whisper
import torch
import torchaudio
import os
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
    print("this is transcribed audio:", transcribedAudio["text"])
    return transcribedAudio["text"]

 
def transcribe_audio(audio_file_path: str, output_file_path: str):
    """
    Transcribes an audio file and saves the transcript into a text file.
 
    Parameters:
    - audio_file_path: str
        Path to the audio file to be transcribed.
    - output_file_path: str
        Path to the output text file where the transcript will be saved.
 
    Returns:
    - None
 
    Raises:
    - FileNotFoundError:
        If the audio file does not exist at the specified path.
    """
def diarizeAndTranscribe(audioFile):
    # Diarization Process

    with tempfile.TemporaryDirectory() as outdir:
        #diarization = Diarizer(embed_model='xvec', cluster_method='sc')
        NUM_SPEAKERS = 2
        #segments = diarization.diarize(audioFile, num_speakers=NUM_SPEAKERS)

        signal, fs = sf.read(audioFile)


        diar = Diarizer(
            embed_model='ecapa', # supported types: ['xvec', 'ecapa']
            cluster_method='sc', # supported types: ['ahc', 'sc']
            window=1.5, # size of window to extract embeddings (in seconds)
            period=0.75 # hop of window (in seconds)
        )

        segments = diar.diarize(audioFile, 
                                num_speakers=NUM_SPEAKERS,
                                outfile="audioFile.rttm")


        # Load the original audio file
        audio = AudioSegment.from_wav(audioFile)

        if os.path.exists('speaker_segments/'):
            for filename in os.listdir('speaker_segments/'):
                file_path = os.path.join('speaker_segments/', filename)
                # Check if it's a file or a directory
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)  # Remove the file
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove the directory
            print("Folder contents deleted.")
        else:
            print("Folder does not exist.")
        # Process each segment
        for segment_info in segments:
            start = int(float(segment_info['start']) * 1000)  # Convert to milliseconds
            end = int(float(segment_info['end']) * 1000)      # Convert to milliseconds
            label = segment_info['label']

            # Extract the segment
            segment = audio[start:end]

            # Save the segment
            segment.export(f'speaker_segments/{label}_{start}_{end}.wav', format='wav')
       
        output_directory = 'speaker_segments'

        # List and sort all WAV files in the directory
        audio_files = [f for f in os.listdir(output_directory) if f.endswith('.wav')]

        model = whisper.load_model("base")  # You can choose 'tiny', 'base', 'small', 'medium', or 'large'

        diarizedTranscript ="Diarized Version \n"
        # Iterate over each file and transcribe
        for file in audio_files:
            # Construct full file path
            file_path = os.path.join(output_directory, file)
            
            # Transcribe the audio
            result = model.transcribe(file_path)

            # Print or save the transcription
            print(f"Transcription for {file}:\n{result['text']}")
            diarizedTranscript=diarizedTranscript+ file[0] + result['text']+"\n"
   
    print("HERE")
    transcript = transcribeAudio(audioFile) + "\n"
    print('Passed line')
    transcript = transcript.replace('...', '')
    transcript = transcript.replace('. ', '.\n')
    transcript = transcript.replace('! ', '!\n')
    transcript = transcript.replace('? ', '?\n')
    transcript = transcript.replace('`', "'")
    transcript = transcript.strip()
    return transcript, diarizedTranscript
