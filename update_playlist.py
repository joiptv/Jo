import os
import re
import requests

PLAYLIST_FILE = "Zoh.m3u"

API_ENDPOINTS = [
    os.environ.get(f"ENDPOINT_{i}") for i in range(1, 6) if os.environ.get(f"ENDPOINT_{i}")
]

def fetch_updated_channel(channel_id):
    for endpoint in API_ENDPOINTS:
        try:
            url = f"{endpoint}?id={channel_id}"
            response = requests.get(url, timeout=15)
            if response.status_code == 200 and "#EXTINF" in response.text:
                return response.text.strip()
        except requests.exceptions.RequestException:
            continue
    return None

def update_playlist():
    if not os.path.exists(PLAYLIST_FILE):
        print("Playlist file not found!")
        return

    with open(PLAYLIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated_playlist = []
    current_block = []
    is_jio_channel = False
    channel_id = None

    handled_channels = set()  # ചാനലുകൾ ട്രാക്ക് ചെയ്യാൻ

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("#EXTM3U"):
            updated_playlist.append(stripped)
            continue

        if stripped.startswith("#EXTINF:"):
            if current_block:
                if is_jio_channel and channel_id and channel_id not in handled_channels:
                    new_data = fetch_updated_channel(channel_id)
                    if new_data:
                        updated_playlist.append(new_data)
                        handled_channels.add(channel_id)  # ട്രാക്ക് ചെയ്തു
                    else:
                        updated_playlist.append("\n".join(current_block))
                else:
                    updated_playlist.append("\n".join(current_block))
                
                current_block = []
                is_jio_channel = False
                channel_id = None

            current_block.append(stripped)

            match = re.search(r'tvg-id="([^"]+)"', stripped)
            if match:
                channel_id = match.group(1)

        else:
            if stripped:
                current_block.append(stripped)
                if any(x in stripped.lower() for x in ["jio", "hdnea", "bpk-tv"]):
                    is_jio_channel = True

    if current_block:
        if is_jio_channel and channel_id and channel_id not in handled_channels:
            new_data = fetch_updated_channel(channel_id)
            if new_data:
                updated_playlist.append(new_data)
                handled_channels.add(channel_id)
            else:
                updated_playlist.append("\n".join(current_block))
        else:
            updated_playlist.append("\n".join(current_block))
    
    with open(PLAYLIST_FILE, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(updated_playlist) + "\n")

if __name__ == "__main__":
    update_playlist()
