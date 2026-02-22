import json
import os
from datetime import datetime
from utils import *

BASE = {
    "stable": "https://get.videolan.org/vlc-android/",
    "beta": "https://get.videolan.org/testing/android/",
    "nightly": "https://artifacts.videolan.org/vlc-android/nightly-arm64/"
}

channel = os.environ["CHANNEL"]
base = BASE[channel]

html = fetch_html(base)
entries = parse_entries(html)
folder, dt = newest(entries)

now = datetime.now()
real_tag_time = now.strftime("%Y%m%d-%H%M")
real_date = now.strftime("%Y-%m-%d")

store = dt.strftime("%Y%m%d%H%M")

if channel == "nightly":
    page = base
else:
    page = base + folder + "/"

apk_html = fetch_html(page)
apk = find_apk(apk_html, channel != "nightly")
url = page + apk

rc = os.system(f"curl -fL '{url}' -o '{apk}'")
if rc != 0:
    raise SystemExit("APK download failed")

tag = f"{channel}-{real_tag_time}"

if channel == "nightly":
    name = f"nightly {real_date}"
else:
    name = folder.replace("-", " ")

create_release(tag, name, channel != "stable")
upload_asset(tag, apk)

with open("versions.json") as f:
    v = json.load(f)

v[channel] = store

with open("versions.json", "w") as f:
    json.dump(v, f, indent=2)

if channel == "nightly":
    msg = f"chore(vlc): {name}"
else:
    msg = f"chore(vlc): {channel} {name}"

git_commit(msg)

rels = os.popen("gh release list --json tagName -q '.[].tagName'").read().splitlines()

for r in rels:
    if r.startswith(channel) and r != tag:
        delete_release(r)
