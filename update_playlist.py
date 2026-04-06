import requests
import re

# ചാനലുകളുടെ ലിസ്റ്റ് (നിങ്ങളുടെ പ്ലേലിസ്റ്റിലെ അതേ പേര് തന്നെ നൽകുക)
TARGET_CHANNELS = ["Asianet", "Asianet Plus", "Asianet Movies"]

# സോഴ്സ് ലിങ്കും നിങ്ങളുടെ ഫയലിന്റെ പേരും
SOURCE_URL = "https://voot.vodep39240327.workers.dev?voot.m3u"
MY_PLAYLIST = "zoh.m3u"

def fetch_source_blocks():
    """സോഴ്സിൽ നിന്ന് ഓരോ ചാനലിന്റെയും ഫുൾ ബ്ലോക്ക് (KODIPROP മുതൽ MPD വരെ) എടുക്കുന്നു"""
    try:
        response = requests.get(SOURCE_URL, timeout=15)
        if response.status_code != 200: return {}
        
        lines = response.text.splitlines()
        source_data = {}
        
        for i, line in enumerate(lines):
            if line.startswith("#EXTINF"):
                # ചാനൽ പേര് കണ്ടുപിടിക്കുന്നു
                for channel in TARGET_CHANNELS:
                    if f'tvg-name="{channel}"' in line or f',{channel}' in line:
                        block = []
                        # അടുത്ത ലൈനുകൾ പരിശോധിക്കുന്നു
                        for j in range(i + 1, len(lines)):
                            if lines[j].startswith("#EXTINF"): break
                            # KODIPROP മുതൽ തുടങ്ങുന്ന ലൈനുകൾ ചേർക്കുന്നു
                            if lines[j].startswith("#KODIPROP") or block:
                                block.append(lines[j])
                                if ".mpd" in lines[j]: break
                        source_data[channel] = block
        return source_data
    except Exception as e:
        print(f"Error fetching source: {e}")
        return {}

def update_my_playlist():
    source_blocks = fetch_source_blocks()
    if not source_blocks:
        print("Source-ൽ നിന്ന് വിവരങ്ങൾ ലഭ്യമല്ല.")
        return

    try:
        with open(MY_PLAYLIST, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"{MY_PLAYLIST} ഫയൽ കണ്ടെത്തിയില്ല.")
        return

    updated_playlist = []
    skip = False
    
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            updated_playlist.append(line)
            skip = False
            # ടാർഗറ്റ് ചാനൽ ആണോ എന്ന് നോക്കുന്നു
            for channel in TARGET_CHANNELS:
                if f'tvg-name="{channel}"' in line or f',{channel}' in line:
                    if channel in source_blocks:
                        # പുതിയ ബ്ലോക്ക് ചേർക്കുന്നു
                        updated_playlist.extend([l + "\n" for l in source_blocks[channel]])
                        skip = True # പഴയ ലിങ്കുകൾ ഒഴിവാക്കാൻ
                    break
        elif skip:
            # അടുത്ത EXTINF വരുന്നത് വരെയുള്ള പഴയ KODIPROP/URL ഒഴിവാക്കുന്നു
            if line.startswith("#EXTINF"):
                skip = False
                updated_playlist.append(line)
            continue
        else:
            if not skip:
                updated_playlist.append(line)

    # ഫയൽ സേവ് ചെയ്യുന്നു
    with open(MY_PLAYLIST, 'w', encoding='utf-8') as f:
        f.writelines(updated_playlist)
    print("Playlist successfully updated!")

if __name__ == "__main__":
    update_my_playlist()
    
