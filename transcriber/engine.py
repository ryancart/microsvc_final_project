from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import torch
import librosa

# Load model directly
processor = AutoProcessor.from_pretrained("openai/whisper-small")
model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-small")

def transcribe(audio_path: str) -> str:
    # Load audio file
    audio, sampling_rate = librosa.load(audio_path, sr=16000)
    
    # Process audio
    inputs = processor(audio, sampling_rate=sampling_rate, return_tensors="pt")
    
    # Generate transcription
    with torch.no_grad():
        generated_ids = model.generate(
            inputs["input_features"],
            max_length=448,
            num_beams=5,
            length_penalty=1.0
        )
    
    # Decode the transcription
    transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return transcription


