# Script for user's audio input and transcription
import torch
import torchaudio
import soundfile as sf
import warnings
import os
# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_DEPRECATION_WARNINGS'] = '0'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# import tensorflow as tf
# tf.get_logger().setLevel('ERROR')

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit.watcher.local_sources_watcher")
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub.file_download")


def transcribe_audio_whisper(filename, whisper_pipeline):
    print(f"Attempting to transcribe file: {filename}")
    
    try:
        # Read the audio file using soundfile
        audio_data, sample_rate = sf.read(filename)
        print(f"Audio file read successfully. Shape: {audio_data.shape}, Sample rate: {sample_rate}")

        # Convert stereo to mono if necessary
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)

        # Convert the audio data to a tensor
        audio_tensor = torch.tensor(audio_data, dtype=torch.float32)
        
        print(f"Audio tensor shape: {audio_tensor.shape}")

        # Normalize the audio
        audio_tensor = audio_tensor / torch.max(torch.abs(audio_tensor))

        # Resample the audio to 16kHz if needed
        if sample_rate != 16000:
            print(f"Resampling audio from {sample_rate}Hz to 16000Hz")
            audio_tensor = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(audio_tensor)

        print("Transcribing audio...")

        # Transcribe the audio
        transcription = whisper_pipeline(audio_tensor.numpy())
        
        print(f"Raw transcription result: {transcription}")

        return transcription['text']
    
    except Exception as e:
        print(f"An error occurred during transcription: {str(e)}")
        return ""
