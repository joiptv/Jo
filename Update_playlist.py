import requests
import re

# സെറ്റിംഗുകൾ
SOURCE_URL = 'https://voot.vodep39240327.workers.dev?voot.m3u'
MY_PLAYLIST_FILE = 'Zoh.m3u'

def update_playlist():
    try:
        # സോഴ്‌സ് ലിങ്ക് ഡൗൺലോഡ് ചെയ്യുന്നു
        print("Fetching source data...")
        source_response = requests.get(SOURCE_URL)
        source_content = source_response.text

        # നിങ്ങളുടെ പ്ലേലിസ്റ്റ് ഫയൽ വായിക്കുന്നു
        with open(MY_PLAYLIST_FILE, 'r', encoding='utf-8') as f:
            my_lines = f.readlines()

        updated_playlist = []
        i = 0
        
        while i < len(my_lines):
            line = my_lines[i]
            
            # EXTINF ലൈൻ ആണോ എന്ന് നോക്കുന്നു
            if line.startswith('#EXTINF'):
                updated_playlist.append(line)
                
                # ചാനൽ പേര് വേർതിരിച്ചെടുക്കുന്നു (അവസാന കോമയ്ക്ക് ശേഷമുള്ള ഭാഗം)
                channel_name_match = re.search(r',([^,]+)$', line.strip())
                if channel_name_match:
                    channel_name = channel_name_match.group(1).strip()
                    
                    # സോഴ്‌സിൽ ഈ ചാനലിന്റെ പുതിയ ഡാറ്റ തിരയുന്നു
                    # ഓരോ ചാനലിനും #KODIPROP മുതൽ ലിങ്ക് (.mpd/m3u8) വരെയുള്ള ഭാഗം പിടിച്ചെടുക്കുന്നു
                    pattern = rf'#EXTINF:.*{re.escape(channel_name)}.*?\n((?:#KODIPROP:.*?\n)*http.*)'
                    match = re.search(pattern, source_content, re.IGNORECASE | re.MULTILINE)
                    
                    if match:
                        new_data = match.group(1)
                        updated_playlist.append(new_data + '\n')
                        
                        # നിങ്ങളുടെ പഴയ ലിങ്ക് സെക്ഷൻ സ്കിപ്പ് ചെയ്യുന്നു
                        i += 1
                        while i < len(my_lines) and not my_lines[i].strip().startswith('#EXTINF') and not my_lines[i].strip().startswith('#EXTM3U'):
                            # അടുത്ത EXTINF വരുന്നത് വരെയുള്ള പഴയ വരികൾ ഒഴിവാക്കാൻ
                            if i + 1 < len(my_lines) and my_lines[i+1].startswith('#EXTINF'):
                                break
                            i += 1
                        i += 1
                        continue
            
            updated_playlist.append(line)
            i += 1

        # പുതിയ ഫയലിലേക്ക് സേവ് ചെയ്യുന്നു
        with open(MY_PLAYLIST_FILE, 'w', encoding='utf-8') as f:
            f.writelines(updated_playlist)
        
        print(f"Success! {MY_PLAYLIST_FILE} has been updated.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_playlist()
