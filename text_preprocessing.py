import os
import json
import re
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Claude API key
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY is not set in the environment variables.")

def retrieve_transcriptions(file_path):
    """
    Reads transcriptions from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing audio transcriptions.

    Returns:
        list: List of transcription dictionaries.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            transcriptions = json.load(f)
        print(f"Successfully loaded {len(transcriptions)} transcriptions.")
        return transcriptions
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

def process_transcription_with_claude(transcription, model_name="claude-3-5-sonnet-20241022"):
    """
    Sends a transcription to Claude API for processing and returns the response.

    Args:
        transcription (str): The transcription text to process.
        model_name (str): The Claude model to use.

    Returns:
        dict: Parsed JSON response from Claude containing the title and processed text.
    """
    # Initialize the Anthropic client
    client = Anthropic(api_key=CLAUDE_API_KEY)

    # Define the user prompt
    user_prompt = (
        f"This is a transcription without punctuation and diacritics: \"{transcription}\".\n"
        "Please:\n"
        "1. Add proper punctuation and diacritics.\n"
        "2. Summarize the transcription in Arabic to create a title.\n"
        "Respond **ONLY** with a JSON object in this format:\n"
        "{\n"
        "  \"title\": \"\",\n"
        "  \"text\": \"\"\n"
        "}"
    )

    # Send the request
    response = client.messages.create(
        model=model_name,
        max_tokens_to_sample=1024,
        temperature=0.5,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    # Extract and parse the response
    raw_content = response["completion"]
    try:
        structured_response = json.loads(raw_content)
        return structured_response
    except json.JSONDecodeError as e:
        print(f"Failed to decode the response as JSON: {e}")
        print("Raw content:", raw_content)
        return {"title": "", "text": ""}

def process_all_transcriptions(input_file, output_file):
    """
    Processes all transcriptions from an input JSON file and saves the results to an output JSON file.

    Args:
        input_file (str): Path to the input JSON file containing transcriptions.
        output_file (str): Path to the output JSON file for saving results.
    """
    transcriptions = retrieve_transcriptions(input_file)
    if not transcriptions:
        print("No transcriptions to process.")
        return

    processed_data = []

    for transcription_entry in transcriptions:
        audio_name = transcription_entry.get("audio_name", "Unknown")
        transcription_text = transcription_entry.get("transcription", "")

        if not transcription_text:
            print(f"Skipping empty transcription for audio: {audio_name}")
            continue

        print(f"Processing transcription for audio: {audio_name}")

        # Process with Claude
        result = process_transcription_with_claude(transcription_text)

        processed_entry = {
            "audio_name": audio_name,
            "original_transcription": transcription_text,
            "title": result.get("title", "No title generated"),
            "processed_text": result.get("text", "No processed text available")
        }

        processed_data.append(processed_entry)

    # Save processed data to output file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)

    print(f"Processed data saved to {output_file}")

if __name__ == "__main__":
    input_file = "audio_transcript.json"
    output_file = "processed_transcripts.json"
    process_all_transcriptions(input_file, output_file)
