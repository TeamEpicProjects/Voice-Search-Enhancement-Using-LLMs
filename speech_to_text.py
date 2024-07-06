# Script for user's audio input and transcription
import torch
import torchaudio
import pyaudio
import wave
import numpy as np
from tqdm import tqdm
import streamlit as st
import warnings
import os
# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_DEPRECATION_WARNINGS'] = '0'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
tf.get_logger().setLevel('ERROR')

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit.watcher.local_sources_watcher")
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub.file_download")

# Function to record audio from the microphone and save it to a file.
def record_audio(filename, sample_rate=16000, channels=1, silence_threshold=500, silence_duration=4):
    
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=1024)

    print("Recording...")

    frames = []
    silence_frames = 0
    silence_limit = int(sample_rate / 1024 * silence_duration)

    while True:
        data = stream.read(1024)
        frames.append(data)

        audio_data = np.frombuffer(data, dtype=np.int16)
        if np.abs(audio_data).mean() < silence_threshold:
            silence_frames += 1
        else:
            silence_frames = 0

        if silence_frames > silence_limit:
            print("Silence detected, stopping recording.")
            st.session_state['recording_stopped'] = True
            st.markdown('<div class="message-bar">Finding matching results...</div>', unsafe_allow_html=True)
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

# Function to transcribe audio using the Whisper model
def transcribe_audio_whisper(filename, whisper_pipeline):
    
    # Read the audio file
    with wave.open(filename, 'rb') as wf:
        num_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        num_frames = wf.getnframes()
        audio_data = wf.readframes(num_frames)

    # Convert the audio data to a tensor
    audio_tensor = torch.tensor(np.frombuffer(audio_data, dtype=np.int16), dtype=torch.float32)
    audio_tensor = audio_tensor / (2**15)

    # Resample the audio to 16kHz if needed
    if sample_rate != 16000:
        audio_tensor = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(audio_tensor)

    print("Transcribing audio...")

    # Transcribe the audio with progress bar
    with tqdm(total=100, desc="Transcription Progress") as pbar:
        transcription = whisper_pipeline(audio_tensor.numpy())
        pbar.update(100)

    return transcription['text']

def get_transcript(whisper_pipeline):

    audio_filename = "recorded_audio.wav"

    # Record audio from the microphone
    record_audio(audio_filename)

    # Transcribe the recorded audio using Whisper
    transcription = transcribe_audio_whisper(audio_filename, whisper_pipeline)

    # Delete the audio file after transcription
    os.remove(audio_filename)
    print(f"Audio file {audio_filename} deleted")

    return transcription

