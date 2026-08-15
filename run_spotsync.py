import json
import os
import shutil
import subprocess
import sys
import time
from spotdl import Spotdl

SPOTSYNC_BANNER = r"""
  /$$$$$$                         /$$      /$$$$$$                               
 /$$__  $$                       | $$     /$$__  $$                              
| $$  \__/  /$$$$$$   /$$$$$$  /$$$$$$  | $$  \__/ /$$   /$$ /$$$$$$$   /$$$$$$$ 
|  $$$$$$  /$$__  $$ /$$__  $$|_  $$_/  |  $$$$$$ | $$  | $$| $$__  $$ /$$_____/ 
 \____  $$| $$  \ $$| $$  \ $$  | $$     \____  $$| $$  | $$| $$  \ $$| $$       
 /$$  \ $$| $$  | $$| $$  | $$  | $$ /$$ /$$  \ $$| $$  | $$| $$  | $$| $$       
|  $$$$$$/| $$$$$$$/|  $$$$$$/  |  $$$$/|  $$$$$$/|  $$$$$$$| $$  | $$|  $$$$$$$ 
 \______/ | $$____/  \______/    \___/   \______/  \____  $$|__/  |__/ \_______/ 
          | $$                                     /$$  | $$                     
          | $$                                    |  $$$$$$/                     
          |__/                                     \______/                      
"""

CONFIG_FILE = "spotify_credentials.json"
BASE_DOWNLOAD_DIR = "DownloadedMusics"
SAVE_ERRORS_FILE = os.path.join(BASE_DOWNLOAD_DIR, "FAILED_TO_DOWNLOAD.txt")

# Rate limit & Backoff configuration
INITIAL_TIMEOUT = 15  # Cooldown in seconds on first failure 15 sec
MAX_TIMEOUT = 60      # Max cooldown cap for consecutive fails
MAX_RETRIES_PER_SONG = 3 # Try downloading a failed song 3 times

