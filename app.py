import os
import shutil
import uuid

from flask import Flask, after_this_request, jsonify, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def base_ydl_opts(**overrides):
    opts = {"quiet": True, "no_warnings": True, "noplaylist": True}
    opts.update(overrides)
    return opts


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/info", methods=["POST"])
def info():
    data = request.get_json(force=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"error": "Please provide a YouTube URL."}), 400

    try:
        with yt_dlp.YoutubeDL(base_ydl_opts()) as ydl:
            result = ydl.extract_info(url, download=False)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    formats = []
    for f in result.get("formats", []):
        if f.get("vcodec") == "none" and f.get("acodec") == "none":
            continue  # storyboards / unusable entries
        formats.append({
            "format_id": f.get("format_id"),
            "ext": f.get("ext"),
            "resolution": f.get("resolution") or ("audio only" if f.get("vcodec") == "none" else "unknown"),
            "fps": f.get("fps"),
            "vcodec": f.get("vcodec"),
            "acodec": f.get("acodec"),
            "note": f.get("format_note"),
            "filesize": f.get("filesize") or f.get("filesize_approx"),
            "tbr": f.get("tbr"),
        })

    formats.sort(key=lambda f: (f.get("tbr") or 0), reverse=True)

    return jsonify({
        "title": result.get("title"),
        "thumbnail": result.get("thumbnail"),
        "duration": result.get("duration"),
        "uploader": result.get("uploader"),
        "formats": formats,
    })


@app.route("/api/download", methods=["POST"])
def download():
    data = request.get_json(force=True) or {}
    url = (data.get("url") or "").strip()
    mode = data.get("mode", "format")  # "format" | "best" | "audio_wav" | "audio_mp3"
    format_id = data.get("format_id")
    needs_merge = bool(data.get("needs_merge"))

    if not url:
        return jsonify({"error": "Please provide a YouTube URL."}), 400

    job_dir = os.path.join(DOWNLOAD_DIR, uuid.uuid4().hex)
    os.makedirs(job_dir, exist_ok=True)
    outtmpl = os.path.join(job_dir, "%(title)s.%(ext)s")

    opts = base_ydl_opts(outtmpl=outtmpl)

    if mode in ("audio_wav", "audio_mp3"):
        opts["format"] = "bestaudio/best"
        if mode == "audio_wav":
            # Lossless container around the best available source stream -
            # no re-encoding loss on top of whatever YouTube already applied.
            opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}]
        else:
            # preferredquality "0" = best VBR quality (~V0, ~245kbps avg),
            # the practical ceiling for MP3.
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",
            }]
    elif mode == "best":
        opts["format"] = "bestvideo+bestaudio/best"
        opts["merge_output_format"] = "mp4"
    else:
        if not format_id:
            return jsonify({"error": "Missing format_id."}), 400
        opts["format"] = f"{format_id}+bestaudio/best" if needs_merge else format_id
        if needs_merge:
            opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except Exception as exc:
        shutil.rmtree(job_dir, ignore_errors=True)
        return jsonify({"error": str(exc)}), 400

    files = os.listdir(job_dir)
    if not files:
        shutil.rmtree(job_dir, ignore_errors=True)
        return jsonify({"error": "Download failed: no output file was produced."}), 500

    filepath = os.path.join(job_dir, files[0])

    @after_this_request
    def cleanup(response):
        shutil.rmtree(job_dir, ignore_errors=True)
        return response

    return send_file(filepath, as_attachment=True, download_name=files[0])


if __name__ == "__main__":
    app.run(debug=True, port=5001)
