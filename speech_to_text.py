import whisper
import torch



# Ensure GPU is available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load the Whisper model
model = whisper.load_model("large", device=device)  # Use 'small', 'medium', or 'large'

# Transcribe the audio file
result = model.transcribe("Ahmed fakhouri _2.wav", language="ar")

# Print the transcribed text
print("Transcription:")
print(result['text'])