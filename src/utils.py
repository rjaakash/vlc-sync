import json
import time
import subprocess
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

VERSIONS_FILENAME = "versions.json"
GIT_STATE_BRANCH = "state"
GIT_BOT_USERNAME = "github-actions[bot]"
GIT_BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"


def fetch_page_html(url):
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.text


def find_latest_apk(page_html):
    soup = BeautifulSoup(page_html, "html.parser")
    apk_candidates = []

    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        link = cols[0].find("a")
        if not link:
            continue

        apk_filename = link.get("href")
        if not apk_filename or not apk_filename.lower().endswith(".apk"):
            continue

        datetime_text = cols[2].get_text(strip=True)

        try:
            apk_datetime = datetime.strptime(datetime_text, "%d-%b-%Y %H:%M")
        except Exception:
            continue

        apk_candidates.append((apk_filename, apk_datetime))

    if not apk_candidates:
        raise RuntimeError("APK not found")

    return max(apk_candidates, key=lambda x: x[1])


def git_bot_config():
    subprocess.run(
        ["git", "config", "user.name", GIT_BOT_USERNAME],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", GIT_BOT_EMAIL], check=True, capture_output=True
    )


def git_commit_if_dirty(commit_message):
    has_staged_changes = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], capture_output=True
    )
    if has_staged_changes.returncode != 0:
        subprocess.run(
            ["git", "commit", "-m", commit_message], check=True, capture_output=True
        )


def state_branch_exists():
    result = subprocess.run(
        ["git", "ls-remote", "--heads", "origin", GIT_STATE_BRANCH],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() != ""


def checkout_state_branch():
    subprocess.run(
        ["git", "fetch", "origin", GIT_STATE_BRANCH],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "checkout", "-B", GIT_STATE_BRANCH, f"origin/{GIT_STATE_BRANCH}"],
        check=True,
        capture_output=True,
    )


def load_state_versions():
    if not state_branch_exists():
        return {}

    checkout_state_branch()

    versions_path = Path(VERSIONS_FILENAME)
    if not versions_path.exists():
        return {}

    raw = versions_path.read_text().strip()
    if not raw:
        return {}

    return json.loads(raw)


def save_state_versions(updated_versions, commit_message):
    for attempt in range(8):
        if not state_branch_exists():
            subprocess.run(
                ["git", "checkout", "--orphan", GIT_STATE_BRANCH],
                check=True,
                capture_output=True,
            )
            subprocess.run(["git", "rm", "-rf", "."], check=False, capture_output=True)
            subprocess.run(["git", "clean", "-fd"], check=False, capture_output=True)
            Path(VERSIONS_FILENAME).write_text(json.dumps({}, indent=2))
            git_bot_config()
            subprocess.run(
                ["git", "add", VERSIONS_FILENAME], check=True, capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                check=True,
                capture_output=True,
            )
            push_result = subprocess.run(
                ["git", "push", "-u", "origin", GIT_STATE_BRANCH], capture_output=True
            )
            if push_result.returncode != 0:
                time.sleep(2**attempt)
                continue
            subprocess.run(
                ["git", "fetch", "origin", GIT_STATE_BRANCH],
                check=False,
                capture_output=True,
            )
        else:
            checkout_state_branch()
            subprocess.run(
                ["git", "reset", "--hard", f"origin/{GIT_STATE_BRANCH}"],
                check=True,
                capture_output=True,
            )
            subprocess.run(["git", "clean", "-fd"], check=True, capture_output=True)

        Path(VERSIONS_FILENAME).write_text(json.dumps(updated_versions, indent=2))
        git_bot_config()
        subprocess.run(
            ["git", "add", VERSIONS_FILENAME], check=True, capture_output=True
        )
        git_commit_if_dirty(commit_message)

        push_result = subprocess.run(
            ["git", "push", "origin", GIT_STATE_BRANCH], capture_output=True
        )
        if push_result.returncode == 0:
            return

        subprocess.run(
            ["git", "reset", "--hard", f"origin/{GIT_STATE_BRANCH}"],
            check=False,
            capture_output=True,
        )
        subprocess.run(["git", "clean", "-fd"], check=False, capture_output=True)
        time.sleep(2**attempt)

    raise SystemExit("Failed to push state after retries")


def delete_github_release(tag):
    subprocess.run(["gh", "release", "delete", tag, "-y", "--cleanup-tag"], check=False)
