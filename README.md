# YouTube Downloader (yt-dlp)

A small local web app: paste a YouTube link, see the available yt-dlp formats, pick one, and download it.

## Setup

Requires Python 3.9+ and [ffmpeg](https://ffmpeg.org/) (needed to merge separate video/audio streams and to extract MP3 audio).

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

Then:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5001.

## Usage

1. Paste a YouTube URL and click **Fetch info**.
2. Either pick one of the quick presets (**Best quality** merged MP4, or **Audio only** MP3), or choose a specific format from the table.
3. Click **Download selected** — the file downloads to your browser once yt-dlp finishes on the server.

Video-only formats are automatically merged with the best available audio track (via ffmpeg) into an MP4.
