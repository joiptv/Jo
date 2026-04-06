import requests
import re

# സെറ്റിംഗുകൾ
SOURCE_URL = 'https://voot.vodep39240327.workers.dev?voot.m3u'
MY_PLAYLIST_FILE = 'Zoh.m3u'

def update_playlist():
    try:
        print("Fetching latest data from source...")
        response = requests.get(SOURCE_URL, timeout=30)
        if response.status_code != 200:
            print("Error: Could not fetch source link")
            return
        
        source_content = response.text

        # നിങ്ങളുടെ പ്ലേലിസ്റ്റ് ഫയൽ വായിക്കുന്നു
        with open(MY_PLAYLIST_FILE, 'r', encoding='utf-8') as f:
            my_lines = f.readlines()

        updated_playlist = []
        i = 0
        
        while i < len(my_lines):
            line = my_lines[i]
            
            # EXTINF ലൈൻ കണ്ടെത്തിയാൽ (ചാനൽ പേര് ഇതിലാണ്)
            if line.startswith('#EXTINF'):
                updated_playlist.append(line)
                
                # ചാനൽ പേര് കൃത്യമായി വേർതിരിച്ചെടുക്കുന്നു (ഉദാ: Asianet Plus)
                name_match = re.search(r',([^,]+)$', line.strip())
                if name_match:
                    channel_name = name_match.group(1).strip()
                    
                    # സോഴ്‌സിൽ ഈ ചാനലിന്റെ ബ്ലോക്ക് തിരയുന്നു
                    # ഇതിൽ #KODIPROP, #EXTVLCOPT, #EXTHTTP, കൂടാതെ URL എന്നിവ ഉൾപ്പെടും
                    pattern = rf'#EXTINF:.*,{re.escape(channel_name)}\s*\n((?:#(?:KODIPROP|EXTVLCOPT|EXTHTTP):.*?\n)*http.*)'
                    match = re.search(pattern, source_content, re.IGNORECASE | re.MULTILINE)
                    
                    if match:
                        # പുതിയ ഡാറ്റ (Headers + Link) ചേർക്കുന്നു
                        new_block = match.group(1)
                        updated_playlist.append(new_block + '\n')
                        
                        # നിങ്ങളുടെ പഴയ പ്ലേലിസ്റ്റിലെ ലിങ്ക് സെക്ഷൻ ഒഴിവാക്കുന്നു
                        i += 1
                        while i < len(my_lines) and not my_lines[i].strip().startswith('#EXTINF'):
                            i += 1
                        continue
            
            updated_playlist.append(line)
            i += 1

        # ഫയൽ സേവ് ചെയ്യുന്നു
        with open(MY_PLAYLIST_FILE, 'w', encoding='utf-8') as f:
            f.writelines(updated_playlist)
        
        print(f"Successfully updated {MY_PLAYLIST_FILE} with all headers and cookies!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    update_playlist()
