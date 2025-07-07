# Use fastapi to create a server that can receive a video file and return a new filename.
# The server should load whisper and able to call LLM, handing video file and return a new filename.

import fastapi
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from utils.whisper_tools import get_whisper_client, getTranscript  # TODD: 改為閉包
from utils.llm_tools import get_client, chat_completion
from utils.frame_tools import VisualClueExtractor
from utils.system_config import get_system_prompt

client = None  # Lazy loading the client
whisper_client = None  # Lazy loading the whisper client


def generate_title(filename, user_prompt="", max_frames: int = 2):
    """
    Generate a new title for a video file based on its content and user prompt.

    Parameters:
    filename (str): The name of the video file to be processed.
    user_prompt (str, optional): Additional context or prompt provided by the user.
    max_frames (int, optional): The maximum number of frames to extract for visual clues. Defaults to 5.

    Returns:
    tuple: A tuple containing the new filename, reason, and tags.
    """

    global client, whisper_client
    if client is None:
        print("[Server]|| Loading LLM Service client ||")
        client = get_client(mode="Local")
        print("[Server]|| Client LLM Service loaded ||")
    if whisper_client is None:
        print("[Server]|| Loading Whisper client ||")
        whisper_client = get_whisper_client(model="base")
        print("[Server]|| Whisper client loaded ||")

    # Get visual clues
    visual_clues = VisualClueExtractor(
        client=client).get_visual_clues(filename, max_frames=max_frames)
    # Get whisper transcript
    transcript = getTranscript(filename, client=whisper_client)
    # @gemini-2.5-pro: Handle empty or invalid transcripts.
    # A transcript with only the WEBVTT header (and whitespace) is considered empty.
    if isinstance(transcript, str) and transcript.strip() == "WEBVTT":
        transcript = "無語音內容"
    elif not transcript:  # handles None or empty string cases
        transcript = "無語音內容"

    # Get system prompt
    system_prompt = get_system_prompt(
        transcript, visual_clues, filename, user_prompt)

    # @gemini-2.5-pro: Print the system prompt for debugging purposes.
    print("|| System Prompt to LLM: ||")
    print(system_prompt)
    print("|| End of System Prompt ||")

    # @gemini-2.5-pro: Wrap the system_prompt string into the correct message format.
    messages = [{"role": "user", "content": system_prompt}]

    # Get LLM response
    response = chat_completion(
        client, messages)

    # @gemini-2.5-pro: Add logging and error handling for JSON decoding.
    print(f"|| Raw LLM Response: {response} ||")
    # Check if response is not None and parse it
    if response:
        import json
        try:
            # The response might be wrapped in ```json ... ```, so we extract it.
            if response.strip().startswith("```json"):
                response = response.strip()[7:-3]

            response_data = json.loads(response)
            new_filename = response_data.get('filename', '')
            reason = response_data.get('reason', '')
            tags = response_data.get('tags', '')
        except json.JSONDecodeError as e:
            print(f"!! JSONDecodeError: {e} !!")
            print(f"!! Failed to decode response: {response} !!")
            new_filename, reason, tags = 'error', f'JSON Decode Error: {e}', 'error'
    else:
        new_filename, reason, tags = '', '', ''
    return new_filename, reason, tags


app = FastAPI()


@app.post("/upload_video/")
async def upload_video(filename, url="", user_prompt="", max_frames: int = 2):
    """
    Endpoint to upload a video file and return a new filename.

    Parameters:
    filename (str): The name of the video file to be processed.
    url (str): The URL where the video file is located.
    user_prompt (str, optional): Additional context or prompt provided by the user.
    max_frames (int, optional): The maximum number of frames to extract for visual clues. Defaults to 5.

    Returns:
    JSONResponse: A JSON response containing the new filename, reason, and tags.
    """
    new_filename, reason, tags = generate_title(
        filename, user_prompt, max_frames=max_frames)
    return JSONResponse(content={"filename": new_filename, "reason": reason, "tags": tags})
