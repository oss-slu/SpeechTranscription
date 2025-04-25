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
    model = whisper.load_model("base.en")
    transcribedAudio = model.transcribe(audioFile, fp16=False, language='English')
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
    timestamps = [f"{int(seg['start']) // 60}:{int(seg['start']) % 60:02}" for seg in transcription["segments"]]
    transcriptionTextWithTimestamps = formatTranscriptionWithTimestamps(transcriptionText, timestamps)
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
            dzList.append([start - 2000, end - 2000, l.split(" ")[-1]])
            segments.append(len(sounds))
            sounds = sounds.append(audio[start:end], crossfade=0)
            sounds = sounds.append(spacer, crossfade=0)

        print("Finished diarization")
        
        # Transcription
        result = transcribeAudio(audioFile)
        captions = [[(int)(caption["start"] * 1000), (int)(caption["end"] * 1000), caption["text"]] for caption in result["segments"]]
        
        transcriptionText = ""
        timestamps = []
        for caption in captions:
            startTime = caption[0]
            endTime = caption[1]
            midpoint = (startTime + endTime) // 2  # Better for overlap detection

            # Default to UNKNOWN
            speaker = "UNKNOWN"
            best_match_duration = -1

            for segment in dzList:
                seg_start, seg_end, seg_speaker = segment
                if seg_start <= midpoint <= seg_end:
                    duration = seg_end - seg_start
                    if duration > best_match_duration:
                        best_match_duration = duration
                        speaker = seg_speaker

            # Format timestamp using startTime
            timestamp = f"{int(startTime // 60000)}:{int((startTime % 60000) // 1000):02}"
            timestamps.append(timestamp)
            transcriptionText += f"{speaker} - {caption[2].strip()}\n"
        transcript = formatTranscriptionWithTimestamps(transcriptionText, timestamps)
        return transcript
    else:
        print("Failed to diarize and transcribe: access token not found")
    
