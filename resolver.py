import json
from utils import fetch_html, parse_entries, newest, find_apk, gh

BASE = {
    "stable": "https://get.videolan.org/vlc-android/",
    "beta": "https://get.videolan.org/testing/android/",
    "nightly": "https://artifacts.videolan.org/vlc-android/nightly-arm64/"
}

with open("versions.json") as f:
    versions = json.load(f)

changed = []

for ch, url in BASE.items():
    html = fetch_html(url)

    if ch == "nightly":
        apk, dt = find_apk(html, False)
    else:
        entries = parse_entries(html)
        name, dt = newest(entries)

    now = dt.strftime("%Y%m%d%H%M")
    last = versions.get(ch)

    if last != now:
        changed.append(ch)

for c in changed:
    gh(["gh", "workflow", "run", "release.yml", "-f", f"channel={c}"])
