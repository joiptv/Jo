import requests
import re

# ചാനലുകളുടെ ലിസ്റ്റ്
TARGET_CHANNELS = ["Asianet", "Asianet Plus", "Asianet Movies"]

# ഫയൽ വിവരങ്ങൾ (Z Capital ആക്കി മാറ്റിയിട്ടുണ്ട്)
SOURCE_URL = "https://voot.vodep39240327.workers.dev?voot.m3u"
MY_PLAYLIST = "Zoh.m3u" 

def get_source_data():
    try:
        response = requests.get(SOURCE_URL, timeout=20)
        return response.text if response.status_code == 200 else None
    except:
        return None

def update_playlist():
    source_content = get_source_data()
    if not source_content:
        return

    source_lines = source_content.splitlines()
    source_map = {}
    
    for i, line in enumerate(source_lines):
        if line.startswith("#EXTINF"):
            for channel in TARGET_CHANNELS:
                if f'tvg-name="{channel}"' in line or f',{channel}' in line:
                    block = []
                    for j in range(i + 1, len(source_lines)):
                        if source_lines[j].startswith("#EXTINF"): break
                        if source_lines[j].startswith("#KODIPROP") or block:
                            block.append(source_lines[j])
                            if ".mpd" in source_lines[j]: break
                    source_map[channel] = block

    try:
        with open(MY_PLAYLIST, 'r', encoding='utf-8') as f:
            my_lines = f.readlines()
    except:
        print("ഫയൽ തുറക്കാൻ പറ്റിയില്ല")
        return

    final_playlist = []
    skip = False

    for line in my_lines:
        if line.startswith("#EXTINF"):
            final_playlist.append(line)
            skip = False
            for channel in TARGET_CHANNELS:
                if f'tvg-name="{channel}"' in line or f',{channel}' in line:
                    if channel in source_map:
                        for new_line in source_map[channel]:
                            final_playlist.append(new_line + "\n")
                        skip = True
                    break
        elif skip:
            if ".mpd" in line or "#KODIPROP" in line: continue
            if line.strip() == "": continue
            skip = False
            final_playlist.append(line)
        else:
            final_playlist.append(line)

    with open(MY_PLAYLIST, 'w', encoding='utf-8') as f:
        f.writelines(final_playlist)

if __name__ == "__main__":
    update_playlist()
