import requests
import subprocess
from bs4 import BeautifulSoup
from datetime import datetime
import os

def fetch_html(url):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.text

def parse_entries(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")
    out = []

    for r in rows:
        cols = r.find_all("td")
        if len(cols) < 3:
            continue

        name = cols[1].get_text(strip=True)
        dt = cols[2].get_text(strip=True)

        try:
            d = datetime.strptime(dt, "%Y-%m-%d %H:%M")
        except:
            try:
                d = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            except:
                continue

        out.append((name, d))

    return out

def newest(entries):
    if not entries:
        raise RuntimeError("No entries found")
    return max(entries, key=lambda x: x[1])

def find_apk(html, arch=True):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")
    candidates = []

    for r in rows:
        cols = r.find_all("td")
        if len(cols) < 3:
            continue

        link = cols[1].find("a")
        if not link:
            continue

        name = link.get("href")
        if not name:
            continue

        low = name.lower()
        if not low.endswith(".apk"):
            continue

        if arch and not ("arm64" in low or "v8a" in low):
            continue

        dt = cols[2].get_text(strip=True)

        try:
            d = datetime.strptime(dt, "%Y-%m-%d %H:%M")
        except:
            try:
                d = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            except:
                continue

        candidates.append((name, d))

    if not candidates:
        raise RuntimeError("APK not found")

    return max(candidates, key=lambda x: x[1])[0]

def gh(cmd):
    subprocess.run(cmd, check=True)

def create_release(tag, name, prerelease):
    args = ["gh", "release", "create", tag, "-t", name]
    if prerelease:
        args.append("--prerelease")
    gh(args)

def upload_asset(tag, file):
    gh(["gh", "release", "upload", tag, file])

def delete_release(tag):
    subprocess.run(["gh", "release", "delete", tag, "-y"], check=True)
    subprocess.run(["git", "push", "origin", f":refs/tags/{tag}"], check=True)

def git_commit(msg):
    gh(["git", "config", "user.name", "github-actions[bot]"])
    gh(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])
    gh(["git", "add", "versions.json"])
    subprocess.run(["git", "commit", "-m", msg], check=False)

    for _ in range(5):
        r = subprocess.run(["git", "push"])
        if r.returncode == 0:
            return
        subprocess.run(["git", "pull", "--rebase"], check=True)

    raise SystemExit("git push failed after retries")
