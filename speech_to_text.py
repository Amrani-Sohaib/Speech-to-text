import whisper
import json
import os
import torch


def transcribe_audios_to_json(input_dir, output_file, model_name="medium", language="ar"):
    """
    Transcribe multiple audio files in a directory and save the results into a single JSON file.
    
    Args:
        input_dir (str): Path to the directory containing audio files.
        output_file (str): Path to the JSON file where results will be saved.
        model_name (str): Name of the Whisper model to use (default: "medium").
        language (str): Language code for transcription (default: "ar" for Arabic).
    
    Returns:
        None: Saves all transcriptions into a single JSON file.
    """
    # Check if GPU is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load the Whisper model
    print(f"Loading Whisper model: {model_name}")
    model = whisper.load_model(model_name, device=device)
    
    # List to hold all transcription results
    transcription_results = []

    # Process each audio file in the input directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith(('.wav', '.mp3', '.flac')):  # Check for valid audio extensions
            audio_path = os.path.join(input_dir, file_name)
            print(f"Processing: {audio_path}")

            # Transcribe the audio
            result = model.transcribe(audio_path, language=language)
            transcription_data = {
                "audio_name": file_name,
                "model_name": model_name,
                "transcription": result["text"]
            }

            # Append transcription data to the results list
            transcription_results.append(transcription_data)
    
    # Save all transcriptions to a single JSON file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(transcription_results, json_file, ensure_ascii=False, indent=4)
    
    print(f"All transcriptions saved to: {output_file}")

if __name__ == "__main__":
    # Example usage
    input_directory = "tiktok_audios"  # audio directory
    output_json_file = "audio_transcript.json"  # JSON file path

    print("Available Whisper models: tiny, base, small, medium, large")
    selected_model = input("Enter the Whisper model name you want to use (default: medium): ").strip() or "medium"

    transcribe_audios_to_json(input_directory, output_json_file, model_name=selected_model, language="ar")
