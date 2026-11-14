# LectureScribe – Multilingual Lecture Transcription & Subtitle Generator

**Student:** V. Ruthik  
**Register Number:** RA2311003050010

LectureScribe is a Flask web application that converts recorded speech into editable text using the OpenAI Whisper speech-recognition model. It supports audio upload, browser microphone recording, detected-language display, timestamped segments, and TXT/SRT/VTT export.

## Features
- Upload WAV, MP3, M4A, OGG, WEBM or MP4 audio (maximum 100 MB).
- Record speech using the browser microphone.
- Automatic language detection and speech-to-text transcription with Whisper.
- Display timestamped transcript segments.
- Edit the transcript and export TXT, SRT or VTT subtitle files.

## Requirements
- Python 3.9 or newer (a Python version supported by the installed PyTorch/Whisper packages).
- FFmpeg installed and available on your system PATH.
- Microphone permission for browser recording.

## Installation

### 1. Install FFmpeg
- **Windows:** Install FFmpeg and add its `bin` directory to PATH.
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **macOS:** `brew install ffmpeg`

### 2. Create and activate a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install Python packages
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```
Open http://127.0.0.1:5000 in your browser.

The first transcription may take time because Whisper downloads the selected model. The default model is `base`. To select another model, set `WHISPER_MODEL` to `tiny`, `base`, `small`, `medium`, or `large` before starting the app. Larger models generally need more memory and processing time.

## GitHub upload
Create a new empty repository on GitHub, then run these commands from this project folder:
```bash
git init
git add .
git commit -m "Initial LectureScribe ASR project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```
Replace the remote URL with your own repository URL.

## Project structure
```text
LectureScribe/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   └── index.html
├── static/
│   ├── app.js
│   └── style.css
└── uploads/
    └── .gitkeep
```

## Notes and limitations
- Whisper transcription runs locally on the machine hosting this application; CPU transcription may be slow.
- Browser microphone recording generally requires localhost or HTTPS.
- Audio is deleted from the upload directory after transcription. Exported subtitle files are stored temporarily in the uploads directory.
- ASR can make mistakes with noise, overlapping speakers, technical terms, accents and low-quality recordings. Review the transcript before relying on it.
- This is a student project starter. Add authentication, rate limiting, deployment configuration and stronger file validation before public production use.

## Author
V. Ruthik | RA2311003050010
