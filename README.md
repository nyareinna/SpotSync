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
