import io
import torchaudio
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import sys

torchaudio.set_audio_backend("soundfile")

processor = WhisperProcessor.from_pretrained("openai/whisper-tiny")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny").to("cuda")
model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(language="english", task="transcribe")


def transcribe(audio_bytes: bytes) -> str:
    waveform, sr = torchaudio.load(io.BytesIO(audio_bytes), format="wav")
    print(f"[transcribe] waveform shape: {waveform.shape}, sr: {sr}", file=sys.stderr)
    print(f"[transcribe] peak: {waveform.abs().max().item():.5f}", file=sys.stderr)
    target_sr = 16000
    if sr != target_sr:
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=target_sr)
        waveform = resampler(waveform)
        sr = target_sr
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    waveform_np = waveform.squeeze(0).numpy()
    print(f"[transcribe] mean: {waveform_np.mean():.5f}", file=sys.stderr)
    
    input_features = processor(
        waveform_np, 
        sampling_rate=sr, 
        return_tensors="pt", 
        return_attention_mask=True
        ).input_features.to('cuda')
    
    with torch.no_grad():
        predicted_ids = model.generate(input_features)

    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    print(f"[transcribe] result: {transcription}", file=sys.stderr)

    return transcription[0] if transcription else ""


