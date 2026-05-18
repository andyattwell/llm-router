import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

ttsmodel = "tts_models/multilingual/multi-dataset/xtts_v2"
# serialize List available 🐸TTS models
ttlman = TTS().list_models()
for model in ttlman.list_tts_models():
    if model == ttsmodel:
      print(f"Model Found: {model}")

langs = ttlman.list_langs()
print(f"Available languages: {langs}")
# Init TTS
# tts = TTS(ttsmodel).to(device)

# # Run TTS
# # ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# # Text to speech list of amplitude values as output
# wav = tts.tts(text="Hello world!", speaker_wav="my/cloning/audio.wav", language="en")
# # Text to speech to a file
# tts.tts_to_file(text="Hello world!", speaker_wav="my/cloning/audio.wav", language="en", file_path="output.wav")