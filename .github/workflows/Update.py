# update_token.py

import requests
import re

FILE = "Zoh.m3u"
SOURCE_URL = "https://raw.githubusercontent.com/alex4528x/m3u/main/jtv.m3u"

headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(SOURCE_URL, headers=headers)
token_match = re.search(r'(__hdnea__=[^"&\s]*)', response.text)

if token_match:
    new_token = token_match.group(1)
    with open(FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if ".mpd" in line and "jio" in line.lower():
            base_link = line.split("?")[0].split(".mpd")[0] + ".mpd"
            new_lines.append(f"{base_link}?{new_token}\n")
        else:
            new_lines.append(line)

    with open(FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print("Zoh.m3u updated successfully")
else:
    print("Token not found")
    exit(1)
