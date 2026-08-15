# SpotSync
SpotSync is a Python script that parses Spotify playlists, identifies the full album or release associated with each track, and downloads the entire album to help expand your local music library. It features automatic rate-limit management and exponential retry backoff logic for smooth, reliable downloads.

---

## Features

* **Complete Album Fetching:** Identifies the full album or release linked to each track in a playlist and downloads the complete album to expand your local library.
* **Album Deduplication:** Automatically groups tracks by release URL so duplicate album downloads are skipped.
* **Rate-Limit Protection:** Batches downloads with delay intervals to stay under provider rate limits.
* **Exponential Backoff:** Automatically re-queues failed downloads with adaptive cooldown timers.
* **Error Logging:** Logs any permanently failed track links to a text file for easy review.
* **Structured Output:** Automatically organizes downloaded tracks into a structured folder hierarchy (`DownloadedMusics/Artist/Album/Track - Artist.m4a`).

---

## Prerequisites

* **Python 3.14+**
* **Spotify Developer Credentials:** A `Client ID` and `Client Secret` obtained from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/nyareinna/SpotSync.git
   cd SpotSync
   ```

2. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
3. **Install Core Dependencies (FFmpeg & Deno):**
   Run the following commands dependin on you OS/Terminal to download and configure FFmpeg and Deno via spotDL:

   * **Linux / macOS / Windows (Command Prompt):**
   ```bash
     spotdl --download-ffmpeg && spotdl --download-deno
   ```

   * **Windows (PowerShell):**
    ```bash
      spotdl --download-ffmpeg; spotdl --download-deno
    ```
---

## Usage

1. **Run the Script:**
   ```bash
   python run_spotsync.py
   ```

2. **First-Time Setup:**
   * Upon first launch, you will be prompted to enter your Spotify **Client ID** and **Client Secret**.
   * Your credentials will be saved locally in `spotify_credentials.json` for subsequent runs.

3. **Download Tracks:**
   * Enter a Spotify playlist URL when prompted.
   * Program is going to begin fetching releases and downloading tracks. This might take quite long for large playlists.

---

### Downloader Configuration

The application uses the following default configuration in `run_downloader.py` (around line 152) to control how `spotdl` fetches, encodes, and saves music files:

```python
downloader_settings = {
    "output": output_template,
    "format": "m4a",
    "bitrate": "128k",
    "save_errors": SAVE_ERRORS_FILE,
    "threads": 3,
    "audio_providers": ["youtube-music", "soundcloud", "bandcamp", "youtube"],
    "yt_dlp_args": "--extractor-args youtube:player_client=android,web_creator"
}

```

### How to Customize Configuration

To alter the default download config, edit the values inside the dictionary in `run_downloader.py`:

* **Change Audio Format:** 
  Replace `"m4a"` with `"mp3"` or `"opus"`.
```
"format": "mp3",
```
* **Adjust Bitrate:** 
  Lower the bitrate for smaller file sizes (e.g., `"128k"`, `"192k"`, `"256k"`, or `"disable"` for non-re-encoded quality).
  Anything over 128Kbps works only with YT Music Premium subscriptions and only up to 256Kbps. Learn how to import your cookies for YT music Premium (here)[https://github.com/spotDL/spotify-downloader/blob/master/docs/usage.md#audio-formats-and-quality]
```
"bitrate": "256k",
```

* **Change Parallel Downloads:** 
  Adjust the thread count. Lower numbers reduce the risk of rate-limiting, while higher numbers speed up downloads on fast connections.
```
"threads": 1,
```

* **Reorder Audio Providers:** 
  Rearrange or trim the list to modify provider search hierarchy.
```
"audio_providers": ["youtube-music", "youtube"],
```

---
  
## Directory Layout
```bash
SpotSync/
├── DownloadedMusics/
│   ├── Artist Name/
│   │   └── Album Name/
│   │       └── Song Title - Artist Name.m4a
│   └── FAILED_TO_DOWNLOAD.txt
├── run_spotsync.py
├── requirements.txt
└── spotify_credentials.json
```
---
