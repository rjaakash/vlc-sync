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
    out = []

    for a in soup.find_all("a"):
        href = a.get("href")
        if not href or href.startswith("../"):
            continue

        tail = a.next_sibling
        if not tail:
            continue

        parts = tail.strip().split()
        if len(parts) < 2:
            continue

        dt = " ".join(parts[:2])

        try:
            d = datetime.strptime(dt, "%d-%b-%Y %H:%M")
        except:
            continue

        out.append((href.strip("/"), d))

    return out

def newest(entries):
    if not entries:
        raise RuntimeError("No entries found")
    return max(entries, key=lambda x: (x[1], x[0]))

def find_apk(html, arch=True):
    soup = BeautifulSoup(html, "html.parser")
    candidates = []

    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        link = cols[0].find("a")
        if not link:
            continue

        name = link.get("href")
        if not name or not name.lower().endswith(".apk"):
            continue

        low = name.lower()
        if arch and not ("arm64" in low or "v8a" in low):
            continue

        dt_text = cols[2].get_text(strip=True)

        try:
            d = datetime.strptime(dt_text, "%d-%b-%Y %H:%M")
        except:
            continue

        candidates.append((name, d))

    if not candidates:
        for a in soup.find_all("a"):
            name = a.get("href")
            if not name or not name.lower().endswith(".apk"):
                continue

            low = name.lower()
            if arch and not ("arm64" in low or "v8a" in low):
                continue

            tail = a.next_sibling
            if not tail:
                continue

            parts = tail.strip().split()
            if len(parts) < 2:
                continue

            dt_text = " ".join(parts[:2])

            try:
                d = datetime.strptime(dt_text, "%d-%b-%Y %H:%M")
            except:
                continue

            candidates.append((name, d))

    if not candidates:
        raise RuntimeError("APK not found")

    return max(candidates, key=lambda x: x[1])

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

    for _ in range(5):
        subprocess.run(["git", "pull", "--rebase"], check=False)

        gh(["git", "add", "versions.json"])
        r = subprocess.run(["git", "commit", "-m", msg])

        subprocess.run([
            "git",
            "-c", "rebase.autoStash=true",
            "-c", "merge.ours.driver=true",
            "pull",
            "--rebase"
        ], check=False)

        p = subprocess.run(["git", "push"])
        if p.returncode == 0:
            return

    raise SystemExit("git push failed after retries")
