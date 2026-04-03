import requests

SOURCE_URL = "https://raw.githubusercontent.com/alex4528x/m3u/refs/heads/main/jtv.m3u"
OLD_FILE_NAME = "Zoh.m3u"
NEW_FILE_NAME = "Updated_Zoh.m3u"

# പഴയ പ്ലേലിസ്റ്റ് വായിക്കുക
with open(OLD_FILE_NAME, "r", encoding="utf-8") as f:
    old_lines = f.readlines()

# പഴയ tvg-id കളുടെ ഒരു സെറ്റ് സൃഷ്ടിക്കുക
tvg_ids = set()
for line in old_lines:
    if "tvg-id=" in line:
        tvg_id = line.split('tvg-id="')[1].split('"')[0]
        tvg_ids.add(tvg_id)

# പുതിയ സോഴ്‌സ് പ്ലേലിസ്റ്റ് വായിക്കുക
response = requests.get(SOURCE_URL)
new_lines_source = response.text.splitlines()

# ഫില്ടർ ചെയ്ത് പുതിയ ലൈൻകൾ ചേർക്കുക
new_lines = []

for line in new_lines_source:
    if "tvg-id=" in line:
        tvg_id = line.split('tvg-id="')[1].split('"')[0]
        if tvg_id in tvg_ids:
            new_lines.append(line + "\n")

# ഫൈനൽ ഫയൽ എഴുതുക
with open(NEW_FILE_NAME, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Playlist updated successfully")
