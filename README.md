# Video Smart Renamer

## Project Introduction

Video Smart Renamer is an intelligent video renaming tool that combines speech transcription (using Whisper) and visual analysis (via LLM for image description) to automatically generate meaningful file names, renaming reasons, and relevant tags based on video content. This tool supports operation through an API service and can handle large video files.

## Key Features

- **Automated Video Renaming**: Generates new file names based on video's audio content and visual clues.
- **Multi-modal Content Analysis**: Integrates Whisper for speech transcription and utilizes LLM to extract key visual information.
- **API Service**: Provides a FastAPI interface, allowing external applications to call its video processing functions.
- **Large File Handling**: For video files exceeding 200MB, they are directly renamed in the source directory to avoid unnecessary copying.
- **Customizable Prompts**: Supports users providing additional prompts (`user_prompt`) to guide the LLM in generating more desired file names.

## Environment Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Install Dependencies

All Python dependencies are listed in `requirements.txt`. You can install them using the following command:

```bash
pip install -r requirements.txt
```

### Docker (Optional)

This project also provides a Dockerfile. You can build the image and run the service using Docker:

```bash
docker build -t video-smart-renamer .
docker run -p 8000:8000 video-smart-renamer
```

## How to Run

### 1. Start the Backend Service

The backend service is built using the FastAPI framework, which loads the Whisper model and LLM client.

#### Windows

Use the `start_server.bat` script to start the server:

```bash
start_server.bat
```

#### Linux/macOS

Use the `start_server.sh` script to start the server:

```bash
sh start_server.sh
```

Or directly use uvicorn:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

### 2. Run the Video Renaming Script

After the backend service is started, you can run the `rename_videos.py` script to process video files.

```bash
python rename_videos.py --source_directory ./test/input --output_directory ./test/output --user_prompt "Generate a name about Cosplay based on the video content"
```

## Usage Instructions

### `rename_videos.py` Parameters

- `--source_directory` (str): Path to the source directory containing video files. Defaults to `./test/input`.
- `--output_directory` (str): Path to the output directory for renamed files. Defaults to `./test/output`.
- `--user_prompt` (str): Additional user prompt provided to the LLM to guide filename generation. Defaults to an empty string.

### API Endpoint (`server.py`)

- `POST /upload_video/`
  - **Parameters**:
    - `filename` (str): The full path of the video file.
    - `url` (str, optional): URL of the video file (currently unused, reserved).
    - `user_prompt` (str, optional): Additional user prompt.
    - `max_frames` (int, optional): Maximum number of frames to extract for visual clues, defaults to 2.
  - **Response**:
    - `filename` (str): The new file name.
    - `reason` (str): The reason for renaming.
    - `tags` (str): Relevant tags.

## Project Structure

```
video-smart-renamer/
├── Dockerfile                  # Docker build file
├── rename_videos.py            # Video renaming client script
├── requirements.txt            # Python dependencies list
├── server.py                   # FastAPI backend service
├── start_server.bat            # Windows server startup batch file
├── start_server.sh             # Linux/macOS server startup script
├── test/                       # Test data directory
│   ├── input/                  # Example input videos
│   └── output/                 # Example output videos
└── utils/                      # Utility library
    ├── frame_tools.py          # Video frame processing tools
    ├── llm_tools.py            # LLM-related tools
    ├── system_config.py        # System configuration and prompt generation
    └── whisper_tools.py        # Whisper speech transcription tools
```

## Important Notes

- Ensure the backend service (`server.py`) is running before executing `rename_videos.py`.
- Large files (over 200MB) are not copied to the output directory; instead, they are directly renamed in the source directory.
- The LLM's response format must conform to JSON, including `filename`, `reason`, and `tags` fields, otherwise errors may occur.
