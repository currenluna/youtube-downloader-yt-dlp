# YouTube Downloader (yt-dlp)

A small local web app: paste a YouTube link, see the available formats, pick one, and download it. Built on [yt-dlp](https://github.com/yt-dlp/yt-dlp).

Each person runs this on their own machine — it's not a hosted service. Nothing to sign up for, nothing shared between users.

## Setup

Requires Python 3.9+ and [ffmpeg](https://ffmpeg.org/) (needed to merge separate video/audio streams and to extract WAV/MP3 audio).

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

Then, every time you want to run it:

```bash
./run.sh
```

That's the only command you need — it creates the virtual environment the first time, keeps dependencies in sync with `requirements.txt` on every run, and starts the server at http://localhost:5001. No manual venv activation, no remembering `pip install`.

On macOS you can also just double-click **`run.command`** in Finder instead of using the terminal.

(SSL certificate errors on macOS are handled automatically — the app points itself at `certifi`'s certificate bundle on startup.)

## Usage

1. Paste a YouTube URL and click **Fetch info**.
2. Pick a quick preset, or choose a specific format from the list:
   - **Best quality** — merged MP4, video + audio, prefers H.264/AAC so it plays natively everywhere (see note below).
   - **Audio only — WAV** — lossless copy of the best available audio track. Largest file, no re-encoding loss.
   - **Audio only — MP3** — best-quality VBR encode (~245kbps avg). Smaller file, one lossy pass.
3. Click **Download** (bottom bar) — the file downloads to your browser once yt-dlp finishes on the server.

## Notes for video editors

- **The Code column** is yt-dlp's raw format ID (e.g. `137`, `248`). Useful if you're cross-referencing with yt-dlp on the command line, or want to reproduce a specific download outside this tool.
- **Codec column, plain-English:**
  - `H.264` (video) + `AAC` (audio) — universally compatible. Imports cleanly into Premiere, Final Cut, DaVinci Resolve, and plays natively in QuickTime/Preview.
  - `VP9`, `AV1` (video) or `Opus` (audio) — shown in amber. These are often YouTube's *actual* highest-quality streams, but QuickTime/Preview can't decode them, and some NLEs need a transcode pass before they'll import smoothly. They'll still play fine in VLC. If you're editing, prefer the H.264/AAC row at the resolution you need over a higher-res VP9/AV1 row, unless your NLE explicitly supports it.
- **Video-only formats** (marked "video only" in the Quality column) get automatically merged with the best available audio track into an MP4 when you download them — you don't need to download audio separately.
- The **Best quality** preset already applies the H.264/AAC preference above automatically, so it's the safest default if you just want something you can drop straight into a timeline.
