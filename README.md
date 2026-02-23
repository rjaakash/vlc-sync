# ▶️ VLC Sync

Personal automation to keep VLC Android Stable, Beta, and Nightly APKs in one place.

I made this repo for myself.

VLC provides stable, beta, and nightly builds on different pages.  
Whenever I wanted to update, I had to open those separate links, check for the latest version, download the APK, and install it manually. If I was using nightly, I had to do this almost every day.

That got annoying.

So I automated it.

This repo watches the VLC pages, downloads the latest APKs, and publishes them as GitHub releases. Now everything lives in one place and I can update easily using tools like Obtainium.

---

## ⚙️ What it does

- Checks VLC Stable / Beta / Nightly endpoints  
- Detects new builds  
- Downloads the latest APK automatically  
- Creates GitHub releases  
- Keeps only the newest release per channel  
- Tracks state using `versions.json`  

---

## 📦 Channels

- stable  
- beta  
- nightly  

---

## 🙏 Credits

- VLC Android builds by **[VideoLAN](https://www.videolan.org/vlc/)**
- Automation powered by **[GitHub Actions](https://github.com/apps/github-actions)**
