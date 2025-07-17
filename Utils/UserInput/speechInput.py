#!/usr/bin/env python3
import os
import wave
import tempfile

import pyaudio
from alive_progress import alive_bar
from openai import OpenAI

# 1) Make sure your OpenAI API key is set:
#    export OPENAI_API_KEY="sk-…"
client = OpenAI()

def speechInput():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    total_iters = int(RATE / CHUNK * RECORD_SECONDS)
    with alive_bar(total_iters, title="Recording for 10 seconds", spinner="horizontal") as bar:
        for _ in range(total_iters):
            data = stream.read(CHUNK)
            frames.append(data)
            bar()

    print("\nRecording finished.\n")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # 2) Write to a temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

    # 3) Call OpenAI’s transcription API
    with open(wav_path, "rb") as audio_file:
        resp = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",   # or "whisper-1"
            file=audio_file,
            response_format="text"       # you can also request "verbose_json", etc.
        )

    # 4) Output and cleanup
    print("Transcription:", resp)
    os.remove(wav_path)
    return resp

if __name__ == "__main__":
    speechInput()
