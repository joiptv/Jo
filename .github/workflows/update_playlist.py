import os
import re
import requests

PLAYLIST_FILE = "Zoh.m3u"

# GitHub Secrets-ൽ നിന്ന് എൻഡ്‌പോയിന്റുകൾ നേരിട്ട് എടുക്കുന്നു
API_ENDPOINTS = [
    os.environ.get(f"ENDPOINT_{i}") for i in range(1, 6) if os.environ.get(f"ENDPOINT_{i}")
]

def fetch_updated_channel(channel_id):
    for endpoint in API_ENDPOINTS:
        try:
            url = f"{endpoint}?id={channel_id}" 
            response = requests.get(url, timeout=15)
            # വർക്കിംഗ് ആണെങ്കിൽ മാത്രം മാറ്റം വരുത്തുക
            if response.status_code == 200 and "#EXTINF" in response.text:
                return response.text.strip()
        except requests.exceptions.RequestException:
            continue
    return None

def update_playlist():
    if not os.path.exists(PLAYLIST_FILE):
        return

    with open(PLAYLIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated_playlist = []
    current_block = []
    is_jio_channel = False
    channel_id = None

    for line in lines:
        stripped_line = line.strip()
        
        if stripped_line.startswith("#EXTM3U"):
            updated_playlist.append(stripped_line)
            continue

        if stripped_line.startswith("#EXTINF:"):
            # പഴയ ചാനൽ ബ്ലോക്ക് അപ്ഡേറ്റ് ചെയ്യാനുണ്ടോ എന്ന് നോക്കുന്നു
            if current_block:
                if is_jio_channel and channel_id:
                    new_data = fetch_updated_channel(channel_id)
                    if new_data:
                        updated_playlist.append(new_data) # പുതിയ ലിങ്ക് കിട്ടിയാൽ അത് വെക്കുക
                    else:
                        updated_playlist.append("\n".join(current_block)) # അല്ലെങ്കിൽ പഴയത് തന്നെ വെക്കുക
                else:
                    updated_playlist.append("\n".join(current_block))
                
                current_block = []
                is_jio_channel = False
                channel_id = None

            current_block.append(stripped_line)
            
            # ചാനൽ ഐഡി കണ്ടെത്തുന്നു (tvg-id)
            match = re.search(r'tvg-id="([^"]+)"', stripped_line)
            if match:
                channel_id = match.group(1)
        else:
            if stripped_line:
                current_block.append(stripped_line)
                # Jio ലിങ്ക് ആണോ എന്ന് ഉറപ്പുവരുത്തുന്നു
                if "jio" in stripped_line.lower() or "hdnea" in stripped_line.lower() or "bpk-tv" in stripped_line.lower():
                    is_jio_channel = True

    # അവസാനത്തെ ചാനൽ ബ്ലോക്ക് സേവ് ചെയ്യാൻ
    if current_block:
        if is_jio_channel and channel_id:
            new_data = fetch_updated_channel(channel_id)
            if new_data:
                updated_playlist.append(new_data)
            else:
                updated_playlist.append("\n".join(current_block))
        else:
            updated_playlist.append("\n".join(current_block))

    # പുതിയ ഡാറ്റ ഫയലിലേക്ക് സേവ് ചെയ്യുന്നു
    with open(PLAYLIST_FILE, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(updated_playlist) + "\n")

if __name__ == "__main__":
    update_playlist()

