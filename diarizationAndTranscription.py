import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from pyannote.audio import Pipeline
    import whisper
from pydub import AudioSegment
import os
import re
from dotenv import load_dotenv

def transcribeAudio(audioFile):
    print("Starting transcription")
    model = whisper.load_model("small.en")  # using small.en for better accuracy
    transcribedAudio = model.transcribe(audioFile, fp16=False, language='English', condition_on_previous_text=False)
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

def transcribe(audioFile):
    transcription = transcribeAudio(audioFile)
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
        pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', use_auth_token=token)
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


    