def load_or_request_credentials():
    """Loads API keys from a local JSON file or asks the user on first run."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            client_id = data.get("client_id")
            client_secret = data.get("client_secret")
            if client_id and client_secret:
                return client_id, client_secret

    print("=== First Time Setup ===")
    print("Create your app here: https://developer.spotify.com/dashboard/create")
    print("Redirect URL doesn't really matter, use this: https://example.com/callback")
    print("Only toggle the 'Web API' radio button")
    print("\n")
    print("Please enter your Spotify Developer Credentials.")
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()

    with open(CONFIG_FILE, "w") as f:
        json.dump({"client_id": client_id, "client_secret": client_secret}, f, indent=4)
    print(f"Credentials saved to {CONFIG_FILE}\n")

    return client_id, client_secret

def extract_unique_releases(spotdl_client, playlist_url):
    """Fetches playlist tracks and extracts unique release URLs (Albums & EPs & Singles)."""
    print("\nFetching playlist details via spotdl...")
    
    playlist_songs = spotdl_client.search([playlist_url])
    
    unique_release_urls = set()
    skipped_count = 0

    for song in playlist_songs:
        if hasattr(song, 'album_id') and song.album_id:
            release_url = f"https://open.spotify.com/album/{song.album_id}"
            unique_release_urls.add(release_url)
        else:
            skipped_count += 1

    print(f"Found {len(unique_release_urls)} unique release(s) to download.")
    if skipped_count > 0:
        print(f"Skipped {skipped_count} track(s) missing album metadata.")
        
    return list(unique_release_urls)

def download_songs_with_rate_limit(spotdl_client, songs):
    """Downloads songs in small batches with individual status indicators and retry logic."""
    queue = list(songs)
    retry_counts = {song.url: 0 for song in queue}
    current_timeout = INITIAL_TIMEOUT

    while queue:
        # Take up to 3 songs to process simultaneously
        batch = []
        while queue and len(batch) < 3:
            batch.append(queue.pop(0))

        # Print separate entries for each track starting download
        for song in batch:
            print(f"---> Processing: {song.display_name}")

        try:
            # Execute download safely on spotdl's main asyncio event loop
            results = spotdl_client.downloader.download_multiple_songs(batch)
            
            # Map successful song objects
            successful_songs = [res[0] for res in results if res and res[1] is not None]
        except Exception as e:
            print(f"[!] Exception during batch execution: {e}")
            successful_songs = []

        failed_in_batch = []

        # Print distinct [OK] or [:(] status indicator for each song in batch
        for song in batch:
            if song in successful_songs:
                print(f"[OK] Downloaded: {song.display_name}")
            else:
                print(f"[:(] Download Failed: {song.display_name}")
                failed_in_batch.append(song)

        if not failed_in_batch:
            # Batch succeeded completely
            current_timeout = INITIAL_TIMEOUT
            time.sleep(1.0)
        else:
            # Process retries and timeout for failed tracks
            for failed_song in failed_in_batch:
                retry_counts[failed_song.url] += 1
                attempts = retry_counts[failed_song.url]

                if attempts < MAX_RETRIES_PER_SONG:
                    print(f"[INFO] Re-queuing track at front (Attempt {attempts}/{MAX_RETRIES_PER_SONG})")
                    queue.insert(0, failed_song)
                else:
                    print(f"[X] Max retries reached for: {failed_song.display_name}. Skipping.\n")
                    with open(SAVE_ERRORS_FILE, "a", encoding="utf-8") as f:
                        f.write(f"{failed_song.url}\n")

            print(f"[!] Cooldown active. Pausing for {current_timeout} seconds...\n")
            time.sleep(current_timeout)
            current_timeout = min(current_timeout * 2, MAX_TIMEOUT)

def check_ffmpeg():
    """Checks if ffmpeg is installed, attempts installation via winget if not."""
    if shutil.which("ffmpeg"):
        return True

    print("[!] ffmpeg not found in PATH.")
    
    if not shutil.which("winget"):
        print("[X] winget is not installed. Cannot install ffmpeg automatically.")
        print("Please install ffmpeg manually: https://ffmpeg.org/download.html")
        sys.exit(1)

    print("[INFO] Attempting to install ffmpeg via winget...")
    try:
        subprocess.run(
            ["winget", "install", "--id=Gyan.FFmpeg", "-e"],
            check=True,
            capture_output=True,
            text=True
        )
        print("[OK] ffmpeg installed successfully.")
        print("[INFO] You may need to restart the terminal for PATH changes to take effect.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[X] Failed to install ffmpeg: {e.stderr}")
        print("Please install ffmpeg manually: https://ffmpeg.org/download.html")
        sys.exit(1)

def main():
    # Clears the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Print the  banner
    print(SPOTSYNC_BANNER)

    check_ffmpeg()

    client_id, client_secret = load_or_request_credentials()

    playlist_url = input("Enter Spotify Playlist Link: ").strip()
    if not playlist_url:
        print("No URL provided. Exiting.")
        sys.exit(0)

    output_template = os.path.join(BASE_DOWNLOAD_DIR, "{artist}", "{album}", "{title} - {artist}")
    os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)

    downloader_settings = {
        "output": output_template,
        "format": "m4a",
        "bitrate": "128k",
        "save_errors": SAVE_ERRORS_FILE,
        "threads": 3, # 3 downloads at a time
        "audio_providers": ["youtube-music", "soundcloud", "bandcamp", "youtube"],
        "yt_dlp_args": "--extractor-args youtube:player_client=android,web_creator",
        "ffmpeg_args": "-vn"
    }

    spotdl_client = Spotdl(
        client_id=client_id,
        client_secret=client_secret,
        downloader_settings=downloader_settings
    )

    releases_to_download = extract_unique_releases(spotdl_client, playlist_url)

    for index, release_url in enumerate(releases_to_download, start=1):
        print(f"\n================================================================================")
        print(f"[{index}/{len(releases_to_download)}] Fetching Release: {release_url}")
        print(f"================================================================================")
        try:
            release_songs = spotdl_client.search([release_url])
            download_songs_with_rate_limit(spotdl_client, release_songs)
        except Exception as e:
            print(f"Failed to fetch release: {release_url}: {e}")

    print(f"\nDownload process finished!")
    if os.path.exists(SAVE_ERRORS_FILE):
        print(f"Any permanently failed downloads logged to: {SAVE_ERRORS_FILE}")

if __name__ == "__main__":
    main()
