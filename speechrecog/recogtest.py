# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 13:54:39 2022

@author: omars
"""
import speech_recognition as sr
r = sr.Recognizer()

class recog:
    def __init__(self, audioUpload):
        harvard = sr.AudioFile(audioUpload)
        print('Transcribing: ', audioUpload)
        with harvard as source:
            audio = r.record(source)

        transcript = r.recognize_google(audio)
        print(transcript)
