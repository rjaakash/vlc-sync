import os
import subprocess
from utils import (
    fetch_page_html,
    find_latest_apk,
    load_state_versions,
    save_state_versions,
    delete_github_release,
)

NIGHTLY_BASE_URL = "https://artifacts.videolan.org/vlc-android/nightly-arm64/"


def check_for_nightly_update():
    stored_versions = load_state_versions()
    stored_version_stamp = stored_versions.get("nightly")

    nightly_page_html = fetch_page_html(NIGHTLY_BASE_URL)
    latest_apk_filename, latest_apk_datetime = find_latest_apk(nightly_page_html)
    latest_version_stamp = latest_apk_datetime.strftime("%Y%m%d-%H%M")

    if latest_version_stamp != stored_version_stamp:
        print("nightly_update_available=true")
    else:
        print("nightly_update_available=false")


def run_nightly_release():
    nightly_page_html = fetch_page_html(NIGHTLY_BASE_URL)
    latest_apk_filename, latest_apk_datetime = find_latest_apk(nightly_page_html)

    version_stamp = latest_apk_datetime.strftime("%Y%m%d-%H%M")
    date_compact = latest_apk_datetime.strftime("%Y%m%d")
    release_date = latest_apk_datetime.strftime("%Y-%m-%d")
    release_tag = f"Nightly-{date_compact}"
    release_title = f"Nightly · {release_date}"
    commit_message = f"release: nightly → {release_date}"

    existing_release_tags = (
        os.popen("gh release list --json tagName -q '.[].tagName'").read().splitlines()
    )
    if release_tag in existing_release_tags:
        delete_github_release(release_tag)

    apk_download_url = NIGHTLY_BASE_URL + latest_apk_filename
    download_exit_code = os.system(
        f"curl -fL --retry 5 --retry-delay 5 --retry-connrefused '{apk_download_url}' -o '{latest_apk_filename}'"
    )
    if download_exit_code != 0:
        raise SystemExit("APK download failed")

    subprocess.run(
        ["gh", "release", "create", release_tag, "-t", release_title, "--latest"],
        check=True,
    )
    subprocess.run(
        ["gh", "release", "upload", release_tag, latest_apk_filename],
        check=True,
    )

    stored_versions = load_state_versions()
    stored_versions["nightly"] = version_stamp
    save_state_versions(stored_versions, commit_message)

    all_release_tags = (
        os.popen("gh release list --json tagName -q '.[].tagName'").read().splitlines()
    )
    for old_tag in sorted(all_release_tags, reverse=True)[3:]:
        delete_github_release(old_tag)
