import os
import json
import logging
from anthropic import Anthropic
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Setup Logging
# -----------------------------------------------------------------------------
# Create a logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a formatter that will add timestamps, log levels, and messages
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Set up console (stream) handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Set up file handler (all output will also go to execution_log.log)
file_handler = logging.FileHandler('execution_log.log', mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# -----------------------------------------------------------------------------
# Load environment variables
# -----------------------------------------------------------------------------
load_dotenv()

# Retrieve Claude API key from environment
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    logger.error("CLAUDE_API_KEY is not set in the environment variables.")
    raise ValueError("CLAUDE_API_KEY is not set in the environment variables.")


def retrieve_transcriptions(file_path):
    """
    Reads transcriptions from a JSON file.

    Args:
        file_path (str):
            Path to the JSON file containing audio transcriptions.

    Returns:
        list:
            A list of transcription dictionaries in the format:
            [
                {
                    "audio_name": "example_audio",
                    "transcription": "your transcription text"
                },
                ...
            ]

    Raises:
        FileNotFoundError:
            If the specified JSON file cannot be found.
        json.JSONDecodeError:
            If the JSON file is invalid or not properly formatted.
    """
    logger.info(f"\n----------\nRetrieving transcriptions from: {file_path}\n----------")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            transcriptions = json.load(f)

        logger.info(f"Successfully loaded {len(transcriptions)} transcriptions.")
        return transcriptions

    except FileNotFoundError:
        logger.error(f"File not found at {file_path}")
        return []

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
        return []


def process_transcription_with_claude(transcription, model_name="claude-3-5-sonnet-20241022"):
    """
    Sends a transcription to Claude API for processing and returns the response.

    This function:
    1. Initializes the Anthropic client with the CLAUDE_API_KEY.
    2. Builds a user prompt to request punctuation, diacritics, and a summary title.
    3. Sends the request to Claude using the specified model.
    4. Attempts to parse the JSON response (should contain 'title' and 'text').

    Args:
        transcription (str):
            The transcription text to process (usually without punctuation and diacritics).
        model_name (str):
            The Claude model to use for processing. Default is "claude-3-5-sonnet-20241022".

    Returns:
        dict:
            A dictionary containing the parsed JSON response from Claude, typically:
            {
                "title": "...",
                "text": "..."
            }
            If parsing fails, an empty dict or default-structured dict is returned.
    """
    logger.info("\n----------\nSending transcription to Claude API\n----------")

    # Initialize the Anthropic client
    client = Anthropic(api_key=CLAUDE_API_KEY)

    # Define the user prompt
    user_prompt = (
        f"This is a transcription without punctuation and diacritics: \"{transcription}\".\n"
        "Please:\n"
        "1. it is mandatory to Add proper punctuation and diacritics.\n"
        "2. Summarize the transcription in Arabic to create a title.\n"
        "Please respond only with a well-escaped single-line JSON object (no unescaped newlines in any text fields).”\n"
        "Respond **ONLY** with a JSON object in this format:\n"
        "{\n"
        "  \"title\": \"\",\n"
        "  \"text\": \"\"\n"
        "}"
    )

    # Send the request to Claude
    try:
        response = client.messages.create(
            model=model_name,
            max_tokens=8192,
            temperature=0.0,
            system="""You are an arabic world-class author with a heavy background in manga and philosophy 
                  and you shine at making philosophical analysis of great works (manga, anime, cinema, books..).
                  your writing style is very deep yet simple, usinbg simple words to explain complex ideas.
                  sometimes you can be very poetic and use metaphors to explain your ideas.
                  Be formal and enthousiast about the topics you talk.""",
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
    except Exception as e:
        logger.error(f"Error sending request to Claude: {e}")
        return {"title": "", "text": ""}

    # The 'content' field in Claude's response is typically an array of messages,
    # so we get the text from the first item.
    if not response or not response.content:
        logger.warning("Response from Claude is empty or malformed.")
        return {"title": "", "text": ""}

    raw_content = response.content[0].text
    logger.info(f"Raw response content from Claude:\n{raw_content}")

    # Attempt to parse the JSON response
    try:
        structured_response = json.loads(raw_content)
        return structured_response
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode the response as JSON: {e}")
        logger.error(f"Raw content:\n{raw_content}")
        return {"title": "", "text": ""}


def process_all_transcriptions(input_file, output_file):
    """
    Processes all transcriptions from an input JSON file and saves the results to an output JSON file.

    Steps:
    1. Retrieves all transcriptions from the provided input JSON file.
    2. Loops through each transcription:
       a. Logs and verifies the audio_name and transcription text.
       b. Skips if there's no transcription text.
       c. Sends transcription text to Claude for processing (punctuation and diacritics).
       d. Extracts 'title' and processed 'text' from Claude's response.
    3. Saves the resulting data to the specified output JSON file.

    Args:
        input_file (str):
            Path to the input JSON file containing transcriptions.
        output_file (str):
            Path to the output JSON file where processed transcriptions will be saved.
    """
    logger.info("\n====================\nStarting transcription processing...\n====================")

    transcriptions = retrieve_transcriptions(input_file)
    if not transcriptions:
        logger.warning("No transcriptions found to process.")
        return

    processed_data = []

    # Process each transcription
    for transcription_entry in transcriptions:
        audio_name = transcription_entry.get("audio_name", "Unknown")
        transcription_text = transcription_entry.get("transcription", "")

        # Log the start of processing
        logger.info(f"\n------------------------------\nProcessing audio: {audio_name}\n------------------------------")

        if not transcription_text:
            logger.warning(f"Skipping empty transcription for audio: {audio_name}")
            continue

        # Send transcription to Claude
        result = process_transcription_with_claude(transcription_text)

        # Build a dictionary of the processed info
        processed_entry = {
            "audio_name": audio_name,
            "original_transcription": transcription_text,
            "title": result.get("title", "No title generated"),
            "processed_text": result.get("text", "No processed text available")
        }

        processed_data.append(processed_entry)
        

    # Save the processed data to output_file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)
        logger.info(f"\nProcessed data saved successfully to {output_file}\n")
    except Exception as e:
        logger.error(f"Error while saving processed data to {output_file}: {e}")


if __name__ == "__main__":
    # Provide default file paths for testing/demonstration
    input_file = "audio_transcript.json"
    output_file = "processed_transcripts.json"

    # Run the main function to process transcriptions
    process_all_transcriptions(input_file, output_file)
