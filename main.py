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

if channel == "nightly":
    folder = ""
else:
    entries = parse_entries(html)
    folder, dt = newest(entries)

now = datetime.now()
real_tag_time = now.strftime("%Y%m%d-%H%M")
real_date = now.strftime("%Y-%m-%d")

if channel == "nightly":
    page = base
else:
    page = base + folder + "/"

apk_html = fetch_html(page)
apk, dt = find_apk(apk_html, channel != "nightly")
url = page + apk

store = dt.strftime("%Y%m%d%H%M")

rc = os.system(f"curl -fL --retry 5 --retry-delay 5 --retry-connrefused '{url}' -o '{apk}'")
if rc != 0:
    raise SystemExit("APK download failed")

tag = f"{channel}-{real_tag_time}"

name = f"{channel} {real_date}"

create_release(tag, name, channel != "stable")
upload_asset(tag, apk)

with open("versions.json") as f:
    v = json.load(f)

v[channel] = store

with open("versions.json", "w") as f:
    json.dump(v, f, indent=2)

msg = f"chore(vlc): {name}"

git_commit(msg)

rels = os.popen("gh release list --json tagName -q '.[].tagName'").read().splitlines()

same = sorted([r for r in rels if r.startswith(channel)], reverse=True)

for r in same[1:]:
    delete_release(r)
