import subprocess
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from pyannote.audio import Pipeline
    import whisper
import tqdm
from pydub import AudioSegment
import os
import re
import types
import importlib
from dotenv import load_dotenv

import sys

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")


_model = None


def loadModel():
    # Loading the model is slow, so keep it for later transcriptions in this process
    global _model
    if _model is None:
        _model = whisper.load_model("small.en")  # using small.en for better accuracy
    return _model


class _ProgressBar(tqdm.tqdm):
    '''Stands in for whisper's tqdm bar and forwards how far through the audio it is.'''
    callback = None

    def update(self, n=1):
        # Count here rather than using self.n, which a disabled bar doesn't track
        self.framesDone = getattr(self, "framesDone", 0) + (n or 0)
        result = super().update(n)
        if self.callback and self.total:
            self.callback(min(self.framesDone / self.total, 1.0))
        return result


def _whisperProgressHook():
    '''The whisper.transcribe module, if it still reports progress through tqdm.tqdm.

    This relies on whisper internals, so if a whisper update changes them we
    transcribe without detailed progress instead of failing.
    '''
    try:
        # (whisper.transcribe is shadowed by the function of the same name, so look the module up)
        whisperTranscribe = importlib.import_module("whisper.transcribe")
    except ImportError:
        return None
    if not callable(getattr(getattr(whisperTranscribe, "tqdm", None), "tqdm", None)):
        print("[WARNING] whisper no longer uses tqdm.tqdm; transcription progress will not be detailed")
        return None
    return whisperTranscribe


def transcribeAudio(audioFile, on_progress=None):
    '''on_progress(fraction) is called with 0.0 to 1.0 as whisper works through the audio.'''
    print("Starting transcription")
    model = loadModel()
    whisperTranscribe = _whisperProgressHook() if on_progress is not None else None
    if whisperTranscribe is None:
        transcribedAudio = model.transcribe(audioFile, fp16=False, language='English', condition_on_previous_text=False)
    else:
        # whisper only reports progress through its tqdm bar, so swap in one that calls back
        progressBar = type("ProgressBar", (_ProgressBar,), {"callback": staticmethod(on_progress)})
        originalTqdm = whisperTranscribe.tqdm
        whisperTranscribe.tqdm = types.SimpleNamespace(tqdm=progressBar)
        try:
            transcribedAudio = model.transcribe(audioFile, fp16=False, language='English',
                                                condition_on_previous_text=False, verbose=False)
        finally:
            whisperTranscribe.tqdm = originalTqdm
    print("Finished transcription")
    return transcribedAudio

def millisec(timeStr):
  spl = timeStr.split(":")
  s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
  return s

def formatTranscription(transcription: str):
    transcript = transcription + "\n"
    transcript = transcript.replace('...', '')
    transcript = transcript.replace('. ', '.\n')
    transcript = transcript.replace('! ', '!\n')
    transcript = transcript.replace('? ', '?\n')
    transcript = transcript.replace('`', "'")
    transcript = transcript.strip()
    return transcript

def formatTranscriptionWithTimestamps(transcription: str, timestamps: list):
    transcript = ""
    for line, timestamp in zip(transcription.split('\n'), timestamps):
        if line.strip():  # Ensure the line is not empty
            transcript += f"[{timestamp}] {line}\n"
    return transcript.strip()

def transcribe(audioFile, on_progress=None):
    '''on_progress(stage, fraction) reports the current step and overall progress (0.0 to 1.0).'''
    def report(stage, fraction):
        if on_progress:
            on_progress(stage, fraction)

    report("Loading model", 0.05)
    loadModel()
    report("Transcribing", 0.1)
    transcription = transcribeAudio(
        audioFile, on_progress=lambda fraction: report("Transcribing", 0.1 + 0.8 * fraction))
    report("Formatting", 0.95)
    transcriptionText = formatTranscription(transcription["text"])
    # Use absolute times with millisecond precision
    timestamps = []
    for seg in transcription["segments"]:
        start_ms = int(seg["start"] * 1000)
        minutes = start_ms // 60000
        seconds = (start_ms % 60000) // 1000
        timestamps.append(f"{minutes}:{seconds:02}")
    # Check if timestamps cover the entire file duration
    audio = AudioSegment.from_file(audioFile)
    audio_duration_ms = len(audio)
    if transcription["segments"]:
        last_segment_end = transcription["segments"][-1]["end"] * 1000
        if abs(last_segment_end - audio_duration_ms) > 1000:
            print(f"[WARNING] Last transcription segment ends at {last_segment_end/1000:.2f}s "
                  f"but audio file is {audio_duration_ms/1000:.2f}s.")
    transcriptionTextWithTimestamps = formatTranscriptionWithTimestamps(
        transcriptionText, timestamps
    )
    return transcriptionTextWithTimestamps

def diarizeAndTranscribe(audioFile):
    # Diarize and transcribe the audio
    load_dotenv()
    token = os.getenv("ACCESS_TOKEN")

    if token:
        # Diarization
        print("Starting diarization")
        pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', token=token)
        DEMO_FILE = {'uri': 'blabal', 'audio': audioFile}
        dz = pipeline(DEMO_FILE)
        audio = AudioSegment.from_wav(audioFile)
        spacer = AudioSegment.silent(duration=2000)
        sounds = spacer
        segments = []
        dzList = []
        diarization = str(dz).splitlines()
        for l in diarization:
            start, end = tuple(re.findall(r'[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=l))
            start = int(millisec(start))
            end = int(millisec(end))
            # Removed unconditional -2000 shift; keep only if absolutely needed
            dzList.append([start, end, l.split(" ")[-1]])
            segments.append(len(sounds))
            sounds = sounds.append(audio[start:end], crossfade=0)
            sounds = sounds.append(spacer, crossfade=0)
        print("Finished diarization")
        # Transcription
        result = transcribeAudio(audioFile)
        captions = [[int(caption["start"] * 1000), int(caption["end"] * 1000), caption["text"]] for caption in result["segments"]]
        transcriptionText = ""
        timestamps = []
        for caption in captions:
            startTime, endTime, text = caption
            timeRange = -1
            speaker = "UNKNOWN"
            for x in range(len(dzList)):
                duration = dzList[x][1] - dzList[x][0]
                start = dzList[x][0]
                end = dzList[x][1]
                if (((start >= startTime) and (start < endTime)) or
                    ((end >= startTime) and (end < endTime)) or
                    ((start <= startTime) and (startTime <= end))) and (timeRange < duration):
                    timeRange = duration
                    speaker = dzList[x][2]
            timestamp = f"{int(startTime // 60000)}:{int((startTime % 60000) // 1000):02}"
            timestamps.append(timestamp)
            transcriptionText += f"{speaker} - {text}\n"
        transcript = formatTranscriptionWithTimestamps(transcriptionText, timestamps)
        return transcript
    else:
        print("Failed to diarize and transcribe: access token not found")


    
