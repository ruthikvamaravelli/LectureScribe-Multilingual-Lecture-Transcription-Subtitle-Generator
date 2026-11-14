import os
import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
import whisper

APP_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = APP_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"wav", "mp3", "m4a", "ogg", "webm", "mp4", "mpeg"}
MODEL_NAME = os.getenv("WHISPER_MODEL", "base")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
model = None

def get_model():
    global model
    if model is None:
        model = whisper.load_model(MODEL_NAME)
    return model

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def timestamp(seconds):
    ms = int(round(seconds * 1000))
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    secs, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"

def make_subtitles(segments, fmt):
    lines = []
    for i, seg in enumerate(segments, 1):
        start, end = seg["start"], seg["end"]
        if fmt == "srt":
            start_s, end_s = timestamp(start), timestamp(end)
            arrow = " --> "
        else:
            start_s = timestamp(start).replace(",", ".")
            end_s = timestamp(end).replace(",", ".")
            arrow = " --> "
        lines.extend([str(i), start_s + arrow + end_s, seg["text"].strip(), ""])
    return "\n".join(lines)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify(error="Please choose or record an audio file."), 400
    audio = request.files["audio"]
    if not audio.filename:
        return jsonify(error="The selected file has no name."), 400
    if not allowed_file(audio.filename):
        return jsonify(error="Unsupported format. Use WAV, MP3, M4A, OGG, WEBM or MP4."), 400

    suffix = Path(audio.filename).suffix.lower()
    path = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
    audio.save(path)
    try:
        result = get_model().transcribe(str(path), task="transcribe", verbose=False)
        segments = [
            {"start": float(s["start"]), "end": float(s["end"]), "text": s["text"].strip()}
            for s in result.get("segments", [])
        ]
        return jsonify(
            text=result.get("text", "").strip(),
            language=result.get("language", "unknown"),
            segments=segments
        )
    except Exception as exc:
        app.logger.exception("Transcription failed")
        return jsonify(error=f"Transcription failed: {exc}"), 500
    finally:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass

@app.route("/export", methods=["POST"])
def export():
    data = request.get_json(silent=True) or {}
    fmt = data.get("format", "txt").lower()
    text = data.get("text", "")
    segments = data.get("segments", [])
    if fmt not in {"txt", "srt", "vtt"}:
        return jsonify(error="Unsupported export format."), 400
    if fmt == "txt":
        content, mimetype, filename = text, "text/plain; charset=utf-8", "lecture-transcript.txt"
    else:
        content = make_subtitles(segments, fmt)
        if fmt == "vtt":
            content = "WEBVTT\n\n" + content
            mimetype, filename = "text/vtt; charset=utf-8", "lecture-subtitles.vtt"
        else:
            mimetype, filename = "application/x-subrip; charset=utf-8", "lecture-subtitles.srt"
    out = UPLOAD_DIR / filename
    out.write_text(content, encoding="utf-8")
    return send_file(out, as_attachment=True, download_name=filename, mimetype=mimetype)

@app.errorhandler(413)
def too_large(_):
    return jsonify(error="File is too large. Maximum size is 100 MB."), 413

if __name__ == "__main__":
    app.run(debug=True)
